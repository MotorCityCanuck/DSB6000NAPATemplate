# Data Dictionary

## Purpose and Authority

This data dictionary is the version-controlled business and technical field reference for the NAPA Olympic Analytics Platform. It supports student review, AI-assisted development, and pull-request-based maintenance of definitions, interpretations, and unresolved questions. Consulting teams also use it to document their own Gold analytical features and measures.

This document does not replace `docs/raw_to_bronze_prompt.md` or `docs/bronze_to_silver_prompt.md`. Those construction prompts remain authoritative for prescribed Bronze and Silver implementation and acceptance requirements. The delivered Parquet files and colocated `manifest.json` provide physical source evidence; executed Databricks objects and pipeline evidence establish implementation results. Do not present a specification or assumption as verified physical fact.

## Verification Status Labels

- **Prescribed:** Defined by the supplied construction specifications but not yet verified against delivered data.
- **Physically verified:** Confirmed through inspection of delivered Parquet files or manifests.
- **Implementation verified:** Confirmed against executed Databricks tables or pipeline evidence.
- **Team-defined:** Established by the consulting team for its analytical solution.
- **Unresolved:** Requires clarification or additional evidence.

Every future field definition should identify its status and evidence source. An expected or prescribed field must not be labeled **Physically verified** without supporting Parquet or manifest evidence.

## Dataset Profiles

The prescribed source contracts apply to these five independent dataset profiles, subject to physical verification of each delivered package:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

No physical source schema is claimed as verified by this registry alone. Record profile-specific schema evidence and deviations when the delivered packages are inspected.

## Source-Table Registry

The purposes and grains below come from `docs/dataset_specification.md`. Keys and relationships come from the supplied construction prompts. The intended primary keys are contract metadata; actual uniqueness must be validated against delivered data.

| Source filename | Business purpose | Record grain | Intended primary key | Important relationships | Applicable profiles | Verification status |
|---|---|---|---|---|---|---|
| `regions.parquet` | Geographic context for players, clubs, and matches | One record per geographic region | `id` | Parent of clubs; optionally referenced by player home region, match region, and registration assigned region | All five | Prescribed |
| `clubs.parquet` | Club and facility context | One record per club or facility | `id` | Requires a region; parent of club memberships | All five | Prescribed |
| `club_memberships.parquet` | Historical player affiliation with clubs | One record per player-club membership period | `id` | Requires a player and club | All five | Prescribed |
| `player_master.parquet` | Player identity, profile, status, rating, and snapshot context | One current or snapshot record per player | `player_id` | May reference a home region; parent of registrations, assessments, memberships, and match participants | All five | Prescribed |
| `player_registrations.parquet` | Player registration and onboarding history | One record per player registration event | `id` | Requires a player and batch; may reference an assigned region | All five | Prescribed |
| `player_assessment_history.parquet` | Longitudinal player assessment evidence | One record per player assessment | `id` | Requires a player and batch | All five | Prescribed |
| `teams.parquet` | Team identity, country/category, and lifecycle context | One record per persistent doubles team or partnership | `id` | Parent of team memberships and match sides; may be referenced as a match winner | All five | Prescribed |
| `team_memberships.parquet` | Team composition and partnership continuity | One record per player-team membership period | `id` | Requires a team and player | All five | Prescribed |
| `matches.parquet` | Match context, result, location, and release reference | One record per match | `id` | Requires a batch; may reference a region and winning team; parent of match sides and games | All five | Prescribed |
| `match_teams.parquet` | Match-side participation linked to a persistent team | One record per participating side in a match | `id` | Requires a match and persistent team; parent of match-side players | All five | Prescribed |
| `match_team_players.parquet` | Player participation and match-time evidence | One record per player participating on a match side | `id` | Requires a match side and player | All five | Prescribed |
| `match_games.parquet` | Game sequence, scores, and result evidence | One record per game within a match | `id` | Requires a parent match | All five | Prescribed |
| `monthly_batches.parquet` | Batch, snapshot, reconciliation, and release-period context | One record per monthly batch or snapshot period | `id` | Parent of matches, registrations, and assessments | All five | Prescribed |

## Source Field Dictionary

The following field contracts come from Appendix A of `docs/bronze_to_silver_prompt.md` and apply to all five dataset profiles. They are **Prescribed**, not physically verified. Type families are stated only when Appendix A defines them. **Unresolved** identifies a meaning, type, format, domain, unit, or constraint that the authoritative sources do not establish; it must not be inferred from a field name.

