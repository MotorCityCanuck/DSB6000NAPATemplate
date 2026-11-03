# NAPA Technical Documentation

The `/docs` directory provides the engineering specifications, technical references, and team working documents for the NAPA Olympic Analytics case study. Use this index to find the governing document for a task; follow the linked document rather than copying its detailed instructions here.

## Documentation Authority

- The official NAPA RFP and Canvas assignments govern business requirements, eligibility, submissions, and assessment.
- The supplied Bronze and Silver construction prompts govern their respective prescribed engineering implementations and acceptance requirements.
- The dataset specification, delivered files and manifest, and repository configuration provide technical reference context.
- Team-maintained documents record implementation decisions, execution evidence, governance, and analytical reasoning.

The engineering foundation is prescribed through Silver. Gold organization, features, analytical methods, validation choices, and recommendation logic remain team-designed within the assignment requirements.

## Prescribed Engineering Specifications

| Document | Purpose | Authority |
|---|---|---|
| [Raw-to-Bronze construction prompt](raw_to_bronze_prompt.md) | Complete construction and acceptance contract for parameterized Raw ingestion and Bronze certification. | **Prescribed** |
| [Bronze-to-Silver construction prompt](bronze_to_silver_prompt.md) | Complete construction, quality, rejection, reconciliation, and acceptance contract for Silver. | **Prescribed** |

## Dataset and Technical References

| Document | Purpose | Authority or maintenance |
|---|---|---|
| [Dataset specification](dataset_specification.md) | Profiles, source package contents, record grains, relationships, release conventions, and documentation boundaries. | **Prescribed technical reference** |
| [Data dictionary](data_dictionary.md) | Field-level definitions, business meanings, and unresolved semantic questions based on actual data and implementations. | **Team-maintained** |
| [Data quality rules](data_quality_rules.md) | Registry for mandatory prompt requirements and additional team-defined analytical checks without redefining the prompts. | **Team-maintained** |
| [Architecture](architecture.md) | Consolidated platform architecture, layer responsibilities, namespace patterns, deployment approach, and decision record. | **Team-maintained** |
| [Lineage](lineage.md) | Expected engineering lineage plus verified implementation and team-designed Gold traceability. | **Team-maintained** |

## Team-Maintained Working Documents

| Document | Purpose | Maintenance |
|---|---|---|
| [Documentation index](README.md) | Current map of the documents in this directory and their authority. | **Team-maintained** |
| [Assignment context](assignment_context.md) | Team interpretation of client objectives, scope, assumptions, uncertainties, and clarification needs. | **Team-maintained** |
| [Analytical methodology](analytical_methodology.md) | Team-selected Gold analytical approach, validation, uncertainty, and recommendation rationale. | **Team-maintained** |
| [Data quality report](data_quality_report.md) | Actual run findings, handling decisions, readiness, and downstream analytical impacts. | **Team-maintained** |
| [Governance](governance.md) | Ownership, stewardship, classification, access, controls, and governance risks. | **Team-maintained** |
| [Runbook](runbook.md) | Reproducible environment setup, configuration, deployment, execution, validation, and troubleshooting evidence. | **Team-maintained** |
| [AI usage summary](ai_usage_summary.md) | AI-assisted activities, human review, validation, risks, and accountability evidence. | **Team-maintained** |
