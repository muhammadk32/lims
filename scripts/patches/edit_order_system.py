"""
Order Edit System:
- Admin unlock for orders with results
- Inline edit page (patient + tests + discount + referral)
- Un-cancel for admins (with refund reversal)
- Ledger dropdown: Edit / Unlock / Un-cancel
"""
import os

# ============================================================
# 1. Model: add edit_unlocked fields
# ============================================================
mp = 'modules/orders/models.py'
m = open(mp, encoding='utf-8').read()

if 'edit_unlocked' not in m:
    anchor = "    # ---- Cancellation + auto-refund ----"
    if anchor in m:
        m = m.replace(
            anchor,
            "    # ---- Edit lock (admin must unlock if results exist) ----\n"
            "    edit_unlocked = db.Column(db.Boolean, nullable=False, default=False)\n"
            "    edit_unlocked_at = db.Column(db.DateTime, nullable=True)\n"
            "    edit_unlocked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)\n"
            "    edit_unlocked_by = db.relationship('User', foreign_keys=[edit_unlocked_by_id])\n\n"
            + anchor,
            1,
        )
        # Also add a has_any_results property
        prop_anchor = "    @property\n    def status_label(self):"
        if prop_anchor in m:
            prop = '''    @property
    def has_any_results(self):
        """True if any item (top or child) has a result value."""
        return any((i.result_value or '').strip() for i in self.items)

    @property
    def is_editable(self):
        """Not cancelled and (no results yet or admin has unlocked)."""
        return (self.status != OrderStatus.CANCELLED
                and (not self.has_any_results or self.edit_unlocked))

'''
            m = m.replace(prop_anchor, prop + prop_anchor, 1)
        open(mp, 'w', encoding='utf-8').write(m)
        print('OK  - Order model: edit fields + helpers added')
    else:
        print('WARN - anchor not found in Order model')
else:
    print('SKIP - Order already has edit_unlocked')

# ============================================================
# 2. ALTER TABLE
# ============================================================
print()
print('Adding columns to DB...')
from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    for stmt in [
        "ALTER TABLE orders ADD COLUMN edit_unlocked BOOLEAN DEFAULT 0",
        "ALTER TABLE orders ADD COLUMN edit_unlocked_at DATETIME",
        "ALTER TABLE orders ADD COLUMN edit_unlocked_by_id INTEGER",
    ]:
        col = stmt.split('ADD COLUMN')[1].strip().split()[0]
        try:
            db.session.execute(text(stmt))
            db.session.commit()
            print(f'  + {col}')
        except Exception as e:
            if 'duplicate column' in str(e).lower():
                print(f'  = {col} already exists')
            else:
                print(f'  ! {col}: {e}')

# ============================================================
# 3. Services: update_order + unlock/lock + un_cancel
# ============================================================
sp = 'modules/orders/services.py'
s = open(sp, encoding='utf-8').read()

