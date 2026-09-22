path = 'modules/billing/templates/billing/report.html'
s = open(path, encoding='utf-8').read()

extra = """
/* ============================================================
   Border reinforcement - visible 1px grid on every cell
   ============================================================ */
.csr-table,
.csr-kpi {
  border: 1.5px solid #212529 !important;
}
.csr-table th,
.csr-table td,
.csr-kpi td {
  border: 1px solid #6c757d !important;
}
.csr-table thead th {
  border: 1px solid #212529 !important;
  border-bottom: 2px solid #212529 !important;
}
.csr-table tfoot td {
  border-top: 2px solid #212529 !important;
}
.csr-table tbody tr:last-child td {
  border-bottom: 1px solid #6c757d !important;
}
"""

# Insert BEFORE the closing </style>
anchor = "@media print {"
if extra.strip() not in s:
    if anchor in s:
        s = s.replace(anchor, extra + "\n" + anchor, 1)
        open(path, 'w', encoding='utf-8').write(s)
        print('OK - visible borders added')
    else:
        # fallback: append at end of <style>
        end = s.rfind('</style>')
        if end != -1:
            s = s[:end] + extra + s[end:]
            open(path, 'w', encoding='utf-8').write(s)
            print('OK - visible borders appended')
        else:
            print('ERR - no </style> found')
else:
    print('SKIP - borders already added')
