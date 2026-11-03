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

Field-level definitions for the remaining ten prescribed source tables are intentionally deferred to later stages.

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
