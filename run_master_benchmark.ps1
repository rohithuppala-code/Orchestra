# ORCHESTRA: Master 3-Scale Experimental Benchmark Runner (450-Run Q1 Matrix: 180 ORCHESTRA/Broadcast Runs)
# Stratified 15 Tasks x 2 Protocols (msg, broadcast) x 2 Perturbations (none, agent_dropout) = 60 runs/scale -> 180 runs total
# Usage Examples:
#   .\run_master_benchmark.ps1 -Model "qwen3.8-27b"
#   .\run_master_benchmark.ps1 -Model "qwen3.8-27b" -AgentCounts 2

param (
    [string]$Model = "qwen2.5:7b",
    [string[]]$TaskIds = @("selected"),
    [int[]]$AgentCounts = @(2, 5, 10),
    [string[]]$Protocols = @("msg", "broadcast"),
    [string]$Prefix = "final_workspace",
    [int]$MaxRounds = 15
)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA: STARTING 3-SCALE MASTER BENCHMARK (60 RUNS PER SCALE)" -ForegroundColor Cyan
Write-Host "  Model:      $Model | Max Rounds: $MaxRounds" -ForegroundColor Cyan
Write-Host "  Tasks:      $($TaskIds -join ', ') (15 stratified tasks across Levels I, II, III)" -ForegroundColor Cyan
Write-Host "  Protocols:  $($Protocols -join ', ') (msg=ORCHESTRA, broadcast=Flat Debate Baseline)" -ForegroundColor Cyan
Write-Host "  Scales:     $($AgentCounts -join ', ')" -ForegroundColor Cyan
Write-Host "  Destination Folders:" -ForegroundColor Cyan
foreach ($n in $AgentCounts) {
    Write-Host "    - $n Agents: ${Prefix}_n${n}" -ForegroundColor Cyan
}
Write-Host "========================================================================" -ForegroundColor Cyan

$phaseIdx = 0
foreach ($n in $AgentCounts) {
    $phaseIdx++
    $wsFolder = "${Prefix}_n${n}"
    Write-Host "`n[PHASE $phaseIdx/$($AgentCounts.Count)] Running $n Agents Benchmark (60 runs) -> $wsFolder..." -ForegroundColor Yellow

    python -u -m orchestra.batch_runner `
        --task-ids $TaskIds `
        --agent-counts $n `
        --protocols $Protocols `
        --perturbations none agent_dropout `
        --model $Model `
        --max-rounds $MaxRounds `
        --hitl `
        --workspace $wsFolder

    Write-Host "`n[ANALYSIS] Generating figures, correlations, and plots for $wsFolder..." -ForegroundColor Cyan
    python -u -m orchestra.analysis --workspace $wsFolder --output-dir $wsFolder
    Write-Host "[PHASE $phaseIdx/$($AgentCounts.Count) COMPLETE] $n-Agent Benchmark Finished in $wsFolder!" -ForegroundColor Green
}

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA SCALES COMPLETE (180 TOTAL RUNS: 60 PER SCALE)!" -ForegroundColor Cyan
Write-Host "  Each folder contains:" -ForegroundColor Cyan
Write-Host "    - batch_comparison_results.csv (All 60 runs for that scale)" -ForegroundColor Cyan
Write-Host "    - structure_performance_correlations.csv (Pearson r matrix)" -ForegroundColor Cyan
Write-Host "    - longitudinal_comparison.png (Publication figures)" -ForegroundColor Cyan
Write-Host "    - 60 case directories with raw telemetry & agent logs" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
