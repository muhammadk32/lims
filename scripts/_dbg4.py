import json, os, sqlite3
DATA = os.path.join('scripts','adamlab_import')
def load(n):
    with open(os.path.join(DATA, n+'.json'),'r',encoding='utf-8') as f: return json.load(f)

lt = load('labtestdetail')
print('labcode distribution (top 15):')
from collections import Counter
print(Counter(r.get('labcode') for r in lt).most_common(15))

print()
print('GroupID distribution (top 15):')
print(Counter(r.get('GroupID') for r in lt).most_common(15))

heads = load('TestHead')
print()
print('TestHead ID → DepartmentID map (first 10):')
for h in heads[:10]:
    print(h.get('ID'), '→', h.get('DepartmentID'), h.get('Name'))

print()
print('Departments present in TestHead (unique DepartmentID):')
print(sorted({h.get('DepartmentID') for h in heads if h.get('DepartmentID') is not None}))

depts = load('labdepartment')
print()
print('All labdepartments:')
for d in depts:
    print(d.get('departmentcode'), d.get('departmentname'))

# how many tests have a GroupID pointing to a TestHead that has a DepartmentID
head_dept = {h.get('ID'): h.get('DepartmentID') for h in heads}
covered = sum(1 for r in lt if head_dept.get(r.get('GroupID')) is not None)
print()
print('tests whose GroupID resolves to a department:', covered, '/', len(lt))