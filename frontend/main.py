import streamlit as st

if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

login_page = st.Page("login.py", title="Вход", icon=":material/login:")
logout_page = st.Page(logout, title="Выход", icon=":material/logout:")
info_page = st.Page("user_info.py", title="Инфо")
chat_page = st.Page("chat.py", title="Чат", default=True)
glossary_page = st.Page("glossary.py", title="Глоссарий")
dataset_page = st.Page("dataset.py", title="Управление датасетом")

if st.session_state.user:
    pages = [logout_page, info_page, chat_page, glossary_page]

    if st.session_state.user.role == 'admin':
        pages.append(dataset_page)

    pg = st.navigation(pages)
else:
    pg = st.navigation([login_page])

pg.run()