import streamlit as st
from pyvis.network import Network
import pyvis

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
col0, col1, col2 = st.columns([0.5, 1, 1])
with col0:
    mode = st.selectbox("Choose your role", ["增加" , "查询", "修改", "删除"])
with col1:
    name = st.text_input("属性名称", key="attribute_name")
with col2:
    change = st.text_input("修改内容", key="change_name")

with st.container():
    if st.button("确认",use_container_width=True):
        # todo：逻辑实现

        st.success(f"{mode}成功")

