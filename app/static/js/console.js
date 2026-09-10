/* ============================================================
   Rental Console — shared JS
   - Sidebar toggle (mobile)
   - Dark mode toggle (persisted)
   - Toast helper
   - fetch wrapper with cookie-based auth
   ============================================================ */

// ---------- Dark mode ----------
(function () {
  const stored = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (stored === 'dark' || (!stored && prefersDark)) {
    document.documentElement.classList.add('dark');
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
  }
});

// ---------- Sidebar toggle ----------
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  const menuBtn = document.getElementById('menu-btn');

  const open = () => {
    sidebar?.classList.remove('-translate-x-full');
    overlay?.classList.remove('hidden');
  };
  const close = () => {
    sidebar?.classList.add('-translate-x-full');
    overlay?.classList.add('hidden');
  };

  menuBtn?.addEventListener('click', open);
  overlay?.addEventListener('click', close);
});

// ---------- Toast ----------
window.toast = function (message, type = 'info') {
  const container = document.getElementById('toasts');
  if (!container) return;
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity 200ms, transform 200ms';
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    setTimeout(() => el.remove(), 250);
  }, 3200);
};

// ---------- fetch wrapper (cookie-based) ----------
window.apiFetch = async function (url, options = {}) {
  const opts = {
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  };
  const res = await fetch(url, opts);
  if (res.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  return res;
};

// ---------- Confirm helper ----------
window.confirmAction = function (message) {
  return window.confirm(message);
};
