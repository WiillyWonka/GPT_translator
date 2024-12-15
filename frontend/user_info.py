import streamlit as st

st.title("Информация о пользователе.")

if "user" in st.session_state and st.session_state.user:
    col1, col2 = st.columns([1, 10])
    with col1:
        st.text(f"Логин:")
        st.text(f"Роль:")
    with col2:
        st.text(st.session_state.user.login)
        st.text(st.session_state.user.role)