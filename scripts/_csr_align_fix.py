"""Fix KPI strip center alignment + table header center alignment."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# 1. Replace KPI CSS
old_kpi = """.csr-kpi td {
  border-right: 1px solid #212529;
  padding: 8px 14px;
  width: 25%;
  background: #f8f9fa;
}"""
new_kpi = """.csr-kpi td {
  border-right: 1px solid #212529;
  padding: 12px 14px !important;
  width: 25%;
  background: #f8f9fa;
  text-align: center !important;
  vertical-align: middle !important;
}"""

# 2. Replace KPI Label CSS
old_label = """.csr-kpi-label {
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c757d;
  font-weight: 700;
  margin-bottom: 3px;
}"""
new_label = """.csr-kpi-label {
  font-size: 0.72rem !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c757d;
  font-weight: 700;
  margin-bottom: 6px !important;
  display: block !important;
}"""

# 3. Replace KPI Value CSS
old_value = """.csr-kpi-value {
  font-size: 1.15rem;
  font-weight: 700;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}"""
new_value = """.csr-kpi-value {
  font-size: 1.3rem !important;
  font-weight: 700;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
  display: block !important;
}"""

# 4. Add margin to the KPI table to separate from header
old_kpi_table = """.csr-kpi {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
  border: 1px solid #212529;
}"""
new_kpi_table = """.csr-kpi {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px !important;
  margin-bottom: 20px !important;
  border: 1px solid #212529;
}"""

changes = 0
for old, new in [(old_kpi, new_kpi), (old_label, new_label), (old_value, new_value), (old_kpi_table, new_kpi_table)]:
    if old in src:
        src = src.replace(old, new)
        changes += 1
    elif new.split("\n")[1] in src:  # check if partially applied
        pass

# 5. Force table header text alignment
if ".csr-table thead th" in src and "text-align: center !important;" not in src.split(".csr-table thead th")[1][:300]:
    # replace the one we wrote last time
    src = src.replace("text-align: left;", "text-align: center !important;")
    src = src.replace("text-align: center !important;", "text-align: center !important;")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print(f"Patched {changes} KPI CSS rules.")
