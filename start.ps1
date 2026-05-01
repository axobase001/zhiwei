$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) { return }
    $parts = $line.Split("=", 2)
    $name = $parts[0].Trim().Trim([char]0xFEFF)
    $value = $parts[1].Trim().Trim('"').Trim("'")
    if ($name) {
      [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
  }
}

$candidates = @()
if ($env:ZHIWEI_PYTHON) {
  $candidates += $env:ZHIWEI_PYTHON
}
$candidates += "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$candidates += "python"
$candidates += "py"

$python = $null
foreach ($candidate in $candidates) {
  if (-not $candidate) { continue }
  $cmd = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $cmd) { continue }
  try {
    & $cmd.Source -c "import sys; print(sys.version)" | Out-Null
    $python = $cmd.Source
    break
  } catch {
    continue
  }
}

if (-not $python) {
  throw "未找到可用 Python。可设置 ZHIWEI_PYTHON 指向 python.exe。"
}

try {
  & $python -c "import pypdf" | Out-Null
} catch {
  Write-Host "缺少 pypdf，正在尝试安装 requirements.txt ..."
  & $python -m pip install -r requirements.txt
}

Write-Host "知微启动中：http://127.0.0.1:8765"
& $python -m backend.app
