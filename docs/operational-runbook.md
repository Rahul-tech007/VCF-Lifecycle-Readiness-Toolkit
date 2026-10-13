# Operational runbook

Generate report:
```bash
python src/vcf_readiness.py --input data/sample_environment.json --output reports/readiness-report.md
```

Run tests:
```bash
python -m unittest discover -s tests -v
```

Review each gap. Confirm actual versions and vendor-supported upgrade paths in current Broadcom documentation before any real infrastructure change. Never commit credentials or sensitive company inventory.
