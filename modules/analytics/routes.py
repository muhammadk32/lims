"""Analytics & Management Reports routes."""
from datetime import datetime

from flask import (
    render_template, request, send_file, redirect, url_for, flash,
)
from flask_login import login_required

from core.decorators import permission_required
from . import analytics_bp
from . import queries as q
from .excel import build_workbook


def _range_from_request():
    df = request.args.get('date_from', '').strip()
    dt = request.args.get('date_to', '').strip()
    return q.parse_range(df, dt)


def _ctx(d_from, d_to, **extra):
    ctx = {
        'date_from': d_from.strftime('%d-%b-%Y'),
        'date_to': d_to.strftime('%d-%b-%Y'),
        'date_from_raw': d_from.strftime('%Y-%m-%d'),
        'date_to_raw': d_to.strftime('%Y-%m-%d'),
        'generated_at': datetime.now(),
    }
    ctx.update(extra)
    return ctx


# ============================================================
# Hub
# ============================================================
@analytics_bp.route('/')
@login_required
@permission_required('view_reports')
def index():
    return render_template('analytics/index.html')


# ============================================================
# 1. Doctor / Referral Performance
# ============================================================
@analytics_bp.route('/doctors')
@login_required
@permission_required('view_reports')
def doctors():
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_report(d_from, d_to)
    return render_template('analytics/doctors.html', **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/doctors.xlsx')
@login_required
@permission_required('view_reports')
def doctors_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_report(d_from, d_to)

    data = [[r['name'], r['orders'], r['tests'], r['billed'], r['collected'], r['avg']] for r in rows]
    headers = ['Referral Name', 'Orders', 'Tests', 'Billed', 'Collected', 'Avg / Order']
    total_row = ['TOTAL', totals['orders'], totals['tests'], totals['billed'], totals['collected'], '']
    kpis = [
        ('Referrals', totals['refs'], '0'),
        ('Orders', totals['orders'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Collected', totals['collected'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Doctor / Referral Performance',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[28, 10, 10, 14, 14, 14],
        number_cols=[2, 3, 4, 5, 6],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'doctors_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# 2. Test Volume
# ============================================================
@analytics_bp.route('/tests')
@login_required
@permission_required('view_reports')
def tests():
    d_from, d_to = _range_from_request()
    rows, totals = q.test_volume_report(d_from, d_to)
    return render_template('analytics/tests.html', **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/tests.xlsx')
@login_required
@permission_required('view_reports')
def tests_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.test_volume_report(d_from, d_to)

    data = [[r['code'], r['name'], r['category'], r['count'], r['revenue'], r['avg']] for r in rows]
    headers = ['Code', 'Test Name', 'Category', 'Times Ordered', 'Revenue', 'Avg Price']
    total_row = ['TOTAL', '', '', totals['total_count'], totals['total_revenue'], '']
    kpis = [
        ('Unique Tests', totals['unique_tests'], '0'),
        ('Total Ordered', totals['total_count'], '0'),
        ('Total Revenue', totals['total_revenue'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Test Volume Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[12, 34, 18, 14, 14, 12],
        number_cols=[4, 5, 6],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'tests_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# 3. Abnormal Results
# ============================================================
@analytics_bp.route('/abnormal')
@login_required
@permission_required('view_reports')
def abnormal():
    d_from, d_to = _range_from_request()
    rows, totals = q.abnormal_report(d_from, d_to)
    return render_template('analytics/abnormal.html', **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/abnormal.xlsx')
@login_required
@permission_required('view_reports')
def abnormal_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.abnormal_report(d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['test'],
            r['value'],
            r['range'],
            r['unit'],
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Test', 'Result', 'Normal Range', 'Unit']
    kpis = [
        ('Abnormal Results', totals['count'], '0'),
        ('Distinct Patients', totals['patients'], '0'),
    ]
    buf = build_workbook(
        'Abnormal Results Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[18, 14, 24, 14, 26, 12, 16, 10],
        number_cols=[],
    )
    return send_file(buf, as_attachment=True,
        download_name=f'abnormal_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# 4. Daily Summary
# ============================================================
@analytics_bp.route('/daily')
@login_required
@permission_required('view_reports')
def daily():
    d_from, d_to = _range_from_request()
    rows, totals = q.daily_report(d_from, d_to)
    return render_template('analytics/daily.html', **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/daily.xlsx')
@login_required
@permission_required('view_reports')
def daily_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.daily_report(d_from, d_to)

    data = [[
        r['date'].strftime('%d-%b-%Y'),
        r['orders'], r['cancelled'], r['tests'],
        r['billed'], r['collected'], r['outstanding'],
    ] for r in rows]
    headers = ['Date', 'Orders', 'Cancelled', 'Tests', 'Billed', 'Collected', 'Outstanding']
    total_row = ['TOTAL', totals['orders'], totals['cancelled'], '',
                 totals['billed'], totals['collected'], totals['outstanding']]
    kpis = [
        ('Days', totals['days'], '0'),
        ('Orders', totals['orders'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Collected', totals['collected'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Daily Summary Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[14, 10, 12, 10, 14, 14, 14],
        number_cols=[2, 3, 4, 5, 6, 7],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'daily_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# Doctor Detail
# ============================================================
@analytics_bp.route('/doctors/<path:referral_name>')
@login_required
@permission_required('view_reports')
def doctor_detail(referral_name):
    """Detail report — all patients and orders for one referral."""
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_detail_report(referral_name, d_from, d_to)
    return render_template(
        'analytics/doctor_detail.html',
        **_ctx(d_from, d_to, rows=rows, totals=totals, referral_name=referral_name),
    )


@analytics_bp.route('/doctors/<path:referral_name>.xlsx')
@login_required
@permission_required('view_reports')
def doctor_detail_xlsx(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_detail_report(referral_name, d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['phone'],
            r['age'],
            r['gender'],
            r['tests'],
            r['test_count'],
            r['billed'],
            r['collected'],
            r['due'],
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Phone', 'Age',
               'Gender', 'Tests', 'Count', 'Billed', 'Collected', 'Due']
    total_row = ['TOTAL', '', '', '', '', '', '', '', totals['tests'],
                 totals['billed'], totals['collected'], totals['due']]
    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Patients', totals['patients'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Collected', totals['collected'], '#,##0.00'),
        ('Outstanding', totals['due'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Doctor Detail: ' + referral_name,
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[18, 14, 22, 14, 14, 6, 8, 40, 8, 12, 12, 12],
        number_cols=[9, 10, 11, 12],
        total_row=total_row,
    )
    safe_name = ''.join(c for c in referral_name if c.isalnum() or c in ' -_')[:40]
    return send_file(buf, as_attachment=True,
        download_name=f'doctor_{safe_name}_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# Commission Report
# ============================================================
@analytics_bp.route('/commissions')
@login_required
@permission_required('view_reports')
def commissions():
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_report(d_from, d_to)
    return render_template('analytics/commissions.html',
                           **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/commissions.xlsx')
@login_required
@permission_required('view_reports')
def commissions_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_report(d_from, d_to)

    data = [[r['name'], r['orders'], r['billed'], r['commission'],
             r['paid'], r['outstanding']] for r in rows]
    headers = ['Referral', 'Orders', 'Billed', 'Commission',
               'Paid', 'Outstanding']
    total_row = ['TOTAL', totals['orders'], '', totals['commission'],
                 totals['paid'], totals['outstanding']]
    kpis = [
        ('Referrals', totals['refs'], '0'),
        ('Commission Earned', totals['commission'], '#,##0.00'),
        ('Commission Paid', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Referral Commission Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[28, 10, 14, 14, 14, 14],
        number_cols=[2, 3, 4, 5, 6],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'commissions_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# Commission Detail — per referral
# ============================================================
@analytics_bp.route('/commissions/<path:referral_name>')
@login_required
@permission_required('view_reports')
def commission_detail(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_detail(referral_name, d_from, d_to)
    return render_template(
        'analytics/commission_detail.html',
        **_ctx(d_from, d_to, rows=rows, totals=totals, referral_name=referral_name),
    )


@analytics_bp.route('/commissions/<path:referral_name>.xlsx')
@login_required
@permission_required('view_reports')
def commission_detail_xlsx(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_detail(referral_name, d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['tests_list'],
            r['total'],
            r['discount'],
            r['commission'],
            'PAID' if r['commission_paid'] else 'PENDING',
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Tests',
               'Total', 'Discount', 'Share', 'Status']
    total_row = ['TOTAL', '', '', '',
                 totals['net'], totals['discount'],
                 totals['commission'], '']
    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Subtotal', totals['subtotal'], '#,##0.00'),
        ('Discount', totals['discount'], '#,##0.00'),
        ('Net', totals['net'], '#,##0.00'),
        ('Commission', totals['commission'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Commission Detail: ' + referral_name,
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[18, 14, 24, 34, 12, 12, 12, 10],
        number_cols=[5, 6, 7],
        total_row=total_row,
    )
    safe = ''.join(c for c in referral_name if c.isalnum() or c in ' -_')[:40]
    return send_file(buf, as_attachment=True,
        download_name=f'commission_{safe}_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ============================================================
# Due Collection
# ============================================================
@analytics_bp.route('/due')
@login_required
@permission_required('view_reports')
def due():
    d_from, d_to = _range_from_request()
    rows, totals = q.due_report(d_from, d_to)
    return render_template('analytics/due.html',
                           **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/due.xlsx')
@login_required
@permission_required('view_reports')
def due_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.due_report(d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['phone'],
            r['referral'],
            r['net'],
            r['paid'],
            r['due'],
            r['days_old'],
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Phone',
               'Referral', 'Net', 'Paid', 'Due', 'Days Old']
    total_row = ['TOTAL', '', '', '', '', '',
                 totals['net'], totals['paid'], totals['due'], '']
    kpis = [
        ('Due Orders', totals['count'], '0'),
        ('Total Net', totals['net'], '#,##0.00'),
        ('Collected', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['due'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Due Collection Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[14, 14, 22, 14, 14, 20, 12, 12, 12, 10],
        number_cols=[7, 8, 9],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'due_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
