# Appendix A — Glossary

*Technical terms in German and English*

---

This glossary is a reference, not a second introductory chapter. Each entry gives a short definition — usually one to three sentences — together with cross-references to other glossary entries (marked with →) and, where appropriate, to the chapter in the main text where the term is treated in depth.

**Conventions.** Entries are sorted alphabetically by their English term, which is shown in **bold**. The German equivalent, where one exists in common use, follows in italic parentheses immediately after the English lemma: **Fund** *(Fonds)*. Where the English term is itself a loan-word used unchanged in German, the italic is omitted. Cross-references use the arrow symbol →, which points at another entry in this glossary or, less frequently, at a numbered chapter or section of the book. The acronyms list in §A.2 collects every abbreviation used in the book in one place for quick lookup.

A final note on the language choice. The main text of this book is written in British English, but the FundsXML community is historically rooted in German-speaking Central Europe, and many of the working documents that practitioners encounter — depositary agreements, fund prospectuses, BaFin circulars, Austrian FMA guidance — are in German. The bilingual glossary is meant to bridge the two vocabularies so that a practitioner can move between an English specification and a German working document without losing the thread.

---

## A.1 Alphabetical Entries

### A

**Accounting NAV** *(Buchhalterischer NAV)* — The net asset value calculated by the fund's accounting system before any adjustments for swing pricing, rounding conventions, or other publication-time modifications. Contrast with the *published NAV*, which is what reaches investors. → NAV, → Swing Pricing.

**Accumulating Share Class** *(Thesaurierende Anteilklasse)* — A share class in which income (dividends, interest, realised gains) is reinvested into the fund rather than distributed to the investor. The investor's return is reflected in an increasing NAV per share rather than in periodic cash payments. Contrast with → Distributing Share Class.

**Administrator** — See → Fund Administrator.

**AIF** — Alternative Investment Fund. Any collective investment undertaking in the EU that does not qualify as a UCITS fund — typically hedge funds, private equity funds, real estate funds, infrastructure funds, and most institutional-only funds. Regulated under → AIFMD.

**AIFMD** — Alternative Investment Fund Managers Directive. The EU directive (2011/61/EU) governing the management and marketing of → AIF funds in the European Union. Its successor, AIFMD II, was adopted in 2024. → Chapter 1 for context.

**Asset Manager** *(Kapitalverwaltungsgesellschaft, KVG)* — The firm that manages a fund's investment portfolio according to its prospectus and investment guidelines. In the FundsXML data model, the asset manager is typically the → Data Supplier for fund-level data. → Chapter 1.

**[Asset Master Data](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData)** — The static reference data about investable instruments (equities, bonds, derivatives) that a portfolio may contain: ISIN, name, issuer, country of risk, classification codes. In FundsXML, this data lives in the `AssetMasterData` block rather than being duplicated inside each position. → Chapter 6.

**Audit Log** *(Audit-Protokoll)* — A chronological, tamper-evident record of every delivery emitted or received by a FundsXML pipeline, together with its status, validation result, and any operator actions. Required for most regulatory frameworks and practically necessary for operational troubleshooting. → Chapter 13.

### B

**Base Currency** *(Basiswährung)* — The currency in which a fund's accounts are kept and in which its primary NAV is expressed. Individual share classes may be denominated in other currencies, in which case the fund-level TNAV is a base-currency figure and the share-class TNAVs are in their own currencies. → Share Class, → TNAV.

**Batch Delivery** *(Stapellieferung)* — A mode of data exchange in which producers emit complete data sets at scheduled intervals (daily, monthly, quarterly) rather than streaming individual events. The dominant pattern in fund data exchange and the pattern for which the FundsXML schema was designed. Contrast with → Event-Driven Architecture.

**Business Rule** *(Geschäftsregel)* — A correctness requirement that goes beyond structural validation and expresses domain-specific logic (e.g., "a DELETE operation must reference the document being retracted"). Business rules are typically enforced with → Schematron rather than with XSD. → Chapter 10.

### C

