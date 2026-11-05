# Architecture

## 1. Purpose and Document Boundaries

This student-maintained document describes the high-level architecture of the NAPA Olympic Analytics Platform: its processing layers, technology responsibilities, configurable namespaces, deployment approach, and team decisions. It consolidates the useful layer-design guidance previously separated from the main architecture record.

This document does not replace the supplied Bronze notebook and guide or the forthcoming revised Silver guidance. The official RFP and Canvas assignments remain authoritative for business deliverables and eligibility requirements.

## 2. System Context and Technology Responsibilities

```text
Delivered Parquet files + manifest.json
  -> Unity Catalog Raw Volume
  -> Bronze Delta tables
  -> Silver accepted tables + exceptions + quality evidence
  -> Team-designed Gold analytics
  -> USA and Canada Olympic roster, alternate, and development-camp recommendations
```

| Technology or participant | Architectural responsibility |
|---|---|
| GitHub repository | Shared source of truth for reviewed configuration, implementation, tests, and maintainable documentation; never a store for Raw datasets, credentials, private paths, or generated Delta storage |
| Databricks Free Edition workspace | Team-shared execution environment for Unity Catalog storage, serverless-compatible processing, validation, and analytical work |
| Unity Catalog | Configurable catalog, schemas, Volumes, managed tables, views, and operational evidence with profile isolation |
| Databricks CLI and Asset Bundles | Individual authentication and manual validation, deployment, and execution of approved team changes |
| Reusable source modules and SQL | Testable implementation of prescribed engineering behavior and team-designed analytics |
| Notebooks or scripts | The supplied notebook implements Bronze; Silver structure will follow the revised instructor guidance |
| AI-assisted development tools | Generate and explain work at team direction; students review, test, approve, and defend the results |

## 3. Five-Profile Dataset Strategy

One parameterized Bronze implementation and one parameterized Silver implementation support five independent, complete historical profiles. The profiles are not incremental steps or monthly updates to one another.

| Dataset profile | Role | Source condition |
|---|---|---|
| `napa_5k_clean` | Development | Clean |
| `napa_5k_tainted` | Development and quality testing | Intentionally tainted |
| `napa_50k_clean` | Engineering validation | Clean |
| `napa_50k_tainted` | Engineering and quality validation | Intentionally tainted |
| `napa_250k_production` | Production-scale analysis and final recommendations | Production data with intentional imperfections |

Profile selection occurs through the supplied Bronze notebook's widget and configuration, not through separate implementations. Build and validate Bronze before Silver for each profile; use production Silver evidence from `napa_250k_production` for final recommendations.

## 4. Raw, Bronze, Silver, and Gold Layer Responsibilities

| Layer | Purpose and expected content | Quality and preservation boundary | Ownership |
|---|---|---|---|
| Raw | The 13 supplied Parquet files and colocated `manifest.json` in the selected Unity Catalog Volume | Preserve the delivered package unchanged; the Bronze bootstrap validates its inventory and manifest | Prescribed engineering foundation |
| Bronze | Raw-preserving managed Delta representation with prescribed ingestion metadata | Preserve every Raw record one-for-one, including duplicate logical keys and business defects; reconcile manifest, Raw, and Bronze counts; perform no business cleansing or feature engineering | Supplied by `notebooks/00_bootstrap_bronze.py` and `docs/bronze_bootstrap_guide.md` |
| Silver | Standardized, quality-controlled analytical foundation | Follow the instructor-provided Silver specifications and revised prompt when published; do not fabricate corrections or requirements | Revised guidance forthcoming |
| Gold | Decision-ready features, measures, comparisons, analytical products, and recommendation evidence | Team defines analytical quality controls and documents assumptions, limitations, uncertainty, and lineage without rewriting upstream evidence | Team-defined |

The supplied Bronze notebook and guide define the active student Bronze workflow. Revised Silver guidance is forthcoming. This architecture records only the layer boundaries.

