"""Enumerate available printers on the server."""
import subprocess
import sys


def list_printers():
    """Return a list of printer names visible to the server.

    Windows: uses win32print if available, falls back to PowerShell.
    Other OS: uses lpstat.
    Returns [] on any failure — callers must handle empty list.
    """
    if sys.platform == 'win32':
        try:
            import win32print
            return sorted({p[2] for p in win32print.EnumPrinters(2)})
        except Exception:
            pass
        # Fallback: PowerShell
        try:
            r = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 'Get-Printer | Select-Object -ExpandProperty Name'],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                return sorted({l.strip() for l in r.stdout.splitlines() if l.strip()})
        except Exception:
            pass
        return []

    # Linux / macOS
    try:
        r = subprocess.run(['lpstat', '-a'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            names = []
            for line in r.stdout.splitlines():
                if line.strip():
                    names.append(line.split()[0].strip())
            return sorted(set(names))
    except Exception:
        pass
    return []
