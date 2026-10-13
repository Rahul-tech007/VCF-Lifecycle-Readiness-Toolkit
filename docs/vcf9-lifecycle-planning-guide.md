# VCF 9.x Lifecycle Planning Guide (Portfolio Lab)

**Status:** Conceptual planning guide, based on a training presentation and public Broadcom API documentation. It is not a validated upgrade procedure for a specific VCF deployment.

## Scope and evidence boundaries

The locally available presentation is titled **“VMware vSphere 8 to 9 Upgrade Project.”** It discusses a vSphere upgrade project: vCenter and ESXi sequencing, compatibility/HCL checks, backups, vSphere Lifecycle Manager, cluster-by-cluster execution, validation, rollback, approvals, and stakeholder coordination. These are useful planning topics, but a vSphere 8-to-9 presentation is **not proof of a supported VMware Cloud Foundation 9 upgrade path**. Confirm the exact product, source release, target release, BOM, and supported path in the current official VCF documentation for the actual environment.

This repository uses fictional data only. The toolkit does not connect to SDDC Manager, vCenter, NSX, ESXi, or any Broadcom API. It does not check compatibility, run prechecks, download bundles, schedule changes, or perform upgrades.

## Planning workflow

1. **Identify the environment** — record the VCF release, domain type, managed components, exact component versions, owners, and data classification. Use sanitized labels in this portfolio.
2. **Confirm release applicability** — consult the current VCF release notes, upgrade guide, interoperability/compatibility guidance, and component-specific documentation. Do not infer a supported path from a generic vSphere upgrade deck.
3. **Inventory lifecycle-managed components** — identify the management domain and workload/VI domains, and the relevant SDDC Manager, vCenter, ESXi, NSX, vSAN, and other components applicable to the deployment. Verify exact scope against the deployed version.
4. **Gather pre-change evidence** — health and alarm review, capacity, backup/recovery evidence, hardware/firmware/driver compatibility, networking and storage dependencies, certificates, licensing, and monitoring.
5. **Plan the change** — named owner, stakeholder contacts, CAB/change approval, maintenance window, outage/impact statement, ordered tasks, validation criteria, and decision points.
6. **Plan recovery** — document component-appropriate recovery steps, recovery-point expectations, escalation contacts, and explicit abort criteria. Do not assume a snapshot is a universal rollback method for every VCF component.
7. **Run supported product prechecks** — in a real VCF environment, use the workflow documented for that exact release. The public API reference describes lifecycle prechecks and task monitoring; older `/v1/system/prechecks` operations are marked deprecated in favour of the newer LCM check-sets endpoints. Confirm current API versions and permissions before any integration.
8. **Review and approve** — resolve blockers, capture evidence references, obtain the required approval, and make a human go/no-go decision.
9. **Execute only through the supported workflow** — this toolkit intentionally does not perform this step.
10. **Validate and close** — verify platform health, management access, alarms, cluster health, VM/network/storage connectivity, backup/monitoring, application-owner sign-off, and updated runbooks as appropriate to the change.

## Checklist: before scheduling

- [ ] Exact source and target VCF releases are confirmed from official documentation.
- [ ] Supported upgrade path and required intermediate releases are confirmed.
- [ ] Release BOM and component compatibility have been reviewed.
- [ ] Hardware, firmware, drivers, and relevant interoperability constraints are checked.
- [ ] Domain and component inventory is complete and current.
- [ ] Health, alarms, capacity, and dependency checks are recorded.
- [ ] Backup and recovery evidence is current and restore/recovery responsibilities are understood.
- [ ] Certificate, DNS, NTP, identity, licensing, and repository/bundle prerequisites are checked where applicable.
- [ ] Network paths (management, vMotion, storage, workload networks) and storage/datastore health are validated where applicable.
- [ ] Maintenance window, change record, stakeholder communications, and CAB approval are recorded.
- [ ] Execution sequence, success criteria, abort criteria, escalation contacts, and recovery plan are documented.
- [ ] Official product prechecks are completed and results reviewed in the target environment.
- [ ] Required evidence is sanitized before inclusion in this public portfolio.

## During-change control points

- Follow the supported release-specific workflow and component ordering; do not use this generic guide as an execution sequence.
- Record task IDs, timestamps, operator, outcome, warnings, and approved deviations without recording credentials or tokens.
- Stop and escalate if a mandatory precheck fails, unexpected component state appears, or a defined abort threshold is reached.
- Do not continue to the next stage until its documented acceptance criteria are met.

## Post-change validation

- [ ] VCF/SDDC Manager and vCenter management access is confirmed.
- [ ] Domain, cluster, host, and component health is reviewed.
- [ ] HA/DRS and lifecycle compliance are reviewed where applicable.
- [ ] Management, vMotion, storage, and workload network paths are validated where applicable.
- [ ] Datastores, multipathing, vSAN health, and storage services are reviewed where applicable.
- [ ] Monitoring, alerting, backup jobs, and operational integrations are healthy.
- [ ] Application owners confirm service validation.
- [ ] Evidence, known issues, and runbooks are updated; change is formally closed.

## Source mapping

The training presentation supplies the project-management topics: scope, current/target architecture, compatibility/HCL, pre-upgrade assessment, backup strategy, vCenter/ESXi upgrade planning, vLCM, network/storage/HA/DRS validation, rollback planning, risk register, CAB, downtime, operational checklist, and roles/responsibilities. The guide above reuses these as **planning prompts**, not as proof that any specific step or order is valid for VCF 9.x.

Official references:

- [VMware Cloud Foundation API Reference Guide](https://developer.broadcom.com/xapis/vmware-cloud-foundation-api/latest/) — API coverage for VCF components and lifecycle operations.
- [VCF Upgrades APIs](https://developer.broadcom.com/xapis/vmware-cloud-foundation-api/latest/upgrades/) — public API overview of bundle discovery, prechecks, upgrades, and task monitoring. Confirm exact behaviour for the deployed release.
- [VCF System Prechecks APIs](https://developer.broadcom.com/xapis/vmware-cloud-foundation-api/latest/system-prechecks/index.html) — precheck context; the page directs users to newer LCM check-set APIs where applicable.
- [VCF API Specifications](https://developer.broadcom.com/sdks/vcf-api-specification/latest) — API specifications and SDK-related resources.

## Portfolio disclosure

This is a self-directed planning/documentation exercise using synthetic inventory and training notes. It does not represent a completed VCF 9.x upgrade, a live-lab validation, or a production-tested runbook.
