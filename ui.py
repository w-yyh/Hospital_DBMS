import streamlit as st
import requests
import jwt
from datetime import datetime, timedelta

# 后端服务器地址
server_url = 'http://localhost:5000'

# 页面配置
st.set_page_config(page_title="医院数据库管理系统", layout="centered")

def init_session_state():
    """初始化所有 session_state 变量"""
    initial_values = {
        'role': None,
        'login_success': False,
        'create_success': False,
        'token': None,
        'token_exp': None,
        'user_id': None
    }
    
    for key, value in initial_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 在文件开头调用
init_session_state()

ROLES = [None, "Patient", "Doctor", "Nurse", "Admin"]

def login():
    st.header("用户登录")

    # 添加切换按钮
    tab_login, tab_register = st.tabs(["登录", "注册"])

    # 登录表单
    with tab_login:
        with st.form("login_form"):
            col0, col1, col2 = st.columns([0.9, 0.5, 2])
            with col0:
                st.write("  ")
            with col1:
                st.image("./images/logo.png", width=75)
            with col2:
                st.markdown("## 登录账号")
            
            login_username = st.text_input("账号名称", key="login_username")
            login_password = st.text_input("账号密码", type="password", key="login_password")

            
            login_submitted = st.form_submit_button("登录", use_container_width=True)

            if login_submitted and login_username and login_password:
                try:
                    response = requests.post(f'{server_url}/auth/login', json={
                        'username': login_username,
                        'password': login_password
                    })
                    if response.status_code == 200:
                        user_data = response.json()
                        st.session_state.token = user_data['token']
                        st.session_state.user_id = user_data['user_id']
                        st.session_state.role = user_data['role']
                        st.session_state.login_success = True
                        
                        try:
                            token_data = jwt.decode(
                                user_data['token'], 
                                verify=False  # 前端不验证签名
                            )
                            st.session_state.token_exp = token_data.get('exp')
                        except Exception as e:
                            print(f"Token decode error: {str(e)}")
                        
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("账号不存在或者密码不正确")
                except Exception as e:
                    st.error(f"连接服务器失败: {str(e)}")

    # 注册表单
    with tab_register:
        with st.form("register_form"):
            col0, col1, col2 = st.columns([0.6, 0.4, 2])
            with col0:
                st.write("  ")
            with col1:
                st.write("  ")
            with col2:
                st.markdown("## 创建新账户")
            
            register_username = st.text_input("账号名称", key="register_username")
            register_password = st.text_input("账号密码", type="password", key="register_password")
            email = st.text_input("邮箱", key="register_email")
            role = st.selectbox("选择角色", ROLES, key="register_role")

            role_info = {}
            if role == "Doctor":
                st.markdown("### 医生信息")
                role_info = {
                    'name': st.text_input("姓名（必填）", key="doctor_name"),
                    'birth_date': st.date_input("出生日期（必填）", key="doctor_birth").strftime("%Y-%m-%d"),
                    'contact': st.text_input("联系方式（必填）", key="doctor_contact"),
                    'department_id': st.selectbox("所属科室（必填）", ['1', '2', '3', '4'], key="doctor_dept"),
                    'specialization': st.text_input("专业（必填）", key="doctor_spec")
                }
            elif role == "Nurse":
                st.markdown("### 护士信息")
                role_info = {
                    'name': st.text_input("姓名（必填）", key="nurse_name"),
                    'birth_date': st.date_input("出生日期（必填）", key="nurse_birth").strftime("%Y-%m-%d"),
                    'contact': st.text_input("联系方式（必填）", key="nurse_contact"),
                    'department_id': st.selectbox("所属科室（必填）", ['1', '2', '3', '4'], key="nurse_dept"),
                    'qualification': st.text_input("资质（必填）", key="nurse_qual")
                }
            elif role == "Patient":
                st.markdown("### 患者信息")
                role_info = {
                    'name': st.text_input("姓名（必填）", key="patient_name"),
                    'birth_date': st.date_input("出生日期（必填）", key="patient_birth").strftime("%Y-%m-%d"),
                    'gender': st.selectbox("性别（必填）", ['男', '女'], key="patient_gender"),
                    'contact': st.text_input("联系方式（必填）", key="patient_contact"),
                    'address': st.text_input("住址（必填）", key="patient_address"),
                    'medical_history': st.text_area("病史", "无", key="patient_history")
                }

            register_submitted = st.form_submit_button("注册", use_container_width=True)

            if register_submitted:
                if not all([register_username, register_password, email, role]):
                    st.error("请填写所有必填字段")
                elif role in ["Doctor", "Nurse", "Patient"] and not all(role_info.values()):
                    st.error(f"请填写{role}的所有附加信息")
                else:
                    try:
                        register_data = {
                            'username': register_username,
                            'password': register_password,
                            'email': email,
                            'role': role
                        }

                        if role in ["Doctor", "Nurse", "Patient"]:
                            register_data[f'{role.lower()}_info'] = role_info

                        response = requests.post(f'{server_url}/auth/register', json=register_data)
                        
                        if response.status_code == 201:
                            st.success("注册成功！请返回登录页面进行登录。")
                        else:
                            st.error(response.json().get('error', '注册失败'))
                    except Exception as e:
                        st.error(f"连接服务器失败: {str(e)}")