**Cash Equivalent** *(Zahlungsmitteläquivalent)* — Short-term, highly liquid instruments (money-market funds, overnight deposits, T-bills with less than three months to maturity) that are treated as cash in portfolio reporting. Carried in FundsXML as a position with a `PositionType` indicating the cash-equivalent classification.

**Consumer** *(Datenempfänger)* — A system or organisation that receives FundsXML files and uses them for downstream processing: a distributor generating KIDs, a data warehouse loading historical positions, a regulator ingesting disclosures for oversight. Contrast with → Producer. → Chapter 1.

**[ControlData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData)** — The envelope block at the top of every FundsXML document that identifies the delivery: unique document ID, content date, data supplier, data operation, language, version. The dispatcher's first anchor when routing an incoming delivery. → Chapter 4.

**Corporate Action** *(Kapitalmaßnahme)* — An event that changes the terms of a security held in a portfolio: a stock split, a dividend, a merger, a spin-off, a name change. Corporate actions are recorded in FundsXML as transaction-like events that adjust positions between valuation dates. → Chapter 7.

**Cross-Border Distribution** *(Grenzüberschreitender Vertrieb)* — The authorised offering of a fund's shares to investors in an EU member state other than the fund's country of domicile. Governed by the UCITS or AIFMD passporting regime. Each distribution country may impose its own information requirements, which FundsXML carries in `CountrySpecificData`. → Chapter 9.

**Custodian** *(Depotbank, Verwahrstelle)* — The bank that holds a fund's assets in safe-keeping and verifies ownership on behalf of investors. Under UCITS and AIFMD, funds must appoint a single depositary that is legally responsible for asset safe-keeping, cash monitoring, and oversight of the fund manager. Often used interchangeably with *depositary* in English, though strictly speaking the depositary has broader duties. → Chapter 1.

**[CustomAttributes](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData/CustomAttributes)** — The FundsXML extension mechanism for carrying producer- or project-specific data that the standard schema does not model natively. Each custom attribute has a name, a type indicator (T/N/D/B for text/number/date/boolean), and a typed value. To be used sparingly; the first question should always be whether a standard element already exists. → Chapter 9.

**Cutoff Time** *(Order-Annahmeschluss)* — The deadline each day by which investor orders (subscriptions or redemptions) must be received to be executed at that day's NAV. Orders after cutoff are held for the next NAV calculation. Relevant to FundsXML because it affects which transactions appear in which delivery's valuation period.

**Cutover** — The transition moment at which a new pipeline takes over from a legacy one. Contrast with → Parallel Run, which keeps both pipelines running for a period. → Chapter 13.

### D

**Data Gap** *(Datenlücke)* — A FundsXML element that a delivery needs to populate but for which no existing source system holds the value. Data gaps are typically surfaced during the mapping phase of an implementation project and must be resolved before production. → Chapter 13.

**[Data Operation](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataOperation)** — One of three enumerated values — `INITIAL`, `AMEND`, `DELETE` — in `ControlData/DataOperation` that tells the consumer what the delivery is meant to do: establish a new record, update an existing record, or retract one. Confusing `AMEND` with a silent overwrite is a classic pipeline bug. → Chapter 4.

**Data Quality** *(Datenqualität)* — The property that data is accurate, complete, consistent, and timely. Data-quality issues, unlike data gaps, involve fields that do exist but hold incorrect or inconsistent values — for example, LEIs that are missing check digits or currency codes that do not match ISO 4217. → Chapter 13.

**[Data Supplier](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataSupplier)** *(Datenlieferant)* — The organisation that generated a particular FundsXML delivery, identified in `ControlData/DataSupplier` by system country, short code, legal name, and type. Not necessarily the asset manager — it might be a fund administrator or a reporting agent acting on the manager's behalf. → Chapter 4.

**Depositary** — See → Custodian.

**Dispatcher** *(Verteiler)* — A consumer-side component that receives incoming FundsXML files and routes them to the correct downstream systems based on their content — distributor KID generator, trading desk, warehouse loader, and so on. → Chapter 12.

