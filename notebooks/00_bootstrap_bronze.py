# Databricks notebook source
"""Student-facing NAPA Raw-to-Bronze bootstrap utility.

This notebook intentionally provides only the small amount of ingestion logic
needed to establish source-preserving Bronze tables. It is not the instructor's
production Raw-to-Bronze workflow and does not create operational evidence.
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # NAPA Bronze bootstrap
# MAGIC
# MAGIC Edit the configuration below, attach this notebook to serverless compute,
# MAGIC and run all cells. The default profile selection is `napa_5k_clean`.
# MAGIC
# MAGIC Bronze preserves every source business value. Data-quality fixes belong
# MAGIC in Silver, not in this notebook.

# COMMAND ----------
# Configuration: change these values for the student's own workspace.

CATALOG = "workspace"
TEAM_PREFIX = "napa_platform"

PROFILE_CONFIG = {
    "napa_5k_clean": {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_5k_clean_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_5k_clean_bronze",
    },
    "napa_5k_tainted": {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_5k_tainted_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_5k_tainted_bronze",
    },
    "napa_50k_clean": {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_50k_clean_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_50k_clean_bronze",
    },
    "napa_50k_tainted": {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_50k_tainted_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_50k_tainted_bronze",
    },
    "napa_250k_production": {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_250k_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_250k_bronze",
    },
}

# "fail" protects existing work. Change to "replace" only for an intentional rerun.
existing_table_action = "fail"

# COMMAND ----------
# Run this cell once if you want to choose a subset before the first full run.
if "dbutils" in globals():
    try:
        dbutils.widgets.text("dataset_profiles", "napa_5k_clean", "Dataset profiles")
    except Exception:
        # Keep the student's current selection when the widget already exists.
        pass

# COMMAND ----------
import json
import re
import uuid
from datetime import datetime, timezone


SUPPORTED_PROFILES = tuple(PROFILE_CONFIG)
SOURCE_TABLES = (
    "regions",
    "clubs",
    "club_memberships",
    "player_master",
    "player_registrations",
    "player_assessment_history",
    "teams",
    "team_memberships",
    "matches",
    "match_teams",
    "match_team_players",
    "match_games",
    "monthly_batches",
)
METADATA_COLUMNS = (
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_version",
    "_release_name",
    "_source_file_name",
    "_source_file_path",
    "_source_file_size",
    "_source_file_modification_ts",
    "_ingested_ts",
    "_source_record_hash",
)
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class BootstrapError(RuntimeError):
    """An input or validation problem with a student-actionable message."""


def select_profiles(selection, supported_profiles=SUPPORTED_PROFILES):
    """Return an ordered, de-duplicated list from `all` or comma-separated input."""
    value = (selection or "napa_5k_clean").strip().lower()
    if value == "all":
        return list(supported_profiles)

    requested = []
    for item in value.split(","):
        profile = item.strip()
        if profile and profile not in requested:
            requested.append(profile)

    if not requested:
        raise BootstrapError("Profile selection is empty. Choose 'all' or a supported profile.")

    unsupported = [profile for profile in requested if profile not in supported_profiles]
    if unsupported:
        raise BootstrapError(
            "Unsupported profile(s): "
            + ", ".join(unsupported)
            + ". Supported values: "
            + ", ".join(supported_profiles)
            + ", or all."
        )
    return requested


def _file_name(value):
    """Return the final path component, without a trailing slash."""
    return str(value or "").rstrip("/").rsplit("/", 1)[-1]


def extract_manifest_counts(manifest):
    """Extract and cross-check counts from the generator's actual manifest format."""
    if not isinstance(manifest, dict):
        raise BootstrapError("manifest.json must contain one JSON object.")

    row_counts = manifest.get("row_counts")
    if not isinstance(row_counts, dict):
        raise BootstrapError("manifest.json field 'row_counts' must be a JSON object.")
    missing_counts = sorted(set(SOURCE_TABLES) - set(row_counts))
    unexpected_counts = sorted(set(row_counts) - set(SOURCE_TABLES))
    if missing_counts or unexpected_counts:
        raise BootstrapError(
            "Manifest row_counts must contain exactly the 13 expected source tables."
        )

    counts = {}
    for table in SOURCE_TABLES:
        value = row_counts[table]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BootstrapError(
                f"Manifest row_counts value for '{table}' must be a non-negative integer."
            )
        counts[table] = value

    output_files = manifest.get("output_files")
    if not isinstance(output_files, list):
        raise BootstrapError("manifest.json field 'output_files' must be a JSON list.")

    manifest_tables = {}
    for entry in output_files:
        if not isinstance(entry, dict):
            raise BootstrapError("Every 'output_files' entry must be a JSON object.")
        table = entry.get("table_name")
        if table in manifest_tables:
            raise BootstrapError(f"Manifest output_files contains duplicate table '{table}'.")
        if table not in SOURCE_TABLES:
            raise BootstrapError(f"Manifest output_files contains unexpected table {table!r}.")
        if entry.get("file_name") != f"{table}.parquet":
            raise BootstrapError(
                f"Manifest file name for '{table}' must be '{table}.parquet'."
            )
        output_count = entry.get("row_count")
        if output_count != counts[table]:
            raise BootstrapError(
                f"Manifest has conflicting counts for '{table}': "
                f"row_counts={counts[table]} and output_files={output_count!r}."
            )
        manifest_tables[table] = entry

    missing_files = sorted(set(SOURCE_TABLES) - set(manifest_tables))
    unexpected_files = sorted(set(manifest_tables) - set(SOURCE_TABLES))
    if missing_files or unexpected_files:
        details = []
        if missing_files:
            details.append("missing: " + ", ".join(missing_files))
        if unexpected_files:
            details.append("unexpected: " + ", ".join(unexpected_files))
        raise BootstrapError(
            "Manifest output_files inventory does not match the 13 expected sources ("
            + "; ".join(details)
            + ")."
        )

    return counts


