"""
Feature 3: Repeat Last Order on patient registration.
- Q1: Skip inactive/archived tests silently
- Q2: Last = most recent approved OR completed order
"""
import os

# ============================================================
# 1. New API endpoint in orders/routes.py
# ============================================================
rp = 'modules/orders/routes.py'
r = open(rp, encoding='utf-8').read()

if 'api_patient_last_order' not in r:
    new_ep = '''

@orders_bp.route('/api/patient-last-order')
@login_required
def api_patient_last_order():
    """Return the most recent completed/approved order for a patient.

    Includes: order code, date, and tests (only active ones).
    Skips archived tests silently.
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test

    patient_id = request.args.get('patient_id', type=int)
    if not patient_id:
        return jsonify({'ok': False, 'error': 'patient_id required'}), 400

    # Most recent order that has results (completed or approved)
    order = (Order.query
             .filter(Order.patient_id == patient_id)
             .filter(Order.status.in_([OrderStatus.COMPLETED, OrderStatus.APPROVED]))
             .order_by(Order.id.desc())
             .first())

    if not order:
        return jsonify({'ok': True, 'found': False})

    # Collect top-level tests (active only)
    items_out = []
    skipped = 0
    for item in order.top_level_items:
        t = item.test
        if not t or not t.is_active:
            skipped += 1
            continue
        items_out.append({
            'id': t.id,
            'code': t.code,
            'name': t.name,
            'price': t.price or 0,
            'is_panel': bool(t.is_panel),
            'parameter_count': len(t.get_parameters()) if t.is_panel else 0,
        })

    return jsonify({
        'ok': True,
        'found': True,
        'order_id': order.id,
        'order_code': order.order_code,
        'created_at': order.created_at.strftime('%d-%b-%Y') if order.created_at else '',
        'tests': items_out,
        'skipped': skipped,
    })
'''
    open(rp, 'w', encoding='utf-8').write(r + new_ep)
    print('OK  - routes.py: /api/patient-last-order added')
else:
    print('SKIP - endpoint already exists')


# ============================================================
# 2. HTML box in new.html (added inside the tests section, top)
# ============================================================
np = 'modules/orders/templates/orders/new.html'
n = open(np, encoding='utf-8').read()

if 'returningPatientBox' not in n:
    # Insert box right after the test-search input
    anchor = '''      <div class="input-group input-group-sm mb-2">
        <span class="input-group-text"><i class="bi bi-search"></i></span>'''
    box = '''      {# ============ RETURNING PATIENT INFO ============ #}
      <div id="returningPatientBox" class="rp-box" style="display:none;">
        <div class="rp-box-header">
          <i class="bi bi-clock-history"></i>
          <strong>RETURNING PATIENT</strong>
          <span class="rp-name" id="rpPatientName"></span>
        </div>
        <div class="rp-box-body">
          <div class="rp-line">
            <span class="rp-label">Last visit:</span>
            <span class="rp-value" id="rpLastDate">—</span>
            <span class="rp-sep">·</span>
            <span class="rp-label">Lab #:</span>
            <span class="rp-value" id="rpLastCode">—</span>
            <span class="rp-sep">·</span>
            <span class="rp-value" id="rpLastCount">0 tests</span>
          </div>
          <div class="rp-line" id="rpTestsLine">
            <span class="rp-label">Tests:</span>
            <span class="rp-value muted" id="rpLastTests">—</span>
          </div>
          <div class="rp-line" id="rpSkippedLine" style="display:none;">
            <span class="rp-warn">
              <i class="bi bi-exclamation-triangle-fill"></i>
              <span id="rpSkippedText"></span>
            </span>
          </div>
        </div>
        <div class="rp-box-actions">
          <button type="button" class="rp-btn rp-btn-primary" id="rpRepeatBtn">
            <i class="bi bi-arrow-clockwise"></i> Repeat Last Order
          </button>
          <a href="#" target="_blank" class="rp-btn" id="rpHistoryLink">
            <i class="bi bi-clock-history"></i> Full History
          </a>
        </div>
      </div>

      <div class="input-group input-group-sm mb-2">
        <span class="input-group-text"><i class="bi bi-search"></i></span>'''
    if anchor in n:
        n = n.replace(anchor, box, 1)
        open(np, 'w', encoding='utf-8').write(n)
        print('OK  - new.html: returning patient box added')
    else:
        print('WARN - test-search anchor not found in new.html')
else:
    print('SKIP - box already in new.html')


# ============================================================
# 3. CSS in reception.css
# ============================================================
cp = 'static/css/reception.css'
c = open(cp, encoding='utf-8').read()

