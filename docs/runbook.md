# Runbook

**Purpose:** This student-maintained runbook records local preparation, dataset configuration, Databricks workspace readiness, Bronze and Silver execution and validation, troubleshooting, and reruns. The supplied notebooks and guides define the engineering foundation; Gold implementation and analytical methods remain team-controlled. Record team-specific assumptions and environment details here without committing credentials, secrets, source data, or private paths.

## Prerequisites

Confirm that the team has:

- Git and GitHub access for the shared repository.
- A supported Python development environment and the project dependencies.
- Access to the shared Databricks workspace and the intended development target.
- The Databricks CLI, with each team member authenticated individually.
- The workspace, catalog, schema, and Volume permissions needed by the approved implementation.
- The five supplied dataset profiles and their colocated `manifest.json` files.
- A team agreement on who coordinates shared-workspace deployments for each approved change.

Record environment-specific gaps or permission issues in this runbook; do not record credentials or tokens.

## Clone Repository

- GitHub is the team's shared source of truth. Document the repository clone process and any template-specific setup actions after cloning.
- Use the established feature-branch and pull-request workflow. Deploy only approved changes merged to the team's `main` branch.
- The separate Git/GitHub team workflow guide is distributed through Canvas. The repository's collaboration responsibilities are summarized in [`AGENTS.md`](../AGENTS.md), [`README.md`](../README.md), and [`docs/governance.md`](governance.md); this runbook does not duplicate the full tutorial.

## Create Local Environment

- Document how the team creates and activates a local environment.
- Record any approved package additions beyond the starter requirements.
- Keep local configuration and authentication files out of Git. Distinguish local unit/configuration checks from execution in Databricks.

## Configure Dataset

The configuration template at [`config/dataset_config.example.yml`](../config/dataset_config.example.yml) supports these five independent profiles:

1. `napa_5k_clean`
2. `napa_5k_tainted`
3. `napa_50k_clean`
4. `napa_50k_tainted`
5. `napa_250k_production`

- Select one profile at a time through the job parameter. Use the same two supplied notebooks for every profile.
- Keep each profile's Raw, Bronze, and Silver destinations separate.
- Replace the catalog and prefix placeholders with team-owned Unity Catalog values. Raw paths follow `/Volumes/<catalog>/<profile-specific-raw-schema>/napa_files`; accepted tables, rejects, and the DQ summary share the corresponding profile-specific Silver schema.
- The student bootstraps do not create legacy enterprise operational evidence. Keep Gold storage separate and team-controlled.
- Students create and populate Raw Volumes; the bootstrap verifies but never modifies or uploads Raw files.
- Do not use a local `data/raw` directory as a substitute for the configured Raw Volume. Keep local configuration safe and do not commit datasets or secrets.

## Databricks Setup Notes

- Confirm the intended Databricks workspace, catalog, profile-specific Raw Volumes, Bronze schemas, and permissions.
- Coordinate shared reloads and keep `existing_table_action = "fail"` for normal operation.
- Follow the [`Bronze and Silver bootstrap guide`](bootstrap_guide.md) for bundle validation, deployment, manual job execution, and inspection.
- Note any differences between local development, Databricks Free Edition, and reviewer environments without assuming capabilities or permissions not confirmed by the team.

## Run the Supplied Bootstraps

1. Validate and deploy the reviewed bundle from approved GitHub `main` using the team's catalog, prefix, and explicit CLI profile.
2. Manually run `napa_bronze_bootstrap` for one profile, beginning with `napa_5k_clean`; keep `existing_table_action=fail`.
3. Confirm all 13 Bronze tables report `PASS`, inspect representative records, and record the evidence.
4. Manually run `napa_silver_bootstrap` for that same profile; keep `existing_table_action=fail`.
5. Inspect the 13 accepted tables, 13 reject tables, and `silver_data_quality_summary`; confirm table-level reconciliation.
6. Use `replace` only for a coordinated, intentional full refresh of the selected team-owned profile.

