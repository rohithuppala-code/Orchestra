# ORCHESTRA: Multi-Agent Baselines Benchmark Runner & Paper Synthesis
# Segregates baseline results into scale-specific folders (n2, n5, n10)
# Full Benchmark: 30 Tasks x 5 Baselines x 2 Perturbations = 300 runs/scale -> 900 runs total
# Usage Examples:
#   .\run_baselines_benchmark.ps1 -Model "qwen2.5:7b"                                        # Full 900 runs
#   .\run_baselines_benchmark.ps1 -Model "qwen2.5:7b" -TaskIds "I-01","I-02","I-03"        # Quick 90 runs test

param (
    [string]$Model = "qwen2.5:7b",
    [string[]]$TaskIds = @("all"),
    [int[]]$AgentCounts = @(2, 5, 10),
    [string[]]$Baselines = @("all"),
    [string[]]$Perturbations = @("none", "agent_dropout"),
    [string]$Prefix = "workspace_baselines",
    [string]$OutputDir = "paper_results/baselines",
    [int]$MaxRounds = 3
)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORCHESTRA: MULTI-AGENT BASELINES BENCHMARK (SEGREGATED BY SCALE)" -ForegroundColor Cyan
Write-Host "  Model:         $Model" -ForegroundColor Cyan
Write-Host "  Tasks:         $($TaskIds -join ', ')" -ForegroundColor Cyan
Write-Host "  Agent Scales:  $($AgentCounts -join ', ')" -ForegroundColor Cyan
Write-Host "  Baselines:     $($Baselines -join ', ')" -ForegroundColor Cyan
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
    Write-Host "`n[$scaleIdx/$($AgentCounts.Count)] Running Baseline Suite for $n Agents -> $wsFolder..." -ForegroundColor Yellow

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

# 2. Synthesize Paper Results across all segregated scale folders
Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  SYNTHESIZING PAPER ARTIFACTS (TABLE 1 & PUBLICATION FIGURES)" -ForegroundColor Cyan
Write-Host "  Input CSVs: $($allCsvPaths -join ', ')" -ForegroundColor Cyan
Write-Host "  Destination: $OutputDir" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

if ($allCsvPaths.Count -gt 0) {
    python -u -m baselines.compare `
        --input-csv $allCsvPaths `
        --output-dir $OutputDir

    Write-Host "`n========================================================================" -ForegroundColor Green
    Write-Host "  BASELINES BENCHMARK & MULTI-SCALE SYNTHESIS COMPLETE!" -ForegroundColor Green
    Write-Host "  Segregated Scale Folders Created:" -ForegroundColor Green
    foreach ($n in $AgentCounts) {
        Write-Host "    - N=$n Agents: ${Prefix}_n${n}/" -ForegroundColor Green
    }
    Write-Host "  Paper Draft Artifacts in $OutputDir/:" -ForegroundColor Green
    Write-Host "    - Table 1 (Master Comparison):   $OutputDir/table1_master_baseline_comparison.*" -ForegroundColor Green
    Write-Host "    - Table 2 (Metrics by Scale):     $OutputDir/table2_metrics_by_agent_scale.*" -ForegroundColor Green
    Write-Host "    - Table 3 (Task Complexity Tier): $OutputDir/table3_task_complexity_breakdown.*" -ForegroundColor Green
    Write-Host "    - Table 4 (Dropout Resilience):   $OutputDir/table4_perturbation_resilience_breakdown.*" -ForegroundColor Green
    Write-Host "    - Figure 1 (Accuracy Bar Chart):  $OutputDir/figure_baseline_accuracy_comparison.png" -ForegroundColor Green
    Write-Host "    - Figure 2 (Dropout Resilience):  $OutputDir/figure_perturbation_resilience.png" -ForegroundColor Green
    Write-Host "    - Figure 3 (Pareto Token Cost):   $OutputDir/figure_token_accuracy_pareto.png" -ForegroundColor Green
    Write-Host "    - Master Raw CSV of All 900 Runs: $OutputDir/master_baseline_results.csv" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[ERROR] No baseline CSV files were produced to synthesize." -ForegroundColor Red
    exit 1
}
