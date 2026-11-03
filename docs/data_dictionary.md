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

## Bronze Entity and Metadata Contracts

The Raw-to-Bronze construction prompt is authoritative for this section. These entries describe the prescribed contract; they do not establish that a team's generated Bronze tables have been physically or implementation verified. The contract applies independently to all five dataset profiles.

### Common business-field preservation contract

For every entity below, Bronze retains every delivered Parquet business column in its original order and appends the ten metadata columns listed in the next section. Bronze does not rename source fields, change their stored types or representations, standardize values, cleanse, filter, join, sort, deduplicate, or derive business features. Nulls, invalid business values, relationships, and duplicate rows remain as delivered. Casts used to calculate `_source_record_hash` apply only inside that expression and do not change stored business columns.

The existing [Source Field Dictionary](#source-field-dictionary) records the prescribed source contracts without repeating all 112 definitions here. The delivered Parquet schemas and manifest remain the physical evidence for actual column names, order, types, and nullability. Any difference between that evidence and the prescribed source dictionary must be recorded rather than silently normalized in Bronze. `manifest.json` is validation evidence and is not a Bronze entity.

### Bronze entity coverage

| Build order | Raw source and source-dictionary reference | Corresponding Bronze entity | Prescribed business-field handling | Verification status |
|---:|---|---|---|---|
| 10 | `regions.parquet` — [`regions`](#regions) | `regions` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 20 | `clubs.parquet` — [`clubs`](#clubs) | `clubs` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 30 | `club_memberships.parquet` — [`club_memberships`](#club_memberships) | `club_memberships` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 40 | `player_master.parquet` — [`player_master`](#player_master) | `player_master` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 50 | `player_registrations.parquet` — [`player_registrations`](#player_registrations) | `player_registrations` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 60 | `player_assessment_history.parquet` — [`player_assessment_history`](#player_assessment_history) | `player_assessment_history` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 70 | `teams.parquet` — [`teams`](#teams) | `teams` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 80 | `team_memberships.parquet` — [`team_memberships`](#team_memberships) | `team_memberships` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 90 | `matches.parquet` — [`matches`](#matches) | `matches` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 100 | `match_teams.parquet` — [`match_teams`](#match_teams) | `match_teams` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 110 | `match_team_players.parquet` — [`match_team_players`](#match_team_players) | `match_team_players` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 120 | `match_games.parquet` — [`match_games`](#match_games) | `match_games` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |
| 130 | `monthly_batches.parquet` — [`monthly_batches`](#monthly_batches) | `monthly_batches` | Apply the common preservation contract; no field rename, stored-type change, or removal is prescribed | Prescribed |

### Required Bronze metadata fields

All ten columns are mandatory on every Bronze entity and are appended after the original business columns in the order shown. A source collision with any reserved metadata name is a construction failure. “Required column” below does not assert `NOT NULL` unless the prompt explicitly establishes value nullability.

| Order | Field name | Intended meaning | Applicable Bronze entities | Required or optional status | Prescribed type or representation | Verification status |
|---:|---|---|---|---|---|---|
| 1 | `_pipeline_run_id` | UUID identifying the shared Raw-to-Bronze workflow run | All 13 | Required column; physical nullability unresolved | UUID value from the shared run context; exact Spark type unresolved | Prescribed |
| 2 | `_pipeline_name` | Configured pipeline name that produced the row | All 13 | Required column; physical nullability unresolved | Configured value; exact Spark type unresolved | Prescribed |
| 3 | `_pipeline_version` | Configured version of the producing pipeline | All 13 | Required column; physical nullability unresolved | Configured value; exact Spark type unresolved | Prescribed |
| 4 | `_release_name` | Selected configured dataset release/profile context | All 13 | Required column; physical nullability unresolved | Shared run-context value; exact Spark type unresolved | Prescribed |
| 5 | `_source_file_name` | Name of the Parquet file from which the row was read | All 13 | Required column; physical nullability unresolved | File-readiness value; exact Spark type unresolved | Prescribed |
| 6 | `_source_file_path` | Actual source path used for the Parquet read, including a `dbfs:` prefix when present | All 13 | Required column; physical nullability unresolved | File-readiness value; exact Spark type unresolved | Prescribed |
| 7 | `_source_file_size` | Available size of the source Parquet file | All 13 | Required column; value may be unavailable; exact nullability handling unresolved | File-readiness value; physical units and exact Spark type are not explicitly prescribed | Prescribed |
| 8 | `_source_file_modification_ts` | Available source-file modification time normalized to UTC | All 13 | Required column; missing modification times remain null | UTC-aware timestamp concept; exact Spark type unresolved | Prescribed |
| 9 | `_ingested_ts` | Bronze table's UTC ingestion start time | All 13 | Required column; the workflow supplies a value; physical nullability unresolved | UTC-aware timestamp concept; exact Spark type unresolved | Prescribed |
| 10 | `_source_record_hash` | SHA-256 fingerprint calculated from all original source columns in source order | All 13 | Required column; physical nullability unresolved | Cast each source value to string only inside the hash expression, replace null with `__NULL__`, join with `||`, and apply SHA-256; exact Spark type unresolved | Prescribed |

The record hash preserves duplicate rows and is not a guaranteed unique key because the encoding does not escape the delimiter or null sentinel. No metadata field has been marked **Physically verified**; verification requires inspection of implemented Bronze tables and execution evidence.

### Documentation boundary and unresolved physical details

This section does not define the separate Raw-to-Bronze operations tables (`pipeline_runs`, `table_runs`, `schema_snapshots`, `reconciliation_results`, or `run_messages`), their run evidence, rejection behavior, acceptance SQL, or job steps. Those operational evidence structures are reserved for a separate task.

The construction prompt does not prescribe exact Spark physical types for the ten Bronze metadata columns or comprehensive `NOT NULL` constraints. It explicitly permits a missing source-file modification timestamp to remain null and describes source-file size as captured when available, but does not fully specify size units or fallback/null handling. These details remain **Unresolved** until clarified by an authoritative specification or physically verified implementation evidence.

## Bronze Operational Evidence Contracts

The Raw-to-Bronze construction prompt prescribes five managed Delta evidence tables in the configured operations schema. The exact deployed catalog and schema are team-configured and have not been physically verified. All entries below are **Prescribed** unless stated otherwise; no primary keys, foreign keys, retention periods, or additional constraints are implied beyond the prompt's exact type and nullability contract. In the field tables, “Required” means the prompt marks the column `NOT NULL`; “Nullable” means it does not.

### Evidence structure inventory

| Prescribed structure | Purpose and record grain | Identifying fields and relationships | Field count | Verification status |
|---|---|---|---:|---|
| `pipeline_runs` | Pipeline-run lifecycle evidence; normally one open run record is finalized, with a terminal fallback record possible when no open record exists | `pipeline_run_id` identifies the workflow run and relates it to every other operations table; no primary-key constraint is prescribed | 14 | Prescribed |
| `table_runs` | Per-source Bronze build-state evidence; separate `RUNNING` and terminal records are appended for each source table | Relates a run, release, source file/entity, and Bronze target through `pipeline_run_id`, `release_name`, `source_file_name`, `source_table`, and `target_table`; no primary key is prescribed | 17 | Prescribed |
| `schema_snapshots` | One captured field definition per run, layer, and Raw or Bronze object | Relates schema evidence to a run and release; Raw `object_name` is the source filename and Bronze `object_name` is the unqualified Bronze table name | 11 | Prescribed |
| `reconciliation_results` | One Raw-to-Bronze reconciliation result per source/target for a pipeline run | Relates a run and release to `source_file_name` and `bronze_table`; no primary key is prescribed | 13 | Prescribed |
| `run_messages` | One diagnostic message event associated with a run and optionally a source | Relates messages to `pipeline_run_id`, `release_name`, and optional `source_name`; no primary key is prescribed | 8 | Prescribed |

### `pipeline_runs` fields

| Order | Field name | Prescribed type | Nullability | Meaning | Verification status |
|---:|---|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Required | UUID identifying the Raw-to-Bronze workflow run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Required | Configured pipeline name | Prescribed |
| 3 | `pipeline_version` | `STRING` | Required | Configured pipeline version | Prescribed |
| 4 | `release_name` | `STRING` | Required | Configured release processed by the run | Prescribed |
| 5 | `processing_mode` | `STRING` | Required | Processing mode used by the run | Prescribed |
| 6 | `configuration_hash` | `STRING` | Required | Reproducible hash of the resolved configuration | Prescribed |
| 7 | `workflow_run_id` | `STRING` | Nullable | Trustworthy external workflow-run identifier when available | Prescribed |
| 8 | `status` | `STRING` | Required | Pipeline lifecycle or terminal status | Prescribed |
| 9 | `started_ts` | `TIMESTAMP` | Required | UTC-normalized pipeline start timestamp | Prescribed |
| 10 | `completed_ts` | `TIMESTAMP` | Nullable | UTC-normalized pipeline completion timestamp | Prescribed |
| 11 | `duration_seconds` | `DOUBLE` | Nullable | Elapsed run duration in seconds | Prescribed |
| 12 | `triggered_by` | `STRING` | Nullable | Trustworthy trigger identity or context when available | Prescribed |
| 13 | `error_class` | `STRING` | Nullable | Error classification for a failed run | Prescribed |
| 14 | `error_message` | `STRING` | Nullable | Run-level error summary | Prescribed |

### `table_runs` fields

| Order | Field name | Prescribed type | Nullability | Meaning | Verification status |
|---:|---|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Required | Identifier of the parent pipeline run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Required | Configured pipeline name | Prescribed |
| 3 | `release_name` | `STRING` | Required | Configured release processed | Prescribed |
| 4 | `source_file_name` | `STRING` | Required | Raw Parquet filename | Prescribed |
| 5 | `source_table` | `STRING` | Required | Configured source entity name | Prescribed |
| 6 | `target_table` | `STRING` | Required | Corresponding Bronze target table | Prescribed |
| 7 | `status` | `STRING` | Required | Build-state status for this appended record | Prescribed |
| 8 | `started_ts` | `TIMESTAMP` | Required | UTC-normalized table-build start timestamp | Prescribed |
| 9 | `completed_ts` | `TIMESTAMP` | Nullable | UTC-normalized terminal timestamp; null on the appended start record | Prescribed |
| 10 | `duration_seconds` | `DOUBLE` | Nullable | Elapsed table-build duration in seconds | Prescribed |
| 11 | `source_file_size` | `BIGINT` | Nullable | Available source-file size | Prescribed |
| 12 | `source_row_count` | `BIGINT` | Nullable | Count of Raw source rows | Prescribed |
| 13 | `bronze_row_count` | `BIGINT` | Nullable | Count of Bronze rows captured during construction | Prescribed |
| 14 | `row_count_difference` | `BIGINT` | Nullable | Bronze row count minus Raw row count | Prescribed |
| 15 | `source_schema_hash` | `STRING` | Nullable | Hash of the ordered Raw source schema | Prescribed |
| 16 | `bronze_schema_hash` | `STRING` | Nullable | Hash of the ordered Bronze schema | Prescribed |
| 17 | `error_message` | `STRING` | Nullable | Source-table build error summary | Prescribed |

### `schema_snapshots` fields

| Order | Field name | Prescribed type | Nullability | Meaning | Verification status |
|---:|---|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Required | Identifier of the parent pipeline run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Required | Configured pipeline name | Prescribed |
| 3 | `release_name` | `STRING` | Required | Configured release represented by the snapshot | Prescribed |
| 4 | `layer_name` | `STRING` | Required | Layer represented by the snapshot, such as Raw or Bronze | Prescribed |
| 5 | `object_name` | `STRING` | Required | Raw source filename or unqualified Bronze table name, according to layer | Prescribed |
| 6 | `column_name` | `STRING` | Required | Captured field name | Prescribed |
| 7 | `data_type` | `STRING` | Required | Captured Spark `simpleString()` field type | Prescribed |
| 8 | `nullable` | `BOOLEAN` | Nullable | Captured source or table field-nullability value | Prescribed |
| 9 | `ordinal_position` | `INT` | Nullable | One-based field position in the captured schema | Prescribed |
| 10 | `schema_hash` | `STRING` | Required | Hash representing the full ordered schema | Prescribed |
| 11 | `captured_ts` | `TIMESTAMP` | Required | Timestamp when schema evidence was captured | Prescribed |

### `reconciliation_results` fields

| Order | Field name | Prescribed type | Nullability | Meaning | Verification status |
|---:|---|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Required | Identifier of the parent pipeline run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Required | Configured pipeline name | Prescribed |
| 3 | `release_name` | `STRING` | Required | Configured release reconciled | Prescribed |
| 4 | `source_file_name` | `STRING` | Required | Raw Parquet filename reconciled | Prescribed |
| 5 | `bronze_table` | `STRING` | Required | Corresponding Bronze table | Prescribed |
| 6 | `raw_row_count` | `BIGINT` | Required | Persisted Raw row count used for reconciliation | Prescribed |
| 7 | `bronze_row_count` | `BIGINT` | Required | Persisted Bronze row count used for reconciliation | Prescribed |
| 8 | `row_count_difference` | `BIGINT` | Required | Bronze row count minus Raw row count | Prescribed |
| 9 | `raw_business_column_count` | `INT` | Required | Number of Raw business columns | Prescribed |
| 10 | `bronze_business_column_count` | `INT` | Required | Number of Bronze business columns, excluding appended metadata | Prescribed |
| 11 | `metadata_column_count` | `INT` | Required | Number of appended Bronze metadata columns | Prescribed |
| 12 | `status` | `STRING` | Required | Reconciliation result status | Prescribed |
| 13 | `evaluated_ts` | `TIMESTAMP` | Required | Timestamp when reconciliation was evaluated | Prescribed |

### `run_messages` fields

| Order | Field name | Prescribed type | Nullability | Meaning | Verification status |
|---:|---|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Required | Identifier of the related pipeline run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Required | Configured pipeline name | Prescribed |
| 3 | `release_name` | `STRING` | Required | Configured release associated with the message | Prescribed |
| 4 | `source_name` | `STRING` | Nullable | Source entity associated with the message, when applicable | Prescribed |
| 5 | `message_level` | `STRING` | Required | Diagnostic message severity or level | Prescribed |
| 6 | `message_code` | `STRING` | Required | Diagnostic message code | Prescribed |
| 7 | `message_text` | `STRING` | Required | Human-readable diagnostic text | Prescribed |
| 8 | `created_ts` | `TIMESTAMP` | Required | Timestamp when the message was created | Prescribed |

### Other prescribed evidence channels

| Evidence channel or concept | Prescribed content | Physical contract status | Verification status |
|---|---|---|---|
| Manifest and Raw-readiness comparison evidence | Expected and actual manifest values, mismatch type, source file, selected dataset profile, release identifier, and pipeline-run identifier | No additional table name, exact field names, types, nullability, or storage representation are prescribed; these details are **Unresolved** | Prescribed concept; physical representation Unresolved |
| Bronze table catalog metadata | A Raw-preserving table comment plus `napa.layer=bronze`, `napa.release=<release>`, `napa.pipeline=raw_to_bronze`, and `napa.processing_mode=full_refresh` properties on each Bronze Delta table | Comment template and property names/values are prescribed; deployed catalog representation and verification remain unresolved | Prescribed; not physically verified |
| Databricks task values | Runtime handoff and diagnostics using `run_id`, `pipeline_run_id`, `release_name`, `config_hash`, `catalog`, `raw_schema`, `bronze_schema`, `source_path`, `operations_schema_fqn`, `bronze_table_count`, `reconciled_source_count`, and `final_status`, as applicable | Keys are prescribed, but physical types, durability, retention, and table representation are not prescribed | Prescribed concept; physical representation Unresolved |
| Job-log failure diagnostics | Root-cause traceback and available failure diagnostics, including publication or cleanup failures | Platform log schema, field names, types, storage, and retention are not prescribed | Prescribed concept; physical representation Unresolved |

Raw-to-Bronze prescribes no rejected-record or defect-row table: Bronze preserves all source rows and does not apply business-rule rejection. Technical validation and publication defects are represented through statuses, error fields, run messages, the required but physically unresolved validation evidence, and job logs where available. This dictionary describes evidence structure only; `docs/raw_to_bronze_prompt.md` remains authoritative for validation rules, diagnostic codes, failure behavior, execution steps, job topology, and acceptance checks.

## Silver Entities and Field Definitions

The Bronze-to-Silver construction prompt is authoritative for this section. Appendix B supplies the ordered accepted-table projections, and Stages 4–8 establish field origin and meaning. These are **Prescribed** contracts, not physically or implementation-verified schemas. They apply independently to all five dataset profiles.

Appendix B requires every accepted table to contain its ordered business fields followed by the seven shared metadata fields documented below. The prompt states broad type families but requires integration schema tests for exact Spark types and nullability. Accordingly, “required accepted value” describes logical acceptance behavior, not a claimed physical `NOT NULL` constraint; all unprovided physical nullability remains **Unresolved**.

### Accepted Silver entity inventory

| Registry order | Accepted target | Record grain | Bronze source and prescribed enrichment dependencies | Prescribed primary key | Business fields | Total fields including 7 metadata | Status |
|---:|---|---|---|---|---:|---:|---|
| 10 | `monthly_batches` | One accepted monthly batch or snapshot period | `monthly_batches` | `batch_id` | 15 | 22 | Prescribed |
| 20 | `regions` | One accepted geographic region | `regions` | `region_id` | 10 | 17 | Prescribed |
| 30 | `players` | One accepted current or snapshot player | `player_master`; accepted `regions` for optional home-region enrichment | `player_id` | 27 | 34 | Prescribed |
| 40 | `clubs` | One accepted club or facility | `clubs`; accepted `regions` | `club_id` | 14 | 21 | Prescribed |
| 50 | `teams` | One accepted persistent doubles team | `teams` | `team_id` | 12 | 19 | Prescribed |
| 60 | `player_registrations` | One accepted player registration event | `player_registrations`; accepted `players`, `monthly_batches`, and optional `regions` | `registration_id` | 20 | 27 | Prescribed |
| 70 | `player_assessment_history` | One accepted player assessment | `player_assessment_history`; accepted `players` and `monthly_batches` | `assessment_id` | 12 | 19 | Prescribed |
| 80 | `club_memberships` | One accepted player-club membership period | `club_memberships`; accepted `players` and `clubs` | `club_membership_id` | 15 | 22 | Prescribed |
| 90 | `team_memberships` | One accepted player-team membership period | `team_memberships`; accepted `teams` and `players` | `team_membership_id` | 15 | 22 | Prescribed |
| 100 | `matches` | One accepted match | `matches`; accepted `monthly_batches`, optional `regions`, and Bronze `match_teams` for winner-side mapping | `match_id` | 17 | 24 | Prescribed |
| 110 | `match_teams` | One accepted participating match side | `match_teams`; accepted `matches` and `teams` | `match_team_id` | 15 | 22 | Prescribed |
| 120 | `match_team_players` | One accepted player participation on a match side | `match_team_players`; accepted `match_teams`, `players`, inherited match/team context, and team-membership history for warning evidence | `match_team_player_id` | 16 | 23 | Prescribed |
| 130 | `match_games` | One accepted game within a match | `match_games`; accepted `matches` | `match_game_id` | 15 | 22 | Prescribed |

The inventory contains 203 ordered business-field occurrences and 91 shared-metadata occurrences, for 294 physical field occurrences across the 13 accepted tables.

### Field-origin and type conventions

- **Source/standardized:** carried from the corresponding Bronze business attribute through a documented canonical rename, alias, normalization, or safe conversion. It is not a Gold feature.
- **Lookup:** obtained from an accepted parent or a prescribed enrichment source. Foreign surrogate keys are obtained from accepted parents.
- **Surrogate:** SHA-256 of the table's valid natural key for the entity's own `_sk` field.
- **Derived:** explicitly calculated by the Silver prompt. Fields whose names begin `derived_` are derived business attributes.
- **Quality:** a non-rejecting `dq_` indicator required by the prompt.
- **Metadata:** one of the seven shared accepted-row operational fields.

Natural and foreign identifiers and surrogate keys are `STRING`; typed dates are `DATE`; flags are `BOOLEAN`; ratings, confidence values, assessment values, and score shares are `DOUBLE`; and date parts, sequences, scores, durations, ages, and count-derived values use corresponding SQL integer types. Exact integer widths, other physical types, precision, and physical nullability are unresolved unless the prompt explicitly states otherwise.

### Shared accepted-row metadata — all 13 tables

These seven fields follow each table's ordered business fields. Their exact physical nullability and, except where a type family is explicit, physical types require implementation verification.

| Order after business fields | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / role | Status |
|---:|---|---|---|---|---|---|---|
| 1 | `_pipeline_run_id` | Metadata | Current Silver pipeline run | Run-level traceability | Identifier (`STRING`) | Required column; physical nullability unresolved | Prescribed |
| 2 | `_pipeline_version` | Metadata | Current Silver pipeline version | Producing pipeline version | Unresolved | Required column; physical nullability unresolved | Prescribed |
| 3 | `_source_dataset` | Metadata | Selected release name | Dataset/release provenance | Unresolved | Required column; physical nullability unresolved | Prescribed |
| 4 | `_source_table` | Metadata | Bronze source name; `player_master` for `players` | Source-entity provenance | Unresolved | Required column; physical nullability unresolved | Prescribed |
| 5 | `_load_ts` | Metadata | Silver load timestamp | Publication-time traceability | Timestamp concept; exact type unresolved | Required column; physical nullability unresolved | Prescribed |
| 6 | `_record_hash` | Metadata | SHA-256 over the table-specific ordered hash inputs in Stage 4 | Accepted-record comparison fingerprint | Unresolved | Required column; not proof that every attribute is unchanged | Prescribed |
| 7 | `_data_quality_status` | Metadata | Constant `ACCEPTED` for accepted rows | Accepted-row disposition | Unresolved categorical type | Required column; remains `ACCEPTED` when separate warning flags are true | Prescribed |

### `monthly_batches` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `batch_id` | Source/standardized | `monthly_batches.id` (fallback alias supported) | Canonical batch identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `batch_sk` | Surrogate | SHA-256 of `batch_id` | Stable batch surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `batch_month` | Source/standardized | `batch_month` | Published batch month attribute | Source representation; exact Silver type unresolved | Required source value; physical nullability unresolved | None | Prescribed |
| 4 | `batch_sequence` | Source/standardized | `batch_sequence` | Batch sequence value | SQL integer family | Required accepted value | None | Prescribed |
| 5 | `batch_type` | Source/standardized | Uppercased `batch_type` | Batch classification | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 6 | `active_player_count_start` | Source/standardized | `active_player_count_start` | Source active-player count at period start | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 7 | `new_player_count` | Source/standardized | `new_player_count` | Source new-player count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 8 | `active_player_count_end` | Source/standardized | `active_player_count_end` | Source active-player count at period end | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 9 | `match_count_generated` | Source/standardized | `match_count_generated` | Source generated-match count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 10 | `rating_update_count` | Source/standardized | `rating_update_count` | Source rating-update count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 11 | `assessment_update_count` | Source/standardized | `assessment_update_count` | Source assessment-update count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 12 | `derived_batch_date` | Derived | Parsed batch date from the supported date/month source | Canonical batch-period date | `DATE` | Expected for accepted rows; physical nullability unresolved | Derived field | Prescribed |
| 13 | `derived_batch_year` | Derived | Year from `derived_batch_date` | Batch year | SQL integer family | Depends on valid derived batch date | Derived field | Prescribed |
| 14 | `derived_batch_month` | Derived | Month from `derived_batch_date` | Batch month number | SQL integer family | Depends on valid derived batch date | Derived field | Prescribed |
| 15 | `derived_batch_quarter` | Derived | Quarter from `derived_batch_date` | Batch quarter number | SQL integer family | Depends on valid derived batch date | Derived field | Prescribed |

### `regions` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `region_id` | Source/standardized | `regions.id` (supported canonical aliases) | Canonical region identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `region_sk` | Surrogate | SHA-256 of `region_id` | Stable region surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `country_code` | Source/standardized | Normalized source country | Canonical USA/CAN country code | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 4 | `region_type` | Source/standardized | `region_type` | Source region classification | Exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 5 | `region_name` | Source/standardized | `region_name` (supported name alias) | Region name | Exact type unresolved | Required accepted value | None | Prescribed |
| 6 | `state_province_code` | Source/standardized | Preserved `state_province_code` | Original state/province code attribute | Exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 7 | `province_state` | Source/standardized | Supported province/state aliases; canonical mapping must be documented | Canonical province/state attribute | Exact type unresolved | Source availability and exact schema 1.6 mapping unresolved | None | Prescribed |
| 8 | `population` | Source/standardized | `population` | Source population value | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 9 | `latitude` | Source/standardized | `latitude` | Source latitude measurement | Numeric measurement; exact Silver type unresolved | Nullable when source contract permits | None | Prescribed |
| 10 | `longitude` | Source/standardized | `longitude` | Source longitude measurement | Numeric measurement; exact Silver type unresolved | Nullable when source contract permits | None | Prescribed |

### `players` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `player_id` | Source/standardized | `player_master.player_id` (preferred canonical ID) | Canonical player identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `player_sk` | Surrogate | SHA-256 of `player_id` | Stable player surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `external_player_key` | Source/standardized | `external_player_key` | External player UUID text | `STRING` | Required source value | Alternate source identifier | Prescribed |
| 4 | `first_name` | Source/standardized | Trimmed `first_name` | Player first name | Exact type unresolved | Required source value | None | Prescribed |
| 5 | `last_name` | Source/standardized | Trimmed `last_name` | Player last name | Exact type unresolved | Required source value | None | Prescribed |
| 6 | `display_name` | Source/standardized | Supplied display/full name when present; otherwise available first/last names | Canonical player display name | Exact type unresolved | Exact physical nullability unresolved | Canonical presentation field | Prescribed |
| 7 | `gender` | Source/standardized | Normalized `gender` | Player gender domain value | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 8 | `birth_date` | Source/standardized | Safely parsed `birth_date` | Player birth date | `DATE` | Required accepted value | None | Prescribed |
| 9 | `dominant_hand` | Source/standardized | Normalized `dominant_hand` | Player dominant-hand value | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 10 | `home_region_id` | Source/standardized | `home_region_id` | Optional home-region identifier | `STRING` | Nullable optional reference | Foreign identifier to `regions.region_id` | Prescribed |
| 11 | `home_region_sk` | Lookup | Surrogate key from accepted home region | Accepted home-region surrogate | `STRING` | Nullable when `home_region_id` is null | Foreign surrogate to `regions.region_sk` | Prescribed |
| 12 | `country_code` | Source/lookup | Normalized supplied country; accepted region fallback only when permitted and source is absent | Canonical player country | Categorical; exact type unresolved | Exact physical nullability unresolved | Optional region enrichment | Prescribed |
| 13 | `registration_date` | Source/standardized | Safely parsed `registration_date` | Player registration date | `DATE` | Required accepted value | None | Prescribed |
| 14 | `player_status` | Source/standardized | Normalized `player_status` | Player source status | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 15 | `rating` | Source/standardized | Preserved source `rating` compatibility attribute | Source rating value | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 16 | `rating_value` | Source/standardized | Preserved and safely converted `rating_value` | Canonical source rating value | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 17 | `confidence_score` | Source/standardized | Preserved and safely converted `confidence_score` | Source rating-confidence measurement | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 18 | `rating_confidence` | Source/standardized | Canonical confidence from supported confidence aliases | Canonical rating-confidence measurement | `DOUBLE` | Nullable when no supported value is supplied | None | Prescribed |
| 19 | `volatility_score` | Source/standardized | `volatility_score` | Source rating-volatility measurement | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 20 | `global_percentile` | Source/standardized | `global_percentile` | Source global-percentile measurement | Numeric measurement; exact Silver type unresolved | Nullable when source contract permits | None | Prescribed |
| 21 | `match_count_used` | Source/standardized | `match_count_used` | Source count of matches used for rating | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 22 | `rating_date` | Source/standardized | Safely parsed `rating_date` | Source rating effective date | `DATE` | Nullable when source contract permits | None | Prescribed |
| 23 | `rating_batch_id` | Source/standardized | `rating_batch_id` | Source batch reference associated with rating | `STRING` | Nullable when source contract permits | Relationship semantics beyond preservation unresolved | Prescribed |
| 24 | `snapshot_month` | Source/standardized | Parsed `snapshot_month` | Player snapshot month | `DATE` (month-level) | Required accepted value | Snapshot context | Prescribed |
| 25 | `derived_active_flag` | Derived | Normalized status/active semantics | Current player active indicator | `BOOLEAN` | May be null for unsupported or absent status semantics | Derived field | Prescribed |
| 26 | `derived_age_at_snapshot` | Derived | Birth date evaluated at manifest snapshot date | Player age at snapshot | SQL integer family | Depends on valid birth and snapshot dates | Derived field | Prescribed |
| 27 | `derived_age_group_at_snapshot` | Derived | Configured age group for `derived_age_at_snapshot` | Player age group at snapshot | Categorical; exact type unresolved | Depends on derived age | Derived field | Prescribed |

### `player_registrations` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `registration_id` | Source/standardized | `player_registrations.id` (supported canonical alias) | Canonical registration identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `registration_sk` | Surrogate | SHA-256 of `registration_id` | Stable registration surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `player_id` | Source/standardized | Required source `player_id` | Registered player identifier | `STRING` | Required accepted reference | Foreign identifier to `players.player_id` | Prescribed |
| 4 | `player_sk` | Lookup | Surrogate key from accepted player | Registered player surrogate | `STRING` | Required when registration is accepted | Foreign surrogate to `players.player_sk` | Prescribed |
| 5 | `batch_id` | Source/standardized | Required physical `batch_id`; compatibility alias cannot conceal absence/null | Registration batch identifier | `STRING` | Required accepted reference | Foreign identifier to `monthly_batches.batch_id` | Prescribed |
| 6 | `batch_sk` | Lookup | Surrogate key from accepted batch | Registration batch surrogate | `STRING` | Required when registration is accepted | Foreign surrogate to `monthly_batches.batch_sk` | Prescribed |
| 7 | `registration_month` | Source/standardized | Preserved `registration_month` | Source registration month | Source month representation; exact Silver type unresolved | Required source value | None | Prescribed |
| 8 | `registration_source` | Source/standardized | Preserved and normalized `registration_source` | Source registration channel/type attribute | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 9 | `assigned_region_id` | Source/standardized | Preserved `assigned_region_id` | Optional assigned-region identifier | `STRING` | Nullable optional reference | Foreign identifier to `regions.region_id` | Prescribed |
| 10 | `assigned_region_sk` | Lookup | Surrogate key from accepted assigned region | Assigned-region surrogate | `STRING` | Nullable when `assigned_region_id` is null | Foreign surrogate to `regions.region_sk` | Prescribed |
| 11 | `initial_rating_value` | Source/standardized | Safely converted `initial_rating_value` | Initial registration rating | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 12 | `initial_confidence_score` | Source/standardized | Safely converted `initial_confidence_score` | Initial rating-confidence value | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 13 | `registration_date` | Source/standardized | Supported registration date; otherwise valid `registration_month` | Canonical registration date | `DATE` | Expected for accepted rows under required month contract | None | Prescribed |
| 14 | `registration_type` | Source/standardized | Normalized supported registration type/source | Canonical registration classification | Categorical; exact type unresolved | May be null when optional source classification is absent | None | Prescribed |
| 15 | `effective_start_date` | Source/standardized | Supported effective/start date; otherwise `registration_month` | Registration effective-start date | `DATE` | Expected from required registration month unless a supported value is invalid | None | Prescribed |
| 16 | `effective_end_date` | Source/standardized | Optional supported effective-end date | Registration effective-end date | `DATE` | Nullable optional value | None | Prescribed |
| 17 | `derived_registration_status` | Derived | Status from effective interval and prescribed comparison date | Derived registration status | Categorical; exact type unresolved | May be null when required comparison inputs are unavailable | Derived field | Prescribed |
| 18 | `derived_current_registration_flag` | Derived | Current-state evaluation of registration interval | Current registration indicator | `BOOLEAN` | May be null when comparison date is unavailable | Derived field | Prescribed |
| 19 | `derived_registration_duration_days` | Derived | Snapshot date minus effective start date | Registration duration in days | SQL integer family | Depends on effective start and snapshot dates | Derived field | Prescribed |
| 20 | `derived_registration_sequence` | Derived | Per-player ordered registration row number | Registration sequence for a player | SQL integer family; window value may be `BIGINT` | Expected for accepted rows; exact width unresolved | Derived field | Prescribed |

### `player_assessment_history` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `assessment_id` | Source/standardized | `player_assessment_history.id` (supported canonical alias) | Canonical assessment identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `assessment_sk` | Surrogate | SHA-256 of `assessment_id` | Stable assessment surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `player_id` | Source/standardized | Required source `player_id` | Assessed player identifier | `STRING` | Required accepted reference | Foreign identifier to `players.player_id` | Prescribed |
| 4 | `player_sk` | Lookup | Surrogate key from accepted player | Assessed player surrogate | `STRING` | Required when assessment is accepted | Foreign surrogate to `players.player_sk` | Prescribed |
| 5 | `batch_id` | Source/standardized | Required source `batch_id` with supported compatibility alias | Assessment batch identifier | `STRING` | Required accepted reference | Foreign identifier to `monthly_batches.batch_id` | Prescribed |
| 6 | `batch_sk` | Lookup | Surrogate key from accepted batch | Assessment batch surrogate | `STRING` | Required when assessment is accepted | Foreign surrogate to `monthly_batches.batch_sk` | Prescribed |
| 7 | `assessment_date` | Source/standardized | Safely parsed assessment date from supported date/month fields | Assessment event date | `DATE` | Required accepted value | Event-time field | Prescribed |
| 8 | `assessment_type` | Source/standardized | Uppercased `assessment_type` | Assessment classification | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 9 | `assessment_value` | Source/standardized | Safely converted `assessment_value` | Assessment measurement | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 10 | `confidence_score` | Source/standardized | Preserved and safely converted source `confidence_score` | Source assessment-confidence measurement | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 11 | `assessment_confidence` | Source/standardized | Canonical confidence from supported confidence aliases | Canonical assessment-confidence measurement | `DOUBLE` | Column required by Silver contract; value may be null when source permits | None | Prescribed |
| 12 | `derived_from_matches` | Source/standardized | Preserved source `derived_from_matches` | Source indicator describing assessment provenance | Exact type unresolved | Nullable when source contract permits | Source attribute despite its name | Prescribed |

### `clubs` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `club_id` | Source/standardized | `clubs.id` (supported canonical alias) | Canonical club identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `club_sk` | Surrogate | SHA-256 of `club_id` | Stable club surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `club_name` | Source/standardized | `club_name` (supported name alias) | Club or facility name | Exact type unresolved | Required accepted value | None | Prescribed |
| 4 | `region_id` | Source/standardized | Required source `region_id` | Club region identifier | `STRING` | Required accepted reference | Foreign identifier to `regions.region_id` | Prescribed |
| 5 | `region_sk` | Lookup | Surrogate key from accepted region | Club region surrogate | `STRING` | Required when club is accepted | Foreign surrogate to `regions.region_sk` | Prescribed |
| 6 | `country_code` | Lookup/standardized | Normalized supplied country when available; accepted region fallback only when permitted | Canonical club country | Categorical; exact type unresolved | Exact physical nullability unresolved | Region enrichment | Prescribed |
| 7 | `club_type` | Source/standardized | Preserved `club_type` | Source club classification | Exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 8 | `competitiveness_level` | Source/standardized | Preserved `competitiveness_level` | Source competitiveness classification | Exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 9 | `member_capacity` | Source/standardized | Preserved `member_capacity` | Source membership capacity | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 10 | `founding_date` | Source/standardized | Safely parsed and preserved `founding_date` | Source founding date | `DATE` | Nullable when source contract permits | None | Prescribed |
| 11 | `indoor_court_count` | Source/standardized | Preserved `indoor_court_count` | Indoor court count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 12 | `outdoor_court_count` | Source/standardized | Preserved `outdoor_court_count` | Outdoor court count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 13 | `open_date` | Source/standardized | Supported open/start/formation date, otherwise founding date | Canonical club opening date | `DATE` | Nullable when no supported value is supplied | None | Prescribed |
| 14 | `close_date` | Source/standardized | Optional supported close/end/dissolution date | Canonical club closing date | `DATE` | Nullable optional value | None | Prescribed |

### `teams` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `team_id` | Source/standardized | `teams.id` (supported canonical alias) | Canonical persistent-team identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `team_sk` | Surrogate | SHA-256 of `team_id` | Stable team surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `team_type` | Source/standardized | Preserved `team_type` | Source team identity/category attribute | Categorical; exact type unresolved | Required source value | None | Prescribed |
| 4 | `team_division` | Source/standardized | Preserved `team_division` | Source team division attribute | Categorical; exact type unresolved | Required source value | None | Prescribed |
| 5 | `team_category` | Source/standardized | Canonical category from prescribed division/category/type precedence | Standardized doubles category | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 6 | `team_identity_type` | Source/standardized | Canonical COMPETITIVE/AD_HOC identity from modern `team_type`; legacy category may yield null | Standardized persistent-team identity | Categorical; exact type unresolved | May be null for supported legacy category semantics | None | Prescribed |
| 7 | `country_code` | Source/standardized | Normalized `country_code` | Team country | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 8 | `team_status` | Source/standardized | Normalized `team_status` | Team lifecycle status | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 9 | `formation_date` | Source/standardized | Safely parsed formation/start date | Team formation date | `DATE` | Required accepted value | None | Prescribed |
| 10 | `dissolution_date` | Source/standardized | Safely parsed optional dissolution/end date | Team dissolution date | `DATE` | Nullable optional value | None | Prescribed |
| 11 | `derived_active_flag` | Derived | Prescribed active/status semantics | Current team active indicator | `BOOLEAN` | May be null when status/active input is absent | Derived field | Prescribed |
| 12 | `derived_team_age_at_snapshot_days` | Derived | Snapshot date minus formation date | Team age at snapshot in days | SQL integer family | Depends on valid formation and snapshot dates | Derived field | Prescribed |

### `club_memberships` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `club_membership_id` | Source/standardized | `club_memberships.id` (supported canonical alias) | Canonical club-membership identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `club_membership_sk` | Surrogate | SHA-256 of `club_membership_id` | Stable club-membership surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `player_id` | Source/standardized | Required source `player_id` | Member player identifier | `STRING` | Required accepted reference | Foreign identifier to `players.player_id` | Prescribed |
| 4 | `player_sk` | Lookup | Surrogate key from accepted player | Member player surrogate | `STRING` | Required when membership is accepted | Foreign surrogate to `players.player_sk` | Prescribed |
| 5 | `club_id` | Source/standardized | Required source `club_id` | Club identifier | `STRING` | Required accepted reference | Foreign identifier to `clubs.club_id` | Prescribed |
| 6 | `club_sk` | Lookup | Surrogate key from accepted club | Club surrogate | `STRING` | Required when membership is accepted | Foreign surrogate to `clubs.club_sk` | Prescribed |
| 7 | `membership_type` | Source/standardized | Preserved `membership_type` | Source membership classification | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 8 | `joined_date` | Source/standardized | Safely parsed and preserved `joined_date` | Source membership join date | `DATE` | Required accepted value | Source lifecycle field | Prescribed |
| 9 | `left_date` | Source/standardized | Safely parsed and preserved `left_date` | Source membership leave date | `DATE` | Nullable optional value | Source lifecycle field | Prescribed |
| 10 | `is_primary` | Source/standardized | Preserved `is_primary` | Source primary-membership indicator | `BOOLEAN` | Nullable when source contract permits | None | Prescribed |
| 11 | `membership_start_date` | Source/standardized | Canonical start from supported membership/join/start fields | Canonical membership start date | `DATE` | Expected from required joined date under schema 1.6 | Canonical interval field | Prescribed |
| 12 | `membership_end_date` | Source/standardized | Canonical end from supported membership/left/end fields | Canonical membership end date | `DATE` | Nullable optional value | Canonical interval field | Prescribed |
| 13 | `derived_membership_duration_days` | Derived | Prescribed interval duration using end or snapshot context | Membership duration in days | SQL integer family | Depends on canonical start and comparison end | Derived field | Prescribed |
| 14 | `derived_current_membership_flag` | Derived | Inclusive interval evaluation at prescribed snapshot context | Current club-membership indicator | `BOOLEAN` | May be null when comparison date is unavailable | Derived field | Prescribed |
| 15 | `dq_membership_overlap_flag` | Quality | Prescribed preceding-interval overlap check | Membership-overlap warning indicator | `BOOLEAN` | Accepted warning field; physical nullability unresolved | Data-quality indicator | Prescribed |

### `team_memberships` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `team_membership_id` | Source/standardized | `team_memberships.id` (supported canonical alias) | Canonical team-membership identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `team_membership_sk` | Surrogate | SHA-256 of `team_membership_id` | Stable team-membership surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `team_id` | Source/standardized | Required source `team_id` | Persistent team identifier | `STRING` | Required accepted reference | Foreign identifier to `teams.team_id` | Prescribed |
| 4 | `team_sk` | Lookup | Surrogate key from accepted team | Persistent team surrogate | `STRING` | Required when membership is accepted | Foreign surrogate to `teams.team_sk` | Prescribed |
| 5 | `player_id` | Source/standardized | Required source `player_id` | Member player identifier | `STRING` | Required accepted reference | Foreign identifier to `players.player_id` | Prescribed |
| 6 | `player_sk` | Lookup | Surrogate key from accepted player | Member player surrogate | `STRING` | Required when membership is accepted | Foreign surrogate to `players.player_sk` | Prescribed |
| 7 | `player_position` | Source/standardized | Normalized `player_position` from supported position aliases | Player's team position | Categorical; exact type unresolved | Required accepted value under schema 1.6 | None | Prescribed |
| 8 | `joined_date` | Source/standardized | Safely parsed and preserved `joined_date` | Source team-join date | `DATE` | Required accepted value | Source lifecycle field | Prescribed |
| 9 | `left_date` | Source/standardized | Safely parsed and preserved `left_date` | Source team-leave date | `DATE` | Nullable optional value | Source lifecycle field | Prescribed |
| 10 | `player_role` | Source/standardized | Optional supported player-role attribute | Player's role on the team | Categorical; exact type unresolved | Nullable when no supported source value is supplied | None | Prescribed |
| 11 | `membership_start_date` | Source/standardized | Canonical start from supported membership/join/start fields | Canonical team-membership start date | `DATE` | Required Silver contract column; expected from required joined date | Canonical interval field | Prescribed |
| 12 | `membership_end_date` | Source/standardized | Canonical end from supported membership/left/end fields | Canonical team-membership end date | `DATE` | Nullable optional value | Canonical interval field | Prescribed |
| 13 | `derived_membership_duration_days` | Derived | End date minus start date only when both are supplied | Closed team-membership duration in days | SQL integer family | Null for open-ended membership | Derived field | Prescribed |
| 14 | `derived_current_membership_flag` | Derived | Inclusive interval evaluation at prescribed snapshot context | Current team-membership indicator | `BOOLEAN` | May be null when comparison date is unavailable | Derived field | Prescribed |
| 15 | `dq_membership_overlap_flag` | Quality | Prescribed preceding-interval overlap check | Membership-overlap warning indicator | `BOOLEAN` | Accepted warning field; physical nullability unresolved | Data-quality indicator | Prescribed |

### `matches` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `match_id` | Source/standardized | `matches.id` (supported canonical alias) | Canonical match identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `match_sk` | Surrogate | SHA-256 of `match_id` | Stable match surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `batch_id` | Source/standardized | Required physical `batch_id` | Match batch identifier | `STRING` | Required accepted reference | Foreign identifier to `monthly_batches.batch_id` | Prescribed |
| 4 | `batch_sk` | Lookup | Surrogate key from accepted batch | Match batch surrogate | `STRING` | Required when match is accepted | Foreign surrogate to `monthly_batches.batch_sk` | Prescribed |
| 5 | `region_id` | Source/standardized | Optional source `region_id` | Match region identifier | `STRING` | Nullable optional reference | Foreign identifier to `regions.region_id` | Prescribed |
| 6 | `region_sk` | Lookup | Surrogate key from accepted region | Match region surrogate | `STRING` | Nullable when `region_id` is null | Foreign surrogate to `regions.region_sk` | Prescribed |
| 7 | `match_date` | Source/standardized | Safely parsed `match_date` | Match event date | `DATE` | Required accepted value | Event-time field | Prescribed |
| 8 | `match_type` | Source/standardized | Preserved/normalized `match_type` | Source match classification | Categorical; exact type unresolved | Required accepted value | None | Prescribed |
| 9 | `court_type` | Source/standardized | Preserved `court_type` | Source court classification | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 10 | `match_format` | Source/standardized | Preserved `match_format` | Source match-format attribute | Categorical; exact type unresolved | Nullable when source contract permits | None | Prescribed |
| 11 | `total_points_played` | Source/standardized | Preserved `total_points_played` | Source match-level points count | SQL integer family | Nullable when source contract permits | None | Prescribed |
| 12 | `competition_category` | Source/standardized | Uppercased `match_type` | Canonical competition category | Categorical; exact type unresolved | Required Silver contract column | Canonical standardized field | Prescribed |
| 13 | `winning_team_id` | Source/standardized | Preserved persistent winner from supported winner-team ID fields | Winning persistent-team identifier | `STRING` | Nullable optional reference | Foreign identifier to `teams.team_id`; must correspond to a side when populated | Prescribed |
| 14 | `derived_winning_team_number` | Lookup/derived | Winner-side mapping from Bronze `match_teams`, reconciled with any explicit winner-side value | Winning match-side number | SQL integer family | Nullable when no winner is supplied; valid values 1 or 2 when populated | Derived field; not a persistent team ID | Prescribed |
| 15 | `derived_completed_flag` | Derived | Presence of a valid winning side number | Match completion indicator | `BOOLEAN` | Expected derived value; physical nullability unresolved | Derived field | Prescribed |
| 16 | `derived_match_year` | Derived | Year from `match_date` | Match year | SQL integer family | Depends on valid match date | Derived field | Prescribed |
| 17 | `derived_match_month` | Derived | Month from `match_date` | Match month number | SQL integer family | Depends on valid match date | Derived field | Prescribed |

### `match_teams` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `match_team_id` | Source/standardized | `match_teams.id` (supported canonical alias) | Canonical match-side identifier | `STRING` | Required accepted value | Primary key; match-side identity | Prescribed |
| 2 | `match_team_sk` | Surrogate | SHA-256 of `match_team_id` | Stable match-side surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `match_id` | Source/standardized | Required source `match_id` | Parent match identifier | `STRING` | Required accepted reference | Foreign identifier to `matches.match_id` | Prescribed |
| 4 | `match_sk` | Lookup | Surrogate key from accepted match | Parent match surrogate | `STRING` | Required when side is accepted | Foreign surrogate to `matches.match_sk` | Prescribed |
| 5 | `team_id` | Source/standardized | Required source `team_id` | Persistent team represented by the side | `STRING` | Required accepted reference | Foreign identifier to `teams.team_id`; not a match-side ID | Prescribed |
| 6 | `team_sk` | Lookup | Surrogate key from accepted persistent team | Persistent team surrogate | `STRING` | Required when side is accepted | Foreign surrogate to `teams.team_sk` | Prescribed |
| 7 | `team_number` | Source/standardized | Safely converted team/side number | Match-local side number | SQL integer family | Required accepted value; valid values 1 or 2 | Match-side role | Prescribed |
| 8 | `team_score` | Source/standardized | Preserved/safely converted `team_score` | Source match-side score | SQL integer family | Required source value | None | Prescribed |
| 9 | `average_team_rating` | Source/standardized | Preserved `average_team_rating` | Source average team rating | `DOUBLE` | Nullable when source contract permits | None | Prescribed |
| 10 | `match_date` | Lookup | Inherited from accepted parent match | Match event date for the side | `DATE` | Required through accepted match relationship | Parent-match enrichment | Prescribed |
| 11 | `pre_match_team_rating` | Source/standardized | Supported pre-match/team-rating value, including `average_team_rating` fallback | Canonical pre-match team rating | `DOUBLE` | Nullable when no supported source value is supplied | None | Prescribed |
| 12 | `derived_winner_flag` | Derived | Comparison to accepted match winner-side context | Whether this side won the match | `BOOLEAN` | Depends on winner context | Derived field | Prescribed |
| 13 | `derived_post_match_team_rating` | Derived | No source-supported calculation is prescribed | Post-match team rating placeholder | `DOUBLE` | Prescribed null when no source-supported value exists | Derived field; no synthetic calculation | Prescribed |
| 14 | `derived_rating_change` | Derived | No source-supported calculation is prescribed | Team rating-change placeholder | `DOUBLE` | Prescribed null when no source-supported value exists | Derived field; no synthetic calculation | Prescribed |
| 15 | `dq_side_cardinality_warning_flag` | Quality | Accepted side count for the parent match differs from two | Match-side cardinality warning | `BOOLEAN` | Accepted warning field; physical nullability unresolved | Data-quality indicator | Prescribed |

### `match_team_players` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `match_team_player_id` | Source/standardized | `match_team_players.id` (supported canonical alias) | Canonical match-participant identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `match_team_player_sk` | Surrogate | SHA-256 of `match_team_player_id` | Stable match-participant surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `match_team_id` | Source/standardized | Required source `match_team_id` | Participating match-side identifier | `STRING` | Required accepted reference | Foreign identifier to `match_teams.match_team_id` | Prescribed |
| 4 | `match_team_sk` | Lookup | Surrogate key from accepted match side | Participating match-side surrogate | `STRING` | Required when participant is accepted | Foreign surrogate to `match_teams.match_team_sk` | Prescribed |
| 5 | `match_id` | Lookup | Inherited from accepted match side | Parent match identifier | `STRING` | Required through accepted side relationship | Foreign identifier to `matches.match_id` | Prescribed |
| 6 | `match_sk` | Lookup | Inherited accepted match surrogate | Parent match surrogate | `STRING` | Required through accepted side relationship | Foreign surrogate to `matches.match_sk` | Prescribed |
| 7 | `team_id` | Lookup | Inherited persistent team from accepted match side | Persistent team represented by the participant's side | `STRING` | Required through accepted side relationship | Foreign identifier to `teams.team_id` | Prescribed |
| 8 | `team_sk` | Lookup | Inherited persistent-team surrogate | Persistent team surrogate | `STRING` | Required through accepted side relationship | Foreign surrogate to `teams.team_sk` | Prescribed |
| 9 | `player_id` | Source/standardized | Required source `player_id` | Participating player identifier | `STRING` | Required accepted reference | Foreign identifier to `players.player_id` | Prescribed |
| 10 | `player_sk` | Lookup | Surrogate key from accepted player | Participating player surrogate | `STRING` | Required when participant is accepted | Foreign surrogate to `players.player_sk` | Prescribed |
| 11 | `player_position` | Source/standardized | Normalized supported participant-position value | Player position on this match side | Categorical; exact type unresolved | Nullable when source contract permits; populated values must be valid | None | Prescribed |
| 12 | `player_rating_at_match` | Source/standardized | Preserved historical `player_rating_at_match` from supported aliases | Player rating at actual match time | `DOUBLE` | Nullable when source contract permits | Historical event-time measurement | Prescribed |
| 13 | `derived_age_at_match` | Derived | Accepted player birth date evaluated at actual match date | Player age at match | SQL integer family | Depends on valid player birth and match dates | Derived field | Prescribed |
| 14 | `derived_age_group_at_match` | Derived | Configured age group for `derived_age_at_match` | Player age group at match | Categorical; exact type unresolved | Depends on derived match-time age | Derived field | Prescribed |
| 15 | `match_date` | Lookup | Inherited from accepted match-side/match context | Actual match event date | `DATE` | Required through accepted match relationship | Parent-match enrichment | Prescribed |
| 16 | `dq_membership_history_warning_flag` | Quality | Membership history exists but no interval contains the match date | Historical membership warning | `BOOLEAN` | No history alone does not set this flag | Data-quality indicator | Prescribed |

### `match_games` accepted fields

| Order | Field | Origin | Prescribed source or derivation | Intended meaning | Type family | Requirement / relationship | Key or field role | Status |
|---:|---|---|---|---|---|---|---|---|
| 1 | `match_game_id` | Source/standardized | `match_games.id` (supported canonical alias) | Canonical game identifier | `STRING` | Required accepted value | Primary key | Prescribed |
| 2 | `match_game_sk` | Surrogate | SHA-256 of `match_game_id` | Stable game surrogate key | `STRING` | Expected for accepted rows; physical nullability unresolved | Entity surrogate key | Prescribed |
| 3 | `match_id` | Source/standardized | Required source `match_id` | Parent match identifier | `STRING` | Required accepted reference | Foreign identifier to `matches.match_id` | Prescribed |
| 4 | `match_sk` | Lookup | Surrogate key from accepted match | Parent match surrogate | `STRING` | Required when game is accepted | Foreign surrogate to `matches.match_sk` | Prescribed |
| 5 | `game_number` | Source/standardized | Safely converted `game_number` | Game sequence within the match | SQL integer family | Required accepted positive value | Match-local identifying component | Prescribed |
| 6 | `team_one_score` | Source/standardized | Safely converted `team_one_score` | Side-one game score | SQL integer family | Required accepted nonnegative value | None | Prescribed |
| 7 | `team_two_score` | Source/standardized | Safely converted `team_two_score` | Side-two game score | SQL integer family | Required accepted nonnegative value | None | Prescribed |
| 8 | `winning_team_number` | Source/standardized | Safely converted `winning_team_number` | Winning match-side number for the game | SQL integer family | Required accepted value 1 or 2 | Match-side role; not a persistent team ID | Prescribed |
| 9 | `target_score` | Source/standardized | Safely converted optional `target_score` | Source game target score | SQL integer family | Nullable optional value | None | Prescribed |
| 10 | `win_by` | Source/standardized | Safely converted optional `win_by` | Source win-by attribute | SQL integer family | Nullable optional value | None | Prescribed |
| 11 | `actual_team_one_score_share` | Source/standardized | Safely converted `actual_team_one_score_share` | Source share of points scored by side one | `DOUBLE` | Nullable optional value | None | Prescribed |
| 12 | `derived_score_margin` | Derived | Absolute difference between side scores | Game score margin | SQL integer family | Expected from accepted scores | Derived field | Prescribed |
| 13 | `derived_total_points` | Derived | Sum of side scores | Total game points | SQL integer family | Expected from accepted scores | Derived field | Prescribed |
| 14 | `derived_close_game_flag` | Derived | Score margin compared with configured close-game margin | Close-game indicator | `BOOLEAN` | Expected from accepted scores | Derived field | Prescribed |
| 15 | `derived_extended_game_flag` | Derived | Winning score strictly greater than populated target score | Extended-game indicator | `BOOLEAN` | May be null when target score is absent | Derived field | Prescribed |

### Accepted-field boundaries and unresolved details

The tables above document accepted Silver fields only. Exception tables, operational evidence, convenience views, detailed rule ordering, SQL, and execution procedures remain outside this task and are governed by the Bronze-to-Silver prompt.

Appendix B supplies exact field names and order but deliberately does not establish exact Spark nullability or every physical type. Supported aliases that are absent from the schema 1.6 physical source contract are compatibility inputs, not additional required source columns. Canonical fields such as `province_state`, `display_name`, `registration_type`, and `player_role` therefore retain the prompt's prescribed output names while their populated-source availability and exact physical nullability remain unresolved until implementation verification. No field in this section is marked physically or implementation verified.


## Silver Exceptions and Operational Structures

This task documents the prescribed Silver exception outputs only. The Bronze-to-Silver construction prompt is authoritative. Silver operational evidence tables, grouped quality summaries, reconciliation, schema snapshots, and run metadata remain outside this section and will be documented separately.

### Exception-output inventory

Each accepted Silver target has one corresponding `<target_table>_exceptions` Delta table in the selected profile's Silver reject schema. Every table uses the same ordered 17-field projection documented below, including when the result is empty. The record grain is one rejected Bronze source-row occurrence with its selected diagnostic evidence. Repeated or duplicate source occurrences remain separately represented; no exception-table primary key is prescribed.

| Exception table | Bronze source entity | Affected accepted Silver target | Purpose | Record grain | Field count | Verification status |
|---|---|---|---|---|---:|---|
| `monthly_batches_exceptions` | `monthly_batches` | `monthly_batches` | Preserve rejected batch occurrences and their diagnostic disposition | One rejected `monthly_batches` source occurrence | 17 | Prescribed |
| `regions_exceptions` | `regions` | `regions` | Preserve rejected region occurrences and their diagnostic disposition | One rejected `regions` source occurrence | 17 | Prescribed |
| `players_exceptions` | `player_master` | `players` | Preserve rejected player occurrences and their diagnostic disposition | One rejected `player_master` source occurrence | 17 | Prescribed |
| `clubs_exceptions` | `clubs` | `clubs` | Preserve rejected club occurrences and their diagnostic disposition | One rejected `clubs` source occurrence | 17 | Prescribed |
| `teams_exceptions` | `teams` | `teams` | Preserve rejected persistent-team occurrences and their diagnostic disposition | One rejected `teams` source occurrence | 17 | Prescribed |
| `player_registrations_exceptions` | `player_registrations` | `player_registrations` | Preserve rejected registration occurrences and their diagnostic disposition | One rejected `player_registrations` source occurrence | 17 | Prescribed |
| `player_assessment_history_exceptions` | `player_assessment_history` | `player_assessment_history` | Preserve rejected assessment occurrences and their diagnostic disposition | One rejected `player_assessment_history` source occurrence | 17 | Prescribed |
| `club_memberships_exceptions` | `club_memberships` | `club_memberships` | Preserve rejected club-membership occurrences and their diagnostic disposition | One rejected `club_memberships` source occurrence | 17 | Prescribed |
| `team_memberships_exceptions` | `team_memberships` | `team_memberships` | Preserve rejected team-membership occurrences and their diagnostic disposition | One rejected `team_memberships` source occurrence | 17 | Prescribed |
| `matches_exceptions` | `matches` | `matches` | Preserve rejected match occurrences and their diagnostic disposition | One rejected `matches` source occurrence | 17 | Prescribed |
| `match_teams_exceptions` | `match_teams` | `match_teams` | Preserve rejected match-side occurrences and their diagnostic disposition | One rejected `match_teams` source occurrence | 17 | Prescribed |
| `match_team_players_exceptions` | `match_team_players` | `match_team_players` | Preserve rejected match-participant occurrences and their diagnostic disposition | One rejected `match_team_players` source occurrence | 17 | Prescribed |
| `match_games_exceptions` | `match_games` | `match_games` | Preserve rejected game occurrences and their diagnostic disposition | One rejected `match_games` source occurrence | 17 | Prescribed |

### Shared exception field contract — all 13 tables

The construction prompt prescribes exact field names and order but does not prescribe Spark physical types, precision, or physical nullability. Those details are **Unresolved** pending authoritative clarification or implementation-schema evidence.

| Order | Field | Meaning | Prescribed source or derivation | Physical type | Physical nullability | Verification status |
|---:|---|---|---|---|---|---|
| 1 | `source_table` | Bronze source entity associated with the rejected occurrence | Transformation source context | Unresolved | Unresolved | Prescribed |
| 2 | `target_table` | Accepted Silver target from which the occurrence was excluded | Transformation target context | Unresolved | Unresolved | Prescribed |
| 3 | `source_business_key` | Source business-key value used to identify the occurrence when available | Normalized or diagnostic source key context | Unresolved | Unresolved | Prescribed |
| 4 | `reject_reason` | Rejection reason code or category assigned to the occurrence | First prescribed rejection disposition for the occurrence | Unresolved | Unresolved | Prescribed |
| 5 | `reject_reason_code` | Compatibility repetition of `reject_reason` | Copies `reject_reason` as explicitly prescribed | Unresolved | Unresolved | Prescribed |
| 6 | `reject_reason_detail` | Human-readable or diagnostic detail about the rejection | Table/rule-specific diagnostic context | Unresolved | Unresolved | Prescribed |
| 7 | `rule_id` | Identifier of the prescribed rule producing the disposition | Applicable table-specific or shared rule | Unresolved | Unresolved | Prescribed |
| 8 | `rule_severity` | Severity assigned to the applicable rule | Prescribed rule metadata | Unresolved | Unresolved | Prescribed |
| 9 | `failed_source_column` | Source column associated with the failed check, when applicable | Conversion or validation evidence | Unresolved | Unresolved | Prescribed |
| 10 | `failed_source_value` | Original offending source value, when applicable | Preserved before failed conversion or validation | Unresolved | Unresolved | Prescribed |
| 11 | `pipeline_run_id` | Pipeline-run identifier for operational traceability | Current Silver run context | Unresolved | Unresolved | Prescribed |
| 12 | `_pipeline_run_id` | Duplicate run identifier retained for compatibility and traceability | Current Silver run context | Unresolved | Unresolved | Prescribed |
| 13 | `_source_dataset` | Selected source dataset or release | Current release context | Unresolved | Unresolved | Prescribed |
| 14 | `load_ts` | Exception-load timestamp for operational traceability | Current exception-write context | Unresolved | Unresolved | Prescribed |
| 15 | `_load_ts` | Duplicate load timestamp retained for compatibility and traceability | Current exception-write context | Unresolved | Unresolved | Prescribed |
| 16 | `source_record_json` | JSON representation of selected source and diagnostic fields | Transformation-selected diagnostic projection; not guaranteed to contain the complete Bronze row | Unresolved | Unresolved | Prescribed |
| 17 | `_record_hash` | SHA-256 fingerprint of `source_record_json` | Hash of the prescribed diagnostic JSON representation | Unresolved | Unresolved | Prescribed |

No primary or foreign key is prescribed for an exception table. `source_business_key` supports identification but is not guaranteed unique, especially for duplicate-key defects or repeated source occurrences. Bronze remains the complete unchanged source evidence when `source_record_json` contains only the selected diagnostic projection.

### High-level rejection semantics

- A null in a required source field is represented with `MISSING_REQUIRED_VALUE`; a missing required physical column is instead a technical preflight failure and does not become an ordinary record-level exception.
- A populated required reference absent from the original Bronze parent dataset is represented with `INVALID_FOREIGN_KEY`.
- A reference whose parent exists in Bronze but was rejected from accepted Silver is represented with `PARENT_REJECTED`.
- Other prescribed failures—including malformed values, invalid domains or intervals, duplicate primary keys, and table-specific structural defects—retain their applicable reason, rule, severity, failed-column/value, and diagnostic JSON evidence without inventing replacement data.
- The first prescribed rejection reason determines the occurrence's exception disposition unless the construction prompt explicitly requires additional evidence. Positive rejection counts do not independently make the pipeline execution fail.

Rejected occurrences are excluded from the corresponding accepted Silver table and written to its exception table. Every original Bronze occurrence must reconcile to exactly one accepted occurrence or one rejected exception occurrence; diagnostic subsets must not be added again to that total.

### Profile-specific namespace separation

| Dataset profile | Accepted Silver schema setting | Silver reject schema setting |
|---|---|---|
| `napa_5k_clean` | `replace_with_prefix_napa_5k_clean_silver` | `replace_with_prefix_napa_5k_clean_silver_reject` |
| `napa_5k_tainted` | `replace_with_prefix_napa_5k_tainted_silver` | `replace_with_prefix_napa_5k_tainted_silver_reject` |
| `napa_50k_clean` | `replace_with_prefix_napa_50k_clean_silver` | `replace_with_prefix_napa_50k_clean_silver_reject` |
| `napa_50k_tainted` | `replace_with_prefix_napa_50k_tainted_silver` | `replace_with_prefix_napa_50k_tainted_silver_reject` |
| `napa_250k_production` | `replace_with_prefix_napa_250k_silver` | `replace_with_prefix_napa_250k_silver_reject` |

The values above are configurable placeholders, not verified deployed schemas. Accepted entities belong in the profile-specific `silver_schema`; exceptions belong in the corresponding profile-specific `silver_reject_schema`; shared operational evidence belongs in the separately configured `<team_prefix>_ops` schema. Rejected rows are not retained in accepted Silver tables, and exception tables are not substitutes for shared operational quality or reconciliation evidence.

No exception schema, table, field, or behavior in this section is marked **Physically verified** or **Implementation verified**. Refer to `docs/bronze_to_silver_prompt.md` for detailed rule order, identifiers, transformations, SQL, execution behavior, and acceptance tests.

## Silver Operational Evidence Contracts

The Bronze-to-Silver construction prompt prescribes six managed Delta evidence tables in the shared, configurable `<team_prefix>_ops` schema. They are separate from the five unprefixed Raw-to-Bronze operations tables already documented above: Silver reuses the shared operations **namespace**, not the Bronze tables or their field contracts. Silver may also consult upstream Raw-to-Bronze run evidence during source preflight without rewriting it.

All contracts below are **Prescribed** and have not been marked **Physically verified** or **Implementation verified**. The prompt specifies field order and broad type conventions, but delegates exact DDL and per-column nullability to the implementation. Consequently, physical nullability is **Unresolved** for every field. Required run context, statuses, and timestamps must not be silently null, but the prompt does not identify the exact `NOT NULL` columns. `threshold_value` also has no prescribed physical type and remains **Unresolved**.

### Evidence-structure inventory

| Prescribed table | Purpose | Record grain | Field count | Principal relationships | Verification status |
|---|---|---|---:|---|---|
| `b2s_pipeline_runs` | Record Silver workflow context, state, timing, and terminal errors | One run-state record for a Silver pipeline run; normally an open record is finalized, with a terminal record permitted when no open record exists | 14 | `pipeline_run_id` links all Silver run evidence; `release_name` identifies the selected profile/release | Prescribed |
| `b2s_table_runs` | Record table-build execution and accepted/rejected publication counts | One execution-state record per run and source/target build; separate `RUNNING` and terminal records are appended | 18 | Links a Bronze `source_table`, accepted Silver `target_table`, run, and build stage | Prescribed |
| `b2s_quality_results` | Record grouped rejection evidence and prescribed cross-table validation results | One run-scoped result for a target table and quality rule evaluation | 13 | Links the evaluated target and rule to the run/release; sampled keys provide diagnostic evidence, not a table key | Prescribed |
| `b2s_reconciliation_results` | Reconcile each Bronze source with its accepted and rejected Silver occurrences | One result per run and independently reconciled source/target pair | 12 | Links Bronze source, accepted Silver target, reject counts, and run/release | Prescribed |
| `b2s_schema_snapshots` | Record the ordered physical schema observed for a Silver object | One field observation per run, layer, table, and column ordinal | 10 | Links a field/schema hash to the run, release, layer, and table | Prescribed |
| `b2s_run_messages` | Retain structured operational diagnostics and terminal messages | One message event for a run and optional target context | 7 | Links message evidence to the run/release and, when applicable, target table | Prescribed |

No primary or foreign keys, retention periods, or additional uniqueness constraints are prescribed for these tables. The single generated `pipeline_run_id` is the common traceability value passed across tasks and evidence records.

### `b2s_pipeline_runs` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | UUID identifying one Silver workflow run | Prescribed |
| 2 | `pipeline_name` | `STRING` | Silver pipeline name | Prescribed |
| 3 | `pipeline_version` | `STRING` | Version of the Silver pipeline implementation | Prescribed |
| 4 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 5 | `processing_mode` | `STRING` | Configured Silver execution mode, including full refresh | Prescribed |
| 6 | `configuration_hash` | `STRING` | Fingerprint of the resolved run configuration | Prescribed |
| 7 | `workflow_run_id` | `STRING` | Databricks workflow-run identifier when available | Prescribed |
| 8 | `status` | `STRING` | Run lifecycle or terminal status | Prescribed |
| 9 | `started_ts` | `TIMESTAMP` | UTC-aware run start timestamp | Prescribed |
| 10 | `completed_ts` | `TIMESTAMP` | UTC-aware run completion timestamp | Prescribed |
| 11 | `duration_seconds` | `DOUBLE` | Elapsed run duration in seconds | Prescribed |
| 12 | `triggered_by` | `STRING` | Trusted trigger identity or context when available | Prescribed |
| 13 | `error_class` | `STRING` | Terminal error class when the run fails | Prescribed |
| 14 | `error_message` | `STRING` | Terminal error summary when the run fails | Prescribed |

### `b2s_table_runs` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Silver pipeline-run identifier | Prescribed |
| 2 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 3 | `source_table` | `STRING` | Bronze source table for the build | Prescribed |
| 4 | `target_table` | `STRING` | Accepted Silver target table | Prescribed |
| 5 | `build_stage` | `STRING` | Prescribed build-stage label | Prescribed |
| 6 | `build_order` | `INT` | Position in the prescribed build order | Prescribed |
| 7 | `status` | `STRING` | Table-build lifecycle or terminal status | Prescribed |
| 8 | `started_ts` | `TIMESTAMP` | UTC-aware table-build start timestamp | Prescribed |
| 9 | `completed_ts` | `TIMESTAMP` | UTC-aware table-build completion timestamp | Prescribed |
| 10 | `duration_seconds` | `DOUBLE` | Elapsed table-build duration in seconds | Prescribed |
| 11 | `source_row_count` | `BIGINT` | Bronze source occurrence count evaluated | Prescribed |
| 12 | `exact_duplicate_count` | `BIGINT` | Diagnostic count of exact duplicate occurrences | Prescribed |
| 13 | `duplicate_key_rejected_count` | `BIGINT` | Diagnostic count of duplicate-key rejected occurrences | Prescribed |
| 14 | `accepted_row_count` | `BIGINT` | Occurrences written to the accepted Silver target | Prescribed |
| 15 | `rejected_row_count` | `BIGINT` | Occurrences written to the corresponding exception table | Prescribed |
| 16 | `warning_count` | `BIGINT` | Warning findings recorded for the build | Prescribed |
| 17 | `published_row_count` | `BIGINT` | Rows published to the accepted target | Prescribed |
| 18 | `error_message` | `STRING` | Table-build error summary when applicable | Prescribed |

### `b2s_quality_results` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Silver pipeline-run identifier | Prescribed |
| 2 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 3 | `target_table` | `STRING` | Silver target associated with the evaluation | Prescribed |
| 4 | `rule_id` | `STRING` | Prescribed validation-rule identifier | Prescribed |
| 5 | `rule_type` | `STRING` | Rule classification | Prescribed |
| 6 | `severity` | `STRING` | Prescribed finding severity | Prescribed |
| 7 | `evaluated_row_count` | `BIGINT` | Denominator count evaluated by the rule | Prescribed |
| 8 | `failed_row_count` | `BIGINT` | Count that failed the rule | Prescribed |
| 9 | `failure_pct` | `DOUBLE` | Failed percentage; null when the denominator is zero | Prescribed |
| 10 | `threshold_value` | Unresolved | Threshold representation when a rule has one; no physical type is prescribed | Prescribed concept; physical type Unresolved |
| 11 | `status` | `STRING` | Validation-result status | Prescribed |
| 12 | `sample_business_keys` | `ARRAY<STRING>` | Up to ten sorted sampled business keys for diagnostic evidence | Prescribed |
| 13 | `evaluated_ts` | `TIMESTAMP` | UTC-aware evaluation timestamp | Prescribed |

### `b2s_reconciliation_results` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Silver pipeline-run identifier | Prescribed |
| 2 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 3 | `source_table` | `STRING` | Bronze source table reconciled | Prescribed |
| 4 | `target_table` | `STRING` | Accepted Silver target table | Prescribed |
| 5 | `bronze_row_count` | `BIGINT` | Original Bronze source occurrence count | Prescribed |
| 6 | `exact_duplicate_count` | `BIGINT` | Diagnostic exact-duplicate subset | Prescribed |
| 7 | `duplicate_key_rejected_count` | `BIGINT` | Diagnostic duplicate-key rejection subset | Prescribed |
| 8 | `rejected_row_count` | `BIGINT` | Rejected occurrence count | Prescribed |
| 9 | `accepted_row_count` | `BIGINT` | Accepted occurrence count | Prescribed |
| 10 | `reconciliation_difference` | `BIGINT` | Bronze count minus accepted and rejected counts | Prescribed |
| 11 | `status` | `STRING` | `MATCHED` or mismatch result, including required schema/column checks | Prescribed |
| 12 | `evaluated_ts` | `TIMESTAMP` | UTC-aware reconciliation timestamp | Prescribed |

### `b2s_schema_snapshots` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Silver pipeline-run identifier | Prescribed |
| 2 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 3 | `layer_name` | `STRING` | Layer associated with the observed object | Prescribed |
| 4 | `table_name` | `STRING` | Observed Silver table | Prescribed |
| 5 | `column_name` | `STRING` | Observed field name | Prescribed |
| 6 | `data_type` | `STRING` | Observed physical field type representation | Prescribed |
| 7 | `nullable` | `BOOLEAN` | Observed physical field-nullability flag | Prescribed |
| 8 | `ordinal_position` | `INT` | One-based field position | Prescribed |
| 9 | `schema_hash` | `STRING` | SHA-256 of the ordered schema representation prescribed by the prompt | Prescribed |
| 10 | `captured_ts` | `TIMESTAMP` | UTC-aware schema-capture timestamp | Prescribed |

### `b2s_run_messages` fields

| Order | Field | Prescribed type | Meaning | Verification status |
|---:|---|---|---|---|
| 1 | `pipeline_run_id` | `STRING` | Silver pipeline-run identifier | Prescribed |
| 2 | `release_name` | `STRING` | Selected dataset profile or release | Prescribed |
| 3 | `target_table` | `STRING` | Related target table when the message is table-specific | Prescribed |
| 4 | `message_level` | `STRING` | Diagnostic message level | Prescribed |
| 5 | `message_code` | `STRING` | Prescribed structured message code | Prescribed |
| 6 | `message_text` | `STRING` | Human-readable diagnostic text without secrets or full sensitive records | Prescribed |
| 7 | `created_ts` | `TIMESTAMP` | UTC-aware message timestamp | Prescribed |

### Evidence responsibilities and namespace boundaries

- **Full-refresh traceability:** `b2s_pipeline_runs`, `b2s_table_runs`, and `b2s_run_messages` connect the selected profile, configuration, workflow state, targeted reset/build activity, and terminal result to one run ID. A successful full refresh requires complete run-scoped execution evidence; quality findings alone do not determine execution success.
- **Accepted and rejected counts:** `b2s_table_runs` records source, accepted, rejected, warning, and published counts. Rejection subsets such as duplicate-key and parent-rejection counts remain diagnostic subsets and are not added again during reconciliation.
- **Source-to-target reconciliation:** `b2s_reconciliation_results` records all 13 independent Bronze-to-Silver reconciliations. Each Bronze occurrence must appear once as accepted or rejected; unexplained differences and required schema/column mismatches are technical failures.
- **Referential integrity and quality:** `b2s_quality_results` records grouped reject evidence and prescribed cross-table checks, including referential-integrity outcomes. Detailed rules and rejection decisions remain in the construction prompt and the profile-specific exception outputs.
- **Acceptance and schema evidence:** `b2s_schema_snapshots`, quality results, reconciliation results, table-run completion records, and structured messages collectively support the completion gate. They document evidence; they do not prove a run succeeded until implementation execution is verified.

Accepted Silver tables remain in the selected profile's configured `silver_schema`; rejected occurrences remain in its `silver_reject_schema`; all six `b2s_*` tables remain in the shared `<team_prefix>_ops` schema. The five Raw-to-Bronze operations tables coexist there under their unprefixed names and retain their existing contracts.

### Non-table operational evidence

| Mechanism | Prescribed evidence | Contract boundary | Verification status |
|---|---|---|---|
| Databricks task values | The resolve task publishes `run_id`; every downstream task receives that same value, and finalization exposes `final_status` | Physical types, durability, and retention are not prescribed; task values do not replace managed operations evidence | Prescribed concept; physical representation Unresolved |
| Databricks job/task state | Workflow and task status, run ID, and dependency outcomes provide execution context, including finalization with `ALL_DONE` | A successful deployment or task state alone does not prove data correctness or production certification | Prescribed concept; implementation evidence not verified |
| Runtime diagnostics | Propagated exceptions and job output provide failure context when managed audit storage is unavailable or incomplete | The prompt prescribes visible failure behavior but no separate log-table schema or retention contract | Prescribed concept; physical representation Unresolved |
| Post-run validation record | Teams capture configuration hash, table/reject counts, reconciliation, quality evidence, views, and job/task status after each profile run | The prompt does not prescribe an additional managed table for this handoff record | Prescribed concept; physical representation Unresolved |

Refer to `docs/bronze_to_silver_prompt.md` for detailed rule logic, message codes, execution procedures, finalization behavior, and acceptance tests. Refer to `docs/data_quality_report.md` for the team-maintained report of actual findings and downstream impacts.

## Gold Analytical Definitions — Team Maintained

Student consulting teams own and maintain this section. Teams select their Gold schemas, tables, views, features, metrics, analytical methods, selection approaches, and recommendation structures. Document Gold outputs as team decisions rather than prescribed NAPA engineering contracts, and keep every output traceable to its upstream Silver inputs and execution evidence.

Use `napa_250k_production` Silver data for final Olympic roster recommendations. Smaller profiles may support development and testing, but must not be represented as final production evidence. No national player-ranking table, ranking algorithm, or particular Gold output is required. The official RFP and Canvas assignments govern business deliverables; illustrative analytical ideas elsewhere in the repository are not mandatory designs.

### How to use this template

Copy the entity and field templates once for each team-created Gold table or view. Replace bracketed placeholders, remove instructional text, and add rows as needed. Use **Team-defined** for documented design intent, **Implementation verified** only after checking the deployed object and supporting run evidence, and **Unresolved** when a material definition or contract is still undecided. Link detailed source-to-output mappings in `docs/lineage.md` and architecture choices in `docs/architecture.md` rather than duplicating them here.

### Gold entity template — copy per table or view

#### `[Gold table or view name]`

| Documentation item | Team entry |
|---|---|
| Object type | `[Table or view]` |
| Team-owned schema and object name | `[Fully qualified name or documented configurable pattern]` |
| Business purpose | `[Decision or analytical need this object supports]` |
| Record grain | `[What one row represents]` |
| Source Silver tables or views | `[Upstream Silver inputs]` |
| Gold dependencies | `[Other team-created Gold inputs, or none]` |
| Primary or identifying key | `[Key or identifying fields, if applicable; otherwise not applicable]` |
| Applicable dataset profiles | `[Profiles used for development, validation, or production]` |
| Refresh approach | `[Team-selected refresh behavior and trigger]` |
| Owner | `[Responsible team role or member]` |
| Verification status | `[Team-defined, Implementation verified, or Unresolved]` |
| Verification evidence | `[Run ID, deployed object, test, review, or evidence reference]` |

### Gold field dictionary template — copy per entity

Document design intent before implementation, then update the status and evidence after verification. Do not infer that a planned type, key, or calculation exists physically until it has been checked.

| Field name | Business definition | Data type | Nullable or required expectation | Source or derivation | Key or relationship role | Validation or quality expectation | Verification status |
|---|---|---|---|---|---|---|---|
| `[field_name]` | `[Business meaning at the entity's stated grain]` | `[Planned or verified type]` | `[Required, nullable, not applicable, or unresolved]` | `[Silver field(s), Gold dependency, or team-defined derivation]` | `[Primary, identifying, relationship, or none]` | `[Team-defined check and expected behavior]` | `[Team-defined, Implementation verified, or Unresolved]` |

### Analytical decisions and traceability

For each material Gold output, feature, metric, or recommendation dependency, record enough context for another reviewer to understand and reproduce the team's decision. Keep detailed methodology in `docs/analytical_methodology.md`, detailed mappings in `docs/lineage.md`, and architectural rationale in `docs/architecture.md`.

| Gold object, field, or decision | Assumption or definition | Source evidence and profile | Method or derivation selected by team | Limitations or known bias | Validation and reproducibility evidence | Recommendation connection | Owner and status |
|---|---|---|---|---|---|---|---|
| `[Team-defined item]` | `[Material assumption, feature, metric, scoring/selection choice, or interpretation]` | `[Silver inputs, date window, and dataset profile]` | `[Team-selected logic; link implementation where applicable]` | `[Uncertainty, missing evidence, comparability concern, or bias]` | `[Tests, sensitivity checks, run/configuration reference, and review evidence]` | `[How the item informs—or does not inform—final rosters, alternates, or development-camp recommendations]` | `[Owner; Team-defined, Implementation verified, or Unresolved]` |

Document observed evidence, modeled or calculated results, and team judgment distinctly. Record material join assumptions, time windows, exclusions, eligibility interpretations, data-quality impacts, uncertainty, and sensitivity findings where they affect an output. A documented Gold definition establishes design intent; only executed and reviewed evidence establishes implementation verification.

## Open Questions and Definition Decisions

Record ambiguous business meanings, profile differences, evidence gaps, and interpretation decisions here as the dictionary is expanded. Keep unresolved items visible until an authoritative source or approved team decision resolves them.
