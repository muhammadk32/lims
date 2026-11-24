# =====================================================================
#  apply_pbox_rowspace2.ps1
#  Target:    D:\lims\lab_management_system\modules\results\templates\results\report.html
#  Reference: D:\lims\lab_management_system\modules\orders\templates\orders\print.html
#
#  Goal: give the PCR report patient box the SAME row spacing as the
#        regular report (image 2): a visible blank gap (~one line) between
#        every text line, i.e. an even ~21px line pitch.
#
#  What it does (idempotent - safe to run again):
#   1) Removes the OLD 'uniform 21px pitch' override block from the
#      previous script if present (superseded by this approach)
#   2) Copies the REAL patient-box CSS (spacing + typography) from
#      orders/print.html into report.html, scoped under the report
#      box class so nothing else in the report is affected   (strategy A)
#   3) If print.html yields no usable spacing rules, injects a measured
#      fallback: uniform 21px line pitch                          (strategy B)
#   4) (if missing) uniform sans-serif font + mojibake icon fix
#
#  Run:
#    powershell -ExecutionPolicy Bypass -File .\apply_pbox_rowspace2.ps1
#  Then paste the FULL console output back to the chat.
# =====================================================================
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$root = 'D:\lims\lab_management_system'
$p    = Join-Path $root 'modules\results\templates\results\report.html'
$po   = Join-Path $root 'modules\orders\templates\orders\print.html'

if (-not (Test-Path $p))  { throw "file not found: $p" }
if (-not (Test-Path $po)) { throw "reference file not found: $po" }
Copy-Item $p "$p.bak_pspace2" -Force
Write-Host "backup created: $p.bak_pspace2"
Write-Host ""

$L = [System.Collections.Generic.List[string]]([System.IO.File]::ReadAllLines($p))
$O = [System.Collections.Generic.List[string]]([System.IO.File]::ReadAllLines($po))
Write-Host ("report.html lines: " + $L.Count + "   orders print.html lines: " + $O.Count)
Write-Host ""

# ---------------------------------------------------------------------
function Dump-Lines {
    param($Arr, [int]$a, [int]$b, [string]$tag)
    Write-Host "----- $tag  (lines $($a+1)..$($b+1)) -----"
    for ($i = $a; $i -le $b; $i++) {
        if ($i -ge 0 -and $i -lt $Arr.Count) { Write-Host ('{0,4}: {1}' -f ($i+1), $Arr[$i]) }
    }
}

function Get-ClassTokens {
    param([string]$s)
    $out = @()
    foreach ($m in [regex]::Matches($s, 'class\s*=\s*"([^"]*)"')) {
        foreach ($t in ($m.Groups[1].Value -split '\s+')) {
            if ($t) { $out += $t }
        }
    }
    return ,$out
}

function Dump-CssRules {
    param($Arr, [string[]]$Classes, [string]$Tag, [int]$MaxPer = 2)
    $sr = Get-StyleRanges $Arr
    if ($sr.Count -eq 0) { Write-Host "($Tag) no style block found"; return }
    foreach ($c in $Classes) {
        if (-not $c) { continue }
        $pat = '\.' + [regex]::Escape($c) + '\s*[,{\s:]'
        $found = 0
        foreach ($rg in $sr) {
            for ($i = $rg[0]; $i -le $rg[1] -and $found -lt $MaxPer; $i++) {
                if ($Arr[$i] -match $pat) {
                    $j = $i
                    while ($j -lt [Math]::Min($i + 12, $rg[1]) -and $Arr[$j] -notmatch '\}') { $j++ }
                    Dump-Lines $Arr $i $j "$Tag css rule"
                    Write-Host "       (class: $c)"
                    $found++
                    $i = $j
                }
            }
        }
        if ($found -eq 0) { Write-Host "($Tag) no css rule found for .$c" }
    }
}

function Get-StyleRanges {
    param($Arr)
    $ranges = New-Object System.Collections.Generic.List[object]
    $s = -1
    for ($i = 0; $i -lt $Arr.Count; $i++) {
        if ($s -lt 0 -and $Arr[$i] -match '<style') { $s = $i }
        elseif ($s -ge 0 -and $Arr[$i] -match '</style>') { $null = $ranges.Add(@($s, $i)); $s = -1 }
    }
    return ,$ranges
}

