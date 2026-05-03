param(
  [int]$WaitPid = 0,
  [int]$PerPaperTimeoutSeconds = 1800
)

$ErrorActionPreference = "Continue"
$repo = "C:\Users\PC\zhiwei"
$python = "C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$logDir = Join-Path $repo "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("cv_pipeline_remaining_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

function Write-Log {
  param([string]$Message)
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $Message
  Add-Content -Path $log -Value $line -Encoding UTF8
  Write-Output $line
}

Set-Location $repo
Write-Log "Starting CV remaining pipeline runner."
Write-Log "Repo: $repo"
Write-Log "Python: $python"

if ($WaitPid -gt 0) {
  $existing = Get-Process -Id $WaitPid -ErrorAction SilentlyContinue
  if ($existing) {
    Write-Log "Waiting for existing pipeline process PID=$WaitPid"
    Wait-Process -Id $WaitPid
    Write-Log "Existing pipeline process PID=$WaitPid finished."
  } else {
    Write-Log "Existing pipeline process PID=$WaitPid not found; continuing."
  }
}

Write-Log "Running missing CV specs through Mimo pipeline."
& $python -X utf8 -c @"
import json
from pathlib import Path
specs = json.loads(Path('samples/benchmark/top_cv/top_cv_specs.json').read_text(encoding='utf-8'))['papers']
summary_path = Path('samples/benchmark/top_cv/top_cv_pipeline_summary.json')
summary = json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.exists() else {'papers': []}
done = {item.get('paper_id') for item in summary.get('papers', []) if item.get('status') in {'ok', 'failed', 'skipped'}}
missing = [spec for spec in specs if spec.get('paper_id') not in done]
Path('samples/benchmark/top_cv/top_cv_missing_queue.json').write_text(json.dumps({'papers': missing}, ensure_ascii=False, indent=2), encoding='utf-8')
print(len(missing))
"@ *>> $log

$queuePath = "samples\benchmark\top_cv\top_cv_missing_queue.json"
$queue = Get-Content $queuePath -Raw | ConvertFrom-Json
$total = @($queue.papers).Count
Write-Log "Missing queue size: $total"

$index = 0
foreach ($spec in $queue.papers) {
  $index += 1
  $paperId = [string]$spec.paper_id
  $title = [string]$spec.title
  Write-Log "[$index/$total] Running $paperId :: $title"

  $singleSpecPath = Join-Path $env:TEMP ("zhiwei_cv_single_" + $paperId + ".json")
  @{ papers = @($spec) } | ConvertTo-Json -Depth 20 | Set-Content -Path $singleSpecPath -Encoding UTF8

  $args = @(
    "-m", "backend.benchmark_pipeline",
    "--spec-file", $singleSpecPath,
    "--paper", $paperId,
    "--sleep", "0"
  )
  $proc = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir "$paperId.out.log") -RedirectStandardError (Join-Path $logDir "$paperId.err.log")
  $finished = Wait-Process -Id $proc.Id -Timeout $PerPaperTimeoutSeconds -ErrorAction SilentlyContinue
  if (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue) {
    Write-Log "Timeout after $PerPaperTimeoutSeconds seconds; killing $paperId"
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    & $python -X utf8 -c @"
import json
from pathlib import Path
paper_id = '$paperId'
title = '''$title'''
summary_path = Path('samples/benchmark/top_cv/top_cv_pipeline_summary.json')
summary = json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.exists() else {'papers': []}
items = [item for item in summary.get('papers', []) if item.get('paper_id') != paper_id]
items.append({'paper_id': paper_id, 'title': title, 'status': 'failed', 'error': 'Per-paper watchdog timeout in run_cv_remaining.ps1'})
summary['papers'] = items
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
"@ *>> $log
    $partialDir = Join-Path "samples\benchmark\generated" $paperId
    if ((Test-Path $partialDir) -and -not (Test-Path (Join-Path $partialDir "paper_ir.json"))) {
      Remove-Item -LiteralPath $partialDir -Recurse -Force -ErrorAction SilentlyContinue
    }
  } else {
    Write-Log "Finished $paperId"
  }
}

Write-Log "Pipeline queue finished."

Write-Log "Running npm test."
cmd /c npm run test *>> $log
$testExit = $LASTEXITCODE
Write-Log "Test exit code: $testExit"

Write-Log "Staging generated files."
git add backend/semantic_cv_pipeline.py scripts/run_cv_remaining.ps1 samples/benchmark/top_cv *>> $log
Get-ChildItem -Path "samples/benchmark/generated" -Directory -Filter "paper_cv_*" | ForEach-Object {
  $irPath = Join-Path $_.FullName "paper_ir.json"
  if (Test-Path $irPath) {
    git add $_.FullName *>> $log
  } else {
    Write-Log "Skipping partial generated directory without paper_ir.json: $($_.Name)"
  }
}
$addExit = $LASTEXITCODE
Write-Log "Git add exit code: $addExit"

$changes = git status --short
if ($changes) {
  Write-Log "Committing changes."
  git commit -m "Add top-cited computer vision benchmarks" *>> $log
  $commitExit = $LASTEXITCODE
  Write-Log "Git commit exit code: $commitExit"

  Write-Log "Pushing to GitHub."
  git push origin main *>> $log
  $pushExit = $LASTEXITCODE
  Write-Log "Git push exit code: $pushExit"
} else {
  Write-Log "No changes to commit."
}

Write-Log "Deploying to Vercel."
cmd /c npx vercel deploy --prod --yes *>> $log
$deployExit = $LASTEXITCODE
Write-Log "Deploy exit code: $deployExit"

Write-Log "CV remaining pipeline runner finished."
