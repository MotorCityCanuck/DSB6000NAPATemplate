# Student AI Build Prompt: NAPA Raw-to-Bronze Pipeline

**Purpose:** Give this complete construction specification to your AI coding assistant to build a configuration-driven NAPA Raw-to-Bronze pipeline. You and your team remain responsible for reviewing the generated implementation, running it, validating the results, and explaining the decisions. The specification is standalone; no completed pipeline or unpublished repository is required.

**Student review:** Read the requirements before construction. You may propose and document justified changes, but do not silently weaken the source-preservation, manifest-validation, namespace-safety, or acceptance requirements.

> ## Task
>
> You are working in a Databricks/PySpark repository for the NAPA Olympic Analytics Platform. Build a configuration-driven **Raw-to-Bronze** pipeline from the supplied Raw Parquet files using the complete construction contract below. The repository may be a clean student template with no existing pipeline code. Inspect it before changing it, preserve its existing structure where reasonable, make focused changes, and do not invent data fields, source schemas, row counts, or results.
>
> Your deliverable must satisfy the following functional contract. Do not seek or assume access to an existing completed pipeline. If a repository convention conflicts with this contract, stop, identify the conflict, and explain it before choosing an approach.
>
> ### Scope and boundaries
>
> Include only Raw-to-Bronze responsibilities:
>
> - automatically initialize release-specific Unity Catalog schemas and validate student-prepared Raw Volumes;
> - validate the colocated `manifest.json`, delivered Raw-file inventory, and Parquet readability;
> - destructively refresh the selected Bronze schema, then copy each source into a managed Bronze Delta table with operational metadata appended;
> - record operational audit evidence and schema snapshots;
> - reconcile manifest, Raw, and Bronze row counts and column contracts;
> - provide a Databricks Asset Bundle job plus local unit tests.
>
> Explicitly exclude Silver cleansing, source-field renaming, type standardization, business-rule validation, deduplication, referential-integrity enforcement, feature engineering, analytics, models, roster recommendations, streaming, Auto Loader, CDC, and incremental `MERGE` into Bronze data tables. Delta `MERGE` is used to finalize the operations run record. Bronze must preserve duplicates, nulls, invalid business values, source attributes, and relationships exactly as delivered, without synthetic correction. Every ingest run is a destructive full refresh of the selected profile's dedicated Bronze schema: clear that schema once during run initialization, before publication, so no output from an earlier execution is carried forward. Do not clear it again after a failure. Tables successfully written before a failure remain available as incomplete diagnostic evidence until a subsequent execution performs its normal initialization reset.
>
> Do not commit source data, generated Delta storage, credentials, tokens, or personal workspace paths. Do not hard-code Windows paths, a cluster ID, or a personal Databricks path.
>
> ### Databricks Free Edition runtime compatibility
>
> Target Databricks Free Edition serverless with the active Databricks `SparkSession`, explicit schemas, Delta-compatible operations, and supported documented APIs. For Unity Catalog discovery, prefer documented SQL metadata statements such as `SHOW CATALOGS`, `SHOW SCHEMAS`, and `SHOW VOLUMES`, with safely validated and quoted identifiers where parameters are needed. Do **not** call `spark.catalog.catalogExists()`; it is not supported in the validated Free Edition serverless path. Do not invent Spark methods, depend on custom clusters, or assume local-only Spark behavior exists in Databricks. Permission denials and metadata-query failures must remain visible and must not be converted into an "object missing" result.
>
> Keep three acceptance stages separate: (1) local unit tests, (2) Databricks Asset Bundle validation, and (3) controlled live execution in Databricks Free Edition. Local mocks and test doubles must use only runtime-supported interfaces and must not conceal an unsupported API. Neither local success nor bundle validation proves live runtime compatibility or production readiness.
>
> ### First actions: inspect and report before editing
>
> 1. Read `AGENTS.md` if present, the root `README.md`, and relevant documentation, bundle configuration, notebooks, source modules, and tests that actually exist in the student repository. Missing optional starter files are not a reason to stop construction.
> 2. Run `git status --short`, `git branch --show-current`, and `git remote -v`. Report unrelated existing changes before editing them.
> 3. Identify whether the repository already has an equivalent configuration/package/test convention. Reuse it rather than introducing a framework or dependency unnecessarily.
> 4. State the files you will create or change, the assumptions that depend on the delivered data, and the validation plan. Then implement.
>
> ### Required runtime design
>
> Build one shared implementation supporting these five dataset profiles:
>
> | Dataset profile / release name | Role | Data condition | Raw schema | Bronze schema | Raw Volume path |
> |---|---|---|---|---|---|
> | `napa_5k_clean` | development | clean | `napa_platform_5k_clean_raw` | `napa_platform_5k_clean_bronze` | `/Volumes/workspace/napa_platform_5k_clean_raw/napa_files` |
> | `napa_5k_tainted` | development | tainted | `napa_platform_5k_tainted_raw` | `napa_platform_5k_tainted_bronze` | `/Volumes/workspace/napa_platform_5k_tainted_raw/napa_files` |
> | `napa_50k_clean` | validation | clean | `napa_platform_50k_clean_raw` | `napa_platform_50k_clean_bronze` | `/Volumes/workspace/napa_platform_50k_clean_raw/napa_files` |
> | `napa_50k_tainted` | validation | tainted | `napa_platform_50k_tainted_raw` | `napa_platform_50k_tainted_bronze` | `/Volumes/workspace/napa_platform_50k_tainted_raw/napa_files` |
> | `napa_250k_production` | production-scale case data | production | `napa_platform_250k_raw` | `napa_platform_250k_bronze` | `/Volumes/workspace/napa_platform_250k_raw/napa_files` |
>
> Use catalog `workspace` and the shared operations schema `napa_platform_ops` as defaults, but put those values in configuration rather than scattering them through code. The Raw Volume name is `napa_files`. The processing mode is `full_refresh`. Use the same code and source registry for all profiles; only the environment configuration may vary.
>
> The names above are illustrative defaults. Before running writes, resolve the team's assigned catalog and prefix in configuration. Keep the naming pattern `<team_prefix>_<scale>_<condition>_raw` and `<team_prefix>_<scale>_<condition>_bronze` for 5K/50K clean and tainted profiles; use `<team_prefix>_250k_raw` and `<team_prefix>_250k_bronze` for the single 250K production profile; and use shared `<team_prefix>_ops`. The five profiles are independent full-refresh datasets, not monthly increments; `monthly_batches.parquet` is an input table and does not drive incremental processing. Do not allow a clean or tainted selector for the 250K production dataset.
>
> Raw files and the matching `manifest.json` must already be placed directly in each configured Volume; the pipeline does not create or modify the Raw Volume and does not upload, generate, move, replace, delete, or copy its files. Do not add an extra release subdirectory. The manifest is part of the delivered Raw input, is not a Bronze source table, and must be read from the same directory as the Parquet files. Confirm authenticated Databricks CLI access, a usable catalog, serverless job access, and permissions to create/use the configured schemas and tables and to read the existing Volume. Environment setup does not create a catalog, create a Raw Volume, or grant privileges.
>
> The source registry must enable the following sources, in this exact build order. Each configured key is a source-designated logical or natural key used as descriptive metadata for downstream consumers. It is not a physically enforced uniqueness constraint in Raw or Bronze. Do **not** use it to filter, reject, select, or deduplicate Bronze rows; duplicate-key enforcement belongs to Bronze-to-Silver.
>
> | Order | Source name / Bronze table | Raw file | Key column(s) |
> |---:|---|---|---|
> | 10 | `regions` | `regions.parquet` | `id` |
> | 20 | `clubs` | `clubs.parquet` | `id` |
> | 30 | `club_memberships` | `club_memberships.parquet` | `id` |
> | 40 | `player_master` | `player_master.parquet` | `player_id` |
> | 50 | `player_registrations` | `player_registrations.parquet` | `id` |
> | 60 | `player_assessment_history` | `player_assessment_history.parquet` | `id` |
> | 70 | `teams` | `teams.parquet` | `id` |
> | 80 | `team_memberships` | `team_memberships.parquet` | `id` |
> | 90 | `matches` | `matches.parquet` | `id` |
> | 100 | `match_teams` | `match_teams.parquet` | `id` |
> | 110 | `match_team_players` | `match_team_players.parquet` | `id` |
> | 120 | `match_games` | `match_games.parquet` | `id` |
> | 130 | `monthly_batches` | `monthly_batches.parquet` | `id` |
>
> Do not fabricate field-level source schemas in YAML. The delivered Parquet schemas are the source of truth for Bronze. Capture their actual schema evidence at runtime.
>
> ### Required configuration
>
> Use the repository's equivalent of the following configuration layout (adapt paths only if the existing repository has a documented alternative):
>
> ```text
> config/raw_to_bronze/
>   base.yml
>   raw_sources.yml
>   logging.yml
>   environments/
>     napa_5k_clean.yml
>     napa_5k_tainted.yml
>     napa_50k_clean.yml
>     napa_50k_tainted.yml
>     napa_250k_production.yml
> ```
>
> Implement a configuration loader that:
>
> - accepts only `napa_5k_clean`, `napa_5k_tainted`, `napa_50k_clean`, `napa_50k_tainted`, and `napa_250k_production`;
> - deep-merges `base.yml`, the selected environment file, the common source registry, and logging configuration without mutating inputs;
> - resolves `${section.nested_key}` placeholders repeatedly until all are resolved, and fails on an unknown or unresolved placeholder;
> - validates required top-level sections (`project`, `runtime`, `objects`, `execution`, `publication`, `metadata`, `performance`, `release`, `schemas`, `volume`, `sources`, `logging`), matching selected/reported dataset profile, valid `release.data_condition` (`clean`, `tainted`, or `production`), disallows `clean`/`tainted` conditions for the 250K profile and disallows `production` for 5K/50K profiles, `full_refresh` processing mode, agreement between `volume.name` and `objects.raw_volume_name`, `volume.manifest_name == manifest.json`, valid `.parquet` source filenames, nonempty source mapping, nonempty `bronze_table` values, and unique integer build order across all configured sources;
> - fails on missing YAML files or non-mapping file content;
> - produces the configuration hash as SHA-256 of UTF-8 encoded `yaml.safe_dump(resolved_config, sort_keys=True)`;
> - exposes enabled sources in ascending build order.
>
> Configure these defaults:
>
> ```yaml
> project:
>   name: napa_olympic_analytics
>   pipeline_name: raw_to_bronze
>   pipeline_version: "1.0.0"
>   processing_mode: full_refresh
> runtime:
>   catalog: workspace
>   team_prefix: napa_platform
>   default_release: napa_5k_clean
>   timezone: America/New_York
> objects:
>   raw_volume_name: napa_files
>   operations_schema: ${runtime.team_prefix}_ops
> publication:
>   format: delta
>   mode: overwrite
>   overwrite_schema: true
> execution:
>   fail_fast: true
>   require_exact_source_inventory: true
>   unexpected_file_policy: fail
>   missing_file_policy: fail
> ```
>
> `config/dataset_config.example.yml` is a planning example, not an independent runtime configuration source. Map its single `shared_operations_schema` value to generated runtime `objects.operations_schema`. In each of the five generated environment profiles, set `schemas.operations: ${objects.operations_schema}`; do not copy or redefine the namespace independently per profile. After placeholder resolution, configuration validation must require every profile's `schemas.operations` to equal the single resolved `objects.operations_schema` exactly. Reject conflicting literals, conflicting overrides, or unresolved placeholders before schema initialization or any write.
>
> Complete the configuration with the following required values and documented behavior. Do not assume a flag implements functionality unless the construction contract explicitly specifies that behavior.
>
> | Section | Additional configuration values |
> |---|---|
> | `execution` | `unexpected_column_policy: fail`, `missing_required_column_policy: fail`, `type_mismatch_policy: fail`, `publish_only_after_validation: true`, `destructive_bronze_refresh: true`, `cleanup_bronze_on_failure: false`, `retain_partial_bronze_on_failure: true`; manifest-matched readable zero-row inputs are allowed |
> | `publication` | `use_staging: false`; publish directly into the freshly recreated Bronze schema |
> | `metadata` | The ten metadata columns in Step 5 are mandatory, including `_pipeline_name`; define their fixed ordered list in configuration rather than exposing ineffective per-column switches |
> | `performance` | `cache_source_during_reconciliation: false`, `optimize_after_publish: false`, `vacuum_after_publish: false` |
> | `logging` | `default_level: INFO`; message codes `CONFIG_LOADED`, `SCHEMA_ALREADY_EXISTS`, `SCHEMA_CREATED`, `SCHEMA_VERIFIED`, `SCHEMA_INITIALIZATION_FAILED`, `ENVIRONMENT_VALIDATED`, `BRONZE_SCHEMA_RESET`, `BRONZE_PARTIAL_OUTPUT_RETAINED`, `RAW_FILE_MISSING`, `RAW_FILE_UNEXPECTED`, `SOURCE_SCHEMA_MISMATCH`, `SOURCE_READ_STARTED`, `SOURCE_READ_COMPLETED`, `BRONZE_WRITE_STARTED`, `BRONZE_WRITE_COMPLETED`, `ROW_COUNT_MISMATCH`, `PIPELINE_SUCCESS_READY`, `PIPELINE_FAILED` |
>
> Each environment file supplies `release.release_name` and `release.dataset_profile` (one of the five profiles above), `release.expected_player_scale` (5000/50000/250000), `release.data_condition` (`clean`, `tainted`, or `production`), `release.role` (`development`/`validation`/`production`), `schemas.raw`, `schemas.bronze`, `schemas.operations: ${objects.operations_schema}`, `volume.name: ${objects.raw_volume_name}`, `volume.manifest_name: manifest.json`, and `volume.path: /Volumes/${runtime.catalog}/${schemas.raw}/${objects.raw_volume_name}`. `performance.shuffle_partitions` is 16 for 5K, 64 for 50K, and `auto` for 250K. Each registry entry contains `enabled: true`, `file_name`, `bronze_table`, `build_order`, a descriptive `grain`, and `key_columns` from the source table above.
>
> Enforce the behavior explicitly described here. Readable zero-row data is permitted only when it agrees with the delivered manifest; readiness uses the manifest as its source contract, not an invented fixed field schema. Publication is direct, not staged, and all ten ordered metadata columns are always appended. Performance and optimization settings are informational unless explicitly implemented; optimization is not required for this assignment. Missing files fail validation, and unexpected inventory entries follow the configured inventory policy. Log the prescribed diagnostic events without presenting a logging-code list as an exhaustive restriction.
>
> ### Multi-step build plan
>
> Implement and validate each step before moving to the next.
>
> 1. **Configuration and package foundation.** Create a small reusable Python package, for example `src/napa_pipeline/raw_to_bronze/`, with focused modules for configuration, environment setup, inventory, Bronze publication, reconciliation, operations, finalization, and CLI helpers. Keep Databricks scripts/notebooks thin orchestration entrypoints.
>
> 2. **Automatic schema initialization, production environment validation, and start-of-run destructive Bronze reset.** Load and completely validate the selected profile configuration and namespace safety, then validate `execution_type`. Determine required schemas from that validated configuration only. `OPERATIONS_VALIDATION` requires only the configured operations schema. `RAW_TO_BRONZE` requires only the selected profile's configured Raw and Bronze schemas plus the configured shared operations schema. Verify that the configured catalog exists; never create a catalog. For each required schema, safely quote its separately validated catalog and schema identifier, issue `CREATE SCHEMA IF NOT EXISTS`, and verify existence and accessibility. Never hard-code instructor namespace text, append an environment-specific prefix/suffix, initialize another profile, or infer a profile from existing objects. Never use `DROP SCHEMA`, `ALTER SCHEMA`, `REPLACE SCHEMA`, `CASCADE`, ownership changes, permission changes, destructive rollback, or data deletion during this automatic initialization. Preserve successfully created schemas if a later schema fails, report the affected fully qualified schema with the underlying exception chained, stop initialization, and do not authorize Bronze reset. Existing schemas and their contents remain unchanged.
>
> For `RAW_TO_BRONZE`, after schema initialization perform a separate read-only environment preflight for the selected profile's configured Raw schema, Bronze schema, shared operations schema, Raw Volume name, and Raw Volume path. Query the Raw schema's Volumes and require the configured Raw Volume to exist and be accessible. Never create or modify the Raw Volume. After confirming that the resolved Bronze schema belongs to the selected dataset profile and is the configured dedicated target, initialize and verify the operations tables, establish the prescribed run context and run ID, persist and read back the current run's `RUNNING` record, and persist available schema-initialization diagnostics as specified in Step 3. Schema creation alone does not grant reset readiness. If the complete evidence cannot be established, fail before altering Bronze. A later implementation performs the required initialization reset exactly once only after that authorization: drop the selected Bronze schema with `DROP SCHEMA IF EXISTS <catalog>.<bronze_schema> CASCADE`, then recreate it with `CREATE SCHEMA <catalog>.<bronze_schema>`. Do not drop or recreate the Raw schema, Raw Volume, operations schema, or any schema outside the selected profile. Do not proceed if the fully qualified target cannot be resolved safely. The initialization reset intentionally removes all tables, views, data, and prior partial-run artifacts in only that selected schema. A failure after this reset must not trigger another reset or cleanup; retain whatever selected-profile Bronze tables were successfully published for investigation. Do not write transformed data into the Raw Volume. This full Raw/Volume/Bronze/operations contract remains mandatory for production execution and for authorization of the future Bronze reset.
>
> 3. **Run context and operations tables.** Generate one UUID `pipeline_run_id` per workflow run, then use it in every task and every audit record. Its context must include pipeline name/version, release, processing mode, configuration hash, and fully qualified operations schema. Create these managed Delta tables if absent:
>
> | Table | Required fields |
> |---|---|
> | `pipeline_runs` | run ID, pipeline name/version, release, mode, execution type, config hash, optional workflow/trigger IDs, status, start/end timestamps, duration, error class/message |
> | `table_runs` | run ID, pipeline/release, source file/table, target table, status, start/end/duration, file size, Raw/Bronze counts and difference, source/Bronze schema hashes, error |
> | `schema_snapshots` | run ID, pipeline/release, layer, object, column name/type/nullability/ordinal, schema hash, capture timestamp |
> | `reconciliation_results` | run ID, pipeline/release, source file, Bronze table, Raw/Bronze counts and difference, Raw/Bronze business-column counts, metadata count, status, evaluation timestamp |
> | `manifest_validation_results` | run ID, selected dataset profile, optional source table, validation type/target, expected and observed values, status, error, validation timestamp |
> | `run_messages` | run ID, pipeline/release, optional source name, message level/code/text, timestamp |
>
> Record a `RUNNING` pipeline row after schema initialization and non-destructive environment checks succeed and before the selected Bronze schema is reset. Every row has required `execution_type`: use `RAW_TO_BRONZE` for production ingestion and `OPERATIONS_VALIDATION` only for the scoped operations-validation workflow. Both execution types use the same configured operations schema; do not create a separate validation schema. `execution_type` identifies what ran, while `status` independently records `RUNNING`, `SUCCEEDED`, or `FAILED`. Use UTC-aware timestamps and calculate duration from start and completion timestamps. After the RUNNING row is read back, persist buffered initialization messages including `CONFIG_LOADED`, `SCHEMA_ALREADY_EXISTS` or `SCHEMA_CREATED`, `SCHEMA_VERIFIED`, and `ENVIRONMENT_VALIDATED`; use `SCHEMA_INITIALIZATION_FAILED` only when operations logging is genuinely available and never fabricate durable evidence before it is. Continue with messages such as `BRONZE_SCHEMA_RESET`, `BRONZE_PARTIAL_OUTPUT_RETAINED`, `BRONZE_WRITE_STARTED`, `BRONZE_WRITE_COMPLETED`, `ROW_COUNT_MISMATCH`, `PIPELINE_SUCCESS_READY`, and `PIPELINE_FAILED`. `PIPELINE_SUCCESS_READY` truthfully records that required checks and diagnostics passed while terminal success persistence is still pending; it is not a successful release marker. Preserve operations history across executions; neither initialization nor failure handling may reset or overwrite prior run evidence except for the prescribed finalization update of the current open pipeline row.
>
> Use these exact operations column names and types. In the following contract, `!` means `NOT NULL`; all other columns are nullable. Every table uses Delta. Keep the listed column order for compatibility.
>
> ```text
> pipeline_runs:
>   pipeline_run_id STRING!, pipeline_name STRING!, pipeline_version STRING!,
>   release_name STRING!, processing_mode STRING!, execution_type STRING!,
>   configuration_hash STRING!,
>   workflow_run_id STRING, status STRING!, started_ts TIMESTAMP!,
>   completed_ts TIMESTAMP, duration_seconds DOUBLE, triggered_by STRING,
>   error_class STRING, error_message STRING
> table_runs:
>   pipeline_run_id STRING!, pipeline_name STRING!, release_name STRING!,
>   source_file_name STRING!, source_table STRING!, target_table STRING!,
>   status STRING!, started_ts TIMESTAMP!, completed_ts TIMESTAMP,
>   duration_seconds DOUBLE, source_file_size BIGINT, source_row_count BIGINT,
>   bronze_row_count BIGINT, row_count_difference BIGINT,
>   source_schema_hash STRING, bronze_schema_hash STRING, error_message STRING
> schema_snapshots:
>   pipeline_run_id STRING!, pipeline_name STRING!, release_name STRING!,
>   layer_name STRING!, object_name STRING!, column_name STRING!, data_type STRING!,
>   nullable BOOLEAN, ordinal_position INT, schema_hash STRING!, captured_ts TIMESTAMP!
> reconciliation_results:
>   pipeline_run_id STRING!, pipeline_name STRING!, release_name STRING!,
>   source_file_name STRING!, bronze_table STRING!, raw_row_count BIGINT!,
>   bronze_row_count BIGINT!, row_count_difference BIGINT!,
>   raw_business_column_count INT!, bronze_business_column_count INT!,
>   metadata_column_count INT!, status STRING!, evaluated_ts TIMESTAMP!
> manifest_validation_results:
>   pipeline_run_id STRING!, dataset_profile STRING!, source_table STRING,
>   validation_type STRING!, validation_target STRING!, expected_value STRING,
>   observed_value STRING, validation_status STRING!, error_message STRING,
>   validated_at TIMESTAMP!
> run_messages:
>   pipeline_run_id STRING!, pipeline_name STRING!, release_name STRING!,
>   source_name STRING, message_level STRING!, message_code STRING!,
>   message_text STRING!, created_ts TIMESTAMP!
> ```
>
> Append audit records using the target table's explicit schema, including records with null values; do not infer their types. Empty record lists are a no-op. Reject any `pipeline_runs.execution_type` other than `RAW_TO_BRONZE` or `OPERATIONS_VALIDATION`. `table_runs` stores separate appended `RUNNING` and terminal rows, so an ordinary successful ingestion run has 26 table-run rows, of which 13 have `completed_ts`. The original `RUNNING` table rows are not updated. Pipeline finalization updates its open pipeline row without changing its execution type. `workflow_run_id` and `triggered_by` are nullable; populate them only when trustworthy runtime values are available. Normalize naive audit start/end timestamps as UTC and convert aware timestamps to UTC before calculating duration. `manifest_validation_results.pipeline_run_id` is a logical relationship to `pipeline_runs.pipeline_run_id`; `source_table`, when populated, is the configured source entity and relates the result to the corresponding source registry and table-run evidence. No primary-key or unique constraint is prescribed for the validation table because one run may record multiple checks for the same source and target.