**Distributing Share Class** *(Ausschüttende Anteilklasse)* — A share class that pays out its income to investors periodically (usually annually or semi-annually) rather than reinvesting it. Contrast with → Accumulating Share Class.

**Distribution Country** *(Vertriebsland)* — A country in which a fund's shares are authorised for offering to investors. Each distribution country may impose local information requirements beyond those of the fund's domicile. → Chapter 9.

**[DocumentGenerated](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData)** — The timestamp, in `ControlData/DocumentGenerated`, at which the FundsXML file was created by the producer. Contrast with → ContentDate, which is the valuation date the delivery describes.

**Domicile** *(Sitzstaat)* — The country in which a fund is legally established and whose regulator primarily supervises it. Luxembourg, Ireland, France, Germany, and Austria account for most UCITS domiciles in the EU.

### E

**EET** — European ESG Template. The FinDatEx template that carries the SFDR-mandated sustainability disclosures for a fund: PAI indicators, Taxonomy alignment, sustainable investment share, exclusions policy, and related fields. → Chapter 8.

**EFT** — European Feeder Fund Template. The FinDatEx template for communicating feeder-fund-specific information between a feeder fund and its master. → Chapter 8.

**EMT** — European MiFID Template. The FinDatEx template that carries the MiFID II target market, cost, and risk-classification information that distributors need for investor-suitability assessments and for PRIIPs KIDs. The most widely used of the FinDatEx templates. → Chapter 8.

**Emission Window** *(Lieferfenster)* — The operational time-slot within which a pipeline is expected to emit its daily or monthly delivery. Failures within the emission window typically trigger an on-call page; failures outside the window can wait for business hours. → Chapter 13.

**EPT** — European PRIIPs Template. The FinDatEx template that carries the inputs a distributor needs to generate a PRIIPs Key Information Document (KID). → Chapter 8.

**ESAP** — European Single Access Point. A centralised EU platform, established by Regulation 2023/2859 and scheduled to become operational in 2027, that aggregates regulatory disclosures from all EU-listed entities and makes them publicly searchable. Funds are within its scope. → Chapter 14.

**ESG** — Environmental, Social, and Governance. The umbrella term for non-financial investment criteria covering sustainability, social impact, and corporate governance. Reflected in FundsXML primarily through the EET module and the SFDR disclosures. → Chapter 8, → Chapter 14.

**ESMA** — European Securities and Markets Authority. The EU authority that issues technical standards and guidance for securities markets, including the regulatory technical standards (RTS) underlying SFDR, MiFID II, PRIIPs, and UCITS. → Chapter 1.

**Event-Driven Architecture** — A system design in which state changes are published as real-time events on a message bus (Kafka, Kinesis, RabbitMQ) rather than aggregated into batch files. FundsXML is designed for batch delivery and does not currently have a first-class event mode. → Chapter 14.

**Exchange-Traded Fund (ETF)** *(Börsengehandelter Fonds)* — A fund whose shares are listed on a stock exchange and traded intraday like equities, in contrast to traditional mutual funds that are bought and sold at a single end-of-day NAV. Most European ETFs are structured as UCITS funds.

### F

**Fair Value** *(Beizulegender Zeitwert)* — The value at which an asset could be exchanged between knowledgeable, willing parties in an arm's-length transaction. For actively traded instruments, fair value is the market price; for illiquid instruments, it is estimated using valuation models. The basis on which NAV is calculated. → NAV.

**Feeder Fund** *(Feeder-Fonds)* — A fund that invests substantially all of its assets in a single other fund (the → Master Fund), typically to give investors in one jurisdiction access to a master fund domiciled elsewhere. Reflected in FundsXML via the EFT module for feeder-specific information.

**FIGI** — Financial Instrument Global Identifier. A 12-character alphanumeric identifier for financial instruments, issued by Bloomberg and standardised as an open identifier. Less common in European fund data than ISIN but growing in use. → ISIN.

