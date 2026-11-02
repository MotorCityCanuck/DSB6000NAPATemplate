# Raw Data and Unity Catalog Volume Guide

**Purpose:** This guide explains how to place the five supplied NAPA dataset packages in Databricks Unity Catalog Volumes so the Raw-to-Bronze pipeline can locate and validate them. The delivered files and their colocated `manifest.json` are the source of truth.

## Dataset profiles

Each profile is an independent, full-refresh dataset package.

| Dataset profile | Purpose |
|---|---|
| `napa_5k_clean` | Small, clean development dataset |
| `napa_5k_tainted` | Small development dataset containing intentional quality issues |
| `napa_50k_clean` | Medium-sized clean validation dataset |
| `napa_50k_tainted` | Medium-sized dataset containing intentional quality issues |
| `napa_250k_production` | Full-scale production dataset containing intentionally imperfect data |

The 250K profile is production-scale case data even though it contains quality issues. Its configured data condition is `production`; there is no separate clean or tainted 250K selector.

## Expected Unity Catalog Volume locations

The Bronze construction prompt uses one Raw schema per dataset profile and a Volume named `napa_files` inside each schema. A Unity Catalog Volume path has this form:

```text
/Volumes/<catalog>/<raw_schema>/napa_files
```

The prompt uses `workspace` as the example catalog and `napa_platform` as the example team prefix. Replace those examples with the catalog and unique prefix assigned to your consulting team.

| Dataset profile | Raw schema pattern | Complete Raw Volume path |
|---|---|---|
| `napa_5k_clean` | `<team_prefix>_5k_clean_raw` | `/Volumes/<catalog>/<team_prefix>_5k_clean_raw/napa_files` |
| `napa_5k_tainted` | `<team_prefix>_5k_tainted_raw` | `/Volumes/<catalog>/<team_prefix>_5k_tainted_raw/napa_files` |
| `napa_50k_clean` | `<team_prefix>_50k_clean_raw` | `/Volumes/<catalog>/<team_prefix>_50k_clean_raw/napa_files` |
| `napa_50k_tainted` | `<team_prefix>_50k_tainted_raw` | `/Volumes/<catalog>/<team_prefix>_50k_tainted_raw/napa_files` |
| `napa_250k_production` | `<team_prefix>_250k_raw` | `/Volumes/<catalog>/<team_prefix>_250k_raw/napa_files` |

Place the 13 Parquet files and `manifest.json` directly at the root of each `napa_files` Volume. Do not add profile, release, month, `raw`, `data`, `clean`, or `tainted` subdirectories inside the Volume. Do not mix files from different dataset packages.

For example, the 5K clean package must have this flat layout:

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

Use the same flat file layout in the other four profile Volumes. The `manifest.json` for a profile must come from the same delivered package as its Parquet files and must be in the same directory. It is validation evidence, not a fourteenth Bronze source table.

## Expected source files

Every profile must contain these 13 supplied Parquet files:

1. `regions.parquet`
2. `clubs.parquet`
3. `club_memberships.parquet`
4. `player_master.parquet`
5. `player_registrations.parquet`
6. `player_assessment_history.parquet`
7. `teams.parquet`
8. `team_memberships.parquet`
9. `matches.parquet`
10. `match_teams.parquet`
11. `match_team_players.parquet`
12. `match_games.parquet`
13. `monthly_batches.parquet`

Preserve the supplied filenames and flat directory structure unless the instructor issues replacement instructions. Bronze validates the inventory, manifest entries, row counts, ordered columns, schemas, and file checksums before publication.

## Configure your team's locations

1. Identify the Unity Catalog catalog assigned to your team and agree on a unique `team_prefix`.
2. Identify or, if authorized, create the profile-specific Raw schemas and the `napa_files` Volume in each schema. The Bronze workflow may provision or validate these objects, but it does not upload source files or grant permissions.
3. Upload each delivered package to its matching Volume using the flat layout above.
4. Copy `config/dataset_config.example.yml` to the team's approved local configuration and set each profile's `raw_volume_path` to the corresponding full `/Volumes/<catalog>/<raw_schema>/napa_files` path.
5. Before running Bronze, verify that the selected path contains exactly the expected 13 Parquet files and one readable, matching `manifest.json`.

Catalog and schema identifiers may differ between consulting teams. The five agreed dataset profile names, fixed `napa_files` Volume name, source filenames, and flat internal layout must remain consistent with the Bronze construction prompt. Record the team's resolved catalog, schemas, and Volume paths in `docs/runbook.md` without recording credentials.

## Source-data handling requirements

- Source datasets are supplied in Parquet format and must not be committed to GitHub.
- Keep the original Parquet files and `manifest.json` unchanged in the configured Raw Volumes.
- Bronze ingestion reads the selected profile only from its configured Raw Volume path.
- Perform cleansing, rejection, remediation, and feature engineering downstream; never rewrite the delivered Raw files to correct data-quality issues.
- Do not commit generated Delta data, large exports, credentials, private workspace paths, or temporary extracts that reproduce source data.
- Local copies may be used for temporary staging when permitted, but no local directory is part of the required Bronze ingestion contract.
