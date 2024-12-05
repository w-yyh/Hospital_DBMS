import streamlit as st
from pages.diagram import *
import requests

def make_request(method, endpoint, **kwargs):
    """发送带认证的请求"""
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f'Bearer {st.session_state.token}'
    
    try:
        response = requests.request(
            method, 
            f'http://localhost:5000{endpoint}',
            headers=headers,
            **kwargs
        )
        return response
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None

st.header("Welcome!!")
st.write(f"You are logged in as {st.session_state.role}.")

st.subheader(f"{st.session_state.role}-ER图")

# 创建网络图
G = Network(notebook=True)

add_nurses_diagram(G)

# 生成交互式网络图
G.show("relationship_graph.html")

# 在Streamlit中显示HTML文件
st.components.v1.html(open("relationship_graph.html", "r").read(), height=600)


st.subheader("用户操作")



st.subheader("护士功能")

# 创建选项卡
tabs = st.tabs(["个人信息", "病房管理", "患者护理"])

# 个人信息选项卡
with tabs[0]:
    st.header("个人信息")
    
    response = make_request('GET', f'/nurse/profile/{st.session_state.user_id}')
    if response and response.status_code == 200:
        profile = response.json()
        st.write("### 基本信息")
        st.write(f"姓名: {profile['name']}")
        st.write(f"科室: {profile['department_name']}")
        st.write(f"资质: {profile['qualification']}")
        st.write(f"联系方式: {profile['contact']}")

# 病房管理选项卡
with tabs[1]:
    st.header("病房管理")
    
    # 显示负责的病房
    response = make_request('GET', '/nurse/wards')
    if response and response.status_code == 200:
        wards = response.json()
        if wards:
            st.write("### 负责的病房")
            st.dataframe(wards)
            
            # 病房详细信息
            selected_ward = st.selectbox(
                "选择病房查看详情",
                [f"{ward['room_number']} - {ward['ward_type']}" for ward in wards]
            )
            
            if selected_ward:
                ward_id = wards[0]['id']  # 获取选中病房的ID
                response = make_request('GET', f'/nurse/ward/{ward_id}/patients')
                if response and response.status_code == 200:
                    patients = response.json()
                    if patients:
                        st.write("### 病房内患者")
                        st.dataframe(patients)
                    else:
                        st.info("该病房暂无患者")
        else:
            st.info("暂未分配病房")

# 患者护理选项卡
with tabs[2]:
    st.header("患者护理")
    
    # 添加护理记录
    with st.form("add_care_record"):
        st.subheader("添加护理记录")
        patient_id = st.text_input("患者ID")
        care_type = st.selectbox(
            "护理类型",
            ["日常护理", "用药护理", "特殊护理"]
        )
        description = st.text_area("护理描述")
        notes = st.text_area("备注")
        
        if st.form_submit_button("提交"):
            response = make_request(
                'POST',
                '/nurse/care-record',
                json={
                    'patient_id': patient_id,
                    'care_type': care_type,
                    'description': description,
                    'notes': notes
                }
            )
            if response and response.status_code == 201:
                st.success("护理记录添加成功！")
            else:
                st.error("添加失败")
    
    # 查看护理记录
    if st.button("查看历史护理记录"):
        response = make_request('GET', '/nurse/care-records')
        if response and response.status_code == 200:
            records = response.json()
            if records:
                st.dataframe(records)
            else:
                st.info("暂无护理记录")