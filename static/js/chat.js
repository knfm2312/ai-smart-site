const getChatElements = () => ({
    widget: document.getElementById('chat-widget'),
    toggle: document.getElementById('chat-toggle'),
    body: document.getElementById('chat-body'),
    input: document.getElementById('user-input')
});

async function loadChatHistory() {
    const el = getChatElements();
    try {
        const res = await fetch('/get_history');
        const history = await res.json();
        el.body.innerHTML = ''; 
        if (history.length > 0) {
            history.forEach(session => {
                // Support both nested and flat message structures
                const msgs = session.messages || [session];
                msgs.forEach(m => {
                    renderMessage(m.content, (m.role === 'assistant' || m.role === 'AI') ? 'bot' : 'user');
                });
            });
        } else {
            displayWelcome();
        }
    } catch (e) {
        console.error("Failed to fetch history:", e);
        displayWelcome();
    }
}

function displayWelcome() {
    const body = document.getElementById('chat-body');
    if (body && body.innerHTML.trim() === "") {
        renderMessage("Hi! I'm your AI assistant. How can I help you today?", 'bot');
    }
}

function renderMessage(text, sender) {
    const body = document.getElementById('chat-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = sender === 'user' ? 'user-msg' : 'bot-msg';
    msgDiv.innerHTML = text.replace(/\n/g, '<br>');
    body.appendChild(msgDiv);
    body.scrollTop = body.scrollHeight;
    return msgDiv;
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    renderMessage(message, 'user');
    input.value = '';

    const botDiv = renderMessage("<i>Thinking...</i>", 'bot');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        botDiv.innerHTML = data.response.replace(/\n/g, '<br>');
        document.getElementById('chat-body').scrollTop = document.getElementById('chat-body').scrollHeight;
    } catch (error) {
        botDiv.innerText = "Error: Connection lost.";
    }
}

// Attach the Send button and Enter key logic safely
document.addEventListener('DOMContentLoaded', () => {
    const sBtn = document.getElementById('send-btn');
    const uInp = document.getElementById('user-input');
    const cBtn = document.getElementById('clear-btn');

    if (sBtn) sBtn.onclick = sendMessage;
    if (uInp) uInp.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
    if (cBtn) {
        cBtn.onclick = async () => {
            if (confirm("Clear all messages?")) {
                await fetch('/delete_history', { method: 'POST' });
                document.getElementById('chat-body').innerHTML = '';
                displayWelcome();
            }
        };
    }
});