**FinDatEx** — European Working Group on Investment Data Exchange. The industry body that publishes the five European data templates (EMT, EPT, EET, EFT, TPT) embedded in the FundsXML `RegulatoryReportings` block. Coordinates its release cycle with the FundsXML association. → Chapter 8, → Chapter 14.

**Fixture** *(Testfixture)* — A pre-prepared test input (a FundsXML file, a database snapshot, a configuration) used to exercise a specific test case reproducibly. The fixture repository of a mature pipeline is the institutional memory of "things that have gone wrong". → Chapter 13.

**FreeXmlToolkit** — An open-source desktop application by Karl Kauc for working with XML, XSD, XSLT, Schematron, and FundsXML files. Covered in detail in → Chapter 11.

**[Fund](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund)** *(Fonds)* — A collective investment undertaking that pools capital from investors and invests it according to a stated strategy. In FundsXML, represented by the `Fund` element with its static and dynamic sub-blocks. → Chapter 5.

**Fund Administrator** *(Fondsbuchhalter, Verwaltungsstelle)* — The firm that provides back-office services to a fund: NAV calculation, fund accounting, investor register maintenance, regulatory reporting. In practice, the fund administrator is often the producer of FundsXML deliveries on behalf of the asset manager. → Chapter 1.

**[FundDynamicData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData)** — The FundsXML block inside each `Fund` element that carries values changing at each valuation: TNAV, share counts, prices, flows, and earnings. Contrast with → FundStaticData. → Chapter 5.

**[FundStaticData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData)** — The FundsXML block inside each `Fund` element that carries values which change rarely: fund name, domicile, launch date, investment manager, custodian, prospectus references. → Chapter 5.

**FundsXML** — The XML-based open standard for fund data exchange maintained by the FundsXML association. The subject of this book.

**FundsXML Association** *(FundsXML-Verein)* — The non-profit body, registered in Austria, that stewards the FundsXML standard: governance, working groups, release coordination, consultation process, documentation. → Chapter 14.

### G

**Generator** — (1) A producer-side component that assembles source data into a FundsXML document. (2) The FreeXmlToolkit feature that creates synthetic FundsXML documents from a schema, useful for testing. → Chapter 11.

**GLEIF** — Global Legal Entity Identifier Foundation. The non-profit body that oversees the global LEI system, including the issuance and verification of LEIs. → LEI.

**Golden Fixture** — A reference FundsXML file whose content is considered correct and against which newer pipeline outputs are compared byte-for-byte or field-by-field in regression testing. → Chapter 13.

### H

**Hedged Share Class** *(Währungsgesicherte Anteilklasse)* — A share class whose currency exposure is hedged back to the investor's reference currency, so that the investor experiences the fund's underlying returns without the additional currency-translation risk. → Share Class.

### I

**Identifier** *(Kennung)* — A code that uniquely identifies a fund, share class, instrument, or legal entity. FundsXML uses LEI for legal entities, ISIN for share classes and instruments, and a small number of additional identifier types (CUSIP, SEDOL, WKN, FIGI, CFI) as alternatives or supplements.

**Idempotency** *(Idempotenz)* — The property that applying the same operation multiple times produces the same result as applying it once. A consumer pipeline that handles idempotency correctly will not duplicate rows when a delivery is re-sent. → Chapter 12.

**INITIAL** — One of three values of → Data Operation, indicating that the delivery introduces new data rather than modifying or retracting an earlier delivery. The default for a normal periodic delivery.

**Integration Test** *(Integrationstest)* — A test that exercises multiple components of a pipeline together, typically end-to-end from source database to validated output file. Contrast with a → Unit Test, which exercises a single component in isolation. → Chapter 13.

**ISIN** — International Securities Identification Number. A 12-character alphanumeric code (ISO 6166) that uniquely identifies a security globally. FundsXML uses ISINs for share classes and portfolio instruments. → Chapter 5.

### K

**KID** — Key Information Document. The standardised three-page investor information document required under the PRIIPs regulation for retail investment products, including UCITS funds. KID content is generated from → EPT template data. → Chapter 8.

