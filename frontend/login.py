import streamlit as st
import requests

from schemas import User

st.title("Авторизация")

ROLES = [None, "User", "Admin"]

if "action" not in st.session_state:
    st.session_state.action = None

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.action == "login":
    name = st.text_input("Ведите имя")
    if st.button("Войти") and name:
        response = requests.get(f'http://localhost:8000/users/{name}')

        if response.ok:
            user = User(**response.json())
            st.session_state.user = user
            st.session_state.action = None
            st.rerun()
        else:
            if response.status_code == 404:
                st.error("Не найден такой пользователь.")
            else:
                st.error("Ошибка сервера.")

elif st.session_state.action == "register":
    name = st.text_input("Ведите имя")
    role = st.selectbox("Выберите роль", ROLES)

    if st.button("Зарегистрироваться") and role and name:
        response = requests.post('http://localhost:8000/users/', json={'login': name, 'role': role})
        if response.ok:
            user = User(**response.json())
            st.session_state.user = user
            st.session_state.action = None
            st.rerun()
        else:
            if response.status_code == 400:
                st.error("Такой пользователь уже существует.")
            else:
                st.error("Ошибка сервера.")

else:
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Войти", use_container_width=True):
            st.session_state.action = "login"
            st.rerun()
        if st.button("Зарегистрироваться", use_container_width=True):
            st.session_state.action = "register"
            st.rerun()