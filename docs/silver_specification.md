# NAPA Simplified Silver Specification

## 1. Purpose and authority

This document is the authoritative student-facing contract for the supplied NAPA Silver bootstrap in `notebooks/01_build_silver.py`. It defines the mandatory baseline data model, transformations, record-level data-quality rules, rejection evidence, summary evidence, and acceptance checks for all five dataset profiles.

The implementation must not add a record-level rejection criterion that is absent from the approved rule catalog in Section 8. A proposed rule must first be documented, reviewed, and added to this specification. Technical failures listed in Section 13 fail notebook execution; they do not create additional business-record rejections.

Authority for this simplified workflow is, in descending order:

1. This specification and `notebooks/01_build_silver.py`.
2. The active Bronze interface in `notebooks/00_bootstrap_bronze.py` and its guide.
3. The source inventory and field definitions in `docs/dataset_specification.md` and the Source Field Dictionary in `docs/data_dictionary.md`.
4. The delivered Parquet files and colocated `manifest.json` as physical evidence.

Historical Silver construction prompts and their enterprise architecture are not active Assignment 10 instructions. Their projections, operations framework, views, and additional rules are not part of this baseline unless a rule is explicitly included here.

## 2. Scope and profile contract

One parameterized notebook processes exactly one selected profile per execution:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

The notebook reads the selected profile's 13 managed Bronze Delta tables and writes one profile-specific Silver schema containing exactly these expected outputs:

- 13 accepted tables with the same names as their Bronze sources;
- 13 rejection tables named `<source_table>_rejects`; and
- `silver_data_quality_summary`.

The same code and contracts apply to every profile. Profiles are independent full datasets, not incremental releases. Silver must not read another profile's Bronze schema or modify another profile's Silver schema.

Gold features, eligibility decisions, rankings, partnership scores, roster recommendations, fatigue measures, rating adjustments, and other analytical judgments are outside this specification.

## 3. Common field and type conventions

### 3.1 Preservation

Every accepted table retains every valid source business attribute under its original source name. Silver may safely convert or standardize the value as documented below, but it must not drop, combine, rename, impute, or infer a source attribute. Rejection tables retain the original Bronze business values before Silver conversion or standardization.

Bronze operational metadata is not required in accepted tables. It is required in every rejection table under Section 10.

### 3.2 Type notation

The repository does not contain delivered Parquet files or a manifest from which every physical precision can be verified. This specification therefore uses the following implementable type contract:

| Specification type | Silver behavior |
|---|---|
| `BIGINT` | Spark `BIGINT`; used for source IDs, integer counts, sequences, side numbers, and scores |
| `STRING` | Spark `STRING`; trim leading/trailing whitespace; preserve case unless a field-specific rule says to uppercase or map aliases |
| `BOOLEAN` | Spark `BOOLEAN` |
| `DATE` | Spark `DATE`, produced with a non-throwing conversion under Section 3.4 |
| `SOURCE_DECIMAL(s=n)` | Preserve the Bronze `DecimalType(p,n)` precision `p` and scale `n`; do not convert to `DOUBLE` or reduce precision |
| `SOURCE_TYPE` | Preserve the validated Bronze physical type because the source dictionary does not prescribe another type |
| `POSITION_SOURCE` | Bronze may publish `player_position` as `BIGINT` or `STRING`. Normalize populated `1`/`"1"` to accepted `LEFT` and `2`/`"2"` to accepted `RIGHT`; accepted Silver type is `STRING`, while a rejection row preserves the original Bronze type and value. |
| `GLOBAL_PERCENTILE_SOURCE` | Bronze may provide either a null-only `STRING`, which accepted Silver preserves as nullable `STRING`, or a validated `DecimalType(p,2)`, which accepted Silver preserves as `SOURCE_DECIMAL(s=2)`. This exception applies to any dataset profile. A populated `STRING` is a technical review stop. |
| `INT` | Spark `INT`; used only for the two derived ages |

If the corresponding Bronze field does not have the prescribed type family, or decimal scale differs from the documented scale, that is a source-contract technical failure. It is not a row rejection. Exact decimal precision may differ by delivered schema and is preserved. `POSITION_SOURCE` is the approved exception to a string-only physical-source assumption; it does not broaden either position domain or add a rejection rule. `GLOBAL_PERCENTILE_SOURCE` permits the two representations above for every profile. It does not authorize parsing populated strings, manufacturing decimal values or precision, or rejecting an occurrence because this optional field is null.

Logical nullability in this document controls accepted records. Delta may report a physically nullable column even when accepted rows are validated as non-null.

**Read-only implementation preflight:** Before building type-dependent Silver transformations or performing any Silver writes, inspect the actual selected-profile Bronze Delta schemas and the colocated manifest in Databricks. Compare the physical column names, type families, decimal precision and scale, and available snapshot fields with Sections 3–8. Confirm the two `SOURCE_TYPE` fields (`match_teams.team_score` and `player_assessment_history.derived_from_matches`), the `GLOBAL_PERCENTILE_SOURCE` contract, and the manifest's actual `snapshot_end_exclusive` representation. Record the evidence and report any mismatch for instructor review; do not guess types, coerce an incompatible schema silently, or convert an unverified assumption into a record-level rejection. Check other profiles' physical compatibility as they are tested. This preflight is read-only and is not authorization to create or replace Silver tables.

### 3.3 String standardization

- Trim leading and trailing whitespace from `STRING` business fields.
- A required string that is null or empty after trimming fails `SILVER-REQ-001`.
- Preserve `US` and `CA` country codes. Uppercase populated `country_code` values, but do not map them to `USA` or `CAN` and do not reject another populated code without an approved domain rule.
- Uppercase populated categorical fields only where the table contract explicitly says `uppercase`.
- Apply only the explicit alias mappings in Section 8. No row-level fallback from one business column to another is permitted.

### 3.4 Date and month standardization

Use Spark-native, non-throwing parsing.

- A date field accepts an existing Spark `DATE` or an ISO string in `yyyy-MM-dd` form.
- A month field accepts an existing Spark `DATE`, an ISO `yyyy-MM-dd` string, or a `yyyy-MM` string. A `yyyy-MM` value becomes the first calendar day of that month.
- A populated value that cannot be parsed under these forms fails `SILVER-DATE-001`.
- A null required date/month fails `SILVER-REQ-001`; a null optional date/month remains null.
- Do not replace malformed dates with the snapshot date, another event date, ingestion time, or the current date.