> An `OPERATIONS_VALIDATION` execution uses a separate non-destructive initialization and preflight contract. It validates the selected profile configuration, verifies the configured catalog, automatically creates only the shared operations schema if missing with `CREATE SCHEMA IF NOT EXISTS`, verifies schema accessibility, and then performs the operations-specific read-only environment preflight. It must not inspect, require, initialize, create, read, or modify a Raw schema, Raw Volume, Bronze schema, Bronze table, or Raw Parquet file. Missing catalogs, permission failures, or inaccessible schemas fail visibly. After that preflight, the execution initializes all six operations tables and verifies every physical column name, order, type, and reliably reported nullability against the definitions above before it establishes the prescribed run context, persists, and reads back its typed `RUNNING` row. It then records `SCHEMA_ALREADY_EXISTS` or `SCHEMA_CREATED` and `SCHEMA_VERIFIED` evidence for the operations schema where operations logging is available. If schema initialization fails before operations storage is available, propagate the chained exception without fabricating a pipeline row or durable diagnostic. Missing, unexpected, reordered, incorrectly typed, or incorrectly nullable columns fail with a table-specific diagnostic. Never drop, replace, or recreate an incompatible existing table; preserve its historical data for investigation. The execution exercises explicit-schema operations and diagnostic persistence and finalizes `SUCCEEDED` only when those checks pass. A validation failure finalizes `FAILED` wherever operations storage remains available and fails the Databricks job while retaining diagnostics. This workflow must never reset Bronze, read Raw Parquet, publish Bronze, modify Silver or Gold, or claim production ingestion success. It is not subject to the 13-source ingestion completion gate. Its successful record cannot authorize Bronze reset or Silver processing.
>
> 4. **Manifest, inventory, and readiness validation.** List the selected Raw Volume using `dbutils.fs.ls`. Require exactly one readable `manifest.json` in the same directory as the Parquet files; do not treat it as an ignorable inventory entry. `release_manifest.json`, if supported by the repository convention, may remain a non-source auxiliary file, but it must not replace or override `manifest.json`. Parse the manifest and require a per-source contract for every enabled source. The manifest's `output_files` entries are the authoritative delivered-file metadata: `file_name`/`file_path`, `table_name`, `checksum`, `row_count`, ordered `columns`, and `schema_hash`. Normalize trailing slashes from file names and paths before comparison. The selected configuration profile and isolated Volume/schema path identify whether the package is 5K clean, 5K tainted, 50K clean, 50K tainted, or 250K production; do not require a new clean/tainted field in the existing manifest. Preserve the manifest's own release metadata as source evidence and record the selected profile alongside it. Fail before Bronze publication if the manifest is missing, malformed, duplicated, missing a configured source, contains an unexpected source, points to a missing/unexpected file, or disagrees with the configured source-to-table mapping. For every configured file, capture file path, size when available, and modification timestamp when available; read it with `spark.read.parquet`; calculate its row count; capture each field as column name, `simpleString()` data type, and nullability; calculate the same ordered schema hash used by the manifest; calculate the SHA-256 checksum of the delivered Parquet file bytes; and compare the actual checksum, row count, ordered column list, and schema hash to the manifest before publication. Any mismatch or unreadable Parquet must fail the task and prevent Bronze publication. The manifest itself is not copied into a Bronze data table.
>
> Persist every required comparison to `<catalog>.<operations_schema>.manifest_validation_results` using the configured catalog and operations schema and the explicit table schema above. Do not hard-code a team or instructor namespace. Record checks for manifest and source-file existence, configured source-to-file/table mapping, expected inventory, ordered columns, schema hash, row count, checksum, Parquet readability, and every other required manifest validation. Core `validation_type` codes are `FILE_EXISTENCE`, `SOURCE_MAPPING`, `INVENTORY`, `PARQUET_READABILITY`, `ROW_COUNT`, `ORDERED_COLUMNS`, `SCHEMA_HASH`, `CHECKSUM`, and `MANIFEST_METADATA`; additional codes may represent another explicit manifest contract check without replacing these required categories. Complete successful coverage includes package-level manifest existence/readability, inventory, and required manifest metadata checks, plus `FILE_EXISTENCE`, `SOURCE_MAPPING`, `PARQUET_READABILITY`, `ROW_COUNT`, `ORDERED_COLUMNS`, `SCHEMA_HASH`, and `CHECKSUM` evidence for every enabled source. Store scalar expected/observed values as strings and serialize lists or structured values as deterministic JSON strings so equivalent evidence compares consistently. Use `validation_status = PASSED` when the observed value satisfies the expectation, `FAILED` when a completed comparison disagrees or a required item is missing/unexpected, and `ERROR` when the validation itself cannot be completed. `error_message` is nullable for `PASSED` and ordinary `FAILED` comparisons but must contain diagnostic detail for `ERROR`; `expected_value` or `observed_value` may be null when a value is genuinely unavailable. For missing or unexpected files, use a `FILE_EXISTENCE` validation with a target that identifies the file and string values such as `present`, `missing`, or `unexpected`. For source-independent package or manifest checks, leave `source_table` null; otherwise populate it with the configured source entity. Persist successful, failed, and error rows before raising wherever operations storage remains available. Never delete or replace prior executions' validation rows. Any required `FAILED` or `ERROR` result, or missing required validation coverage, fails readiness and must contribute to a terminal `FAILED` pipeline outcome.
>
> Fall back to the path's final component when a listing entry has no name. Use the listing's actual path, including any `dbfs:` prefix, for reads and lineage. Modification times may be absent, already be datetime values, or be epoch milliseconds; normalize available values to UTC-aware timestamps, including conversion of epoch milliseconds. Keep missing modification timestamps nullable rather than inventing values.
>
> Hash a schema by joining ordered `column_name:data_type:nullable` strings with `|`, then applying SHA-256 to UTF-8 bytes; use Python's `True`, `False`, or `None` spelling. Schema snapshot ordinals start at 1. Raw `object_name` is the source filename, and Bronze `object_name` is the unqualified Bronze table name. Append Raw snapshots only after all sources pass readiness. Construction and reconciliation must independently verify that their inputs remain manifest-matched; they need not share in-memory DataFrames across separate tasks. Keep Raw files unchanged throughout a run.
>
> 5. **Bronze construction.** For each source in build order, first require that the Raw readiness record is manifest-matched, then read the Parquet file again and retain every original column in its original order. Fail if a source already has any of the reserved metadata column names below. Append these columns in this exact order:
>
> ```text
> _pipeline_run_id
> _pipeline_name
> _pipeline_version
> _release_name
> _source_file_name
> _source_file_path
> _source_file_size
> _source_file_modification_ts
> _ingested_ts
> _source_record_hash
> ```
>
> Use the shared run context and file-readiness record for the first eight values; use the table's UTC start timestamp for `_ingested_ts` in the workflow. Any helper invoked without an explicit ingestion timestamp must also use a UTC-aware timestamp. Compute `_source_record_hash` with Spark built-in functions only: cast every **original source column** to string, replace null with the literal `__NULL__`, concatenate values in original source-column order with `||`, then apply SHA-256. These casts apply only inside the hash expression, not to stored business columns. Do not collect source data to the driver, use Python UDFs, join, filter, sort, or otherwise transform business rows. Duplicate source rows must remain duplicate Bronze rows, even if their hashes match. The hash encoding does not escape `||` or the null sentinel, so it is not a guaranteed unique row key.
>
> 6. **Full-refresh Delta publication and table metadata.** For each configured target `catalog.bronze_schema.bronze_table`, write the enriched DataFrame using `format("delta")`, `mode("overwrite")`, `option("overwriteSchema", "true")`, and `saveAsTable`. The start-of-run schema reset has already removed prior tables and data; table-level overwrite remains required for deterministic reruns and must never be replaced with append. Then apply a table comment stating that it is a Raw-preserving Delta representation for the release, and set these table properties: `napa.layer=bronze`, `napa.release=<release>`, `napa.pipeline=raw_to_bronze`, and `napa.processing_mode=full_refresh`. Record table start and terminal success/failure audit rows. On a failed source, persist error evidence, re-raise, and retain every table that was successfully published earlier in the current run. Mark the run incomplete and unsuitable for Silver; do not present retained partial tables as a successful release. A subsequent whole-workflow rerun must create a new run ID, reset the selected schema during initialization, and publish exactly the 13 configured Bronze tables rather than append or retain prior tables.
>
> Count the enriched DataFrame and capture its schema/hash before writing. After successful publication and table metadata updates, append its Bronze schema snapshots. The stored table-run Bronze count is this pre-write count; task 5 separately counts the persisted table. Both count differences are `bronze - raw`. Raw and Bronze full-schema hashes normally differ because Bronze includes metadata; do not require their equality. The exact table comment is `Raw-preserving Delta representation of the NAPA <source_name> Parquet file for release <release_name>. Business values are unchanged; operational ingestion metadata is appended.`
>
> Publication writes directly into the selected Bronze schema; there is no staging, release-wide transaction, or rollback of previously published tables. A comment/property error can fail a build after some tables have been written. Retain those selected-profile tables and any available schema snapshots, table-run records, messages, and diagnostics. Record `BRONZE_PARTIAL_OUTPUT_RETAINED` when partial tables remain. The Raw schema, Raw Volume, operations schema, and all historical operations evidence must remain intact for diagnosis and rerun. Wrap publication failures as `BronzePublicationError` with the original exception chained; record `BRONZE_WRITE_FAILED` and preserve the root-cause traceback in job logs. Record other failure evidence where audit storage is available, without promising durable records when storage itself is unavailable. Whole-run idempotency means unchanged inputs produce the same business rows/counts after the next execution performs its initialization reset; run IDs, ingestion timestamps, and appended audit history intentionally change.
>
> 7. **Reconciliation.** For each target table, read it back and compare it to its manifest-matched Raw readiness record. The helper returns `MATCHED` only for matching manifest/Raw/Bronze row counts, all ten metadata columns, all manifest/Raw business columns, no additional business columns, and exact manifest/Raw business-column order; otherwise it returns `MISMATCH`. It does not compare business values, hashes, data types, nullability, metadata values/types, or the order of the metadata columns unless the team explicitly adds those checks. A column-order mismatch is therefore a reconciliation failure and must be treated the same as a row-count, missing-column, or unexpected-column mismatch. The task must persist all reconciliation results and relevant diagnostic messages before raising, wherever audit storage is available. After persistence, the task must raise a reconciliation failure whenever any result has `status != "MATCHED"`; it must never log or report successful reconciliation when any source has a `MISMATCH`. An unreadable target raises `ReconciliationError`, logs `SCHEMA_RECONCILIATION_FAILED`, and exits only after any available buffered results and diagnostics are persisted. Finalization must continue to evaluate the persisted reconciliation results and mark the pipeline `FAILED` if any result is not `MATCHED`.
>
> 8. **Finalization.** Apply success criteria by execution type. For `RAW_TO_BRONZE`, summarize audit evidence for the original run ID and mark it `SUCCEEDED` only when the number of completed table-run records equals the enabled source count, every completed record is `SUCCEEDED`, the reconciliation-record count equals the enabled source count, every reconciliation is `MATCHED`, all required manifest-validation coverage exists, every required manifest-validation result is `PASSED`, and the selected Bronze schema contains exactly the enabled source tables with no unexpected tables; otherwise mark it `FAILED`. An `OPERATIONS_VALIDATION` run uses only its operations-specific checks described above and must not be evaluated against or bypass the ingestion gate. Count only table-run records with non-null `completed_ts`. These are row-count checks, not checks of distinct source coverage or actual Databricks task states. Error messages alone do not force a production ingestion failure, but a `FAILED` or `ERROR` manifest-validation status does. A started production run with missing evidence fails; no production pipeline/table/reconciliation/manifest-validation evidence at all raises `PipelineFinalizationError` even if messages exist. For any failed ingestion run, finalization must retain the current selected-profile Bronze state and all manifest-validation evidence, record a terminal failed outcome wherever operations storage is available, and make clear that the retained output is incomplete and not eligible for downstream Silver processing. Do not delete Raw, Bronze, or operations evidence during failure finalization.
>
> Update open `pipeline_runs` records with a Delta `MERGE` on `pipeline_run_id` and `target.completed_ts IS NULL`, using the existing table schema and cleaning up the temporary view. Preserve the original start time, workflow ID, and trigger. The terminal append fallback must use the preserved original run-context start timestamp. If that timestamp is unavailable, finalization must fail visibly and retain available diagnostics without appending a fabricated terminal record. Failed terminal records use `error_class = PipelineRunFailed` and the summary as `error_message`.
>
> Delta transactions do not span `pipeline_runs` and `run_messages`, so success finalization must use status-last ordering. Persist a truthful `PIPELINE_SUCCESS_READY` message first, stating that checks and required diagnostics passed but the terminal commit is pending. Then make the `SUCCEEDED` pipeline-row MERGE or fallback append the final required durable operation; do not perform another required persistence step afterward. If the pre-commit diagnostic fails, persist `FAILED` and available failure diagnostics wherever the operations store remains functional. If terminal persistence reports an error, accept success only when an immediate read proves that the exact intended terminal row committed; otherwise recover to `FAILED` where possible and propagate the failure. A failure-path diagnostic is best effort, but the terminal outcome remains `FAILED`. No `PIPELINE_SUCCESS_READY` message by itself authorizes Silver or represents a successful release; only the complete terminal production evidence does. `final_status`, when published as a task value after terminal persistence, is non-authoritative workflow metadata and its unavailability must not contradict the durable terminal row or turn a completed durable success into a failed job. Raise when the summarized execution is failed. Task-level repair with the same run ID is not supported by this audit contract; use a new whole-job run ID after correcting a failure.
>
> ### Databricks Asset Bundle requirement
>
> Use a Databricks Asset Bundle rather than a manually configured job. Create or update root `databricks.yml` with a team-specific `bundle.name`, `include: [config/raw_to_bronze/workflows/*.yml]`, and `sync.include` entries for `config/raw_to_bronze/**`, `notebooks/**`, `src/**`, and `requirements.txt`. Because `sync.include` is additive rather than an allowlist, add explicit `sync.exclude` patterns for tests, unrelated documentation, deliverables, outputs, local artifacts, bundle resource YAML not needed at runtime, and other non-runtime repository content. Define `variables.script_root.default: ${workspace.file_path}/notebooks`. Define target `dev` with `default: true` and `mode: development`. Prefer supplying the workspace host and authentication through the explicitly selected local Databricks CLI profile; omit `targets.dev.workspace.host` when the profile is authoritative. Never embed an instructor, another person's host, credentials, secrets, or local paths. Preserve existing includes if other workflows are already in scope; a standalone Bronze build does not need Silver, Gold, certification, or orchestration jobs.
>
> Define `config/raw_to_bronze/workflows/napa_raw_to_bronze.job.yml` with job resource key `napa_raw_to_bronze`, display name `NAPA Raw to Bronze`, `max_concurrent_runs: 1`, tag `pipeline_name: raw_to_bronze`, `performance_target: STANDARD`, and one job parameter:
>
> ```yaml
> - name: dataset_profile
>   default: napa_5k_clean
> ```
>
> The CLI `dataset_profile` parser must accept exactly `napa_5k_clean`, `napa_5k_tainted`, `napa_50k_clean`, `napa_50k_tainted`, and `napa_250k_production`; the standalone helper trims whitespace and lowercases its input before validation. The selected profile maps directly to the corresponding environment file and configured `release.release_name`; this need not equal the generator's native manifest `release_name`. Do not silently map a clean or tainted profile to a generic scale-only profile. Configure the job environment with `environment_key: napa_serverless_python`, `spec.environment_version: "4"`, and `spec.dependencies: [pyyaml]`; assign this environment key to every script task. Set the owner tag to the assigned team. Validate these construction settings in the target workspace. Do not use an existing cluster, job cluster, cluster ID, or warehouse ID.
>
> Create six `spark_python_task` tasks, using a configurable `${var.script_root}` that points to the synced `notebooks` directory:
>
> ```text
> resolve_configuration
>   -> validate_release_environment
>   -> validate_raw_inventory
>   -> build_bronze_tables
>   -> validate_bronze_reconciliation
>   -> finalize_pipeline_run
> ```
>
> Use the exact entrypoints and timeouts below. Tasks 2-5 each depend on the immediately preceding task. Task 6 depends on all five earlier tasks and uses `run_if: ALL_DONE`; it is not simply an ordinary success-only dependency on task 5. Do not configure automatic task repair or retries that reuse the same run ID.
>
> | Task key | File under `notebooks/` | Timeout (seconds) |
> |---|---|---:|
> | `resolve_configuration` | `01_resolve_configuration.py` | 900 |
> | `validate_release_environment` | `02_validate_release_environment.py` | 1200 |
> | `validate_raw_inventory` | `03_validate_raw_inventory.py` | 1800 |
> | `build_bronze_tables` | `04_build_bronze_tables.py` | 7200 |
> | `validate_bronze_reconciliation` | `05_validate_bronze_reconciliation.py` | 3600 |
> | `finalize_pipeline_run` | `06_finalize_pipeline_run.py` | 1200 |
>
> Each task receives `--dataset-profile {{job.parameters.dataset_profile}}`. Task 1 creates the run ID and publishes it with `dbutils.jobs.taskValues.set(key="run_id", value=...)`; every later task requires `--run-id {{tasks.resolve_configuration.values.run_id}}`. All scripts support optional `--config-path`, defaulting to the repository's `config/raw_to_bronze`; blank paths are treated as unset. The job need not expose this override as a job parameter. Each script reloads the selected configuration. Task 2 automatically initializes only the required configured schemas and requires the Raw Volume to already exist for production; tasks 4 and 5 require all selected-profile resources to exist.
>
> Publish diagnostic task values: task 1 sets `run_id`, `pipeline_run_id`, `execution_type`, `release_name`, `config_hash`, `catalog`, `raw_schema`, `bronze_schema`, and `source_path`; task 2 adds `operations_schema_fqn`; task 4 adds `bronze_table_count`; task 5 adds `reconciled_source_count`; task 6 adds `final_status`. Tasks 2-6 also set `run_id`. The production workflow sets `execution_type = RAW_TO_BRONZE`; the separate operations-validation entrypoint sets `execution_type = OPERATIONS_VALIDATION` internally and does not add a job parameter. Runtime helpers may resolve `spark`/`dbutils` from the supported execution context and must fail clearly if unavailable. Do not suppress failure to publish the critical `run_id` value or invent a replacement run ID. `ALL_DONE` cannot guarantee finalization if task 1 never produced its run ID or audit storage is unavailable.
>
> Include a compact bootstrap helper if needed so the bundled entrypoints can locate `src/napa_pipeline` without relying on a local Windows path.
>
> The finished repository should support:
>
> ```bash
> databricks bundle validate -t dev
> databricks bundle deploy -t dev
> databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_5k_clean
> databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_5k_tainted
> databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_50k_clean
> databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_50k_tainted
> databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_250k_production
> ```
>
> Add a runbook covering authentication/configuration, automatic required-schema initialization, student-owned Raw Volume creation and colocated manifest/Raw-file placement, deployment, 5K clean and tainted execution and whole-job reruns, then 50K clean and tainted execution, and finally 250K production execution. Document clearly that every run drops/recreates only the selected dedicated Bronze schema during initialization, that a failed run retains its selected-profile partial Bronze tables and diagnostics as incomplete evidence, that Silver must refuse a failed or incomplete Bronze run, and that the next execution clears the retained output during its normal initialization. Resolve the target namespace before deployment or execution. Do not claim deployment or runtime acceptance if only YAML/local tests were checked.
>
> For each successful run, record the run ID, config hash, one validated manifest, complete `PASSED` manifest-validation evidence, 13 readable and manifest-matched inputs, 13 published tables, 13 completed successful table-run records, 13 matched reconciliations, zero manifest/Raw/Bronze count differences, ten metadata columns per table, and a terminal successful pipeline row. Verify business-row preservation in integration tests; count equality alone does not prove it. For troubleshooting, query `manifest_validation_results` by `pipeline_run_id` and `dataset_profile`, query the other operations tables by run/release as applicable, inspect completed table-run rows, order messages by `created_ts`, and check the failed task's traceback. Failures after operations initialization must have a terminal `FAILED` outcome; a failure before operations initialization must remain visible in workflow status/logs and cannot alter Bronze because reset has not begun. Prefer a whole-job rerun after correcting the cause; task repair with the same run ID can duplicate audit evidence and fail finalization's count checks.
>
> ### Required tests
>
> The following is the required test plan for the implementation. Use small local fakes for logic tests, but validate actual Spark/Delta behavior with integration tests where available. The test plan is specified here and does not depend on a pre-existing test suite.
>
> Use the repository's existing test framework (pytest if none exists) and small fakes/fixtures so local unit tests do not require Databricks, network access, or production data. Add tests for at least:
>
> - valid configuration resolution for all five dataset profiles, deep merge, placeholder resolution, unsupported profile rejection, invalid clean/tainted/production combinations, duplicate build-order rejection, and deterministic config hash;
> - release-specific schema, Volume path, fully-qualified Bronze target construction, start-of-run destructive schema reset, exact 13-table success state, and partial-table retention after failure;
> - missing/malformed manifest files, missing or unexpected manifest entries, checksum mismatches, manifest row-count/column/schema-hash mismatches, missing and unexpected inventory entries, trailing-slash names, unreadable Parquet, readiness row-count/schema capture, and ordered schema hashes;
> - `manifest_validation_results` Delta DDL and append behavior; exact column order/types/nullability; nullable source-table/package-level checks; `PASSED`, `FAILED`, and `ERROR` semantics; string expected/observed values; missing-file diagnostics; successful and failed result persistence before task failure; historical retention across runs; and logical linkage to `pipeline_runs` and configured sources;
> - automatic creation and detection of only execution-required schemas, idempotent reruns, partial initialization failure without rollback, existing-schema inaccessibility, missing/inaccessible catalog errors, unsafe/injected identifier rejection, student-style namespaces without instructor-specific text, no cross-profile creation, and mandatory pre-existing Raw Volume validation;
> - the exact metadata-column tuple/order, metadata collision failure, source-record hash semantics, one-for-one preservation of identical rows and duplicate logical keys, Delta writer format/mode/schema overwrite options, standardized comment/properties, and wrapped publication failures;
> - reconciliation helper and orchestration behavior: a column-order mismatch produces `MISMATCH`, every `status != "MATCHED"` causes the reconciliation task to fail even when it is the only mismatch, the mismatch and diagnostic evidence are persisted before failure where storage is available, a fully matched dataset allows reconciliation to succeed, and finalization identifies the persisted failed reconciliation;
> - operations-table DDL/record construction, required execution-type values, UTC duration behavior, audit finalization success and failure, successful and failed operations validation, operations-validation exclusion from Bronze reset and Silver readiness, manifest-validation coverage in the production completion gate, non-`PASSED` manifest results forcing production pipeline failure, and use of `MERGE` to close an open pipeline row;
> - dataset-profile CLI validation, invalid profile behavior, and rejection of clean/tainted selection for 250K;
> - bundle workflow definition: one `dataset_profile` parameter with the five allowed values, the exact six-task order/dependencies, Python-script task files, downstream run-ID dynamic references, final `ALL_DONE`, serverless environment references, and no cluster configuration;
> - cross-pipeline compatibility if a Bronze-to-Silver configuration already exists: same Bronze catalog/schema, source/table mapping, and natural keys.
>
> Include tests for the documented limits: readable zero-row input with a matching manifest passes readiness; an order-only mismatch is persisted and fails the reconciliation task and finalization; repeated same-run terminal audit records fail the count checks; missing audit evidence raises; and a finished pipeline with no open row takes the append fallback. Also test that a run drops prior selected-profile Bronze tables before publication, never appends to a prior run, publishes exactly the configured 13 tables on success, retains partial tables after a publication failure, preserves Raw and historical operations evidence, records a terminal failed outcome where audit storage is available, leaves other profiles untouched, and refuses to drop an unresolved or non-dedicated schema. Test that the next execution's initialization reset removes the retained partial output. Test task orchestration as well as helper results so a correct helper cannot conceal an incorrect task status. Additional coverage should include metadata collisions, hash sentinel/delimiter ambiguity, and environment/CLI error paths. Do not require staging, cross-table rollback, post-failure cleanup, or a fixed expected business schema beyond the manifest contract.
>
> If a Spark-enabled test environment is available, add a small integration test with synthetic Parquet that verifies original row/column preservation, metadata values, hash behavior for nulls and duplicates, reconciliation, and overwrite idempotency. Do not require the real NAPA data for unit tests.
>
> ### Verification and final response
>
> After implementation, run and report local unit tests separately from Databricks Asset Bundle validation and controlled live Databricks Free Edition execution. Also run applicable formatting/lint checks already present in the repository, `git diff --check`, and inspect the final diff. Do not claim bundle validity unless validation ran, and do not claim Databricks runtime or production readiness unless the applicable workflow was actually deployed and executed with its required durable evidence.
>
> In your final response, use this exact factual structure:
>
> ```text
> Summary
> - What changed
>
> Files changed
> - path/to/file
>
> Validation
> - Tests or checks run, including results
>
> Assumptions
> - Actual assumptions made; distinguish them from validated facts
>
> Remaining items
> - Anything not run, unresolved, or needing team review
> ```

## Student review checklist

Before accepting AI-produced code, your team should be able to explain why each source is copied without business cleansing or uniqueness enforcement, how the run ID moves through the workflow, how start-of-run reset avoids append duplicates, what causes a run to fail, why partial Bronze tables are retained after failure, how Silver is prevented from consuming them, and how to locate evidence for a failed run in the operations schema. Record meaningful AI assistance in your project's AI-usage documentation.
