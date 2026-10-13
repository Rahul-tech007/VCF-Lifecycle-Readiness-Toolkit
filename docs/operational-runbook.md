# Operational Runbook (Portfolio Lab)

## Generate a report

From the repository root:

```bash
python src/vcf_readiness.py --input data/sample_environment.json --output reports/readiness-report.md
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Review process

1. Inspect each generated status and evidence gap.
2. Treat `BLOCKED` and `REVIEW` as prompts for human follow-up.
3. Do not treat `READY` as proof of compatibility, a successful vendor precheck, or authorization to perform an upgrade.
4. For any real environment, confirm the exact deployed and target VCF releases, component BOM, supported upgrade path, and current product workflow in official Broadcom documentation.
5. Use the VCF 9.x planning guide and CSV checklist as documentation templates only. Mark non-applicable checks with a reason in a real change record.
6. Keep secrets, production inventories, internal hostnames, certificate private keys, API tokens, and restricted course content out of Git.

## Safety boundary

This tool is offline and read-only. It does not call VCF APIs, collect credentials, validate compatibility, perform prechecks, download bundles, schedule changes, or execute upgrades.
