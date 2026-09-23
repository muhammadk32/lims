# Add "Referrals & Commission" link under CONFIGURATION in Administration dropdown
p = 'templates/layout/topnav.html'
s = open(p, encoding='utf-8').read()

if 'settings.referrals' in s:
    print('SKIP - Referrals link already in nav')
else:
    # Find the Report Signatures link and insert after it
    idx = s.find('Report Signatures')
    if idx == -1:
        print('WARN - Report Signatures not found')
    else:
        close_idx = s.find('</a>', idx)
        if close_idx == -1:
            print('WARN - closing </a> not found')
        else:
            insert = '''

        <a href="{{ url_for('settings.referrals') }}"
           class="dropdown-item {% if '/settings/referrals' in request.path %}active{% endif %}">
          <i class="bi bi-person-badge"></i> Referrals &amp; Commission
        </a>'''
            s = s[:close_idx + 4] + insert + s[close_idx + 4:]
            open(p, 'w', encoding='utf-8').write(s)
            print('OK - Referrals & Commission added to Administration menu')