### 3.5 Duplicate identity

Logical primary keys are evaluated after required type normalization and string trimming. Every occurrence in a duplicated non-null logical-primary-key group fails `SILVER-PK-002`. Do not select a winner with `DISTINCT`, `dropDuplicates`, row order, completeness, timestamps, or ranking. Null keys fail `SILVER-PK-001` and are not included in duplicate grouping.

## 4. Accepted-table registry and dependency order

| Order | Accepted table | Business grain | Logical primary key | Mandatory accepted parents | Optional accepted parents |
|---:|---|---|---|---|---|
| 10 | `monthly_batches` | One monthly batch or snapshot period | `id` | None | None |
| 20 | `regions` | One geographic region | `id` | None | None |
| 30 | `player_master` | One current/snapshot player record | `player_id` | None | `home_region_id → regions.id` |
| 40 | `teams` | One persistent doubles team | `id` | None | None |
| 50 | `clubs` | One club or facility | `id` | `region_id → regions.id` | None |
| 60 | `player_registrations` | One player registration event | `id` | `player_id → player_master.player_id`; `batch_id → monthly_batches.id` | `assigned_region_id → regions.id` |
| 70 | `player_assessment_history` | One player assessment | `id` | `player_id → player_master.player_id`; `batch_id → monthly_batches.id` | None |
| 80 | `club_memberships` | One player-club membership period | `id` | `player_id → player_master.player_id`; `club_id → clubs.id` | None |
| 90 | `team_memberships` | One player-team membership period | `id` | `team_id → teams.id`; `player_id → player_master.player_id` | None |
| 100 | `matches` | One match | `id` | `batch_id → monthly_batches.id` | `region_id → regions.id`; `winning_team_id → teams.id` |
| 110 | `match_teams` | One participating side in a match | `id` | `match_id → matches.id`; `team_id → teams.id` | None |
| 120 | `match_team_players` | One player participating on one match side | `id` | `match_team_id → match_teams.id`; `player_id → player_master.player_id` | None |
| 130 | `match_games` | One game in a match | `id` | `match_id → matches.id` | None |

The order exists to make cascading rejection understandable. Implementations may prepare reusable DataFrames in another order, but parent acceptance must be known before a dependent row is classified.

## 5. Accepted-table field contracts

In the tables below, `R` means logically required in accepted Silver and `O` means nullable. `Direct` means the source field is preserved under the same name. Dates and months use Section 3.4. No fields other than the two explicitly identified ages may be added to the mandatory baseline.

### 5.1 `regions`

Purpose: geographic context. Grain and key are defined in Section 4.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `country_code` | `STRING` | R | Direct; trim and uppercase; preserve `US`/`CA` |
| `region_type` | `STRING` | O | Direct; trim and uppercase |
| `region_name` | `STRING` | R | Direct; trim; preserve case |
| `state_province_code` | `STRING` | O | Direct; trim and uppercase |
| `population` | `BIGINT` | O | Direct |
| `latitude` | `SOURCE_DECIMAL(s=6)` | O | Direct |
| `longitude` | `SOURCE_DECIMAL(s=6)` | O | Direct |

### 5.2 `clubs`

Purpose: club and facility context.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `club_name` | `STRING` | R | Direct; trim; preserve case |
| `region_id` | `BIGINT` | R | Direct; mandatory FK |
| `club_type` | `STRING` | O | Direct; trim and uppercase |
| `competitiveness_level` | `STRING` | O | Direct; trim and uppercase |
| `member_capacity` | `BIGINT` | O | Direct |
| `founding_date` | `DATE` | O | Direct; safe date conversion |
| `indoor_court_count` | `BIGINT` | O | Direct |
| `outdoor_court_count` | `BIGINT` | O | Direct |

### 5.3 `club_memberships`

Purpose: historical player-club affiliation.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `player_id` | `BIGINT` | R | Direct; mandatory FK |
| `club_id` | `BIGINT` | R | Direct; mandatory FK |
| `membership_type` | `STRING` | O | Direct; trim and uppercase |
| `joined_date` | `DATE` | R | Direct; safe date conversion |
| `left_date` | `DATE` | O | Direct; safe date conversion |
| `is_primary` | `BOOLEAN` | O | Direct |

### 5.4 `player_master`

Purpose: player identity and snapshot attributes.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `player_id` | `BIGINT` | R | Direct |
| `external_player_key` | `STRING` | R | Direct; trim; no UUID-version rejection is approved |
| `first_name` | `STRING` | R | Direct; trim; preserve case |
| `last_name` | `STRING` | R | Direct; trim; preserve case |
| `gender` | `STRING` | O | Direct; trim and uppercase; no approved domain rejection |
| `birth_date` | `DATE` | R | Direct; safe date conversion |
| `dominant_hand` | `STRING` | O | Direct; trim and uppercase; no approved domain rejection |
| `home_region_id` | `BIGINT` | O | Direct; optional FK |
| `country_code` | `STRING` | O | Direct; trim and uppercase; preserve `US`/`CA` |
| `registration_date` | `DATE` | R | Direct; safe date conversion |
| `player_status` | `STRING` | R | Direct; trim and uppercase; no approved domain rejection |
| `rating` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `rating_value` | `SOURCE_DECIMAL(s=3)` | O | Direct; do not merge with `rating` |
| `confidence_score` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `volatility_score` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `global_percentile` | `GLOBAL_PERCENTILE_SOURCE` | O | Direct; any profile preserves a null-only physical `STRING` as nullable `STRING`, or preserves validated source decimal precision and scale 2; optional null never causes rejection |
| `match_count_used` | `BIGINT` | O | Direct |
| `rating_date` | `DATE` | O | Direct; safe date conversion |
| `rating_batch_id` | `BIGINT` | O | Direct; no FK is approved |
| `snapshot_month` | `DATE` | R | Direct; safe month conversion |
| `derived_age_at_snapshot` | `INT` | R | Derived under Section 7 |

### 5.5 `player_registrations`

