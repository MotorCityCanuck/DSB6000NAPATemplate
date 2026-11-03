# NAPA Olympic Analytics Platform

Student team template | DSB6000 — Data Science Strategy & Leadership

## What your team is building

Your team is an analytics consulting firm responding to a fictional **North American Pickleball Association (NAPA) request for proposal (RFP)**. Build a working data platform, investigate player and doubles-partnership performance, and make defensible roster recommendations to the NAPA RFP evaluation committee.

The project emphasizes **AI-assisted software development, data-informed decision-making, teamwork, governance, and executive communication**. It does not require every student to become a specialist in Databricks or data engineering.

The division of responsibility is intentional:

1. **Raw → Bronze:** Use the supplied `docs/raw_to_bronze_prompt.md` with Codex to construct the prescribed ingestion pipeline.
2. **Bronze → Silver:** Once Bronze tables exist, review and use `docs/bronze_to_silver_prompt.md` to construct the shared, quality-controlled analytical foundation.
3. **Silver → Gold:** Your **team designs the analytical approach and its own Codex prompts** for features, comparisons, selection methods, and recommendations. Codex can help implement your decisions.

The two construction prompts are detailed contracts, not completed code. Review, test, and explain what your AI assistant produces. The team is free to propose justified changes, but must understand their impact.

## Team information — complete before starting

- **Consulting team name:** _Enter name_
- **Members and responsibilities:** _Enter names/roles_
- **GitHub repository:** _Enter URL_
- **Primary team contact:** _Enter name/email_
- **Databricks workspace/catalog:** _Enter workspace and catalog_
- **Team namespace prefix (`team_prefix`):** _Enter a unique, agreed prefix_

## Read these first

- [`AGENTS.md`](AGENTS.md): short instructions that help Codex work appropriately in this student repository.
- **NAPA RFP and course assignment:** scope, milestones, eligibility, and precise deliverables. These documents control business requirements.
- [`docs/raw_to_bronze_prompt.md`](docs/raw_to_bronze_prompt.md): detailed Bronze build and acceptance requirements.
- [`docs/bronze_to_silver_prompt.md`](docs/bronze_to_silver_prompt.md): detailed Silver build, data-quality, and acceptance requirements.
- [`docs/dataset_specification.md`](docs/dataset_specification.md) and [`docs/assignment_context.md`](docs/assignment_context.md): dataset and assignment reference material, if included in the template.

**Important:** Keep both construction prompts in `docs/` as shown below so students and Codex can find them consistently. No instructor reference implementation is needed or available for construction.

## The data flow

```text
13 delivered Parquet files + manifest.json  (one package per dataset profile)
                  |
                  v
    Databricks Unity Catalog Raw Volume
                  |
          Raw-to-Bronze pipeline   <-- supplied construction prompt
                  |
                  v
      Bronze Delta tables          (retain source business values)
                  |
        Bronze-to-Silver pipeline  <-- supplied construction prompt
                  |
                  v
      Silver Delta tables          (standardized, validated, complete attributes)
      + rejection/quality evidence
                  |
            Team-designed Gold     <-- team-written analytical prompts
                  |
                  v
       Player and partnership analysis -> rosters -> executive presentation
```

**One codebase, five configurations.** Do not construct five separate Bronze programs or five separate Silver programs. Each pipeline accepts the `dataset_profile` parameter and writes only to that profile's designated schemas.

## Project milestones

1. **Milestone 1 — Foundation and Initial Engineering:** Establish the development environment, team workflow, and dataset access. Load and validate all five Raw dataset profiles, then implement the Bronze layer for both 5K profiles.
2. **Milestone 2 — Data Engineering and Quality:** Complete Bronze and Silver processing for all five profiles. Apply the prescribed data-quality and transformation requirements.
3. **Milestone 3 — Analytics and Recommendations:** Develop the Gold layer and analytics using the available datasets. Use the 250K production dataset to support final Olympic roster recommendations, development-camp recommendations, and executive deliverables.

## Dataset profiles and recommended test order

