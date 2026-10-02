content = """{% extends 'base.html' %}
{% block title %}Cash Summary - LabMS{% endblock %}

{% block content %}
<div class="container py-5" style="max-width: 760px;">

  <div class="text-center mb-4">
    <h3 class="fw-bold mb-1"><i class="bi bi-cash-coin text-primary"></i> Cash Summary</h3>
    <p class="text-muted small mb-0">Choose a date range and open the report in a new window</p>
  </div>

  <div class="card border-0 shadow-sm">
    <div class="card-body p-4">
      <form method="GET" action="/billing/report" target="_blank">
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <label class="form-label small fw-semibold text-uppercase text-muted">From date</label>
            <input type="date" name="date_from" class="form-control form-control-lg"
                   value="{{ default_from }}" required>
          </div>
          <div class="col-md-5">
            <label class="form-label small fw-semibold text-uppercase text-muted">To date</label>
            <input type="date" name="date_to" class="form-control form-control-lg"
                   value="{{ default_to }}" required>
          </div>
          <div class="col-md-2">
            <button type="submit" class="btn btn-primary btn-lg w-100">
              <i class="bi bi-file-earmark-bar-graph"></i> Report
            </button>
          </div>
        </div>

        <div class="mt-3 small text-muted">
          <i class="bi bi-info-circle"></i>
          The report opens in a new tab. Print or save as PDF from there.
        </div>
      </form>
    </div>
  </div>

</div>
{% endblock %}
"""

path = 'modules/billing/templates/billing/list.html'
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK - list.html fully replaced')
