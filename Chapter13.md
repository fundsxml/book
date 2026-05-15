<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 13 — An Implementation Project from A to Z

*A practical guide for introducing FundsXML*

---

## 13.1 Setting the Scene: What an Implementation Project Looks Like

Thirteen chapters of schema, tooling, and architecture are useful only insofar as they help a real team ship a real pipeline. This chapter is about that shipping process. It describes, phase by phase, how an asset management company actually introduces FundsXML into its operational landscape — not as a collection of abstract project-management principles, but as a concrete nine-month project at the Europa Asset Management S.A. fictional-but-realistic team that has been the producer of the Europa Growth Fund's data throughout the book.

The project we follow runs from December 2025, when the project kickoff meeting was held, to August 2026, when the first production FundsXML delivery reached all eleven of the fund's distribution countries. In between are six phases: requirements analysis, data mapping, prototyping and piloting, testing, acceptance and go-live, and the transition into operations and maintenance. Each phase gets its own section in this chapter, and §13.8 lays out the full timeline as a single page for the reader who wants to see the arc at a glance.

The project is narratively specific but operationally generic. The names (Europa Asset Management, the Europa Growth Fund, the eleven distribution countries) are the fictional ones that the book has used throughout. The scale and sequence of the phases, the kinds of decisions made at each checkpoint, and the recurring challenges are drawn from real FundsXML implementation projects that the authoring community has seen in practice. A reader running a similar project should find the concrete details useful as a template to adapt rather than as a script to follow literally — every project has its own politics, its own technical debt, and its own internal opposition, and no generic walkthrough can capture all of it.

A note on scope. This chapter treats the *producer* side of the project — Europa Asset Management produces FundsXML deliveries, and the project is about building the pipeline that produces them. The *consumer* side (what the eleven distribution countries do with the deliveries) is out of scope for this chapter, except where it intersects with the producer's work. Consumers typically run their own, independent implementation projects that look structurally similar but focus on ingestion rather than emission. Readers on the consumer side can read this chapter with minor mental translation; the phase structure is the same, and most of the decisions are analogous.

By the end of this chapter, you should be able to:

- structure a FundsXML implementation project into its six standard phases and plan the duration of each;
- draw up a requirements document for a producer-side project, naming the data sources, the target consumers, and the regulatory scope;
- build a mapping table that connects internal system fields to FundsXML elements;
- run a prototyping and piloting cycle that catches structural problems before production commitment;
- design a testing plan that covers both schema validation and business-rule validation against realistic fixtures;
- organise acceptance and go-live gates with the producer's stakeholders and the consumer's downstream systems;
- transition a working pipeline from "project" to "operations" without losing the institutional knowledge the project accumulated.

---

## 13.2 Phase 1: Project Preparation and Requirements Analysis

### 13.2.1 The Trigger and the Kickoff

Every implementation project has a trigger — a specific business event that makes "do it" more urgent than "wait and see". For Europa Asset Management, the trigger was a combination of three pressures in late 2025: the French distributor BNP Distribution Services notified Europa that it would stop accepting the legacy CSV format at the end of Q2 2026 and would require FundsXML going forward; the SFDR Level 2 technical standards mandated quarterly EET deliveries from January 2026, and the existing CSV pipeline had no clean path to carry them; and an internal audit had flagged the CSV pipeline's lack of structured validation as a control weakness after a near-miss incident in October 2025. None of the three pressures alone would have justified the project; all three together made it unavoidable.

The kickoff meeting was held on 8 December 2025. Present were the head of Operations (the project sponsor), the head of IT (delivery accountability), a representative from the Fund Administration team (the data owners), a representative from the Compliance team (regulatory sign-off), and two external consultants engaged for schema expertise. The meeting ran for ninety minutes and produced three outputs: a one-page project charter, a list of twelve open questions that the next four weeks would need to answer, and a commitment to return on 5 January 2026 for a requirements review with a first draft of the answers.

### 13.2.2 The Requirements Document

Over the next three weeks, the project lead drafted the requirements document that would govern the project for the next nine months. A good FundsXML requirements document has seven sections, each shorter than a typical business requirement document because the FundsXML schema itself carries much of the structural detail that would otherwise need to be written down.

**1. Scope.** Which funds, which share classes, which distribution countries, which consumers, which regulatory modules. For the Europa project: the Europa Growth Fund and its three share classes, eleven distribution countries, initial consumer list of six retail distributors (the others would be added in a subsequent wave), regulatory modules EMT, EPT, EET, and TPT (but not EFT — the producer does not produce EFT).

**2. Frequency and Calendar.** How often a delivery is produced and for which valuation dates. Europa's decision: daily NAV deliveries to the internal fund administrator systems, monthly consolidated deliveries to external distributors, quarterly EET refreshes, quarterly TPT updates. The daily and monthly were operationally urgent; the EET and TPT were regulatory deadlines.

**3. Data Sources.** Which internal systems hold which parts of the data the pipeline needs. Europa's landscape had: a portfolio management system (PMS) holding positions and NAVs, a client reference database (CRD) holding fund and share-class static data, a regulatory reporting data mart (RRDM) holding SFDR classifications and PAI values, and an administrator-provided Excel workbook holding EMT template data. Each of the four sources had its own owner, its own release cadence, and its own quirks.

**4. Target Consumers and Delivery Channels.** Which external parties receive the deliveries, how they receive them, and what acknowledgements the producer needs. Europa's six initial distributors each had their own SFTP drop-box conventions, their own file-naming rules, and their own acknowledgement mechanisms — two used plain SFTP with a signed delivery receipt, three used SFTP with an out-of-band email confirmation, and one used an HTTPS REST API. The pipeline had to support all three.