| Order | `dataset_profile` | Purpose | Input condition |
|---:|---|---|---|
| 1 | `napa_5k_clean` | Learn the workflow and validate basic correctness | Clean |
| 2 | `napa_5k_tainted` | Check data-quality detection and rejection | Low-level injected defects |
| 3 | `napa_50k_clean` | Validate on more substantial data | Clean |
| 4 | `napa_50k_tainted` | Test quality handling at larger scale | Low-level injected defects |
| 5 | `napa_250k_production` | Production-scale analysis and final recommendations | Tainted production case data |

The 5K and 50K datasets each have separate **clean** and **tainted** profiles. The 250K production dataset is **tainted** and has no separate clean profile.

Each profile is an **independent full historical dataset**, not the next monthly increment of the previous profile. Its player-scale label is approximate; the accompanying manifest is the authority for actual file counts. Complete **Bronze, then Silver, then acceptance checks** for one profile before advancing to the next. Your team's final Gold conclusions should use the 250K production Silver dataset.

## Set up Raw data in Databricks — required before ingestion

The Raw-to-Bronze pipeline reads from **Unity Catalog Volumes in Databricks**, not a local `data/raw/` directory. Your team must arrange for each supplied dataset package to be uploaded to its **own Raw Volume**. The pipeline may provision or validate schemas/Volumes, but it **does not upload the files**.

The prompt's defaults are catalog `workspace`, team prefix `napa_platform`, and Volume name `napa_files`. Resolve your team's actual catalog and unique `team_prefix` before writing data. These example paths are **defaults, not mandatory shared team destinations**:

| Dataset profile | Default Raw Volume directory containing the files |
|---|---|
| `napa_5k_clean` | `/Volumes/workspace/napa_platform_5k_clean_raw/napa_files/` |
| `napa_5k_tainted` | `/Volumes/workspace/napa_platform_5k_tainted_raw/napa_files/` |
| `napa_50k_clean` | `/Volumes/workspace/napa_platform_50k_clean_raw/napa_files/` |
| `napa_50k_tainted` | `/Volumes/workspace/napa_platform_50k_tainted_raw/napa_files/` |
| `napa_250k_production` | `/Volumes/workspace/napa_platform_250k_raw/napa_files/` |

**Inside each Volume, place the following 14 files directly at its root:**

```text
/Volumes/<catalog>/<team_prefix>_5k_clean_raw/napa_files/
  manifest.json
  regions.parquet
  clubs.parquet
  club_memberships.parquet
  player_master.parquet
  player_registrations.parquet
  player_assessment_history.parquet
  teams.parquet
  team_memberships.parquet
  matches.parquet
  match_teams.parquet
  match_team_players.parquet
  match_games.parquet
  monthly_batches.parquet
```

Repeat this exact **flat file layout** for each of the other four profile Volumes, substituting that profile's Raw schema. **Do not** add a `raw/`, `data/`, `clean/`, `tainted/`, `release/`, or month-named subdirectory inside `napa_files`. Do not mix files from different datasets. The manifest must be from the **same package** as its 13 Parquet files; it is validation evidence, not a fourteenth Bronze table.

