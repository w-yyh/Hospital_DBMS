import streamlit as st
from pages.diagram import *

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