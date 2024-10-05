document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');

    let sessionId = null;

    // Создаем новую сессию при загрузке страницы
    fetch('/sessions/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: 'web_user' })
    })
    .then(response => response.json())
    .then(data => {
        sessionId = data.id;
    });

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const message = messageInput.value;
        if (!message) return;

        // Добавляем сообщение пользователя в чат
        addMessage(message, 'user');

        // Отправляем сообщение на сервер
        fetch(`/sessions/${sessionId}/messages/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ role: 'user', content: message })
        })
        .then(response => response.json())
        .then(data => {
            // Добавляем ответ от ассистента в чат
            addMessage(data.content, 'assistant');
        });

        messageInput.value = '';
    });

    function addMessage(content, role) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', role);
        messageElement.textContent = content;
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
});