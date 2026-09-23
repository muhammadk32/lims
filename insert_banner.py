"""Insert the revisit banner into new.html."""
path = 'modules/orders/templates/orders/new.html'

with open(path, encoding='utf-8') as f:
    content = f.read()

if 'revisit-banner' in content:
    print('SKIP - banner already present')
else:
    anchor = '<div class="rec-page" id="recPage" data-currency="{{ config.currency_symbol }}">'

    if anchor not in content:
        print('ERR - rec-page anchor not found')
    else:
        banner = anchor + '''

  {% if revisit_order and prefill_patient %}
  <div class="revisit-banner" id="revisitBanner">
    <i class="bi bi-arrow-repeat"></i>
    <strong>REVISITING from Lab #{{ revisit_order.order_code }}</strong>
    <span class="revisit-info">
      {{ prefill_patient.full_name }} ({{ prefill_patient.patient_code }})
      - {{ prefill_tests|length }} test{{ 's' if prefill_tests|length != 1 }} pre-filled
      {% if skipped_count %} - {{ skipped_count }} archived skipped{% endif %}
    </span>
    <button type="button" class="revisit-close"
            onclick="document.getElementById('revisitBanner').remove();">
      <i class="bi bi-x-lg"></i>
    </button>
  </div>
  {% endif %}'''

        content = content.replace(anchor, banner, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print('OK  - banner inserted')
