$ErrorActionPreference = "Stop"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.11+ is required." }
python -m venv .venv
$python = if ($IsWindows -or $env:OS -eq "Windows_NT") { ".\.venv\Scripts\python.exe" } else { ".venv/bin/python" }
& $python -m pip install -e ".[dev]"
& $python -m zeroburn