if 'def update_order' not in s:
    new_svcs = '''

# ============================================================
# Edit / unlock / un-cancel
# ============================================================
def update_order(order, form, new_test_ids, user):
    """Update an order's patient info, tests, discount and referral.

    Blocks when results exist unless the order has been unlocked by admin.
    Removing a test is blocked when that test already has a result.

    Returns (ok, error_message).
    """
    from modules.orders.models import OrderStatus, OrderItem
    from modules.patients.models import Patient
    from modules.tests.models import Test

    if order.status == OrderStatus.CANCELLED:
        return False, 'Cancelled orders cannot be edited.'
    if order.has_any_results and not order.edit_unlocked:
        return False, 'Results already entered. An admin must unlock the order first.'

    # ---- 1. Update patient ----
    patient = order.patient
    if patient:
        name = (form.get('patient_name') or '').strip()
        if name:
            patient.full_name = name
        for field in ('phone', 'email', 'address', 'gender', 'blood_group'):
            v = (form.get(f'patient_{field}') or form.get(field) or '').strip()
            if v or v == '':
                setattr(patient, field, v or None)
        try:
            age = form.get('patient_age', type=int)
            if age is not None:
                patient.age = age or None
        except Exception:
            pass

    # ---- 2. Update items ----
    current_top = list(order.top_level_items)
    incoming = set(new_test_ids or [])

    # Remove top-level items whose id is not in incoming
    for item in current_top:
        if item.id not in incoming:
            # block if it has a result (or any child has a result)
            has_result = bool((item.result_value or '').strip())
            if not has_result and item.has_children:
                has_result = any((c.result_value or '').strip() for c in item.children)
            if has_result:
                return False, f'Cannot remove "{item.test.name if item.test else item.id}" — it already has a result.'
            db.session.delete(item)

    db.session.flush()

    # Add new tests that weren't already there
    existing_test_ids = {i.test_id for i in current_top if i.id in incoming}
    for tid in new_test_ids or []:
        if tid in existing_test_ids:
            continue
        t = Test.query.get(tid)
        if not t:
            continue
        if t.is_panel:
            parent = OrderItem(order_id=order.id, test_id=t.id, price=t.price,
                               parent_item_id=None, sort_order=0)
            db.session.add(parent)
            db.session.flush()
            for idx, param in enumerate(t.get_parameters()):
                db.session.add(OrderItem(order_id=order.id, test_id=param.id, price=0.0,
                                         parent_item_id=parent.id, sort_order=idx))
        else:
            db.session.add(OrderItem(order_id=order.id, test_id=t.id, price=t.price,
                                     parent_item_id=None, sort_order=0))
    db.session.flush()

    # ---- 3. Discount ----
    dtype = (form.get('discount_type') or 'amount').strip()
    if dtype not in ('amount', 'percent'):
        dtype = 'amount'
    order.discount_type = dtype
    order.discount_reason = (form.get('discount_reason') or '').strip() or None
    if dtype == 'percent':
        try:
            order.discount_percent = max(0.0, min(100.0, float(form.get('discount_percent') or 0)))
            order.discount_amount = 0.0
        except (ValueError, TypeError):
            order.discount_percent = 0.0
    else:
        try:
            order.discount_amount = round_money(float(form.get('discount_amount') or 0))
            order.discount_percent = 0.0
        except (ValueError, TypeError):
            order.discount_amount = 0.0

    order.recompute_total()

    # ---- 4. Referral ----
    ref_name = (form.get('referred_by') or '').strip() or None
    if ref_name is not None:
        try:
            int(ref_name)
            order.referred_by_name = None
        except (ValueError, TypeError):
            order.referred_by_name = ref_name
            try:
                upsert_referral(ref_name)
            except Exception:
                pass

    # ---- 5. Lock again if admin had unlocked and no results now exist ----
    if order.edit_unlocked and not order.has_any_results:
        order.edit_unlocked = False
        order.edit_unlocked_at = None
        order.edit_unlocked_by_id = None

    db.session.commit()
    log_action('update', 'order', order.id,
               f'Edited order {order.order_code}')
    return True, None


def unlock_order(order, user):
    """Admin unlocks editing of an order with existing results."""
    if not order.has_any_results:
        return False, 'No results exist — order is already editable.'
    order.edit_unlocked = True
    order.edit_unlocked_at = datetime.utcnow()
    order.edit_unlocked_by_id = user.id
    db.session.commit()
    log_action('unlock', 'order', order.id,
               f'Unlocked {order.order_code} for editing (results exist)')
    return True, None


def lock_order(order, user):
    order.edit_unlocked = False
    order.edit_unlocked_at = None
    order.edit_unlocked_by_id = None
    db.session.commit()
    log_action('lock', 'order', order.id,
               f'Locked {order.order_code} again')
    return True, None


def un_cancel_order(order, user):
    """Admin reverses a cancellation and reverses the refund if any was made.

    Reverses the auto-refund by creating a compensating positive Payment.
    Returns (ok, error_message, restored_amount).
    """
    from modules.orders.models import OrderStatus
    from modules.billing.models import Payment, PaymentMethod

    if order.status != OrderStatus.CANCELLED:
        return False, 'Order is not cancelled.', 0.0

    # Find the auto-refund payment (if any) — negative amount
    refund_payments = [p for p in order.payments if (p.amount or 0) < -0.001]
    refund_total = sum(abs(p.amount) for p in refund_payments)

    now = datetime.utcnow()

    if refund_total > 0.001:
        # Compensating positive payment to reverse the refund
        db.session.add(Payment(
            order_id=order.id,
            amount=refund_total,
            method=PaymentMethod.CASH,
            reference='Reversal of refund (un-cancel)',
            notes=f'Reversing refund due to un-cancel by {user.username if user else "admin"}',
            received_by_id=user.id if user else None,
        ))

    order.status = OrderStatus.COMPLETED
    order.cancel_reason = None
    order.cancelled_at = None
    order.cancelled_by_id = None
    order.refunded_at = None

    db.session.commit()
    log_action('un_cancel', 'order', order.id,
               f'Un-cancelled {order.order_code} — reversed refund {refund_total:.2f}')
    return True, None, refund_total
'''
    open(sp, 'w', encoding='utf-8').write(s + new_svcs)
    print('OK  - services.py: update/unlock/lock/un_cancel added')
