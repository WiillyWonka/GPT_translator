import streamlit as st
import requests

import schemas

# Glossary Management
st.title("Глоссарий")

def get_glossary(cached=False):
    if not cached or "glossary" not in st.session_state:
        if st.session_state.user.role == schemas.UserRole.USER:
            response = requests.get(f'http://localhost:8000/glossary/{st.session_state.user.id}')
            if not response.ok:
                st.error("Не удаётся получить пользовательский глоссарий.")
                return {}

            user_glossary = [schemas.Glossary(**item) for item in response.json()]
    
            response = requests.get(f'http://localhost:8000/glossary')
            if not response.ok:
                st.error("Не удаётся получить базовый глоссарий.")
                return {}

            general_glossary = [schemas.Glossary(**item) for item in response.json()]

            glossary = {'mutable': user_glossary, 'immutable': general_glossary}
            st.session_state.glossary = glossary

        elif st.session_state.user.role == schemas.UserRole.ADMIN:
            response = requests.get(f'http://localhost:8000/glossary')
            if not response.ok:
                st.error("Не удаётся получить базовый глоссарий.")
                return {}

            general_glossary = [schemas.Glossary(**item) for item in response.json()]

            glossary = {'mutable': general_glossary, 'immutable': []}
            st.session_state.glossary = glossary
        else:
            raise ValueError(f"Undefined user role: {st.session_state.user.role}")

    return st.session_state.glossary

# Add Term
st.header("Добавить новый термин")
term = st.text_input("Термин").strip()
translation = st.text_input("Перевод").strip()
comment = st.text_input("Комментарий к переводу").strip()

if st.button("Добавить термин"):
    if term != "" and translation != "":
        response = requests.post('http://localhost:8000/glossary/', json={'term': term, 'translation': translation, 'comment': comment, 'user_id': st.session_state.user.id})
        if response.ok:
            st.success("Термин успешно добавлен!")
            glossary = get_glossary(cached=False)
        else:
            st.error("Не удалось добавить термин!")

# Load Glossary
glossary = get_glossary(cached=True)

# Элементы глоссария, которые можно удалить
st.header("Глоссарий")
for i, glossary_item in enumerate(glossary['mutable']):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.text(glossary_item.term)

    with col2:
        is_view = st.button("Просмотреть", key=f"view_{i}")

    if is_view:
        line = f"**Термин**: {glossary_item.term}\n\n**Перевод**: {glossary_item.translation}"
        if glossary_item.comment:
            line += f"\n\n**Комментарий**: {glossary_item.comment}"
        st.info(line)

    with col3:
        if st.button("Удалить", key=f"delete_{i}"):
            response = requests.delete('http://localhost:8000/glossary/', json={'id': glossary_item.id})
            print(response)
            if response.ok:
                glossary = get_glossary(cached=False)
                st.rerun()
            else:
                st.error("Не удалось удалить пример")

# Элементы глоссария, которые нельзя удалить
for i, glossary_item in enumerate(glossary['immutable']):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.text(glossary_item.term)

    with col2:
        is_view = st.button("Просмотреть", key=f"view_immutable_{i}")

    if is_view:
        line = f"**Термин**: {glossary_item.term}\n\n**Перевод**: {glossary_item.translation}"
        if glossary_item.comment:
            line += f"\n\n**Комментарий**: {glossary_item.comment}"
        st.info(line)
    