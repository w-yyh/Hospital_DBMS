import streamlit as st

st.header("Settings")
st.write(f"You are logged in as {st.session_state.role}.")

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


# 修改密码
if st.session_state.login_success:
    current_password, new_password = change_password()
    if current_password and new_password:

        st.session_state["change_password_success"] = True  # todo：实现修改密码逻辑

        if st.session_state["change_password_success"]:
            st.success("修改密码成功")