else:
    print('SKIP - services already has update_order')

# ============================================================
# 4. Routes
# ============================================================
rp = 'modules/orders/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def edit_order' not in r:
    new_routes = '''

# ============================================================
# Edit / Unlock / Un-cancel
# ============================================================
@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('update_order_status')
def edit_order(order_id):
    """Edit order: patient info, tests, discount, referral."""
    from modules.orders.models import OrderStatus
    order = _get_order_or_404(order_id)

    if order.status == OrderStatus.CANCELLED:
        flash('Cancelled orders cannot be edited.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    if order.has_any_results and not order.edit_unlocked:
        flash('Results already entered. Ask an admin to unlock this order first.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    if request.method == 'POST':
        new_test_ids = request.form.getlist('test_ids', type=int)
        ok, error = svc.update_order(order, request.form, new_test_ids, current_user)
        if not ok:
            flash(error, 'warning')
            return redirect(url_for('orders.edit_order', order_id=order.id))
        flash(f'Order {order.order_code} updated.', 'success')
        return redirect(url_for('orders.view_order', order_id=order.id))

    return render_template('orders/edit.html', order=order, config={
        'currency_symbol': request.args.get('_', '') or '',
    })


@orders_bp.route('/<int:order_id>/unlock', methods=['POST'])
@login_required
@permission_required('update_order_status')
def unlock_order(order_id):
    if not (current_user.is_authenticated and current_user.role == 'admin'):
        flash('Only admins can unlock orders.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))
    order = _get_order_or_404(order_id)
    ok, error = svc.unlock_order(order, current_user)
    flash(error if not ok else f'Order {order.order_code} unlocked for editing.',
          'warning' if not ok else 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/lock', methods=['POST'])
@login_required
@permission_required('update_order_status')
def lock_order(order_id):
    order = _get_order_or_404(order_id)
    svc.lock_order(order, current_user)
    flash(f'Order {order.order_code} locked again.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/un-cancel', methods=['POST'])
@login_required
@permission_required('update_order_status')
def un_cancel_order(order_id):
    if not (current_user.is_authenticated and current_user.role == 'admin'):
        flash('Only admins can un-cancel orders.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))
    order = _get_order_or_404(order_id)
    ok, error, restored = svc.un_cancel_order(order, current_user)
    if not ok:
        flash(error, 'warning')
    else:
        msg = f'Order {order.order_code} restored to COMPLETED.'
        if restored > 0:
            msg += f' Reversed refund: {restored:.2f}.'
        flash(msg, 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))
'''
    open(rp, 'w', encoding='utf-8').write(r + new_routes)
    print('OK  - routes.py: edit/unlock/lock/un-cancel routes added')
else:
    print('SKIP - edit routes already exist')