**Knowledge Transfer** *(Wissenstransfer)* — The deliberate process of moving institutional knowledge from a project team to the permanent operations team before the project team disbands. A critical but often neglected phase of an implementation project. → Chapter 13.

### L

**LEI** — Legal Entity Identifier. A 20-character alphanumeric code (ISO 17442) that uniquely identifies a legal entity in financial markets. Mandatory for fund management companies, funds, and counterparties to most regulated transactions. → Chapter 4, → Chapter 5.

**Life-Cycle** *(Lebenszyklus)* — The sequence of states a fund moves through from launch to liquidation: in-registration, launched, active, in-liquidation, liquidated. FundsXML does not carry a formal life-cycle enumeration, but some status information is captured in the fund static data.

### M

**Management Company** — See → Asset Manager.

**Mapping** *(Abbildung)* — The systematic connection between each FundsXML element that a pipeline must populate and the source-system field from which its value is drawn. Typically captured in a mapping table with columns for path, source system, source column, transformation rule, and default. → Chapter 13.

**Master Fund** — The fund in which one or more → Feeder Funds invest substantially all of their assets. A master-feeder structure is typically used for cross-border distribution efficiency.

**MiFID II** — Markets in Financial Instruments Directive II. The EU directive (2014/65/EU) that governs investment services and regulated markets, including the target-market and cost-disclosure requirements that the → EMT template carries. → Chapter 8.

### N

**Namespace** *(Namensraum)* — An XML mechanism for scoping element and attribute names to a specific vocabulary, identified by a URI. FundsXML 4.2 is defined without a target namespace, which is unusual for a modern XML standard but simplifies tooling. → Chapter 4.

**NAV** — Net Asset Value *(Nettoinventarwert)*. The total value of a fund's assets minus its liabilities, usually expressed both as a total figure (→ TNAV) and as a per-share figure (NAV per share). The central number in fund accounting and the anchor of every FundsXML dynamic-data delivery. → Chapter 5.

**Non-Functional Requirement** *(Nicht-funktionale Anforderung)* — A requirement about how a system operates rather than what it does: performance, availability, security, monitoring, audit retention. → Chapter 13.

### O

**OFFICIAL** — One of three values of `TotalAssetNature` (together with `ESTIMATED` and `TECHNICAL`), indicating that the NAV in the delivery is the final, official figure that investors will transact against. → Chapter 5.

**Operations Team** *(Betriebsteam)* — The permanent team that runs the production pipeline after the project team has disbanded. Its role, capabilities, and relationship to the builders are central to the project-to-operations transition. → Chapter 13.

### P

**PAI** — Principal Adverse Impacts. A defined set of sustainability indicators, mandated by SFDR, that asset managers must disclose for investment products. PAI values are carried in the → EET template. → Chapter 8.

**Parallel Run** *(Parallelbetrieb)* — A go-live strategy in which both the legacy pipeline and the new pipeline emit deliveries for the same period, allowing daily comparison and a safety net if the new pipeline fails. The professional standard for FundsXML go-lives. → Chapter 13.

**Paying Agent** *(Zahlstelle)* — A local agent in a distribution country that handles subscription payments, redemption payments, and distributions on behalf of investors in that country. A legal requirement for cross-border UCITS distribution in some jurisdictions.

**Pipeline** — The end-to-end sequence of components that move data from source to destination: in the producer case, from internal databases through aggregation, generation, validation, and emission; in the consumer case, from ingestion through parsing, validation, and loading. → Chapter 12.

**[Portfolio](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio)** *(Portfolio, Vermögensaufstellung)* — The full list of positions held by a fund at a given valuation date. In FundsXML, carried in the `Portfolios` block as one or more `Portfolio` elements, each containing multiple `Position` entries. → Chapter 6.

**Position** *(Position)* — A specific holding of a specific instrument within a portfolio: the quantity, the unit price, the market value, and any associated classifications. → Chapter 6.

**PRIIPs** — Packaged Retail and Insurance-based Investment Products. The EU regulation (1286/2014) that requires a standardised → KID for retail investment products. → EPT template data is the input. → Chapter 8.

