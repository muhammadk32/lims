/* ==========================================================
   LabMS — Main JavaScript
   ==========================================================
   Handles:
   - Top navigation mobile toggle + dropdowns
   - Multi-theme picker (8 themes, saved to DB per user)
   - Auto theme (follows OS preference)
   - Flash → Toast conversion
   - Global search shortcut (/)
   - Loading overlay helpers
   ========================================================== */

(function () {
  'use strict';

  /* ========================================================
     LabMS namespace — public API used by templates
     ======================================================== */
  window.LabMS = window.LabMS || {};

  /* ---------- Toast ---------- */
  window.LabMS.showToast = function (message, category) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const cat = (category || 'info').toLowerCase();
    const icon = {
      success: 'check-circle-fill',
      danger:  'x-circle-fill',
      warning: 'exclamation-triangle-fill',
      info:    'info-circle-fill',
      message: 'info-circle-fill',
    }[cat] || 'info-circle-fill';

    const el = document.createElement('div');
    el.className = `toast toast-${cat} align-items-center border-0`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi bi-${icon}"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close me-2 m-auto"
                data-bs-dismiss="toast"></button>
      </div>
    `;
    container.appendChild(el);

    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
  };

  /* ---------- Loading overlay ---------- */
  window.LabMS.showLoading = function () {
    const el = document.getElementById('loadingOverlay');
    if (el) el.classList.remove('d-none');
  };
  window.LabMS.hideLoading = function () {
    const el = document.getElementById('loadingOverlay');
    if (el) el.classList.add('d-none');
  };

  /* ========================================================
     Top navigation — mobile toggle + dropdown behavior
     ======================================================== */
  function initTopNav() {
    const topnav = document.getElementById('appTopnav');
    const toggleBtn = document.getElementById('topnavToggle');

    if (!topnav) return;

    /* ----- Mobile hamburger ----- */
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        topnav.classList.toggle('open');
        const icon = toggleBtn.querySelector('i');
        if (icon) {
          icon.className = topnav.classList.contains('open')
            ? 'bi bi-x-lg'
            : 'bi bi-list';
        }
      });
    }

    /* ----- Dropdown buttons ----- */
    const dropdownButtons = topnav.querySelectorAll('.topnav-item > .topnav-link');
    dropdownButtons.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        // Desktop: CSS hover handles it — do nothing
        if (window.innerWidth >= 992) return;

        // Mobile: toggle the parent .open class
        e.preventDefault();
        const item = btn.parentElement;
        topnav.querySelectorAll('.topnav-item.open').forEach(function (el) {
          if (el !== item) el.classList.remove('open');
        });
        item.classList.toggle('open');
      });
    });

    /* ----- Close mobile nav on outside click ----- */
    document.addEventListener('click', function (e) {
      if (window.innerWidth >= 992) return;
      if (!topnav.contains(e.target) && e.target !== toggleBtn) {
        topnav.classList.remove('open');
      }
    });

    /* ----- Reset state on resize ----- */
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 992) {
        topnav.classList.remove('open');
        topnav.querySelectorAll('.topnav-item.open').forEach(function (el) {
          el.classList.remove('open');
        });
        if (toggleBtn) {
          const icon = toggleBtn.querySelector('i');
          if (icon) icon.className = 'bi bi-list';
        }
      }
    });
  }

  /* ========================================================
     MULTI-THEME SYSTEM
     ========================================================
     Themes: light, dark, auto, grey, blue, green, purple, high_contrast
     - The user's theme is stored in the DB (User.theme)
     - Server-side rendered into <html data-bs-theme="...">
     - JS handles live switching + saving back to server
     - 'auto' resolves to 'dark' or 'light' based on OS preference
     ======================================================== */
  const THEME_STORAGE_KEY = 'labms-theme';

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  function resolveTheme(theme) {
    // 'auto' resolves to the OS preference
    return theme === 'auto' ? getSystemTheme() : theme;
  }

  function applyTheme(theme) {
    const resolved = resolveTheme(theme);
    document.documentElement.setAttribute('data-bs-theme', resolved);

    // Update the picker: mark the chosen theme (not the resolved one)
    document.querySelectorAll('.theme-option').forEach(function (btn) {
      const key = btn.dataset.themeKey;
      const isActive = key === theme;
      btn.classList.toggle('active', isActive);
      const check = btn.querySelector('.theme-check');
      if (check) check.style.display = isActive ? 'inline-block' : 'none';
    });
  }

  function getCsrfToken() {
    // Prefer the meta tag
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;

    // Fall back to a global JS variable
    if (window.LABMS_CSRF_TOKEN) return window.LABMS_CSRF_TOKEN;

    // Last resort: any form's hidden input
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
  }

  function saveThemeToServer(theme) {
    const endpoint = window.LABMS_THEME_ENDPOINT;
    if (!endpoint) {
      // Not logged in or public page — skip silently
      return;
    }

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify({ theme: theme }),
    })
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function (data) {
      if (data && data.ok) {
        // Silent success — the visual change is obvious enough
        // (if you want a toast, uncomment the next line)
        // window.LabMS.showToast('Theme saved: ' + theme, 'success');
      } else {
        window.LabMS.showToast('Theme not saved: ' + (data.error || 'unknown'), 'warning');
      }
    })
    .catch(function (err) {
      console.warn('[theme] save failed:', err);
      window.LabMS.showToast('Could not save theme to server', 'warning');
    });
  }

  function initTheme() {
    const html = document.documentElement;

    // 1) Determine initial theme:
    //    - Prefer server-rendered value (window.LABMS_THEME)
    //    - Fall back to localStorage
    //    - Default to 'light'
    const serverTheme = window.LABMS_THEME || '';
    const localTheme = localStorage.getItem(THEME_STORAGE_KEY) || '';
    const initial = serverTheme || localTheme || 'light';

    applyTheme(initial);
    localStorage.setItem(THEME_STORAGE_KEY, initial);

    // 2) Wire up theme picker clicks
    document.querySelectorAll('.theme-option').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const theme = btn.dataset.themeKey;
        if (!theme) return;

        applyTheme(theme);
        localStorage.setItem(THEME_STORAGE_KEY, theme);
        saveThemeToServer(theme);
      });
    });

    // 3) Watch OS preference changes (only matters if theme is 'auto')
    try {
      const media = window.matchMedia('(prefers-color-scheme: dark)');
      const onChange = function () {
        const current = localStorage.getItem(THEME_STORAGE_KEY) || serverTheme || 'light';
        if (current === 'auto') applyTheme('auto');
      };
      if (media.addEventListener) {
        media.addEventListener('change', onChange);
      } else if (media.addListener) {
        // Safari < 14
        media.addListener(onChange);
      }
    } catch (e) {
      // Ignore — some browsers block matchMedia in unusual contexts
    }
  }

  /* ========================================================
     Global search shortcut (/)
     ======================================================== */
  function initSearchShortcut() {
    const input = document.getElementById('globalSearchInput');
    if (!input) return;

    document.addEventListener('keydown', function (e) {
      // Ignore if typing in another field
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) return;

      if (e.key === '/') {
        e.preventDefault();
        input.focus();
      }
    });
  }

  /* ========================================================
     Boot
     ======================================================== */
  function boot() {
    initTopNav();
    initTheme();
    initSearchShortcut();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();