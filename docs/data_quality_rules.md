# Data Quality Rules

**Purpose:** This document helps teams track required engineering quality rules and any additional analytical checks they design. It is an evidence registry and planning aid; it does not replace the supplied construction prompts.

## Rule authority and categories

### Mandatory Bronze engineering requirements

`docs/raw_to_bronze_prompt.md` is authoritative for Raw package validation, Bronze publication, reconciliation, certification evidence, and failure behavior. These requirements are mandatory and must not be weakened, bypassed, or reclassified as optional team checks. Record evidence showing which prompt requirements were executed and whether they passed; do not create a competing Bronze rule specification here.

The delivered Parquet files and colocated `manifest.json` must remain unchanged. Bronze preserves source business values, including invalid values and duplicates, while adding only the prescribed operational metadata. Quality remediation belongs downstream and must never rewrite the Raw package.

### Mandatory Silver engineering requirements

`docs/bronze_to_silver_prompt.md` is authoritative for Silver validation, standardization, duplicate handling, referential integrity, rejection, reconciliation, quality evidence, and failure behavior. These requirements are mandatory and must not be weakened, bypassed, or replaced by a team-designed policy. Reference the prompt's rule identifiers and contracts rather than redefining them here.

Expected record-level quality defects must be handled and evidenced as prescribed without being confused with technical pipeline failure. Teams must preserve required reject, reconciliation, and operational evidence and must not synthesize corrections for invalid source values.

### Team-defined analytical requirements

Teams may add checks that support their own Gold-layer analytics, including validation of derived measures, analytical features, comparisons, and evidence used for Olympic roster and development-camp recommendations. These checks supplement the mandatory engineering foundation; they do not alter Raw, Bronze, Silver, rejection, or audit evidence.

The team selects checks appropriate to its analytical approach and explains why they are useful. This document does not prescribe Gold algorithms, models, tables, thresholds, or selection methods.

## Dataset-profile coverage

For every rule or check, identify which profiles it applies to:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

Do not assume that a result from one profile proves the same result for another. Record the selected profile and run evidence for each execution.

## Rule documentation standard

Document mandatory and team-defined checks using the same traceable fields. For mandatory rules, cite the governing prompt and preserve its identifier, severity, disposition, and failure behavior.

| Rule identifier | Category and authority | Applicable profiles | Processing layer | Description | Business or technical rationale | Validation method | Observed result and evidence | Treatment of failure | Downstream analytical impact |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

Distinguish checks that block pipeline completion from findings that reject a record, produce a warning, reduce analytical confidence, or require human review. Never report a check as passed unless it was executed.

## Reference quality areas

The following existing areas remain useful for planning. They are not a new mandatory rule set. When an area is governed by a construction prompt, reference and implement the exact prompt requirement; otherwise document any additional Gold check as team-defined.

| Quality area | Planning question |
|---|---|
| Athlete identity and status | Are identifiers, status, and geography usable for the intended analysis? |
| Rating validity | Are rating values interpretable for the team's selected features and comparisons? |
| Team composition and membership | Do candidate partnerships and membership periods support the intended use? |
| Match structure and winner integrity | Are participating sides, players, winners, and relationships coherent? |
| Game integrity | Are game numbers, scores, winners, and related measures usable? |
| Referential integrity | Do required relationships resolve without inventing replacement parents? |
| Duplicate detection | Are duplicate occurrences handled under the applicable layer contract? |
| Temporal consistency | Are dates, snapshot boundaries, and historical relationships evaluated in the correct time context? |
