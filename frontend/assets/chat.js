/* ═══════════════════════════════════════════════════════════════════════════
   StudySync — Chat + WebSocket Client
   Connects to WS, handles chat messages + task updates + online status
   ═══════════════════════════════════════════════════════════════════════════ */

let reconnectAttempts = 0;
const MAX_RECONNECT = 10;

function connectWS() {
  const token = localStorage.getItem('token');
  if (!token) return;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const url = `${protocol}//${window.location.host}/ws/${ROOM_ID}?token=${token}`;

  ws = new WebSocket(url);
  const statusEl = document.getElementById('ws-status');

  ws.onopen = () => {
    console.log('WebSocket connected');
    statusEl.classList.add('connected');
    statusEl.title = 'Connected';
    reconnectAttempts = 0;
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleWSMessage(data);
    } catch (e) {
      console.error('WS parse error:', e);
    }
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
    statusEl.classList.remove('connected');
    statusEl.title = 'Disconnected';

    // Auto-reconnect
    if (reconnectAttempts < MAX_RECONNECT) {
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts})`);
      setTimeout(connectWS, delay);
    }
  };

  ws.onerror = (err) => {
    console.error('WebSocket error:', err);
  };
}

function handleWSMessage(data) {
  switch (data.type) {
    case 'chat':
      addChatMessage(data);
      break;
    case 'task_update':
      handleTaskUpdate(data);
      break;
    case 'system':
      addSystemMessage(data.content);
      if (data.online) updateOnlineUsers(data.online);
      break;
    case 'pong':
      break;
  }
}

// ── Chat Messages ──────────────────────────────────────────────────────────
function addChatMessage(data) {
  const container = document.getElementById('chat-messages');
  const isMine = data.user_id === ME.id;

  // Remove welcome message if present
  const welcome = container.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const el = document.createElement('div');
  el.className = `chat-msg ${isMine ? 'mine' : 'theirs'}`;

  const time = data.time ? new Date(data.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  el.innerHTML = `
    <div class="chat-msg-sender">${isMine ? 'You' : data.user}</div>
    <div class="chat-msg-text">${escapeHtmlChat(data.content)}</div>
    <div class="chat-msg-time">${time}</div>
  `;

  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
}

function addSystemMessage(content) {
  const container = document.getElementById('chat-messages');
  const el = document.createElement('div');
  el.className = 'chat-msg system';
  el.textContent = content;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
}

function sendChat(e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const content = input.value.trim();
  if (!content || !ws || ws.readyState !== WebSocket.OPEN) return;

  ws.send(JSON.stringify({ type: 'chat', content }));
  input.value = '';
}

function escapeHtmlChat(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── Keep-alive ping ────────────────────────────────────────────────────────
setInterval(() => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 25000);
