# Databricks notebook source
"""NAPA Bronze-to-Silver bootstrap.

One selected profile is classified into 13 accepted tables, 13 rejection
tables, and one current-state data-quality summary. The 25 record-level rules
come only from docs/silver_specification.md.
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # NAPA Silver bootstrap
# MAGIC
# MAGIC Configure the catalog, team prefix, profile, and existing-table action,
# MAGIC then run all cells. Use `fail` for the first run and `replace` only for an
# MAGIC intentional full refresh of the selected profile's 27 Silver tables.

# COMMAND ----------
CATALOG = "workspace"
TEAM_PREFIX = "napa_platform"
existing_table_action = "fail"

if "dbutils" in globals():
    for widget_name, default_value, label in (
        ("catalog", CATALOG, "Catalog"),
        ("team_prefix", TEAM_PREFIX, "Team prefix"),
        ("dataset_profile", "napa_5k_clean", "Dataset profile"),
        ("existing_table_action", existing_table_action, "Existing table action"),
    ):
        try:
            dbutils.widgets.text(widget_name, default_value, label)
        except Exception:
            pass
    CATALOG = dbutils.widgets.get("catalog").strip()
    TEAM_PREFIX = dbutils.widgets.get("team_prefix").strip()
    existing_table_action = dbutils.widgets.get("existing_table_action").strip().lower()

PROFILE_SUFFIXES = {
    "napa_5k_clean": "5k_clean",
    "napa_5k_tainted": "5k_tainted",
    "napa_50k_clean": "50k_clean",
    "napa_50k_tainted": "50k_tainted",
    "napa_250k_production": "250k",
}


def profile_config(profile):
    suffix = PROFILE_SUFFIXES[profile]
    return {
        "raw_volume_path": f"/Volumes/{CATALOG}/{TEAM_PREFIX}_{suffix}_raw/napa_files",
        "bronze_schema": f"{TEAM_PREFIX}_{suffix}_bronze",
        "silver_schema": f"{TEAM_PREFIX}_{suffix}_silver",
    }


# COMMAND ----------
import json
import re
from datetime import date, datetime, timedelta, timezone

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T


SOURCE_TABLES = (
    "regions", "clubs", "club_memberships", "player_master",
    "player_registrations", "player_assessment_history", "teams",
    "team_memberships", "matches", "match_teams", "match_team_players",
    "match_games", "monthly_batches",
)
PROCESSING_ORDER = (
    "monthly_batches", "regions", "player_master", "teams", "clubs",
    "player_registrations", "player_assessment_history", "club_memberships",
    "team_memberships", "matches", "match_teams", "match_team_players",
    "match_games",
)
METADATA_COLUMNS = (
    "_pipeline_run_id", "_pipeline_name", "_pipeline_version", "_release_name",
    "_source_file_name", "_source_file_path", "_source_file_size",
    "_source_file_modification_ts", "_ingested_ts", "_source_record_hash",
)
RULE_IDS = (
    "SILVER-PK-001", "SILVER-PK-002", "SILVER-REQ-001", "SILVER-DATE-001",
    "SILVER-FK-001", "SILVER-FK-002", "SILVER-BATCH-001", "SILVER-TEAM-001",
    "SILVER-TEAM-002", "SILVER-TEAM-003", "SILVER-POS-001", "SILVER-POS-002",
    "SILVER-MATCH-001", "SILVER-SIDE-001", "SILVER-GAME-001",
    "SILVER-GAME-002", "SILVER-GAME-003", "SILVER-GAME-004",
    "SILVER-GAME-005", "SILVER-GAME-006", "SILVER-GAME-007",
    "SILVER-GAME-008", "SILVER-GAME-009", "SILVER-AGE-001", "SILVER-AGE-002",
)
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

BUSINESS_FIELDS = {
    "regions": ("id", "country_code", "region_type", "region_name", "state_province_code", "population", "latitude", "longitude"),
    "clubs": ("id", "club_name", "region_id", "club_type", "competitiveness_level", "member_capacity", "founding_date", "indoor_court_count", "outdoor_court_count"),
    "club_memberships": ("id", "player_id", "club_id", "membership_type", "joined_date", "left_date", "is_primary"),
    "player_master": ("player_id", "external_player_key", "first_name", "last_name", "gender", "birth_date", "dominant_hand", "home_region_id", "country_code", "registration_date", "player_status", "rating", "rating_value", "confidence_score", "volatility_score", "global_percentile", "match_count_used", "rating_date", "rating_batch_id", "snapshot_month"),
    "player_registrations": ("id", "player_id", "batch_id", "registration_month", "registration_source", "assigned_region_id", "initial_rating_value", "initial_confidence_score"),
    "player_assessment_history": ("id", "player_id", "assessment_date", "assessment_type", "assessment_value", "confidence_score", "derived_from_matches", "batch_id"),
    "teams": ("id", "team_type", "team_division", "team_status", "country_code", "formation_date", "dissolution_date"),
    "team_memberships": ("id", "team_id", "player_id", "player_position", "joined_date", "left_date"),
    "matches": ("id", "match_date", "region_id", "match_type", "court_type", "match_format", "winning_team_id", "total_points_played", "batch_id"),
    "match_teams": ("id", "match_id", "team_number", "team_id", "team_score", "average_team_rating"),
    "match_team_players": ("id", "match_team_id", "player_id", "player_position", "player_rating_at_match"),
    "match_games": ("id", "match_id", "game_number", "team_one_score", "team_two_score", "winning_team_number", "target_score", "win_by", "actual_team_one_score_share"),
    "monthly_batches": ("id", "batch_month", "batch_sequence", "batch_type", "active_player_count_start", "new_player_count", "active_player_count_end", "match_count_generated", "rating_update_count", "assessment_update_count"),
}
PRIMARY_KEYS = {table: ("player_id" if table == "player_master" else "id") for table in SOURCE_TABLES}
REQUIRED_FIELDS = {
    "regions": ("id", "country_code", "region_name"),
    "clubs": ("id", "club_name", "region_id"),
    "club_memberships": ("id", "player_id", "club_id", "joined_date"),
    "player_master": ("player_id", "external_player_key", "first_name", "last_name", "birth_date", "registration_date", "player_status", "snapshot_month"),
    "player_registrations": ("id", "player_id", "batch_id", "registration_month"),
    "player_assessment_history": ("id", "player_id", "assessment_date", "assessment_type", "batch_id"),
    "teams": ("id", "team_type", "team_division", "team_status", "formation_date"),
    "team_memberships": ("id", "team_id", "player_id", "player_position", "joined_date"),
    "matches": ("id", "match_date", "match_type", "batch_id"),
    "match_teams": ("id", "match_id", "team_number", "team_id", "team_score"),
    "match_team_players": ("id", "match_team_id", "player_id"),
    "match_games": ("id", "match_id", "game_number", "team_one_score", "team_two_score", "winning_team_number"),
    "monthly_batches": ("id", "batch_month", "batch_sequence", "batch_type"),
}
DATE_FIELDS = {
    "regions": (), "clubs": ("founding_date",),
    "club_memberships": ("joined_date", "left_date"),
    "player_master": ("birth_date", "registration_date", "rating_date", "snapshot_month"),
    "player_registrations": ("registration_month",),
    "player_assessment_history": ("assessment_date",),
    "teams": ("formation_date", "dissolution_date"),
    "team_memberships": ("joined_date", "left_date"),
    "matches": ("match_date",), "match_teams": (), "match_team_players": (),
    "match_games": (), "monthly_batches": ("batch_month",),
}
MONTH_FIELDS = {("player_master", "snapshot_month"), ("player_registrations", "registration_month"), ("monthly_batches", "batch_month")}
STRING_FIELDS = {
    "regions": {"country_code", "region_type", "region_name", "state_province_code"},
    "clubs": {"club_name", "club_type", "competitiveness_level"},
    "club_memberships": {"membership_type"},
    "player_master": {"external_player_key", "first_name", "last_name", "gender", "dominant_hand", "country_code", "player_status"},
    "player_registrations": {"registration_source"},
    "player_assessment_history": {"assessment_type"},
    "teams": {"team_type", "team_division", "team_status", "country_code"},
    "team_memberships": set(), "matches": {"match_type", "court_type", "match_format"},
    "match_teams": set(), "match_team_players": set(), "match_games": set(),
    "monthly_batches": {"batch_type"},
}
UPPER_FIELDS = {
    ("regions", "country_code"), ("regions", "region_type"), ("regions", "state_province_code"),
    ("clubs", "club_type"), ("clubs", "competitiveness_level"),
    ("club_memberships", "membership_type"), ("player_master", "gender"),
    ("player_master", "dominant_hand"), ("player_master", "country_code"),
    ("player_master", "player_status"), ("player_registrations", "registration_source"),
    ("player_assessment_history", "assessment_type"), ("teams", "country_code"),
    ("matches", "match_type"), ("matches", "court_type"), ("matches", "match_format"),
    ("monthly_batches", "batch_type"),
}
FK_RELATIONSHIPS = {
    "clubs": (("region_id", "regions"),),
    "club_memberships": (("player_id", "player_master"), ("club_id", "clubs")),
    "player_master": (("home_region_id", "regions"),),
    "player_registrations": (("player_id", "player_master"), ("batch_id", "monthly_batches"), ("assigned_region_id", "regions")),
    "player_assessment_history": (("player_id", "player_master"), ("batch_id", "monthly_batches")),
    "team_memberships": (("team_id", "teams"), ("player_id", "player_master")),
    "matches": (("region_id", "regions"), ("winning_team_id", "teams"), ("batch_id", "monthly_batches")),
    "match_teams": (("match_id", "matches"), ("team_id", "teams")),
    "match_team_players": (("match_team_id", "match_teams"), ("player_id", "player_master")),
    "match_games": (("match_id", "matches"),),
}


class SilverError(RuntimeError):
    pass


# COMMAND ----------
def qid(value):
    if not IDENTIFIER_PATTERN.fullmatch(value or ""):
        raise SilverError(f"Unsafe identifier: {value!r}")
    return f"`{value}`"


def fqn(schema, table):
    return f"{qid(CATALOG)}.{qid(schema)}.{qid(table)}"


def c(name):
    return F.col(f"`{name}`")


def n(name):
    return f"__n_{name}"


def safe_date(name):
    value = f"trim(CAST(`{name}` AS STRING))"
    return F.expr(
        f"CASE WHEN `{name}` IS NULL THEN CAST(NULL AS DATE) "
        f"WHEN {value} RLIKE '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$' "
        f"THEN try_cast({value} AS DATE) ELSE CAST(NULL AS DATE) END"
    )


def safe_month(name):
    value = f"trim(CAST(`{name}` AS STRING))"
    return F.expr(
        f"CASE WHEN `{name}` IS NULL THEN CAST(NULL AS DATE) "
        f"WHEN {value} RLIKE '^[0-9]{{4}}-[0-9]{{2}}$' "
        f"THEN try_cast(concat({value}, '-01') AS DATE) "
        f"WHEN {value} RLIKE '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$' "
        f"THEN try_cast({value} AS DATE) ELSE CAST(NULL AS DATE) END"
    )


def mapped(value, aliases):
    result = value
    for source, target in aliases.items():
        result = F.when(value == source, F.lit(target)).otherwise(result)
    return result


def position(name):
    value = F.upper(F.trim(c(name).cast("string")))
    return mapped(value, {"1": "LEFT", "2": "RIGHT"})


def normalize_expression(table, field):
    if (table, field) in MONTH_FIELDS:
        return safe_month(field)
    if field in DATE_FIELDS[table]:
        return safe_date(field)
    if field == "player_position" and table in {"team_memberships", "match_team_players"}:
        return position(field)
    if table == "teams" and field == "team_type":
        return mapped(F.upper(F.trim(c(field))), {"AD HOC": "AD_HOC"})
    if table == "teams" and field == "team_division":
        return mapped(F.upper(F.trim(c(field))), {"MENS_DOUBLES": "MENS", "WOMENS_DOUBLES": "WOMENS", "MIXED_DOUBLES": "MIXED", "OPEN_DOUBLES": "OPEN"})
    if table == "teams" and field == "team_status":
        return mapped(F.upper(F.trim(c(field))), {"DORMANT": "INACTIVE", "RETIRED": "DISSOLVED"})
    if field in STRING_FIELDS[table]:
        value = F.trim(c(field))
        return F.upper(value) if (table, field) in UPPER_FIELDS else value
    return c(field)


def prepare(table, source):
    required_columns = set(BUSINESS_FIELDS[table] + METADATA_COLUMNS)
    missing = sorted(required_columns - set(source.columns))
    if missing:
        raise SilverError(f"{table} is missing required Bronze columns: {missing}")
    work = source
    for field in BUSINESS_FIELDS[table]:
        work = work.withColumn(n(field), normalize_expression(table, field))
    key = PRIMARY_KEYS[table]
    duplicates = (
        work.where(c(n(key)).isNotNull()).groupBy(c(n(key))).count()
        .where(F.col("count") > 1)
        .select(c(n(key)).alias("__duplicate_key"), F.lit(True).alias("__duplicate_pk"))
    )
    return work.join(duplicates, c(n(key)) == F.col("__duplicate_key"), "left").drop("__duplicate_key")


def reason(condition, rule_id, classification, fields, message):
    return F.when(condition, F.struct(
        F.lit(rule_id).alias("rule_id"), F.lit(classification).alias("classification"),
        fields.alias("fields"), F.lit(message).alias("message"),
    ))


def static_fields(*fields):
    return F.array(*[F.lit(field) for field in fields])


def failed_fields(items):
    return F.filter(F.array(*[F.when(condition, F.lit(field)) for field, condition in items]), lambda value: value.isNotNull())


def common_reasons(table, work):
    key = PRIMARY_KEYS[table]
    missing = []
    for field in REQUIRED_FIELDS[table]:
        value = c(n(field))
        condition = value.isNull()
        if (
            isinstance(work.schema[n(field)].dataType, T.StringType)
            or field == "player_position"
        ):
            condition = condition | (value == "")
        missing.append((field, condition))
    invalid_dates = [(field, c(field).isNotNull() & c(n(field)).isNull()) for field in DATE_FIELDS[table]]
    output = [
        reason(c(n(key)).isNull(), "SILVER-PK-001", "DIRECT", static_fields(key), "Logical primary key is null."),
        reason(F.coalesce(F.col("__duplicate_pk"), F.lit(False)), "SILVER-PK-002", "DIRECT", static_fields(key), "Every occurrence of a duplicated logical primary key is rejected."),
        reason(F.size(failed_fields(missing)) > 0, "SILVER-REQ-001", "DIRECT", failed_fields(missing), "One or more required values are missing or blank."),
    ]
    if invalid_dates:
        output.append(reason(F.size(failed_fields(invalid_dates)) > 0, "SILVER-DATE-001", "DIRECT", failed_fields(invalid_dates), "One or more populated dates or months are invalid."))
    return output


def add_fk_evidence(table, work, prepared, results):
    relationships = FK_RELATIONSHIPS.get(table, ())
    direct_items, cascade_items = [], []
    for index, (field, parent) in enumerate(relationships):
        parent_key = PRIMARY_KEYS[parent]
        bronze_flag = f"__fk_bronze_{index}"
        accepted_flag = f"__fk_accepted_{index}"
        bronze_keys = prepared[parent].where(c(n(parent_key)).isNotNull()).select(c(n(parent_key)).alias(f"__bk_{index}")).distinct().withColumn(bronze_flag, F.lit(True))
        accepted_keys = results[parent]["accepted"].select(c(parent_key).alias(f"__ak_{index}")).distinct().withColumn(accepted_flag, F.lit(True))
        work = work.join(bronze_keys, c(n(field)) == F.col(f"__bk_{index}"), "left").drop(f"__bk_{index}")
        work = work.join(accepted_keys, c(n(field)) == F.col(f"__ak_{index}"), "left").drop(f"__ak_{index}")
        populated = c(n(field)).isNotNull()
        direct_items.append((field, populated & F.col(bronze_flag).isNull()))
        cascade_items.append((field, populated & F.col(bronze_flag).isNotNull() & F.col(accepted_flag).isNull()))
    reasons = []
    if relationships:
        direct_fields = failed_fields(direct_items)
        cascade_fields = failed_fields(cascade_items)
        reasons.extend([
            reason(F.size(direct_fields) > 0, "SILVER-FK-001", "DIRECT", direct_fields, "One or more populated foreign keys have no Bronze parent."),
            reason(F.size(cascade_fields) > 0, "SILVER-FK-002", "CASCADING", cascade_fields, "One or more Bronze parents were rejected from accepted Silver."),
        ])
    return work, reasons


def completed_age(birth, reference):
    reference_year = F.year(reference)
    leap_year = ((reference_year % 400) == 0) | (((reference_year % 4) == 0) & ((reference_year % 100) != 0))
    leap_birth = (F.month(birth) == 2) & (F.dayofmonth(birth) == 29)
    anniversary = F.make_date(
        reference_year,
        F.when(leap_birth & ~leap_year, F.lit(3)).otherwise(F.month(birth)),
        F.when(leap_birth & ~leap_year, F.lit(1)).otherwise(F.dayofmonth(birth)),
    )
    return (reference_year - F.year(birth) - F.when(anniversary > reference, 1).otherwise(0)).cast("int")


def finish(table, work, reasons, rejected_at, derived=None):
    reason_array = F.array_sort(F.filter(F.array(*reasons), lambda item: item.isNotNull()))
    classified = work.withColumn("rejection_reasons", reason_array)
    accepted_columns = [c(n(field)).alias(field) for field in BUSINESS_FIELDS[table]]
    if derived:
        accepted_columns.extend(expression.alias(name) for name, expression in derived.items())
    accepted = classified.where(F.size("rejection_reasons") == 0).select(*accepted_columns)
    rejected = (
        classified.where(F.size("rejection_reasons") > 0)
        .withColumn("has_direct_rejection", F.exists("rejection_reasons", lambda item: item["classification"] == "DIRECT"))
        .withColumn("has_cascading_rejection", F.exists("rejection_reasons", lambda item: item["classification"] == "CASCADING"))
        .withColumn("rejected_at", F.lit(rejected_at).cast("timestamp"))
        .select(*[c(field) for field in BUSINESS_FIELDS[table]], *[c(field) for field in METADATA_COLUMNS], "rejection_reasons", "has_direct_rejection", "has_cascading_rejection", "rejected_at")
    )
    return {"accepted": accepted.cache(), "rejected": rejected.cache()}


# COMMAND ----------
def build_silver(bronze, snapshot_as_of_date, rejected_at):
    prepared = {table: prepare(table, bronze[table]) for table in SOURCE_TABLES}
    results = {}

    def classify(table, extras=(), derived=None, work=None):
        current = prepared[table] if work is None else work
        current, fk_reasons = add_fk_evidence(table, current, prepared, results)
        results[table] = finish(table, current, common_reasons(table, current) + fk_reasons + list(extras), rejected_at, derived)

    batch_work = prepared["monthly_batches"]
    classify("monthly_batches", [reason(c(n("batch_sequence")) < 0, "SILVER-BATCH-001", "DIRECT", static_fields("batch_sequence"), "Batch sequence must be zero or positive.")])
    classify("regions")

    player_work = prepared["player_master"].withColumn("__snapshot_date", F.lit(snapshot_as_of_date).cast("date"))
    classify("player_master", [reason(c(n("birth_date")) > F.col("__snapshot_date"), "SILVER-AGE-001", "DIRECT", static_fields("birth_date"), "Birth date is after the dataset snapshot date.")], {"derived_age_at_snapshot": completed_age(c(n("birth_date")), F.col("__snapshot_date"))}, player_work)

    team_work = prepared["teams"]
    classify("teams", [
        reason(c(n("team_type")).isNotNull() & (c(n("team_type")) != "") & ~c(n("team_type")).isin("COMPETITIVE", "AD_HOC"), "SILVER-TEAM-001", "DIRECT", static_fields("team_type"), "Team type is outside the approved domain."),
        reason(c(n("team_division")).isNotNull() & (c(n("team_division")) != "") & ~c(n("team_division")).isin("MENS", "WOMENS", "MIXED", "OPEN"), "SILVER-TEAM-002", "DIRECT", static_fields("team_division"), "Team division is outside the approved domain."),
        reason(c(n("team_status")).isNotNull() & (c(n("team_status")) != "") & ~c(n("team_status")).isin("ACTIVE", "INACTIVE", "DISSOLVED"), "SILVER-TEAM-003", "DIRECT", static_fields("team_status"), "Team status is outside the approved domain."),
    ])
    classify("clubs")
    classify("player_registrations")
    classify("player_assessment_history")
    classify("club_memberships")
    classify("team_memberships", [reason(c(n("player_position")).isNotNull() & (c(n("player_position")) != "") & ~c(n("player_position")).isin("LEFT", "RIGHT"), "SILVER-POS-001", "DIRECT", static_fields("player_position"), "Player position must be LEFT or RIGHT.")])

    bronze_match_pairs = prepared["match_teams"].where(c(n("match_id")).isNotNull() & c(n("team_id")).isNotNull()).select(c(n("match_id")).alias("__winner_match"), c(n("team_id")).alias("__winner_team")).distinct().withColumn("__winner_pair_exists", F.lit(True))
    match_work = prepared["matches"].join(bronze_match_pairs, (c(n("id")) == F.col("__winner_match")) & (c(n("winning_team_id")) == F.col("__winner_team")), "left").drop("__winner_match", "__winner_team")
    classify("matches", [reason(c(n("winning_team_id")).isNotNull() & F.col("__winner_pair_exists").isNull(), "SILVER-MATCH-001", "DIRECT", static_fields("id", "winning_team_id"), "Winning team is not a Bronze participant in the match.")], work=match_work)
    classify("match_teams", [reason(c(n("team_number")).isNotNull() & ~c(n("team_number")).isin(1, 2), "SILVER-SIDE-001", "DIRECT", static_fields("team_number"), "Team number must be 1 or 2.")])

    participant_work = prepared["match_team_players"]
    side_context = results["match_teams"]["accepted"].select(F.col("id").alias("__side_id"), F.col("match_id").alias("__context_match_id"))
    match_context = results["matches"]["accepted"].select(F.col("id").alias("__context_match_id_2"), F.col("match_date").alias("__match_date"))
    player_context = results["player_master"]["accepted"].select(F.col("player_id").alias("__context_player_id"), F.col("birth_date").alias("__birth_date"))
    participant_work = participant_work.join(side_context, c(n("match_team_id")) == F.col("__side_id"), "left").drop("__side_id")
    participant_work = participant_work.join(match_context, F.col("__context_match_id") == F.col("__context_match_id_2"), "left").drop("__context_match_id_2")
    participant_work = participant_work.join(player_context, c(n("player_id")) == F.col("__context_player_id"), "left").drop("__context_player_id")
    classify("match_team_players", [
        reason(c(n("player_position")).isNotNull() & (c(n("player_position")) != "") & ~c(n("player_position")).isin("LEFT", "RIGHT"), "SILVER-POS-002", "DIRECT", static_fields("player_position"), "Populated player position must be LEFT or RIGHT."),
        reason(F.col("__birth_date").isNotNull() & F.col("__match_date").isNotNull() & (F.col("__birth_date") > F.col("__match_date")), "SILVER-AGE-002", "DIRECT", static_fields("player_id"), "Player birth date is after the match date."),
    ], {"derived_age_at_match": completed_age(F.col("__birth_date"), F.col("__match_date"))}, participant_work)

    game_work = prepared["match_games"]
    game_pairs = game_work.where(c(n("match_id")).isNotNull() & c(n("game_number")).isNotNull()).groupBy(c(n("match_id")), c(n("game_number"))).count().where(F.col("count") > 1).select(c(n("match_id")).alias("__gm"), c(n("game_number")).alias("__gn"), F.lit(True).alias("__duplicate_game_pair"))
    game_work = game_work.join(game_pairs, (c(n("match_id")) == F.col("__gm")) & (c(n("game_number")) == F.col("__gn")), "left").drop("__gm", "__gn")
    one, two, winner = c(n("team_one_score")), c(n("team_two_score")), c(n("winning_team_number"))
    score_inputs = one.isNotNull() & two.isNotNull() & winner.isNotNull()
    classify("match_games", [
        reason(c(n("game_number")) <= 0, "SILVER-GAME-001", "DIRECT", static_fields("game_number"), "Game number must be positive."),
        reason(one < 0, "SILVER-GAME-002", "DIRECT", static_fields("team_one_score"), "Team one score must be nonnegative."),
        reason(two < 0, "SILVER-GAME-003", "DIRECT", static_fields("team_two_score"), "Team two score must be nonnegative."),
        reason(winner.isNotNull() & ~winner.isin(1, 2), "SILVER-GAME-004", "DIRECT", static_fields("winning_team_number"), "Winning team number must be 1 or 2."),
        reason(score_inputs & ((one == two) | ((winner == 1) & (one <= two)) | ((winner == 2) & (two <= one))), "SILVER-GAME-005", "DIRECT", static_fields("winning_team_number", "team_one_score", "team_two_score"), "Winner and game scores are inconsistent."),
        reason(c(n("target_score")).isNotNull() & (c(n("target_score")) < 0), "SILVER-GAME-006", "DIRECT", static_fields("target_score"), "Target score must be nonnegative when populated."),
        reason(c(n("win_by")).isNotNull() & (c(n("win_by")) < 0), "SILVER-GAME-007", "DIRECT", static_fields("win_by"), "Win-by must be nonnegative when populated."),
        reason(c(n("actual_team_one_score_share")).isNotNull() & ((one + two) > 0) & (F.abs(c(n("actual_team_one_score_share")).cast("double") - (one.cast("double") / (one + two).cast("double"))) > F.lit(0.0001)), "SILVER-GAME-008", "DIRECT", static_fields("actual_team_one_score_share", "team_one_score", "team_two_score"), "Score share differs from the scores by more than 0.0001."),
        reason(F.coalesce(F.col("__duplicate_game_pair"), F.lit(False)), "SILVER-GAME-009", "DIRECT", static_fields("match_id", "game_number"), "Every occurrence of a duplicate match/game-number pair is rejected."),
    ], work=game_work)
    return prepared, results


# COMMAND ----------
SUMMARY_SCHEMA = T.StructType([
    T.StructField("row_type", T.StringType(), False), T.StructField("dataset_profile", T.StringType(), False),
    T.StructField("source_table", T.StringType(), False), T.StructField("reason_id", T.StringType(), True),
    T.StructField("reason_classification", T.StringType(), True), T.StructField("bronze_record_count", T.LongType(), True),
    T.StructField("accepted_record_count", T.LongType(), True), T.StructField("rejected_record_count", T.LongType(), True),
    T.StructField("rejection_percentage", T.DoubleType(), True), T.StructField("direct_rejected_record_count", T.LongType(), True),
    T.StructField("cascading_rejected_record_count", T.LongType(), True), T.StructField("reason_occurrence_count", T.LongType(), True),
    T.StructField("reconciliation_difference", T.LongType(), True), T.StructField("reconciliation_status", T.StringType(), True),
    T.StructField("summary_generated_at", T.TimestampType(), False),
])


def build_summary(spark, profile, bronze, results, generated_at):
    totals, reason_frames = [], []
    for table in SOURCE_TABLES:
        bronze_count = bronze[table].count()
        accepted_count = results[table]["accepted"].count()
        rejected_count = results[table]["rejected"].count()
        difference = bronze_count - accepted_count - rejected_count
        direct_count = results[table]["rejected"].where("has_direct_rejection").count()
        cascading_count = results[table]["rejected"].where("has_cascading_rejection").count()
        totals.append(("TABLE_TOTAL", profile, table, None, None, bronze_count, accepted_count, rejected_count, 0.0 if bronze_count == 0 else 100.0 * rejected_count / bronze_count, direct_count, cascading_count, None, difference, "MATCHED" if difference == 0 else "MISMATCH", generated_at))
        reason_frames.append(
            results[table]["rejected"].select(F.explode("rejection_reasons").alias("reason"))
            .select(
                F.col("reason.rule_id").alias("reason_id"),
                F.col("reason.classification").alias("reason_classification"),
            )
            .groupBy("reason_id", "reason_classification").count()
            .select(
                F.lit("REASON_TOTAL").alias("row_type"), F.lit(profile).alias("dataset_profile"), F.lit(table).alias("source_table"),
                F.col("reason_id"), F.col("reason_classification"),
                F.lit(None).cast("long").alias("bronze_record_count"), F.lit(None).cast("long").alias("accepted_record_count"),
                F.lit(None).cast("long").alias("rejected_record_count"), F.lit(None).cast("double").alias("rejection_percentage"),
                F.lit(None).cast("long").alias("direct_rejected_record_count"), F.lit(None).cast("long").alias("cascading_rejected_record_count"),
                F.col("count").cast("long").alias("reason_occurrence_count"), F.lit(None).cast("long").alias("reconciliation_difference"),
                F.lit(None).cast("string").alias("reconciliation_status"), F.lit(generated_at).cast("timestamp").alias("summary_generated_at"),
            )
        )
    totals_df = spark.createDataFrame(totals, SUMMARY_SCHEMA)
    reasons_df = reason_frames[0]
    for frame in reason_frames[1:]:
        reasons_df = reasons_df.unionByName(frame)
    summary = totals_df.unionByName(reasons_df)
    mismatches = [row for row in totals if row[12] != 0]
    if mismatches:
        raise SilverError(f"Reconciliation failed before writing: {mismatches}")
    return summary


def validate_accepted_keys(results):
    for table in SOURCE_TABLES:
        key = PRIMARY_KEYS[table]
        accepted = results[table]["accepted"]
        if accepted.where(F.col(key).isNull()).limit(1).count():
            raise SilverError(f"Accepted {table}.{key} contains null.")
        if accepted.groupBy(key).count().where(F.col("count") > 1).limit(1).count():
            raise SilverError(f"Accepted {table}.{key} is not unique.")
    for child, relationships in FK_RELATIONSHIPS.items():
        for field, parent in relationships:
            parent_key = PRIMARY_KEYS[parent]
            unresolved = (
                results[child]["accepted"].where(F.col(field).isNotNull())
                .join(
                    results[parent]["accepted"].select(
                        F.col(parent_key).alias("__accepted_parent_key")
                    ),
                    F.col(field) == F.col("__accepted_parent_key"),
                    "left_anti",
                )
                .limit(1)
                .count()
            )
            if unresolved:
                raise SilverError(
                    f"Accepted foreign key {child}.{field} does not resolve to {parent}.{parent_key}."
                )


def read_inputs(spark, dbutils, profile, config):
    manifest_path = config["raw_volume_path"].rstrip("/") + "/manifest.json"
    try:
        manifest = json.loads(dbutils.fs.head(manifest_path, 10 * 1024 * 1024))
        snapshot_end = date.fromisoformat(manifest["snapshot_end_exclusive"])
    except Exception as exc:
        raise SilverError(f"Cannot read a valid snapshot_end_exclusive from {manifest_path}.") from exc
    bronze_schema = config["bronze_schema"]
    try:
        present = {row["tableName"] for row in spark.sql(f"SHOW TABLES IN {qid(CATALOG)}.{qid(bronze_schema)}").collect()}
    except Exception as exc:
        raise SilverError(f"Cannot inspect Bronze schema {CATALOG}.{bronze_schema}.") from exc
    missing = sorted(set(SOURCE_TABLES) - present)
    if missing:
        raise SilverError(f"Missing Bronze tables: {missing}")
    bronze = {table: spark.table(fqn(bronze_schema, table)) for table in SOURCE_TABLES}
    for table, frame in bronze.items():
        missing_columns = sorted(set(BUSINESS_FIELDS[table] + METADATA_COLUMNS) - set(frame.columns))
        if missing_columns:
            raise SilverError(f"{table} is missing columns: {missing_columns}")
        if frame.where(
            F.col("_release_name").isNull() | (F.col("_release_name") != profile)
        ).limit(1).count():
            raise SilverError(
                f"{table} contains Bronze records outside selected profile {profile}."
            )
    percentile_type = bronze["player_master"].schema["global_percentile"].dataType
    if isinstance(percentile_type, T.StringType):
        if bronze["player_master"].where("global_percentile IS NOT NULL").limit(1).count():
            samples = [row[0] for row in bronze["player_master"].where("global_percentile IS NOT NULL").select("global_percentile").distinct().limit(20).collect()]
            raise SilverError(
                f"{profile} has unexpected populated STRING global_percentile values; "
                f"source representation requires review; samples={samples}"
            )
    elif not (isinstance(percentile_type, T.DecimalType) and percentile_type.scale == 2):
        raise SilverError(
            f"{profile} global_percentile must be null-only STRING or DECIMAL(scale=2); "
            f"observed {percentile_type.simpleString()}."
        )
    for table in ("team_memberships", "match_team_players"):
        data_type = bronze[table].schema["player_position"].dataType
        if not isinstance(data_type, (T.LongType, T.StringType)):
            raise SilverError(f"{table}.player_position must be BIGINT or STRING.")
    return bronze, snapshot_end - timedelta(days=1)


def existing_expected_tables(spark, schema):
    present = {
        row["tableName"]
        for row in spark.sql(
            f"SHOW TABLES IN {qid(CATALOG)}.{qid(schema)}"
        ).collect()
    }
    expected = set(SOURCE_TABLES) | {f"{table}_rejects" for table in SOURCE_TABLES} | {"silver_data_quality_summary"}
    return sorted(expected & present)


def publish(spark, profile, config, results, summary):
    schema = config["silver_schema"]
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {qid(CATALOG)}.{qid(schema)}")
    existing = existing_expected_tables(spark, schema)
    if existing and existing_table_action == "fail":
        raise SilverError(f"Existing-table protection stopped before writes: {existing}")
    if existing_table_action == "replace":
        print(f"WARNING: replacing all 27 expected outputs in {CATALOG}.{schema} for {profile}.")
    written = []
    try:
        for table in SOURCE_TABLES:
            results[table]["accepted"].write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(fqn(schema, table))
            written.append(table)
            results[table]["rejected"].write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(fqn(schema, f"{table}_rejects"))
            written.append(f"{table}_rejects")
        summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(fqn(schema, "silver_data_quality_summary"))
        written.append("silver_data_quality_summary")
    except Exception as exc:
        raise SilverError(f"FAILED / INCOMPLETE after writing {written}. Do not use this profile for Gold until a complete rerun succeeds.") from exc
    if len(written) != 27 or len(existing_expected_tables(spark, schema)) != 27:
        raise SilverError("FAILED / INCOMPLETE: all 27 outputs were not confirmed after writing.")


# COMMAND ----------
def run_silver(spark, dbutils):
    if len(RULE_IDS) != 25 or len(set(RULE_IDS)) != 25:
        raise SilverError("The approved rule registry must contain exactly 25 unique rules.")
    if existing_table_action not in {"fail", "replace"}:
        raise SilverError("existing_table_action must be fail or replace.")
    if not IDENTIFIER_PATTERN.fullmatch(CATALOG) or not IDENTIFIER_PATTERN.fullmatch(TEAM_PREFIX):
        raise SilverError("Catalog and team prefix must be safe SQL identifiers.")
    profile = dbutils.widgets.get("dataset_profile").strip().lower()
    if profile not in PROFILE_SUFFIXES:
        raise SilverError(f"Unsupported dataset_profile: {profile}")
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    config = profile_config(profile)
    print(f"Reading Bronze: {CATALOG}.{config['bronze_schema']}")
    print(f"Writing Silver: {CATALOG}.{config['silver_schema']}")
    bronze, snapshot_as_of = read_inputs(spark, dbutils, profile, config)
    generated_at = datetime.now(timezone.utc)
    _, results = build_silver(bronze, snapshot_as_of, generated_at)
    summary = build_summary(spark, profile, bronze, results, generated_at).cache()
    validate_accepted_keys(results)
    print("Classification and reconciliation passed for all 13 sources.")
    publish(spark, profile, config, results, summary)
    display(summary.orderBy("row_type", "source_table", "reason_id"))
    print(f"OVERALL PASS: refreshed 27 Silver tables for {profile}.")


if "spark" in globals() and "dbutils" in globals():
    try:
        run_silver(spark, dbutils)
    except SilverError as exc:
        print(f"OVERALL FAIL: {exc}")
        raise
