import requests
import streamlit as st

from schemas import User

st.title("Информация о пользователе.")

if "user" in st.session_state and st.session_state.user:
    response = requests.get(f'http://localhost:8000/users/{st.session_state.user.login}')

    if response.ok:
        user = User(**response.json())
        st.session_state.user = user
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.text(f"Логин:")
            st.text(f"Роль:")
            st.text(f"Входящие токены:")
            st.text(f"Исходящие токены:")
        with col2:
            st.text(st.session_state.user.login)
            st.text(st.session_state.user.role)
            st.text(st.session_state.user.total_input_tokens)
            st.text(st.session_state.user.total_output_tokens)
    else:
        if response.status_code == 404:
            st.error("Не найден такой пользователь.")
        else:
            st.error("Ошибка сервера.")