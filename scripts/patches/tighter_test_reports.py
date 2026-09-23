# Reduce spacing in Test Reports page
p = 'modules/reports/templates/reports/list.html'
s = open(p, encoding='utf-8').read()

# Tighter page padding
s = s.replace('  padding: 16px 24px 40px;', '  padding: 10px 18px 30px;')

# Tighter header
s = s.replace('  padding-bottom: 8px;\n  margin-bottom: 14px;', '  padding-bottom: 5px;\n  margin-bottom: 8px;')

# Tighter filter strip
s = s.replace('  padding: 10px 12px;\n  margin-bottom: 12px;', '  padding: 6px 10px;\n  margin-bottom: 8px;')
s = s.replace('  gap: 10px;\n  align-items: end;', '  gap: 8px;\n  align-items: end;')

# Compact inputs
s = s.replace('  padding: 6px 9px;\n  border: 1px solid #6c757d;\n  border-radius: 0;\n  font-size: 0.85rem;\n  background: #fff;\n}',
              '  padding: 3px 8px;\n  border: 1px solid #6c757d;\n  border-radius: 0;\n  font-size: 0.82rem;\n  background: #fff;\n  height: 28px;\n}')

# Compact buttons
s = s.replace('  padding: 6px 14px;\n  font-size: 0.78rem;\n  font-weight: 600;\n  border: 1px solid #212529;',
              '  padding: 4px 12px;\n  font-size: 0.74rem;\n  font-weight: 600;\n  border: 1px solid #212529;')

# Compact table cells
s = s.replace('  padding: 8px 12px;\n  text-align: left;\n  border: 1px solid #212529;',
              '  padding: 4px 10px;\n  text-align: left;\n  border: 1px solid #212529;')
s = s.replace('  padding: 8px 12px;\n  border: 1px solid #6c757d;\n  vertical-align: middle;',
              '  padding: 3px 10px;\n  border: 1px solid #6c757d;\n  vertical-align: middle;')

# Smaller header font in table
s = s.replace("  font-size: 0.66rem;\n  font-weight: 700;\n  text-transform: uppercase;\n  letter-spacing: 0.06em;\n  padding: 4px 10px;",
              "  font-size: 0.64rem;\n  font-weight: 700;\n  text-transform: uppercase;\n  letter-spacing: 0.05em;\n  padding: 4px 10px;")

# Compact action buttons
s = s.replace('  padding: 4px 9px;\n  font-size: 0.78rem;', '  padding: 2px 7px;\n  font-size: 0.74rem;')

# Compact badges
s = s.replace('  padding: 2px 8px;\n  font-size: 0.66rem;', '  padding: 1px 6px;\n  font-size: 0.64rem;')

# Compact empty state
s = s.replace('  padding: 40px 20px;', '  padding: 24px 16px;')

open(p, 'w', encoding='utf-8').write(s)
print('OK  - Test Reports spacing reduced')
