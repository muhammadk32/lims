# Fix .strftime() calls in templates to use | localtime filter
# Safe: only touches files inside `templates/` and `modules/*/templates/`

$ErrorActionPreference = 'Stop'

# Find every HTML template with .strftime() calls
$files = Get-ChildItem -Recurse -Filter "*.html" |
         Where-Object { $_.FullName -match '\\templates\\' }

$total = 0

foreach ($f in $files) {
    $content = Get-Content -Raw -Path $f.FullName
    $original = $content
    $changed = $false

    # Pattern 1: X.strftime('%Y-%m-%d %H:%M')  →  X | localtime
    $pattern1 = "([A-Za-z_][A-Za-z0-9_\.\[\]']*)\.strftime\(\s*['""]%Y-%m-%d %H:%M['""]\s*\)"
    $new1 = '$1 | localtime'
    $content = [regex]::Replace($content, $pattern1, $new1)

    # Pattern 2: X.strftime('%d/%m/%y %H:%M')  →  X | localtime('%d/%m/%y %H:%M')
    $pattern2 = "([A-Za-z_][A-Za-z0-9_\.\[\]']*)\.strftime\(\s*['""]([^'""]+)['""]\s*\)"
    $new2 = '$1 | localtime(''$2'')'
    $content = [regex]::Replace($content, $pattern2, $new2)

    if ($content -ne $original) {
        # Backup the original first
        Copy-Item -Path $f.FullName -Destination ($f.FullName + '.bak') -Force
        Set-Content -Path $f.FullName -Value $content -NoNewline
        Write-Host "✓ Fixed: $($f.FullName)"
        $total++
    }
}

Write-Host ""
Write-Host "Done. Files changed: $total"
Write-Host "Backups saved with .bak extension."