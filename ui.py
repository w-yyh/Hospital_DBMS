from datetime import date

import requests
import streamlit as st

st.set_page_config(page_title="医院数据库管理系统", layout="centered", initial_sidebar_state="collapsed")

# 定义后端地址
server_url = 'http://125.216.245.32:5000'

page = st.sidebar.radio("选择页面", ["登录","主页"])

# 登录
def login():
    '''
    返回值：
    username: str
    password: str
    submitted: bool 是否注册
    '''
    with st.form("Credentials"):
        col0, col1, col2 = st.columns([0.6, 0.4, 2])
        with col0:
            st.write("  ")
        with col1:
            # st.image("./utils/logo.png", width=75)
            st.write("  ")
        with col2:
            st.markdown("## 登录账号")
        username = st.text_input("账号名称", key="username")
        password = st.text_input("账号密码", type="password", key="password")
        cols = st.columns([4, 1])
        submitted = cols[1].form_submit_button("登录")
    return username, password, submitted

# 注册基本信息
def register():
    '''
    返回值：
    username: str
    password: str
    role:
    email: str
    submitted: bool 是否注册
    '''
    with st.form("Register"):
        col0, col1, col2 = st.columns([0.6, 0.4, 2])
        with col0:
            st.write("  ")
        with col1:
            # st.image("./utils/logo.png", width=75)
            st.write("  ")
        with col2:
            st.markdown("## 创建新账户")
        username = st.text_input("账号名称", key="register_username")
        password = st.text_input("账号密码", type="password", key="register_password")
        email = st.text_input("邮箱", key="register_email")
        role = st.selectbox("选择角色", ['admin', 'doctor', 'nurse', 'patient'], key="register_role")
        submitted = st.form_submit_button("确认基本信息")

        return username, password, role, email, submitted

# 注册角色信息
def register_for_role(role:str):  # todo：实现4个角色的注册逻辑
    '''
    输入：
    role ： str
    返回值：

    '''
    with st.form("Register for role"):
        st.markdown("## 完善账户信息")
        if role == 'doctor':
            # 具体加信息
            submitted = st.form_submit_button("注册")
            return submitted
        # elif:
        else:
            submitted = st.form_submit_button("注册")
            return submitted


# 修改密码功能
def change_password():
    with st.expander("修改密码"):
        current_password = st.text_input("当前密码", type="password")
        new_password = st.text_input("新密码", type="password")
        confirm_new_password = st.text_input("确认新密码", type="password")

        # 先判断是否按下了确认修改按钮
        if st.button("确认修改", use_container_width=True):
            # 检查新密码与确认密码是否匹配
            if new_password != confirm_new_password:
                st.error("新密码与确认密码不一致")
                return None, None  # 返回None表示修改失败
            # 进一步可以在这里加上当前密码验证逻辑
            return current_password, new_password
    return None, None  # 没有点击修改按钮时返回None

# '''登录页面'''

if page == "登录":
    selection = st.radio("选择操作", ("登录已有账号", "创建新账户"))

    if selection == "登录已有账号":
        username, password, submitted = login()

        st.session_state["login_success"] = True  # todo：实现密码正误逻辑
        st.write(username, password)  # 调试用

        if not st.session_state["login_success"]:
            st.error("😕 账号不存在或者密码不正确")
            st.stop()
        else:
            st.success("登录成功")

            # 登录完成后，获得账户信息，根据role展示不同功能
            st.session_state["role"] = "admin"  # todo：实现获得role逻辑
            st.session_state["user_name"] = username

            st.write(f"**{st.session_state["role"]}**{st.session_state["user_name"]}")
            st.write("欢迎登录医院管理系统！")


        # 修改密码
        if st.session_state["login_success"]:
            current_password, new_password = change_password()
            if current_password and new_password:

                st.session_state["change_password_success"] = True  # todo：实现修改密码逻辑

                if st.session_state["change_password_success"]:
                    st.success("修改密码成功")

    elif selection == "创建新账户":
        username, password, role, email, submitted = register()

        st.session_state["create_basic_account_success"] = True  # todo：实现基本信息创建正误逻辑
        st.write(username, password, role, email)  # 调试用

        if st.session_state["create_basic_account_success"]:
            role_submitted = register_for_role(role)


            st.session_state["create_role_account_success"] = True  # todo：实现role信息创建正误逻辑
            st.write(role_submitted)  # 调试用

            if st.session_state["create_basic_account_success"] and st.session_state["create_role_account_success"]:
                st.success("账号创建成功")

# 主页方法

def intro_for_main_window():
    # st.header("项目简介")
    st.subheader("UI: 杨竣杰 Flask后端：王昱皓 SQL数据库：何鹏晖，陈傲天")
    st.write("该项目是一个基于Streamlit框架的医院数据库管理系统，旨在提供一个简单的界面来处理用户的注册、登录、密码修改等操作。"
             "项目的核心技术栈包括Streamlit用于前端界面开发，Python用于业务逻辑处理，Flask作为后端框架，结合SQL数据库用于存储用户信息。")

# todo：输出信息示例
def show_doctor_info(response):
    # 获取医生信息按钮
    if st.button("获取医生信息"):
        doctor_info = response.json()

        # 显示医生信息
        st.write("### 医生详细信息")
        st.write(f"**姓名**: {doctor_info['name']}")
        st.write(f"**出生日期**: {doctor_info['birth_date']}")
        st.write(f"**联系方式**: {doctor_info['contact']}")
        st.write(f"**邮箱**: {doctor_info['email']}")
        st.write(f"**科室名称**: {doctor_info['department_name']}")
        st.write(f"**专业领域**: {doctor_info['specialization']}")



# '''主页'''
if page == "主页" and st.session_state["login_success"]:
    with st.expander("项目简介"):
        intro_for_main_window()



