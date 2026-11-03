# Notebook Guide

The `notebooks/` directory is reserved for student-created Databricks notebooks and workflow entry points. The current template intentionally contains no executable notebooks.

Bronze and Silver implementation structure, execution responsibilities, validation, and acceptance requirements are governed by `docs/raw_to_bronze_prompt.md` and `docs/bronze_to_silver_prompt.md`. Teams should create the entry points required by those prompts as part of their implementation.

Teams may also create notebooks for team-designed Gold analytics, executive evidence, or presentation support. Notebook names, Gold tables, analytical methods, and algorithms remain team-controlled.

Use manual Databricks Asset Bundle validation, deployment, and execution as described by the repository workflow and construction prompts. Preserve run evidence and update the relevant lineage, runbook, and analytical documentation.
