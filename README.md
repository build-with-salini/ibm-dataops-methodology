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

## 10. Identifying the Data Issues

Before a DataOps team can deliver value, it must honestly assess the current state of its data landscape. Data issues typically fall into three categories, each of which creates different bottlenecks in delivery:

### Data Inventory Issues

These issues prevent the team from even knowing what data exists and where.

- **Lack of classification** of critical data elements (CDEs) and physical assets to high-priority business initiatives — teams can't connect data to business outcomes
- **Lack of known available existing data assets** — data exists but is undiscovered, duplicated, or siloed
- **Inability to gain access to data sets** — access controls or ownership gaps block progress
- **Inconsistent data definitions** — the same field means different things in different systems, making joins and comparisons unreliable
- **Lack of established communication with Subject Matter Experts (SMEs)** — data engineers can't resolve ambiguity without domain experts, but there's no structured way to engage them

### Data Quality and Governance Issues

These issues affect whether data can be trusted once found.

- **Inability to prioritise data quality and governance issues** against high-priority business initiatives — everything feels equally urgent, so nothing gets fixed strategically
- **Inability to clearly define data quality goals** — without agreed quality rules, "good enough" is subjective and inconsistently applied
- **Inability to quickly remediate data quality issues** — root causes are unclear or fixing them requires access to upstream systems that other teams own
- **Lack of a structured governance program** — ad-hoc governance means policies are inconsistently enforced or ignored entirely
- **Lack of ability to enforce data quality and privacy rules** — policies exist on paper but there's no mechanism to detect or act on violations

### Data Integration Issues

These issues affect the ability to move, combine, and deliver data reliably.

- **Lack of ability to map high-value data pipelines** — no clear picture of which pipelines are most critical to the business
- **Inability to clearly define data flow requirements** — vague or undocumented specifications lead to rework
- **Lack of goals and measures for developing and maintaining data flows** — pipelines are built and forgotten, with no quality bar for ongoing operation
- **Lack of knowledge of existing data flows and data assets** — pipelines are duplicated, or data is re-fetched from source when it already exists downstream

> **Key insight:** These three issue categories directly map to the three KPI categories (see Section 11). Identifying issues upfront allows each data sprint to include intentional time to address them, rather than having them silently derail delivery.

---

## 11. Describing Data KPIs

KPIs give a DataOps team a shared, measurable definition of progress. Without them, "are we done?" is unanswerable. KPIs are organised into the same three categories as the issues they address.

### Data Inventory KPIs

These measure how well the organisation knows and manages its data assets.

| KPI | What it measures |
|-----|-----------------|
| % assets discovered | How much of the data landscape has been found and catalogued |
| % assets classified | How much data has been labelled by type, domain, or sensitivity |
| % assets assigned business terms | How much data is linked to the business glossary, making it understandable to non-technical users |
| % assets with completed metadata | How much data has owner, description, lineage, and quality information filled in |
| % assets assigned governance policy | How much data has rules applied (e.g., retention, access, privacy) |
| % assets with an assigned data steward | How much data has a named accountable person |
| % assets assigned a data privacy policy | How much data has been assessed for privacy risk and labelled accordingly |

### Quality and Governance KPIs

These measure whether data can be trusted.

| KPI | What it measures |
|-----|-----------------|
| Overall quality score | Aggregate measure of data quality across all assets in scope |
| Quality score for CDEs | Quality focused specifically on Critical Data Elements — the fields that most directly affect business outcomes |
| % data quality exceptions unresolved | Proportion of known quality issues that remain open |
| Average time to data quality exception resolution | How fast the team responds to and fixes quality problems |
| Estimated business impact due to data quality issues | Translates quality problems into business terms (revenue risk, compliance exposure, etc.) |

### Integration KPIs

These measure the reliability and performance of data movement.

| KPI | What it measures |
|-----|-----------------|
| % rows completed by organisation | Completeness of data flowing through pipelines from each source system |
| Average completion time per 10k rows by organisation | Pipeline throughput — a performance baseline for each data source |
| % data integration exceptions unresolved | Proportion of pipeline failures or data gaps that remain open |
| Average time to data integration exception resolution | How fast pipeline issues are diagnosed and fixed |
| Estimated impact due to data integration issues | Business cost of pipeline failures (delayed reports, incorrect analytics, etc.) |

> **Why KPIs matter in every sprint:** KPIs make the implicit explicit. They allow stakeholders to see progress, allow the team to prioritise ruthlessly, and create a shared definition of "done" that survives team turnover.