### `regions`

Source: `regions.parquet`. Grain: one geographic region. This table provides geographic context for clubs and other entities where the documented relationship is present.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a geographic region | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `country_code` | Unresolved | Required (prescribed non-null) | None specified | Source country code for the region | Examples include `US` and `CA`; these are not Silver-standardized `USA` and `CAN`. The complete source domain is unresolved | Prescribed | Appendix A required-fields table and country-value note |
| `region_type` | Unresolved | Optional under prescribed contract | None specified | Unresolved — the source documents do not define the classification's business semantics | Unresolved — no allowed values are specified | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable |
| `region_name` | Unresolved | Required (prescribed non-null) | None specified | Name of the geographic region | Unresolved — no naming convention or constrained domain is specified | Prescribed | Appendix A ordered columns and required-fields table; dataset specification |
| `state_province_code` | Unresolved | Optional under prescribed contract | None specified | Source state or province code retained separately from any Silver canonical geography | Unresolved — no coding scheme or allowed values are specified | Prescribed | Appendix A ordered columns; Silver prompt requires preservation of this source attribute |
| `population` | `INT64` (source count) | Optional under prescribed contract | None specified | Population measure associated with the region; the measurement basis is unresolved | Unresolved — population basis, reference date, and unit convention are not specified | Prescribed | Appendix A ordered columns and type-family statement |
| `latitude` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Geographic latitude coordinate for the region | Decimal scale 6; precision, bounds, and coordinate reference convention are unresolved | Prescribed | Appendix A ordered columns, type-family statement, and decimal-scale expectation |
| `longitude` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Geographic longitude coordinate for the region | Decimal scale 6; precision, bounds, and coordinate reference convention are unresolved | Prescribed | Appendix A ordered columns, type-family statement, and decimal-scale expectation |

### `clubs`

Source: `clubs.parquet`. Grain: one club or facility. Each club's required `region_id` relates the club to `regions.id`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a club or facility | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `club_name` | Unresolved | Required (prescribed non-null) | None specified | Name of the club or facility | Unresolved — no naming convention or constrained domain is specified | Prescribed | Appendix A ordered columns and required-fields table; dataset specification |
| `region_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `regions.id` | Identifies the region associated with the club | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; Silver parent-key contract |
| `club_type` | Unresolved | Optional under prescribed contract | None specified | Source classification of the club; detailed semantics are unresolved | Unresolved — no allowed values are specified | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable |
| `competitiveness_level` | Unresolved | Optional under prescribed contract | None specified | Source competitiveness classification; detailed semantics are unresolved | Unresolved — no scale or allowed values are specified | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable |
| `member_capacity` | `INT64` (source count) | Optional under prescribed contract | None specified | Membership-capacity measure for the club; the measurement basis is unresolved | Unresolved — capacity basis and valid range are not specified | Prescribed | Appendix A ordered columns and type-family statement |
| `founding_date` | String-published date | Optional under prescribed contract | None specified | Source date associated with the club's founding | Unresolved — no string format or valid range is specified | Prescribed | Appendix A ordered columns and statement that dates are published as strings |
| `indoor_court_count` | `INT64` (source count) | Optional under prescribed contract | None specified | Number of indoor courts associated with the club | Count of courts; valid range is unresolved | Prescribed | Appendix A ordered columns and type-family statement |
| `outdoor_court_count` | `INT64` (source count) | Optional under prescribed contract | None specified | Number of outdoor courts associated with the club | Count of courts; valid range is unresolved | Prescribed | Appendix A ordered columns and type-family statement |

### `club_memberships`

Source: `club_memberships.parquet`. Grain: one player-club membership period. Each record's required `club_id` relates to `clubs.id`, and its required `player_id` relates to `player_master.player_id`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a player-club membership record | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `player_master.player_id` | Identifies the player in the membership period | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; Silver parent-key contract |
| `club_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `clubs.id` | Identifies the club in the membership period | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; Silver parent-key contract |
| `membership_type` | Unresolved | Optional under prescribed contract | None specified | Source classification of the membership; detailed semantics are unresolved | Unresolved — no allowed values are specified | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable |
| `joined_date` | String-published date | Required (prescribed non-null) | None specified | Start or joining date for the membership period | Unresolved — no string format or valid range is specified | Prescribed | Appendix A ordered columns, required-fields table, and statement that dates are published as strings; dataset specification grain |
| `left_date` | String-published date | Optional under prescribed contract | None specified | End or leaving date for the membership period | Unresolved — no string format or valid range is specified | Prescribed | Appendix A ordered columns and statement that dates are published as strings; dataset specification grain |
| `is_primary` | `BOOLEAN` | Optional under prescribed contract | None specified | Source indicator related to primary club membership; the precise business interpretation is unresolved | `true` or `false` when populated; null is allowed under the prescribed source contract | Prescribed | Appendix A ordered columns, explicit type statement, and nullable-by-default rule |