Source-designated Raw/Bronze keys describe logical entity identity and relationships; they do not impose physical uniqueness in Bronze. Normal bootstrap use keeps `existing_table_action = "fail"`; intentional reloads replace only the selected expected Bronze tables as documented in the guide. The bootstrap does not create enterprise operational evidence. Silver validation and enforcement behavior will be defined by the forthcoming revised guidance.

## 5. Unity Catalog Namespace and Storage Architecture

Catalog and team prefix values are configurable. The patterns below are the construction-prompt conventions; actual values must be team-owned and recorded without embedding credentials or personal paths.

| Object | 5K and 50K profiles | 250K production profile |
|---|---|---|
| Raw schema | `<team_prefix>_<scale>_<condition>_raw` | `<team_prefix>_250k_raw` |
| Raw Volume path | `/Volumes/<catalog>/<team_prefix>_<scale>_<condition>_raw/napa_files` | `/Volumes/<catalog>/<team_prefix>_250k_raw/napa_files` |
| Bronze schema | `<team_prefix>_<scale>_<condition>_bronze` | `<team_prefix>_250k_bronze` |
| Silver accepted schema | `<team_prefix>_<scale>_<condition>_silver` | `<team_prefix>_250k_silver` |
| Silver reject schema | `<team_prefix>_<scale>_<condition>_silver_reject` | `<team_prefix>_250k_silver_reject` |

Raw, Bronze, Silver, and Silver-reject namespaces are isolated by profile. The one shared operations schema follows `<team_prefix>_ops`; no separate operations-validation schema is used. `config/dataset_config.example.yml` supplies configurable placeholders for these destinations and a `gold_schema` for each profile.

Gold must remain separate from engineering evidence, but its physical organization is a team decision. Teams may use the configured Gold schema placeholders or document another assignment-consistent, team-owned organization; the supplied Bronze workflow and forthcoming Silver guidance do not prescribe Gold tables or models.

## 6. Application Structure and Deployment Approach

- Keep environment and profile values in configuration rather than source code.
- Reuse the same configured implementation across all profiles.
- Use the supplied Bronze notebook as documented and follow the revised Silver boundaries when published.
- Keep implementation, configuration templates, tests, and documentation in GitHub; keep source data, secrets, local authentication, and generated storage outside the repository.
- Use `databricks.yml` as the bundle root. It defines bundle `napa_olympic_analytics` and one default development target. The reusable target omits a workspace host so the explicitly selected local Databricks CLI profile supplies team-specific host and authentication; executable resources are added only when implementing the prescribed workflows.
- Team members authenticate individually through the Databricks CLI. The team designates a deployment coordinator to manually validate and deploy approved changes from its GitHub `main` branch.
- Do not assume GitHub Actions, production deployment targets, paid clusters, or embedded credentials.
- Target Databricks Free Edition serverless with the active Databricks SparkSession, explicit schemas, Delta-compatible operations, and documented APIs. Prefer supported SQL metadata inspection such as `SHOW CATALOGS`; do not rely on `spark.catalog.catalogExists()`, custom clusters, or test doubles that conceal unsupported runtime calls.

Deployment success confirms resource deployment, not data correctness. Runtime acceptance requires the applicable prompt's validation evidence.

## 7. Evidence, Reproducibility, and Validation

For each profile and layer, retain enough evidence to connect a reviewed code/configuration state to an actual execution. At minimum, record the selected profile, configuration or version reference, actual source and destination names, run identifier, execution status, structured manifest-validation results, table and row-count evidence, reconciliation results, quality findings, deviations, and disposition.

Keep local unit tests, Asset Bundle validation, and controlled live Databricks Free Edition execution as separate evidence. Never claim that a pipeline, dataset, or recommendation is validated unless the relevant check ran. Use `docs/lineage.md` for expected and verified source-to-output mappings and `docs/runbook.md` for actual setup, deployment, runs, failures, fixes, and reruns.

## 8. Team-Owned Gold Analytical Design

