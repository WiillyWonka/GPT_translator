import streamlit as st

pg = st.navigation(
    [
        st.Page("chat.py", title="Чат"),
        st.Page("glossary.py", title="Глоссарий"),
        st.Page("dataset.py", title="Управление датасетом"),
    ]
)

pg.run()