### `player_master`

Source: `player_master.parquet`. Grain: one current or snapshot record per player. The table is the parent of player registrations and assessment history. Its nullable `home_region_id` relates to `regions.id`; Appendix A does not prescribe a foreign-key role for `rating_batch_id`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for the player snapshot record | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `external_player_key` | `STRING` (published UUID text) | Required (prescribed non-null) | Alternate identifier; no referential role specified | External identifier for the player | UUID text; exact UUID version and validation details are unresolved | Prescribed | Appendix A ordered columns, explicit UUID-text statement, and required-fields table |
| `first_name` | Unresolved | Required (prescribed non-null) | None specified | Player's first name | Unresolved — no naming convention or constrained domain is specified | Prescribed | Appendix A ordered columns and required-fields table; player transformation preserves trimmed name case |
| `last_name` | Unresolved | Required (prescribed non-null) | None specified | Player's last name | Unresolved — no naming convention or constrained domain is specified | Prescribed | Appendix A ordered columns and required-fields table; player transformation preserves trimmed name case |
| `gender` | Unresolved | Optional under prescribed contract | None specified | Source gender attribute for the player; detailed semantics are unresolved | Unresolved — Silver standardization rules do not establish the complete physical source domain | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable; Silver player validation |
| `birth_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Player's source birth date | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table |
| `dominant_hand` | Unresolved | Optional under prescribed contract | None specified | Source dominant-hand attribute for the player; detailed semantics are unresolved | Unresolved — Silver standardization rules do not establish the complete physical source domain | Prescribed | Appendix A ordered columns; all fields not listed as required are nullable; Silver player validation |
| `home_region_id` | `INT64` (source ID) | Optional under prescribed contract | Nullable foreign key to `regions.id` | Identifies the player's source home region when populated | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns; source-relationship matrix marks this relationship nullable |
| `country_code` | Unresolved | Optional under prescribed contract | None specified | Source country code for the player | Examples include `US` and `CA`; these are not Silver-standardized `USA` and `CAN`. The complete source domain is unresolved | Prescribed | Appendix A country-value note; all fields not listed as required are nullable |
| `registration_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Source date associated with the player's registration | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table |
| `player_status` | Unresolved | Required (prescribed non-null) | None specified | Source status attribute for the player | Unresolved — Silver recognizes configured status and boolean-like values, but Appendix A does not prescribe a complete source domain | Prescribed | Appendix A ordered columns and required-fields table; Silver player status handling |
| `rating` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Compatibility alias of `rating_value`; it is not a separate derived Silver rating | Decimal scale 3; precision, units, range, and rating methodology are unresolved | Prescribed | Appendix A explicit alias statement and decimal-scale expectation |
| `rating_value` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source player rating measure for the snapshot | Decimal scale 3; precision, units, range, and rating methodology are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; snapshot-history requirements |
| `confidence_score` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source confidence measure associated with the player rating; exact interpretation is unresolved | Decimal scale 3; precision, units, and range are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver player transformation |
| `volatility_score` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source volatility measure; exact interpretation is unresolved | Decimal scale 3; precision, units, and range are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation |
| `global_percentile` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source global-percentile measure; comparison population and calculation are unresolved | Decimal scale 2; precision, units, and numeric bounds are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation |
| `match_count_used` | `INT64` (source count) | Optional under prescribed contract | None specified | Source match count associated with the player snapshot or rating; exact inclusion logic is unresolved | Count of matches; valid range and inclusion window are unresolved | Prescribed | Appendix A ordered columns and type-family statement; snapshot-history requirements |
| `rating_date` | `STRING` (published date) | Optional under prescribed contract | None specified | Source date associated with the player rating | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns and type-family statement; snapshot-history requirements |
| `rating_batch_id` | `INT64` (source ID) | Optional under prescribed contract | None specified | Source batch identifier associated with the player rating; referential enforcement is unresolved | Unresolved — Appendix A specifies the ID type but no foreign-key constraint | Prescribed | Appendix A ordered columns and type-family statement; not listed in the source-relationship matrix |
| `snapshot_month` | `STRING` (published date/month) | Required (prescribed non-null) | None specified | Source month identifying the player snapshot context | Unresolved — no string format is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; snapshot-history requirements |