---

## 12. Critical Data Elements (CDEs) and Critical Data Sources (CDSs)

### What are Critical Data Elements?

A **Critical Data Element (CDE)** is a data field that is essential to a specific business outcome. Not all data is equally important — CDEs are the subset that, if missing or wrong, would materially affect a business decision or process.

Identifying CDEs:

- **Specifies the Data Inventory** — CDEs define the scope of what the team needs to find, classify, and track
- **Describes data as "Information"** — CDEs are expressed in business language (e.g., "Customer Date of Birth") rather than technical field names (e.g., `cust_dob_dt`), making them generally understood across the organisation
- **Existing business terms can help** — a business glossary, if one exists, accelerates CDE identification by providing pre-agreed definitions
- **Identify Critical Data Sources where possible** — once CDEs are agreed, the team maps them to the system(s) of record that hold authoritative values

### Why CDEs Drive Sprint Scope

CDEs are the unit of work. A data task is essentially: *"deliver this set of CDEs, from these Critical Data Sources, to this level of quality, for this business purpose."* Without CDEs, sprint scope is vague. With them, the team has a precise, verifiable definition of what needs to be done.

The scope also matters for complexity estimation:
- 20 CDEs from a **single domain** (e.g., all about a Customer) are relatively straightforward to deliver
- 20 CDEs **spread across multiple domains** (Customer, Product, Transaction, Risk) crossing different lines of business and sourced from multiple systems involve exponentially more coordination, governance, and integration effort

---

## 13. Delivering Business Value Through Data Sprints

### Why Business Value is Central to DataOps

A major goal of DataOps is to **deliver business value quickly** to stakeholders and data consumers. This is in sharp contrast to traditional data management, which often treats all data as equally valuable and attempts to make everything available from every source — an approach that mirrors a manufacturer producing 1,000 units of every product regardless of demand.

DataOps instead functions like a **demand-driven factory floor**:

- The data pipeline carries raw data through processes of refinement, quality assurance, and integration
- The output is not raw data — it is **trusted, business-ready data** delivered to specific consumers for specific purposes
- At every stage, the question is: *what does the consumer need, and when?*

Speed of delivery is a direct result of focus. Vague or unbounded requirements introduce waste. DataOps borrows from Agile and DevOps to impose discipline: small, iterative deliveries with defined outcomes, measurable progress, and continuous stakeholder involvement.

### The DataOps Team

A DataOps team is deliberately cross-functional, combining:

- **Deep business subject matter expertise** — understanding what data means and how it is used in context
- **Data stewardship expertise** — ensuring data gathered is optimised for reuse across the organisation, not just for one task
- **Detailed knowledge of data sources** — understanding where data lives, how it is structured, and what its quality characteristics are
- **Skilled data engineering** — the technical capability to ensure quality, combine, and transform data reliably

Because these people are scarce and expensive, it is critical to **maximise the team's throughput** by focusing effort on work that directly delivers business value — and to be able to demonstrate that return to the organisation.

### Data Stories, Data Tasks, and Data Issues

Requirements in DataOps are expressed as atomic units of work, using terminology borrowed from adjacent disciplines:

- **Data Stories** — borrowed from Agile, describing a data need from the perspective of the data consumer
- **Data Tasks** or **Data Issues** — borrowed from GitHub, describing the concrete work required to deliver a CDE or set of CDEs to a defined quality standard

Each data task:
- Clearly articulates the **business value** of delivering the information
- Defines **what is required** (CDEs and their sources)
- Specifies **when the goal has been reached** (KPIs)
- Can be tagged with metadata such as urgency, stakeholder, and domain to support prioritisation

### Creating a Data Sprint

A data sprint is a time-boxed, focused iteration of the DataOps team. It bundles data tasks into a coherent unit of work that can be delivered end-to-end. When creating a sprint:

- **Consider the priority and score of data tasks** — tasks are ranked by business impact, urgency, and risk of non-delivery
- **Group data tasks with overlapping Critical Data Sources** — tasks that draw from the same source systems can share discovery, profiling, and integration work, reducing duplication
- **Include technical debt** — every sprint should allocate capacity to address underlying data infrastructure problems (undocumented pipelines, unclassified assets, missing stewards) that would otherwise accumulate and slow future sprints
- **Validate the right mix in the DataOps team** — confirm that all necessary roles (engineer, steward, quality analyst, SME) are represented for the tasks in the sprint
- **Assign KPIs to the data sprint** — each sprint has measurable targets, not just a to-do list
- **Use dashboards to measure progress** — real-time visibility into KPIs allows the team and sponsors to answer "are we done yet?" at any point during the sprint