# ============================================================
# 5. Edit template
# ============================================================
os.makedirs('modules/orders/templates/orders', exist_ok=True)
tpl = """{% extends 'base.html' %}
{% block title %}Edit Order {{ order.order_code }} - LabMS{% endblock %}

{% block head %}
<style>
.eo-page { max-width: 1200px; margin: 0 auto; padding: 16px 24px 40px;
           font-family: 'Segoe UI', Arial, sans-serif; font-size: 0.85rem; }
.eo-header { display: flex; justify-content: space-between; align-items: flex-end;
             border-bottom: 2px solid #212529; padding-bottom: 8px; margin-bottom: 14px; }
.eo-title { font-size: 1.15rem; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: 0.02em; }
.eo-sub { font-size: 0.78rem; color: #6c757d; font-family: Consolas, Monaco, monospace; margin-top: 2px; }
.eo-actions { display: flex; gap: 6px; }
.eo-btn { display: inline-block; padding: 6px 14px; font-size: 0.8rem; font-weight: 600;
          border: 1px solid #212529; background: #fff; color: #212529; text-decoration: none;
          border-radius: 0; cursor: pointer; text-transform: uppercase; letter-spacing: 0.03em; }
.eo-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.eo-btn-primary:hover { background: #146c43; color: #fff; }
.eo-btn:hover { background: #f1f3f5; color: #212529; }

.eo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.eo-card { border: 1px solid #212529; background: #fff; }
.eo-card-head { background: #212529; color: #fff; padding: 6px 12px;
                font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.eo-card-body { padding: 12px 14px; }
.eo-field { margin-bottom: 10px; }
.eo-field label { display: block; font-size: 0.66rem; font-weight: 700; color: #6c757d;
                  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px; }
.eo-field input, .eo-field select, .eo-field textarea {
  width: 100%; padding: 6px 9px; border: 1px solid #6c757d; border-radius: 0;
  font-size: 0.85rem; background: #fff;
}
.eo-field input:focus, .eo-field select:focus, .eo-field textarea:focus {
  outline: none; border-color: #198754; box-shadow: 0 0 0 2px rgba(25,135,84,0.15);
}
.eo-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.eo-item-row { display: flex; justify-content: space-between; align-items: center;
               padding: 6px 8px; border-bottom: 1px solid #dee2e6; font-size: 0.85rem; }
.eo-item-row:last-child { border-bottom: none; }
.eo-item-row .name { font-weight: 600; }
.eo-item-row .code { font-family: Consolas, Monaco, monospace; font-size: 0.72rem; color: #6c757d; }
.eo-item-row .remove {
  background: #fff; border: 1px solid #dc3545; color: #dc3545; padding: 2px 8px;
  cursor: pointer; font-size: 0.8rem; border-radius: 0;
}
.eo-item-row .remove:hover { background: #dc3545; color: #fff; }
.eo-item-row .locked { color: #adb5bd; font-size: 0.7rem; font-style: italic; }

.eo-search { margin-top: 8px; }
.eo-search input { width: 100%; padding: 6px 9px; border: 1px solid #6c757d; border-radius: 0; font-size: 0.85rem; }
.eo-search-results { border: 1px solid #6c757d; border-top: none; max-height: 240px;
                     overflow-y: auto; display: none; background: #fff; }
.eo-search-result { display: flex; justify-content: space-between; align-items: center;
                    padding: 6px 10px; border-bottom: 1px solid #e9ecef; cursor: pointer; font-size: 0.82rem; }
.eo-search-result:hover { background: #f1f3f5; }
.eo-search-result:last-child { border-bottom: none; }
.eo-search-result .price { color: #198754; font-weight: 700; font-family: Consolas, Monaco, monospace; }

@media (max-width: 900px) {
  .eo-grid, .eo-2col { grid-template-columns: 1fr; }
}
</style>
{% endblock %}

{% block content %}
<form method="POST" id="editForm">
<input type="hidden" name="_csrf" value="">
<div class="eo-page">

  <div class="eo-header">
    <div>
      <h1 class="eo-title">Edit Order</h1>
      <div class="eo-sub">
        Lab # {{ order.order_code }} ·
        {{ order.patient.full_name }} ·
        {{ order.created_at | localtime('%d-%b-%Y %H:%M') }}
      </div>
    </div>
    <div class="eo-actions">
      <a href="{{ url_for('orders.view_order', order_id=order.id) }}" class="eo-btn">Cancel</a>
      <button type="submit" class="eo-btn eo-btn-primary">Save Changes</button>
    </div>
  </div>

  {% if order.has_any_results %}
  <div class="alert alert-warning py-2 mb-3 small">
    <i class="bi bi-unlock-fill"></i>
    <strong>Admin unlocked</strong> — this order has results entered. Removing a test with a
    result is still blocked. Other changes will save.
  </div>
  {% endif %}

  <div class="eo-grid">

    {# ---- PATIENT ---- #}
    <div class="eo-card">
      <div class="eo-card-head">Patient Information</div>
      <div class="eo-card-body">
        <div class="eo-field">
          <label>Full Name</label>
          <input type="text" name="patient_name" value="{{ order.patient.full_name }}" required>
        </div>
        <div class="eo-2col">
          <div class="eo-field">
            <label>Age</label>
            <input type="number" name="patient_age" value="{{ order.patient.age or '' }}" min="0" max="130">
          </div>
          <div class="eo-field">
            <label>Gender</label>
            <select name="patient_gender">
              <option value="">—</option>
              {% for g in ['Male','Female','Other'] %}
              <option value="{{ g }}" {% if order.patient.gender == g %}selected{% endif %}>{{ g }}</option>
              {% endfor %}
            </select>
          </div>
        </div>
        <div class="eo-2col">
          <div class="eo-field">
            <label>Phone</label>
            <input type="tel" name="patient_phone" value="{{ order.patient.phone or '' }}">
          </div>
          <div class="eo-field">
            <label>Blood Group</label>
            <select name="patient_blood_group">
              <option value="">—</option>
              {% for bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-'] %}
              <option value="{{ bg }}" {% if order.patient.blood_group == bg %}selected{% endif %}>{{ bg }}</option>
              {% endfor %}
            </select>
          </div>
        </div>
        <div class="eo-field">
          <label>Email</label>
          <input type="email" name="patient_email" value="{{ order.patient.email or '' }}">
        </div>
        <div class="eo-field">
          <label>Address</label>
          <textarea name="patient_address" rows="2">{{ order.patient.address or '' }}</textarea>
        </div>
      </div>
    </div>

    {# ---- TESTS ---- #}
    <div class="eo-card">
      <div class="eo-card-head">
        Tests
        <span id="testCount" class="ms-2" style="font-weight:400;">({{ order.top_level_items|length }})</span>
      </div>
      <div class="eo-card-body">
        <div id="currentTests">
          {% for item in order.top_level_items %}
          <div class="eo-item-row" data-id="{{ item.id }}">
            <div>
              <input type="hidden" name="test_ids" value="{{ item.id }}" class="test-id-input">
              <div class="name">
                {{ item.test.name }}
                {% if item.has_children %}<span class="code">(Panel)</span>{% endif %}
              </div>
              <div class="code">{{ item.test.code }} · {{ item.price | money }}</div>
            </div>
            {% if item.result_value or item.children|selectattr('result_value')|list|length > 0 %}
              <span class="locked"><i class="bi bi-lock-fill"></i> has result</span>
            {% else %}
              <button type="button" class="remove" onclick="removeTest(this)">Remove</button>
            {% endif %}
          </div>
          {% endfor %}
        </div>

        <div class="eo-search">
          <input type="text" id="testSearch" placeholder="Type test name or code to add...">
          <div class="eo-search-results" id="testSearchResults"></div>
        </div>
      </div>
    </div>

  </div>

  <div class="eo-grid">

    {# ---- DISCOUNT ---- #}
    <div class="eo-card">
      <div class="eo-card-head">Discount &amp; Referral</div>
      <div class="eo-card-body">
        <div class="eo-2col">
          <div class="eo-field">
            <label>Discount Type</label>
            <select name="discount_type" id="discountType">
              <option value="amount" {% if order.discount_type == 'amount' %}selected{% endif %}>Amount</option>
              <option value="percent" {% if order.discount_type == 'percent' %}selected{% endif %}>Percent</option>
            </select>
          </div>
          <div class="eo-field">
            <label>Discount Value</label>
            <input type="number" name="discount_amount" step="0.01" min="0"
                   value="{{ '%.2f'|format(order.discount_amount or 0) }}">
          </div>
        </div>
        <div class="eo-field">
          <label>Discount Percent (if type = percent)</label>
          <input type="number" name="discount_percent" step="0.01" min="0" max="100"
                 value="{{ '%.2f'|format(order.discount_percent or 0) }}">
        </div>
        <div class="eo-field">
          <label>Discount Reason</label>
          <input type="text" name="discount_reason" value="{{ order.discount_reason or '' }}"
                 maxlength="200" placeholder="Optional">
        </div>
        <div class="eo-field">
          <label>Referred By</label>
          <input type="text" name="referred_by" id="referredBy"
                 value="{{ order.referred_by_name or '' }}"
                 placeholder="Doctor name or leave blank">
        </div>
      </div>
    </div>

    {# ---- SUMMARY ---- #}
    <div class="eo-card">
      <div class="eo-card-head">Order Summary</div>
      <div class="eo-card-body">
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dotted #dee2e6;">
          <span>Current Subtotal</span>
          <span style="font-family:Consolas,monospace;">{{ order.subtotal | money }}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dotted #dee2e6;">
          <span>Current Discount</span>
          <span style="font-family:Consolas,monospace; color:#dc3545;">{{ order.discount_value | money }}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dotted #dee2e6;">
          <span>Current Total</span>
          <span style="font-family:Consolas,monospace; font-weight:700; color:#198754;">{{ order.final_total | money }}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:6px 0;">
          <span>Already Paid</span>
          <span style="font-family:Consolas,monospace;">{{ order.paid_amount | money }}</span>
        </div>
        <div style="margin-top:10px; font-size:0.72rem; color:#6c757d; font-style:italic;">
          Totals will be <strong>recomputed</strong> after saving.
        </div>
      </div>
    </div>

  </div>

</div>
</form>

<script>
const currencySymbol = "{{ config.currency_symbol if config else '' }}";

function removeTest(btn) {
  const row = btn.closest('.eo-item-row');
  if (!row) return;
  if (!confirm('Remove this test from the order?')) return;
  row.remove();
  updateTestCount();
}

function updateTestCount() {
  const n = document.querySelectorAll('#currentTests .eo-item-row').length;
  document.getElementById('testCount').textContent = '(' + n + ')';
}

// ---- Test search (add new test) ----
const $ts = document.getElementById('testSearch');
const $tsr = document.getElementById('testSearchResults');
let _timer = null;

if ($ts) {
  $ts.addEventListener('input', function() {
    clearTimeout(_timer);
    const v = $ts.value.trim();
    if (v.length < 2) { $tsr.style.display = 'none'; return; }
    _timer = setTimeout(async function() {
      try {
        const r = await fetch('/orders/api/test-search?q=' + encodeURIComponent(v));
        const data = await r.json();
        if (!data.length) { $tsr.innerHTML = '<div style="padding:10px;color:#6c757d;">No matches</div>'; $tsr.style.display = 'block'; return; }
        $tsr.innerHTML = '';
        data.forEach(t => {
          const div = document.createElement('div');
          div.className = 'eo-search-result';
          div.innerHTML = '<div><strong>' + t.name + '</strong><div style="font-size:0.72rem;color:#6c757d;">' + t.code + (t.is_panel ? ' · Panel' : '') + '</div></div><div class="price">' + (t.price || 0) + '</div>';
          div.addEventListener('click', () => addTestRow(t));
          $tsr.appendChild(div);
        });
        $tsr.style.display = 'block';
      } catch (e) { console.error(e); }
    }, 220);
  });
}

function addTestRow(t) {
  // Already present?
  const existing = Array.from(document.querySelectorAll('#currentTests .test-id-input'))
                        .map(i => parseInt(i.value, 10));
  if (existing.includes(t.id)) {
    alert('This test is already in the order.');
    $ts.value = ''; $tsr.style.display = 'none'; return;
  }

  const wrap = document.getElementById('currentTests');
  const row = document.createElement('div');
  row.className = 'eo-item-row';
  row.dataset.id = t.id;
  row.innerHTML =
    '<div>' +
      '<input type="hidden" name="test_ids" value="' + t.id + '" class="test-id-input">' +
      '<div class="name">' + t.name + (t.is_panel ? ' <span class="code">(Panel)</span>' : '') + '</div>' +
      '<div class="code">' + t.code + ' · ' + (t.price || 0) + '</div>' +
    '</div>' +
    '<button type="button" class="remove" onclick="removeTest(this)">Remove</button>';
  wrap.appendChild(row);
  updateTestCount();

  $ts.value = '';
  $tsr.style.display = 'none';
}

document.addEventListener('click', function(e) {
  if ($tsr && !$tsr.contains(e.target) && e.target !== $ts) {
    $tsr.style.display = 'none';
  }
});
</script>
{% endblock %}
"""