function Get-BoxInfo {
    param($Arr, [string]$Tag)
    $hits = New-Object System.Collections.Generic.List[int]
    for ($i = 0; $i -lt $Arr.Count; $i++) {
        if ($Arr[$i] -match 'Patient\s+Name') { $hits.Add($i) }
    }
    if ($hits.Count -eq 0) { throw "anchor 'Patient Name' not found ($Tag)" }
    Write-Host ("$Tag 'Patient Name' found at line(s): " + (($hits | ForEach-Object { $_ + 1 }) -join ', '))
    $idx = $hits[0]

    # container class: nearest preceding class token that looks box-like
    $boxCls = ''
    for ($i = $idx - 1; $i -ge [Math]::Max(0, $idx - 30); $i--) {
        foreach ($t in (Get-ClassTokens $Arr[$i])) {
            if ($t -match '(?i)(patient|patbox|pat-box|pbox|meta|infobox|info-box|info)') { $boxCls = $t; break }
        }
        if ($boxCls) { break }
    }
    if (-not $boxCls) {
        for ($i = $idx - 1; $i -ge [Math]::Max(0, $idx - 30); $i--) {
            foreach ($t in (Get-ClassTokens $Arr[$i])) {
                if ($t -match '(?i)(box|head)') { $boxCls = $t; break }
            }
            if ($boxCls) { break }
        }
    }
    if (-not $boxCls) {
        for ($i = $idx - 1; $i -ge [Math]::Max(0, $idx - 30); $i--) {
            $tks = Get-ClassTokens $Arr[$i]
            if ($tks.Count -gt 0) { $boxCls = $tks[0]; break }
        }
    }

    $rs = [Math]::Max(0, $idx - 24)
    $re = [Math]::Min($Arr.Count - 1, $idx + 18)
    $classes = @(); $ids = @(); $tags = @()
    for ($i = $rs; $i -le $re; $i++) {
        foreach ($t in (Get-ClassTokens $Arr[$i])) { if ($classes -notcontains $t) { $classes += $t } }
        foreach ($m in [regex]::Matches($Arr[$i], 'id\s*=\s*"([^"]+)"')) { if ($ids -notcontains $m.Groups[1].Value) { $ids += $m.Groups[1].Value } }
        foreach ($m in [regex]::Matches($Arr[$i], '<([a-zA-Z][a-zA-Z0-9]*)')) {
            $t = $m.Groups[1].Value.ToLower()
            if ($tags -notcontains $t) { $tags += $t }
        }
    }
    Dump-Lines $Arr $rs $re "$Tag BOX HTML"
    Write-Host ("$Tag discovered container class: '$boxCls'")
    Write-Host ("$Tag classes in region: [" + ($classes -join ', ') + "]")
    Write-Host ("$Tag ids in region:     [" + ($ids -join ', ') + "]")
    Write-Host ("$Tag tags in region:    [" + ($tags -join ', ') + "]")
    Write-Host ""

    return @{ Idx = $idx; BoxCls = $boxCls; Classes = $classes; Ids = $ids; Tags = $tags; Start = $rs; End = $re }
}

