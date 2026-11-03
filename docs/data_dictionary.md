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

Reserved for field-level source definitions. A later stage will record prescribed column names and then distinguish them from profile-specific physical types, nullability, units, domains, and evidence. No individual source fields are populated in this stage.

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
