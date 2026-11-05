# AGENTS.md

## 1. Purpose

This is a **student team repository** for the North American Pickleball Association (NAPA) Olympic Analytics case study in DSB6000, Data Science Strategy & Leadership.

Help the team build a repeatable Raw-to-Bronze-to-Silver data platform, design its own Gold analytics, recommend competitive doubles rosters, and present its case to the NAPA RFP evaluation committee. The project emphasizes **AI-assisted development, analytical judgment, governance, and leadership** rather than advanced infrastructure engineering.

Students own the analytical strategy, final recommendations, and submitted work. The AI assistant can write substantial code, tests, notebooks, and presentations **at the team's direction**, but must explain assumptions and results. Do not assume a completed implementation or another team's solution is available.

The instructor supplies the student-facing Bronze bootstrap utility. Students use it to create and validate Bronze tables without constructing an ingestion pipeline. Instructor-provided Silver specifications and a revised Silver prompt are forthcoming. Students author their own Silver-to-Gold prompts and own the Gold analytical design.

## 2. Sources of truth

Read the documents that actually exist in the repository before acting:

1. **NAPA RFP and course assignment:** business requirements, eligibility, deliverables, milestones, and assessment criteria.
2. **`notebooks/00_bootstrap_bronze.py` and `docs/bronze_bootstrap_guide.md`:** supplied Bronze utility and operating guidance.
3. **Instructor-provided Silver specifications and revised prompt:** forthcoming Silver construction guidance when published.
4. **Delivered Parquet files and colocated `manifest.json`:** physical source and release evidence.
5. **README, existing code/configuration/tests, and team decisions:** implementation context.

Find the actual locations of these files; do not assume a particular folder layout. Do not invent Silver requirements while the revised guidance is forthcoming. If a genuine conflict appears, explain it to the team and seek direction before changing affected behavior.

## 3. Working with the team

For each task:

1. Read the relevant RFP/specification, Bronze bootstrap guidance, and existing implementation.
2. Check `git status --short`, `git branch --show-current`, and `git remote -v` before editing.
3. Explain the proposed change, files affected, important assumptions, and validation plan.
4. Make focused, reviewable edits; preserve unrelated student work and established interfaces.
5. Run relevant checks. Distinguish tests executed from tests merely proposed.
6. Summarize results and unresolved decisions in plain language.

Prefer a small working step with a visible result over unnecessary frameworks or complex infrastructure. Ask targeted questions only when the answer materially changes implementation. Do not invent fields, counts, eligibility rules, analysis results, or successful deployments.

Do not commit, push, merge, deploy, or delete shared resources without team authorization.

## 4. Data architecture and dataset profiles

The intended flow is:

```text
Delivered Parquet + manifest.json
  -> Raw Volume
  -> Bronze Delta tables (supplied bootstrap notebook)
  -> Silver Delta tables + rejects and quality evidence (revised guidance forthcoming)
  -> Gold features, analytics, comparisons, and rankings (team-designed)
  -> roster recommendations, development camp, and RFP presentation
```

Use the **same supplied Bronze bootstrap notebook** for all five independent, full-refresh dataset profiles. Use the forthcoming Silver guidance for the shared Silver implementation. The `dataset_profile` values, in recommended test order, are:

1. `napa_5k_clean`
2. `napa_5k_tainted`
3. `napa_50k_clean`
4. `napa_50k_tainted`
5. `napa_250k_production`

For each profile, build and validate Bronze before running Silver. The production-scale dataset includes imperfect data. Use configuration for the team's catalog, prefix, schemas, and Volumes. Avoid hard-coded personal or cross-team paths. The initial five profiles are **not incremental monthly updates**; follow separate instructions if additional releases are issued.

## 5. Layer boundaries

**Raw:** The delivered source package contains 13 Parquet files and `manifest.json` in the selected Raw Volume. Preserve it as received. The manifest is delivery evidence, not an additional Bronze table.

**Bronze:** Use `notebooks/00_bootstrap_bronze.py` according to `docs/bronze_bootstrap_guide.md`. Students create and populate the Raw Volume; the notebook verifies but never modifies its files. The utility preserves every source record and business column, including duplicate logical keys and invalid values, appends the prescribed metadata, and reconciles manifest, Raw, and Bronze counts. Do not cleanse or engineer business features in Bronze. Keep `existing_table_action = "fail"` for normal use; follow the guide's Danger Zone only for an intentional reload.

**Silver:** Instructor-provided Silver specifications and a revised construction prompt are forthcoming. Do not implement or infer a replacement Silver contract until that guidance is available. Continue to preserve source attributes, historical timing, and data-quality evidence needed for the revised workflow.