def verify_manifest_profile(manifest, selected_profile):
    """Verify generator validation status and the scale encoded in release_name."""
    if str(manifest.get("validation_status", "")).strip().lower() != "passed":
        raise BootstrapError("Manifest validation_status must be 'passed'.")
    release_name = manifest.get("release_name")
    if not isinstance(release_name, str) or not release_name.strip():
        raise BootstrapError("Manifest release_name must be a non-empty string.")

    normalized = release_name.strip().lower()
    expected_scale = "250k" if "250k" in selected_profile else ("50k" if "50k" in selected_profile else "5k")
    if not normalized.startswith(expected_scale + "_"):
        raise BootstrapError(
            f"Manifest release_name {release_name!r} does not identify the selected "
            f"{expected_scale} profile. Check the configured Raw Volume path."
        )
    return str(release_name)


def validate_business_schema(source_fields, bronze_fields):
    """Compare names, order, and types; report nullability without enforcing it."""
    business_fields = bronze_fields[: len(source_fields)]
    source_contract = [(field.name, field.dataType.simpleString()) for field in source_fields]
    bronze_contract = [(field.name, field.dataType.simpleString()) for field in business_fields]
    if source_contract != bronze_contract:
        return False, "Business-column names, order, or data types differ from Raw."
    source_nullability = [field.nullable for field in source_fields]
    bronze_nullability = [field.nullable for field in business_fields]
    note = "nullability unchanged"
    if source_nullability != bronze_nullability:
        note = "Delta-reported nullability differs (informational only)"
    return True, note


def _quote_identifier(value, label):
    if not IDENTIFIER_PATTERN.fullmatch(value or ""):
        raise BootstrapError(
            f"Invalid {label} {value!r}. Use only letters, numbers, and underscores, "
            "and do not start with a number."
        )
    return f"`{value}`"


def _column(name):
    """Quote a Spark column name so dots are not treated as nested-field separators."""
    from pyspark.sql import functions as F

    return F.col("`" + name.replace("`", "``") + "`")


