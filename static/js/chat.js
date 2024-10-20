document.addEventListener('DOMContentLoaded', async () => {
    // Create a new session on page load
    const response = await fetch('/sessions/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: 'user1' })
    });
    const data = await response.json();
    const sessionId = data.id;
    localStorage.setItem('sessionId', sessionId);

    // Load previous messages if any
    await loadMessages(sessionId);
});

async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;

    if (message.trim() === '') return;

    const sessionId = localStorage.getItem('sessionId');

    // Send message to the server
    const response = await fetch(`/sessions/${sessionId}/messages/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: message })
    });

    const data = await response.json();

    // Display the message and the assistant's response
    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
    messagesContainer.innerHTML += `<div><strong>Assistant:</strong> ${data.content}</div>`;

    messageInput.value = '';
}

async function loadMessages(sessionId) {
    const response = await fetch(`/sessions/${sessionId}/messages`);
    const data = await response.json();

    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    data.forEach(message => {
        messagesContainer.innerHTML += `<div><strong>${message.role}:</strong> ${message.content}</div>`;
    });
}