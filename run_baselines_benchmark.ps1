# ORCHESTRA: Multi-Agent Baselines Benchmark Runner & Paper Synthesis
# Usage Examples:
#   .\run_baselines_benchmark.ps1 -Model "qwen2.5:7b"
#   .\run_baselines_benchmark.ps1 -Model "qwen2.5:7b" -TaskIds "I-01","I-02","I-03" -AgentCounts 2,5,10
#   .\run_baselines_benchmark.ps1 -Model "qwen2.5:7b" -TaskIds "all" -Baselines "all"

param (
    [string]$Model = "qwen2.5:7b",
    [string[]]$TaskIds = @("I-01", "I-02", "I-03"),
    [int[]]$AgentCounts = @(2, 5, 10),
    [string[]]$Baselines = @("all"),
    [string[]]$Perturbations = @("none", "agent_dropout"),
    [string]$Workspace = "workspace_baselines",
    [string]$OutputDir = "paper_results/baselines",
    [int]$MaxRounds = 3
)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA: MULTI-AGENT BASELINES BENCHMARK RUNNER" -ForegroundColor Cyan
Write-Host "  Model:         $Model" -ForegroundColor Cyan
Write-Host "  Tasks:         $($TaskIds -join ', ')" -ForegroundColor Cyan
Write-Host "  Agent Scales:  $($AgentCounts -join ', ')" -ForegroundColor Cyan
Write-Host "  Baselines:     $($Baselines -join ', ')" -ForegroundColor Cyan
Write-Host "  Perturbations: $($Perturbations -join ', ')" -ForegroundColor Cyan
Write-Host "  Max Rounds:    $MaxRounds" -ForegroundColor Cyan
Write-Host "  Workspace:     $Workspace" -ForegroundColor Cyan
Write-Host "  Paper Output:  $OutputDir" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Execute the multi-baseline benchmark matrix
Write-Host "`n[PHASE 1/2] Executing Baseline Matrix across Scales & Perturbations..." -ForegroundColor Yellow

$taskArgs = $TaskIds
$agentArgs = $AgentCounts | ForEach-Object { "$_" }
$baselineArgs = $Baselines
$pertArgs = $Perturbations

python -u -m baselines.batch_runner `
    --baselines $baselineArgs `
    --task-ids $taskArgs `
    --agent-counts $agentArgs `
    --perturbations $pertArgs `
    --model $Model `
    --max-rounds $MaxRounds `
    --workspace $Workspace

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Baseline batch execution encountered errors. Exit code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

# 2. Synthesize Paper Results (Table 1 and Publication Figures)
Write-Host "`n[PHASE 2/2] Synthesizing Table 1 and Publication Plots for Paper Draft..." -ForegroundColor Cyan

$csvFile = Join-Path $Workspace "baseline_comparison_results.csv"

python -u -m baselines.compare `
    --input-csv $csvFile `
    --output-dir $OutputDir

Write-Host "`n========================================================================" -ForegroundColor Green
Write-Host "  BASELINES BENCHMARK & PAPER ARTIFACTS COMPLETE!" -ForegroundColor Green
Write-Host "  Output Directory: $OutputDir" -ForegroundColor Green
Write-Host "  Generated Artifacts:" -ForegroundColor Green
Write-Host "    - Table 1 (CSV):  $OutputDir/table1_master_baseline_comparison.csv" -ForegroundColor Green
Write-Host "    - Table 1 (MD):   $OutputDir/table1_master_baseline_comparison.md" -ForegroundColor Green
Write-Host "    - Figure 1 (PNG): $OutputDir/figure_baseline_accuracy_comparison.png" -ForegroundColor Green
Write-Host "    - Figure 2 (PNG): $OutputDir/figure_perturbation_resilience.png" -ForegroundColor Green
Write-Host "    - Figure 3 (PNG): $OutputDir/figure_token_accuracy_pareto.png" -ForegroundColor Green
Write-Host "  Core ORCHESTRA codebase and workspace/ remain 100% intact!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