def _read_manifest(dbutils, manifest_path):
    try:
        text = dbutils.fs.head(manifest_path, 10 * 1024 * 1024)
    except Exception as exc:
        raise BootstrapError(
            f"Cannot read {manifest_path}. Confirm that manifest.json was uploaded with "
            "the 13 Parquet files and that the notebook has Volume access."
        ) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"{manifest_path} is not valid JSON: {exc.msg}.") from exc


def _inventory_by_name(dbutils, raw_volume_path):
    try:
        entries = dbutils.fs.ls(raw_volume_path)
    except Exception as exc:
        raise BootstrapError(
            f"Cannot list Raw Volume path {raw_volume_path!r}. Check the configuration, "
            "uploaded files, and Volume permissions."
        ) from exc
    inventory = {}
    for entry in entries:
        name = _file_name(getattr(entry, "name", None) or getattr(entry, "path", None))
        if name in inventory:
            raise BootstrapError(f"Raw Volume contains duplicate inventory name {name!r}.")
        inventory[name] = entry
    return inventory


def _preflight_profile(spark, dbutils, profile, config):
    raw_path = config["raw_volume_path"].rstrip("/")
    manifest_path = f"{raw_path}/manifest.json"
    inventory = _inventory_by_name(dbutils, raw_path)
    expected_files = {f"{table}.parquet" for table in SOURCE_TABLES}
    actual_parquet = {name for name in inventory if name.lower().endswith(".parquet")}
    missing = sorted(expected_files - actual_parquet)
    unexpected = sorted(actual_parquet - expected_files)
    if missing or unexpected:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise BootstrapError(f"Raw file inventory problem for {profile} ({'; '.join(details)}).")
    if "manifest.json" not in inventory:
        raise BootstrapError(
            f"{profile} is missing its generator manifest. Expected path: {manifest_path}"
        )

    manifest = _read_manifest(dbutils, manifest_path)
    verify_manifest_profile(manifest, profile)
    manifest_counts = extract_manifest_counts(manifest)

    sources = {}
    for table in SOURCE_TABLES:
        file_name = f"{table}.parquet"
        entry = inventory[file_name]
        source_path = getattr(entry, "path", None) or f"{raw_path}/{file_name}"
        try:
            raw_df = spark.read.parquet(source_path)
            raw_count = raw_df.count()
        except Exception as exc:
            raise BootstrapError(
                f"Cannot read {source_path} as Parquet. Confirm that the correct source "
                "file was uploaded completely."
            ) from exc
        expected_count = manifest_counts[table]
        if raw_count != expected_count:
            raise BootstrapError(
                f"Count mismatch for {profile}.{table}: manifest={expected_count:,}, "
                f"Raw={raw_count:,}. Check that the manifest and Parquet files came from "
                "the same dataset package."
            )
        collision = sorted(set(raw_df.columns) & set(METADATA_COLUMNS))
        if collision:
            raise BootstrapError(
                f"Raw source {profile}.{table} uses reserved Bronze metadata column(s): "
                + ", ".join(collision)
            )
        sources[table] = {
            "path": source_path,
            "file_name": file_name,
            "file_size": getattr(entry, "size", None),
            "modification_time": getattr(entry, "modificationTime", None),
            "manifest_count": expected_count,
            "raw_count": raw_count,
            "source_fields": raw_df.schema.fields,
        }
    return sources


def _list_tables(spark, catalog, schema):
    catalog_sql = _quote_identifier(catalog, "catalog")
    schema_sql = _quote_identifier(schema, "Bronze schema")
    rows = spark.sql(f"SHOW TABLES IN {catalog_sql}.{schema_sql}").collect()
    return {row["tableName"] for row in rows}


