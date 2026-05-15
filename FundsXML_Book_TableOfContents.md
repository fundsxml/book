# FundsXML – The European Standard for Fund Data Exchange

*A Practical Handbook for Fund Professionals*

Based on FundsXML Schema Version 4.2.x — **2026**

---

## Table of Contents with Chapter Summaries and Page Counts

**Total length (including preface, appendices and index): approx. 523 pages**

---

### Preface
Introduction to the book, target audience, structure, and the fictional "Europa Growth Fund" that serves as the common thread throughout all chapters. Motivation and value of the work for fund professionals.
**Pages 1–4**

### Management Summary
A two-minute executive overview of FundsXML: what problem it solves, what the standard covers, who benefits, and how this book is organised for different audiences.
**Pages 5–6**

---

## PART I — FOUNDATIONS

### Chapter 1 — Challenges in Fund Data Exchange
*Why the industry needs a standard*

Analysis of the European fund industry's data landscape: master data, price data, portfolio data, and transaction data; data volumes and frequencies; typical data flows between asset managers, custodians, distributors, data vendors, and regulators. Presentation of typical problems without standardisation, regulatory pressure as a driver, and an overview of existing standards (FIX, SWIFT, ISO 20022, openfunds) to position FundsXML in the landscape.
**Pages 7–31**

### Chapter 2 — XML and XSD — The Technological Basis
*Foundational knowledge for working with FundsXML*

Concise introduction to XML and XSD (XML Schema Definition) as the technological foundation. Covers syntax, elements, attributes, namespaces, data types, structuring options, XML validation in practice, XSLT transformations, and an overview of key tools for day-to-day XML work.
**Pages 32–61**

### Chapter 3 — FundsXML — The Standard at a Glance
*History, organisation, and architecture*

History of FundsXML since 2001, the organisation and community around the FundsXML initiative, design principles of the standard, and the underlying schema architecture with its main areas (ControlData, Funds, AssetMasterData, Documents, RegulatoryReportings).
**Pages 62–81**

---

## PART II — FUNDSXML IN DETAIL

### Chapter 4 — ControlData — The Metadata of a Delivery
*Document ID, reporting date, sender, and operation type*

Detailed description of the ControlData section: mandatory fields, data sender and receiver, DataOperation types (INITIAL, UPDATE, DELETE), versioning, and a complete, schema-valid ControlData block as a practical example.
**Pages 82–103**

### Chapter 5 — Funds, Sub-Funds, and Share Classes
*Static and dynamic fund information*

Comprehensive treatment of the Fund structure: identifiers (ISIN, WKN, LEI, Valor), multilingual names and descriptions, fund classification, share class modelling, and dynamic fund data (FundDynamicData), including a full practical example for the "Europa Growth Fund".
**Pages 104–143**

### Chapter 6 — Portfolio and Positions
*Holdings and asset classes*

Structure of the Portfolio section, coverage of all asset classes (Equity, Bond, Fund, Derivative, Cash, Real Estate, etc.), common data fields per position, linkage to AssetMasterData via UniqueIDs, and portfolio breakdowns. A mixed portfolio serves as an end-to-end practical example.
**Pages 144–188**

### Chapter 7 — Transactions and Orders
*Orders, settlements, and corporate actions*

Transaction types in FundsXML: subscriptions, redemptions, switches, distributions and income, and Order Execution Types. The chapter is rounded off by a complete practical example of a transaction file.
**Pages 189–218**

### Chapter 8 — Regulatory Modules
*EMT, EPT, EET, EFT, and TPT in FundsXML*

Embedding of the FinDatEx templates in FundsXML: European MiFID Template (EMT), European PRIIPs Template (EPT), European ESG Template (EET), European Feedback Template (EFT), and Tripartite Template (TPT) for Solvency II. Complemented by the European Single Access Point (ESAP) and a comprehensive practical example of a full regulatory delivery.
**Pages 219–268**

### Chapter 9 — Advanced Schema Areas
*Factsheets, digital signatures, and CustomDataFields*

Coverage of less frequently used but important schema areas: factsheet data and the Documents section, digital signatures based on XMLDSig, CustomDataFields for proprietary extensions, and country-specific additions.
**Pages 269–293**

---

## PART III — IMPLEMENTATION AND PRACTICE

### Chapter 10 — Validation and Quality Assurance
*Ensuring correct FundsXML files*

The two-stage validation model (schema validation plus business validation), the most common validation errors and their resolution, automated quality checks (Schematron, business rules), and a complete validation workflow as a practical example.
**Pages 294–318**

### Chapter 11 — Tools and Toolchain
*The right tools for productive use*

Presentation of the most important tools: FreeXmlToolkit in detail, Online Schema Viewer, FundsXML CSV Converter, FundsXML Generator, and integration into development environments (IDEs such as IntelliJ, VS Code, Eclipse).
**Pages 319–346**

### Chapter 12 — FundsXML in the System Landscape
*Integration into existing IT architectures*

Typical architecture scenarios, comparison of programming languages for generating FundsXML (Java, Python, C#, JavaScript), strategies for reading and processing, database integration and data warehousing, and automation and scheduling of productive FundsXML processes.
**Pages 347–378**

### Chapter 13 — An Implementation Project from A to Z
*A practical guide for introducing FundsXML*

End-to-end walkthrough of a FundsXML implementation project: project preparation and requirements analysis, mapping of existing data to FundsXML, prototyping and piloting, testing, acceptance and go-live, and operations and maintenance.
**Pages 379–408**

---

## PART IV — OUTLOOK AND REFERENCE

### Chapter 14 — Future and Further Development
*Where is FundsXML heading?*

Current development directions of the standard, the role of FundsXML in an API-driven world, the influence of AI and automation, and ways in which readers themselves can contribute to its further development.
**Pages 409–426**

---

## APPENDICES

### Appendix A — Glossary
Technical terms in German/English with definitions and cross-references.
**Pages 427–438**

### Appendix B — XML Quick Reference
A compact cheat sheet for XML syntax, XPath, and XSLT.
**Pages 439–446**

### Appendix C — FundsXML Schema Overview
Structured overview of all important elements, types, and enumerations.
**Pages 447–461**

### Appendix D — Complete Example Files
Complete, schema-valid FundsXML sample files for the "Europa Growth Fund".
**Pages 462–481**

### Appendix E — Resources and Links
Official sources, GitHub repository, community, and training offerings.
**Pages 482–485**

### Appendix F — Solutions to the Exercises
Model solutions for all chapter-level exercises.
**Pages 486–505**

### Index
**Pages 506–515**
