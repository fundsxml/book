<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Management Summary

*A two-minute orientation for fund professionals*

---

The European fund industry moves more money than any other financial sector in the region, yet it spends an outsized share of its operating budget simply **moving information about that money from one system to another**. Every asset manager, every administrator, every depositary, every distributor, every regulator consumes overlapping views of the same underlying facts — net asset values, holdings, costs, risks, sustainability disclosures — and for most of the industry's history, almost every pair of counterparties has invented its own way of exchanging them.

This book is about the European answer to that problem: **FundsXML**.

## Why a standard is needed

A mid-sized UCITS distributed across ten European countries will today feed dozens of downstream systems — fund accounting, portfolio management, depositary oversight, data vendors, regulatory portals, distributor databases, ESG analytics — each expecting fund data in its own preferred format. The information is essentially identical; the packaging is not. One counterparty wants a bespoke CSV with forty columns; another insists on an Excel workbook; a third accepts only SWIFT messages; a fourth has built a proprietary XML dialect. The operations team is therefore obliged to maintain tens of bilateral interfaces to ship the same data in different shapes, and every small change at the source — a new ISIN, a reclassified cost component, a renamed benchmark — triggers work across every one of them.

Add to this the rising tide of regulatory templates — PRIIPs KIDs, EMT, EPT, EET, EFT, TPT, AIFMD Annex IV, MMF, and ESAP submissions — and the data-exchange problem becomes not a technical inconvenience but a **material component of the industry's cost base**. Standardisation, once a voluntary ambition, has become a commercial and regulatory necessity.

## What FundsXML is

FundsXML is an **open, XML-based data standard for the exchange of fund-related information across the European asset-management industry**. Governed by a non-profit initiative and continuously developed since 2001, its current version — 4.2.x — covers the full spectrum of fund data that practitioners exchange every day:

- **ControlData** — who sent what, when, and with which operational intent;
- **Fund structure** — funds, sub-funds, and share classes, with their identifiers, descriptions, classifications, and fee structures;
- **Portfolio** — positions across all asset classes, linked to centralised asset master data;
- **Transactions and orders** — subscriptions, redemptions, switches, distributions, and corporate actions;
- **Regulatory modules** — the FinDatEx templates (EMT, EPT, EET, EFT, TPT) embedded natively in the schema;
- **Documents, signatures, and proprietary extensions** — factsheets, XMLDSig signatures, and CustomDataFields.

The standard is defined by a single XML Schema Definition (XSD), validated by open tools, and supported by a growing ecosystem of converters, libraries, and worked examples. FundsXML does not attempt to replace ISO 20022, SWIFT, FIX, or openfunds; it sits alongside them, focused on the *fund-data payload* that those transport standards were never designed to model in detail.

## Who benefits

FundsXML is used in production by **asset managers, fund administrators, depositaries, distributors, data vendors, and regulators** across the European market, with particularly strong adoption in the German-speaking countries and in the Luxembourg and Irish cross-border fund centres. A mid-sized administrator that adopts FundsXML typically collapses several bilateral feeds into a single canonical delivery; an asset manager that accepts FundsXML as an input format reduces its onboarding time for new distributors from weeks to days; a regulator that consumes FundsXML receives the same data that the industry already produces internally, rather than requiring a parallel reporting chain.

The economic case is straightforward: **one format, one validation, one change process, many consumers.**

## What this book delivers

The book is organised in four parts. **Part I — Foundations** sets out the data problem, the underlying XML and XSD technology, and the history and architecture of FundsXML. **Part II — FundsXML in Detail** examines each area of the schema — ControlData, Funds, Portfolio, Transactions, Regulatory Modules, and Advanced Areas — with complete, schema-valid worked examples. **Part III — Implementation and Practice** covers validation, tooling, system integration, and the end-to-end delivery of a FundsXML project. **Part IV — Outlook and Reference** looks ahead to FundsXML in an API-driven, AI-assisted world.

A fictional Luxembourg-domiciled UCITS — the **Europa Growth Fund** — runs through every chapter as a continuous narrative thread, so that abstract schema constructs are always illustrated against a concrete, realistic case.

Readers with operational or managerial responsibilities may read Parts I and III and dip into Part II as required. Readers implementing FundsXML — whether on the generating or the consuming side — will find Parts II and III the working core of the book. Readers new to XML itself should begin with Chapter 2 before moving on.