### `player_registrations`

Source: `player_registrations.parquet`. Grain: one player registration event. Each record's required `player_id` relates to `player_master.player_id`, its required `batch_id` relates to `monthly_batches.id`, and its optional `assigned_region_id` relates to `regions.id` when populated.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a player registration event | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `player_master.player_id` | Identifies the player associated with the registration event | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `batch_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `monthly_batches.id` | Identifies the monthly batch associated with the registration event | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `registration_month` | `STRING` (published date/month) | Required (prescribed non-null) | None specified | Source month associated with the registration event | A valid `YYYY-MM` value is interpreted as the first day of that month by Silver; the complete physical source format is unresolved | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Silver registration transformation |
| `registration_source` | Unresolved | Optional under prescribed contract | None specified | Source classification describing how the registration originated; detailed semantics are unresolved | Unresolved — no allowed values are prescribed | Prescribed | Appendix A ordered columns; Silver preserves and uppercases this source attribute |
| `assigned_region_id` | `INT64` (source ID) | Optional under prescribed contract | Nullable foreign key to `regions.id` | Identifies an assigned region for the registration when populated | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns; source-relationship matrix marks this relationship nullable |
| `initial_rating_value` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source initial rating measure associated with the registration; exact interpretation is unresolved | Decimal scale 3; precision, units, range, and rating methodology are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver registration transformation preserves the attribute |
| `initial_confidence_score` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source initial confidence measure associated with the registration; exact interpretation is unresolved | Decimal scale 3; precision, units, and range are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver registration transformation preserves the attribute |

### `player_assessment_history`

Source: `player_assessment_history.parquet`. Grain: one player assessment. Each record's required `player_id` relates to `player_master.player_id`, and its required `batch_id` relates to `monthly_batches.id`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a player assessment record | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `player_master.player_id` | Identifies the player associated with the assessment | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `assessment_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Source date of the player assessment | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Silver assessment transformation |
| `assessment_type` | Unresolved | Required (prescribed non-null) | None specified | Source classification of the assessment; detailed semantics are unresolved | Unresolved — no allowed values are prescribed | Prescribed | Appendix A ordered columns and required-fields table; Silver uppercases the source value without prescribing its domain |
| `assessment_value` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source assessment measure; its business interpretation depends on the unresolved assessment type | Decimal scale 3; precision, units, range, and scale interpretation are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver assessment transformation |
| `confidence_score` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source confidence measure associated with the assessment; exact interpretation is unresolved | Decimal scale 3; precision, units, and range are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver assessment transformation |
| `derived_from_matches` | Unresolved | Optional under prescribed contract | None specified | Source attribute retained with the assessment; its exact business meaning is unresolved | Unresolved — no logical type or allowed values are prescribed | Prescribed | Appendix A ordered columns; Appendix B requires preserving this source attribute |
| `batch_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `monthly_batches.id` | Identifies the monthly batch associated with the assessment | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |

### `teams`

Source: `teams.parquet`. Grain: one persistent doubles team or partnership. A persistent team records partnership identity and lifecycle context; it is not a match-side occurrence or evidence of which players actually participated in a particular match. `match_teams` links a persistent team to a match side, and `match_team_players` records actual match participants; those field contracts are deferred to Group 4.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a persistent doubles team or partnership | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `team_type` | Unresolved | Required (prescribed non-null) | None specified | Schema 1.6 interprets modern `team_type` as team identity, distinct from team division; the meaning of legacy division-valued entries is compatibility-dependent | Standardized identity values are `COMPETITIVE` and `AD_HOC`, with `AD HOC` mapped to `AD_HOC`; the complete physical source domain and legacy semantics are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver domain table and team transformation require identity/division separation |
| `team_division` | Unresolved | Required (prescribed non-null) | None specified | Source team division or category, distinct from team identity | Standardized values are `MENS`, `WOMENS`, `MIXED`, and `OPEN`; corresponding `*_DOUBLES` values map to these categories. The complete physical source domain is unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver domain table and team transformation |
| `team_status` | Unresolved | Required (prescribed non-null) | None specified | Source lifecycle status of the persistent team | Standardized values are `ACTIVE`, `INACTIVE`, and `DISSOLVED`; `DORMANT` maps to `INACTIVE`, and `RETIRED` maps to `DISSOLVED`. The complete physical source domain is unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver domain table and team transformation |
| `country_code` | Unresolved | Optional under prescribed contract | None specified | Source country code for the persistent team | Examples include `US` and `CA`; these are not Silver-standardized `USA` and `CAN`. The complete source domain is unresolved | Prescribed | Appendix A country-value note; all fields not listed as required are nullable |
| `formation_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Source date associated with formation of the persistent team | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Silver team transformation |
| `dissolution_date` | `STRING` (published date) | Optional under prescribed contract | None specified | Source date associated with dissolution of the persistent team | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns and type-family statement; Silver team transformation |