**5. Regulatory Modules.** Which FinDatEx templates the pipeline must populate and to which version. Europa: EMT v4.3, EPT v2.4, EET v1.1.2, TPT v7.0 — all current as of 2026. The requirements document also named the ESMA technical standards each template implemented, so that the team had a clear regulatory anchor.

**6. Non-Functional Requirements.** Performance, availability, monitoring, audit, retention. Europa: deliveries must be emitted within two hours of the valuation point, availability 99.5% of business days, full audit log of every delivery retained for ten years, Monday-to-Friday business-hours monitoring with on-call escalation only for failures during the emission window.

**7. Out of Scope.** Explicit statements of what the project will *not* do. Europa's out-of-scope list included: no consumer-side pipeline (consumers handle their own ingestion), no changes to the underlying source systems (the PMS and CRD stay as-is; the pipeline reads from them), no EFT support (this producer does not produce EFT), no historical backfill (the pipeline starts with new deliveries only; pre-2026 data stays in the legacy CSV archive).

### 13.2.3 The Five Open Questions Every Project Answers Early

Beyond the written requirements, every implementation project has a short list of decisions that need to be made explicitly and early, because a wrong answer taken silently will undermine the rest of the project. Europa's five were:

1. **Build or buy?** Europa decided to build. The alternative — licensing a vendor FundsXML generator — was considered but rejected on grounds of cost and long-term flexibility. A later section (§13.4) describes the technology stack they chose.
2. **Java, Python, or C#?** Europa was a Java shop for its core systems but had a small Python team for data engineering. The decision: Java for the generator (integrated into the existing fund-administration platform), Python for the ETL that extracts source data and for the validation pipeline. Node.js was not considered, because no consumer piece was being built.
3. **In-house or cloud?** Europa ran a private datacentre for its production systems and had no public-cloud deployment in scope. The pipeline would run in the existing on-premises infrastructure, with the option to migrate to cloud later if the organisation's overall strategy moved that way. This decision simplified the security and compliance conversation significantly.
4. **Single-team or multi-team ownership?** A single cross-functional project team of four engineers plus a part-time BA and a part-time QA was chartered. Ownership would transfer to the existing Fund Operations IT team at go-live. The cross-functional structure was chosen to avoid the handoff overhead that a "development team ships, ops team operates" model would create.
5. **Greenfield or side-by-side?** Europa decided to run the new FundsXML pipeline side-by-side with the legacy CSV pipeline for a transition period, with distributors gradually switching over as each one validated their own consumer. The legacy pipeline would be decommissioned once the last distributor had confirmed successful FundsXML ingestion.

### 13.2.4 Timeline and Budget

The project plan that emerged from requirements analysis had the following shape: 5 January to 31 January 2026 for requirements completion and stakeholder sign-off; 1 February to 28 February for data mapping; 1 March to 30 April for prototyping and piloting; 1 May to 31 May for testing; 1 June to 30 June for user acceptance and go-live preparation; 1 July for first production delivery; ongoing operations thereafter. The timeline included one intentional slack week in each phase, because every FundsXML project the consultants had seen had encountered unexpected delays somewhere, and the question was only *where* the slack would be consumed. The project ultimately ran two weeks longer than plan and consumed every slack week and then some.

The budget was modest for a project of this scope: four engineers for six months full-time, plus the two consultants part-time, plus tooling and infrastructure costs. The total was comfortably under one million euros — not because FundsXML implementations are cheap, but because the existing source systems provided the hard data, and the project scope was tight enough that no upstream system remediation was required.

---

## 13.3 Phase 2: Mapping Existing Data to FundsXML

### 13.3.1 Why Mapping Is the Hardest Phase

Mapping is the phase where the abstract schema meets the concrete internal data, and it is almost always the phase where FundsXML projects discover that the hard work is not XML — it is understanding the source data. Every field that the FundsXML delivery needs has to come from somewhere, and "somewhere" usually means a column in an internal database whose meaning has been implicit for years and that no one has written down precisely. Phase 2 is the phase where the team writes it all down.

Europa's mapping phase ran from 1 February to 28 February 2026 and consumed roughly two engineer-months of effort. It produced three artefacts: a mapping spreadsheet (the core deliverable), a list of data gaps (fields FundsXML requires that no source system currently holds), and a list of data-quality issues (fields that exist in source but are populated inconsistently or incorrectly).

### 13.3.2 Structure of a Mapping Table

A mapping table has one row per FundsXML field that the pipeline needs to populate. The columns are:

- **FundsXML element path** — the XPath or dotted path from the root to the target element. For example, `ControlData/DataSupplier/LEI` or `Funds/Fund/Identifiers/LEI`.
- **Source system** — which internal system holds the source data. One of PMS, CRD, RRDM, or EMT-Excel for Europa's landscape.
- **Source column or field** — the specific column name or field identifier in the source system. For example, `CRD.LEGAL_ENTITIES.LEI_CODE`.
- **Transformation rule** — any conversion, lookup, or derivation needed between the source value and the target value. For example, "trim to 20 characters", "convert DD/MM/YYYY to ISO", "lookup country code from COUNTRY_ID via COUNTRY dimension".
- **Default value** — what to write if the source is null or missing. Often blank (meaning "omit the optional element"); sometimes a hard-coded literal.
- **Notes** — any peculiarities, known edge cases, or questions for a later round.

**Table 13.1 — Excerpt from Europa Asset Management's mapping table (ControlData)**

