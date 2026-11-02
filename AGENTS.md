# AGENTS.md

## 1. Purpose

This is a **student team repository** for the North American Pickleball Association (NAPA) Olympic Analytics case study in DSB6000, Data Science Strategy & Leadership.

Help the team build a repeatable Raw-to-Bronze-to-Silver data platform, design its own Gold analytics, recommend competitive doubles rosters, and present its case to the NAPA RFP evaluation committee. The project emphasizes **AI-assisted development, analytical judgment, governance, and leadership** rather than advanced infrastructure engineering.

Students own the analytical strategy, final recommendations, and submitted work. The AI assistant can write substantial code, tests, notebooks, and presentations **at the team's direction**, but must explain assumptions and results. Do not assume a completed implementation or another team's solution is available.

## 2. Sources of truth

Read the documents that actually exist in the repository before acting:

1. **NAPA RFP and course assignment:** business requirements, eligibility, deliverables, milestones, and assessment criteria.
2. **`raw_to_bronze_prompt.md`:** detailed Raw-to-Bronze construction and acceptance contract.
3. **`bronze_to_silver_prompt.md`:** detailed Bronze-to-Silver construction, data-quality, and acceptance contract.
4. **Delivered Parquet files and colocated `manifest.json`:** physical source and release evidence.
5. **README, existing code/configuration/tests, and team decisions:** implementation context.

Find the actual locations of these files; do not assume a particular folder layout. The two construction prompts govern their respective layers. **Do not duplicate, weaken, or silently replace their technical specifications.** If a genuine conflict appears, explain it to the team and seek direction before changing affected behavior.

## 3. Working with the team

For each task:

1. Read the relevant RFP/specification, build prompt, and existing implementation.
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
  -> Bronze Delta tables (supplied construction prompt)
  -> Silver Delta tables + rejects and quality evidence (supplied prompt)
  -> Gold features, analytics, comparisons, and rankings (team-designed)
  -> roster recommendations, development camp, and RFP presentation
```

Use the **same parameterized Bronze implementation and the same parameterized Silver implementation** for all five independent, full-refresh dataset profiles. The `dataset_profile` values, in recommended test order, are:

1. `napa_5k_clean`
2. `napa_5k_tainted`
3. `napa_50k_clean`
4. `napa_50k_tainted`
5. `napa_250k_production`

For each profile, build and validate Bronze before running Silver. The production-scale dataset includes imperfect data. Use configuration for the team's catalog, prefix, schemas, and Volumes. Avoid hard-coded personal or cross-team paths. The initial five profiles are **not incremental monthly updates**; follow separate instructions if additional releases are issued.

## 5. Layer boundaries

**Raw:** The delivered source package contains 13 Parquet files and `manifest.json` in the selected Raw Volume. Preserve it as received. The manifest is delivery evidence, not an additional Bronze table.

**Bronze:** Follow the complete Raw-to-Bronze prompt. Validate files and manifest, preserve all original business rows and columns (including duplicates and invalid values), append required technical metadata, publish Delta tables, and reconcile counts. Do not cleanse or engineer business features in Bronze. Use the prompt's selected-profile refresh and failure rules.

**Silver:** Follow the complete Bronze-to-Silver prompt. Preserve all available source business attributes in accepted outputs, standardize and validate data, and write required rejected-record and quality evidence. Do not synthesize fixes or choose a winner among duplicate primary keys. Expected data-quality defects must be logged and rejected **without independently failing the whole job**; genuine technical errors must fail visibly. Preserve remaining Silver and diagnostic evidence after technical failure until the next run completes preflight and performs its specified targeted reset.

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

- Treat the team GitHub repository as the shared source of truth. Work on feature branches, review pull requests, and merge deliberately.
- Keep commits focused; review AI-generated changes before accepting them.
- Use **manual Databricks Asset Bundle** validation, deployment, and job runs. Do not assume GitHub Actions are available.
- Use team-specific, serverless-compatible Databricks Free Edition configurations and fully qualified table names where appropriate.
- Preserve the existing bundle includes and other team work when adding jobs. Never use broad deletion or `bundle destroy` as routine troubleshooting.
- Do not commit full NAPA datasets, Delta storage, credentials, tokens, `.env` secrets, or private workspace paths to the public repository.

Typical commands after configuration and team approval:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev napa_raw_to_bronze --params dataset_profile=napa_5k_clean
databricks bundle run -t dev napa_bronze_to_silver --params dataset_profile=napa_5k_clean
```

Use the actual bundle job names if the team's configuration differs. Deployment success alone does not establish correct data.

## 9. Validation and completion

Follow the staged profile sequence in Section 4. At every profile, verify the relevant prompt's acceptance criteria and record run IDs, table/count reconciliation, validation results, and defect logs. Use small deterministic fixtures for unit tests and actual Spark/Delta execution where required to prove behavior. Never claim a test passed unless it ran.

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