if '.rp-box' not in c:
    css = '''

/* ============================================================
   Returning Patient Box
   ============================================================ */
.rp-box {
  border: 1px solid #198754;
  background: #f0fdf4;
  margin-bottom: 8px;
}
.rp-box-header {
  background: #198754;
  color: #fff;
  padding: 4px 10px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: flex;
  align-items: center;
  gap: 6px;
}
.rp-name {
  margin-left: auto;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.72rem;
}
.rp-box-body {
  padding: 6px 10px;
  font-size: 0.78rem;
  font-family: 'Segoe UI', Arial, sans-serif;
}
.rp-line {
  display: flex;
  gap: 6px;
  align-items: baseline;
  padding: 1px 0;
  flex-wrap: wrap;
}
.rp-label {
  color: #6c757d;
  font-weight: 600;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.rp-value {
  color: #212529;
  font-family: Consolas, Monaco, monospace;
  font-size: 0.78rem;
}
.rp-value.muted {
  color: #6c757d;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.74rem;
}
.rp-sep { color: #adb5bd; }
.rp-warn {
  color: #b45309;
  font-size: 0.72rem;
  font-weight: 600;
}
.rp-box-actions {
  padding: 6px 10px 8px;
  display: flex;
  gap: 6px;
  border-top: 1px dashed #198754;
  background: #fff;
}
.rp-btn {
  display: inline-block;
  padding: 3px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  border: 1px solid #212529;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.rp-btn:hover { background: #f1f3f5; color: #212529; }
.rp-btn-primary {
  background: #198754;
  border-color: #198754;
  color: #fff;
}
.rp-btn-primary:hover { background: #146c43; color: #fff; }
.rp-btn i { margin-right: 3px; }
'''
    open(cp, 'w', encoding='utf-8').write(c + css)
    print('OK  - reception.css: rp-box styles added')
else:
    print('SKIP - rp-box styles already present')


# ============================================================
# 4. JS in reception.js
# ============================================================
jp = 'static/js/reception.js'
j = open(jp, encoding='utf-8').read()

if 'returningPatientBox' not in j:
    # Insert after the selectPatient function
    anchor = "  function selectPatient(p) {"
    # Find the end of that function
    idx = j.find(anchor)
    if idx == -1:
        print('WARN - selectPatient not found in reception.js')
    else:
        # Insert the fetch + render functions and hook into selectPatient
        # 4a. Add the "show info box" call inside selectPatient
        old_select_end = '''    disablePatientFields();
    updateBilling();
  }'''
        new_select_end = '''    disablePatientFields();
    loadReturningPatientInfo(p);
    updateBilling();
  }

  /* ============ RETURNING PATIENT (Repeat Last Order) ============ */
  var _lastOrderData = null;

  function loadReturningPatientInfo(p) {
    var box = document.getElementById('returningPatientBox');
    if (!box) return;
    _lastOrderData = null;
    box.style.display = 'none';

    fetch('/orders/api/patient-last-order?patient_id=' + encodeURIComponent(p.id))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok || !data.found) return;

        _lastOrderData = data;

        document.getElementById('rpPatientName').textContent = p.full_name + ' (' + p.patient_code + ')';
        document.getElementById('rpLastDate').textContent = data.created_at;
        document.getElementById('rpLastCode').textContent = data.order_code;
        document.getElementById('rpLastCount').textContent = data.tests.length + ' test' + (data.tests.length === 1 ? '' : 's');

        var names = data.tests.map(function (t) { return t.name; }).join(' · ');
        document.getElementById('rpLastTests').textContent = names || '—';

        var histLink = document.getElementById('rpHistoryLink');
        if (histLink) histLink.href = '/results/history/' + p.id;

        if (data.skipped && data.skipped > 0) {
          document.getElementById('rpSkippedLine').style.display = '';
          document.getElementById('rpSkippedText').textContent =
            data.skipped + ' archived test' + (data.skipped === 1 ? '' : 's') + ' will not be repeated.';
        } else {
          document.getElementById('rpSkippedLine').style.display = 'none';
        }

        // Warn if box would duplicate tests already in the current selection
        box.style.display = 'block';
      })
      .catch(function (err) { console.error('[last-order]', err); });
  }

  var rpRepeatBtn = document.getElementById('rpRepeatBtn');
  if (rpRepeatBtn) {
    rpRepeatBtn.addEventListener('click', function () {
      if (!_lastOrderData || !_lastOrderData.tests) return;
      var added = 0;
      var skipped = 0;
      _lastOrderData.tests.forEach(function (t) {
        var already = state.selectedTests.some(function (x) { return x.id === t.id; });
        if (already) { skipped++; return; }
        addTest({
          id: t.id,
          code: t.code,
          name: t.name,
          price: t.price,
          is_panel: t.is_panel,
          parameter_count: t.parameter_count || 0,
        });
        added++;
      });
      if (added === 0 && skipped > 0) {
        alert('All tests from the last order are already selected.');
      }
    });
  }'''
        if old_select_end in j:
            j = j.replace(old_select_end, new_select_end, 1)
            open(jp, 'w', encoding='utf-8').write(j)
            print('OK  - reception.js: returning patient logic added')
        else:
            print('WARN - selectPatient end anchor not found')
else:
    print('SKIP - returning patient logic already present')


print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  1. /orders/new -> search phone -> select patient')
print('  2. Green "RETURNING PATIENT" box appears if they have history')
print('  3. Click "Repeat Last Order" -> tests are pre-selected')
print('=' * 55)