Purpose: registration and onboarding history.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `player_id` | `BIGINT` | R | Direct; mandatory FK |
| `batch_id` | `BIGINT` | R | Direct; mandatory FK |
| `registration_month` | `DATE` | R | Direct; safe month conversion |
| `registration_source` | `STRING` | O | Direct; trim and uppercase |
| `assigned_region_id` | `BIGINT` | O | Direct; optional FK |
| `initial_rating_value` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `initial_confidence_score` | `SOURCE_DECIMAL(s=3)` | O | Direct |

### 5.6 `player_assessment_history`

Purpose: historical assessment evidence.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `player_id` | `BIGINT` | R | Direct; mandatory FK |
| `assessment_date` | `DATE` | R | Direct; safe date conversion |
| `assessment_type` | `STRING` | R | Direct; trim and uppercase; no approved domain rejection |
| `assessment_value` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `confidence_score` | `SOURCE_DECIMAL(s=3)` | O | Direct |
| `derived_from_matches` | `SOURCE_TYPE` | O | Direct; despite its name, this is a source field |
| `batch_id` | `BIGINT` | R | Direct; mandatory FK |

### 5.7 `teams`

Purpose: persistent doubles-team identity and lifecycle context.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `team_type` | `STRING` | R | Direct; uppercase; `AD HOC → AD_HOC` |
| `team_division` | `STRING` | R | Direct; uppercase; documented aliases under Section 8 |
| `team_status` | `STRING` | R | Direct; uppercase; documented aliases under Section 8 |
| `country_code` | `STRING` | O | Direct; trim and uppercase; preserve `US`/`CA` |
| `formation_date` | `DATE` | R | Direct; safe date conversion |
| `dissolution_date` | `DATE` | O | Direct; safe date conversion |

### 5.8 `team_memberships`

Purpose: historical player-team composition.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `team_id` | `BIGINT` | R | Direct; mandatory FK |
| `player_id` | `BIGINT` | R | Direct; mandatory FK |
| `player_position` | `STRING` | R | `POSITION_SOURCE`; trim/uppercase when physically `STRING`; map physical `BIGINT` `1` or string `"1"` to `LEFT`, and physical `BIGINT` `2` or string `"2"` to `RIGHT` |
| `joined_date` | `DATE` | R | Direct; safe date conversion |
| `left_date` | `DATE` | O | Direct; safe date conversion |

### 5.9 `matches`

Purpose: match context, result, and release reference.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `match_date` | `DATE` | R | Direct; safe date conversion |
| `region_id` | `BIGINT` | O | Direct; optional FK |
| `match_type` | `STRING` | R | Direct; trim and uppercase; no approved domain rejection |
| `court_type` | `STRING` | O | Direct; trim and uppercase; no approved domain rejection |
| `match_format` | `STRING` | O | Direct; trim and uppercase; no approved domain rejection |
| `winning_team_id` | `BIGINT` | O | Direct; optional FK plus `SILVER-MATCH-001` |
| `total_points_played` | `BIGINT` | O | Direct; no approved range or game-reconciliation rule |
| `batch_id` | `BIGINT` | R | Direct; mandatory FK |

### 5.10 `match_teams`

Purpose: a persistent team participating as one side of a match.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `match_id` | `BIGINT` | R | Direct; mandatory FK |
| `team_number` | `BIGINT` | R | Direct; must be `1` or `2` |
| `team_id` | `BIGINT` | R | Direct; mandatory FK |
| `team_score` | `SOURCE_TYPE` | R | Direct; no approved range or reconciliation rule |
| `average_team_rating` | `SOURCE_DECIMAL(s=3)` | O | Direct |

### 5.11 `match_team_players`

Purpose: actual player participation on a match side.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `match_team_id` | `BIGINT` | R | Direct; mandatory FK |
| `player_id` | `BIGINT` | R | Direct; mandatory FK |
| `player_position` | `STRING` | O | `POSITION_SOURCE`; null remains null; trim/uppercase when physically `STRING`; map physical `BIGINT` `1` or string `"1"` to `LEFT`, and physical `BIGINT` `2` or string `"2"` to `RIGHT` |
| `player_rating_at_match` | `SOURCE_DECIMAL(s=3)` | O | Direct; do not replace with snapshot rating |
| `derived_age_at_match` | `INT` | R | Derived under Section 7 |

### 5.12 `match_games`

Purpose: game sequence and score evidence within a match.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `match_id` | `BIGINT` | R | Direct; mandatory FK |
| `game_number` | `BIGINT` | R | Direct; positive |
| `team_one_score` | `BIGINT` | R | Direct; nonnegative |
| `team_two_score` | `BIGINT` | R | Direct; nonnegative |
| `winning_team_number` | `BIGINT` | R | Direct; `1` or `2`, consistent with larger score |
| `target_score` | `BIGINT` | O | Direct; nonnegative when populated |
| `win_by` | `BIGINT` | O | Direct; nonnegative when populated |
| `actual_team_one_score_share` | `SOURCE_DECIMAL(s=4)` | O | Direct; validate under `SILVER-GAME-008` |

### 5.13 `monthly_batches`

Purpose: batch, snapshot, and historical-period context.

| Field | Type | Null | Mapping and standardization |
|---|---|---:|---|
| `id` | `BIGINT` | R | Direct |
| `batch_month` | `DATE` | R | Direct; safe month conversion |
| `batch_sequence` | `BIGINT` | R | Direct; zero or positive |
| `batch_type` | `STRING` | R | Direct; trim and uppercase; no approved domain rejection |
| `active_player_count_start` | `BIGINT` | O | Direct; no approved range rule |
| `new_player_count` | `BIGINT` | O | Direct; no approved range rule |
| `active_player_count_end` | `BIGINT` | O | Direct; no approved range rule |
| `match_count_generated` | `BIGINT` | O | Direct; no approved range rule |
| `rating_update_count` | `BIGINT` | O | Direct; no approved range rule |
| `assessment_update_count` | `BIGINT` | O | Direct; no approved range rule |

## 6. Referential-integrity behavior

For each relationship in Section 4:

1. Normalize and classify the child reference without changing the source occurrence.
2. A null mandatory FK fails `SILVER-REQ-001`.
3. A null optional FK is allowed.
4. For a populated reference, first check the normalized key in the original Bronze parent table.
5. If it is absent from Bronze, apply `SILVER-FK-001` as a direct rejection.
6. If it exists in Bronze but no corresponding accepted parent exists, apply `SILVER-FK-002` as a cascading rejection.
7. If an occurrence has multiple invalid relationships, retain every applicable reason on its single rejection row.

Only relationships listed in Section 4 are foreign keys. In particular, `player_master.rating_batch_id` is not an approved FK.

`matches.winning_team_id` is optional. When populated, it must resolve to an accepted `teams.id` and must also satisfy `SILVER-MATCH-001`. The latter is evaluated against normalized Bronze `match_teams` pairs to avoid a circular accepted-table dependency.

**Scope of winner-participation validation:** `SILVER-MATCH-001` establishes that a corresponding match/team participation pair exists in **Bronze**, not necessarily in accepted Silver. A Bronze `match_teams` occurrence can subsequently fail its own Silver rules, leaving an accepted `matches` row without that winning team represented among accepted Silver match sides. This is a known limitation of the simplified, non-circular baseline; do not silently add reverse cascading rejection or a new post-Silver winner rule. Surface any such cases during review of the tainted profiles and seek instructor approval before changing the student-facing rejection contract.

## 7. Required age derivations

### 7.1 Authoritative snapshot date

Read the selected profile's colocated `<raw_volume_path>/manifest.json` read-only. Require a valid ISO `snapshot_end_exclusive` date and calculate:

```text
snapshot_as_of_date = snapshot_end_exclusive - 1 calendar day
```

Do not use wall-clock time, notebook execution time, manifest build time, `MAX(monthly_batches.batch_month)`, or `player_master.snapshot_month` as a substitute. A missing, malformed, or profile-inconsistent manifest/snapshot value is a technical failure before any Silver write.

Before implementing the snapshot-age expression, verify in the read-only preflight that the actual selected manifest contains this field, establish its location and format, and confirm that it belongs to the selected profile. If the field is absent or structured differently, report the discrepancy and stop the affected implementation until the contract is clarified; do not fabricate a fallback date.

### 7.2 Completed-year algorithm

Age is the number of completed calendar years at the reference date:

```text
age = reference year - birth year
      - 1 when the birthday anniversary is after the reference date
```

For a February 29 birth, the birthday anniversary is March 1 in a non-leap reference year. Therefore, the age does not increment on February 28 and increments on March 1. A birthday on the reference date increments the age on that date.

### 7.3 `player_master.derived_age_at_snapshot`

- Birth source: accepted conversion of `player_master.birth_date`.
- Reference date: manifest-derived `snapshot_as_of_date`.
- If birth date is after the snapshot date, apply `SILVER-AGE-001` and reject the player occurrence.
- For an accepted player, the derived field is non-null `INT`.

### 7.4 `match_team_players.derived_age_at_match`

Join without fanout through:

```text
match_team_players.match_team_id → match_teams.id
match_teams.match_id             → matches.id
match_team_players.player_id     → player_master.player_id
```

- Birth source: accepted `player_master.birth_date`.
- Reference date: accepted `matches.match_date` reached through the accepted match side.
- Never use the snapshot date for historical match age.
- If birth date is after match date, apply `SILVER-AGE-002` as a direct participant rejection.
- For an accepted participant, the derived field is non-null `INT`.
- The joins and calculation must not alter the participant grain or count before classification.

No generic `age` or age-group field is part of the mandatory baseline.

## 8. Complete approved record-level rejection-rule catalog

This is the complete approved baseline. The implementation may attach multiple rules to one rejected occurrence. Unless stated otherwise, `rejection behavior` means exclude the occurrence from its accepted table, write it once to its source-specific rejection table, and include the rule in `rejection_reasons`.

### 8.1 Shared rules

| Rule ID | Source table(s) | Fields | Exact invalid condition | Class | Dependencies and behavior |
|---|---|---|---|---|---|
| `SILVER-PK-001` | All 13 | Logical PK from Section 4 | PK is null after type normalization, or blank after trimming when physically represented as a string | Direct | Reject occurrence; do not include null keys in duplicate grouping |
| `SILVER-PK-002` | All 13 | Logical PK from Section 4 | A non-null normalized PK occurs more than once in the source table | Direct | Reject every occurrence in the duplicate group; preserve multiplicity |
| `SILVER-REQ-001` | All 13 | Required fields in Section 8.2 | Required value is null, or a required string is empty after trimming | Direct | Retain all missing required fields in the reason evidence; PK null also receives `SILVER-PK-001` |
| `SILVER-DATE-001` | Tables/fields in Section 8.3 | Populated date/month fields | Non-null source value cannot be converted under Section 3.4 | Direct | Optional null remains valid; required null is handled by `SILVER-REQ-001` |
| `SILVER-FK-001` | Relationships in Section 8.4 | Populated FK | Normalized FK does not occur in the original Bronze parent key set | Direct | Reject child as a missing-parent defect |
| `SILVER-FK-002` | Relationships in Section 8.4 | Populated FK | Normalized FK occurs in Bronze parent data but has no accepted Silver parent | Cascading | Reject child as a consequence of parent rejection |

### 8.2 Required fields for `SILVER-REQ-001`

| Source table | Required fields |
|---|---|
| `regions` | `id`, `country_code`, `region_name` |
| `clubs` | `id`, `club_name`, `region_id` |
| `club_memberships` | `id`, `player_id`, `club_id`, `joined_date` |
| `player_master` | `player_id`, `external_player_key`, `first_name`, `last_name`, `birth_date`, `registration_date`, `player_status`, `snapshot_month` |
| `player_registrations` | `id`, `player_id`, `batch_id`, `registration_month` |
| `player_assessment_history` | `id`, `player_id`, `assessment_date`, `assessment_type`, `batch_id` |
| `teams` | `id`, `team_type`, `team_division`, `team_status`, `formation_date` |
| `team_memberships` | `id`, `team_id`, `player_id`, `player_position`, `joined_date` |
| `matches` | `id`, `match_date`, `match_type`, `batch_id` |
| `match_teams` | `id`, `match_id`, `team_number`, `team_id`, `team_score` |
| `match_team_players` | `id`, `match_team_id`, `player_id` |
| `match_games` | `id`, `match_id`, `game_number`, `team_one_score`, `team_two_score`, `winning_team_number` |
| `monthly_batches` | `id`, `batch_month`, `batch_sequence`, `batch_type` |

