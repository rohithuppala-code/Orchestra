# ORCHESTRA: Multi-Agent Baselines Benchmark Runner & Paper Synthesis (450-Run Q1 Matrix: 270 Baseline Runs)
# Segregates baseline results into scale-specific folders (n2, n5, n10)
# Matrix: 15 Stratified Tasks x 3 Non-Redundant Baselines (independent, central_coordinator, hierarchical_coordinator) x 2 Perturbations
#         = 90 runs/scale -> 270 baseline runs (+ 180 ORCHESTRA/broadcast runs = 450 runs total)
# Usage Examples:
#   .\run_baselines_benchmark.ps1 -Model "qwen3.8-27b"                                      # Full 270 baseline runs + 450-run synthesis
#   .\run_baselines_benchmark.ps1 -Model "qwen3.8-27b" -TaskIds "I-01" -AgentCounts 2       # Quick 6-run sanity test

param (
    [string]$Model = "qwen2.5:7b",
    [string[]]$TaskIds = @("selected"),
    [int[]]$AgentCounts = @(2, 5, 10),
    [string[]]$Baselines = @("all"),
    [string[]]$Perturbations = @("none", "agent_dropout"),
    [string]$Prefix = "workspace_baselines",
    [string]$OrchestraPrefix = "final_workspace",
    [string]$OutputDir = "paper_results/baselines",
    [int]$MaxRounds = 15
)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA: MULTI-AGENT BASELINES BENCHMARK (90 RUNS PER SCALE)" -ForegroundColor Cyan
Write-Host "  Model:         $Model" -ForegroundColor Cyan
Write-Host "  Tasks:         $($TaskIds -join ', ') (15 stratified tasks)" -ForegroundColor Cyan
Write-Host "  Agent Scales:  $($AgentCounts -join ', ')" -ForegroundColor Cyan
Write-Host "  Baselines:     $($Baselines -join ', ') (independent, central_coordinator, hierarchical_coordinator)" -ForegroundColor Cyan
Write-Host "  Perturbations: $($Perturbations -join ', ')" -ForegroundColor Cyan
Write-Host "  Max Rounds:    $MaxRounds" -ForegroundColor Cyan
Write-Host "  Folder Prefix: $Prefix (e.g. ${Prefix}_n2, ${Prefix}_n5, ${Prefix}_n10)" -ForegroundColor Cyan
Write-Host "  Paper Output:  $OutputDir" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$allCsvPaths = @()
$scaleIdx = 0

# 1. Execute baseline matrix segregated per agent scale
foreach ($n in $AgentCounts) {
    $scaleIdx++
    $wsFolder = "${Prefix}_n${n}"
    Write-Host "`n[$scaleIdx/$($AgentCounts.Count)] Running Baseline Suite for $n Agents (90 runs) -> $wsFolder..." -ForegroundColor Yellow

    python -u -m baselines.batch_runner `
        --baselines $Baselines `
        --task-ids $TaskIds `
        --agent-counts $n `
        --perturbations $Perturbations `
        --model $Model `
        --max-rounds $MaxRounds `
        --workspace $wsFolder

    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n[WARNING] Baseline run for N=$n encountered non-zero exit code: $LASTEXITCODE" -ForegroundColor DarkYellow
    }

    $csvFile = Join-Path $wsFolder "baseline_comparison_results.csv"
    if (Test-Path $csvFile) {
        $allCsvPaths += $csvFile
        Write-Host "  [OK] Saved scale results to: $csvFile" -ForegroundColor Green
    }
}

# Automatically discover and include ORCHESTRA & Broadcast results from final_workspace_n* if present
foreach ($n in $AgentCounts) {
    $orchCsv = Join-Path "${OrchestraPrefix}_n${n}" "batch_comparison_results.csv"
    if (Test-Path $orchCsv) {
        $allCsvPaths += $orchCsv
        Write-Host "  [OK] Found ORCHESTRA/Broadcast scale results for Master Synthesis: $orchCsv" -ForegroundColor Green
    }
}

# 2. Synthesize Paper Results across all segregated scale folders (450 total runs -> 5 methods)
Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  SYNTHESIZING PAPER ARTIFACTS (TABLES 1-4 & PUBLICATION FIGURES)" -ForegroundColor Cyan
Write-Host "  Input CSVs: $($allCsvPaths -join ', ')" -ForegroundColor Cyan
Write-Host "  Destination: $OutputDir" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

if ($allCsvPaths.Count -gt 0) {
    python -u -m baselines.compare `
        --input-csv $allCsvPaths `
        --output-dir $OutputDir

    Write-Host "`n========================================================================" -ForegroundColor Green
    Write-Host "  BASELINES BENCHMARK & 450-RUN MULTI-SCALE SYNTHESIS COMPLETE!" -ForegroundColor Green
    Write-Host "  Segregated Scale Folders Created:" -ForegroundColor Green
    foreach ($n in $AgentCounts) {
        Write-Host "    - N=$n Agents: ${Prefix}_n${n}/" -ForegroundColor Green
    }
    Write-Host "  Paper Draft Artifacts in $OutputDir/ (5 Methods: 4 Baselines + ORCHESTRA):" -ForegroundColor Green
    Write-Host "    - Table 1 (Master Comparison):    $OutputDir/table1_master_baseline_comparison.*" -ForegroundColor Green
    Write-Host "    - Table 2 (Metrics by Scale):     $OutputDir/table2_metrics_by_agent_scale.*" -ForegroundColor Green
    Write-Host "    - Table 3 (Task Complexity Tier): $OutputDir/table3_task_complexity_breakdown.*" -ForegroundColor Green
    Write-Host "    - Table 4 (Dropout Resilience):   $OutputDir/table4_perturbation_resilience_breakdown.*" -ForegroundColor Green
    Write-Host "    - Figure 1 (Accuracy Bar Chart):  $OutputDir/figure_baseline_accuracy_comparison.png" -ForegroundColor Green
    Write-Host "    - Figure 2 (Dropout Resilience):  $OutputDir/figure_perturbation_resilience.png" -ForegroundColor Green
    Write-Host "    - Figure 3 (Pareto Token Cost):   $OutputDir/figure_token_accuracy_pareto.png" -ForegroundColor Green
    Write-Host "    - Master Raw CSV (450 Runs):      $OutputDir/master_baseline_results.csv" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] No baseline CSV files were produced to synthesize." -ForegroundColor Red
    exit 1
}
