let socket = io();
let currentRoom = 'General';
let username = document.getElementById('username').textContent;
let roomMessages = {};

function updateRoomHighlight(room) {
    document.querySelectorAll('.room-item').forEach((item) => {
        item.classList.toggle('active-room', item.dataset.room === room);
    });
}

socket.on('connect', () => {
    joinRoom('General');
});

socket.on('message', (data) => {
    addMessage(data.username, data.msg, data.username === username ? 'own' : 'other');
});

socket.on('private_message', (data) => {
    addMessage(data.from, `[Private] ${data.msg}`, 'private');
});

socket.on('status', (data) => {
    addMessage('System', data.msg, 'system');
});

socket.on('active_users', (data) => {
    const userList = document.getElementById('active-users');
    userList.innerHTML = data.users
        .map((user) => `
            <div class="user-item" onclick="insertPrivateMessage('${user}')">
                ${user}${user === username ? ' (you)' : ''}
            </div>
        `)
        .join('');
});

function addMessage(sender, message, type) {
    if (!roomMessages[currentRoom]) {
        roomMessages[currentRoom] = [];
    }
    roomMessages[currentRoom].push({ sender, message, type });

    const chat = document.getElementById('chat');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = `${sender}: ${message}`;
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('message');
    const message = input.value.trim();

    if (!message) {
        return;
    }

    if (message.startsWith('@')) {
        const [target, ...msgParts] = message.substring(1).split(/\s+/);
        const privateMsg = msgParts.join(' ');

        if (privateMsg && target) {
            socket.emit('message', {
                msg: privateMsg,
                type: 'private',
                target,
                room: currentRoom,
            });
        }
    } else {
        socket.emit('message', {
            msg: message,
            room: currentRoom,
        });
    }

    input.value = '';
    input.focus();
}

function joinRoom(room) {
    const safeRoom = room || 'General';

    if (currentRoom && currentRoom !== safeRoom) {
        socket.emit('leave', { room: currentRoom });
    }

    currentRoom = safeRoom;
    socket.emit('join', { room: safeRoom });

    const chat = document.getElementById('chat');
    chat.innerHTML = '';

    if (roomMessages[safeRoom]) {
        roomMessages[safeRoom].forEach((msg) => {
            addMessage(msg.sender, msg.message, msg.type);
        });
    }

    updateRoomHighlight(safeRoom);
}

function insertPrivateMessage(user) {
    const input = document.getElementById('message');
    input.value = `@${user}`;
    input.focus();
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.room-item').forEach((item) => {
        item.addEventListener('click', () => joinRoom(item.dataset.room));
    });
    updateRoomHighlight(currentRoom);
});