| FundsXML path | Source system | Source column | Transformation | Default |
|---|---|---|---|---|
| `ControlData/UniqueDocumentID` | (generated) | — | Concatenate: `EGF-` + `YYYYMMDD` + `-` + sequence number | — |
| `ControlData/DocumentGenerated` | (system clock) | — | Current UTC timestamp at emission | — |
| `ControlData/Version` | (constant) | — | Hard-coded `4.2.8` | `4.2.8` |
| `ControlData/ContentDate` | PMS | `VALUATION.VAL_DATE` | Convert to ISO format | — |
| `ControlData/DataSupplier/SystemCountry` | (constant) | — | Hard-coded `LU` | `LU` |
| `ControlData/DataSupplier/Short` | (constant) | — | Hard-coded `EAM` | `EAM` |
| `ControlData/DataSupplier/Name` | CRD | `COMPANIES.LEGAL_NAME` | Where `ROLE = 'MANUFACTURER'` | — |
| `ControlData/DataSupplier/Type` | (constant) | — | Hard-coded `IC` | `IC` |
| `ControlData/DataOperation` | (computed) | — | Normal delivery: `INITIAL`; retry: `AMEND` | `INITIAL` |
| `ControlData/Language` | (constant) | — | Hard-coded `en` | `en` |
| `Funds/Fund/Identifiers/LEI` | CRD | `FUNDS.LEI_CODE` | Where `FUND_ID = :current` | — |
| `Funds/Fund/Names/OfficialName` | CRD | `FUNDS.OFFICIAL_NAME` | Where `FUND_ID = :current` | — |
| `Funds/Fund/Currency` | CRD | `FUNDS.BASE_CURRENCY` | ISO 4217 code | — |
| `Funds/Fund/SingleFundFlag` | (computed) | — | `true` if no sub-funds, else `false` | `true` |
| `Funds/Fund/FundDynamicData/TotalAssetValues/TotalAssetValue/NavDate` | PMS | `NAV_HEADER.VAL_DATE` | — | — |
| `Funds/Fund/FundDynamicData/TotalAssetValues/TotalAssetValue/TotalAssetNature` | (computed) | — | `OFFICIAL` for final NAV; `ESTIMATED` for preliminary | `OFFICIAL` |
| `Funds/Fund/FundDynamicData/TotalAssetValues/TotalAssetValue/TotalNetAssetValue/Amount` | PMS | `NAV_HEADER.TNAV` | `ccy` attribute from `NAV_HEADER.CCY` | — |

The excerpt above shows seventeen rows. The full mapping table for the Europa Growth Fund project had approximately 450 rows covering the complete ControlData, Fund, Portfolio, and RegulatoryReportings blocks. Each row was reviewed by the data owner of the relevant source system and signed off formally. The sign-off was important because the mapping became the authoritative contract between the producer pipeline and the source systems: any change to a source column's meaning or format would need to be reflected in the mapping before the pipeline could handle it.

### 13.3.3 Handling Data Gaps

The mapping exercise inevitably surfaces **data gaps**: FundsXML fields that the producer needs to populate but that no existing source system holds. Europa's project found twenty-three such gaps, ranging in severity from "trivial, add a constant" to "major, requires new upstream data feed". Three of the more interesting ones:

- **`Funds/Fund/FundStaticData/Custodian`** — the custodian (depositary bank) of the fund. The CRD held the custodian relationship for recent funds but not for older funds that had been migrated from a legacy system in 2018. For the Europa Growth Fund specifically the data was there; for other funds that would be onboarded later, the CRD would need to be backfilled. The decision: phase-1 launch covered only funds with complete custodian data in CRD; the backfill was logged as a follow-on task.
- **`RegulatoryReportings/EET/EET_PAI/*`** — the PAI values for the EET. These were held in the RRDM but with a quarterly refresh cadence, which conflicted with the monthly EET that the quarterly-only regulatory schedule didn't strictly demand. The decision: emit the most-recent PAI values in every monthly delivery, with an explicit `EET_PAI_AsOfDate` field indicating when the values were computed. Consumers who need real-time PAI values would get stale data; consumers following the standard quarterly cadence would see no difference.
- **`Funds/Fund/FundStaticData/FundTexts`** — the multi-language marketing and investment-objective text. These existed in the CRD but only in English; the German, French, and Italian translations were maintained in a separate Marketing-managed spreadsheet that had never been integrated with the core systems. The decision: phase-1 launch included English-only text; the multi-language build-out was scheduled for phase 2 of the project in September 2026.

Data gaps are rarely blockers in themselves, but they force the project to make scoping decisions about whether to launch without the missing data, delay until the gaps are filled, or invent a workaround. Europa's approach — ship without the missing data, fill the gaps in follow-on waves — is the most common pragmatic choice.

### 13.3.4 Data-Quality Issues

Separately from data gaps, the mapping exercise surfaces **data-quality issues** in fields that *do* exist but hold questionable values. Europa found a dozen of these, two of which were operationally significant:

- **LEI values in the CRD were missing the two-character country prefix check digits.** A valid LEI is 20 characters and the last two are check digits; Europa's CRD held 18-character values because an earlier migration had truncated them. The fix was a one-off database update to recompute the check digits from the authoritative GLEIF register, followed by a CRD constraint to prevent the error from recurring.
- **Currency codes in the PMS used internal three-letter codes that mostly matched ISO 4217 but differed for a few cases** (the internal code for the Norwegian krone was `NOK`, matching ISO, but for the Czech koruna it was `CZK` — close but with historical variants in the data). The fix was a lookup table mapping internal codes to ISO codes, implemented as part of the mapping transformation layer.

