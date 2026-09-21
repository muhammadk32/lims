/* ==========================================================
   Lab Test Settings — client-side handlers
   ========================================================== */

window.TestSettings = (function () {
  'use strict';

  console.log('[TestSettings] module loaded');

  // ---------- Shared helpers ----------
  function toast(message, kind) {
    const el = document.getElementById('settingsToast');
    if (!el) {
      console.warn('[TestSettings] #settingsToast not found');
      return;
    }
    el.className = 'test-settings-toast show ' + (kind || 'success');
    el.querySelector('.toast-message').textContent = message;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove('show'), 2400);
  }

  async function postJSON(url, body, csrf) {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf || '',
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify(body || {}),
    });
    let data = {};
    try { data = await resp.json(); } catch (_) {}
    return { ok: resp.ok && data.ok, status: resp.status, data };
  }

  // ==========================================================
  // CATEGORIES
  // ==========================================================
  function initCategories(opts) {
    console.log('[TestSettings] initCategories called');

    const csrf = (opts && opts.csrf) || '';
    const endpoints = (opts && opts.endpoints) || {};

    const modalEl = document.getElementById('catModal');
    if (!modalEl) {
      console.warn('[TestSettings] #catModal missing — aborting');
      return;
    }
    if (!window.bootstrap || !window.bootstrap.Modal) {
      console.error('[TestSettings] Bootstrap Modal not available');
      return;
    }

    // Force-clean the modal on init
    modalEl.classList.remove('show');
    modalEl.style.display = '';
    modalEl.setAttribute('aria-hidden', 'true');
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');

    const modal = new bootstrap.Modal(modalEl);

    const $title = document.getElementById('catModalTitle');
    const $id = document.getElementById('catId');
    const $name = document.getElementById('catName');
    const $desc = document.getElementById('catDescription');
    const $err = document.getElementById('catError');
    const $save = document.getElementById('catSaveBtn');
    const $spin = document.getElementById('catSpinner');
    const $saveText = document.getElementById('catSaveText');

    function resetModal() {
      if ($id) $id.value = '';
      if ($name) $name.value = '';
      if ($desc) $desc.value = '';
      if ($err) { $err.classList.add('d-none'); $err.textContent = ''; }
    }

    function showErr(msg) {
      if ($err) { $err.textContent = msg; $err.classList.remove('d-none'); }
    }

    // ---------- New button ----------
    const newBtn = document.getElementById('btnNewCategory');
    if (newBtn) {
      newBtn.addEventListener('click', () => {
        console.log('[TestSettings] New Category clicked');
        resetModal();
        if ($title) $title.textContent = 'New Category';
        if ($saveText) $saveText.textContent = 'Create';
        modal.show();
        setTimeout(() => $name && $name.focus(), 200);
      });
    } else {
      console.warn('[TestSettings] #btnNewCategory not found');
    }

    // ---------- Edit buttons ----------
    document.querySelectorAll('.btn-edit-cat').forEach(btn => {
      btn.addEventListener('click', () => {
        const row = btn.closest('tr');
        if (!row) return;
        resetModal();
        if ($id) $id.value = row.dataset.catId || '';
        if ($name) $name.value = row.dataset.catName || '';
        if ($desc) $desc.value = row.dataset.catDescription || '';
        if ($title) $title.textContent = 'Edit Category';
        if ($saveText) $saveText.textContent = 'Save Changes';
        modal.show();
        setTimeout(() => $name && $name.focus(), 200);
      });
    });

    // ---------- Save ----------
    if ($save) {
      $save.addEventListener('click', async () => {
        const id = $id ? $id.value : '';
        const name = ($name ? $name.value : '').trim();
        const description = ($desc ? $desc.value : '').trim();

        if (!name) { showErr('Name is required.'); return; }

        $save.disabled = true;
        if ($spin) $spin.classList.remove('d-none');

        let result;
        if (id) {
          const url = (endpoints.update || '').replace('/0/', '/' + id + '/');
          result = await postJSON(url, { name, description }, csrf);
        } else {
          result = await postJSON(endpoints.create, { name, description }, csrf);
        }

        if ($spin) $spin.classList.add('d-none');
        $save.disabled = false;

        if (!result.ok) {
          showErr(result.data.error || 'Save failed.');
          return;
        }

        toast(id ? 'Category updated' : 'Category created', 'success');
        modal.hide();
        setTimeout(() => window.location.reload(), 500);
      });
    }

    // ---------- Delete buttons ----------
    document.querySelectorAll('.btn-delete-cat').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (btn.disabled) return;
        const row = btn.closest('tr');
        if (!row) return;
        const id = row.dataset.catId;
        const name = row.dataset.catName;

        if (!confirm('Delete category "' + name + '"?\n\nThis cannot be undone.')) return;

        btn.disabled = true;
        const url = (endpoints.delete || '').replace('/0/', '/' + id + '/');
        const result = await postJSON(url, {}, csrf);

        if (!result.ok) {
          toast(result.data.error || 'Delete failed', 'danger');
          btn.disabled = false;
          return;
        }

        toast('Category deleted', 'success');
        row.style.transition = 'opacity 0.3s';
        row.style.opacity = '0';
        setTimeout(() => row.remove(), 300);
        setTimeout(() => window.location.reload(), 900);
      });
    });

    // ---------- Enter key ----------
    if ($name) $name.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); $save.click(); }
    });
    if ($desc) $desc.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); $save.click(); }
    });

    console.log('[TestSettings] initCategories complete');
  }

  // ==========================================================
  // PANELS
  // ==========================================================
  function initPanels(opts) {
    console.log('[TestSettings] initPanels called');
    const csrf = (opts && opts.csrf) || '';
    const endpoints = (opts && opts.endpoints) || {};

    document.querySelectorAll('.btn-delete-panel').forEach(btn => {
      btn.addEventListener('click', async () => {
        const row = btn.closest('tr');
        if (!row) return;
        const id = row.dataset.panelId;
        const nameEl = row.querySelector('.fw-semibold');
        const name = nameEl ? nameEl.textContent.trim() : 'this panel';

        if (!confirm('Delete panel "' + name + '"?\n\nThis cannot be undone.')) return;

        btn.disabled = true;
        const url = (endpoints.delete || '').replace('/0/', '/' + id + '/');
        const result = await postJSON(url, {}, csrf);

        if (!result.ok) {
          toast(result.data.error || 'Delete failed', 'danger');
          btn.disabled = false;
          return;
        }

        toast('Panel deleted', 'success');
        row.style.transition = 'opacity 0.3s';
        row.style.opacity = '0';
        setTimeout(() => row.remove(), 300);
        setTimeout(() => window.location.reload(), 900);
      });
    });
  }

  // ==========================================================
  // PANEL EDIT
  // ==========================================================
  function initPanelEdit(opts) {
    console.log('[TestSettings] initPanelEdit called');

    const list = document.getElementById('paramList');
    if (!list) return;

    const search = document.getElementById('paramSearch');
    const countEl = document.getElementById('selectedCount');
    const hidden = document.getElementById('selectedParams');
    const previewList = document.getElementById('previewParamList');
    const previewPrice = document.getElementById('previewPrice');
    const previewTotal = document.getElementById('previewTotal');
    const priceInput = document.querySelector('input[name="price"]');
    const nameInput = document.querySelector('input[name="name"]');
    const codeInput = document.querySelector('input[name="code"]');
    const previewName = document.querySelector('.panel-preview-name');
    const previewCode = document.querySelector('.panel-preview-code');

    const checkboxes = Array.from(list.querySelectorAll('.param-checkbox'));

    function updateHidden() {
      const selected = checkboxes.filter(cb => cb.checked);

      if (hidden) {
        hidden.innerHTML = '';
        selected.forEach(cb => {
          const inp = document.createElement('input');
          inp.type = 'hidden';
          inp.name = 'parameter_ids';
          inp.value = cb.value;
          hidden.appendChild(inp);
        });
      }

      checkboxes.forEach(cb => {
        const item = cb.closest('.param-item');
        if (!item) return;
        const badge = item.querySelector('.param-order-badge');
        const idx = selected.indexOf(cb);
        if (badge) {
          if (idx >= 0) {
            badge.textContent = idx + 1;
            badge.style.display = 'inline-flex';
          } else {
            badge.style.display = 'none';
          }
        }
        item.classList.toggle('checked', idx >= 0);
      });

      if (countEl) countEl.textContent = selected.length;
      updatePreview(selected);
    }

    function updatePreview(selected) {
      if (!previewList) return;
      previewList.innerHTML = '';
      if (selected.length === 0) {
        previewList.innerHTML =
          '<li class="text-muted small">No parameters selected yet</li>';
        return;
      }
      selected.forEach((cb, i) => {
        const item = cb.closest('.param-item');
        const nameEl = item.querySelector('.fw-semibold');
        const codeEl = item.querySelector('code');
        const name = nameEl ? nameEl.textContent.trim() : '—';
        const code = codeEl ? codeEl.textContent.trim() : '—';
        const li = document.createElement('li');
        li.innerHTML =
          '<span class="param-index">' + (i + 1) + '</span>' +
          '<code class="small text-muted">' + code + '</code>' +
          '<span class="ms-1">' + name + '</span>';
        previewList.appendChild(li);
      });
    }

    checkboxes.forEach(cb => cb.addEventListener('change', updateHidden));

    list.querySelectorAll('.param-item').forEach(item => {
      item.addEventListener('click', e => {
        if (e.target.tagName === 'INPUT') return;
        const cb = item.querySelector('.param-checkbox');
        if (!cb) return;
        cb.checked = !cb.checked;
        updateHidden();
      });
    });

    if (search) {
      search.addEventListener('input', e => {
        const q = (e.target.value || '').toLowerCase().trim();
        list.querySelectorAll('.param-item').forEach(item => {
          const hay = item.dataset.search || '';
          const match = !q || hay.includes(q);
          item.classList.toggle('hidden', !match);
        });
      });
    }

    if (priceInput) {
      priceInput.addEventListener('input', () => {
        const val = parseFloat(priceInput.value) || 0;
        if (previewPrice) previewPrice.textContent = val.toFixed(2);
        if (previewTotal) previewTotal.textContent = val.toFixed(2);
      });
    }

    if (nameInput && previewName) {
      nameInput.addEventListener('input', () => {
        previewName.textContent = nameInput.value || 'Your Panel Name';
      });
    }
    if (codeInput && previewCode) {
      codeInput.addEventListener('input', () => {
        previewCode.textContent = (codeInput.value || 'CODE').toUpperCase();
      });
    }

    updateHidden();
  }

  // ==========================================================
  // Public API
  // ==========================================================
  return {
    initCategories,
    initPanels,
    initPanelEdit,
    toast,
  };
})();