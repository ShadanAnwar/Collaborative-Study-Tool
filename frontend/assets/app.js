/* ═══════════════════════════════════════════════════════════════════════════
   StudySync — Shared JavaScript Utilities
   API helper, auth guards, setLoading
   ═══════════════════════════════════════════════════════════════════════════ */

const API_BASE = '';   // same origin

// ── API helper ─────────────────────────────────────────────────────────────
async function api(endpoint, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('token');
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(API_BASE + endpoint, opts);

  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
    throw new Error('Session expired');
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Something went wrong');
  return data;
}

// ── Auth Guard ─────────────────────────────────────────────────────────────
function requireAuth() {
  if (!localStorage.getItem('token')) {
    window.location.href = '/';
  }
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch {
    return null;
  }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/';
}

// ── Loading state helper ───────────────────────────────────────────────────
function setLoading(btn, loading) {
  const text = btn.querySelector('.btn-text');
  const spinner = btn.querySelector('.btn-spinner');
  if (text) text.classList.toggle('hidden', loading);
  if (spinner) spinner.classList.toggle('hidden', !loading);
  btn.disabled = loading;
  btn.style.opacity = loading ? '0.7' : '1';
}
