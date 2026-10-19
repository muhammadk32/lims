import json, os
DATA = os.path.join('scripts','adamlab_import')
def load(n):
    with open(os.path.join(DATA, n+'.json'),'r',encoding='utf-8') as f: return json.load(f)

sub_tests = load('subdepartmenttestdetail')
print('subdepartmenttestdetail sample:')
for r in sub_tests[:5]: print(r)
print('distinct subdepartmentcode:', len({r.get('subdepartmentcode') for r in sub_tests}))

lt = load('labtestdetail')
print('labtestdetail keys:', list(lt[0].keys()))

# do tests have a labcode linking to subdepartment?
codes_with_sub = {r.get('testcode') for r in sub_tests}
matched = sum(1 for r in lt if r.get('testcode') in codes_with_sub)
print('tests matched to a sub-department:', matched, '/', len(lt))