### Addressing the Factory Floor's Health

Each sprint is also an opportunity to incrementally improve the data infrastructure without halting business delivery. The team should regularly assess:

- **Data inventory health** — are CDEs being classified? Are stewards assigned? Is the catalog growing?
- **Governance maturity** — are quality rules being defined and enforced consistently across sources, not just in one line of business?
- **Integration reliability** — are pipelines documented? Are known issues being resolved or accumulating?
- **Team dynamics** — are cross-functional handoffs working? Are SMEs engaged effectively?

These health checks prevent the team from optimising locally (delivering one sprint perfectly) while the broader data environment degrades around them.

---

## Summary: The Business Value Loop

```
Identify Issues (Inventory / Quality / Integration)
         ↓
Define CDEs and Critical Data Sources
         ↓
Create Data Tasks (Stories / Issues) with clear business value
         ↓
Assemble a Data Sprint (prioritised, KPI-driven, right team mix)
         ↓
Deliver Trusted, Business-Ready Data
         ↓
Measure with KPIs → Review → Refine → Next Sprint
```

## 14. Data Quality — Why It Matters

Data quality is not a technical nicety — it is a business risk. Poor quality data leads to incorrect decisions, failed regulatory audits, customer dissatisfaction, and wasted engineering effort. In a DataOps context, data quality is everyone's responsibility and must be treated as an ongoing operational discipline, not a one-time cleansing project.

A useful way to think about data quality is: **fit for purpose**. Data does not need to be perfect in every dimension — it needs to meet the quality bar required for the specific business use case it supports. A customer phone number used for marketing may tolerate a 5% error rate. The same field used to send legally required notifications cannot.

---

## 15. Common Data Quality Dimensions

Data quality is multi-dimensional. A dataset can be accurate but incomplete, or complete but inconsistent. The five most commonly referenced dimensions are:

| Dimension | Definition | Example of failure |
|-----------|------------|-------------------|
| **Accuracy** | Data correctly reflects the real-world entity or event it represents | A customer's date of birth is recorded as 1920 instead of 1990 |
| **Completeness** | All required data is present — no mandatory fields are null or missing | 30% of customer records are missing an email address |
| **Consistency** | The same data element has the same value across different systems or representations | A product price is £10 in the CRM but £12 in the billing system |
| **Integrity** | Relationships between data entities are valid and referential integrity is maintained | An order record references a customer ID that does not exist in the customer table |
| **Uniqueness** | Each real-world entity is represented only once — no duplicates | The same customer appears three times under slightly different name spellings |

> **Why five is not enough:** These five dimensions are a good starting point but are not exhaustive. Gartner's framework (see Section 16) extends this significantly to cover dimensions that are harder to measure but equally important in practice.

---

## 16. Gartner Data Quality Dimensions

Gartner's data quality model divides dimensions into two categories: **Objective** (measurable by automated rules) and **Subjective** (assessed by human judgement). Both matter in practice.

### Objective Dimensions

These can be measured programmatically against known rules or reference values.

| Dimension | What it means |
|-----------|--------------|
| **Accessibility** | Data can be found and retrieved by those who need it, within an acceptable time frame |
| **Accuracy** | Data correctly reflects the real-world fact it represents |
| **Consistency** | Data values do not conflict across systems or time periods |
| **Completeness** | All required attributes are populated |
| **Existence** | The data asset itself exists and is available — it has not been deleted, corrupted, or lost |
| **Integrity** | Relationships between records are valid (referential integrity, no orphaned records) |
| **Precision** | Data is recorded at the right level of granularity — not too coarse, not unnecessarily fine |
| **Reliability** | Data can be depended upon to be consistently available and accurate over time |
| **Timeliness** | Data is available when it is needed and reflects the current state of the real world |
| **Uniqueness** | No duplicate representations of the same real-world entity exist |
| **Validity** | Data conforms to defined formats, ranges, and business rules (e.g., a date field contains a valid date) |

### Subjective Dimensions

These require human interpretation and cannot be fully automated — they depend on context, domain knowledge, and stakeholder judgement.