Both issues would have caused validation failures once the pipeline went live, and discovering them during mapping was exactly the point of doing the mapping phase thoroughly.

---

## 13.4 Phase 3: Prototyping and Piloting

### 13.4.1 Why a Prototype Comes Before a Production Build

Once the requirements are clear and the mapping is signed off, the temptation is to start building the production pipeline directly. Europa's project did *not* do this. Instead, the team spent two months building a **prototype** — a throwaway implementation of the pipeline that would produce real FundsXML files from real source data, but without any of the production-grade concerns (error handling, monitoring, operational hooks, audit logging). The purpose of the prototype was to discover the problems that only become visible when code meets data.

The prototype ran from 1 March to 30 April 2026 and consumed roughly three engineer-months. It used Python (rather than the Java target for production) because Python was faster for exploratory development; the team knew they would throw the prototype away once it had served its purpose. The prototype's output — FundsXML files for the Europa Growth Fund with real data from February and March 2026 — was the primary input to the testing phase that followed.

### 13.4.2 The Prototype Architecture

A prototype does not need to be architecturally pretty. Europa's prototype was a single Python script, roughly six hundred lines, that:

1. Connected to the PMS, CRD, and RRDM databases through direct SQL queries.
2. Read the EMT Excel workbook for the regulatory template data.
3. Applied the mapping transformations from §13.3.
4. Built a FundsXML document using `lxml`'s `ElementTree` API.
5. Validated the result against `FundsXML4.xsd` using `xmllint`.
6. Wrote the file to a local directory.

Six hundred lines is not a lot of code, and the prototype worked end-to-end within the first two weeks. The remaining six weeks were spent discovering the *problems* — the things the mapping table did not anticipate, the quirks of the source data, the ambiguous fields where the schema allowed several interpretations and the team had to pick one. Every problem was logged, every fix went into the mapping table or into a "design decisions" document, and every fix was re-tested before the next problem was attacked.

### 13.4.3 The Problems the Prototype Surfaced

Europa's prototype surfaced more than thirty distinct problems during its six weeks of iteration. Most were small; a few were structural enough to change the project plan. Four are worth describing concretely:

**Problem 1 — Currency mismatches between share classes.** The prototype produced EMT blocks for each share class, and the EMT `FinancialInstrument_Currency` field should match the share class's own currency. For the R-CHF-ACC-HEDGED class, the team had initially written `EUR` (the fund's base currency) because that was what the first version of the mapping table said. The prototype's validation caught it on the second day: the schema does not check the consistency, but the downstream consumer expected CHF for a CHF-denominated class. The fix was a mapping-table correction: `EMT_FinancialInstrument_Currency` should come from the share class, not from the fund. Fifteen minutes of work; six weeks' worth of potential confusion if it had been found in production.

**Problem 2 — FX rate sourcing for TNAV aggregation.** The fund-level `TotalNetAssetValue` is the sum of the per-share-class TNAVs after conversion to the fund base currency. The prototype initially used the PMS's own FX-rate table, but the administrator had a *different* FX-rate source (a vendor feed that was updated at the valuation point), and the two rates differed by basis points. The consumer-facing TNAV had to match the administrator's official figure; the pipeline had to switch to the administrator's FX source. The switch required adding a new data feed that the original mapping had not identified.

**Problem 3 — Portfolio position ordering.** The prototype emitted positions in the order they came out of the PMS database, which was roughly the order of trade dates. The validator passed, but the consumer's downstream comparison tool (which diff'd each month's delivery against the previous month's to flag significant changes) flagged thousands of "positions moved" diffs, because the order had shifted. The fix was to sort positions by ISIN before emission — a trivial change, but only visible once a real consumer's downstream tool had run against the output.

**Problem 4 — The CustomAttributes question.** Two pieces of producer-specific data — the sequential delivery number and the source-system version that generated the file — had no natural home in the FundsXML schema. The initial mapping had left them unmapped. The prototype team, after consulting Chapter 9, added them as [`CustomAttributes`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData/CustomAttributes) entries in ControlData with a namespace-like `eam.delivery.*` prefix. The decision was recorded in the design-decisions document as a permanent project convention.

### 13.4.4 The Pilot Delivery

Toward the end of the prototyping phase, on 28 April 2026, the team emitted their first **pilot delivery**: a complete FundsXML file for the Europa Growth Fund's 31 March 2026 valuation, containing [ControlData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData), Fund, [FundStaticData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData), [FundDynamicData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData), Portfolios, [RegulatoryReportings](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings) (EMT, EPT, EET, TPT), [AssetMasterData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData), and [Documents](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Documents). The file was 14 megabytes, passed schema validation, passed the Schematron rule set the team had written in parallel, and was sent through the SFTP channel to two cooperative pilot consumers: BNP Distribution Services in France and Comdirect Bank in Germany. Both consumers received the file, parsed it successfully, and reported back any issues they found.

The pilot revealed two further problems, both on the consumer side. BNP reported that their PRIIPs KID generator expected the `EPT_FinancialInstrument_UmbrellaName` field to be populated, but the Europa Growth Fund (modelled in the book and in the prototype as a standalone fund) had none. The fix was to set the umbrella name to a placeholder `"Europa Asset Management Investments"` — the umbrella name the fund *would* have if it were modelled correctly as a sub-fund — and to treat the real migration to an umbrella structure as a follow-on task. Comdirect reported a purely cosmetic issue: their ingestion was strict about the XML declaration's `encoding` attribute being `UTF-8` exactly, and the prototype had omitted the encoding attribute entirely. The fix took ten minutes.