### 8.3 Date/month fields for `SILVER-DATE-001`

| Source table | Fields |
|---|---|
| `clubs` | `founding_date` |
| `club_memberships` | `joined_date`, `left_date` |
| `player_master` | `birth_date`, `registration_date`, `rating_date`, `snapshot_month` |
| `player_registrations` | `registration_month` |
| `player_assessment_history` | `assessment_date` |
| `teams` | `formation_date`, `dissolution_date` |
| `team_memberships` | `joined_date`, `left_date` |
| `matches` | `match_date` |
| `monthly_batches` | `batch_month` |

### 8.4 FK fields for `SILVER-FK-001` and `SILVER-FK-002`

| Child source/field | Parent source/field | Nullable |
|---|---|---:|
| `clubs.region_id` | `regions.id` | No |
| `club_memberships.player_id` | `player_master.player_id` | No |
| `club_memberships.club_id` | `clubs.id` | No |
| `player_master.home_region_id` | `regions.id` | Yes |
| `player_registrations.player_id` | `player_master.player_id` | No |
| `player_registrations.batch_id` | `monthly_batches.id` | No |
| `player_registrations.assigned_region_id` | `regions.id` | Yes |
| `player_assessment_history.player_id` | `player_master.player_id` | No |
| `player_assessment_history.batch_id` | `monthly_batches.id` | No |
| `team_memberships.team_id` | `teams.id` | No |
| `team_memberships.player_id` | `player_master.player_id` | No |
| `matches.region_id` | `regions.id` | Yes |
| `matches.winning_team_id` | `teams.id` | Yes |
| `matches.batch_id` | `monthly_batches.id` | No |
| `match_teams.match_id` | `matches.id` | No |
| `match_teams.team_id` | `teams.id` | No |
| `match_team_players.match_team_id` | `match_teams.id` | No |
| `match_team_players.player_id` | `player_master.player_id` | No |
| `match_games.match_id` | `matches.id` | No |

### 8.5 Table-specific rules

| Rule ID | Source table | Fields | Exact invalid condition | Class | Dependencies and behavior |
|---|---|---|---|---|---|
| `SILVER-BATCH-001` | `monthly_batches` | `batch_sequence` | Converted value is less than `0` | Direct | Zero is valid |
| `SILVER-TEAM-001` | `teams` | `team_type` | After trim/uppercase and `AD HOC → AD_HOC`, value is not `COMPETITIVE` or `AD_HOC` | Direct | No inference from `team_division` |
| `SILVER-TEAM-002` | `teams` | `team_division` | After trim/uppercase and alias mapping, value is not `MENS`, `WOMENS`, `MIXED`, or `OPEN` | Direct | Aliases: `MENS_DOUBLES → MENS`, `WOMENS_DOUBLES → WOMENS`, `MIXED_DOUBLES → MIXED`, `OPEN_DOUBLES → OPEN` |
| `SILVER-TEAM-003` | `teams` | `team_status` | After trim/uppercase and alias mapping, value is not `ACTIVE`, `INACTIVE`, or `DISSOLVED` | Direct | Aliases: `DORMANT → INACTIVE`, `RETIRED → DISSOLVED` |
| `SILVER-POS-001` | `team_memberships` | `player_position` | Required populated value after mapping is not `LEFT` or `RIGHT` | Direct | Bronze may be `BIGINT` or `STRING`; map `1`/`"1" → LEFT` and `2`/`"2" → RIGHT`; preserve the original Bronze value and type in rejects |
| `SILVER-POS-002` | `match_team_players` | `player_position` | Optional populated value after mapping is not `LEFT` or `RIGHT` | Direct | Null is valid; Bronze may be `BIGINT` or `STRING`; map `1`/`"1" → LEFT` and `2`/`"2" → RIGHT`; preserve the original Bronze value and type in rejects |
| `SILVER-MATCH-001` | `matches` | `id`, `winning_team_id`; Bronze `match_teams.match_id`, `team_id` | `winning_team_id` is populated and no normalized Bronze `match_teams` row has the same `(match_id, team_id)` | Direct | Separate from FK to accepted `teams`; inspect Bronze pairs to avoid accepted-table circularity. Does not guarantee an accepted Silver match-side row (Section 6). |
| `SILVER-SIDE-001` | `match_teams` | `team_number` | Converted value is not exactly `1` or `2` | Direct | No other side-number domain is approved |
| `SILVER-GAME-001` | `match_games` | `game_number` | Converted value is less than or equal to `0` | Direct | Positive integers only |
| `SILVER-GAME-002` | `match_games` | `team_one_score` | Converted value is less than `0` | Direct | No upper score limit is approved |
| `SILVER-GAME-003` | `match_games` | `team_two_score` | Converted value is less than `0` | Direct | No upper score limit is approved |
| `SILVER-GAME-004` | `match_games` | `winning_team_number` | Converted value is not exactly `1` or `2` | Direct | Match-local side number, not persistent team ID |
| `SILVER-GAME-005` | `match_games` | `winning_team_number`, `team_one_score`, `team_two_score` | Scores are tied, or winner is `1` without `team_one_score > team_two_score`, or winner is `2` without `team_two_score > team_one_score` | Direct | Evaluate after rules 002–004 conversions |
| `SILVER-GAME-006` | `match_games` | `target_score` | Populated converted value is less than `0` | Direct | Null is valid; no universal target is approved |
| `SILVER-GAME-007` | `match_games` | `win_by` | Populated converted value is less than `0` | Direct | Null is valid; no tournament-specific rule is approved |
| `SILVER-GAME-008` | `match_games` | `actual_team_one_score_share`, scores | Share is populated, total score is greater than zero, and absolute difference from `team_one_score / (team_one_score + team_two_score)` exceeds `0.0001` | Direct | Preserve source decimal precision; no comparison when total score is zero |
| `SILVER-GAME-009` | `match_games` | `match_id`, `game_number` | A normalized pair occurs more than once in Bronze | Direct | Reject every occurrence in the duplicate pair; independent of PK duplication |
| `SILVER-AGE-001` | `player_master` | `birth_date`; manifest snapshot date | Valid birth date is after `snapshot_as_of_date` | Direct | Prevent negative snapshot age |
| `SILVER-AGE-002` | `match_team_players` | player birth date and actual match date | Accepted player birth date is after the participant's accepted match date | Direct | Reject participant occurrence; parent rows remain accepted |