For example, if you are authorized to create the initial namespace yourself, the Databricks SQL pattern for the 5K clean profile is:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.napa_platform_5k_clean_raw;
CREATE VOLUME IF NOT EXISTS workspace.napa_platform_5k_clean_raw.napa_files;
```

Adjust the catalog and team prefix first. Repeat for the other four Raw schemas as needed. Alternatively, use the Databricks Catalog user interface. Ensure your team has permission to upload/read the files. An empty Volume is **not ready** for ingestion.

Before the first Bronze run, check that each intended Volume contains exactly the **13 named Parquet files and `manifest.json`**, all at the same level. Keep file names unchanged. Bronze checks inventory, manifest metadata, row counts, schemas, and file checksums; a missing or mixed package should fail validation.

You may keep a local copy for personal staging, but **never commit any source datasets, generated Delta data, or private storage paths to GitHub**.

## Expected Databricks objects

For a selected profile, the pipelines create or use the following separate schemas (all names are beneath your configured catalog):

| Layer | 5K/50K schema pattern | 250K production schema pattern |
|---|---|---|
| Raw | `<team_prefix>_<scale>_<clean_or_tainted>_raw` | `<team_prefix>_250k_raw` |
| Bronze | `<team_prefix>_<scale>_<clean_or_tainted>_bronze` | `<team_prefix>_250k_bronze` |
| Silver accepted | `<team_prefix>_<scale>_<clean_or_tainted>_silver` | `<team_prefix>_250k_silver` |
| Silver rejected | `<team_prefix>_<scale>_<clean_or_tainted>_silver_reject` | `<team_prefix>_250k_silver_reject` |
| Shared run/quality operations | `<team_prefix>_ops` | `<team_prefix>_ops` |

Gold is **team-designed** and should use a distinct schema. The Silver layer retains source attributes so teams can select their Gold features without rebuilding Silver simply to recover omitted columns.

## Beginner-friendly build sequence

1. **Prepare.** Confirm team roles, GitHub access, Databricks authentication/permissions, selected profile, source uploads, and the team's catalog/prefix.
2. **Build Bronze with Codex.** Have Codex read `AGENTS.md` and `docs/raw_to_bronze_prompt.md`. Ask it to inspect the repository, present a plan, and implement the pipeline and tests.
3. **Review in GitHub.** Inspect the changed files, test results, and pull request with teammates. Merge reviewed work using the team's branch/PR workflow.
4. **Deploy and run Bronze.** Validate/deploy the Databricks Asset Bundle manually; run the selected profile and inspect the job status, 13 Bronze tables, manifest reconciliation, and operations evidence. Fix problems and repeat the review/run cycle.
5. **Build Silver only after Bronze is ready.** Have Codex read `docs/bronze_to_silver_prompt.md`, implement the transformations/quality logic, and repeat GitHub review, manual deployment, execution, and acceptance checks.
6. **Repeat for all five profiles** in the order above, changing **only configuration/parameters**, except where verified defects require a code correction.
7. **Design Gold as a team.** Decide the business questions, scoring and selection methods, eligibility approach, partnership evaluation, and uncertainty handling; write your own Codex prompts to build and test those analytical products.
8. **Prepare the RFP response.** Use your Gold evidence to recommend teams and explain your reasoning to the NAPA evaluation committee.

Typical commands after your bundle is configured, reviewed, and deployed (the job names come from the supplied prompts):

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_5k_clean
databricks bundle run -t dev napa_bronze_to_silver --params dataset_profile=napa_5k_clean
```

**Do not run Silver until the selected profile's Bronze tables exist and have passed validation.** Use manual deployment; GitHub Actions are not assumed available. A successful deployment is not the same as a successful data-quality test.

## What successful data handling looks like

- **Bronze** reproduces the delivered source business rows/columns and adds ingestion metadata; it does not silently repair or deduplicate source data. A run refreshes only its selected Bronze schema. The supplied Bronze prompt requires cleanup of that schema after a failed run; Raw and operations evidence remain.
- **Silver** applies the prescribed standardization and rules, retains business attributes, and records rejected records and quality findings. Expected business-quality defects **do not themselves crash the entire pipeline**; records are rejected rather than fabricated or repaired. Duplicate-key groups are rejected in full, with dependent rejects handled according to the prompt. On technical failure, available Silver output and diagnostics remain for investigation; **the next run clears designated targets only after successful preflight**, then rebuilds them.
- **Time-aware analysis** preserves the manifest-derived dataset snapshot boundary and actual match/event dates. Do not use a player's end-of-year age as though it were their age at every historical match.
- **Gold** records team-defined feature logic and traceable inputs without rewriting historical Bronze/Silver evidence to favor a model.

## Your Gold analytics and NAPA RFP deliverables

