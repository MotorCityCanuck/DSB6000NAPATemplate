# Architecture

## 1. Purpose and Document Boundaries

This student-maintained document describes the high-level architecture of the NAPA Olympic Analytics Platform: its processing layers, technology responsibilities, configurable namespaces, deployment approach, and team decisions. It consolidates the useful layer-design guidance previously separated from the main architecture record.

This document does not replace the detailed Raw-to-Bronze or Bronze-to-Silver construction prompts. Those prompts are authoritative for their respective engineering behavior, quality controls, outputs, failure handling, and acceptance criteria. The official RFP and Canvas assignments remain authoritative for business deliverables and eligibility requirements.

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
| Notebooks or scripts | Thin orchestration and review surfaces; detailed Bronze and Silver structure follows the construction prompts |
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

Profile selection occurs through configuration and the `dataset_profile` parameter, not through separate pipeline forks. Bronze and Silver use full-refresh execution for the selected profile. Build and validate Bronze before Silver for each profile; use production Silver evidence from `napa_250k_production` for final recommendations.

## 4. Raw, Bronze, Silver, and Gold Layer Responsibilities

| Layer | Purpose and expected content | Quality and preservation boundary | Ownership |
|---|---|---|---|
| Raw | The 13 supplied Parquet files and colocated `manifest.json` in the selected Unity Catalog Volume | Preserve the delivered package unchanged; validate its inventory and manifest as required by the Bronze prompt | Prescribed engineering foundation |
| Bronze | Raw-preserving managed Delta representation with prescribed ingestion metadata and operational evidence | Certify source readiness, preserve all source business rows and values including defects and duplicates, reconcile publication, and perform no business cleansing or feature engineering | Prescribed by `docs/raw_to_bronze_prompt.md` |
| Silver | Standardized accepted entities, corresponding exception outputs, convenience views, reconciliation, quality results, and operational evidence | Apply the prompt's mandatory validation and standardization; preserve accepted attributes and diagnostic evidence; do not fabricate corrections | Prescribed by `docs/bronze_to_silver_prompt.md` |
| Gold | Decision-ready features, measures, comparisons, analytical products, and recommendation evidence | Team defines analytical quality controls and documents assumptions, limitations, uncertainty, and lineage without rewriting upstream evidence | Team-defined |

The construction prompts contain the detailed table mappings, rules, execution behavior, and acceptance tests. This architecture records only the layer boundaries.

## 5. Unity Catalog Namespace and Storage Architecture

Catalog and team prefix values are configurable. The patterns below are the construction-prompt conventions; actual values must be team-owned and recorded without embedding credentials or personal paths.

| Object | 5K and 50K profiles | 250K production profile |
|---|---|---|
| Raw schema | `<team_prefix>_<scale>_<condition>_raw` | `<team_prefix>_250k_raw` |
| Raw Volume path | `/Volumes/<catalog>/<team_prefix>_<scale>_<condition>_raw/napa_files` | `/Volumes/<catalog>/<team_prefix>_250k_raw/napa_files` |
| Bronze schema | `<team_prefix>_<scale>_<condition>_bronze` | `<team_prefix>_250k_bronze` |
| Silver accepted schema | `<team_prefix>_<scale>_<condition>_silver` | `<team_prefix>_250k_silver` |
| Silver reject schema | `<team_prefix>_<scale>_<condition>_silver_reject` | `<team_prefix>_250k_silver_reject` |

Raw, Bronze, Silver, and Silver-reject namespaces are isolated by profile. The shared operations schema follows `<team_prefix>_ops`. `config/dataset_config.example.yml` supplies configurable placeholders for these destinations and a `gold_schema` for each profile.

Gold must remain separate from engineering evidence, but its physical organization is a team decision. Teams may use the configured Gold schema placeholders or document another assignment-consistent, team-owned organization; the construction prompts do not prescribe Gold tables or models.

## 6. Application Structure and Deployment Approach

- Keep environment and profile values in configuration rather than source code.
- Reuse the same configured implementation across all profiles.
- Follow the construction prompts' boundaries for reusable modules, thin orchestration entrypoints, SQL, tests, and workflow definitions.
- Keep implementation, configuration templates, tests, and documentation in GitHub; keep source data, secrets, local authentication, and generated storage outside the repository.
- Use `databricks.yml` as the bundle root. It currently defines bundle `napa_olympic_analytics`, one default development target, and a team workspace URL placeholder; executable resources are added only when implementing the prescribed workflows.
- Team members authenticate individually through the Databricks CLI. The team designates a deployment coordinator to manually validate and deploy approved changes from its GitHub `main` branch.
- Do not assume GitHub Actions, production deployment targets, paid clusters, or embedded credentials.

Deployment success confirms resource deployment, not data correctness. Runtime acceptance requires the applicable prompt's validation evidence.

## 7. Evidence, Reproducibility, and Validation

For each profile and layer, retain enough evidence to connect a reviewed code/configuration state to an actual execution. At minimum, record the selected profile, configuration or version reference, actual source and destination names, run identifier, execution status, table and row-count evidence, reconciliation results, quality findings, deviations, and disposition.

Tests and local configuration checks must be distinguished from Databricks execution. Never claim that a pipeline, dataset, or recommendation is validated unless the relevant check ran. Use `docs/lineage.md` for expected and verified source-to-output mappings and `docs/runbook.md` for actual setup, deployment, runs, failures, fixes, and reruns.

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
| Use five isolated dataset profiles with parameterized Bronze and Silver processing | README and construction prompts | Established |
| Use full-refresh Bronze and Silver execution | Construction prompts | Established |
| Store Raw and managed layer outputs in configurable Unity Catalog namespaces | Construction prompts and dataset configuration | Established |
| Treat Bronze and Silver prompts as authoritative engineering contracts | `AGENTS.md` and construction prompts | Established |
| Deploy manually through a development Asset Bundle target | Repository workflow and `databricks.yml` | Established |
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
| `docs/raw_to_bronze_prompt.md` | Authoritative Bronze construction and acceptance contract |
| `docs/bronze_to_silver_prompt.md` | Authoritative Silver construction, quality, and acceptance contract |
| Official RFP and Canvas assignments | Business requirements, eligibility, deliverables, and assessment authority |