The catalog does not contain a general numeric-conversion rejection because the source contract publishes IDs/counts as integers and measurements as decimals. A delivered Bronze type-family mismatch is a technical source-contract failure. Date/month strings are the documented row-level conversion case.

### 8.6 Complete rule coverage by source

This matrix is exhaustive. A rule absent from a source row does not apply to that source under the mandatory baseline.

| Source table | Applicable record-level rules |
|---|---|
| `regions` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001` |
| `clubs` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002` |
| `club_memberships` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002` |
| `player_master` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-AGE-001` |
| `player_registrations` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002` |
| `player_assessment_history` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002` |
| `teams` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-TEAM-001`, `SILVER-TEAM-002`, `SILVER-TEAM-003` |
| `team_memberships` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-POS-001` |
| `matches` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-MATCH-001` |
| `match_teams` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-SIDE-001` |
| `match_team_players` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-POS-002`, `SILVER-AGE-002` |
| `match_games` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-FK-001`, `SILVER-FK-002`, `SILVER-GAME-001` through `SILVER-GAME-009` |
| `monthly_batches` | `SILVER-PK-001`, `SILVER-PK-002`, `SILVER-REQ-001`, `SILVER-DATE-001`, `SILVER-BATCH-001` |

## 9. Rules explicitly not approved for rejection

The following are not record-level rejection criteria in this baseline because the current source contract does not define them precisely enough or the simplified prompt does not require them:

- Domains for country code beyond preserving/uppercasing observed codes, including rejection of codes other than `US` or `CA`.
- Domains for gender, dominant hand, player status, assessment type, registration source, batch type, region type, club type, competitiveness level, match type, court type, or match format.
- UUID-format or UUID-version validation for `external_player_key`.
- Bounds for ratings, confidence, volatility, percentile, coordinates, populations, capacities, court counts, batch counts, `team_score`, `average_team_rating`, `total_points_played`, or player rating at match.
- Equality between `rating` and `rating_value`.
- Referential enforcement of `player_master.rating_batch_id`.
- `left_date >= joined_date` or `dissolution_date >= formation_date`. These are reasonable candidate temporal rules, but the current Source Field Dictionary describes their formats while leaving valid ranges unresolved.
- Snapshot-boundary rejection for registration, assessment, formation, dissolution, membership, rating, or match dates, other than the two required age-validity rules.
- Exactly two sides per match, exactly two participants per side, exactly two current players per team, or distinct-side/team checks.
- Rejection of the same player appearing twice on a side or on both sides of a match.
- Membership-at-match validation or overlap detection.
- Reconciliation of match totals, team scores, games, or match winners beyond the explicit approved game and winner-side rules.
- Gold eligibility, current-active, ranking, roster, suitability, or performance rules.

These may be profiled or discussed outside the mandatory rejection logic. Turning any item into a rejection requires instructor approval and an update to this specification and its traceability matrix.

## 10. Rejection-table contract

Create one managed Delta rejection table for every source, including an empty table with its declared schema:

```text
regions_rejects
clubs_rejects
club_memberships_rejects
player_master_rejects
player_registrations_rejects
player_assessment_history_rejects
teams_rejects
team_memberships_rejects
matches_rejects
match_teams_rejects
match_team_players_rejects
match_games_rejects
monthly_batches_rejects
```

Each table has, in order:

1. Every original source business column in source order, with its original Bronze value and Bronze type.
2. The ten Bronze metadata columns in this order and with their Bronze types:
   `_pipeline_run_id`, `_pipeline_name`, `_pipeline_version`, `_release_name`, `_source_file_name`, `_source_file_path`, `_source_file_size`, `_source_file_modification_ts`, `_ingested_ts`, `_source_record_hash`.
3. The following rejection fields:

| Field | Type | Null | Meaning |
|---|---|---:|---|
| `rejection_reasons` | `ARRAY<STRUCT<rule_id:STRING,classification:STRING,fields:ARRAY<STRING>,message:STRING>>` | R | All distinct applicable rule reasons in stable rule-ID order |
| `has_direct_rejection` | `BOOLEAN` | R | True when at least one reason has classification `DIRECT` |
| `has_cascading_rejection` | `BOOLEAN` | R | True when at least one reason has classification `CASCADING` |
| `rejected_at` | `TIMESTAMP` | R | One UTC timestamp assigned by the current Silver execution |

`classification` is exactly `DIRECT` or `CASCADING`. The `fields` array identifies the relevant child fields; `message` is a concise student-readable explanation and must not contain an entire source record.

One rejected Bronze occurrence produces one rejection row, no matter how many reasons apply. Duplicate occurrences remain separate rows. Do not group, deduplicate, or create one output row per reason.

For each source:

```text
Bronze occurrence count = accepted occurrence count + rejected occurrence count
```

## 11. Persisted DQ summary contract

The managed Delta table is `silver_data_quality_summary`. It is a current-state summary, not run history, and is fully replaced by each successful authorized profile execution.

### 11.1 Schema

| Field | Type | Null | `TABLE_TOTAL` | `REASON_TOTAL` |
|---|---|---:|---|---|
| `row_type` | `STRING` | R | `TABLE_TOTAL` | `REASON_TOTAL` |
| `dataset_profile` | `STRING` | R | Selected profile | Selected profile |
| `source_table` | `STRING` | R | Source name | Source name |
| `reason_id` | `STRING` | O | Null | Rule ID |
| `reason_classification` | `STRING` | O | Null | `DIRECT` or `CASCADING` |
| `bronze_record_count` | `BIGINT` | O | Populated | Null |
| `accepted_record_count` | `BIGINT` | O | Populated | Null |
| `rejected_record_count` | `BIGINT` | O | Populated | Null |
| `rejection_percentage` | `DOUBLE` | O | Populated | Null |
| `direct_rejected_record_count` | `BIGINT` | O | Populated | Null |
| `cascading_rejected_record_count` | `BIGINT` | O | Populated | Null |
| `reason_occurrence_count` | `BIGINT` | O | Null | Populated |
| `reconciliation_difference` | `BIGINT` | O | Populated | Null |
| `reconciliation_status` | `STRING` | O | `MATCHED` or `MISMATCH` | Null |
| `summary_generated_at` | `TIMESTAMP` | R | Current UTC generation time | Same generation time |