function Extract-Rules {
    param($Arr, [string[]]$Cls, [string[]]$Ids, [string]$Tag)

    $ranges = Get-StyleRanges $Arr
    $all = New-Object System.Collections.Generic.List[string]
    foreach ($rg in $ranges) {
        $i = $rg[0]
        while ($i -le $rg[1]) {
            $line = $Arr[$i]
            if ($line -match '@(media|supports|keyframes|font-face)') {
                $depth = 0; $started = $false
                while ($i -le $rg[1]) {
                    foreach ($ch in [regex]::Matches($Arr[$i], '\{|\}')) {
                        if ($ch.Value -eq '{') { $depth++; $started = $true } else { $depth-- }
                    }
                    if ($started -and $depth -le 0) { break }
                    $i++
                }
                $i++; continue
            }
            if ($line -match '\{') {
                $buf = $line
                while ($i -le $rg[1] -and $buf -notmatch '\}') {
                    $i++
                    if ($i -le $rg[1]) { $buf += ' ' + $Arr[$i].Trim() }
                }
                $m = [regex]::Match($buf, '([^{}]+)\{([^}]*)\}')
                if ($m.Success) {
                    $sel  = $m.Groups[1].Value.Trim()
                    $body = ($m.Groups[2].Value -replace '\s+', ' ').Trim()
                    $null = $all.Add($sel + ' { ' + $body + ' }')
                }
            }
            $i++
        }
    }

    $keep = New-Object System.Collections.Generic.List[string]
    foreach ($r in $all) {
        $sel = ($r -split '\{')[0].Trim()
        if ($sel -match '^\s*(@|body|html|\*)') { continue }
        $hit = $false
        foreach ($c in $Cls) {
            if ($c -and $sel -match ('\.' + [regex]::Escape($c) + '(?![\w-])')) { $hit = $true; break }
        }
        if (-not $hit) {
            foreach ($c in $Ids) {
                if ($c -and $sel -match ('#' + [regex]::Escape($c) + '(?![\w-])')) { $hit = $true; break }
            }
        }
        if (-not $hit -and $sel -notmatch '[.#\[@]') {
            # bare element rule (e.g. 'td { ... }') - safe once scoped under the box
            if ($sel -match '\b(p|div|span|td|th|tr|table|thead|tbody|small|b|strong|label|ul|li)\b') { $hit = $true }
        }
        if ($hit) { $null = $keep.Add($r) }
    }

    Write-Host ("$Tag style blocks: " + $ranges.Count + ", total rules parsed: " + $all.Count + ", box-relevant rules: " + $keep.Count)
    foreach ($r in $keep) { Write-Host ("   REF-RULE: " + $r) }
    Write-Host ""
    return ,$keep
}

function Scope-Rule {
    param([string]$Rule, [string]$RefBox, [string]$RepBox)
    $pair = $Rule -split '\{', 2
    $sel  = $pair[0].Trim()
    $body = $pair[1].Trim()
    if ($body -notmatch '\}$') { $body = $body + ' }' }
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($pt in ($sel -split ',')) {
        $s = $pt.Trim()
        if (-not $s) { continue }
        $refPat = ''
        if ($RefBox) { $refPat = '\.' + [regex]::Escape($RefBox) + '(?![\w-])' }
        if ($RefBox -and $RepBox -and ($s -match $refPat)) {
            if ($RefBox -ne $RepBox) { $s = [regex]::Replace($s, $refPat, ('.' + $RepBox)) }
        } elseif ($RepBox) {
            $s = '.' + $RepBox + ' ' + $s
        }
        $null = $out.Add($s)
    }
    return (($out -join ', ') + ' { ' + $body)
}

# ---------------------------------------------------------------------
# STEP 1: locate + describe the patient box in both files
$rep = Get-BoxInfo $L 'report.html'
$ref = Get-BoxInfo $O 'orders print.html'

$overlap = @()
foreach ($c in $ref.Classes) { if ($c -and ($rep.Classes -contains $c)) { $overlap += $c } }
Write-Host ("class overlap report-box vs reference-box: [" + ($overlap -join ', ') + "]")
Write-Host ""

# conflict diagnostics: existing report.css rules on the box classes + global table rules
$diagCls = @()
if ($rep.BoxCls) { $diagCls += $rep.BoxCls }
foreach ($c in $overlap) { if ($diagCls.Count -lt 6 -and ($diagCls -notcontains $c)) { $diagCls += $c } }
Dump-CssRules $L $diagCls 'report.html'
Write-Host ""
$srL = Get-StyleRanges $L
if ($srL.Count -gt 0) {
    Write-Host '----- report.html font-family lines -----'
    foreach ($rg in $srL) {
        for ($i = $rg[0]; $i -le $rg[1]; $i++) {
            if ($L[$i] -match 'font-family') { Write-Host ('{0,4}: {1}' -f ($i+1), $L[$i].Trim()) }
        }
    }
    Write-Host '----- report.html GLOBAL table/td/tr rules (potential conflicts) -----'
    $shown = 0
    foreach ($rg in $srL) {
        for ($i = $rg[0]; $i -le $rg[1] -and $shown -lt 6; $i++) {
            if ($L[$i] -match '^\s*(table|td|th|tr)\s*[,{]') {
                $j = $i
                while ($j -lt [Math]::Min($i + 10, $rg[1]) -and $L[$j] -notmatch '\}') { $j++ }
                Dump-Lines $L $i $j 'GLOBAL table rule'
                $shown++
                $i = $j
            }
        }
    }
    Write-Host ""
}