**Time matters:** Preserve the manifest-derived snapshot date and actual historical event dates. Current-state age/status may use the snapshot date; historical age, rating, and membership analysis must use the appropriate event-time evidence. Never apply a later value retroactively or invent missing history.

**Gold:** This is the team's analytical layer. Keep Gold outputs in a separate team-owned schema. Never modify Raw, Bronze, Silver, rejection, or audit evidence to accommodate a preferred model. Record feature definitions and lineage so results can be reproduced.

## 6. Gold analytics and student decisions

The team, rather than the AI assistant, decides:

- How to evaluate individual players and doubles partnerships.
- Which features, comparisons, statistical methods, models, or scoring rules to use.
- How to address eligibility, limited match history, uncertainty, and tradeoffs.
- How to select and defend the final competitive rosters and development candidates.

Help the team turn those choices into working code, tables, experiments, and charts. Before implementation, confirm the **decision question, data grain, source inputs, date window, evaluation method, and expected outputs**. Offer alternatives when a choice is genuinely open; do not impose a single solution as mandatory.

Protect against duplicate-producing joins, unsupported eligibility assumptions, future-data leakage, misleading confidence claims, and fabricated results. Distinguish observed evidence, modeled estimates, and team judgment. Use the 250K production Silver data for final production recommendations; smaller profiles may support development and testing.

## 7. NAPA RFP outcomes

The Gold layer and team presentation must support the RFP's required recommendations for **USA and Canada men's doubles, women's doubles, and mixed doubles**, plus specified alternates. The team must also propose a **development camp** and deliver a persuasive, evidence-based presentation to the **NAPA RFP evaluation committee**.

For executive outputs, help the team communicate:

- Who is recommended and why, including partnership choices and alternatives.
- The analytical evidence and decision criteria, stated in business language.
- Confidence, uncertainty, data-quality effects, and major risks or tradeoffs.
- Development-camp rationale and useful next steps.
- How the team can reproduce its results and explain its use of AI-assisted development.

The published RFP controls exact roster sizes, eligibility, and number of alternates. Do not fabricate them. Keep technical details in supporting materials or the repository rather than overwhelming the committee presentation.

## 8. GitHub and Databricks workflow

- Treat the team GitHub repository as the shared source of truth. All four members may work on feature branches, use Codex, run local tests, and test non-destructive functionality. Review pull requests and merge deliberately.
- Keep commits focused; review AI-generated changes before accepting them.
- Shared release execution must use reviewed files from approved GitHub `main`. Record the exact commit SHA used for shared work. Do not assume GitHub Actions are available.
- Coordinate every intentional reload that can replace shared Bronze, Silver, or Gold data. Normal Bronze use keeps `existing_table_action = "fail"`.
- Use team-specific, serverless-compatible Databricks Free Edition configurations and fully qualified table names where appropriate. Use the active Databricks SparkSession and documented APIs. Prefer documented SQL metadata commands such as `SHOW CATALOGS`; do not rely on unsupported or invented methods, including `spark.catalog.catalogExists()`.
- Make permission and metadata-query failures visible. Test doubles must not conceal unsupported runtime APIs, and local-only Spark behavior must not be treated as Databricks compatibility evidence.
- Preserve the existing bundle includes and other team work when adding jobs. Never use broad deletion or `bundle destroy` as routine troubleshooting.
- Do not commit full NAPA datasets, Delta storage, credentials, tokens, `.env` secrets, or private workspace paths to the public repository.

For Bronze, configure and run `notebooks/00_bootstrap_bronze.py` directly in Databricks Free Edition according to `docs/bronze_bootstrap_guide.md`. Follow later instructor guidance for Silver deployment and execution.

## 9. Validation and completion

Follow the staged profile sequence in Section 4. At every Bronze profile, record table/count reconciliation and validation results. Follow the forthcoming revised Silver guidance for Silver evidence. Keep local checks distinct from controlled live execution in Databricks Free Edition, and never claim a test passed unless it ran.

Before presenting Gold conclusions, confirm data lineage, valid joins and eligibility, correct historical dates, interpretable comparisons, and reproducibility from production Silver. Performance optimization and elaborate CI/CD are outside the required scope unless the team explicitly elects to explore them.

At the end of a task, respond briefly with:

```text
Summary: what changed and why
Files: paths changed
Validation: checks actually run and their results
Decisions: assumptions or choices for the team
Remaining: limitations and next steps
```

**Guiding rule:** Let the detailed prompts specify how to construct Bronze and Silver. Let the students specify what Gold should accomplish. Help them implement, validate, understand, and defend the resulting solution.