### 11.2 Grain and counting

- `TABLE_TOTAL`: exactly one row for each of the 13 sources, including zero-row and zero-reject sources.
- `REASON_TOTAL`: one row for each `(source_table, reason_id, reason_classification)` that occurs at least once.
- `rejected_record_count` counts rejection-table rows, not reasons.
- `direct_rejected_record_count` counts rejection rows with `has_direct_rejection = true`.
- `cascading_rejected_record_count` counts rejection rows with `has_cascading_rejection = true`.
- A rejection may appear in both direct and cascading counts. Do not add those counts to derive `rejected_record_count`.
- `reason_occurrence_count` counts rejected occurrences containing that distinct rule/classification once. Reason totals may sum to more than rejected records.
- `rejection_percentage = 100.0 * rejected_record_count / bronze_record_count`; use `0.0` when the Bronze count is zero.
- `reconciliation_difference = bronze_record_count - accepted_record_count - rejected_record_count`.
- `reconciliation_status = MATCHED` only when the difference is zero.
- Reason rows must leave disposition/count columns null so totals cannot be accidentally double-counted across row types.

### 11.3 Example student SQL

Table-level disposition evidence:

```sql
SELECT source_table,
       bronze_record_count,
       accepted_record_count,
       rejected_record_count,
       ROUND(rejection_percentage, 2) AS rejection_percentage,
       reconciliation_status
FROM <catalog>.<silver_schema>.silver_data_quality_summary
WHERE row_type = 'TABLE_TOTAL'
ORDER BY source_table;
```

Most common rejection reasons:

```sql
SELECT source_table,
       reason_id,
       reason_classification,
       reason_occurrence_count
FROM <catalog>.<silver_schema>.silver_data_quality_summary
WHERE row_type = 'REASON_TOTAL'
ORDER BY reason_occurrence_count DESC, source_table, reason_id;
```

Direct and cascading evidence without treating them as additive:

```sql
SELECT source_table,
       rejected_record_count,
       direct_rejected_record_count,
       cascading_rejected_record_count
FROM <catalog>.<silver_schema>.silver_data_quality_summary
WHERE row_type = 'TABLE_TOTAL'
ORDER BY source_table;
```

Profile-wide rejected-record total, using totals rows only:

```sql
SELECT dataset_profile,
       SUM(bronze_record_count) AS bronze_records,
       SUM(accepted_record_count) AS accepted_records,
       SUM(rejected_record_count) AS rejected_records
FROM <catalog>.<silver_schema>.silver_data_quality_summary
WHERE row_type = 'TABLE_TOTAL'
GROUP BY dataset_profile;
```

## 12. Full-refresh and existing-output behavior

The default is:

```python
existing_table_action = "fail"
```

Only `fail` and `replace` are valid.

In `fail` mode, inspect all 27 expected fully qualified objects before the first write. If any exists, list it and stop without modifying any output.

In `replace` mode, require deliberate student authorization and display the selected profile, exact Silver schema, all 27 targets, and a warning that their prior contents will not be preserved. Replace only those 27 expected tables. Do not drop a schema, use wildcard deletion, or modify Bronze, Raw, another profile, or unrelated objects.

Every successful execution must write or replace all 13 accepted tables, all 13 rejection tables including empty ones, and the summary from the same in-memory classification results. It must not append prior accepted, rejected, or summary rows.

The 27 Delta writes are not atomic. If any write or required validation fails, report `FAILED / INCOMPLETE`, identify outputs that may have changed, and state that the selected profile is unsuitable for Gold until a complete authorized rerun succeeds. This specification intentionally defines no persisted readiness status, operations table, rollback, or transaction simulation.

## 13. Technical checks and failure behavior

The following are technical acceptance checks, not record-level DQ rules. Failure must stop or fail the notebook visibly and must not create a new business rejection reason:

- Invalid profile, catalog, schema, Raw Volume, or `existing_table_action` configuration.
- Unsafe or cross-profile target names.
- Missing/unreadable manifest, invalid `snapshot_end_exclusive`, or manifest/profile mismatch.
- Missing/unreadable Bronze table or any Bronze table outside the selected profile.
- Missing required physical source or Bronze metadata column.
- Source type-family or documented decimal-scale incompatibility.
- Existing output in `fail` mode.
- Spark/runtime expression failure, unsupported conversion expression, or unexpected exception.
- Failed managed Delta write or inability to create an empty declared reject table.
- Missing accepted, reject, or summary output after writing.
- Accepted PK nullness or uniqueness failure.
- Accepted mandatory-FK integrity failure.
- Join fanout or row-count change not explained by accepted/rejected classification.
- Empty/missing rejection reasons or invalid reason classification on a rejected row.
- Any per-source reconciliation difference.
- DQ summary counts that do not equal the current accepted/rejected outputs.
- Missing `TABLE_TOTAL` row or extra/stale profile/summary row.
- Missing age field, null accepted age, incorrect birthday calculation, or participant-age join fanout.
- Failure to write all 27 outputs during the current execution.

Expected record-level defects, cascading effects, and nonzero rejection counts do not independently fail the notebook. A technical failure does.

## 14. Acceptance criteria

A selected profile passes only when all of the following are demonstrated:

