$ErrorActionPreference = "Stop"
# Run from the repository root. These scenarios use synthetic status data only.
$scenarios = @("no-go", "review", "go")
foreach ($scenario in $scenarios) {
    $html = "reports/scenarios/$scenario.html"
    $report = "reports/scenarios/$scenario.md"
    python src/vcf_dashboard.py --status "data/scenarios/$scenario.csv" --html $html --report $report
    if ($LASTEXITCODE -ne 0) { throw "Scenario $scenario failed" }
}
Write-Host "Generated NO-GO, REVIEW, and GO evidence-tracking examples under reports/scenarios."
Write-Host "These are synthetic decision-rule demonstrations, not live VCF validation."
