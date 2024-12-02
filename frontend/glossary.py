import streamlit as st
import requests

# Glossary Management
st.title("Глоссарий")

def get_glossary(cached=False):
    if not cached or "glossary" not in st.session_state:
        response = requests.get('http://localhost:8000/glossary/')
        if not response.ok:
            st.error("Не удаётся получить глоссарий.")
            return []

        st.session_state.glossary = response.json()

    glossary = st.session_state.glossary

    return glossary

# Add Term
st.header("Добавить новый термин")
term = st.text_input("Термин")
translation = st.text_input("Перевод")
comment = st.text_input("Комментарий к переводу")

if st.button("Добавить термин"):
    if term.strip() != "" and translation.strip() != "":
        response = requests.post('http://localhost:8000/glossary/', json={'term': term, 'translation': translation, 'comment': comment})
        if response.ok:
            st.success("Термин успешно добавлен!")
            glossary = get_glossary(cached=False)
        else:
            st.error("Не удалось добавить термин!")

# Load Glossary
glossary = get_glossary(cached=True)

# Содержимое глоссария
st.header("Глоссарий")
for i, term in enumerate(glossary):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.text(term["term"])

    with col2:
        is_view = st.button("Просмотреть", key=f"view_{i}")

    if is_view:
        line = f"**Термин**: {term['term']}\n\n**Перевод**: {term['translation']}"
        if term["comment"]:
            line += f"\n\n**Комментарий**: {term['comment']}"
        st.info(line)

    with col3:
        if st.button("Удалить", key=f"delete_{i}"):
            response = requests.delete('http://localhost:8000/glossary/', json={'term': term["term"]})
            if response.ok:
                glossary = get_glossary(cached=False)
                st.rerun()
            else:
                st.error("Не удалось удалить пример")
    