1. Exactly the 13 expected selected-profile Bronze inputs were read.
2. Every required source business column and all ten Bronze metadata columns passed preflight.
3. All 13 accepted tables exist with the fields, types, logical nullability outcomes, and original names in Section 5.
4. All 13 rejection tables exist with the contract in Section 10, including empty tables.
5. The DQ summary exists with exactly 13 `TABLE_TOTAL` rows and valid reason rows.
6. Every accepted logical PK is non-null and unique.
7. Every occurrence of each duplicate logical PK and duplicate game pair was rejected.
8. Every mandatory accepted FK resolves; populated optional FKs resolve.
9. Missing-Bronze parents and rejected parents are distinguished as direct and cascading.
10. Every applicable approved rejection reason is retained on one rejection row per source occurrence.
11. Every source satisfies `Bronze = accepted + rejected` without adding diagnostic subsets again.
12. Accepted fields preserve valid source meaning and decimal precision.
13. `derived_age_at_snapshot` and `derived_age_at_match` use the correct dates, completed-year logic, and March 1 leap-day convention.
14. Tests cover birthdays before, on, and after the reference date and February 29 around February 28/March 1 in a non-leap year.
15. Classification joins do not multiply source occurrences.
16. All 27 tables were written or intentionally replaced by the current execution and validated afterward.
17. No table outside the selected profile's 27 expected targets was modified.
18. The notebook reports overall `PASS` only after every required write and check succeeds; otherwise it reports `FAILED / INCOMPLETE` and prohibits Gold use.

Small deterministic fixtures are sufficient for local logic tests. Actual Databricks Spark/Delta execution is required before claiming runtime or managed-table acceptance.

## 15. DQ traceability matrix

| Silver rule or contract | Existing student-facing source | Alignment |
|---|---|---|
| Quality categories, expected-defect versus technical-failure distinction, and profile coverage | `docs/data_quality_rules.md`; `docs/data_quality_report.md` | This specification supplies the exact simplified rules and evidence contract those documents currently lack |
| Source inventory, grains, logical keys | `docs/dataset_specification.md` Expected source files; `docs/data_dictionary.md` Source-Table Registry | Same 13 sources and source-designated keys |
| Required fields | `docs/data_dictionary.md` Source Field Dictionary required/non-null expectations | Reproduced exactly in Section 8.2 |
| Source field names, type families, decimal scales | `docs/data_dictionary.md` Source Field Dictionary; approved `napa_5k_clean` and `napa_5k_tainted` physical preflight decisions | Preserved; unresolved precision remains source-preserved; `global_percentile` uses the any-profile `GLOBAL_PERCENTILE_SOURCE` exception without a new DQ rule |
| Bronze metadata | `notebooks/00_bootstrap_bronze.py`; `docs/data_dictionary.md` Required Bronze metadata fields | Same ten ordered columns in rejects |
| Duplicate logical keys | This specification Sections 3.5 and 8; `docs/dataset_specification.md` logical-key descriptions | Reject every occurrence; no winner selection |
| Required and optional FKs | `docs/dataset_specification.md` Conceptual relationships; `docs/data_dictionary.md` key roles and relationship matrix | Reproduced in Sections 4 and 8.4 |
| Direct versus cascading FK handling | This specification Sections 6 and 8.4 | Missing Bronze parent is direct; rejected parent is cascading |
| Date/month conversions | `docs/data_dictionary.md` source date/month definitions and documented `YYYY-MM` behavior | Safe ISO conversion, no invented dates |
| `US`/`CA` preservation | `docs/data_dictionary.md` country-code definitions; approved task decision | Uppercase and preserve; no `USA`/`CAN` mapping |
| Team domains and aliases | `docs/data_dictionary.md` `teams` field domains | Same canonical values and listed aliases |
| Position domains, physical representation, and aliases | `docs/data_dictionary.md` `team_memberships` and `match_team_players`; `napa_5k_clean` physical preflight | Bronze `BIGINT` and documented string representations are accepted inputs; accepted output remains `STRING`; same `LEFT`/`RIGHT`, `1`/`2` mappings; rejects preserve Bronze values |
| Match winner must be a participating team | `docs/data_dictionary.md` `matches.winning_team_id` relationship | Direct structural rule against Bronze match-team pairs |
| Match-side number | `docs/data_dictionary.md` `match_teams.team_number` | Same allowed values `1`/`2` |
| Game sequence, scores, winner, target, win-by, share | `docs/data_dictionary.md` `match_games` known domains | Same explicit conditions and `0.0001` tolerance |
| Batch sequence | `docs/data_dictionary.md` `monthly_batches.batch_sequence` | Negative rejected; zero accepted |
| Snapshot and match ages | This specification Section 7; `docs/data_dictionary.md` player/match date meanings | Only two derived fields; correct temporal references |
| March 1 leap-day convention | Approved task decision | Explicit in Section 7; no conflicting current rule found |
| Accepted/rejected reconciliation | This specification Sections 11 and 14 | One disposition per occurrence |
| Reject rows and multi-reason evidence | This specification Section 10 | Full source row, Bronze metadata, all reasons, one reject row |
| DQ summary totals/reasons | This specification Section 11 | Two explicit row grains and non-additive direct/cascade counts |
| Full refresh and reload protection | This specification Section 12; `docs/bronze_bootstrap_guide.md` conventions | `fail` default, deliberate `replace`, 27 current outputs |

## 16. Documentation synchronization

The repository's student-facing README files, architecture, lineage, runbook, quality templates, and configuration examples must remain aligned with this specification and the supplied notebook. Historical accepted projections, exception tables, convenience views, separate reject schemas, and `b2s_*` operations structures are not active Assignment 10 requirements.

## 17. Open review items

These ambiguities are intentionally not hidden requirements:

1. The mandatory read-only preflight must still verify physical decimal precision, source nullability, the manifest's `snapshot_end_exclusive` field and format, and schema compatibility across profiles as each is tested; discrepancies require instructor review before affected implementation or writes.
2. `team_score` and `derived_from_matches` retain `SOURCE_TYPE` because the current dictionary does not prescribe their physical types.
3. The interval-order rules identified in Section 9 require instructor approval before becoming rejection rules.
4. Any desired participant-cardinality, membership-history, side-cardinality, or cross-winner checks require an explicit decision about rejection versus non-rejecting evidence and a documented summary contract.
5. The complete country, player, match, club, region, batch, and assessment categorical domains remain unresolved; no implementation may infer them from observed samples alone.
6. The Bronze-based winner-participation check deliberately does not guarantee the winning side survives into accepted Silver. Review resulting cases in tainted-profile validation before proposing any more complex rejection behavior (Section 6).
