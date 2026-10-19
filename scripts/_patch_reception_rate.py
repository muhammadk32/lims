"""Patch reception.js with rate-list helpers. Preserves CRLF."""
import io, os

path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Detect line ending
nl = "\r\n" if "\r\n" in src else "\n"
print("line ending:", repr(nl))

# 1) helpers
old1 = f"  function _companyRate(price, pct) {{{nl}    return Math.round((Number(price) || 0) * (1 - pct / 100) * 100) / 100;{nl}  }}"
new1 = (
f"  function _testPct(testId) {{{nl}"
f"    var labId = (document.getElementById('laboratoryId') || {{}}).value;{nl}"
f"    if (!labId) return 0;{nl}"
f"    var map = (window.LAB_RATE_MAP || {{}})[labId] || {{}};{nl}"
f"    return Number(map[String(testId)] || 0);{nl}"
f"  }}{nl}"
f"{nl}"
f"  function _labHasRateList() {{{nl}"
f"    var labId = (document.getElementById('laboratoryId') || {{}}).value;{nl}"
f"    if (!labId) return false;{nl}"
f"    var m = (window.LAB_RATE_MAP || {{}})[labId];{nl}"
f"    return !!m && Object.keys(m).length > 0;{nl}"
f"  }}{nl}"
f"{nl}"
f"  function _companyRate(price, pct) {{{nl}"
f"    return Math.round((Number(price) || 0) * (1 - pct / 100) * 100) / 100;{nl}"
f"  }}"
)
if old1 in src:
    src = src.replace(old1, new1, 1)
    print("helpers inserted")
else:
    print("HELPERS MISS")

# 2) addTest
old2 = "      company_rate: _companyRate(t.price, pct),"
new2 = "      company_rate: _companyRate(t.price, _labHasRateList() ? _testPct(t.id) : pct),"
if old2 in src:
    src = src.replace(old2, new2, 1)
    print("addTest patched")
else:
    print("addTest MISS")

# 3) refreshCompanyRates
old3 = f"  function refreshCompanyRates() {{{nl}    const pct = _pct();{nl}    state.selectedTests.forEach(t => {{{nl}      t.company_rate = _companyRate(t.price, pct);{nl}    }});"
new3 = f"  function refreshCompanyRates() {{{nl}    const pct = _pct();{nl}    const usingRates = _labHasRateList();{nl}    state.selectedTests.forEach(t => {{{nl}      var p = usingRates ? _testPct(t.id) : pct;{nl}      t.company_rate = _companyRate(t.price, p);{nl}    }});"
if old3 in src:
    src = src.replace(old3, new3, 1)
    print("refreshCompanyRates patched")
else:
    print("refreshCompanyRates MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")
