/* ============================================================
   TaskNest — Main JavaScript
   ============================================================ */

// ── Sidebar Toggle ───────────────────────────────────────────
const sidebar  = document.getElementById('sidebar');
const toggler  = document.getElementById('sidebarToggle');

if (toggler && sidebar) {
  toggler.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !toggler.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Auto-dismiss Alert / Toast Messages ─────────────────────
function autoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert, [data-auto-dismiss]');
  if (!alerts.length) return;
  setTimeout(() => {
    alerts.forEach(el => {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 420);
    });
  }, 4500);
}
document.addEventListener('DOMContentLoaded', autoDismissAlerts);

// ── Personal Task Toggle (mark complete/incomplete) ──────────
function toggleTask(pk, el) {
  const csrfToken = getCsrfToken();
  fetch(`/tasks/${pk}/toggle/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    },
  })
  .then(r => r.json())
  .then(data => {
    if (!data.success) return;
    const isDone = data.status === 'completed';
    // Toggle check circle
    el.classList.toggle('checked', isDone);
    // Toggle parent task-item style
    const item = el.closest('.task-item');
    if (item) {
      item.classList.toggle('completed-task', isDone);
      const titleEl = item.querySelector('.task-title');
      if (titleEl) titleEl.style.textDecoration = isDone ? 'line-through' : '';
    }
  })
  .catch(err => console.warn('Toggle failed:', err));
}

// ── CSRF helper ──────────────────────────────────────────────
function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.trim().split('=')[1] : '';
}

// ── Copy Invite Code ─────────────────────────────────────────
function copyCode(code, el) {
  if (!navigator.clipboard) {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = code;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showCopied(el);
    return;
  }
  navigator.clipboard.writeText(code).then(() => showCopied(el));
}

function showCopied(el) {
  const codeEl = el && el.querySelector ? el.querySelector('.invite-code') : null;
  if (!codeEl) return;
  const orig = codeEl.textContent;
  codeEl.textContent = 'Copied! ✓';
  el.style.background = 'var(--petal)';
  el.style.borderColor = 'var(--blossom)';
  setTimeout(() => {
    codeEl.textContent = orig;
    el.style.background = '';
    el.style.borderColor = '';
  }, 1800);
}

// ── Form field animation: float label on focus ───────────────
document.addEventListener('DOMContentLoaded', () => {
  // Add subtle focus ring animation to all form-controls
  document.querySelectorAll('.form-control').forEach(input => {
    input.addEventListener('focus', () => {
      input.closest('.form-group')?.classList.add('focused');
    });
    input.addEventListener('blur', () => {
      input.closest('.form-group')?.classList.remove('focused');
    });
  });

  // Auto-resize textareas
  document.querySelectorAll('textarea.form-control').forEach(ta => {
    ta.addEventListener('input', () => {
      ta.style.height = 'auto';
      ta.style.height = ta.scrollHeight + 'px';
    });
  });
});

// ── Group task status quick-submit ───────────────────────────
function submitStatusForm(pk) {
  const form = document.getElementById(`status-form-${pk}`);
  if (form) form.submit();
}

// ── Confirm before destructive actions ───────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm(btn.dataset.confirm)) e.preventDefault();
    });
  });
});

// ── Mobile: close sidebar on nav link click ──────────────────
document.querySelectorAll('.nav-item').forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth < 1024 && sidebar) {
      sidebar.classList.remove('open');
    }
  });
});

// ── Highlight active nav item from URL ───────────────────────
(function highlightNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(a => {
    if (a.getAttribute('href') && path.startsWith(a.getAttribute('href')) && a.getAttribute('href') !== '/') {
      a.classList.add('active');
    }
  });
})();