| Dimension | What it means |
|-----------|--------------|
| **Accessibility** | Data is easy to find and access from the perspective of the consumer (overlaps with objective, but includes UX and discoverability) |
| **Believability** | Data consumers trust and believe the data — often influenced by source reputation and past quality |
| **Clarity** | Data and its metadata are expressed in language that is unambiguous to the intended audience |
| **Interpretability** | The data can be correctly understood and used by its consumers — labels, units, and context are sufficient |
| **Objectivity** | Data is collected and presented without bias — the process that produced it does not systematically favour one outcome |
| **Usability** | Data is in a form that makes it practical to use for its intended purpose without excessive transformation |

> **Key insight:** Subjective dimensions are often the reason that technically "clean" data is still not trusted or used by the business. A dataset can score highly on all objective dimensions and still fail on believability or interpretability if the data team has not invested in communication, metadata, and stakeholder engagement.

---

## 17. The Data Quality Framework

IBM's Data Quality Framework provides a structured, repeatable four-stage process for managing data quality. It is cyclic — Monitor feeds back into Define for continuous improvement.

```
Define → Assess → Remediate → Monitor → (back to Define)
```

The framework applies to every Critical Data Element (CDE) and every data sprint. It prevents quality management from being reactive (only fixing things when a problem is reported) and instead makes it proactive and measurable.

---

## 18. Stage 1 — Define Data Quality

The Define stage establishes **what good looks like** before any measurement begins. Without this, "assess" is meaningless because there is no standard to measure against.

### Key Activities

**Review CDEs**
Start with the Critical Data Elements identified for the current data task or sprint. Quality rules are defined per CDE, not generically across all data. Different CDEs will have different quality requirements based on their business use — a field used in regulatory reporting has a zero-tolerance threshold for errors; a field used for internal dashboards may tolerate more.

**Define data quality dimensions to measure for CDEs**
Not every dimension applies to every CDE. For each CDE, select the relevant dimensions from the common or Gartner lists (Sections 15–16). For example, a date-of-birth field will need: accuracy, completeness, validity (is it a real date?), and timeliness (is it current?). A transaction amount field may additionally need precision and consistency across systems.

**Define acceptable thresholds and agree with the business**
This is a collaborative, not a technical, step. The data team proposes a threshold (e.g., "95% completeness for customer email address") and negotiates with the business stakeholder who owns that CDE. The agreed threshold becomes the quality target for the sprint KPI. Without this agreement, disputes arise later about whether quality is "good enough."

**Review and associate metadata with critical data elements**
Metadata enriches the CDE with context: who owns it, where it comes from, what it means, what governance policy applies. This metadata is essential for quality assessment (you need to know the source to understand why quality might be poor) and for enabling self-service by downstream consumers.

---

## 19. Stage 2 — Assess Data Quality

The Assess stage measures the **actual quality of data** against the thresholds defined in Stage 1. It produces a clear, evidence-based picture of where quality problems exist and what their likely impact is.

### Key Activities

**Conduct data profiling**
Data profiling is the systematic examination of a data source to understand its structure, content, and statistics. Profiling reveals: null rates per field, value distributions, min/max/average values, pattern analysis (e.g., are phone numbers in the expected format?), uniqueness counts, and referential integrity checks. Profiling is typically run by a Data Quality Analyst using automated tooling (e.g., IBM Watson Knowledge Catalog, Informatica, or open-source tools like Great Expectations). It gives the team an objective, data-driven baseline — removing guesswork about where problems lie.

**Design and implement Data Quality Rules**
Quality rules are the programmatic expressions of the thresholds agreed in Stage 1. For example: "field `customer_email` must not be null AND must match regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`". Rules are typically implemented in the data platform or quality tool, run against the data, and produce pass/fail counts per record. Well-designed rules are reusable — once written for a CDE, they can be applied across every system that contains that element.

**Review and analyse profiling results**
Raw profiling output is translated into actionable intelligence. The quality team examines: which rules are failing and at what rate, whether failures are concentrated in specific sources or time periods, whether the failures are systematic (a process bug) or random (data entry errors), and what the trend is over time (getting better or worse?).

**Identify critical data quality exceptions and develop recommendations**
Not all quality failures have the same business impact. The team prioritises exceptions by their effect on the business use case (a missing field in a regulatory report is more critical than a missing field in an internal dashboard). For each critical exception, a recommendation is produced: fix at source, cleanse at ingestion, apply a transformation rule, or accept and document the limitation.

---