### `team_memberships`

Source: `team_memberships.parquet`. Grain: one player-team membership period. Each record's required `team_id` relates to `teams.id`, and its required `player_id` relates to `player_master.player_id`. Membership records describe partnership composition and continuity over time; they do not establish that a player represented the team in a particular match. Match participation is recorded through `match_teams` and `match_team_players` and will be documented separately.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a player-team membership period | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `team_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `teams.id` | Identifies the persistent team in the membership period | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `player_master.player_id` | Identifies the player in the membership period | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `player_position` | Unresolved | Required (prescribed non-null) | None specified | Source position attribute within the player-team membership; positional semantics beyond the standardized labels are unresolved | Standardized values are `LEFT` and `RIGHT`; string `1` maps to `LEFT`, and string `2` maps to `RIGHT`. The complete physical source domain is unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver domain table and team-membership transformation |
| `joined_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Start or joining date for the player-team membership period | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; dataset specification grain |
| `left_date` | `STRING` (published date) | Optional under prescribed contract | None specified | End or leaving date for the player-team membership period | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns and type-family statement; dataset specification grain |

### `matches`

Source: `matches.parquet`. Grain: one match. A match is the parent of its participating side records in `match_teams` and its individual games in `match_games`. Its required `batch_id` relates to `monthly_batches.id`; optional `region_id` relates to `regions.id`. Optional `winning_team_id` identifies a persistent `teams.id` and must correspond to `match_teams.team_id` for the same match; it is not a `match_teams.id` match-side identifier.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a match | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `match_date` | `STRING` (published date) | Required (prescribed non-null) | None specified | Source date of the match | Unresolved — no string format or valid range is prescribed by Appendix A | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Silver match transformation |
| `region_id` | `INT64` (source ID) | Optional under prescribed contract | Nullable foreign key to `regions.id` | Identifies the region associated with the match when populated | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns; source-relationship matrix marks this relationship nullable |
| `match_type` | Unresolved | Required (prescribed non-null) | None specified | Source classification of the match; Silver uses its uppercased value as `competition_category` | Unresolved — no allowed values or detailed category semantics are prescribed | Prescribed | Appendix A ordered columns and required-fields table; Silver match transformation |
| `court_type` | Unresolved | Optional under prescribed contract | None specified | Source court classification for the match; detailed semantics are unresolved | Unresolved — no allowed values are prescribed | Prescribed | Appendix A ordered columns; Silver match transformation preserves the attribute |
| `match_format` | Unresolved | Optional under prescribed contract | None specified | Source match-format classification; detailed semantics are unresolved | Unresolved — no allowed values are prescribed | Prescribed | Appendix A ordered columns; Silver match transformation preserves the attribute |
| `winning_team_id` | `INT64` (source ID) | Optional under prescribed contract | Nullable foreign key to `teams.id`; must also match `match_teams.team_id` for the same match | Identifies the persistent team recorded as the match winner; it is not the match-side row ID | Unresolved — winner mapping must be unambiguous, but no identifier range or additional outcome semantics are prescribed | Prescribed | Appendix A ordered columns; source-relationship matrix and Silver winner-mapping instructions |
| `total_points_played` | `INT64` (source count) | Optional under prescribed contract | None specified | Source match-level total-points measure | Count of points; calculation method, reconciliation to games, and valid range are unresolved | Prescribed | Appendix A ordered columns and type-family statement; Silver match transformation preserves the attribute |
| `batch_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `monthly_batches.id` | Identifies the monthly batch associated with the match | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |

### `match_teams`

Source: `match_teams.parquet`. Grain: one participating side in a match. Each record's required `match_id` relates to `matches.id`, while required `team_id` identifies the persistent `teams.id` represented by that side. The source `id` identifies the match-side row itself and must not be treated as the persistent team identifier.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a participating match-side record | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `match_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `matches.id` | Identifies the match in which the side participated | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `team_number` | Integer side number | Required (prescribed non-null) | Match-local side identifier; not a persistent team key | Identifies the side as team one or team two within the match | Allowed values are integer `1` or `2` after safe conversion | Prescribed | Appendix A ordered columns and required-fields table; Silver match-side transformation |
| `team_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `teams.id` | Identifies the persistent doubles team represented by the match side | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `team_score` | Unresolved | Required (prescribed non-null) | None specified | Source match-level score for the participating side; it is distinct from scores for individual games | Unresolved — physical type, units, calculation, valid range, and reconciliation to game scores are not prescribed | Prescribed | Appendix A ordered columns and required-fields table; Silver match-side transformation preserves the attribute |
| `average_team_rating` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source average team rating, used as a possible source for Silver pre-match team rating; averaging methodology is unresolved | Decimal scale 3; precision, units, range, and averaging method are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver match-side transformation |

### `match_team_players`

Source: `match_team_players.parquet`. Grain: one player participating on a match side. Each record's required `match_team_id` relates to the match-side row `match_teams.id`, and required `player_id` relates to `player_master.player_id`. This table records actual match participation and is distinct from the longer-lived partnership periods in `team_memberships`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a player's participation on a match side | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `match_team_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `match_teams.id` | Identifies the participating match side on which the player appeared | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `player_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `player_master.player_id` | Identifies the player participating on the match side | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `player_position` | Unresolved | Optional under prescribed contract | None specified | Source position attribute for the player in the match-side participation record; detailed semantics are unresolved | Standardized values are `LEFT` and `RIGHT`; string `1` maps to `LEFT`, and string `2` maps to `RIGHT`. The complete physical source domain is unresolved | Prescribed | Appendix A ordered columns; Silver player-position domain and match-participant transformation |
| `player_rating_at_match` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Historical player rating recorded at match time; it is distinct from the player snapshot rating | Decimal scale 3; precision, units, range, and rating methodology are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver requires preservation of match-time rating |

### `match_games`

Source: `match_games.parquet`. Grain: one individual game within a parent match. Each record's required `match_id` relates to `matches.id`. Game scores and `winning_team_number` describe a game-level result using match-local side numbers; they are distinct from the match-level persistent winner recorded by `matches.winning_team_id`.

| Field name | Prescribed logical type or family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for an individual game within a match | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; Raw-to-Bronze source registry |
| `match_id` | `INT64` (source ID) | Required (prescribed non-null) | Foreign key to `matches.id` | Identifies the parent match containing the game | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns and required-fields table; source-relationship matrix |
| `game_number` | Integer game sequence | Required (prescribed non-null) | Match-local game identifier; not a standalone foreign key | Identifies the game's sequence within its parent match | Must be a positive integer; uniqueness within a match is validated separately | Prescribed | Appendix A ordered columns and required-fields table; Silver game transformation and integrity checks |
| `team_one_score` | Integer score | Required (prescribed non-null) | None specified | Game-level score attributed to match side number 1 | Must be a nonnegative integer; scoring units and tournament-specific limits are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver game transformation |
| `team_two_score` | Integer score | Required (prescribed non-null) | None specified | Game-level score attributed to match side number 2 | Must be a nonnegative integer; scoring units and tournament-specific limits are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Silver game transformation |
| `winning_team_number` | Integer side number | Required (prescribed non-null) | Match-local side identifier; not `teams.id` or `match_teams.id` | Identifies the winning match side for this game | Allowed values are integer `1` or `2`; it must agree with the side having the larger game score | Prescribed | Appendix A ordered columns and required-fields table; Silver game transformation |
| `target_score` | Integer score | Optional under prescribed contract | None specified | Source target-score attribute for the game; detailed competition semantics are unresolved | When populated, must be nonnegative; no universal target or tournament-specific meaning is prescribed | Prescribed | Appendix A ordered columns; Silver game transformation explicitly avoids inventing a universal score target |
| `win_by` | Integer score or margin | Optional under prescribed contract | None specified | Source win-by attribute for the game; exact interpretation is unresolved | When populated, must be nonnegative; units and competition-specific semantics are unresolved | Prescribed | Appendix A ordered columns; Silver game transformation |
| `actual_team_one_score_share` | `DECIMAL` (numeric measurement) | Optional under prescribed contract | None specified | Source share of game points attributed to match side number 1 | Decimal scale 4; when total game points are positive, Silver validates agreement with `team_one_score / (team_one_score + team_two_score)` within `0.0001`. Precision and numeric bounds are unresolved | Prescribed | Appendix A ordered columns and decimal-scale expectation; Silver game transformation |

### `monthly_batches`

Source: `monthly_batches.parquet`. Grain: one monthly batch or snapshot period. These records provide release or batch context for registrations, assessments, and matches through the required relationships `player_registrations.batch_id`, `player_assessment_history.batch_id`, and `matches.batch_id` to `monthly_batches.id`. Batch month and sequence describe batch context; they do not replace registration, assessment, match, or other business-event dates. No release schedule, retention period, or historical coverage is prescribed.

| Field name | Prescribed logical type or type family | Required/non-null expectation | Key role | Supported business meaning | Known domain, units, or allowed values | Verification status | Source reference or notes |
|---|---|---|---|---|---|---|---|
| `id` | `INT64` (source ID) | Required (prescribed non-null) | Primary key | Identifier for a monthly batch or snapshot-period record | Unresolved — no value range is specified | Prescribed | Appendix A ordered columns, type-family statement, and required-fields table; dataset specification grain and key |
| `batch_month` | `STRING` (published date or month) | Required (prescribed non-null) | None specified | Identifies the historical batch period used as release or snapshot context | Stage 5 recognizes a valid `YYYY-MM` value for conversion to the first day of that month; other physical formats, supported periods, and release schedules are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Stage 5 monthly-batch transformation; temporal-reference policy |
| `batch_sequence` | Integer sequence | Required (prescribed non-null) | None specified | Source sequence associated with the batch record | Silver rejects negative values and permits zero; global ordering, uniqueness, and continuity semantics are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Stage 5 monthly-batch transformation |
| `batch_type` | Unresolved categorical source attribute | Required (prescribed non-null) | None specified | Source classification for the batch or snapshot-period record | Silver standardizes populated values to uppercase; allowed values and physical type are unresolved | Prescribed | Appendix A ordered columns and required-fields table; Stage 5 monthly-batch transformation |
| `active_player_count_start` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of active players at the start of the batch period | Unit is players; the active-player definition, calculation, timing boundary, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |
| `new_player_count` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of new players associated with the batch period | Unit is players; inclusion logic, measurement window, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |
| `active_player_count_end` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of active players at the end of the batch period | Unit is players; the active-player definition, calculation, timing boundary, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |
| `match_count_generated` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of matches associated with or generated for the batch period | Unit is matches; generation logic, inclusion criteria, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |
| `rating_update_count` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of rating updates associated with the batch period | Unit is rating updates; update definition, inclusion criteria, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |
| `assessment_update_count` | `INT64` (source count) | Optional under prescribed contract | None specified | Source count of assessment updates associated with the batch period | Unit is assessment updates; update definition, inclusion criteria, and valid range are unresolved | Prescribed | Appendix A ordered columns and source count type-family statement |

## Bronze Metadata and Operational Evidence

Reserved for the prescribed Bronze metadata columns and operational evidence structures. A later stage will document their definitions and verification status without duplicating the full Raw-to-Bronze construction prompt.

## Silver Entities and Field Definitions

Reserved for prescribed Silver accepted entities, standardized fields, derived fields, source preservation, transformations, and joins. A later stage will reference the Silver construction prompt and deployed-schema evidence rather than treating expected projections as physically verified.

## Silver Exceptions and Operational Structures

Reserved for the prescribed exception-table contract, quality evidence, reconciliation, schema snapshots, and run metadata. A later stage will distinguish specification from executed pipeline evidence.

## Gold Analytical Definitions — Team Maintained

Reserved for consulting-team definitions of Gold features, metrics, measures, analytical outputs, and their Silver lineage. Gold design remains team-controlled; no Gold fields or methods are prescribed here.

## Open Questions and Definition Decisions

Record ambiguous business meanings, profile differences, evidence gaps, and interpretation decisions here as the dictionary is expanded. Keep unresolved items visible until an authoritative source or approved team decision resolves them.
