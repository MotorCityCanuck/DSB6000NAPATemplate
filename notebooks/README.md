# Notebook Guide

This directory contains two instructor-supplied Databricks notebooks:

- `00_bootstrap_bronze.py` creates and validates source-preserving Bronze tables.
- `01_build_silver.py` creates accepted Silver tables, per-source reject tables, and the persisted DQ summary defined in `docs/silver_specification.md`.

Follow `docs/bootstrap_guide.md`: manually run Bronze, inspect its results, then manually run Silver and inspect accepted, rejected, and quality-summary evidence. The jobs are independent and have no schedule or automatic chain.

Teams may add notebooks for team-designed Gold analytics, executive evidence, or presentation support. Gold tables, methods, and recommendation algorithms remain team-controlled.