**Producer** *(Datenlieferant)* — A system or organisation that generates FundsXML deliveries: asset manager, fund administrator, reporting agent. Contrast with → Consumer. → Chapter 1.

**Prospectus** *(Verkaufsprospekt)* — The official legal document describing a fund's investment strategy, risks, costs, and structure, required by UCITS and AIFMD for investor disclosure. Referenced from FundsXML by URL or document identifier rather than embedded.

**Prototype** *(Prototyp)* — A throwaway implementation built during Phase 3 of an implementation project to discover the problems that only become visible when code meets real data. Deliberately separate from the production build. → Chapter 13.

### R

**Redemption** *(Rücknahme)* — An investor's sale of fund shares back to the fund at the current NAV, reducing the fund's TNAV and share count. Recorded in FundsXML in the dynamic-data flows block. → Chapter 7.

**[RegulatoryReportings](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings)** — The FundsXML block that carries the five FinDatEx regulatory templates (EMT, EPT, EET, EFT, TPT) for a fund. Embedded rather than referenced, so the full regulatory content travels with the delivery. → Chapter 8.

**RelatedDocumentIDs** — A FundsXML element that back-references a previous delivery whose content the current delivery modifies or replaces. Required for AMEND and DELETE operations so that the consumer can locate the original. → Chapter 4, → Chapter 10.

**Runbook** *(Betriebshandbuch)* — The operational manual for a pipeline: how to start and stop it, how to investigate failures, how to re-emit deliveries, how to roll back in an emergency. Written during the testing phase, delivered to operations at go-live. → Chapter 13.

### S

**Schema** *(Schema)* — In the XML context, a formal description of the permitted structure and content of a class of documents. The FundsXML schema is defined in XSD and is the authoritative specification of what a valid FundsXML document looks like. → XSD.

**Schematron** — A rule-based validation language that expresses business rules as XPath assertions, complementing the structural validation that XSD provides. The second stage of the two-stage validation pattern. → Chapter 10.

**SFDR** — Sustainable Finance Disclosure Regulation. The EU regulation (2019/2088) that requires asset managers to disclose how they integrate sustainability risks and adverse impacts into their investment processes. The regulatory driver behind the → EET template. → Chapter 8.

**[Share Class](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass)** *(Anteilklasse)* — A sub-category of a fund offering different terms to different investor groups: different fees, different currencies, different distribution policies, different minimum investments. Each share class has its own ISIN and its own NAV per share. → Chapter 5.

**Signature** *(Signatur)* — A cryptographic proof that a document has not been altered since it was signed. FundsXML supports XML Digital Signatures (XMLDSig) at the document root, so that consumers can verify provenance and integrity. → Chapter 9.

**Source System** *(Quellsystem)* — The internal system (portfolio management, client reference database, regulatory data mart, spreadsheet) from which a producer pipeline reads its input data. The mapping table is the contract between the source systems and the pipeline. → Chapter 13.

**Subscription** *(Zeichnung)* — An investor's purchase of newly issued fund shares from the fund at the current NAV, increasing the fund's TNAV and share count. Contrast with → Redemption. → Chapter 7.

**Sub-Fund** *(Teilfonds)* — A fund that is part of an → Umbrella Fund structure, with its own investment strategy, portfolio, and NAV but sharing the umbrella's legal personality, prospectus, and management company.

**Swing Pricing** *(Swing Pricing)* — A technique in which the fund's NAV is adjusted on days of large net subscriptions or redemptions to protect existing shareholders from the transaction costs caused by other investors' flows. Applied on top of the accounting NAV to produce the published NAV.

### T

**Target Market** *(Zielmarkt)* — The category of investors for which a fund is considered suitable, as defined by MiFID II and carried in the → EMT template: investor type, knowledge and experience, financial situation, risk tolerance, investment objective, distribution strategy. → Chapter 8.

**T+1 / T+2** *(T+1 / T+2)* — Settlement conventions indicating that a trade settles one (T+1) or two (T+2) business days after trade date. European equities moved to T+2 years ago; the US moved to T+1 in 2024; Europe is scheduled to follow in 2027. → Chapter 14.

