# Data Quality Report

**Purpose:** Use this team-maintained template to record actual data quality observations, validation evidence, handling decisions, and effects on downstream analysis. It reports results; it does not redefine quality rules or replace the Bronze and Silver construction prompts.

## Reporting Scope

Create or update a report for each significant run and dataset profile:

- `napa_5k_clean`
- `napa_5k_tainted`
- `napa_50k_clean`
- `napa_50k_tainted`
- `napa_250k_production`

Record findings for the applicable Raw, Bronze, Silver, or Gold layer. Classify each check as one of the following:

- **Mandatory Bronze:** Evidence from validation required by `raw_to_bronze_prompt.md`.
- **Mandatory Silver:** Evidence from validation required by `bronze_to_silver_prompt.md`.
- **Team-defined analytical:** Additional checks selected by the team for its Gold features, analyses, or recommendations.

The construction prompts are authoritative for mandatory Bronze and Silver handling. Team-defined checks must support the team's analytical design without changing those requirements or prescribing a particular Gold model or method.

## Execution Context

- Dataset profile:
- Processing layer:
- Execution date and time:
- Pipeline or job run identifier, if available:
- Configuration or code version:
- Reviewer:
- Evidence location or reference:
- Scope of this review:

## Validation Coverage

Use one row for each profile and layer evaluated. Record checks that were not run rather than implying that they passed.

| Dataset profile | Layer | Execution date | Run identifier | Checks executed | Result summary | Evidence reference |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Significant Findings

Use one row for each finding that requires evidence, a decision, or follow-up. Report observed results only; do not invent results for unexecuted checks.

| Finding ID | Check category | Profile and layer | Rule or check | Validation method | Observed result and evidence | Issue identified | Handling or remediation decision | Downstream analytical impact | Status or owner |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

For mandatory checks, retain the construction prompt's rule identifier or evidence reference when available. For a team-defined analytical check, describe its rationale and how its result affects derived measures, candidate-team comparisons, or recommendation confidence.

## Handling Expectations

A quality finding does not automatically require deleting a record. Follow the applicable construction prompt and document whether the finding caused a run failure, warning, rejection to a prescribed exception output, acceptance with a flag, or a downstream analytical limitation. Keep expected record-level quality issues distinct from technical execution failures.

The original Raw Parquet files and colocated `manifest.json` must remain unchanged. Apply permitted standardization, rejection, or analytical handling in the appropriate downstream layer; never rewrite Raw data to make a validation pass. Any Gold-layer exclusion or adjustment must be justified, reproducible, and limited to the team's analysis.

## Readiness and Recommendation Impact

- Overall data readiness for the intended use:
- Significant unresolved issues:
- Known limitations and uncertainty:
- Implications for USA and Canada Olympic roster recommendations:
- Implications for alternate and development-camp recommendations:
- Required follow-up, owner, and target milestone:

State how the evidence affects confidence in the team's conclusions. A successful pipeline run does not by itself establish that the data is free of quality limitations.