def _add_metadata(raw_df, profile, run_id, source, ingested_ts):
    from pyspark.sql import functions as F

    source_columns = list(raw_df.columns)
    hash_inputs = [
        F.coalesce(_column(name).cast("string"), F.lit("__NULL__")) for name in source_columns
    ]
    record_hash = F.sha2(F.concat_ws("||", *hash_inputs), 256)

    modification_time = source["modification_time"]
    if isinstance(modification_time, (int, float)):
        modification_time = datetime.fromtimestamp(modification_time / 1000, tz=timezone.utc)

    return raw_df.select(
        "*",
        F.lit(run_id).alias("_pipeline_run_id"),
        F.lit("bronze_bootstrap").alias("_pipeline_name"),
        F.lit("1.0.0").alias("_pipeline_version"),
        F.lit(profile).alias("_release_name"),
        F.lit(source["file_name"]).alias("_source_file_name"),
        F.lit(source["path"]).alias("_source_file_path"),
        F.lit(source["file_size"]).cast("long").alias("_source_file_size"),
        F.lit(modification_time).cast("timestamp").alias("_source_file_modification_ts"),
        F.lit(ingested_ts).cast("timestamp").alias("_ingested_ts"),
        record_hash.alias("_source_record_hash"),
    )


def _display_results(spark, results):
    result_df = spark.createDataFrame(results).select(
        "dataset_profile",
        "source_table",
        "manifest_expected_count",
        "raw_record_count",
        "bronze_record_count",
        "validation_result",
        "details",
    )
    if "display" in globals():
        display(result_df.orderBy("dataset_profile", "source_table"))
    else:
        result_df.orderBy("dataset_profile", "source_table").show(100, truncate=False)