**TNAV** — Total Net Asset Value. The fund-level aggregate of net asset value across all share classes, expressed in the fund's base currency. Carried in FundsXML in `FundDynamicData/TotalAssetValues/TotalAssetValue`. → Chapter 5.

**TPT** — Tripartite Template. The FinDatEx template used for institutional reporting of portfolio composition between an asset manager, its insurance client, and the client's regulator. Named for its three-party audience. → Chapter 8.

**Transaction** *(Transaktion)* — A trade or capital event that changes the composition or size of a fund's portfolio: a buy, a sell, a subscription, a redemption, a corporate action. Recorded in FundsXML in the `Transactions` block. → Chapter 7.

**Transfer Agent** *(Transferstelle)* — The firm that maintains the register of a fund's investors and processes subscriptions, redemptions, and transfers between investors. Typically part of the fund administrator's service offering but legally a distinct role.

**Two-Stage Validation** — The validation pattern in which a FundsXML document is first checked against the XSD schema for structural correctness and then against a Schematron rule set for business-rule correctness. Only documents that pass both stages are considered valid. → Chapter 10.

### U

**UAT** — User Acceptance Testing. The phase of an implementation project in which stakeholders review the pipeline's output and formally sign off that it meets their expectations. A gate before go-live. → Chapter 13.

**UCITS** — Undertakings for Collective Investment in Transferable Securities. The EU directive framework (originally 1985, most recently consolidated as 2009/65/EC) governing retail investment funds that can be distributed cross-border within the EU on the basis of a single authorisation. The dominant European fund structure. → Chapter 1.

**Umbrella Fund** *(Umbrella-Fonds, Dachfonds)* — A legal fund structure that contains multiple → Sub-Funds under a single legal personality and a single prospectus. Common in Luxembourg and Ireland for operational and marketing efficiency.

**Unit Test** *(Unit-Test)* — A test that exercises a single small component (a single transformation rule, a single function) in isolation, giving fast and precise feedback about whether that component is correct. Contrast with → Integration Test. → Chapter 13.

### V

**Validation** *(Validierung)* — The process of checking that a FundsXML document is both structurally correct (against XSD) and semantically correct (against Schematron business rules). Distinct from *verification* of the data itself, which is an upstream concern. → Chapter 10.

**Valuation Point** *(Bewertungszeitpunkt)* — The moment in time, usually a specific time of day, at which a fund's NAV is calculated. Orders received before the cutoff time are executed at the NAV from the next valuation point. → Cutoff Time.

### W

**WKN** — Wertpapierkennnummer. The six-character German national security identifier, historically preceding ISIN and still used alongside ISIN in German-speaking markets. A secondary identifier in FundsXML.

**Working Group** *(Arbeitsgruppe)* — A standing committee of practitioners within the FundsXML association (or FinDatEx) that meets regularly to discuss a specific topic area — schema evolution, regulatory coordination, tooling — and to draft proposals for the next release. → Chapter 14.

### X

**XML** — Extensible Markup Language. The W3C standard for structured text documents on which FundsXML is built. → Chapter 2.

**XML Digital Signature** — See → Signature.

**XPath** — A W3C standard query language for selecting nodes in an XML document. The expression language used by Schematron and by most XML processing libraries. → Chapter 2, → Chapter 10.

**XSD** — XML Schema Definition. The W3C standard schema language in which the FundsXML schema is written. Describes element and attribute structure, data types, cardinalities, and enumerations. → Chapter 2, → Chapter 10.

**XSLT** — Extensible Stylesheet Language Transformations. The W3C standard language for transforming XML documents into other XML documents (or HTML, or text). Useful for producing human-readable reports from FundsXML files or for converting between schema versions. → Chapter 12 §12.3.7 for worked examples, → Chapter 11 for the FreeXmlToolkit XSLT Developer tab.

---

## A.2 Acronyms

The following acronyms recur throughout the book. Where a term is treated in detail elsewhere in this glossary or in the main text, the relevant reference is given.

