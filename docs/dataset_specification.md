# Dataset Specification

**Purpose:** This document is a technical reference for the NAPA dataset packages, including their profiles, source files, record grains, conceptual relationships, and release conventions. Teams must still validate each delivered package and its manifest before use.

## Documentation boundaries

- This specification describes package structure, record grains, conceptual relationships, and releases.
- `docs/data_dictionary.md` records field-level definitions, business semantics, and team interpretations.
- `notebooks/00_bootstrap_bronze.py` and `docs/bronze_bootstrap_guide.md` govern the active student Bronze workflow; revised Silver guidance is forthcoming.
- The official NAPA RFP and Canvas assignments govern business deliverables, eligibility, and submission requirements.

Do not treat this document as a substitute for the delivered Parquet schemas, `manifest.json`, supplied Bronze guidance, forthcoming revised Silver guidance, or official assignment materials.

## Dataset profiles

| Dataset profile | Role | Data condition | Intended use |
|---|---|---|---|
| `napa_5k_clean` | Development | Clean | Small package for initial workflow development and correctness checks |
| `napa_5k_tainted` | Development | Intentionally tainted | Small package for validating quality detection and rejection behavior |
| `napa_50k_clean` | Validation | Clean | Medium package for broader engineering validation |
| `napa_50k_tainted` | Validation | Intentionally tainted | Medium package for validating quality behavior at greater scale |
| `napa_250k_production` | Production-scale case data | Production with intentionally imperfect data | Final production-scale engineering and analytical evidence |

The 250K package is production data even though it contains quality issues. Its configured condition is `production`; there is no separate clean or tainted 250K profile.

## Expected source files

Each profile contains the same 13 source Parquet files plus a colocated `manifest.json`. The manifest is package evidence, not a fourteenth source table.

| Source file | Record grain | Key | Business purpose |
|---|---|---|---|
| `regions.parquet` | One record per geographic region | `id` | Geographic context for players, clubs, and matches |
| `clubs.parquet` | One record per club or facility | `id` | Club and facility context |
| `club_memberships.parquet` | One record per player-club membership period | `id` | Historical player affiliation with clubs |
| `player_master.parquet` | One current or snapshot record per player | `player_id` | Player identity, profile, status, rating, and snapshot context |
| `player_registrations.parquet` | One record per player registration event | `id` | Player registration and onboarding history |
| `player_assessment_history.parquet` | One record per player assessment | `id` | Longitudinal player assessment evidence |
| `teams.parquet` | One record per persistent doubles team or partnership | `id` | Team identity, country/category, and lifecycle context |
| `team_memberships.parquet` | One record per player-team membership period | `id` | Team composition and partnership continuity |
| `matches.parquet` | One record per match | `id` | Match context, result, location, and release reference |
| `match_teams.parquet` | One record per participating side in a match | `id` | Match-side participation linked to a persistent team |
| `match_team_players.parquet` | One record per player participating on a match side | `id` | Player participation and match-time evidence |
| `match_games.parquet` | One record per game within a match | `id` | Game sequence, scores, and result evidence |
| `monthly_batches.parquet` | One record per monthly batch or snapshot period | `id` | Batch, snapshot, reconciliation, and release-period context |

The supplied file names must remain unchanged. Field-level columns, types, nullability, and business definitions belong in the data dictionary and must be verified against the delivered files and manifest.

## Conceptual relationships

- A player may have registration events and assessment history associated with that player's master record.
- Regions provide geographic context for clubs, players, registrations, and matches where the relevant relationship is present.
- Club memberships connect players to clubs over membership periods; clubs connect to regions.
- Team memberships connect players to persistent doubles teams over membership periods.
- A match has participating side records in `match_teams.parquet`; each side references the persistent team represented in that match.
- `match_team_players.parquet` associates participating players with a match side.
- Individual games in `match_games.parquet` belong to their parent match.
- Monthly batch identifiers provide release or snapshot context for records that reference a batch.

These are conceptual paths, not a complete field-level relationship contract. Use the delivered schema, supplied Bronze guidance, and forthcoming revised Silver guidance for exact keys, nullability, and validation behavior.

## Release conventions

The five initial profiles are independent, full historical datasets processed as full refreshes. They are not sequential monthly increments and do not need to be combined to reconstruct a later profile. `monthly_batches.parquet` is a source table within each package; its presence does not make the initial profiles incremental releases.

Each profile has its own configured Raw Volume and layer schemas. The selected profile and isolated path identify the clean, tainted, or production package, while the colocated manifest supplies the authoritative file inventory, release metadata, and actual row counts.

If later production monthly releases are issued, follow their separate instructions. Do not infer a release schedule, append strategy, dates, or row counts from the initial five profiles.

## Milestone alignment

- **Milestone 1 — Foundation and Initial Engineering:** Validate Raw access for all five profiles and implement Bronze ingestion for `napa_5k_clean` and `napa_5k_tainted`.
- **Milestone 2 — Data Engineering and Quality:** Complete Bronze and Silver processing for all five profiles using the prescribed requirements.
- **Milestone 3 — Analytics and Recommendations:** Develop team-designed Gold analytics and Olympic recommendations, using `napa_250k_production` for final production recommendations.

Milestones represent stages of engineering and analytical development; no milestone corresponds exclusively to one dataset size.

## Storage and source preservation

- Store each package in its configured Databricks Unity Catalog Raw Volume as described in `data/README.md`.
- Keep the supplied Parquet files and colocated `manifest.json` unchanged.
- Do not commit source datasets, generated Delta storage, or extracts that reproduce source data to GitHub.
- Perform standardization, rejection, remediation, and feature engineering downstream without rewriting Raw files.
- Record the team's configured paths and execution evidence without committing credentials or private workspace details.

## Student validation responsibilities

> The delivered files and colocated manifest are the physical source of truth.

- Confirm the exact expected files and one readable `manifest.json` are present for the selected profile.
- Profile schemas rather than assuming consistency.
- Validate Bronze using the supplied notebook and guide; follow the forthcoming revised Silver guidance for downstream validation.
- Record the selected profile, run evidence, quality findings, and any deviations without inventing replacement data.
