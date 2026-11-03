# Deliverables Guide

**Purpose:** This document explains how the deliverables folder should be used to organize milestone evidence for the NAPA Olympic Analytics Platform consulting case. The template provides the folder structure only; teams must decide what evidence to preserve and summarize based on their own implementation and review process.

The official Canvas assignments and NAPA RFP govern required submissions, eligibility rules, roster sizes, deadlines, and evaluation criteria. This guide only suggests how to organize concise, review-ready evidence in the repository.

## Milestone folders

Milestones do not correspond exclusively to the 5K, 50K, and 250K dataset sizes. The five dataset profiles support different stages of development, validation, and final analysis across the three milestones.

The profiles are `napa_5k_clean`, `napa_5k_tainted`, `napa_50k_clean`, `napa_50k_tainted`, and `napa_250k_production`.

### `milestone_1/` — Foundation and Initial Engineering

Organize evidence of:

- development-environment readiness and the team's collaboration workflow;
- access to and validation of all five Raw dataset profiles;
- Bronze ingestion for `napa_5k_clean` and `napa_5k_tainted`; and
- successful execution and validation, such as reviewed test results, run identifiers, source inventories, table/count reconciliation, and documented limitations.

### `milestone_2/` — Data Engineering and Quality

Organize evidence of:

- completed Bronze and Silver processing for all five dataset profiles;
- required data-quality checks, reject evidence, reconciliation, and validation results;
- findings, issue dispositions, and remediation decisions without altering delivered Raw files; and
- reproducible pipeline execution, including the profiles, configuration evidence, run identifiers, commands, and checks actually used.

### `milestone_3/` — Analytics and Recommendations

Organize evidence of:

- the team-designed Gold layer and analytical development;
- final Olympic doubles roster recommendations for the USA and Canada in men's, women's, and mixed doubles;
- specified alternates and development-camp recommendations; and
- traceable support for analytical conclusions, uncertainty, limitations, and executive deliverables.

The 250K production profile supports final production-scale recommendations, while smaller profiles may also provide development and validation evidence. The team determines and documents its Gold methodology; this guide does not prescribe analytical methods or models.

## Commit guidance

Large files should not be committed unless instructed. When a milestone folder is used, include a short Markdown summary that explains what the folder contains, why it matters, and how it supports review.
