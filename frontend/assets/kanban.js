/* ═══════════════════════════════════════════════════════════════════════════
   StudySync — Kanban Board Logic
   Drag-and-drop with vanilla JS, task CRUD, real-time sync
   ═══════════════════════════════════════════════════════════════════════════ */

// ── Load + Render tasks ────────────────────────────────────────────────────
async function loadTasks() {
  tasks = await api(`/api/rooms/${ROOM_ID}/tasks`);
  renderKanban();
}

function renderKanban() {
  const cols = { todo: [], inprogress: [], done: [] };
  tasks.forEach(t => {
    const status = t.status || 'todo';
    if (cols[status]) cols[status].push(t);
  });

  Object.keys(cols).forEach(status => {
    const container = document.getElementById(`tasks-${status}`);
    container.innerHTML = '';
    cols[status].forEach(task => {
      container.appendChild(createTaskCard(task));
    });
    document.getElementById(`count-${status}`).textContent = cols[status].length;
  });
}

function createTaskCard(task) {
  const card = document.createElement('div');
  card.className = 'task-card';
  card.draggable = true;
  card.dataset.taskId = task.id;
  card.dataset.status = task.status;

  const assignee = members.find(m => m.user_id === task.assigned_to);
  const creator = members.find(m => m.user_id === task.created_by);

  card.innerHTML = `
    <div class="task-card-title">${escapeHtml(task.title)}</div>
    <div class="task-card-meta">
      ${assignee ? `👤 ${assignee.user.username}` : ''}
      ${creator ? `• Created by ${creator.user.username}` : ''}
    </div>
    <button class="task-card-delete" onclick="deleteTask(${task.id}, event)" title="Delete task">✕</button>
  `;

  // Drag events
  card.addEventListener('dragstart', onDragStart);
  card.addEventListener('dragend', onDragEnd);

  return card;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── Add Task ───────────────────────────────────────────────────────────────
async function addTask(e) {
  e.preventDefault();
  const input = document.getElementById('new-task-input');
  const title = input.value.trim();
  if (!title) return;

  try {
    const task = await api(`/api/rooms/${ROOM_ID}/tasks`, 'POST', { title });
    tasks.push(task);
    renderKanban();
    input.value = '';
  } catch (err) {
    alert(err.message);
  }
}

// ── Delete Task ────────────────────────────────────────────────────────────
async function deleteTask(taskId, e) {
  e.stopPropagation();
  try {
    await api(`/api/tasks/${taskId}`, 'DELETE');
    tasks = tasks.filter(t => t.id !== taskId);
    renderKanban();
  } catch (err) {
    alert(err.message);
  }
}

// ── Drag & Drop ────────────────────────────────────────────────────────────
let draggedTaskId = null;

function onDragStart(e) {
  draggedTaskId = parseInt(e.target.dataset.taskId);
  e.target.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', draggedTaskId);
}

function onDragEnd(e) {
  e.target.classList.remove('dragging');
  draggedTaskId = null;
  document.querySelectorAll('.task-list').forEach(el => el.classList.remove('drag-over'));
}

function onDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}

// Remove drag-over when leaving
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.task-list').forEach(list => {
    list.addEventListener('dragleave', (e) => {
      if (!list.contains(e.relatedTarget)) {
        list.classList.remove('drag-over');
      }
    });
  });
});

async function onDrop(e, newStatus) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');

  const taskId = parseInt(e.dataTransfer.getData('text/plain'));
  if (!taskId) return;

  const task = tasks.find(t => t.id === taskId);
  if (!task || task.status === newStatus) return;

  // Optimistic update
  task.status = newStatus;
  renderKanban();

  try {
    await api(`/api/tasks/${taskId}`, 'PATCH', { status: newStatus });
    // Send via WebSocket for real-time sync
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'task_update', task_id: taskId, status: newStatus }));
    }
  } catch (err) {
    console.error('Failed to update task:', err);
    await loadTasks(); // Revert on failure
  }
}

// ── Handle real-time task updates from WebSocket ───────────────────────────
function handleTaskUpdate(data) {
  const task = tasks.find(t => t.id === data.task_id);
  if (task) {
    task.status = data.status;
    renderKanban();
  } else {
    // A new task was moved that we don't have yet — reload
    loadTasks();
  }
}
