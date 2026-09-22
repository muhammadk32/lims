/* ============================================================
   Reception page — patient lookup, test search, billing math
   ============================================================ */
(function () {
  'use strict';

  const root = document.getElementById('recPage');
  if (!root) return;

  const CURRENCY = root.dataset.currency || '';

  const state = {
    selectedPatient: null,
    selectedTests: [],
    highlightIndex: -1,
  };

  let _discountLock = null;

  const $lookupPhone = document.getElementById('lookupPhone');
  const $lookupResults = document.getElementById('lookupResults');
  const $selectedPatientBox = document.getElementById('selectedPatientBox');
  const $spName = document.getElementById('spName');
  const $spMeta = document.getElementById('spMeta');
  const $btnChangePatient = document.getElementById('btnChangePatient');
  const $patientIdInput = document.getElementById('patientIdInput');
  const $patientBadge = document.getElementById('patientBadge');
  const $newPatientForm = document.getElementById('newPatientForm');

  const $testSearch = document.getElementById('testSearch');
  const $testSearchResults = document.getElementById('testSearchResults');
  const $selectedTestsList = document.getElementById('selectedTestsList');
  const $testCountBadge = document.getElementById('testCountBadge');
  const $clearTestSearch = document.getElementById('clearTestSearch');

  const $sumSubtotal = document.getElementById('sumSubtotal');
  const $sumDiscount = document.getElementById('sumDiscount');
  const $sumTotal = document.getElementById('sumTotal');
  const $sumBalance = document.getElementById('sumBalance');
  const $discountRow = document.getElementById('discountRow');
  const $discountAmount = document.getElementById('discountAmountInput');
  const $discountPercent = document.getElementById('discountPercentInput');
  const $paymentAmount = document.getElementById('paymentAmount');
  const $fillFullAmount = document.getElementById('fillFullAmount');
  const $submitBtn = document.getElementById('submitBtn');
  const $orderForm = document.getElementById('orderForm');

  // Referral typeahead
  const $referralInput = document.getElementById('referralInput');
  const $referralResults = document.getElementById('referralResults');

  // Age inputs
  const $ageValue = document.getElementById('ageValue');
  const $ageUnit = document.getElementById('ageUnit');
  const $ageHidden = document.getElementById('fld_patient_age');

  // ---------- helpers ----------
  function roundMoney(n) { return Math.round((Number(n) || 0)); }
  function fmt(n) { return CURRENCY + ' ' + (Number(n) || 0).toFixed(2); }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function debounce(fn, delay) {
    let t;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), delay);
    };
  }
  function hideLookup() {
    if ($lookupResults) $lookupResults.style.display = 'none';
  }
  function esc(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // ---------- Age → stored years ----------
  function updateAgeHidden() {
    if (!$ageHidden) return;
    const v = parseInt($ageValue?.value || 0) || 0;
    const unit = $ageUnit?.value || 'years';

    let years = 0;
    if (unit === 'years') years = v;
    else if (unit === 'months') years = v / 12.0;
    else if (unit === 'days') years = v / 365.0;

    $ageHidden.value = years ? years.toFixed(2) : '';
  }
  [$ageValue, $ageUnit].forEach(el => {
    if (el) el.addEventListener('input', updateAgeHidden);
    if (el) el.addEventListener('change', updateAgeHidden);
  });
  updateAgeHidden();

  /* ======================== PATIENT LOOKUP ======================== */
  if ($lookupPhone) {
    const doLookup = debounce(async function () {
      const phone = $lookupPhone.value.trim();
      if (phone.length < 3) { hideLookup(); return; }
      try {
        const resp = await fetch('/orders/api/patient-lookup?phone=' + encodeURIComponent(phone));
        const data = await resp.json();
        if (!Array.isArray(data) || data.length === 0) {
          $lookupResults.innerHTML =
            '<div class="lookup-empty">' +
            '<i class="bi bi-person-plus fs-5 d-block mb-1"></i>' +
            'No existing patient found.</div>';
          $lookupResults.style.display = 'block';
          return;
        }
        $lookupResults.innerHTML = '';
        data.forEach(p => {
          const div = document.createElement('div');
          div.className = 'lookup-result';
          div.innerHTML =
            '<div class="lr-name">' + esc(p.full_name) + '</div>' +
            '<div class="lr-meta">' +
            '<code>' + esc(p.patient_code) + '</code>' +
            (p.age ? ' · ' + p.age + 'y' : '') +
            (p.gender ? ' · ' + esc(p.gender) : '') +
            '</div>';
          div.addEventListener('click', () => selectPatient(p));
          $lookupResults.appendChild(div);
        });
        $lookupResults.style.display = 'block';
      } catch (err) { console.error('[lookup]', err); }
    }, 300);
    $lookupPhone.addEventListener('input', doLookup);
    $lookupPhone.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') hideLookup();
    });
  }

  document.addEventListener('click', (e) => {
    if (!$lookupResults || !$lookupPhone) return;
    if ($lookupPhone.disabled) return;
    const inWrap = $lookupPhone.parentElement.contains(e.target);
    const inDropdown = $lookupResults.contains(e.target);
    if (!inWrap && !inDropdown) hideLookup();
  });

  document.querySelectorAll('#newPatientForm input, #newPatientForm select, #newPatientForm textarea').forEach(el => {
    if (el === $lookupPhone) return;
    el.addEventListener('focus', hideLookup);
  });

  const _requiredSnapshot = new Map();
  function disablePatientFields() {
    if (!$newPatientForm) return;
    $newPatientForm.querySelectorAll('input, select, textarea').forEach(el => {
      if (!_requiredSnapshot.has(el)) _requiredSnapshot.set(el, el.required);
      el.required = false;
      el.disabled = true;
    });
  }
  function enablePatientFields() {
    if (!$newPatientForm) return;
    $newPatientForm.querySelectorAll('input, select, textarea').forEach(el => {
      el.disabled = false;
      if (_requiredSnapshot.has(el)) el.required = _requiredSnapshot.get(el);
    });
  }

  function selectPatient(p) {
    state.selectedPatient = p;
    $patientIdInput.value = p.id;
    $patientBadge.textContent = 'Existing';
    $patientBadge.className = 'badge bg-success';
    $spName.textContent = p.full_name;
    $spMeta.textContent = p.patient_code +
      (p.age ? ' · ' + p.age + 'y' : '') +
      (p.gender ? ' · ' + p.gender : '');
    hideLookup();
    $lookupPhone.disabled = true;
    $newPatientForm.style.display = 'none';
    $selectedPatientBox.style.display = 'block';
    disablePatientFields();
    updateBilling();
  }

  if ($btnChangePatient) {
    $btnChangePatient.addEventListener('click', () => {
      state.selectedPatient = null;
      $patientIdInput.value = '';
      $patientBadge.textContent = 'New';
      $patientBadge.className = 'badge bg-secondary';
      $selectedPatientBox.style.display = 'none';
      $lookupPhone.disabled = false;
      $lookupPhone.value = '';
      hideLookup();
      $newPatientForm.style.display = '';
      enablePatientFields();
      updateBilling();
    });
  }

  /* ======================== REFERRAL TYPEAHEAD ======================== */
  const doReferralSearch = debounce(async function () {
    if (!$referralInput || !$referralResults) return;
    const q = $referralInput.value.trim();
    if (q.length < 3) {
      $referralResults.style.display = 'none';
      return;
    }
    try {
      const resp = await fetch('/orders/api/referral-search?q=' + encodeURIComponent(q));
      if (!resp.ok) return;
      const data = await resp.json();
      if (!Array.isArray(data) || data.length === 0) {
        $referralResults.style.display = 'none';
        return;
      }
      $referralResults.innerHTML = '';
      data.forEach(r => {
        const div = document.createElement('div');
        div.className = 'referral-result';
        div.innerHTML =
          '<div class="rr-name">' + esc(r.name) + '</div>' +
          (r.clinic ? '<div class="rr-meta">' + esc(r.clinic) + '</div>' : '');
        div.addEventListener('mousedown', (e) => {
          e.preventDefault();
          $referralInput.value = r.name;
          $referralResults.style.display = 'none';
        });
        $referralResults.appendChild(div);
      });
      $referralResults.style.display = 'block';
    } catch (err) { console.error('[referral-search]', err); }
  }, 250);

  if ($referralInput) {
    $referralInput.addEventListener('input', doReferralSearch);
    $referralInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && $referralResults) {
        $referralResults.style.display = 'none';
      }
    });
    $referralInput.addEventListener('blur', () => {
      setTimeout(() => {
        if ($referralResults) $referralResults.style.display = 'none';
      }, 150);
    });
  }

  document.addEventListener('click', (e) => {
    if ($referralResults && $referralInput &&
        !$referralResults.contains(e.target) &&
        e.target !== $referralInput) {
      $referralResults.style.display = 'none';
    }
  });

  /* ======================== TEST SEARCH ======================== */
  let currentResults = [];

  const doTestSearch = debounce(async function () {
    const q = $testSearch.value.trim();
    if (q.length < 2) {
      $testSearchResults.style.display = 'none';
      currentResults = [];
      return;
    }
    try {
      const resp = await fetch('/orders/api/test-search?q=' + encodeURIComponent(q));
      const data = await resp.json();
      currentResults = data;
      state.highlightIndex = data.length > 0 ? 0 : -1;
      renderTestResults();
    } catch (err) { console.error('[test-search]', err); }
  }, 250);

  function renderTestResults() {
    if (!currentResults || currentResults.length === 0) {
      $testSearchResults.innerHTML =
        '<div class="test-search-hint">' +
        '<i class="bi bi-search fs-5 d-block mb-1"></i>No tests match</div>';
      $testSearchResults.style.display = 'block';
      return;
    }
    $testSearchResults.innerHTML = '';
    currentResults.forEach((t, idx) => {
      const already = state.selectedTests.some(x => x.id === t.id);
      const div = document.createElement('div');
      div.className = 'test-search-result' +
        (t.is_panel ? ' is-panel' : '') +
        (idx === state.highlightIndex ? ' highlighted' : '');
      if (already) div.style.opacity = '0.5';
      const paramInfo = t.is_panel
        ? '<span class="badge bg-info-subtle text-info-emphasis ms-2" style="font-size:0.66rem;">' +
          t.parameter_count + ' params</span>'
        : '';
      div.innerHTML =
        '<div class="flex-grow-1">' +
        '<div class="tsr-name">' +
        (t.is_panel
          ? '<i class="bi bi-collection text-primary"></i>'
          : '<i class="bi bi-droplet text-muted"></i>') +
        esc(t.name) + paramInfo +
        '</div>' +
        '<div class="tsr-meta">' +
        '<code>' + esc(t.code) + '</code>' +
        (t.category ? ' · ' + esc(t.category) : '') +
        (t.unit ? ' · ' + esc(t.unit) : '') +
        '</div>' +
        '</div>' +
        '<div class="tsr-price">' + fmt(t.price) + '</div>' +
        '<i class="bi bi-plus-circle-fill ms-2 ' +
        (already ? 'text-secondary' : 'text-success') + '"></i>';
      div.addEventListener('click', () => {
        if (already) return;
        addTest(t);
        $testSearch.value = '';
        $testSearchResults.style.display = 'none';
        currentResults = [];
        $testSearch.focus();
      });
      $testSearchResults.appendChild(div);
    });
    $testSearchResults.style.display = 'block';
  }

  function scrollHighlightIntoView() {
    const hl = $testSearchResults.querySelector('.highlighted');
    if (hl) hl.scrollIntoView({ block: 'nearest' });
  }

  if ($testSearch) {
    $testSearch.addEventListener('input', doTestSearch);
    $testSearch.addEventListener('keydown', (e) => {
      if ($testSearchResults.style.display === 'none' || currentResults.length === 0) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        state.highlightIndex = Math.min(currentResults.length - 1, state.highlightIndex + 1);
        renderTestResults();
        scrollHighlightIntoView();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        state.highlightIndex = Math.max(0, state.highlightIndex - 1);
        renderTestResults();
        scrollHighlightIntoView();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (state.highlightIndex >= 0 && state.highlightIndex < currentResults.length) {
          const t = currentResults[state.highlightIndex];
          const already = state.selectedTests.some(x => x.id === t.id);
          if (!already) {
            addTest(t);
            $testSearch.value = '';
            $testSearchResults.style.display = 'none';
            currentResults = [];
          }
        }
      } else if (e.key === 'Escape') {
        $testSearchResults.style.display = 'none';
      }
    });
  }

  if ($clearTestSearch) {
    $clearTestSearch.addEventListener('click', () => {
      $testSearch.value = '';
      $testSearchResults.style.display = 'none';
      currentResults = [];
      $testSearch.focus();
    });
  }

  document.addEventListener('click', (e) => {
    if ($testSearchResults && !$testSearchResults.contains(e.target) && e.target !== $testSearch) {
      $testSearchResults.style.display = 'none';
    }
  });

  /* ======================== SELECTED TESTS ======================== */
  function addTest(t) {
    if (state.selectedTests.some(x => x.id === t.id)) return;
    state.selectedTests.push({
      id: t.id, code: t.code, name: t.name, price: t.price,
      is_panel: t.is_panel,
      parameter_count: t.parameter_count || 0,
    });
    renderSelectedTests();
    updateBilling();
  }

  function removeTest(id) {
    state.selectedTests = state.selectedTests.filter(x => x.id !== id);
    renderSelectedTests();
    updateBilling();
  }

  function renderSelectedTests() {
    const n = state.selectedTests.length;
    $testCountBadge.textContent = n + ' selected';
    if (n === 0) {
      $selectedTestsList.innerHTML =
        '<li class="selected-empty">' +
        '<i class="bi bi-inbox fs-5 d-block mb-1"></i>' +
        'No tests selected yet.</li>';
      return;
    }
    $selectedTestsList.innerHTML = '';
    state.selectedTests.forEach(t => {
      const li = document.createElement('li');
      li.className = 'selected-item' + (t.is_panel ? ' is-panel' : '');
      li.innerHTML =
        '<div>' +
        '<div class="si-name">' +
        (t.is_panel ? '<i class="bi bi-collection text-primary"></i> ' : '') +
        esc(t.name) + '</div>' +
        '<div class="si-meta">' +
        '<code>' + esc(t.code) + '</code>' +
        (t.is_panel && t.parameter_count
          ? ' · Panel · ' + t.parameter_count + ' params' : '') +
        '</div></div>' +
        '<div class="d-flex align-items-center">' +
        '<span class="si-price">' + fmt(t.price) + '</span>' +
        '<button type="button" class="si-remove"><i class="bi bi-x-lg"></i></button>' +
        '</div>';
      li.querySelector('.si-remove').addEventListener('click', () => removeTest(t.id));
      $selectedTestsList.appendChild(li);
    });
  }

  /* ======================== DISCOUNT — linked fields ======================== */
  if ($discountPercent) {
    $discountPercent.addEventListener('input', () => {
      _discountLock = 'percent';
      updateBilling();
    });
    $discountPercent.addEventListener('blur', () => { _discountLock = null; });
  }
  if ($discountAmount) {
    $discountAmount.addEventListener('input', () => {
      _discountLock = 'amount';
      updateBilling();
    });
    $discountAmount.addEventListener('blur', () => { _discountLock = null; });
  }
  if ($paymentAmount) {
    $paymentAmount.addEventListener('input', updateBilling);
  }
  if ($fillFullAmount) {
    $fillFullAmount.addEventListener('click', () => {
      if ($paymentAmount && $sumTotal) {
        $paymentAmount.value = $sumTotal.dataset.value || 0;
        updateBilling();
      }
    });
  }

  /* ======================== BILLING ======================== */
  function updateBilling() {
    const subtotal = state.selectedTests.reduce(
      (s, t) => s + (Number(t.price) || 0), 0
    );
    const roundedSubtotal = roundMoney(subtotal);
    $sumSubtotal.textContent = fmt(roundedSubtotal);

    const pctInput = $discountPercent;
    const amtInput = $discountAmount;
    let discountValue = 0;

    if (_discountLock === 'percent' && pctInput) {
      const pct = clamp(parseFloat(pctInput.value) || 0, 0, 100);
      discountValue = roundedSubtotal * (pct / 100);
      if (amtInput) amtInput.value = roundMoney(discountValue).toFixed(2);
    } else if (_discountLock === 'amount' && amtInput) {
      const amt = Math.max(0, parseFloat(amtInput.value) || 0);
      discountValue = Math.min(amt, roundedSubtotal);
      if (pctInput && roundedSubtotal > 0) {
        const pct = (discountValue / roundedSubtotal) * 100;
        pctInput.value = pct.toFixed(2);
      } else if (pctInput) {
        pctInput.value = '0';
      }
      if (amtInput) amtInput.value = roundMoney(discountValue).toFixed(2);
    } else {
      const amt = Math.max(0, parseFloat(amtInput?.value) || 0);
      const pct = clamp(parseFloat(pctInput?.value) || 0, 0, 100);
      if (amt > 0) {
        discountValue = Math.min(amt, roundedSubtotal);
      } else if (pct > 0) {
        discountValue = roundedSubtotal * (pct / 100);
      }
    }

    if (discountValue > roundedSubtotal) discountValue = roundedSubtotal;
    const roundedDiscount = roundMoney(discountValue);

    if (roundedDiscount > 0) {
      $discountRow.style.display = 'flex';
      $sumDiscount.textContent = '−' + fmt(roundedDiscount);
    } else {
      $discountRow.style.display = 'none';
    }

    const total = Math.max(0, roundedSubtotal - roundedDiscount);
    $sumTotal.textContent = fmt(total);
    $sumTotal.dataset.value = total.toFixed(2);

    if ($paymentAmount && $sumBalance) {
      const paid = Math.max(0, parseFloat($paymentAmount.value) || 0);
      const balance = Math.max(0, total - paid);
      $sumBalance.textContent = fmt(balance);
      $sumBalance.classList.toggle('text-danger', balance > 0.001);
      $sumBalance.classList.toggle('text-success', balance <= 0.001);
    }

    updateSubmitState();
  }

  function updateSubmitState() {
    const nameEl = document.getElementById('fld_patient_name');
    const hasPatient = !!state.selectedPatient ||
                       (nameEl && nameEl.value.trim().length > 0);
    const hasTests = state.selectedTests.length > 0;
    if ($submitBtn) $submitBtn.disabled = !(hasPatient && hasTests);
  }

  document.querySelectorAll('#fld_patient_name, #npFullName')
    .forEach(el => el.addEventListener('input', updateSubmitState));

  /* ======================== SUBMIT ======================== */
  if ($orderForm) {
    $orderForm.addEventListener('submit', (e) => {
      document.querySelectorAll('input[name="test_ids"][type="hidden"]').forEach(el => el.remove());
      state.selectedTests.forEach(t => {
        const inp = document.createElement('input');
        inp.type = 'hidden';
        inp.name = 'test_ids';
        inp.value = t.id;
        $orderForm.appendChild(inp);
      });

      const pctNow = clamp(parseFloat($discountPercent?.value) || 0, 0, 100);
      const amtNow = Math.max(0, parseFloat($discountAmount?.value) || 0);
      const $discountType = document.getElementById('discountType');
      if ($discountType) {
        if (amtNow > 0) {
          $discountType.value = 'amount';
          if ($discountPercent) $discountPercent.value = '0';
          if ($discountAmount) $discountAmount.value = amtNow.toFixed(2);
        } else if (pctNow > 0) {
          $discountType.value = 'percent';
          if ($discountAmount) $discountAmount.value = '0';
        } else {
          $discountType.value = 'amount';
        }
      }

      const printPatient = document.querySelector('input[name="print_patient_copy"]')?.checked || false;
      const printLab = document.querySelector('input[name="print_lab_copy"]')?.checked || false;
      try {
        sessionStorage.setItem('labms_print_patient', printPatient ? '1' : '0');
        sessionStorage.setItem('labms_print_lab', printLab ? '1' : '0');
      } catch (_) {}

      if ($submitBtn) {
        $submitBtn.disabled = true;
        $submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving…';
      }
    });
  }

  /* ======================== INIT ======================== */
  updateBilling();

  setTimeout(function () {
    if ($lookupPhone && !$lookupPhone.disabled) {
      $lookupPhone.focus();
    } else if (document.getElementById('fld_patient_name')) {
      document.getElementById('fld_patient_name').focus();
    } else if ($testSearch) {
      $testSearch.focus();
    }
  }, 100);

})();