def logout():
    """清除所有会话状态并返回登录页面"""
    # 清除所有会话状态
    for key in ['token', 'user_id', 'role', 'login_success', 'token_exp']:
        if key in st.session_state:
            del st.session_state[key]
    
    # 重新初始化会话状态
    init_session_state()
    
    # 强制重新加载页面
    st.rerun()
    
    # 显示登录页面
    login()

def make_authenticated_request(method, url, **kwargs):
    """发送带有认证令牌的请求"""
    if st.session_state.token:
        # 检查令牌是否过期
        if st.session_state.token_exp and datetime.fromtimestamp(st.session_state.token_exp) < datetime.now():
            st.error("登录已过期，请重新登录")
            logout()
            return None
            
        # 添加认证头
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {st.session_state.token}'
        kwargs['headers'] = headers
        
    try:
        response = requests.request(method, url, **kwargs)
        
        # 处理认证错误
        if response.status_code == 401:
            st.error("认证失败，请重新登录")
            logout()
            return None
            
        return response
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        return None

def main():
    if not st.session_state.login_success:
        login()
    else:
        # 验证令牌是否有效
        if st.session_state.token_exp and datetime.fromtimestamp(st.session_state.token_exp) < datetime.now():
            st.error("登录已过期，请重新登录")
            logout()
            return
            
        # 设置页面导航
        role = st.session_state.role
        
        # 定义页面
        logout_page = st.Page(logout, title="退出登录", icon="🚪")
        settings = st.Page("pages/settings.py", title="设置", icon="⚙️")
        patient = st.Page("pages/patient.py", title="患者", icon="🏥", default=(role == "Patient"))
        doctor = st.Page("pages/doctor.py", title="医生", icon="👨‍⚕️", default=(role == "Doctor"))
        nurse = st.Page("pages/nurse.py", title="护士", icon="👩‍⚕️", default=(role == "Nurse"))
        admin = st.Page("pages/admin.py", title="管理员", icon="👑", default=(role == "Admin"))

        # 组织页面
        account_pages = [logout_page, settings]
        patient_pages = [patient]
        doctor_pages = [doctor]
        nurse_pages = [nurse]
        admin_pages = [admin]

        # 根据角色显示不同页面
        page_dict = {}
        if role in ["Patient", "Admin"]:
            page_dict["Patient"] = patient_pages
        if role in ["Doctor", "Admin"]:
            page_dict["Doctor"] = doctor_pages
        if role in ["Nurse", "Admin"]:
            page_dict["Nurse"] = nurse_pages
        if role == "Admin":
            page_dict["Admin"] = admin_pages

        # 设置导航
        if len(page_dict) > 0:
            pg = st.navigation({"Account": account_pages} | page_dict)
            pg.run()

if __name__ == "__main__":
    main()