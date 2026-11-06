# NAPA Bronze Bootstrap Guide

For the two-job Asset Bundle workflow and exact deployment commands, start with
[`bootstrap_guide.md`](bootstrap_guide.md). This guide retains the detailed
Bronze input and reload behavior.

## Purpose

`notebooks/00_bootstrap_bronze.py` creates source-preserving Bronze Delta tables from the NAPA Parquet packages uploaded during Assignment 10. It is a teaching utility, not the instructor's production ingestion pipeline. It intentionally omits operational evidence tables, job orchestration, retries, and deployment infrastructure.

The notebook preserves all business values—including intentional defects—and appends the ten standard Bronze metadata columns. Data cleansing and quality remediation belong in Silver.

## Before you begin

For every profile you plan to build, Assignment 10 should already have placed these items directly in its Unity Catalog Raw Volume:

- the original `manifest.json`; and
- all 13 supplied `.parquet` files, with their original names.

Do not place them in an extra profile, release, or `raw` subfolder. The manifest and Parquet files for a profile must come from the same delivered package.

The notebook always derives the manifest location from that profile's configured `raw_volume_path`:

```text
<raw_volume_path>/manifest.json
```

It does not use a separate manifest setting, search other locations, or read a manifest from the repository's local `data/` directory. If the file is absent, the notebook stops and displays the complete expected Raw Volume path.

You also need permission to read those Volumes and create schemas and managed tables in your Databricks Free Edition workspace.

## Add the notebook to an existing repository

You do **not** need to recreate your GitHub repository, discard work, or repeat Assignment 10.

Copy `notebooks/00_bootstrap_bronze.py` into the existing repository's `notebooks` folder. You may commit it through your team's normal review process or import/upload the file directly into Databricks. The notebook is also suitable for separate Canvas distribution.

## Configure Bronze

For the normal Asset Bundle workflow, pass `catalog` and `team_prefix` as documented in [`bootstrap_guide.md`](bootstrap_guide.md), select the `dataset_profiles` job parameter, and leave `existing_table_action=fail` for the first run. The job parameters override the notebook's neutral defaults.

Review every `raw_volume_path` and `bronze_schema` in `PROFILE_CONFIG`. Edit that mapping only if the team's approved Raw Volumes do not follow the standard naming pattern below. A direct interactive notebook run may instead set `CATALOG` and `TEAM_PREFIX` in the first configuration cell.

The default paths follow the repository conventions:

```text
/Volumes/<catalog>/<team_prefix>_5k_clean_raw/napa_files
/Volumes/<catalog>/<team_prefix>_5k_tainted_raw/napa_files
/Volumes/<catalog>/<team_prefix>_50k_clean_raw/napa_files
/Volumes/<catalog>/<team_prefix>_50k_tainted_raw/napa_files
/Volumes/<catalog>/<team_prefix>_250k_raw/napa_files
```

Change individual paths in `PROFILE_CONFIG` if your Assignment 10 Volumes use different approved locations.

## Run in Databricks Free Edition

Normally, manually run the deployed `napa_bronze_bootstrap` job as shown in [`bootstrap_guide.md`](bootstrap_guide.md). For a direct interactive run or troubleshooting:

1. Open the notebook in Databricks.
2. Attach it to serverless compute.
3. To choose a subset before the first build, run the configuration cell and the following widget cell. Enter the selection in the `dataset_profiles` widget.
4. Choose **Run all**. If you do not create or change the widget first, its default is `napa_5k_clean`.

The widget accepts:

- one profile, such as `napa_5k_clean`;
- a comma-separated subset, such as `napa_5k_clean,napa_5k_tainted`; or
- `all` for all five profiles and 65 Bronze tables.

Supported profile names are `napa_5k_clean`, `napa_5k_tainted`, `napa_50k_clean`, `napa_50k_tainted`, and `napa_250k_production`.

Process profiles sequentially whenever practical. Begin with `napa_5k_clean`, review its 13 PASS results, and then continue in this order:

1. `napa_5k_tainted`
2. `napa_50k_clean`
3. `napa_50k_tainted`
4. `napa_250k_production`

The subset and `all` options remain available, but sequential runs make configuration or upload problems easier to identify.

## Read the results

Before writing, the notebook reads `manifest.json` directly beside the 13 Parquet files in each selected profile's configured Raw Volume. It checks the manifest, file inventory, source readability, source schema, and manifest-versus-Raw record count. The generator manifest identifies the dataset scale (5K, 50K, or 250K); the configured profile-specific Raw Volume path distinguishes clean from tainted data because the manifest does not contain that condition. The notebook stops with a short explanation—including the expected manifest path—when an input is missing, invalid, or has the wrong scale.

After writing, the displayed result has one row per table:

- dataset profile and source table;
- manifest expected count;
- Raw and Bronze record counts;
- `PASS` or `FAIL`; and
- structural-validation details.

`OVERALL PASS` means every selected table exists, its business-column names/order/types were preserved, all ten metadata columns are present, and:

```text
manifest count = Raw count = Bronze count
```

Delta may report nullability differently after persistence. The notebook reports that difference for information but does not treat it as data loss or a validation failure.

Do not continue to Silver after `OVERALL FAIL`. Check the named Volume, manifest, file upload, permissions, or target table identified by the message.

## Existing tables and reruns

The default `existing_table_action = "fail"` checks all selected targets before the first Bronze write. If an expected table already exists, the notebook stops and lists it without modifying any existing table.

## ⚠️ DANGER ZONE — INTENTIONAL BRONZE RELOAD

Normal operation uses `existing_table_action = "fail"`. Use `"replace"` only when you deliberately intend to reload an existing profile's 13 expected Bronze tables.

**Replace is destructive for those selected expected Bronze tables. Their previous content is not preserved by this workflow. Never use replace on instructor reference tables.**

For an intentional reload:

1. Select one dataset profile. Avoid `all` during a reload.
2. Verify `CATALOG`, `TEAM_PREFIX`, `raw_volume_path`, and `bronze_schema`. Identify the exact target as `<CATALOG>.<bronze_schema>` and confirm it belongs to your team.
3. Confirm that the selected Raw Volume contains `manifest.json` and all 13 Parquet files.
4. Set `existing_table_action = "replace"`.
5. Choose **Run all** once and wait for completion. Do not separately rerun the final execution cell.
6. Confirm that all 13 expected tables report `PASS`. If the run fails, investigate the cause before running it again.
7. Immediately restore `existing_table_action = "fail"` and save the notebook.

Before writing, replace mode displays the selected profile and exact fully qualified destination schema. It overwrites only the selected profile's 13 expected Bronze tables. It does not intentionally drop schemas, modify Raw Parquet files, or delete unrelated tables.

## Continue to Silver

After the selected profile reports `OVERALL PASS`, inspect representative Bronze records and follow [`bootstrap_guide.md`](bootstrap_guide.md) to run the independent `napa_silver_bootstrap` job. The supplied Silver notebook is designed for these bootstrap-created Bronze tables; historical enterprise readiness gates are not part of the Assignment 10 student workflow.
