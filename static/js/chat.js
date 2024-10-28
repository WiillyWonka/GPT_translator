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

    // Add paste event listener to preserve line breaks
    const messageInput = document.getElementById('message-input');
    messageInput.addEventListener('paste', function(event) {
        event.preventDefault();
        const text = (event.clipboardData || window.clipboardData).getData('text');
        document.execCommand('insertText', false, text);
    });
});

async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;

    if (message.trim() === '') return;

    const sessionId = localStorage.getItem('sessionId');

    // Display the user's message immediately
    const messagesContainer = document.getElementById('messages');
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.innerHTML = `<strong>You:</strong> ${message.replace(/\n/g, '<br>')}`;
    messagesContainer.appendChild(userMessageDiv);

    // Scroll to the bottom of the chat
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Add indication that the response is being generated
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'message assistant-message';
    loadingIndicator.innerHTML = '<strong>Assistant:</strong> Generating response...';
    messagesContainer.appendChild(loadingIndicator);

    // Scroll to the bottom of the chat again after adding the loading indicator
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Send message to the server
    const response = await fetch(`/sessions/${sessionId}/messages/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: message })
    });

    const data = await response.json();

    // Replace the loading indicator with the actual response
    loadingIndicator.innerHTML = `<strong>Assistant:</strong> ${data.content.replace(/\n/g, '<br>')}`;

    // Scroll to the bottom of the chat after receiving the response
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    messageInput.value = '';
}

async function loadMessages(sessionId) {
    const response = await fetch(`/sessions/${sessionId}/messages`);
    const data = await response.json();

    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';

    data.forEach(message => {
        const messageClass = message.role === 'user' ? 'user-message' : 'assistant-message';
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${messageClass}`;
        messageDiv.innerHTML = `<strong>${message.role}:</strong> ${message.content.replace(/\n/g, '<br>')}`;
        messagesContainer.appendChild(messageDiv);
    });

    // Scroll to the bottom of the chat after loading previous messages
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
