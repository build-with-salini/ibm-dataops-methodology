# IBM DataOps Methodology

> Source: [IBM DataOps Methodology — Coursera](https://www.coursera.org/learn/ibm-data-ops-methodology)

---

## 1. What is DataOps?

> "DataOps is a collaborative data management practice focused on improving the communication, integration and automation of data flows between data managers and data consumers across an organization."

---

## 2. The DataOps Methodology

The methodology is structured in three phases that form a continuous loop:

### Phase 1 — Establish DataOps

The foundational phase that sets up the conditions for DataOps to operate. Key steps:

- Establish Data Strategy
- Establish Team
- Establish Toolchain
- Establish Baseline
- Establish Business Priorities

### Phase 2 — Iterate DataOps

The core operational cycle, centred around a **Catalog**. Activities in this phase include:

- Discover
- Classify
- Manage Quality & Entities
- Manage Policies
- Self Service
- Manage Movement & Integration
- Improve / Complete

### Phase 3 — Improve DataOps

A continuous improvement loop that feeds back into Phase 2. Key steps:

- Review
- Refine
- Recommend

> The three phases are cyclical: Establish → Iterate → Improve → (back to Iterate).

---

## 3. The AI Ladder

IBM's AI Ladder is a framework for progressively building AI capability within an organisation. The rungs, from bottom to top:

| Rung | Action | Description |
|------|--------|-------------|
| 1 | **Collect** | Make data simple and accessible |
| 2 | **Organize** | Create a business-ready analytics foundation |
| 3 | **Analyze** | Build and scale AI with trust & explainability |
| 4 | **Infuse** | Operationalize AI throughout the business |

---

## 4. Organize — Critical Capabilities

The **Organize** rung of the AI Ladder sits between Collect and Analyze. Its critical capabilities are structured around three goals: **Know**, **Trust**, and **Use**.

| Goal | Capability |
|------|------------|
| **Know** | Data Governance and Curation |
| **Trust** | Data Quality, Master Data Management |
| **Trust / Use** | Data Integration, Data Replication, Data Virtualization |
| **Use** | Data Prep for self service and testing |

> **Underpinning all capabilities:** Catalog & Metadata Management

---

## 5. What is a Data Strategy?

> A data strategy connects your business plan and priorities to your data, AI, and analytics requirements. A data strategy is the **foundation for becoming a data-centric organization**.

To be **actionable**, the strategy, architecture, roadmap and action plan are developed in consideration of your current-state culture, data, and capabilities.

### Data Strategy Development Flow

```
Business Objectives
       ↓
Unconstrained Development
(Forward-thinking, within a focused area, independent of current inhibitors)
       ↓
Constrained Development
(Opportunities and gaps, "as-is" data topology, refined current state, people and technology)
       ↓
Actionable Architectures and Strategies
  ├── Action Plan and Next Steps (Sequencing, owners, and capabilities to deliver)
  └── Strategic Roadmap
       ↓
Continuous Delivery of Results
(Production-ready Data and AI Solutions)
```

**Business Objectives** include: Outcomes, Stakeholders, Measures of Success.

---

## 6. Core Elements of a Data Strategy

> Identify data needs across multiple business objectives within or across lines of business to show the value of data as a strategic asset that should be **owned**, **managed**, and **governed**.

A data strategy bridges **Business Outcomes** (top) down to **Technology Enablers** (bottom).

### The Four Core Elements

| Element | Question it answers |
|---------|---------------------|
| **Business Objectives & Priorities** | Short-term ("keep the lights on") and longer-term ("strategic") objectives and priorities |
| **Measures & KPIs** | How do you measure success against objectives? |
| **Data Value Across Objectives** | What data is needed? |
| **Capabilities & Architecture** | What AI / analytics and technical capabilities are needed? |

### Stakeholder Considerations

Cutting across all four elements are stakeholder questions:

- Who are the stakeholders within and across the organization in support of given objectives? How are they being measured?
- Who **owns** the data?
- Who **manages** the data?
- Who **defines policies** for security, privacy, and compliance?

---

## 7. DataOps Orchestration

DataOps Orchestration describes **who does what** as data moves through its lifecycle — from raw ingestion through to business consumption. It maps roles to activities at each stage of the data pipeline, with organisation-wide **Governance** (led by the CDO) underpinning everything.

### Data Lifecycle Stages and Roles

| Stage | Data Type | Activity | Role |
|-------|-----------|----------|------|
| 1 | **Raw Data** | Organize & Structure | Data Engineer |
| 2 | **Raw Data** | Explore & Profile | Data Steward |
| 3 | **Refined Data** | Monitor & Remediate Quality | Data Quality Analyst |
| 4 | **Refined Data** | Transform | Data Engineer |
| 5 | **Refined Data** | Model | Data Scientist |
| 6 | **Business Ready Data** | Consume | Business User |

> **Governance (CDO)** spans the entire pipeline — the Chief Data Officer and their governance function oversee all stages to ensure policy, compliance, and accountability are maintained end-to-end.

### Why This Matters

Orchestration makes clear that DataOps is not a single person's job — it requires a **cross-functional team** with clearly defined handoffs. Without this clarity, data quality issues tend to fall through the cracks between teams (e.g., a Data Engineer delivers raw data but no one is assigned to profile it for quality issues before transformation).

Assigning explicit roles to each stage also enables:

- **Accountability** — each activity has an owner
- **Automation** — workflows can be built around known handoff points
- **Auditability** — you can trace issues back to a specific stage and responsible role

---

## 8. Models and Operating Standards

Operating standards provide the **shared language and rules** that allow a DataOps organisation to function consistently. Without them, different teams use different definitions of the same data, leading to conflicting reports, trust issues, and slow delivery.

### Key Models and Operating Standards

**Data Domains and Stewardship**
Data domains are logical groupings of related data (e.g., Customer, Product, Finance). Each domain is assigned a **Data Steward** — a person accountable for the quality, meaning, and appropriate use of data within that domain. Stewardship bridges the gap between technical data management and business understanding.

**Business Glossary**
A business glossary is a curated dictionary of terms and their agreed-upon definitions across the organisation. It ensures that when a data analyst says "active customer" and a finance team says "active customer," they mean the same thing. Without it, KPIs calculated by different teams will diverge even when using the same underlying data.

**Data Classification**
Classification labels data according to its sensitivity, confidentiality level, or regulatory requirements (e.g., PII, confidential, public). This directly informs access controls, encryption requirements, and retention policies. Classification is typically a precondition for effective governance.

**Reference Data**
Reference data is the set of permissible values used to categorise or describe other data — for example, country codes, currency codes, product category lists. Managing reference data centrally prevents inconsistencies where one system uses "UK" and another uses "GB" for the same country.

**Catalog**
A data catalog is a searchable inventory of an organisation's data assets — tables, reports, APIs, models — enriched with metadata such as ownership, lineage, quality scores, and classifications. It enables data consumers to **find, understand, and trust** data without having to ask the data engineering team directly, enabling true self-service.

**Workflow**
Workflows formalise the processes by which data moves through the organisation — from ingestion to quality checks to publication. Defined workflows enable automation, reduce manual intervention, and create a consistent, repeatable path to production-ready data.

---

## 9. Examples of Information Governance

Information Governance is the framework of policies, roles, and processes that ensures data is managed as a strategic organisational asset — responsibly, ethically, and in compliance with regulations.

### Information as an Asset

- Information is a **company asset** and a **sharable resource** — it should be treated with the same rigour as financial or physical assets.

### Properties of Well-Governed Information

| Property | What it means in practice |
|----------|--------------------------|
| **Identified and classified** | Every data asset is known, labelled by type and sensitivity, and recorded in the catalog |
| **Owned** | There is a named person or team accountable for each data asset |
| **Protected** | Access controls, encryption, and security measures are applied based on classification |
| **Kept as long as it is needed** | Retention policies ensure data is not held beyond its useful or legally permitted life |
| **Managed in a cost-effective manner** | Storage, processing, and maintenance costs are proportional to the value of the data |
| **Everyone's responsibility** | Governance is not just an IT or compliance function — all data users have a role in upholding standards |

### Information Users

- Information users are **identified** (known) and **responsible** (accountable for how they use data)
- **Decision makers use appropriate data** — governance ensures the right data reaches the right decision makers, in the right form
- **Information and analytics will only be used for approved, ethical purposes** — this is especially critical in the age of AI, where biased or misused data can cause real-world harm

### Why Governance Underpins Everything

Governance is not a phase or a step — it is the **operating layer beneath all DataOps activity**. Without it:

- Data quality cannot be enforced because no one owns the problem
- Regulatory compliance (GDPR, HIPAA, etc.) cannot be demonstrated
- Trust in data erodes, and business decisions revert to intuition rather than evidence
- Self-service analytics becomes dangerous, as users may access or misuse data they don't fully understand

Effective governance transforms data from a liability into a **trusted, strategic asset**.

---
