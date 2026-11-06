# NAPA Bronze and Silver Bootstrap Guide

This repository supplies two independent, manually run Databricks jobs. Run Bronze first, inspect it, then run Silver. Gold remains team-designed.

## 1. Configure the bundle

Edit the defaults in `databricks.yml`, or pass variable overrides on each command:

- `catalog`: your Unity Catalog catalog, commonly `workspace` in Free Edition.
- `team_prefix`: your team's unique SQL-safe prefix.
- `dataset_profiles`: the Bronze job parameter. Start with `napa_5k_clean`.
- `dataset_profile`: the Silver job parameter. Start with `napa_5k_clean`.
- `existing_table_action`: keep `fail` for a first run. Use `replace` only for an intentional full refresh after checking the exact profile and schema.

The selected Raw Volume must already contain `manifest.json` and the 13 named Parquet files described in `docs/bronze_bootstrap_guide.md`.

## 2. Validate and deploy

From the repository root, using your authenticated Databricks CLI profile:

```bash
databricks bundle validate -t dev --profile <team-profile> \
  --var="catalog=workspace" --var="team_prefix=<team_prefix>"

databricks bundle deploy -t dev --profile <team-profile> \
  --var="catalog=workspace" --var="team_prefix=<team_prefix>"
```

Deployment creates or updates job definitions. It does not prove that the data is valid.

## 3. Run Bronze

```bash
databricks bundle run -t dev --profile <team-profile> \
  --var="catalog=workspace" --var="team_prefix=<team_prefix>" \
  napa_bronze_bootstrap \
  --params dataset_profiles=napa_5k_clean,existing_table_action=fail
```

For an authorized reload, change only `existing_table_action=replace`. Bronze validates the Raw package, preserves all source records and business values, adds ten metadata fields, and creates 13 Bronze tables.

## 4. Inspect Bronze

In Databricks SQL or a notebook, confirm the 13 tables and inspect representative records:

```sql
SHOW TABLES IN workspace.<team_prefix>_5k_clean_bronze;
SELECT * FROM workspace.<team_prefix>_5k_clean_bronze.player_master LIMIT 20;
```

Do not run Silver unless Bronze reports `OVERALL PASS`.

## 5. Run Silver

```bash
databricks bundle run -t dev --profile <team-profile> \
  --var="catalog=workspace" --var="team_prefix=<team_prefix>" \
  napa_silver_bootstrap \
  --params dataset_profile=napa_5k_clean,existing_table_action=fail
```

Silver applies exactly the 25 approved rules in `docs/silver_specification.md`. A successful run creates a complete current set of 27 managed tables in the selected profile's Silver schema: 13 accepted tables, 13 `<source>_rejects` tables, and `silver_data_quality_summary`.

## 6. Inspect Silver and DQ evidence

```sql
SHOW TABLES IN workspace.<team_prefix>_5k_clean_silver;

SELECT source_table, bronze_record_count, accepted_record_count,
       rejected_record_count, rejection_percentage, reconciliation_status
FROM workspace.<team_prefix>_5k_clean_silver.silver_data_quality_summary
WHERE row_type = 'TABLE_TOTAL'
ORDER BY source_table;

SELECT source_table, reason_id, reason_classification, reason_occurrence_count
FROM workspace.<team_prefix>_5k_clean_silver.silver_data_quality_summary
WHERE row_type = 'REASON_TOTAL'
ORDER BY reason_occurrence_count DESC, source_table, reason_id;
```

Nonzero rejection counts are expected data-quality evidence, not automatically a failed run. Every table-level row must reconcile.

## 7. Continue to Gold

Build Gold in a separate team-owned schema. Use accepted Silver tables as the baseline and inspect rejection evidence when explaining limitations. If Gold requires another trustworthy source attribute or objective transformation, update `docs/silver_specification.md` first, review the change, and then make a focused Silver edit. Do not add roster rankings, partnership scores, eligibility choices, or other Gold judgments to the supplied Silver baseline.

Repeat Bronze then Silver for the remaining profiles in the documented order. Use `napa_250k_production` for final recommendations.
