# OA Mock setup for Windows 10/11 (PowerShell).
#   Double-click setup.bat, or run:  powershell -ExecutionPolicy Bypass -File setup.ps1
#   -NoJava   skip the JDK
#   -NoStart  set up only, don't start the runner
param([switch]$NoJava, [switch]$NoStart)
$ErrorActionPreference = "Continue"
Set-Location -Path $PSScriptRoot

function Ok($m)   { Write-Host "  [ok] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Step($m) { Write-Host "`n$m" -ForegroundColor White }
function Have($c) { [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
  $links = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links"
  if (Test-Path $links) { $env:Path += ";$links" }
}
function Winget-Install($id) {
  if (-not (Have "winget")) { return $false }
  winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
  Refresh-Path
  return $true
}
function Find-Python {
  foreach ($c in @("py", "python", "python3")) {
    if (Have $c) {
      $args0 = @(); if ($c -eq "py") { $args0 = @("-3") }
      try {
        & $c @args0 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { return ,(@($c) + $args0) }
      } catch {}
    }
  }
  return $null
}

Write-Host "OA Mock setup (Windows)"
if (-not (Have "winget")) { Warn "winget isn't available, so missing tools can't be installed automatically. Install 'App Installer' from the Microsoft Store to get it." }

# ---------- Python ----------
Step "1/3 Python 3.8+"
$py = Find-Python
if (-not $py) {
  Warn "Python 3.8+ not found. Installing with winget..."
  Winget-Install "Python.Python.3.12" | Out-Null
  $py = Find-Python
}
if (-not $py) { Warn "Install Python from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'), then run setup again."; Read-Host "Press Enter to exit"; exit 1 }
$pyExe = $py[0]; $pyArgs = @(); if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
Ok ((& $pyExe @pyArgs --version 2>&1) | Out-String).Trim()

# ---------- C++ ----------
Step "2/3 C++ compiler (g++ for C++17 answers)"
if (-not (Have "g++")) {
  Warn "g++ not found. Installing MinGW-w64 (WinLibs) with winget..."
  Winget-Install "BrechtSanders.WinLibs.POSIX.UCRT" | Out-Null
}
if (Have "g++") { Ok ((& g++ --version | Select-Object -First 1) | Out-String).Trim() }
else { Warn "No g++. Install MinGW-w64 (https://winlibs.com) and add its bin folder to PATH. Python and JavaScript answers still work." }

# ---------- Java ----------
Step "3/3 Java JDK (for Java answers)"
if (Have "javac") { Ok ((& javac -version 2>&1 | Select-Object -Last 1) | Out-String).Trim() }
elseif ($NoJava) { Warn "Skipped (-NoJava). C++, Python and JavaScript still work." }
else {
  Warn "No JDK found. Installing Temurin 21 with winget..."
  Winget-Install "EclipseAdoptium.Temurin.21.JDK" | Out-Null
  if (Have "javac") { Ok ((& javac -version 2>&1 | Select-Object -Last 1) | Out-String).Trim() }
  else { Warn "No JDK yet. If it just installed, open a new window and run setup again. Everything else works." }
}

# ---------- launcher ----------
$launcher = "@echo off`r`ncd /d `"%~dp0`"`r`nrem Stop the mock with Ctrl+C.`r`nwhere py >nul 2>nul && (py -3 oa_mock_local.py %* & goto :eof)`r`npython oa_mock_local.py %*`r`n"
Set-Content -Path (Join-Path $PSScriptRoot "start.bat") -Value $launcher -Encoding ASCII -NoNewline
Step "Done"
Ok "Start the mock any time by double-clicking start.bat (stop it with Ctrl+C)."
Ok "If a compiler was just installed and isn't detected, close this window and open a new one."

if (-not $NoStart) {
  Write-Host ""
  & $pyExe @pyArgs oa_mock_local.py
}