The consulting team owns the Gold architecture and analytical strategy, including:

- Gold organization and analytical outputs.
- Features, measures, comparisons, and partnership evaluation.
- Selection methods, statistical techniques, models, or scoring rules.
- Gold-specific validation, sensitivity, and uncertainty analysis.
- Evidence connecting analytical conclusions to USA and Canada men's, women's, and mixed doubles recommendations, alternates, and development-camp candidates.

Gold decisions must use traceable Silver inputs, preserve historical and quality context, and remain reproducible. This document does not prescribe Gold algorithms, tables, thresholds, or models.

## 9. Three-Milestone Project Progression

1. **Milestone 1 — Foundation and Initial Engineering:** Establish the environment and team workflow, validate access to all five Raw profiles, and implement Bronze for `napa_5k_clean` and `napa_5k_tainted`.
2. **Milestone 2 — Data Engineering and Quality:** Complete Bronze and Silver processing, mandatory quality validation, and reproducible evidence for all five profiles.
3. **Milestone 3 — Analytics and Recommendations:** Develop team-owned Gold analytics and Olympic recommendations, using `napa_250k_production` for final production recommendations and executive deliverables.

Milestones represent stages of platform and analytical maturity; no milestone corresponds exclusively to one dataset size.

## 10. Architecture Decisions and Rationale

### Established requirements

| Decision | Rationale or authority | Status |
|---|---|---|
| Use five isolated dataset profiles with the supplied Bronze utility | README and Bronze bootstrap guide | Established |
| Process and validate one Bronze profile at a time | Bronze bootstrap guide | Established |
| Preserve Raw records one-for-one in Bronze without enforcing logical-key uniqueness or business quality | Supplied Bronze utility | Established |
| Protect existing Bronze tables by default and require an explicit, targeted reload choice | Bronze bootstrap guide | Established |
| Keep enterprise operational infrastructure out of the student Bronze workflow | Simplified course design | Established |
| Require students to prepare Raw Volumes and configure team-owned Bronze schemas | Supplied Bronze utility | Established |
| Store Raw and managed layer outputs in configurable Unity Catalog namespaces | Dataset configuration and Bronze guide | Established |
| Treat the supplied Bronze guidance as active and the revised Silver guidance as forthcoming | `AGENTS.md` and README | Established |
| Run the supplied Bronze notebook directly in Databricks Free Edition | Bronze bootstrap guide | Established |
| Keep Gold analytical architecture team-owned and separate from engineering evidence | Assignment boundary and `AGENTS.md` | Established |

### Team decision record

Record only choices that remain open to the team. Add rows as decisions are made and link supporting evidence where useful.

| Decision | Rationale | Alternatives considered | Risks or tradeoffs | Owner | Status |
|---|---|---|---|---|---|
| Gold physical organization |  |  |  |  | Open |
| Gold feature and output organization |  |  |  |  | Open |
| Analytical validation approach |  |  |  |  | Open |
| Evidence and output retention approach |  |  |  |  | Open |
| Deployment coordinator |  |  |  |  | Open |

## 11. Related Documentation

| Document | Responsibility |
|---|---|
| `docs/lineage.md` | Expected and verified source-to-target lineage, actual deployed names, execution evidence, and Gold traceability |
| `docs/governance.md` | Stewardship, ownership, access, controls, approvals, and responsible AI decisions |
| `docs/runbook.md` | Authentication, setup, upload, deployment, execution, troubleshooting, and actual run evidence |
| `docs/dataset_specification.md` | Dataset profiles, source-package contents, record grains, relationships, and release conventions |
| `notebooks/00_bootstrap_bronze.py` | Supplied student Bronze utility |
| `docs/bronze_bootstrap_guide.md` | Bronze configuration, operation, validation, and reload safety |
| Revised Silver prompt | Forthcoming instructor-provided Silver construction guidance |
| Official RFP and Canvas assignments | Business requirements, eligibility, deliverables, and assessment authority |