## 20. Stage 3 — Remediate Data Quality

Remediation is about **fixing quality problems** — but critically, it distinguishes between fixing the symptom (the bad data) and fixing the cause (the process that produced it). DataOps emphasises root-cause remediation over repetitive cleansing.

### Key Activities

**Resolve data quality exceptions**
Exceptions identified in the Assess stage are worked through systematically. Some can be resolved automatically (e.g., a transformation rule that standardises date formats). Others require manual review by a Data Steward or SME (e.g., deciding which of two conflicting customer addresses is correct). Each resolved exception is logged with its resolution method, creating an audit trail.

**Data cleansing techniques and data validation**
Data cleansing is the process of correcting or removing inaccurate, incomplete, or improperly formatted data. Common techniques include: standardisation (reformatting values to a consistent pattern), deduplication (merging or removing duplicate records), enrichment (filling missing values from a reference source), and parsing (breaking a combined field into structured components, e.g., splitting a full name into first and last). Data validation confirms that after cleansing, the data now meets the defined quality rules.

**Share results with stakeholders (data source and data application owners) so they can work to eliminate the root cause**
This is the most important and most often skipped step. Simply cleansing data at the pipeline level means the same bad data will arrive again next time. Sharing quality reports with the owners of the source system — and working with them to fix the upstream process, UI validation, or ETL logic that is generating poor quality data — is the only path to sustainable quality improvement. DataOps treats this as a collaborative loop, not a blame exercise.

---

## 21. Stage 4 — Monitor Data Quality

Monitoring ensures that **quality improvements are sustained** and that new problems are detected quickly. Without monitoring, quality degrades silently between assessments.

### Key Activities

**Perform profiling on a regular basis to compare profile results**
Profiling is not a one-time activity — it should be scheduled to run on each data refresh cycle. Comparing current profile results against historical baselines reveals quality drift: fields that were 98% complete last month and are now 85% complete indicate a problem in an upstream process. Trend analysis also demonstrates improvement over time, which is valuable for reporting to sponsors.

**Monitor data quality by using business rules**
Beyond statistical profiling, business rules encode domain-specific expectations. For example: "no customer should have a future date of birth", "every transaction must have a corresponding order record", "the sum of line-item amounts must equal the invoice total." These rules run continuously against live or near-live data and trigger alerts when violations are detected — enabling near-real-time quality assurance rather than batch-cycle discovery.

**Data Quality Dashboard**
A quality dashboard aggregates quality scores, exception counts, trend lines, and rule pass rates into a single view accessible to the DataOps team, data stewards, and business stakeholders. It answers "are we done?" (are we above the agreed threshold?) and "are we getting better?" (is the trend improving?). Dashboards also create accountability — when quality scores are visible to senior stakeholders, teams are more motivated to address root causes rather than deferring them.

**Share Data Quality Scores in catalog with data consumers**
Publishing quality scores in the data catalog — alongside the data asset itself — is a fundamental enabler of self-service analytics. When a data consumer opens a catalog entry and can see "completeness: 97%, accuracy: 99%, last profiled: 2 hours ago," they can make an informed decision about whether that data is fit for their purpose. This eliminates the "trust but verify" cycle where every consumer independently assesses quality before use, which wastes enormous time across the organisation.

---

## Summary: The Data Quality Lifecycle

```
DEFINE
  ├── Which CDEs need quality management?
  ├── Which dimensions apply to each CDE?
  ├── What are the agreed thresholds?
  └── What metadata enriches each CDE?
         ↓
ASSESS
  ├── Profile the data (automated)
  ├── Implement and run quality rules
  ├── Analyse failures by impact
  └── Prioritise exceptions
         ↓
REMEDIATE
  ├── Resolve exceptions (auto + manual)
  ├── Cleanse and validate data
  └── Feed root causes back to source owners
         ↓
MONITOR
  ├── Schedule recurring profiling
  ├── Run business rules continuously
  ├── Surface scores on dashboard
  └── Publish quality scores to catalog
         ↓
      (back to DEFINE — refine thresholds, add new CDEs)
```

### The Objective vs. Subjective Quality Balance

A mature DataOps team manages both objective and subjective quality. Automated tools handle objective dimensions at scale. Subjective dimensions — believability, interpretability, clarity — require ongoing investment in documentation, stakeholder communication, and metadata curation. Teams that ignore subjective quality often find that their data, despite being technically clean, is not actually used by the business because people do not trust or understand it.