# ---------------------------------------------------------------------
# STEP 2: remove the OLD uniform-pitch override block (previous script)
$mk = -1
for ($i = 0; $i -lt $L.Count; $i++) {
    if ($L[$i] -match 'patient box row spacing: uniform 21px pitch') { $mk = $i }
}
if ($mk -ge 0) {
    $j = $mk + 1
    while ($j -lt $L.Count -and $L[$j].Trim() -ne '' -and $L[$j] -notmatch '^\s*/\*') { $j++ }
    Dump-Lines $L ([Math]::Max(0, $mk - 2)) ([Math]::Min($L.Count - 1, $j)) 'REMOVING old uniform-pitch block'
    $rmCount = $j - $mk
    $L.RemoveRange($mk, $rmCount)
    if ($mk -lt $L.Count -and $L[$mk].Trim() -eq '') { $L.RemoveAt($mk) }
    Write-Host ("removed " + $rmCount + " line(s) of the old uniform-pitch override")
} else {
    Write-Host 'old uniform-pitch override block: not present (nothing to remove)'
}
Write-Host ""

# ---------------------------------------------------------------------
# STEP 3: extract the reference box CSS from print.html and scope it
$cands = @($ref.Classes)
if ($ref.BoxCls -and ($cands -notcontains $ref.BoxCls)) { $cands += $ref.BoxCls }
$refRules = Extract-Rules $O $cands $ref.Ids 'print.html'

$validCls = @($rep.Classes)
if ($rep.BoxCls -and ($validCls -notcontains $rep.BoxCls)) { $validCls += $rep.BoxCls }

$spaceRules = New-Object System.Collections.Generic.List[string]
$typoRules  = New-Object System.Collections.Generic.List[string]
$existSet = @{}
for ($i = 0; $i -lt $L.Count; $i++) { $existSet[$L[$i].Trim()] = $true }

foreach ($r in $refRules) {
    $scoped = Scope-Rule $r $ref.BoxCls $rep.BoxCls
    # validity: every comma-part must reference classes that exist in the report box,
    # or be a bare-tag selector scoped under the discovered box class
    $sel = ($scoped -split '\{')[0]
    $ok = $true
    foreach ($pt in ($sel -split ',')) {
        $t = $pt.Trim()
        if (-not $t) { continue }
        $clsToks = @()
        foreach ($m in [regex]::Matches($t, '\.([A-Za-z0-9_-]+)')) { $clsToks += $m.Groups[1].Value }
        if ($clsToks.Count -gt 0) {
            $hitC = $false
            foreach ($c in $clsToks) { if ($validCls -contains $c) { $hitC = $true; break } }
            if (-not $hitC) { $ok = $false; break }
        } else {
            if (-not $rep.BoxCls) { $ok = $false; break }
        }
    }
    if (-not $ok) { Write-Host ("   skipped (not applicable to report box): " + $scoped); continue }
    if ($existSet.ContainsKey($scoped.Trim())) { Write-Host ("   skipped (already present): " + $scoped); continue }
    if ($scoped -match '(padding|margin|line-height)') { $null = $spaceRules.Add($scoped) }
    else { $null = $typoRules.Add($scoped) }
}
Write-Host ("scoped rules accepted: " + ($spaceRules.Count + $typoRules.Count) + "  (with spacing props: " + $spaceRules.Count + ")")
foreach ($r in $spaceRules) { Write-Host ("   INJECT-A spacing   : " + $r) }
foreach ($r in $typoRules)  { Write-Host ("   INJECT-A typography: " + $r) }
Write-Host ""

# ---------------------------------------------------------------------
# STEP 4: fallback rules (measured 21px pitch) when reference has no spacing CSS
$alreadySp2 = $false
for ($i = 0; $i -lt $L.Count; $i++) {
    if ($L[$i] -match 'patient box spacing copied from orders/print\.html' -or $L[$i] -match 'measured 21px pitch') { $alreadySp2 = $true }
}

