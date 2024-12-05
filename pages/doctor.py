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

add_doctors_diagram(G)

# 生成交互式网络图
G.show("relationship_graph.html")

# 在Streamlit中显示HTML文件
st.components.v1.html(open("relationship_graph.html", "r").read(), height=600)



st.subheader("医生功能")

# 创建选项卡
tabs = st.tabs(["个人信息", "患者管理", "诊断记录"])

# 个人信息选项卡
with tabs[0]:
    st.header("个人信息")
    st.write(f"医生ID: {st.session_state.user_id}")
    try:
        # 发送请求获取医生信息
        response = make_request('GET', f'/doctor/profile/{st.session_state.user_id}')
        
        if response and response.status_code == 200:
            profile = response.json()

            # 使用HTML表格格式展示信息
            st.markdown("### 基本信息")

            table_html = f"""
            <table style="width:100%; border: 1px solid #ddd; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background-color: #f4f4f4;">姓名</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{profile['name']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background-color: #f4f4f4;">专业</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{profile['specialization']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background-color: #f4f4f4;">科室</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{profile['department_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background-color: #f4f4f4;">联系方式</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{profile['contact']}</td>
                </tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

        else:
            # 打印状态码和响应内容以获取更多信息
            st.error("获取个人信息失败")
            st.write(f"错误代码: {response.status_code if response else 'No Response'}")
            st.write(f"错误详情: {response.text if response else 'No Response Content'}")
    
    except Exception as e:
        # 捕获请求过程中的任何异常并显示详细信息
        import traceback
        st.error("发生错误，请检查日志")
        st.write("错误信息:")
        st.write(str(e))
        st.write("堆栈追踪:")
        st.text(traceback.format_exc())

        

# 患者管理选项卡
with tabs[1]:
    st.header("患者管理")
    
    # 选择操作类型：查询患者信息、修改患者信息或增添新患者
    operation = st.selectbox("选择操作", ["查询患者信息", "修改患者信息", "增添新患者"])

    if operation == "查询患者信息":
        st.write("### 查询患者信息")
        
        # 获取当前医生的患者列表
        response_list = make_request('GET', '/doctor/patients')
        
        if response_list:
            if response_list.status_code == 200:
                patients = response_list.json()
                if patients:
                    # 创建一个字典，键为 "ID - 姓名"，值为患者信息
                    patient_options = {f"{patient['id']} - {patient['name']}": patient for patient in patients}
                    
                    # 使用 selectbox 让医生选择患者
                    selected_patient_key = st.selectbox("选择患者", list(patient_options.keys()))
                    selected_patient = patient_options[selected_patient_key]
                    
                    # 显示选定患者的详细信息
                    st.write("### 患者信息")
                    st.write(f"**姓名**: {selected_patient.get('name', 'N/A')}")
                    st.write(f"**出生日期**: {selected_patient.get('birth_date', 'N/A')}")
                    st.write(f"**性别**: {selected_patient.get('gender', 'N/A')}")
                    st.write(f"**联系方式**: {selected_patient.get('contact', 'N/A')}")
                    st.write(f"**住址**: {selected_patient.get('address', 'N/A')}")
                    st.write(f"**病史**: {selected_patient.get('medical_history', 'N/A')}")
                    st.write(f"**关联开始日期**: {selected_patient.get('relationship_start', 'N/A')}")
                    st.write(f"**备注**: {selected_patient.get('notes', 'N/A')}")
                else:
                    st.info("当前医生没有患者。")
            else:
                try:
                    # 尝试提取详细的错误信息
                    error_detail = response_list.json().get('error', '获取患者列表失败，请重试。')
                    st.error(f"获取患者列表失败: {error_detail}")
                except ValueError:
                    # 如果无法解析 JSON，显示通用错误信息
                    st.error("获取患者列表失败，请检查服务器响应。")
        else:
            st.error("无法连接到服务器，请稍后再试。")
    elif operation == "修改患者信息":
        # 修改患者信息
        patient_id = st.text_input("输入需要修改的患者ID", key="edit_patient_id")
        
        if patient_id:
            response = make_request('GET', f'/doctor/patient/{patient_id}')
            if response and response.status_code == 200:
                patient = response.json()
                if patient:
                    st.write("### 患者信息")
                    st.write(f"当前姓名: {patient['name']}")
                    new_name = st.text_input("修改姓名", value=patient['name'])
                    new_birth_date = st.date_input("修改出生日期", value=patient['birth_date'])
                    new_gender = st.selectbox("修改性别", ['男', '女'], index=['男', '女'].index(patient['gender']))
                    new_contact = st.text_input("修改联系方式", value=patient['contact'])
                    new_address = st.text_input("修改住址", value=patient['address'])
                    new_medical_history = st.text_area("修改病史", value=patient['medical_history'])

                    # 提交修改
                    if st.button("提交修改"):
                        updated_patient_info = {
                            'name': new_name,
                            'birth_date': new_birth_date.strftime("%Y-%m-%d"),
                            'gender': new_gender,
                            'contact': new_contact,
                            'address': new_address,
                            'medical_history': new_medical_history
                        }
                        update_response = make_request('PUT', f'/doctor/patient/{patient_id}', json=updated_patient_info)
                        if update_response and update_response.status_code == 200:
                            st.success("患者信息修改成功")
                        else:
                            st.error("修改失败，请重试")
                else:
                    st.info("未找到该患者信息")
            else:
                st.error("查询失败，请检查患者ID")

    elif operation == "增添新患者":
        # 增添新患者
        st.write("### 新患者信息")

        patient_id = st.text_input("患者ID（必填）", key="new_patient_id")
        new_name = st.text_input("姓名（必填）", key="new_patient_name")
        new_birth_date = st.date_input("出生日期（必填）", key="new_patient_birth")
        new_gender = st.selectbox("性别（必填）", ['男', '女'], key="new_patient_gender")
        new_contact = st.text_input("联系方式（必填）", key="new_patient_contact")
        new_address = st.text_input("住址（必填）", key="new_patient_address")
        new_medical_history = st.text_area("病史", "无", key="new_patient_history")

        # 提交新增患者
        if st.button("提交新增患者"):
            if not all([new_name, new_birth_date, new_gender, new_contact, new_address]):
                st.error("请填写所有必填字段")
            else:
                new_patient_info = {

                    'patient_id': patient_id,
                    'name': new_name,
                    'birth_date': new_birth_date.strftime("%Y-%m-%d"),
                    'gender': new_gender,
                    'contact': new_contact,
                    'address': new_address,
                    'medical_history': new_medical_history
                }
                add_response = make_request('POST', '/doctor/patient', json=new_patient_info)
                if add_response:
                    if add_response.status_code == 201:
                        st.success(f"新患者信息已成功添加")
                    else:
                        try:
                            error_detail = add_response.json().get('error', '新增失败，请重试')
                            st.error(f"新增失败: {error_detail}")
                        except ValueError:
                            st.error("新增失败，请重试")
                else:
                    st.error("无法连接到服务器，请稍后重试")





# 诊断记录选项卡
with tabs[2]:
    st.header("诊断记录")
    
    # 添加诊断记录
    with st.form("add_treatment"):
        st.subheader("添加诊断记录")
        patient_id = st.text_input("患者ID")
        diagnosis = st.text_area("诊断结果")
        treatment_plan = st.text_area("治疗方案")
        medications = st.text_area("用药建议")
        
        if st.form_submit_button("提交"):
            response = make_request(
                'POST',
                '/doctor/treatment',
                json={
                    'patient_id': patient_id,
                    'diagnosis': diagnosis,
                    'treatment_plan': treatment_plan,
                    'medications': medications
                }
            )
            if response and response.status_code == 201:
                st.success("诊断记录添加成功！")
            else:
                st.error("添加失败")
    
    # 显示历史诊断记录
    if st.button("查看历史诊断记录"):
        response = make_request('GET', '/doctor/treatments')
        if response and response.status_code == 200:
            treatments = response.json()
            if treatments:
                st.dataframe(treatments)
            else:
                st.info("暂无诊断记录")