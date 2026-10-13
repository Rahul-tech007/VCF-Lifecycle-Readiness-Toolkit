# VCF Lifecycle Readiness Toolkit (Portfolio Lab)

**Scope:** This is a read-only planning and validation lab using fictional data. It does not connect to or modify a live VMware Cloud Foundation environment. Do not present it as a completed VCF deployment or upgrade.

## What it demonstrates
- Infrastructure inventory validation
- Change-readiness evidence checks
- Markdown reporting
- Python unit tests and GitHub Actions CI
- Operational change planning: owner, maintenance window, backup evidence, health checks, compatibility reference, rollback plan, approval

## Run
Requires Python 3.10+; no third-party packages.

```bash
python src/vcf_readiness.py --input data/sample_environment.json --output reports/readiness-report.md
python -m unittest discover -s tests -v
```

The tool checks planning evidence only. `READY` means the checklist is complete, not that a real upgrade path is vendor-supported. Validate exact deployed versions against current Broadcom documentation before any real change.

## Layout
- `data/sample_environment.json` — synthetic sample inventory
- `src/vcf_readiness.py` — report generator
- `tests/` — unit tests
- `docs/` — design and runbook
- `.github/workflows/tests.yml` — CI test workflow
- `reports/sample-readiness-report.md` — generated example

## Next steps
1. Replace the synthetic sample data with additional fictional test cases.
2. Add CSV export and severity filters.
3. In a separate lab, consider a read-only API integration using an authorized test environment and official SDKs.
4. Never commit credentials, production inventories, internal hostnames, or company-sensitive data.

## Official references
- [VCF API Reference](https://developer.broadcom.com/xapis/vmware-cloud-foundation-api/latest/)
- [VCF API Specifications](https://developer.broadcom.com/sdks/vcf-api-specification/latest)
- [VCF 9.0 developer documentation overview](https://blogs.vmware.com/cloud-foundation/2025/07/06/improved-developer-documentation/)
