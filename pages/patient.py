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

add_patients_diagram(G)

# 生成交互式网络图
G.show("relationship_graph.html")

# 在Streamlit中显示HTML文件
st.components.v1.html(open("relationship_graph.html", "r").read(), height=600)


st.subheader("用户操作")



st.subheader("患者功能")

# 创建选项卡
tabs = st.tabs(["个人信息", "就医记录", "住院信息"])

# 个人信息选项卡
with tabs[0]:
    st.header("个人信息")
    
    response = make_request('GET', f'/patient/profile/{st.session_state.user_id}')
    if response and response.status_code == 200:
        profile = response.json()
        st.write("### 基本信息")
        st.write(f"姓名: {profile['name']}")
        st.write(f"性别: {profile['gender']}")
        st.write(f"出生日期: {profile['birth_date']}")
        st.write(f"联系方式: {profile['contact']}")
        st.write(f"地址: {profile['address']}")
        
        with st.expander("病史记录"):
            st.write(profile.get('medical_history', '暂无病史记录'))

# 就医记录选项卡
with tabs[1]:
    st.header("就医记录")
    
    # 显示主治医生
    response = make_request('GET', '/patient/doctors')
    if response and response.status_code == 200:
        doctors = response.json()
        if doctors:
            st.write("### 主治医生")
            st.dataframe(doctors)
        else:
            st.info("暂无主治医生信息")
    
    # 显示诊断记录
    if st.button("查看诊断记录"):
        response = make_request('GET', '/patient/treatments')
        if response and response.status_code == 200:
            treatments = response.json()
            if treatments:
                for treatment in treatments:
                    with st.expander(f"诊断日期: {treatment['treatment_date']}"):
                        st.write(f"医生: {treatment['doctor_name']}")
                        st.write(f"诊断: {treatment['diagnosis']}")
                        st.write(f"治疗方案: {treatment['treatment_plan']}")
                        st.write(f"用药建议: {treatment['medications']}")
            else:
                st.info("暂无诊断记录")

# 住院信息选项卡
with tabs[2]:
    st.header("住院信息")
    
    # 显示当前住院信息
    response = make_request('GET', '/patient/admissions/current')
    if response and response.status_code == 200:
        admission = response.json()
        if admission:
            st.write("### 当前住院信息")
            st.write(f"病房号: {admission['ward_number']}")
            st.write(f"入院日期: {admission['admission_date']}")
            st.write(f"预计出院日期: {admission['expected_discharge_date']}")
            st.write(f"主治医生: {admission['doctor_name']}")
            
            # 显示护理记录
            if st.button("查看护理记录"):
                response = make_request('GET', '/patient/care-records')
                if response and response.status_code == 200:
                    records = response.json()
                    if records:
                        st.write("### 护理记录")
                        st.dataframe(records)
                    else:
                        st.info("暂无护理记录")
        else:
            st.info("当前没有住院记录")
    
    # 显示历史住院记录
    if st.button("查看历史住院记录"):
        response = make_request('GET', '/patient/admissions/history')
        if response and response.status_code == 200:
            history = response.json()
            if history:
                st.write("### 历史住院记录")
                st.dataframe(history)
            else:
                st.info("暂无历史住院记录")