open('modules/orders/templates/orders/edit.html', 'w', encoding='utf-8').write(tpl)
print('OK  - orders/edit.html created')

# ============================================================
# 6. Ledger dropdown: add Edit / Unlock / Un-cancel
# ============================================================
lp = 'modules/orders/templates/orders/list.html'
l = open(lp, encoding='utf-8').read()

if 'Edit Order' not in l:
    # Insert after the "View Details" item
    anchor = '''                <li>
                  <a class="dropdown-item"
                     href="{{ url_for('orders.view_order', order_id=o.id) }}">
                    <i class="bi bi-file-earmark-text me-2"></i> View Details
                  </a>
                </li>'''
    insert = anchor + '''

                {% if o.status != 'cancelled' and (not o.has_any_results or o.edit_unlocked) %}
                <li>
                  <a class="dropdown-item"
                     href="{{ url_for('orders.edit_order', order_id=o.id) }}">
                    <i class="bi bi-pencil-square me-2 text-primary"></i> Edit Order
                  </a>
                </li>
                {% endif %}

                {% if o.status != 'cancelled' and o.has_any_results and not o.edit_unlocked and current_user.role == 'admin' %}
                <li>
                  <form method="POST" action="{{ url_for('orders.unlock_order', order_id=o.id) }}" class="d-inline">
                    <button type="submit" class="dropdown-item">
                      <i class="bi bi-unlock-fill me-2 text-warning"></i> Unlock for Edit
                    </button>
                  </form>
                </li>
                {% endif %}

                {% if o.status == 'cancelled' and current_user.role == 'admin' %}
                <li>
                  <form method="POST" action="{{ url_for('orders.un_cancel_order', order_id=o.id) }}" class="d-inline"
                        onsubmit="return confirm('Restore this cancelled order? Any refund will be reversed.');">
                    <button type="submit" class="dropdown-item text-success">
                      <i class="bi bi-arrow-counterclockwise me-2"></i> Un-cancel Order
                    </button>
                  </form>
                </li>
                {% endif %}'''
    if anchor in l:
        l = l.replace(anchor, insert, 1)
        open(lp, 'w', encoding='utf-8').write(l)
        print('OK  - ledger dropdown: Edit / Unlock / Un-cancel added')
    else:
        print('WARN - ledger anchor not found (View Details item)')
else:
    print('SKIP - ledger already has Edit Order')


print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  /orders/ -> eye dropdown -> Edit Order')
print('  Order with results -> admin sees "Unlock for Edit"')
print('  Cancelled order -> admin sees "Un-cancel Order"')
print('=' * 55)
