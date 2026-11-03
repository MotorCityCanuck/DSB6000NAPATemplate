# Runbook

**Purpose:** This student-maintained runbook records local preparation, dataset configuration, Databricks workspace readiness, deployment and execution of generated workflows, result verification, operational evidence, troubleshooting, and reruns for the NAPA Olympic Analytics Platform. The Raw-to-Bronze and Bronze-to-Silver construction prompts define the required engineering behavior; Gold implementation and analytical methods remain team-controlled. Record team-specific assumptions and environment details here without committing credentials, secrets, source data, or private paths.

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

- Select one profile through configuration and the `dataset_profile` parameter. Use the same parameterized Bronze implementation and the same parameterized Silver implementation for every profile.
- Bronze and Silver are full-refresh processes for the selected profile; keep each profile's Raw, Bronze, accepted Silver, and Silver-reject destinations separate.
- Replace the catalog and schema placeholders with team-owned Unity Catalog values. Raw paths follow `/Volumes/<catalog>/<profile-specific-raw-schema>/napa_files`; accepted Silver and Silver-reject outputs use their corresponding profile-specific schemas.
- Bronze and Silver operational evidence uses the shared team operations schema, following the construction-prompt naming convention `<team_prefix>_ops`. The implementation/runtime configuration establishes that schema; `config/dataset_config.example.yml` intentionally does not expose an `operations_schema` key. Bronze and Silver retain their distinct operational-evidence table contracts. Keep Gold storage separate and team-controlled.
- Do not use a local `data/raw` directory as a substitute for the configured Raw Volume. Keep local configuration safe and do not commit datasets or secrets.

## Databricks Setup Notes

- Each team member authenticates individually with the Databricks CLI. Confirm that the CLI targets the team's shared workspace and that the `dev` target in [`databricks.yml`](../databricks.yml) uses the team's approved workspace URL placeholder before deployment.
- Record the team's catalog, profile-specific schemas, Raw Volumes, shared operations schema, and permission gaps. Resolve namespace values before implementation execution.
- Coordinate changes to the shared workspace through the designated deployment coordinator. The coordinator deploys approved changes from the team's GitHub `main` branch; do not make conflicting manual workspace changes.
- The current [`databricks.yml`](../databricks.yml) intentionally contains no executable workflow resources. Students must generate the required Bronze and Silver jobs and entry points according to [`docs/raw_to_bronze_prompt.md`](raw_to_bronze_prompt.md) and [`docs/bronze_to_silver_prompt.md`](bronze_to_silver_prompt.md) before attempting workflow execution.
- Note any differences between local development, Databricks Free Edition, and reviewer environments without assuming capabilities or permissions not confirmed by the team.

## Deploy and Execute Generated Workflows

The template currently has no executable bundle resources. These steps become actionable after the team generates the prescribed workflow resources and entry points from the construction prompts.

1. Complete and review implementation changes.
2. Merge approved changes into the team's shared GitHub branch.
3. Confirm the intended Databricks workspace, development target, and profile configuration.
4. Validate the Asset Bundle manually:

   ```powershell
   databricks bundle validate -t dev
   ```

5. Deploy the approved bundle manually:

   ```powershell
   databricks bundle deploy -t dev
   ```

6. Confirm that the expected generated workflow resources are available.
7. Execute the selected workflow using the actual generated resource name and the selected `dataset_profile`.
8. Review the results and capture the run evidence below.

Bronze workflow structure and execution responsibilities come from [`docs/raw_to_bronze_prompt.md`](raw_to_bronze_prompt.md). Silver workflow structure and execution responsibilities come from [`docs/bronze_to_silver_prompt.md`](bronze_to_silver_prompt.md). Do not assume that either workflow exists before implementation. Gold execution, notebooks, and analytical methods are team-designed.

## Profile Execution Sequence

Use this recommended progressive testing order:

1. `napa_5k_clean`
2. `napa_5k_tainted`
3. `napa_50k_clean`
4. `napa_50k_tainted`
5. `napa_250k_production`

For each profile, complete and validate Bronze before its dependent Silver processing. Use the same parameterized implementation, full-refresh behavior, and profile-isolated destinations for every profile. Record the actual generated workflow names and execution commands after implementation; do not invent them in this template.

This is a progressive testing sequence, not a mapping of dataset sizes to milestones:

- **Milestone 1:** Prepare and validate all five Raw profiles, then build Bronze for both 5K profiles.
- **Milestone 2:** Complete Bronze and Silver processing for all five profiles.
- **Milestone 3:** Develop team-designed Gold analytics and final recommendations using the `napa_250k_production` dataset.

## Run Evidence Checklist

For each Bronze, Silver, or Gold run, record as applicable:

- Dataset profile.
- Configuration or version reference and Git commit or implementation version.
- Processing layer and actual workflow identity.
- Run identifier and execution status.
- Actual catalog, schema, Volume, and table names.
- Source, accepted, and rejected record counts.
- Reconciliation results.
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
- Bundle validation or deployment failures.
- Missing generated workflow resources.
- Bronze or Silver execution failures.
- Rejected records and unresolved parent references.
- Reconciliation or acceptance-check failures.
- Partial or incomplete runs.

Inspect logs and operational evidence before taking corrective action. Follow the construction prompts' failure and rerun contracts; do not manually delete evidence or output tables as routine troubleshooting. Record the problem, corrective action, and results of the subsequent run. Do not change Raw data or invent data-repair policies to make a check pass.

## Milestone Evidence and Submissions

Organize supporting evidence in the form most useful to the team; this runbook does not prescribe repository folder names. Retain the relevant configuration, code version, run identifiers, validation results, quality findings, lineage, and decision records for review.

Canvas assignments and the NAPA RFP govern formal deliverables, required evidence, and submission procedures. The three milestones represent the progression described above and do not correspond exclusively to individual dataset sizes.

## Known Environment Differences

Record relevant differences across Windows, Linux, macOS, local development, Databricks, and reviewer environments. Keep this section concise and avoid adding unvalidated installation instructions or platform-specific commands.
