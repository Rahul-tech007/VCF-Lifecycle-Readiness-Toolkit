# Source Material Map

This map records how the training presentation **“VMware vSphere 8 to 9 Upgrade Project”** informs the public portfolio. It avoids copying the presentation wholesale and separates its vSphere-focused content from VCF-specific claims.

| Training presentation topic | Portfolio treatment | Boundary / caveat |
|---|---|---|
| Project overview, scope, roles and responsibilities | Planning workflow and change record | Customize to a fictional scenario only |
| Compatibility/HCL, firmware, drivers, backup software | Pre-change checklist | Validate against current official release-specific guidance |
| Health, capacity, snapshots, licensing | Pre-change evidence prompts | No automated technical validation is performed |
| Backup strategy and rollback plan | Required evidence and recovery-planning prompts | Recovery is component-specific; do not assume snapshot rollback always applies |
| vCenter and ESXi upgrade overview | General change-planning concepts | Do not treat as a VCF 9.x upgrade sequence |
| vSphere Lifecycle Manager image/compliance/remediation | Lifecycle terminology in the guide | Confirm VCF-specific orchestration and supported workflow for the target release |
| Network, storage, HA/DRS validation | Post-change validation prompts | Applies only where relevant to the actual design |
| CAB, maintenance window, risk register and communications | Change-control evidence fields | No approval is inferred by the toolkit |

## Source limitation

The presentation's stated scenario is vSphere 8.x to vSphere 9 and its own slides indicate that environment-specific content and architecture screenshots must be customized. It does not, by itself, establish a supported VCF 9.x upgrade path. Keep the original presentation and course materials private unless you have permission to redistribute them. This repository contains an original summary/checklist rather than the source deck.