- **AIF** — Alternative Investment Fund → A.1
- **AIFMD** — Alternative Investment Fund Managers Directive → A.1, Chapter 1
- **BaFin** — Bundesanstalt für Finanzdienstleistungsaufsicht (German financial supervisory authority)
- **CFI** — Classification of Financial Instruments (ISO 10962)
- **CRD** — Client Reference Database (a type of internal source system, not a standard acronym)
- **CSV** — Comma-Separated Values (legacy tabular format)
- **CUSIP** — Committee on Uniform Securities Identification Procedures (9-character North American security identifier)
- **DOM** — Document Object Model (tree-based XML parsing API)
- **DTD** — Document Type Definition (older XML schema language, predecessor to XSD)
- **EET** — European ESG Template → A.1, Chapter 8
- **EFT** — European Feeder Fund Template → A.1, Chapter 8
- **EMIR** — European Market Infrastructure Regulation
- **EMT** — European MiFID Template → A.1, Chapter 8
- **EPT** — European PRIIPs Template → A.1, Chapter 8
- **ESAP** — European Single Access Point → A.1, Chapter 14
- **ESG** — Environmental, Social, and Governance → A.1
- **ESMA** — European Securities and Markets Authority → A.1
- **ETF** — Exchange-Traded Fund → A.1
- **EU** — European Union
- **FIGI** — Financial Instrument Global Identifier → A.1
- **FinDatEx** — European Working Group on Investment Data Exchange → A.1, Chapter 8
- **FMA** — Finanzmarktaufsicht (Austrian financial market authority)
- **GLEIF** — Global Legal Entity Identifier Foundation → A.1
- **HTTPS** — HyperText Transfer Protocol Secure
- **ISIN** — International Securities Identification Number → A.1
- **ISO** — International Organization for Standardization
- **JAXP** — Java API for XML Processing
- **JSON** — JavaScript Object Notation
- **KID** — Key Information Document → A.1, Chapter 8
- **KVG** — Kapitalverwaltungsgesellschaft (German: management company)
- **LEI** — Legal Entity Identifier → A.1
- **MIC** — Market Identifier Code (ISO 10383, 4-character venue identifier)
- **MiFID II** — Markets in Financial Instruments Directive II → A.1, Chapter 8
- **NAV** — Net Asset Value → A.1, Chapter 5
- **PAI** — Principal Adverse Impacts → A.1, Chapter 8
- **PMS** — Portfolio Management System (internal system type, not a standard acronym)
- **PRIIPs** — Packaged Retail and Insurance-based Investment Products → A.1, Chapter 8
- **RRDM** — Regulatory Reporting Data Mart (internal system type, not a standard acronym)
- **REST** — Representational State Transfer
- **RTS** — Regulatory Technical Standards (issued by ESMA)
- **SAX** — Simple API for XML (streaming XML parser interface)
- **SEDOL** — Stock Exchange Daily Official List (7-character UK/Irish security identifier)
- **SFDR** — Sustainable Finance Disclosure Regulation → A.1, Chapter 8
- **SFTP** — SSH File Transfer Protocol
- **SFTR** — Securities Financing Transactions Regulation
- **StAX** — Streaming API for XML (Java pull-parser)
- **TNAV** — Total Net Asset Value → A.1, Chapter 5
- **TPT** — Tripartite Template → A.1, Chapter 8
- **UAT** — User Acceptance Testing → A.1, Chapter 13
- **UCITS** — Undertakings for Collective Investment in Transferable Securities → A.1, Chapter 1
- **URL** — Uniform Resource Locator
- **UTC** — Coordinated Universal Time
- **UUID** — Universally Unique Identifier
- **WKN** — Wertpapierkennnummer → A.1
- **XML** — Extensible Markup Language → A.1
- **XMLDSig** — XML Digital Signature → A.1, Chapter 9
- **XPath** — XML Path Language → A.1
- **XQuery** — XML Query Language
- **XSD** — XML Schema Definition → A.1
- **XSLT** — Extensible Stylesheet Language Transformations → A.1