$fallbackRules = New-Object System.Collections.Generic.List[string]
if ($spaceRules.Count -eq 0) {
    Write-Host 'no usable spacing rules found in print.html - building measured fallback (21px pitch)'
    # re-locate the anchor: STEP 2 removal above may have shifted line numbers
    $idx = -1
    for ($i = 0; $i -lt $L.Count; $i++) {
        if ($L[$i] -match 'Patient\s+Name') { $idx = $i; break }
    }
    if ($idx -lt 0) { throw "anchor 'Patient Name' lost after removing the old block" }
    $lblLine = $L[$idx]
    $lblToks = Get-ClassTokens $lblLine
    $lblCls = ''
    if ($lblToks.Count -gt 0) { $lblCls = $lblToks[-1] }
    $valSameLine = ($lblLine -match '\{\{')
    $valCls = ''
    if (-not $valSameLine) {
        for ($i = $idx + 1; $i -le [Math]::Min($idx + 10, $L.Count - 1); $i++) {
            if ($L[$i] -match '\{\{') {
                $vt = Get-ClassTokens $L[$i]
                if ($vt.Count -gt 0) { $valCls = $vt[-1]; break }
            }
        }
    }
    $cellCls = ''
    for ($i = $idx - 1; $i -ge [Math]::Max(0, $idx - 10); $i--) {
        if ($L[$i] -match '<(td|div|li)\b') {
            $ct = Get-ClassTokens $L[$i]
            if ($ct.Count -gt 0 -and $ct[-1] -ne $lblCls -and $ct[-1] -ne $valCls) { $cellCls = $ct[-1]; break }
        }
    }
    Write-Host ("fallback discovery: label='$lblCls' value='$valCls' cell='$cellCls' box='$($rep.BoxCls)'")

    $box = $rep.BoxCls
    $null = $fallbackRules.Add('/* ==== patient box row spacing: measured 21px pitch (matches regular report) ==== */')
    if ($box) { $null = $fallbackRules.Add(('.' + $box + ' { line-height: 21px !important; }')) }
    $pair = @()
    if ($lblCls -and $box) { $pair += ('.' + $box + ' .' + $lblCls) }
    if ($valCls -and $box) { $pair += ('.' + $box + ' .' + $valCls) }
    if ($pair.Count -gt 0) {
        $null = $fallbackRules.Add(($pair -join ', ') + ' { line-height: 21px !important; margin-top: 0 !important; margin-bottom: 0 !important; }')
    }
    if ($cellCls -and $box -and $cellCls -ne $box) {
        $null = $fallbackRules.Add(('.' + $box + ' .' + $cellCls + ' { padding-top: 0 !important; padding-bottom: 0 !important; }'))
    }
    if (-not $box -and $pair.Count -eq 0 -and -not $cellCls) {
        Write-Host 'WARNING: no usable class discovered for the fallback - nothing will be injected. Paste the output back.'
    }
}

# ---------------------------------------------------------------------
# STEP 5: assemble + inject before the last </style>
$inject = New-Object System.Collections.Generic.List[string]
if ($spaceRules.Count -gt 0) {
    $null = $inject.Add('/* ==== patient box spacing copied from orders/print.html (image 2 look) ==== */')
    foreach ($r in $spaceRules) { $null = $inject.Add($r) }
    if ($typoRules.Count -gt 0) {
        $null = $inject.Add('/* ---- typography of the same box, copied from print.html ---- */')
        foreach ($r in $typoRules) { $null = $inject.Add($r) }
    }
    Write-Host 'strategy A: real print.html spacing rules will be injected'
} else {
    if ($typoRules.Count -gt 0) {
        $null = $inject.Add('/* ---- typography of the patient box, copied from print.html ---- */')
        foreach ($r in $typoRules) { $null = $inject.Add($r) }
    }
    foreach ($r in $fallbackRules) { $null = $inject.Add($r) }
    if ($fallbackRules.Count -gt 0) { Write-Host 'strategy B: measured 21px pitch fallback will be injected' }
}
Write-Host ""

$sty = -1
for ($i = 0; $i -lt $L.Count; $i++) { if ($L[$i] -match '</style>') { $sty = $i } }
if ($sty -lt 0) { throw '</style> not found in report.html' }

if ($alreadySp2) {
    Write-Host 'spacing rules from this script already present - injection skipped'
} elseif ($inject.Count -gt 0) {
    Write-Host '--- CSS to inject (before </style>) ---'
    foreach ($r in $inject) { Write-Host ('  ' + $r) }
    for ($k = $inject.Count - 1; $k -ge 0; $k--) { $L.Insert($sty, $inject[$k]) }
    Write-Host ("injected " + $inject.Count + " line(s) before </style> at line " + ($sty + 1))
} else {
    Write-Host 'nothing to inject'
}
Write-Host ""

