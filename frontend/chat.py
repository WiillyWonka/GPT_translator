import streamlit as st
import requests

st.title("Чат")

# Initialize session state
if 'session_id' not in st.session_state:
    response = requests.post('http://localhost:8000/sessions/', json={'user_id': 'user1'})
    st.session_state.session_id = response.json()['id']

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def generate_response(user_message):

    response = requests.post(f'http://localhost:8000/sessions/{st.session_state.session_id}/messages/', json={'content': user_message})
    assistant_response = response.json()['content']

    return assistant_response

if prompt := st.chat_input("Введите сообщение..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = generate_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(response)