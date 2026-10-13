# Scenario Demonstration

This repository includes three **synthetic evidence-tracking scenarios** to demonstrate how checklist states affect the decision logic. They are not representations of real VCF environments or vendor validation.

## Run all scenarios

From the repository root, on Windows, macOS, or Linux:

```bash
python scripts/run_scenarios.py
```

On PowerShell, the existing wrapper is also available with `\scripts\run-scenarios.ps1`, but the Python runner is recommended because it works across platforms and validates each expected decision.

The script writes HTML dashboards and Markdown reports to `reports/scenarios/`. It passes each scenario's status CSV into the same dashboard generator without changing the default `data/checklist_status.csv`.

| Input | Expected decision | Why |
|---|---|---|
| `data/scenarios/no-go.csv` | `NO-GO` | One or more blocking checks have missing evidence or are not started. |
| `data/scenarios/review.csv` | `REVIEW` | Blocking checks have synthetic evidence, but a non-blocking item remains in progress. |
| `data/scenarios/go.csv` | `GO` | All checks satisfy the evidence-tracking rule using synthetic placeholders or a documented illustrative N/A rationale. |

**Critical limitation:** The `GO` case means only that the fictional checklist satisfies this tool's rules. The placeholder evidence is not proof of supported upgrade paths, compatibility, component health, backups, change approval, or actual upgrade eligibility. Never use this scenario to authorize a production change. Replace synthetic references with verified evidence and complete product-supported technical prechecks in an authorized environment.
