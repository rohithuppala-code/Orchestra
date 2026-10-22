# ORCHESTRA: Master 3-Scale Experimental Benchmark Runner
# Usage Example:
#   .\run_master_benchmark.ps1 -Model "qwen2.5:7b"

param (
    [string]$Model = "qwen2.5:7b",
    [string]$Prefix = "final_workspace",
    [int]$MaxRounds = 3
)

$WsN2  = "${Prefix}_n2"
$WsN5  = "${Prefix}_n5"
$WsN10 = "${Prefix}_n10"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA: STARTING 3-SCALE MASTER BENCHMARK (180 RUNS PER SCALE)" -ForegroundColor Cyan
Write-Host "  Model: $Model | Max Rounds: $MaxRounds" -ForegroundColor Cyan
Write-Host "  Destination Folders:" -ForegroundColor Cyan
Write-Host "    - 2  Agents: $WsN2" -ForegroundColor Cyan
Write-Host "    - 5  Agents: $WsN5" -ForegroundColor Cyan
Write-Host "    - 10 Agents: $WsN10" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Scale 1: 2 Agents (180 Runs -> $WsN2)
Write-Host "`n[PHASE 1/3] Running 2 Agents Benchmark (180 runs) -> $WsN2..." -ForegroundColor Yellow
python -u -m orchestra.batch_runner `
    --task-ids all `
    --agent-counts 2 `
    --protocols msg broadcast sfs `
    --perturbations none agent_dropout `
    --model $Model `
    --max-rounds $MaxRounds `
    --hitl `
    --workspace $WsN2

Write-Host "`n[ANALYSIS] Generating figures, correlations, and plots for $WsN2..." -ForegroundColor Cyan
python -u -m orchestra.analysis --workspace $WsN2 --output-dir $WsN2
Write-Host "[PHASE 1/3 COMPLETE] 2-Agent Benchmark Finished in $WsN2!" -ForegroundColor Green

# 2. Scale 2: 5 Agents (180 Runs -> $WsN5)
Write-Host "`n[PHASE 2/3] Running 5 Agents Benchmark (180 runs) -> $WsN5..." -ForegroundColor Yellow
python -u -m orchestra.batch_runner `
    --task-ids all `
    --agent-counts 5 `
    --protocols msg broadcast sfs `
    --perturbations none agent_dropout `
    --model $Model `
    --max-rounds $MaxRounds `
    --hitl `
    --workspace $WsN5

Write-Host "`n[ANALYSIS] Generating figures, correlations, and plots for $WsN5..." -ForegroundColor Cyan
python -u -m orchestra.analysis --workspace $WsN5 --output-dir $WsN5
Write-Host "[PHASE 2/3 COMPLETE] 5-Agent Benchmark Finished in $WsN5!" -ForegroundColor Green

# 3. Scale 3: 10 Agents (180 Runs -> $WsN10)
Write-Host "`n[PHASE 3/3] Running 10 Agents Benchmark (180 runs) -> $WsN10..." -ForegroundColor Yellow
python -u -m orchestra.batch_runner `
    --task-ids all `
    --agent-counts 10 `
    --protocols msg broadcast sfs `
    --perturbations none agent_dropout `
    --model $Model `
    --max-rounds $MaxRounds `
    --hitl `
    --workspace $WsN10

Write-Host "`n[ANALYSIS] Generating figures, correlations, and plots for $WsN10..." -ForegroundColor Cyan
python -u -m orchestra.analysis --workspace $WsN10 --output-dir $WsN10
Write-Host "[PHASE 3/3 COMPLETE] 10-Agent Benchmark Finished in $WsN10!" -ForegroundColor Green

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  ALL 3 SCALES (540 TOTAL RUNS) SUCCESSFULLY COMPLETED!" -ForegroundColor Cyan
Write-Host "  Each folder contains:" -ForegroundColor Cyan
Write-Host "    - batch_comparison_results.csv (All 180 runs)" -ForegroundColor Cyan
Write-Host "    - structure_performance_correlations.csv (Pearson r matrix)" -ForegroundColor Cyan
Write-Host "    - longitudinal_comparison.png (Publication figures)" -ForegroundColor Cyan
Write-Host "    - 180 case directories with raw telemetry & agent logs" -ForegroundColor Cyan
Write-Host "  Existing gemma4 results in workspace/ remain completely untouched!" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
