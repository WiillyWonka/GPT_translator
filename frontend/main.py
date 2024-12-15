import streamlit as st

if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

login_page = st.Page("login.py", title="Вход", icon=":material/login:")
logout_page = st.Page(logout, title="Выход", icon=":material/logout:")
info_page = st.Page("user_info.py", title="Инфо")
chat_page = st.Page("chat.py", title="Чат", default=True)
glossary_page = st.Page("glossary.py", title="Глоссарий")
dataset_page = st.Page("dataset.py", title="Управление датасетом")

if st.session_state.user:
    pg = st.navigation([logout_page, info_page, chat_page, glossary_page, dataset_page])
else:
    pg = st.navigation([login_page])

pg.run()