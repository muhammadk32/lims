# Daily Summary: dense classical layout
p = 'modules/analytics/templates/analytics/daily.html'
t = """{% extends 'analytics/_base.html' %}
{% block report_title %}Daily Summary Report{% endblock %}
{% block excel_url %}{{ url_for('analytics.daily_xlsx', date_from=date_from_raw, date_to=date_to_raw) }}{% endblock %}

{% block report_body %}
<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Days</div><div class="an-kpi-value">{{ totals.days }}</div></td>
    <td><div class="an-kpi-label">Orders</div><div class="an-kpi-value">{{ totals.orders }}</div></td>
    <td><div class="an-kpi-label">Cancelled</div><div class="an-kpi-value text-danger">{{ totals.cancelled }}</div></td>
    <td><div class="an-kpi-label">Billed</div><div class="an-kpi-value">{{ totals.billed | money }}</div></td>
    <td><div class="an-kpi-label">Collected</div><div class="an-kpi-value text-success">{{ totals.collected | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.outstanding | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th style="width: 130px;">Date</th>
      <th class="num">Orders</th>
      <th class="num">Cancelled</th>
      <th class="num">Tests</th>
      <th class="num">Billed</th>
      <th class="num">Collected</th>
      <th class="num">Outstanding</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="fw-semibold" style="font-family: Consolas, Monaco, monospace;">{{ r.date.strftime('%d-%b-%Y') }}</td>
      <td class="num">{{ r.orders }}</td>
      <td class="num">{% if r.cancelled %}<span class="badge-cancel">{{ r.cancelled }}</span>{% else %}—{% endif %}</td>
      <td class="num">{{ r.tests }}</td>
      <td class="num">{{ r.billed | money }}</td>
      <td class="num text-success">{{ r.collected | money }}</td>
      <td class="num text-danger">{{ r.outstanding | money }}</td>
    </tr>
    {% else %}
    <tr><td colspan="7" class="an-empty">No data for this date range.</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td style="text-align:right; border-top: 2px solid #212529;">TOTAL</td>
      <td class="num" style="border-top: 2px solid #212529;">{{ totals.orders }}</td>
      <td class="num" style="border-top: 2px solid #212529;">{{ totals.cancelled }}</td>
      <td class="num" style="border-top: 2px solid #212529;"></td>
      <td class="num" style="border-top: 2px solid #212529;">{{ totals.billed | money }}</td>
      <td class="num" style="border-top: 2px solid #212529;">{{ totals.collected | money }}</td>
      <td class="num" style="border-top: 2px solid #212529;">{{ totals.outstanding | money }}</td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""
open(p, 'w', encoding='utf-8').write(t)
print('OK  - daily.html updated')