Both consumer issues were absorbed before the prototype phase ended, and the delivery was re-sent on 29 April. The second pilot was accepted by both consumers without further issues. The prototype had done its job: the team now had a concrete, working example of every data flow, every transformation, every validation, and every consumer interaction. They were ready to start the production build.

---

## 13.5 Phase 4: Testing

### 13.5.1 What Testing Means for a FundsXML Project

With the prototype retired and the production code in development, the testing phase (1 May to 31 May 2026) focused on verifying that the production implementation matched the prototype's behaviour at scale and under all the edge cases the prototype had not seen. The testing phase had three layers.

**Layer 1 — Unit tests** of each transformation step. Each mapping rule from §13.3 became a unit test: given a known source row, the transformation must produce a known target value. Europa's unit-test suite grew to roughly 400 tests by the end of the month, each independently runnable, each taking milliseconds, each giving a clean pass/fail that told the developer immediately when a change had broken a rule.

**Layer 2 — Integration tests** that run the whole pipeline end-to-end against a fixture dataset. The fixture was a snapshot of the source databases from 31 March 2026 (the valuation date the prototype had used), with deliberate modifications to exercise edge cases: missing optional fields, a share class with no portfolio positions (a theoretical case that should not happen but might), a late-arriving CORRECTION that replaces an earlier delivery, a day with no subscriptions or redemptions, a day with a single very large subscription. The integration-test suite ran roughly a dozen scenarios, each producing a FundsXML file, each validated against XSD and Schematron, each compared against a golden-output fixture.

**Layer 3 — Acceptance tests with the pilot consumers.** Real FundsXML files produced from real source data, sent through real delivery channels, consumed by real consumer systems. BNP, Comdirect, and two further distributors were involved in this layer. The acceptance tests ran three deliveries: a normal month-end file, a correction of a deliberately wrong earlier file, and a delete of a file that should never have been sent. All three exercised the full producer-consumer handshake and exposed any remaining issues.

### 13.5.2 The Test Fixtures

A good fixture is the foundation of effective testing. Europa's fixtures came from three sources:

- **Real historical data.** Four months of source-database snapshots (December 2025 through March 2026) were archived in a dedicated fixture repository and used as input to the integration tests. Real data is the best test data because it exercises the quirks and edge cases the team cannot anticipate.
- **Synthetic edge cases.** For scenarios that real data did not cover — a SPLIT corporate action, a share class with zero shares outstanding, a day with a negative net flow — the team hand-crafted fixtures by taking a real snapshot and modifying specific fields. Synthetic fixtures are the right tool for exercising error paths and edge cases that rarely occur in production.
- **Generated samples.** For structural tests that needed complete schema coverage (every optional element populated at least once), the team used the FundsXML Generator from Chapter 11 to produce comprehensive fixtures. Generated fixtures are the right tool for structural completeness but the wrong tool for business-logic correctness, because the generated values are plausible but not semantically meaningful.

Europa's fixture repository held roughly seventy distinct fixtures by the end of the testing phase, organised into categories (normal, edge-case, error-case, regression). Each fixture had a short README describing its intent, so that a new engineer encountering the repository six months later could understand what each one was for.

### 13.5.3 The Bugs Found in Testing

Testing found twenty-two bugs that the prototype had missed, most of them small. Four are worth describing because they illustrate typical categories:

**Bug 1 — Integer overflow on a share count.** A test fixture with 2.1 billion shares outstanding (deliberately set higher than the PMS's normal maximum) overflowed a 32-bit signed integer in the transformation layer. The fix was to use a 64-bit type for the share-count field. The bug had been dormant in the prototype because no real data had ever approached the overflow threshold; the fixture was specifically designed to exercise it.

**Bug 2 — Missing `RelatedDocumentIDs` on a generated AMEND.** The pipeline produced an AMEND delivery in the correction-test scenario, but forgot to populate the `RelatedDocumentIDs` element pointing at the original delivery. The Schematron rule from Chapter 10 caught it on the next validation run. The fix was to add the back-pointer to the producer's generation logic; the test case was retained as a permanent regression fixture.

**Bug 3 — Locale-dependent number formatting.** The production pipeline, deployed on a Linux container configured for the German locale, emitted decimal numbers with commas as the decimal separator (`124,5078`) instead of the English ISO-standard period (`124.5078`). The bug manifested only in production configuration, not in the unit tests, which ran under the default English locale. The fix was to force the JVM locale to `en-GB` (the British English locale that uses period-as-decimal and is the closest to "ISO English" for number formatting purposes) at startup. This kind of locale dependency is a classic production-only bug.

**Bug 4 — File-not-found on a concurrent run.** A test scenario that triggered two pipeline invocations simultaneously revealed that both invocations were writing to the same temporary file, and one of them was corrupting the other's output. The fix was to add a per-invocation UUID to the temporary file names. The bug was uncovered by a chaos-test that deliberately triggered overlap; in production, the scheduler would normally prevent overlap, but the defensive fix removed the risk entirely.

### 13.5.4 Test-Driven Scope Control

An important operational discipline during testing: when a bug was found, the team first wrote a **failing test fixture** that reproduced the bug, then fixed the code, then verified that the test passed. The fixture was retained permanently in the regression suite. This discipline had two benefits: every bug became a permanent test case that would catch the same bug if it recurred, and the fixture repository grew organically to cover the real edge cases that mattered. By the end of testing, the fixture repository was the institutional knowledge of "things that have gone wrong with this pipeline", and it remained the most valuable testing asset through the project's go-live and into operations.

---

## 13.6 Phase 5: Acceptance and Go-Live

### 13.6.1 Formal Acceptance

User acceptance testing (UAT) ran from 1 June to 28 June 2026, with stakeholders from Operations, Fund Administration, Compliance, and the six pilot distributors participating. The UAT process was straightforward: the pipeline produced a set of deliveries, each stakeholder reviewed the output relevant to their role, and each stakeholder signed off that the output met their expectations. Failures during UAT went back to the development team for fixing and re-testing.

Three UAT sign-offs mattered most.

**Operations sign-off** confirmed that the pipeline could be operated by the existing Fund Operations IT team after go-live — that the runbook was clear, the monitoring dashboards were understandable, the alerting thresholds were appropriate, and the runbook actions for each likely failure mode were achievable by on-call staff without needing to escalate to the development team. Operations signed off on 18 June after two rounds of runbook revisions.

**Compliance sign-off** confirmed that the regulatory modules (EMT, EPT, EET, TPT) were populated correctly and that the audit trail was sufficient to defend the delivery chain in a regulatory inspection. Compliance signed off on 22 June.

**Distributor sign-off** was the most operationally important. Each of the six pilot distributors received two deliveries during UAT and confirmed that their own ingestion pipeline processed them correctly, that the resulting downstream fact sheets and regulatory documents were correct, and that they were ready to receive production deliveries. Five of the six signed off by 24 June; the sixth (one of the smaller distributors) requested a follow-up adjustment to the `DocumentURL` scheme in the Documents section and signed off on 27 June, one day before the UAT deadline.

### 13.6.2 Go-Live Strategy — Parallel Run

The go-live strategy was **parallel run**: for the month of July 2026, both the legacy CSV pipeline and the new FundsXML pipeline would emit deliveries for the same valuation dates. Each distributor would process whichever format their own systems preferred. Europa's operations team would compare the two outputs daily and investigate any discrepancies. This approach was slower and more expensive than a hard cutover, but it guaranteed that the legacy pipeline was still available as a safety net if the new pipeline failed.

The first parallel-run delivery was emitted on 1 July 2026 at 06:47 UTC for the 30 June 2026 valuation point — the first production FundsXML delivery in Europa Asset Management's history. Both pipelines produced their outputs, both passed their respective validations, and both reached all six distributors within the operational window. Five distributors confirmed successful ingestion of the FundsXML version by 09:00 UTC; the sixth confirmed by 11:30 after a brief issue with its SFTP configuration. Day 1 was a success.

### 13.6.3 The First Month in Production

The first month of parallel run surfaced three operational issues. None were severe enough to trigger a rollback, but each required a follow-up.

- **An SFTP timeout on day 3.** One of the distributors' SFTP drop-boxes experienced a brief outage, and the pipeline's retry logic was more conservative than the distributor's recovery time. The pipeline had already failed the delivery and alerted when the distributor recovered. Operations re-emitted the delivery manually. The fix was to extend the retry timeout; rolled out on day 6.
- **A locale issue on day 8.** The locale bug from §13.5.3 reappeared in a slightly different form — the German locale configuration had been set correctly on the production server, but one of the regulatory modules was using a separate formatting library that picked up the system locale independently. The fix was to force the locale on that library explicitly. Rolled out on day 9.
- **A performance issue on day 17.** The month-end delivery took 45 minutes to produce, when the pipeline's design target had been 20 minutes. Investigation found that a database query against the portfolio table was doing a full table scan instead of using an index that the test environment had had but the production database did not. The fix was to add the missing index. Rolled out on day 18.

By the end of July, all three issues were fixed, the parallel run had completed successfully for every daily and month-end delivery, and the decommissioning of the legacy CSV pipeline could be scheduled for 31 August 2026. Europa Asset Management had successfully transitioned to FundsXML as its authoritative fund-data format.

---

## 13.7 Phase 6: Operations and Maintenance

### 13.7.1 The Day After Go-Live

Go-live is the end of the project, but it is the beginning of the operation. The project team that built the pipeline typically disbands within a few weeks of successful go-live, and the system passes into the care of a permanent operations team that is — by definition — less familiar with the code than the builders were. The transition from "project" to "operations" is one of the riskiest moments in a FundsXML implementation, because institutional knowledge evaporates quickly if it is not captured deliberately.

Europa's transition plan had four elements.

**A runbook** documenting every production procedure: how to start and stop the pipeline, how to re-emit a failed delivery, how to investigate a validation failure, how to rotate credentials, how to roll back to the legacy pipeline in an emergency. The runbook was written during the testing phase (not after go-live, when the team would have less patience for it) and was the primary hand-off artefact to operations.

**A dashboard** showing the health of the pipeline at a glance: last successful delivery, last failed delivery, queue depth, average validation time, per-distributor ingestion-confirmation status. The dashboard was built in the company's existing Grafana instance (no new infrastructure) and was the first thing the on-call engineer looked at every morning.

**An alerting policy** defining which conditions trigger a page to on-call staff and which do not. Europa's policy: failed delivery within the emission window pages immediately; failed ingestion confirmation from a distributor pages within 30 minutes; delayed delivery (more than 30 minutes behind schedule) pages within the emission window but not outside it; validation warnings (non-blocking) are logged but do not page.

**A knowledge transfer plan** of sessions between the project team and the operations team, held during the last three weeks of the project. The sessions walked through the pipeline's architecture, the fixture repository, the runbook procedures, and the most likely failure modes. The goal was that by the time the project team disbanded, the operations team could handle every Tuesday-morning failure without calling the developers.

### 13.7.2 The First Six Months of Operations

By January 2027 — six months after go-live — Europa's FundsXML pipeline had emitted approximately 180 production deliveries (daily NAVs for the retail classes plus month-end deliveries plus ad-hoc regulatory deliveries) without a single emission that had caused downstream incident at a distributor. The operational metrics were:

- **Availability**: 99.8% of scheduled deliveries made it out within the emission window (against a 99.5% target).
- **Validation pass rate**: 100% of emitted deliveries passed both XSD and Schematron validation before emission (no bad delivery reached a distributor).
- **Incident count**: eleven operational incidents, all resolved within the on-call response SLA, none causing regulatory consequences.
- **Schema-upgrade handling**: one — FundsXML 4.2.9 was released by the FundsXML association in November 2026, and Europa's pipeline needed to be updated to match. The upgrade took two developer-weeks and was deployed without incident.

The operations team had absorbed the pipeline as an ordinary part of its workload. The project team had disbanded in late August 2026 with a handful of follow-on tasks (the multi-language text build-out, the umbrella-structure migration, the data-gap backfill) that were scheduled into the normal engineering backlog rather than treated as urgent.

### 13.7.3 Schema Upgrades — Continuous Maintenance

FundsXML releases minor updates two or three times a year, and each release can introduce new fields, deprecate old ones, or tighten validation rules. A producer that ignores these updates will eventually emit files that consumers reject because they are built against an older schema than the consumer expects. Staying current is therefore not optional — it is a continuous maintenance task.

Europa's schema-upgrade process, refined after the 4.2.9 upgrade, has five steps:

1. **Monitor** the FundsXML release channel (the GitHub releases page, the official mailing list). New releases are typically announced four to six weeks before they become mandatory for consumers that want to use the new features.
2. **Review** the changelog. Every minor release has a changelog enumerating the fields added, removed, or changed. Most fields are backwards-compatible additions that do not affect the producer's output; occasionally a release requires the producer to emit a new mandatory field.
3. **Update** the pipeline's schema reference (`FundsXML4.xsd`), update any mapping-table entries affected by the change, and run the test suite against the new schema.
4. **Pilot** the new version with one distributor before rolling out to all. A pilot reveals any consumer-side surprises that the test suite does not catch.
5. **Roll out** to all distributors, coordinated with the consumer side where possible.

The full cycle takes two to four developer-weeks of work per release, depending on the scope of the changes. A mature producer typically has this workflow documented and practised enough that it becomes an ordinary part of the engineering cadence rather than a disruptive event.

### 13.7.4 Producer-Consumer Relationship as an Ongoing Conversation

One operational lesson from Europa's first six months deserves to be stated explicitly: **the producer-consumer relationship is not a one-time contract signed at go-live; it is an ongoing conversation.**

Distributors occasionally request changes to the data they receive — a new field they need for a new regulatory disclosure, a different format for a cost figure, an additional language in the description text. Regulators occasionally update the rules that drive the templates — EMT, EPT, EET, TPT all evolve on their own release cadences. Internal data sources change, not always in ways that are visible from the pipeline's perspective. The producer's operations team has to monitor the conversation, route requests to the right responders, and occasionally push back when a requested change would be disruptive.

Europa's approach, again refined after six months, is to hold a **quarterly review meeting** with each distributor relationship, in which both sides share feedback on the recent deliveries and flag any upcoming needs. The meetings are short (30 minutes per distributor), informal, and structured around three questions: "Is everything working?" / "Is anything about to change on your side?" / "Is anything about to change on our side?" The meetings replace the need for ad-hoc firefighting when a change surprises one side; they catch the surprises early and let both sides plan together.

---

## 13.8 The Europa Growth Fund Timeline — A Case-Study Recap

The project described in this chapter ran from December 2025 to August 2026 — nine months from kickoff to go-live, followed by ongoing operations. The timeline, in summary:

**Table 13.2 — The Europa Asset Management FundsXML project timeline**

| Phase | Dates | Duration | Key deliverables |
|---|---|---|---|
| **Phase 0** — Trigger and kickoff | Oct–Dec 2025 | 2 months | Audit finding, distributor notice, project charter |
| **Phase 1** — Requirements analysis | 8 Dec 2025 – 31 Jan 2026 | 2 months | Requirements document, stakeholder sign-off |
| **Phase 2** — Data mapping | 1 Feb – 28 Feb 2026 | 1 month | Mapping table, data-gap list, quality-issue list |
| **Phase 3** — Prototyping and piloting | 1 Mar – 30 Apr 2026 | 2 months | Working prototype, two pilot deliveries accepted |
| **Phase 4** — Testing | 1 May – 31 May 2026 | 1 month | Unit/integration/acceptance test suites, regression fixtures |
| **Phase 5** — UAT and go-live preparation | 1 Jun – 30 Jun 2026 | 1 month | Stakeholder sign-offs, runbook, dashboards, alerting |
| **Phase 6a** — Parallel run | 1 Jul – 31 Jul 2026 | 1 month | First production deliveries, legacy comparison |
| **Phase 6b** — Legacy decommission | 31 Aug 2026 | — | Legacy CSV pipeline retired |
| **Phase 6c** — Steady-state operations | Sep 2026 onwards | Indefinite | Ongoing deliveries, schema upgrades, relationship reviews |

Several observations about the timeline are worth making.

**Requirements and mapping together consumed three months** — one-third of the project duration. Newcomers to FundsXML implementation projects typically underestimate these phases and overestimate the build phases; the Europa project's distribution of effort is more realistic than the typical newcomer plan.

**Prototyping consumed two months** — twice the one month the initial plan had allocated. The team had pre-negotiated an additional slack week per phase, and the prototyping phase consumed all of it plus a week of the testing phase. This is typical: the first phase where code meets data is almost always longer than planned.

**Testing consumed the allocated month exactly.** The unit, integration, and acceptance tests all fit into their slots, largely because the prototype had already surfaced the most time-consuming problems.

**UAT consumed the allocated month exactly as well**, with one late sign-off from the smallest distributor. The parallel run and the go-live went smoothly, though not without three operational issues in the first month that the team had to address quickly.

**The post-go-live schema upgrade happened on schedule** (FundsXML 4.2.9 in November 2026) and cost two developer-weeks — a small but recurring maintenance cost that was comfortably absorbed by the operations team's normal workload.

Nine months from kickoff to production is a realistic timeframe for a first-time FundsXML implementation at a mid-sized asset manager with a clean scope, a cooperative set of distributors, and a pragmatic team. Larger organisations with more internal stakeholders, or messier source data, or more complex distribution relationships, typically take twelve to eighteen months for the same scope. The Europa project was successful partly because the scope was kept tight, the team was cross-functional from day one, and the stakeholders stayed engaged through the full timeline.

---

## 13.9 Common Pitfalls

- **Underestimating the mapping phase.** Every newcomer project thinks mapping will take a week; every mature project knows it takes a month. The mapping is where the source data's quirks become visible, and those quirks are the hardest problem the project will face. Plan for a full phase on mapping, not a week.
- **Skipping the prototype.** Building the production pipeline directly, without a throwaway prototype, causes the production code to absorb every early mistake as permanent technical debt. The prototype is cheap; the production code bears the cost of its mistakes for years.
- **Ignoring the pilot consumer.** A pilot delivery to a real consumer surfaces problems that no amount of internal testing can find, because only a real consumer's downstream tools exercise the full integration. Every project should have at least one cooperative pilot consumer engaged from the prototyping phase onwards.
- **Treating go-live as the end.** Projects that celebrate go-live and then disband the team leave the operations team without institutional knowledge and the pipeline without a mechanism for ongoing maintenance. The transition from project to operations is a deliberate phase, not an afterthought.
- **Cutting over hard instead of running in parallel.** A hard cutover gives the project a romantic "all-in, no turning back" feeling, but it leaves no safety net when something goes wrong. A parallel run for at least one month is the professional standard, and the cost (running both pipelines for a few weeks) is much lower than the cost of a rollback from a failed hard cutover.
- **Ignoring schema upgrades.** FundsXML releases minor updates several times a year, and each one needs to be absorbed by the pipeline. A producer that lets the schema drift will eventually emit files that consumers reject; the maintenance cost is permanent but small if treated as part of the engineering cadence.
- **Letting the producer-consumer relationship go stale.** The relationship is an ongoing conversation, not a one-time contract. Regular check-ins (quarterly, even informally) prevent ad-hoc firefighting when one side's needs change.
- **Building the pipeline without involving Compliance.** Compliance sign-off is not optional, and late Compliance engagement typically surfaces regulatory gaps that force painful rework. Engage Compliance from the requirements phase onwards, and keep them involved through every gate.

---

## 13.10 Key Takeaways

- A FundsXML implementation project at a mid-sized asset manager typically runs **nine to twelve months** from kickoff to first production delivery, through six distinct phases: requirements, mapping, prototyping, testing, acceptance and go-live, and operations.
- **Phase 1 (requirements)** produces a tight scope document naming the funds, share classes, regulatory modules, delivery channels, and — explicitly — the things the project will *not* do. The out-of-scope list is as important as the in-scope list.
- **Phase 2 (mapping)** is the hardest phase. It produces a mapping table with one row per FundsXML field, naming the source system, source column, transformation, and default for each. The mapping exercise surfaces data gaps and data-quality issues that the project must address before production.
- **Phase 3 (prototyping)** builds a throwaway implementation in a fast language (Python, typically) to discover the problems that only become visible when code meets data. A pilot delivery to a cooperative real consumer at the end of the prototype phase surfaces further integration problems that internal testing alone cannot find.
- **Phase 4 (testing)** has three layers — unit tests per mapping rule, integration tests end-to-end against fixtures, acceptance tests with real consumers. Every bug found becomes a permanent regression fixture, and the fixture repository is the institutional knowledge of the pipeline's edge cases.
- **Phase 5 (UAT and go-live)** collects formal sign-offs from Operations, Compliance, and each pilot distributor, then runs the new pipeline in parallel with the legacy pipeline for at least a month before the legacy is decommissioned. Parallel run is the professional standard; hard cutover is a gamble.
- **Phase 6 (operations)** begins at go-live and continues indefinitely. It requires a runbook, a dashboard, an alerting policy, and deliberate knowledge transfer from the project team to the operations team. Schema upgrades are a recurring maintenance task (two to four developer-weeks per FundsXML minor release), and the producer-consumer relationship is an ongoing conversation that deserves regular check-ins.
- The Europa Asset Management project that forms this chapter's narrative ran from December 2025 to August 2026 and is a realistic template for a first-time implementation at a mid-sized asset manager. It succeeded because the scope stayed tight, the team was cross-functional, and the stakeholders stayed engaged through the full timeline.

Three chapters remain. Chapter 14 closes Part IV of the book with a forward-looking view: where FundsXML is heading, how the API-driven shift will affect the next decade of fund-data exchange, the role of AI and automation in producer and consumer pipelines, and how the reader can contribute to the standard's continued evolution.
