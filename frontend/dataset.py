import streamlit as st
import requests

# Glossary Management
st.title("Управление датасетом")

def get_dataset(cached=False):
    if not cached or "samples" not in st.session_state:
        response = requests.get('http://localhost:8000/train_samples/')
        if not response.ok:
            st.error("Не удаётся получить датасет.")
            return []

        st.session_state.samples = response.json()

    samples = st.session_state.samples

    return samples

samples = get_dataset(cached=True)

if st.button("Загрузить датасет на платформу OpenAI"):
    response = requests.post('http://localhost:8000/train_samples/upload')
    if response.ok:
        st.success("Датасет загружен успешно!")
    else:
        st.error("Не удалось загрузить датасет!")

# Добавление новго примера
st.header("Добавить пример")

source = st.text_input("Введите текст на исходном языке..")
translation = st.text_input("Введите текст перевода..")
if st.button("Добавить пример"):
    if source and translation:
        response = requests.post('http://localhost:8000/train_samples/', json={'foreign_text': source, 'translation': translation})
        if response.ok:
            st.success("Пример добавлен!")
            samples = get_dataset(cached=False)
        else:
            st.error("Не удалось добавить пример!")
        
st.header("Датасет")

# Отображение списка примеров
for i, sample in enumerate(samples):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.text(f"Пример {sample['id']}: {sample['foreign_text'][:30]}...")  # Показываем первые 50 символов
    with col2:
        is_view = st.button("Просмотреть", key=f"view_{i}")

    if is_view:
        st.info(f"**Исходный текст**: {sample['foreign_text']}\n\n**Перевод**: {sample['translation']}")

    with col3:
        if st.button("Удалить", key=f"delete_{i}"):
            response = requests.delete(f'http://localhost:8000/train_samples/{sample["id"]}')
            if response.ok:
                samples = get_dataset(cached=False)
                st.rerun()
            else:
                st.error("Не удалось удалить пример")