def run_bootstrap(spark, dbutils):
    """Preflight all selected inputs, publish tables, and display validation results."""
    action = existing_table_action.strip().lower()
    if action not in {"fail", "replace"}:
        raise BootstrapError("existing_table_action must be either 'fail' or 'replace'.")
    _quote_identifier(CATALOG, "catalog")
    for profile, config in PROFILE_CONFIG.items():
        _quote_identifier(config["bronze_schema"], f"Bronze schema for {profile}")

    # Create the default widget when run_bootstrap is invoked without running the
    # earlier widget cell first (for example, through Run all).
    try:
        dbutils.widgets.text("dataset_profiles", "napa_5k_clean", "Dataset profiles")
    except Exception:
        pass
    selected_profiles = select_profiles(dbutils.widgets.get("dataset_profiles"))
    print("Selected profiles: " + ", ".join(selected_profiles))
    print(f"Existing-table action: {action}")

    # UTC keeps timestamp metadata consistent across workspaces.
    spark.conf.set("spark.sql.session.timeZone", "UTC")

    # Validate every selected input before creating or replacing any table.
    preflight = {}
    for profile in selected_profiles:
        print(f"Preflight: validating manifest, inventory, schemas, and Raw counts for {profile}...")
        preflight[profile] = _preflight_profile(spark, dbutils, profile, PROFILE_CONFIG[profile])

    # Create only the selected schemas, then protect existing expected objects globally.
    existing_targets = []
    catalog_sql = _quote_identifier(CATALOG, "catalog")
    try:
        for profile in selected_profiles:
            schema = PROFILE_CONFIG[profile]["bronze_schema"]
            schema_sql = _quote_identifier(schema, "Bronze schema")
            spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_sql}.{schema_sql}")
            present = _list_tables(spark, CATALOG, schema)
            existing_targets.extend(
                f"{CATALOG}.{schema}.{table}" for table in SOURCE_TABLES if table in present
            )
    except Exception as exc:
        raise BootstrapError(
            "Cannot create or inspect a selected Bronze schema. Check CATALOG, the configured "
            "Bronze schema names, and your Unity Catalog permissions."
        ) from exc
    if existing_targets and action == "fail":
        raise BootstrapError(
            "Existing-table protection stopped the notebook before any Bronze writes. "
            "Existing expected target(s): "
            + ", ".join(existing_targets)
            + ". Keep 'fail' to preserve them, or review the targets and explicitly set "
            "existing_table_action = 'replace'."
        )
    if action == "replace":
        print("=" * 78)
        print("WARNING — INTENTIONAL BRONZE RELOAD")
        print("RELOAD MODE: replace")
        print("Selected dataset profile(s): " + ", ".join(selected_profiles))
        print("Exact destination schema(s):")
        for profile in selected_profiles:
            schema = PROFILE_CONFIG[profile]["bronze_schema"]
            print(f"  - {profile}: {CATALOG}.{schema}")
        print("Existing expected Bronze tables in these schemas will be replaced.")
        print("Previous content in those expected Bronze tables will not be preserved.")
        print("Unrelated tables and Raw Parquet files are not intended to be modified.")
        print("=" * 78)

    run_id = str(uuid.uuid4())
    results = []
    print(f"Bootstrap run ID: {run_id}")
    try:
        for profile in selected_profiles:
            config = PROFILE_CONFIG[profile]
            schema = config["bronze_schema"]
            schema_sql = _quote_identifier(schema, "Bronze schema")
            for table in SOURCE_TABLES:
                source = preflight[profile][table]
                table_sql = _quote_identifier(table, "Bronze table")
                target_name = f"{catalog_sql}.{schema_sql}.{table_sql}"
                ingested_ts = datetime.now(timezone.utc)
                raw_df = spark.read.parquet(source["path"])
                bronze_df = _add_metadata(raw_df, profile, run_id, source, ingested_ts)
                bronze_df.write.format("delta").mode("overwrite").option(
                    "overwriteSchema", "true"
                ).saveAsTable(target_name)

                persisted_df = spark.table(target_name)
                bronze_count = persisted_df.count()
                schema_ok, schema_note = validate_business_schema(
                    source["source_fields"], persisted_df.schema.fields
                )
                metadata_ok = tuple(persisted_df.columns[len(source["source_fields"]) :]) == METADATA_COLUMNS
                counts_ok = (
                    source["manifest_count"] == source["raw_count"] == bronze_count
                )
                passed = schema_ok and metadata_ok and counts_ok
                details = [schema_note]
                if not metadata_ok:
                    details.append("required metadata columns are missing or out of order")
                if not counts_ok:
                    details.append("manifest, Raw, and Bronze counts do not agree")
                results.append(
                    {
                        "dataset_profile": profile,
                        "source_table": table,
                        "manifest_expected_count": source["manifest_count"],
                        "raw_record_count": source["raw_count"],
                        "bronze_record_count": bronze_count,
                        "validation_result": "PASS" if passed else "FAIL",
                        "details": "; ".join(details),
                    }
                )

        # Final inventory validation checks expected tables without rejecting unrelated work.
        for profile in selected_profiles:
            schema = PROFILE_CONFIG[profile]["bronze_schema"]
            present = _list_tables(spark, CATALOG, schema)
            missing_tables = sorted(set(SOURCE_TABLES) - present)
            if missing_tables:
                raise BootstrapError(
                    f"Bronze inventory for {profile} is missing: {', '.join(missing_tables)}."
                )

        _display_results(spark, results)
        failed = [row for row in results if row["validation_result"] != "PASS"]
        if failed:
            raise BootstrapError(
                f"Overall FAIL: {len(failed)} of {len(results)} table validations failed. "
                "Review the displayed details before continuing to Silver."
            )
        print(f"OVERALL PASS: {len(results)} Bronze tables validated for run {run_id}.")
    except BootstrapError:
        if results:
            _display_results(spark, results)
        raise
    except Exception as exc:
        if results:
            _display_results(spark, results)
        raise BootstrapError(
            "Bronze bootstrap stopped during table creation or validation. Review the last "
            "profile/table shown above and the first underlying Spark error. Existing tables "
            "are not automatically deleted."
        ) from exc


# COMMAND ----------
if "spark" in globals() and "dbutils" in globals():
    try:
        run_bootstrap(spark, dbutils)
    except BootstrapError as exc:
        print(f"OVERALL FAIL: {exc}")
        raise
