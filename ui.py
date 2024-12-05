import streamlit as st

st.set_page_config(page_title="医院数据库管理系统", layout="centered")

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None,"Patient" , "Doctor", "Nurse", "Admin"]


def login():
    st.header("用户登录")

    # 登录
    with st.form("Credentials"):
        col0, col1, col2 = st.columns([0.9, 0.5, 2])
        with col0:
            st.write("  ")
        with col1:
            st.image("./images/logo.png", width=75)
            # st.write("  ")
        with col2:
            st.markdown("## 登录账号")
        login_username = st.text_input("账号名称", key="username")
        login_password = st.text_input("账号密码", type="password", key="password")
        role = st.selectbox("Choose your role", ROLES)
        # cols = st.columns([4, 1])
        with st.container():
            submitted = st.form_submit_button("登录", use_container_width=True)

    # 注册
    with st.form("Register"):
        col0, col1, col2 = st.columns([0.6, 0.4, 2])
        with col0:
            st.write("  ")
        with col1:
            # st.image("./utils/logo.png", width=75)
            st.write("  ")
        with col2:
            st.markdown("## 创建新账户")
        register_username = st.text_input("账号名称", key="register_username")
        register_password = st.text_input("账号密码", type="password", key="register_password")
        email = st.text_input("邮箱", key="register_email")
        with st.container():
            submitted = st.form_submit_button("确认信息", use_container_width=True)

    st.session_state.login_success = True  # todo：实现密码正误逻辑
    st.write(login_username, login_password)  # 调试用

    st.session_state.create_success = True  # todo：实现账户创建正误逻辑
    if st.session_state.create_success:
        st.success("账号创建成功")
    st.write(register_username, register_password, email)  # 调试用

    if not st.session_state.login_success:
        st.error("😕 账号不存在或者密码不正确")
    else:
        # st.success("登录成功")
        st.session_state.role = role
        st.rerun()



def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("pages/settings.py", title="Settings", icon=":material/settings:")
patient = st.Page(
    "pages/patient.py",
    title="Patient",
    icon=":material/help:",
    default=(role == "Patient"),
)
doctor = st.Page(
    "pages/doctor.py",
    title="Doctor",
    icon=":material/help:",
    default=(role == "Doctor"),
)
nurse = st.Page(
    "pages/nurse.py",
    title="Nurse",
    icon=":material/healing:",
    default=(role == "Nurse"),
)
admin = st.Page(
    "pages/admin.py",
    title="Admin",
    icon=":material/person_add:",
    default=(role == "Admin"),
)

account_pages = [logout_page, settings]
patient_pages = [patient]
doctor_pages = [doctor]
nurse_pages = [nurse]
admin_pages = [admin]

st.title("医院数据库管理系统")
st.logo("images/logo.png", icon_image="images/logo.png")

page_dict = {}
if st.session_state.role in ["Patient", "Admin"]:
    page_dict["Patient"] = patient_pages
if st.session_state.role in ["Doctor", "Admin"]:
    page_dict["Doctor"] = doctor_pages
if st.session_state.role in ["Nurse", "Admin"]:
    page_dict["Nurse"] = nurse_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()