import streamlit as st
from pyvis.network import Network
import pyvis
import requests

def make_request(method, endpoint, **kwargs):
    """发送带认证的请求"""
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f'Bearer {st.session_state.token}'
    
    try:
        response = requests.request(
            method, 
            f'http://localhost:5000{endpoint}',  # 后端服务器地址
            headers=headers,
            **kwargs
        )
        return response
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None

from pages.diagram import *

st.header("Welcome!!")
st.write(f"You are logged in as {st.session_state.role}.")

st.subheader("UI: 杨竣杰 Flask后端：王昱皓 SQL数据库：何鹏晖，陈傲天")
st.write("该项目是一个基于Streamlit框架的医院数据库管理系统，旨在提供一个简单的界面来处理用户的注册、登录、密码修改等操作。"
         "项目的核心技术栈包括Streamlit和pyvis用于前端界面开发，Python用于业务逻辑处理，Flask作为后端框架，结合SQL数据库用于存储用户信息。")

st.subheader("项目整体ER图展示")

with st.expander("参考资料"):
    st.image("images/ER_pic.png")

# 创建网络图
G = Network(notebook=True)

# 绘制所有ER图
add_users_diagram(G)
add_dormitory_diagram(G)
add_wards_diagram(G)
add_doctors_diagram(G)
add_nurses_diagram(G)
add_patients_diagram(G)

# 弱实体继承关系
G.add_edge("users", "doctors", width=5, color="red", label="继承")
G.add_edge("users", "nurses", width=5, color="red", label="继承")
G.add_edge("users", "patients", width=5, color="red", label="继承")

# 患者-医生关系
G.add_node("diagnosis", size=40, shape="diamond", color="yellow", title="诊断", label="diagnosis")
G.add_edge("doctors", "diagnosis", width=5, color="yellow", arrows="middle")
G.add_edge("diagnosis", "patients", width=5, color="yellow", arrows="middle")

G.add_node("visit_date", size=30, shape="dot", color="lightgreen", title="就诊日期", label="visit_date")
G.add_edge("visit_date", "diagnosis", width=3, color="gray")

# 患者-病房关系
G.add_node("occupy", size=40, shape="diamond", color="yellow", title="使用", label="occupy")
G.add_edge("patients", "occupy", width=5, color="yellow", arrows="middle")
G.add_edge("occupy", "wards", width=5, color="yellow", arrows="middle")

G.add_node("admission_date", size=30, shape="dot", color="lightgreen", title="入院日期", label="admission_date")
G.add_edge("admission_date", "occupy", width=3, color="gray")
G.add_node("discharge_date", size=30, shape="dot", color="lightgreen", title="出院日期", label="discharge_date")
G.add_edge("discharge_date", "occupy", width=3, color="gray")

# accommodate 医生，护士-宿舍关系
G.add_node("dormitory_offerings", size=40, shape="diamond", color="yellow", title="提供宿舍", label="dormitory_offerings")
G.add_edge("doctors", "dormitory_offerings", width=5, color="yellow", arrows="middle")
G.add_edge("nurses", "dormitory_offerings", width=5, color="yellow", arrows="middle")
G.add_edge("dormitory_offerings", "dormitory", width=5, color="yellow", arrows="middle")

G.add_node("room_number", size=30, shape="dot", color="lightgreen", title="房间号", label="room_number")
G.add_edge("room_number", "dormitory_offerings", width=3, color="gray")

G.force_atlas_2based()
# 生成交互式网络图
G.show("relationship_graph.html")

# 在Streamlit中显示HTML文件
st.components.v1.html(open("relationship_graph.html", "r").read(), height=600)

st.subheader("数据库操作")

# 增删查改
st.subheader("管理功能")

# 创建选项卡
tabs = st.tabs(["医生管理", "科室管理", "护士分配"])

# 医生管理选项卡
with tabs[0]:
    st.header("医生管理")
    
    # 显示所有医生
    response = make_request('GET', '/admin/doctors')
    if response and response.status_code == 200:
        doctors = response.json()
        if doctors:
            st.write("医生列表：")
            st.dataframe(doctors)
    
    # 添加医生
    with st.form("add_doctor"):
        st.subheader("添加新医生")
        doctor_data = {
            'doctor_id': st.text_input("医生ID"),
            'name': st.text_input("姓名"),
            'birth_date': st.date_input("出生日期").strftime("%Y-%m-%d"),
            'contact': st.text_input("联系电话"),
            'specialization': st.text_input("专业"),
            'department_id': st.text_input("科室ID"),
            'email': st.text_input("邮箱")
        }
        
        if st.form_submit_button("添加"):
            response = make_request('POST', '/admin/doctor', json=doctor_data)
            if response and response.status_code == 200:
                st.success("医生添加成功！")
            else:
                st.error("添加失败")

# 科室管理选项卡
with tabs[1]:
    st.header("科室管理")
    
    # 分配科室
    with st.form("assign_department"):
        st.subheader("分配科室")
        doctor_id = st.text_input("医生ID")
        department_id = st.text_input("科室ID")
        
        if st.form_submit_button("分配"):
            response = make_request(
                'PUT', 
                f'/admin/department/{doctor_id}/assign',
                json={'department_id': department_id}
            )
            if response and response.status_code == 200:
                st.success("科室分配成功！")
            else:
                st.error(response.json().get('error', '分配失败'))

# 护士分配统计选项卡
with tabs[2]:
    st.header("护士分配统计")
    
    if st.button("获取统计信息"):
        response = make_request('GET', '/admin/nurse-assignment/stats')
        if response and response.status_code == 200:
            stats = response.json()
            
            # 显示总体统计
            st.subheader("总体统计")
            overall = stats['overall_stats']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总护士数", overall['total_nurses'])
            with col2:
                st.metric("总病房数", overall['total_wards'])
            with col3:
                st.metric("总分配数", overall['total_assignments'])
            with col4:
                st.metric("活跃分配比例", f"{overall['active_assignment_percentage']}%")
            
            # 显示病房详细统计
            st.subheader("病房护士分配详情")
            ward_stats = stats['ward_stats']
            if ward_stats:
                st.dataframe(ward_stats)
            else:
                st.info("暂无病房分配信息")

