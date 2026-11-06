# Data Lineage

**Purpose:** Maintain traceable evidence for the flow **Raw → Bronze → Silver → Gold → Olympic Recommendations**. Lineage supports reproducibility, governance, validation, and defensible business recommendations by connecting each output to its source data, processing rules, quality evidence, and execution record.

The Bronze and Silver entries below describe the supplied bootstrap contracts. They are not proof that a team's deployed Databricks resources conform to those contracts.

## Dataset Profiles and Naming

The same parameterized engineering lineage applies independently to all five full-refresh profiles:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

Resolve `<catalog>`, `<raw_schema>`, `<bronze_schema>`, and `<silver_schema>` from team configuration. Record fully qualified deployed names during verification; do not substitute illustrative defaults for observed resources.

## Expected Lineage — Based on Supplied Bootstraps

### Raw to Bronze

The supplied Bronze notebook and operating guide govern this layer. Each selected profile supplies 13 Parquet files and a colocated `manifest.json`. The manifest is delivery and validation evidence, not a Bronze table.

For every source, Bronze retains each successfully ingested record and all business columns in source order, including duplicate logical keys and invalid values, and appends the ten prescribed metadata columns. Source-designated keys are lineage metadata, not physically enforced uniqueness constraints. Bronze performs no business cleansing, filtering, joins, sorting, deduplication, referential-integrity enforcement, or feature engineering. The normal `fail` action protects existing tables; an intentional selected-profile reload uses `replace`.

| Raw source file | Source profile | Bronze destination | Significant ingestion or preservation behavior | Mandatory certification and validation controls |
|---|---|---|---|---|
| `regions.parquet` | Any approved profile | `<catalog>.<bronze_schema>.regions` | Raw-preserving copy with ingestion metadata appended | Manifest inventory, checksum, row count, ordered schema/hash, readability, and Raw/Bronze reconciliation |
| `clubs.parquet` | Any approved profile | `<catalog>.<bronze_schema>.clubs` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `club_memberships.parquet` | Any approved profile | `<catalog>.<bronze_schema>.club_memberships` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_master.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_master` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_registrations.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_registrations` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `player_assessment_history.parquet` | Any approved profile | `<catalog>.<bronze_schema>.player_assessment_history` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `teams.parquet` | Any approved profile | `<catalog>.<bronze_schema>.teams` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `team_memberships.parquet` | Any approved profile | `<catalog>.<bronze_schema>.team_memberships` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `matches.parquet` | Any approved profile | `<catalog>.<bronze_schema>.matches` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_teams.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_teams` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_team_players.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_team_players` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `match_games.parquet` | Any approved profile | `<catalog>.<bronze_schema>.match_games` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |
| `monthly_batches.parquet` | Any approved profile | `<catalog>.<bronze_schema>.monthly_batches` | Raw-preserving copy with ingestion metadata appended | Same required readiness and reconciliation controls |

The notebook reports one validation row per table and an overall result. Do not run Silver unless all 13 tables report `PASS` and the notebook reports `OVERALL PASS`. The student bootstrap does not create the legacy enterprise operations tables described elsewhere as reference material.

### Bronze to Silver

The supplied Silver notebook reads the 13 tables in the selected profile's Bronze schema and writes exactly 27 managed tables in that profile's Silver schema:

- 13 accepted tables with the same names as their Bronze sources;
- 13 rejection tables named `<source_table>_rejects`; and
- `silver_data_quality_summary`.

The notebook standardizes documented fields, derives the two approved age fields, applies exactly the 25 record-level rules in `docs/silver_specification.md`, and reconciles each source as `Bronze = accepted + rejected`. Reject rows retain source values and reason arrays. Expected data defects may produce rejects without failing the job; technical or reconciliation failures remain visible.

Record the job run, fully qualified schemas, accepted/rejected counts, `TABLE_TOTAL` reconciliation rows, and `REASON_TOTAL` rule evidence. The supplied Silver baseline creates no convenience views, separate reject schema, or enterprise operations tables.

## Verified Lineage — Student Record

Verify expected lineage against the generated implementation and deployed Databricks resources for each profile. Do not mark an entry verified from documentation alone.

| Profile and layer | Expected mapping reference | Implementation status | Actual fully qualified source(s) | Actual fully qualified destination(s) | Run ID or validation evidence | Deviation and disposition | Verified by/date |
|---|---|---|---|---|---|---|---|
|  |  | Not started / implemented / verified |  |  |  |  |  |

Record deviations without silently changing the expected specification. Resolve Bronze or Silver deviations against the active layer guidance and retain evidence of any approved decision.

## Gold Lineage — Team-Completed Template

Gold design is entirely team-defined. Add one row per Gold table, feature set, analytical output, figure, or recommendation artifact; do not treat the examples of required fields as a prescribed architecture or method.

| Silver source tables/views | Team-defined Gold destination or analytical output | Derived features and measures | Transformations and business logic | Validation and quality controls | Recommendation connection | Run/evidence reference | Owner/status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

For every analytical output, document the dataset profile, source grain, joins, date window, assumptions, exclusions, uncertainty, and relevant quality findings. Final production recommendations should be traceable to `napa_250k_production` Silver evidence.

Use the following coverage register to connect team-defined Gold evidence to required business decisions without prescribing how those decisions are calculated:

| Country | Doubles category | Primary roster evidence | Alternate evidence | Development-camp evidence | Final recommendation artifact |
|---|---|---|---|---|---|
| USA | Men's doubles |  |  |  |  |
| USA | Women's doubles |  |  |  |  |
| USA | Mixed doubles |  |  |  |  |
| Canada | Men's doubles |  |  |  |  |
| Canada | Women's doubles |  |  |  |  |
| Canada | Mixed doubles |  |  |  |  |

## Known Lineage Gaps and Follow-up

| Gap or unresolved deviation | Affected profile/layer/output | Business or validation impact | Owner | Next action | Status |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