The jobs are independent: there is no schedule or automatic chain. Gold execution, notebooks, and analytical methods remain team-designed.

## Profile Execution Sequence

Use this recommended progressive testing order:

1. `napa_5k_clean`
2. `napa_5k_tainted`
3. `napa_50k_clean`
4. `napa_50k_tainted`
5. `napa_250k_production`

For each profile, complete and inspect Bronze before manually running Silver. Use the same supplied pair of bootstraps and profile-isolated destinations for every profile.

This is a progressive testing sequence, not a mapping of dataset sizes to milestones:

- **Milestone 1:** Prepare and validate all five Raw profiles, then build Bronze for both 5K profiles.
- **Milestone 2:** Complete Bronze and Silver processing for all five profiles.
- **Milestone 3:** Develop team-designed Gold analytics and final recommendations using the `napa_250k_production` dataset.

## Run Evidence Checklist

For each Bronze, Silver, or Gold run, record as applicable:

- Dataset profile.
- Configuration or version reference and Git commit or implementation version.
- Exact deployed Git commit SHA and deployment coordinator for shared releases.
- Processing layer and actual workflow identity.
- Run identifier and execution status.
- Actual catalog, schema, Volume, and table names.
- Source, accepted, and rejected record counts.
- Reconciliation results.
- Bronze bootstrap manifest/Raw/Bronze validation results.
- Quality findings and exception evidence.
- Acceptance-check results.
- Relevant logs or diagnostics.
- Reviewer and verification status.

Do not invent execution results. Refer to [`docs/data_dictionary.md`](data_dictionary.md) for field contracts and evidence definitions.

## Review Outputs and Documentation

After each authorized run, review the generated tables, counts, reconciliation, quality findings, exceptions, acceptance checks, and diagnostics. Keep expected specification separate from verified execution evidence.

Update the following documents as evidence becomes available:

- [`docs/lineage.md`](lineage.md) with actual source-to-output names, run identifiers, and verified lineage.
- [`docs/data_quality_report.md`](data_quality_report.md) with observed findings, handling decisions, and downstream implications.
- [`docs/data_dictionary.md`](data_dictionary.md) when physical schemas are verified or team-owned Gold structures are implemented.
- [`docs/governance.md`](governance.md) when ownership or operating decisions change.

## Failures, Reruns, and Troubleshooting

Capture recurring issues and the team's resolution, including:

- Authentication or workspace-permission failures.
- Incorrect profile selection, catalog, schema, or Volume configuration.
- Missing Raw Parquet files or colocated manifests.
- Notebook import, attachment, or execution failures.
- Bronze or Silver execution failures.
- Rejected records and unresolved parent references.
- Reconciliation or acceptance-check failures.
- Partial or incomplete runs.

Inspect the job output and any tables created before a failure. Investigate the cause, confirm the selected profile and destinations, and use `replace` only for a deliberate coordinated reload. Record the problem, corrective action, and later result. Do not change Raw data or invent repairs to make a check pass; do not run Silver unless Bronze reported `OVERALL PASS`.

## Milestone Evidence and Submissions

Organize supporting evidence in the form most useful to the team; this runbook does not prescribe repository folder names. Retain the relevant configuration, code version, run identifiers, validation results, quality findings, lineage, and decision records for review.

Canvas assignments and the NAPA RFP govern formal deliverables, required evidence, and submission procedures. The three milestones represent the progression described above and do not correspond exclusively to individual dataset sizes.

## Known Environment Differences

Record relevant differences across Windows, Linux, macOS, local development, Databricks, and reviewer environments. Keep local checks and controlled live Databricks Free Edition execution as distinct evidence. Use the active Databricks SparkSession and documented serverless APIs. Test doubles must not hide unsupported runtime calls. Keep this section concise and avoid unvalidated installation instructions.