Your team chooses how to compare individual players, evaluate doubles partnerships, handle eligibility and uncertainty, and develop its recommendations. At minimum, support the RFP's USA and Canada **men's, women's, and mixed doubles** selections, specified alternates, and **development camp** proposal. The final executive presentation should explain why the recommended rosters make sense, the evidence and limitations, and the team's approach to governance and AI-assisted development.

The **NAPA RFP and assignment** determine exact roster counts, eligibility rules, and submission details. Do not invent requirements. Preserve meaningful evidence in the GitHub repository, and make business conclusions explainable to a nontechnical committee.

## Repository structure — intended layout

This template starts with scaffolding; **Codex creates the working pipeline modules and job definitions**. The tree below combines starter locations and expected additions. Not every listed file/folder must exist before the build.

```text
AGENTS.md                      Codex team working instructions
README.md                      This student starting guide
LICENSE.md                     Template usage terms, if provided
databricks.yml                 Asset Bundle root (created/updated during build)
config/
  dataset_config.example.yml   Starter dataset/configuration examples, if present
  project_config.example.yml
  raw_to_bronze/               Five profile files, source registry, Bronze workflow
  bronze_to_silver/            Five profile files, rules, Silver workflow
notebooks/                     Thin Databricks job entry points
src/                           Team-built Python transformations and helpers
sql/                           Optional analytical SQL and planning
tests/                         Unit and integration tests
docs/                          Specifications and project documentation
  raw_to_bronze_prompt.md      Supplied Bronze construction contract
  bronze_to_silver_prompt.md   Supplied Silver construction contract
  architecture.md              Architecture decisions and diagrams
  analytical_methodology.md    Team-designed Gold analytics
  runbook.md                   Setup, execution, and validation evidence
outputs/                       Summaries and small evidence files (not raw data)
deliverables/                  Milestone and final presentation artifacts
data/                          Local guidance/staging only; do not commit NAPA data
```

The full pipeline-specific configuration layouts are prescribed in their respective Markdown prompts. Prefer their conventions over inventing an alternative folder framework.

## Team collaboration and evidence

- Keep **GitHub as the shared source of truth**. Use feature branches, pull requests, reviews, and deliberate merges; avoid having all members edit one shared main branch.
- Use Databricks Free Edition-compatible, team-owned configurations and **manual** Asset Bundle deployment. Do not assume GitHub Actions, paid clusters, or an existing instructor pipeline.
- Have team members who are less technical participate in requirements interpretation, validation, governance, analytical decisions, documentation, and executive storytelling—not just observe coding.
- Record release/profile, job run ID, counts, reject findings, assumptions, fixes, and tests in [`docs/runbook.md`](docs/runbook.md) and appropriate project evidence.
- Document material AI assistance and team review in [`docs/ai_usage_summary.md`](docs/ai_usage_summary.md).
- Keep tokens, credentials, `.env` files, data extracts, Databricks-managed storage, and private configuration out of public commits. Review your `.gitignore`.

## Documentation starting points

Use the documentation templates that are actually present in the repository:

| File | What to record |
|---|---|
| `docs/architecture.md` | Pipeline architecture and selected namespaces |
| `docs/dataset_specification.md`, `docs/data_dictionary.md` | Source/field understanding |
| `docs/data_quality_rules.md`, `docs/data_quality_report.md` | Rules, findings, rejects, and implications |
| `docs/lineage.md`, `docs/governance.md` | Provenance, stewardship, and control decisions |
| `docs/analytical_methodology.md` | Team-defined Gold features, evidence, validation, and selection methods |
| `docs/ai_usage_summary.md` | AI contributions, human review, and lessons |
| `docs/runbook.md` | Actual setup, parameters, runs, issues, fixes |

## Template use and publication

This repository is provided for DSB6000 course use. The assignment calls for a **public team GitHub project repository**; before publication, review `LICENSE.md` and course instructions to confirm allowed reuse of template material. Never publish supplied source datasets, credentials, confidential information, or private workspace exports. Additional redistribution or commercial use is governed by the license and course terms.

**The goal is not a perfect production system.** It is a working, validated platform that enables your team to exercise judgment, build its own Gold analytics, and present a credible recommendation to NAPA.