# ---------------------------------------------------------------------
# STEP 6: uniform sans-serif font (screen + WeasyPrint PDF) - if missing
$sty = -1
for ($i = 0; $i -lt $L.Count; $i++) { if ($L[$i] -match '</style>') { $sty = $i } }
$alreadyFf = $false
for ($i = 0; $i -lt $L.Count; $i++) {
    if ($L[$i] -match 'uniform sans-serif across the report') { $alreadyFf = $true }
}
if (-not $alreadyFf) {
    $ff = New-Object System.Collections.Generic.List[string]
    $null = $ff.Add('')
    $null = $ff.Add('/* ==== uniform sans-serif across the report (screen + WeasyPrint PDF) ==== */')
    $null = $ff.Add('body { font-family: Arial, Helvetica, sans-serif; }')
    $null = $ff.Add('table, thead, tbody, tr, td, th, div, span, p, h1, h2, h3, h4, strong, b, em, i, small, label, ul, li { font-family: inherit; }')
    for ($k = $ff.Count - 1; $k -ge 0; $k--) { $L.Insert($sty, $ff[$k]) }
    Write-Host ("inserted " + $ff.Count + " font line(s) before </style>")
} else {
    Write-Host 'font-family rule already present - skipped'
}
Write-Host ""

# ---------------------------------------------------------------------
# STEP 7: mojibake fix (phone / fax icons in the header)
$bad1 = [string][char]0x00E2 + [string][char]0x02DC + [string][char]0x017D  # mojibake of phone
$bad2 = [string][char]0x00E2 + [string][char]0x0153 + [string][char]0x2030  # mojibake of fax
$ok1  = [string][char]0x260E
$ok2  = [string][char]0x2709
$cnt1 = 0; $cnt2 = 0
for ($i = 0; $i -lt $L.Count; $i++) {
    $s = $L[$i]
    if ($s.Contains($bad1)) { $s = $s.Replace($bad1, $ok1); $cnt1++ }
    if ($s.Contains($bad2)) { $s = $s.Replace($bad2, $ok2); $cnt2++ }
    $L[$i] = $s
}
Write-Host "mojibake fixed: phone on $cnt1 line(s), fax on $cnt2 line(s)"
Write-Host ""

# ---------------------------------------------------------------------
# STEP 8: write UTF-8 (no BOM) + verify
[System.IO.File]::WriteAllLines($p, $L, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "written: $p"
Write-Host ("new total lines: " + $L.Count)
Write-Host ""

$L2 = [System.Collections.Generic.List[string]]([System.IO.File]::ReadAllLines($p))
$cOld = 0; $cA = 0; $cB = 0; $cFf = 0
for ($i = 0; $i -lt $L2.Count; $i++) {
    if ($L2[$i] -match 'patient box row spacing: uniform 21px pitch') { $cOld++ }
    if ($L2[$i] -match 'patient box spacing copied from orders/print\.html') { $cA++ }
    if ($L2[$i] -match 'measured 21px pitch') { $cB++ }
    if ($L2[$i] -match 'uniform sans-serif across the report') { $cFf++ }
}
Write-Host "verify: old uniform-pitch marker      = $cOld  (expect 0)"
Write-Host "verify: print.html spacing marker (A) = $cA   (expect 0 or 1)"
Write-Host "verify: measured fallback marker (B)  = $cB   (expect 0 or 1)"
Write-Host "verify: sans-serif marker             = $cFf  (expect 1)"

$sty2 = -1
for ($i = 0; $i -lt $L2.Count; $i++) { if ($L2[$i] -match '</style>') { $sty2 = $i } }
Dump-Lines $L2 ([Math]::Max(0, $sty2 - 40)) ([Math]::Min($L2.Count - 1, $sty2 + 1)) 'VERIFY: tail of style block'

Write-Host ""
Write-Host 'DONE. Hard-refresh the report page (Ctrl+F5) and regenerate the PCR PDF.'
Write-Host 'Expected: a visible blank gap (~one line) between every row of the patient box, like image 2.'
Write-Host 'If the box still looks tight, paste the FULL console output above back to the chat.'
