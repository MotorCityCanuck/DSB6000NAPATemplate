# Governance

**Purpose:** This student-maintained record captures the team's governance decisions, responsibilities, access practices, stewardship, risks, and accountability for the NAPA project. Keep entries concise and update them when a material decision changes.

## Authority and boundaries

- The supplied [Bronze bootstrap guide](bronze_bootstrap_guide.md) governs operation and validation of the student Bronze utility.
- Instructor-provided Silver specifications and a revised prompt are forthcoming.
- The official RFP and Canvas assignments govern business deliverables, eligibility, milestones, and submissions.
- The team controls Gold architecture, analytical methods, validation choices, and recommendation logic. Team decisions must remain supported by evidence and must not rewrite Raw, Bronze, Silver, rejection, or audit evidence.

This document records governance choices and accountability. It does not replace active layer guidance or duplicate detailed architecture, execution, quality, lineage, or security procedures.

## Team operating model

The four-member team may share or rotate responsibilities. Record people or role labels only after the team agrees; no permanent individual assignment is required.

| Responsibility area | Responsible team member(s) | Backup or reviewer | Notes or status |
|---|---|---|---|
| GitHub integration and pull-request coordination | `[ ]` | `[ ]` | `[ ]` |
| Databricks deployment coordination | `[ ]` | `[ ]` | `[ ]` |
| Dataset/profile and configuration stewardship | `[ ]` | `[ ]` | `[ ]` |
| Data-quality and reconciliation evidence | `[ ]` | `[ ]` | `[ ]` |
| Architecture, lineage, and data-dictionary documentation | `[ ]` | `[ ]` | `[ ]` |
| Gold analytical validation and recommendation review | `[ ]` | `[ ]` | `[ ]` |
| Final deliverable integration | `[ ]` | `[ ]` | `[ ]` |

The team remains collectively accountable for submitted work. Assign an owner for resolving each integration conflict, while allowing review and escalation to be shared.

## GitHub and deployment accountability

- GitHub is the shared source of truth for reviewed code, configuration, tests, and documentation.
- All four team members may develop on feature branches, use Codex, run local tests, deploy personal development bundles, and test non-destructive functionality. Use pull requests and review shared changes before merging to the team `main` branch.
- Assign an integration-conflict owner when changes overlap; record the decision and affected evidence when needed.
- Validate, deploy, and run Databricks Asset Bundles manually. A shared release deployment must originate from approved GitHub `main` and a clean local checkout synchronized to it. Designate one deployment coordinator for each approved deployment; this responsibility may rotate.
- The coordinator must select an explicit local Databricks CLI profile, verify the intended workspace, and record the exact deployed Git commit SHA with the release evidence.
- Coordinate any full-refresh execution that can reset shared Bronze, Silver, or Gold data. A personal development deployment does not authorize an uncoordinated reset of shared data.
- Separate personal data schemas are not required. Use the team's approved configuration and coordination controls rather than adding unnecessary infrastructure.
- Keep deployment commands and environment-specific procedures in [`docs/runbook.md`](runbook.md). Do not assume GitHub Actions are available.

## Workspace access and credentials

- Team members authenticate individually to the shared Databricks workspace and GitHub repository.
- Keep credentials, tokens, secrets, local authentication files, private workspace paths, and source datasets out of Git commits.
- Record relevant access responsibilities, missing permissions, and approved follow-up actions here without inventing institutional security policies or workspace capabilities.
- Coordinate shared workspace changes through the deployment process and review them against the selected profile and approved configuration.

## Data stewardship and evidence

The team stewards all five independent full-refresh profiles:

`napa_5k_clean`, `napa_5k_tainted`, `napa_50k_clean`, `napa_50k_tainted`, and `napa_250k_production`.

Record responsibility for:

- Preserving supplied Raw Parquet files and `manifest.json` unchanged and outside GitHub.
- Maintaining profile separation and using the prescribed Bronze and Silver processing contracts.
- Keeping configuration, run identifiers, counts, reconciliation, quality findings, deviations, and disposition evidence.
- Maintaining the data dictionary and expected-versus-verified lineage.
- Recording quality exceptions, assumptions, analytical limitations, and their effects on recommendations.

Refer to [`docs/data_dictionary.md`](data_dictionary.md), [`docs/lineage.md`](lineage.md), and [`docs/data_quality_report.md`](data_quality_report.md) for the corresponding documentation structures. Do not reproduce their field contracts, evidence schemas, or detailed validation rules here.

## AI-assisted development accountability

Students remain responsible for AI-generated code, tests, documentation, analysis, and recommendations. The team must review and validate AI-assisted work, explain material assumptions, and reject unsupported claims or outputs that conflict with active instructor guidance.

Record meaningful AI assistance, human review, risks, and validation in [`docs/ai_usage_summary.md`](ai_usage_summary.md). AI output does not override prescribed Bronze/Silver requirements or establish analytical evidence without appropriate execution and review.

## Governance decisions and risks

Record only decisions the team has made or questions that require follow-up. Do not mark placeholders as completed decisions.

| Decision or issue | Rationale | Alternatives considered | Responsible person | Status | Risks or assumptions |
|---|---|---|---|---|---|
| Catalog and namespace structure |  |  |  | Open |  |
| Naming conventions |  |  |  | Open |  |
| Profile and configuration stewardship |  |  |  | Open |  |
| GitHub review and integration practice |  |  |  | Open |  |
| Databricks deployment coordination |  |  |  | Open |  |
| Ownership of final analytical outputs |  |  |  | Open |  |
| Data classification and sharing assumptions |  |  |  | Open |  |
| Workspace access and unresolved permissions |  |  |  | Open |  |
| AI review and accountability practice |  |  |  | Open |  |

## Documentation boundaries

| Topic | Primary reference |
|---|---|
| Architecture and namespaces | [`docs/architecture.md`](architecture.md) |
| Authentication, setup, deployment, execution, and troubleshooting | [`docs/runbook.md`](runbook.md) |
| Expected and verified lineage | [`docs/lineage.md`](lineage.md) |
| Field contracts and team-defined Gold fields | [`docs/data_dictionary.md`](data_dictionary.md) |
| Quality findings and downstream impact | [`docs/data_quality_report.md`](data_quality_report.md) |
| AI-assisted work and human review | [`docs/ai_usage_summary.md`](ai_usage_summary.md) |
| Bronze student workflow | [`notebooks/00_bootstrap_bronze.py`](../notebooks/00_bootstrap_bronze.py) and [`docs/bronze_bootstrap_guide.md`](bronze_bootstrap_guide.md) |
| Silver engineering requirements | Revised instructor specifications and prompt forthcoming |
