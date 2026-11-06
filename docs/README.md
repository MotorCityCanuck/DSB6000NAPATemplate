# NAPA Technical Documentation

The `/docs` directory contains the supplied engineering specifications and the team's working documentation for the NAPA Olympic Analytics case study. The official NAPA RFP and Canvas assignments govern business requirements, milestones, eligibility, submissions, and assessment.

## Assignment 10 workflow

Use these documents in order:

1. [Bronze and Silver bootstrap guide](bootstrap_guide.md) — configure the team namespace, manually validate and deploy the bundle, run Bronze, inspect it, run Silver, and inspect DQ evidence.
2. [Bronze bootstrap guide](bronze_bootstrap_guide.md) — detailed Raw Volume, Bronze validation, and safe-reload guidance.
3. [Silver specification](silver_specification.md) — the accepted-table contract, reject outputs, DQ summary, and all 25 approved rejection rules.

The supplied notebooks implement Bronze and Silver. Historical Raw-to-Bronze, Bronze-to-Silver, and Silver build prompts are not active student instructions. Gold organization, features, methods, validation choices, and recommendation logic remain team-designed within the assignment requirements.

## Dataset and technical references

| Document | Purpose | Authority or maintenance |
|---|---|---|
| [Dataset specification](dataset_specification.md) | Profiles, source package contents, grains, relationships, and release conventions. | Prescribed technical reference |
| [Data dictionary](data_dictionary.md) | Field definitions and unresolved semantic questions; legacy enterprise sections are reference-only. | Team-maintained |
| [Data quality rules](data_quality_rules.md) | Registry for approved Silver rules and additional team-defined analytical checks. | Team-maintained |
| [Architecture](architecture.md) | Platform layers, namespaces, deployment approach, and decisions. | Team-maintained |
| [Lineage](lineage.md) | Expected and verified source-to-output traceability. | Team-maintained |

## Team working documents

| Document | What the team records |
|---|---|
| [Assignment context](assignment_context.md) | Client objectives, scope, assumptions, and clarification needs. |
| [Analytical methodology](analytical_methodology.md) | Team-selected Gold approach, validation, uncertainty, and recommendation rationale. |
| [Data quality report](data_quality_report.md) | Actual run findings, handling decisions, readiness, and analytical impacts. |
| [Governance](governance.md) | Ownership, stewardship, access, controls, and governance risks. |
| [Runbook](runbook.md) | Actual setup, parameters, runs, issues, fixes, and evidence. |
| [AI usage summary](ai_usage_summary.md) | AI-assisted activities, human review, validation, and accountability. |
