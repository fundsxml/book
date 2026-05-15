# Appendix E — Resources and Links

*Official sources, GitHub repository, community, and training offerings*

---

This appendix collects the external resources that a FundsXML practitioner is most likely to need. It is organised by category rather than alphabetically, so that a reader looking for a specific kind of resource can find the right section quickly. URLs are current as of early 2026; if a link has moved by the time you read this, the organisation name and resource description should give you enough context to find the new location.

---

## E.1 The FundsXML Association

The FundsXML association is the non-profit body that stewards the standard. Its website is the authoritative source for governance information, membership details, working-group schedules, and announcements.

- **FundsXML association website** — [https://www.fundsxml.org](https://www.fundsxml.org) — The official home of the standard. Contains the current schema files, the release changelog, the membership list, the board composition, and the working-group calendar. The website also hosts the association's contact form for enquiries about membership, schema questions, and working-group participation.
- **FundsXML GitHub repository** — [https://github.com/fundsxml](https://github.com/fundsxml) — The public repository where the schema files, sample documents, and related tooling are maintained. The issue tracker on the repository is the primary channel for reporting schema bugs, requesting clarifications, and proposing new features. Readers who want to contribute should start here. → Chapter 14 for the contribution process.
- **FundsXML schema releases** — [https://github.com/fundsxml/schema/releases](https://github.com/fundsxml/schema/releases) — Tagged releases of the FundsXML schema, each with the XSD file, changelog, and release notes. The URL pattern `https://github.com/fundsxml/schema/releases/download/{version}/FundsXML.xsd` gives direct access to any version (see §4.7.2).
- **FundsXML implementation guide** — [https://www.fundsxml.org/implementation-guide/](https://www.fundsxml.org/implementation-guide/) — Practical guidance for getting started with the standard, including the root-element declaration and schema referencing.
- **FundsXML downloads** — [https://www.fundsxml.org/downloads/](https://www.fundsxml.org/downloads/) — Schema files, sample documents, and supplementary materials available for direct download.
- **FundsXML community** — [https://www.fundsxml.org/community/](https://www.fundsxml.org/community/) — Community resources, discussion channels, and announcements.

---

## E.2 Schema and Specification Files

- **FundsXML4.xsd** — Available from [https://github.com/fundsxml/schema/releases](https://github.com/fundsxml/schema/releases) and from the association website. The file is approximately 1.7 MB and defines the complete structure of a valid FundsXML 4.x document.
- **xmldsig-core-schema.xsd** — The W3C XML Digital Signature schema, imported by `FundsXML4.xsd` for the optional `ds:Signature` element. Available from [https://www.w3.org/TR/xmldsig-core/](https://www.w3.org/TR/xmldsig-core/) and typically bundled with the FundsXML schema distribution.
- **FundsXML Online Schema Documentation** — [https://fundsxml.github.io](https://fundsxml.github.io/) — An interactive, browser-based reference for the FundsXML 4.x schema. Every element is navigable by XPath: appending `?xpath=/FundsXML4/ControlData` to the URL, for example, opens the documentation for the `ControlData` node directly. The documentation shows each element's type, cardinality, child elements, and annotations. This is the quickest way to look up a specific node without opening the XSD in an editor. Throughout this book, element names in the running text link directly to the corresponding page in this documentation. Table E.1 below lists the most important entry points.
- **FundsXML Release Changelog** — Published alongside each release on [https://github.com/fundsxml/schema/releases](https://github.com/fundsxml/schema/releases), the changelog enumerates every field added, removed, or changed. Essential reading when upgrading a pipeline from one version to the next.
- **FundsXML Documentation** — [https://www.fundsxml.org/downloads/](https://www.fundsxml.org/downloads/) — The association publishes supplementary documentation for the schema, including element-by-element descriptions, usage guidelines, and worked examples.

---

## E.3 FinDatEx Templates

The five FinDatEx regulatory templates embedded in FundsXML are published and maintained by FinDatEx, not by the FundsXML association. Each template has its own specification document, field-by-field definition, and version history.

- **FinDatEx website** — [https://findatex.eu](https://findatex.eu) — The official home of the European Working Group on Investment Data Exchange. Contains the current versions of all templates, the consultation documents for upcoming versions, and the working-group meeting calendar.
- **EMT (European MiFID Template)** — Current version: v4.3. The specification document defines approximately 150 fields covering target market, costs, risk classification, and distribution strategy. Published as an Excel workbook with field definitions and as a PDF specification.
- **EPT (European PRIIPs Template)** — Current version: v2.1. Defines the inputs needed for PRIIPs KID generation: performance scenarios, cost structures, risk indicators, and recommended holding periods.
- **EET (European ESG Template)** — Current version: v1.1.3. Carries SFDR-mandated sustainability disclosures: PAI indicators, Taxonomy alignment percentages, sustainable investment share, and exclusions policy.
- **EFT (European Feedback Template)** — Current version: v1.0. Facilitates the exchange of feeder-fund-specific information between feeder and master funds.
- **TPT (Tripartite Template)** — Current version: v7.0. Used for institutional Solvency II reporting of portfolio composition between asset managers, insurance clients, and their regulators.

---

## E.4 Tooling

### E.4.1 FreeXmlToolkit

FreeXmlToolkit is the open-source desktop application covered in Chapter 11. It provides an integrated environment for editing, validating, transforming, and signing FundsXML files.

- **FreeXmlToolkit GitHub repository** — [https://github.com/karlkauc/FreeXmlToolkit](https://github.com/karlkauc/FreeXmlToolkit) — Source code, binary releases, issue tracker, and contribution guide. The application is written in Java and JavaFX and runs on Windows, macOS, and Linux.

### E.4.2 Validation Tools

- **xmllint** — [https://gitlab.gnome.org/GNOME/libxml2](https://gitlab.gnome.org/GNOME/libxml2) — The command-line XML validator from the libxml2 project. Available on virtually all Linux and macOS systems and installable on Windows via MSYS2 or WSL. Used throughout this book for schema validation. Invocation: `xmllint --schema FundsXML4.xsd file.xml --noout`.
- **Saxon** — [https://www.saxonica.com](https://www.saxonica.com) — The reference XSLT 2.0 / 3.0 and XPath 2.0 / 3.1 processor, available in open-source (Saxon-HE) and commercial (Saxon-PE, Saxon-EE) editions. Useful for Schematron validation (which requires an XSLT processor) and for complex XPath queries.
- **lxml (Python)** — [https://lxml.de](https://lxml.de) — The Python binding for libxml2 and libxslt. Provides schema validation, XPath queries, XSLT transformation, and ISO Schematron support through the `lxml.isoschematron` module. Used in the Chapter 10 and Chapter 12 code examples.

### E.4.3 Programming Libraries

The four languages covered in Chapter 12 each have standard XML libraries suitable for FundsXML work:

- **Java: JAXP** — The Java API for XML Processing, included in the standard JDK. Provides DOM, SAX, StAX parsing, XPath evaluation, schema validation, and XSLT transformation.
- **Python: lxml** — See above. The `lxml.etree` module is the recommended library for FundsXML work in Python.
- **C#: System.Xml.Linq (LINQ to XML)** — The .NET standard library for XML processing. Provides XDocument/XElement for document construction and query, plus XmlSchemaSet for validation.
- **JavaScript/Node.js: fast-xml-parser** — [https://www.npmjs.com/package/fast-xml-parser](https://www.npmjs.com/package/fast-xml-parser) — A high-performance XML parser for Node.js. Used in the Chapter 12 example. Alternative: `xml2js` for a more DOM-like API.

---

## E.5 Regulatory References

The regulatory frameworks that drive FundsXML's content — particularly the FinDatEx template content — are published by the European Commission and by ESMA. The primary references are:

- **UCITS Directive** — Directive 2009/65/EC of the European Parliament and of the Council. The foundational directive for European retail investment funds. Consolidated text available on EUR-Lex.
- **AIFMD** — Directive 2011/61/EU on alternative investment fund managers. The companion directive for non-UCITS funds. AIFMD II (adopted 2024) amends the original.
- **MiFID II** — Directive 2014/65/EU on markets in financial instruments. The directive that drives the EMT template's target-market and cost-disclosure requirements.
- **PRIIPs Regulation** — Regulation (EU) No 1286/2014 on key information documents for packaged retail investment products. The regulation that drives the EPT template's KID-generation inputs.
- **SFDR** — Regulation (EU) 2019/2088 on sustainability-related disclosures in the financial services sector. The regulation that drives the EET template's ESG disclosures.
- **Taxonomy Regulation** — Regulation (EU) 2020/852 on the establishment of a framework to facilitate sustainable investment. Defines the criteria for environmentally sustainable economic activities referenced by the EET.
- **ESAP Regulation** — Regulation (EU) 2023/2859 establishing a European Single Access Point. Scheduled to become operational in 2027; relevant for producers whose deliveries will flow into the centralised platform. → Chapter 14.
- **EUR-Lex** — [https://eur-lex.europa.eu](https://eur-lex.europa.eu) — The official portal for EU law. All regulations and directives referenced above are available in all EU languages, with consolidated texts that incorporate subsequent amendments.

---

## E.6 Standards and Identifier Registries

- **ISO 6166 (ISIN)** — The international standard for securities identification numbers. ISINs are issued by national numbering agencies and are the primary instrument identifier in FundsXML.
- **ISO 17442 (LEI)** — The international standard for legal entity identifiers. LEIs are issued by local operating units under the oversight of GLEIF.
- **GLEIF (Global LEI Foundation)** — [https://www.gleif.org](https://www.gleif.org) — The foundation that oversees the global LEI system. Its website provides a free LEI lookup service, bulk data downloads, and documentation on LEI validation (including the check-digit algorithm).
- **ISO 4217 (Currency Codes)** — The international standard for three-letter currency codes used in FundsXML's `ISOCurrencyCodeType`.
- **ISO 3166 (Country Codes)** — The international standard for two-letter country codes used in FundsXML's `ISOCountryCodeType`.
- **ISO 10962 (CFI)** — The Classification of Financial Instruments standard. Six-character codes that classify instruments by category, group, and attribute.
- **ISO 10383 (MIC)** — The Market Identifier Code standard. Four-character codes identifying trading venues.

---

## E.7 Community and Learning

- **FundsXML annual conference** — The association organises an annual conference (typically in Vienna or a rotating European city) where practitioners, vendors, and regulators meet to discuss the state of the standard, share implementation experiences, and plan future development. The conference is open to members and, on a registration basis, to non-members.
- **Working-group meetings** — The association's working groups meet monthly by video conference and are the primary venue for hands-on schema development. Participation is open to members and, on invitation, to external experts. → Chapter 14 for how to join.
- **FundsXML on LinkedIn** — [https://www.linkedin.com/company/fundsxml](https://www.linkedin.com/company/fundsxml) — The association maintains a LinkedIn presence where announcements, conference invitations, and community news are posted.
- **FundsXML on YouTube** — [https://www.youtube.com/channel/UCzSMxta13eDlYQPEmH2_iww](https://www.youtube.com/channel/UCzSMxta13eDlYQPEmH2_iww) — Webinars, conference recordings, and tutorial videos.
- **W3C XML specifications** — [https://www.w3.org/XML/](https://www.w3.org/XML/) — The W3C website hosts the authoritative specifications for XML 1.0, XML Schema (XSD), XPath, XSLT, and XML Digital Signatures. Essential reading for practitioners who want to understand the technology layer beneath FundsXML. → Appendix B for a condensed reference.
- **This book** — *FundsXML — The European Standard for Fund Data Exchange* is itself intended as a community resource. Feedback, corrections, and suggestions for future editions are welcome through the publisher's contact channels.

---

## E.8 Companion Files from This Book

The following files accompany this book and are available for download from the book's repository. They are designed to be used together: the sample FundsXML file provides the input, and the XSLT stylesheets and programming-language scripts process it. Readers are encouraged to download all files, run the examples, and adapt them to their own FundsXML data.

### E.8.1 Sample Data

| File | Description | Chapters |
|---|---|---|
| `europa_growth_fund.xml` | Complete, schema-valid FundsXML 4.2.2 document for the fictional Europa Growth Fund. Contains ControlData, fund static data (domicile, entities), three share classes with prices and NAVs, fifteen portfolio positions (equities, bonds, FX forward, cash), and asset master data for all referenced instruments. This is the single input file for all examples below. | 4–8, 12 |
| `FundsXML.xsd` | The FundsXML 4.2.2 schema definition file, for offline validation. Validate the sample file with: `xmllint --noout --schema FundsXML.xsd europa_growth_fund.xml` | 2, 10 |

### E.8.2 XSLT Stylesheets

All stylesheets are XSLT 1.0 and can be run with `xsltproc` (bundled with libxml2 on Linux and macOS), with Saxon, or with any XSLT-capable library (Python `lxml`, Java `javax.xml.transform`, .NET `System.Xml.Xsl`).

| File | Description | Chapter |
|---|---|---|
| `examples/xslt/shareclass_csv.xsl` | Extracts a multi-column CSV of share-class data (fund name, LEI, ISIN, share-class name, currency, NAV date). Run: `xsltproc examples/xslt/shareclass_csv.xsl europa_growth_fund.xml` | §2.12.2 |
| `examples/xslt/factsheet_simple.xsl` | Produces a self-contained HTML fact sheet with fund metadata table (LEI, currency, NAV, dates) and a share-class listing. | §2.12.3 |
| `examples/xslt/dq_nav_check.xsl` | Data-quality check: verifies that portfolio position values sum to the fund's total net asset value, with rounding tolerance. | §2.12.4 |
| `examples/xslt/factsheet.xsl` | Produces a self-contained HTML fact sheet with a table showing LEI, currency, NAV, NAV date, and content date. | §12.3.7 |
| `examples/xslt/positions_csv.xsl` | Exports all portfolio positions as a CSV file, joining position data with asset master data via the UniqueID/IDREF mechanism. | §12.3.7 |

### E.8.3 Programming-Language Examples

Each script reads or processes `europa_growth_fund.xml`. Run instructions and dependency notes are included as comments at the top of each file.

**Python** (requires `lxml`; install with `pip install lxml`)

| File | Description | Chapter |
|---|---|---|
| `examples/python/read_fund.py` | Reads a FundsXML file and prints the fund name, LEI, and total NAV. | §12.3.2 |
| `examples/python/import_fund.py` | Parses a FundsXML file and imports fund data and portfolio positions into PostgreSQL. Requires `psycopg`. | §12.5.1 |
| `examples/python/export_fund.py` | Queries fund data from PostgreSQL and reconstructs a FundsXML fragment. Requires `psycopg`. | §12.5.1 |

**Java** (JDK 17+; external libraries noted per file)

| File | Description | Chapter |
|---|---|---|
| `examples/java/ReadFund.java` | Reads a FundsXML file with JAXP and XPath (no external dependencies). | §12.3.3 |
| `examples/java/FundsXmlToMongo.java` | Imports a FundsXML file into MongoDB. Requires `mongodb-driver-sync`. | §12.5.2 |
| `examples/java/MongoToFundsXml.java` | Exports fund data from MongoDB and builds a FundsXML fragment with JAXP DOM. Requires `mongodb-driver-sync`. | §12.5.2 |
| `examples/java/FundsXmlToBaseX.java` | Imports a FundsXML file into a BaseX XML database. Requires `org.basex:basex`. | §12.5.3 |
| `examples/java/BaseXQuery.java` | Queries and exports fund data from BaseX using embedded XQuery. Requires `org.basex:basex`. | §12.5.3 |

**C#** (.NET 8+)

| File | Description | Chapter |
|---|---|---|
| `examples/csharp/ReadFund.cs` | Reads a FundsXML file with LINQ to XML (no external dependencies). | §12.3.4 |

**JavaScript / Node.js** (requires `fast-xml-parser`; install with `npm install fast-xml-parser`)

| File | Description | Chapter |
|---|---|---|
| `examples/javascript/read_fund.mjs` | Reads a FundsXML file with fast-xml-parser. | §12.3.5 |

---

## E.9 FundsXML Online Schema Documentation — Quick Reference

The interactive schema documentation at [https://fundsxml.github.io](https://fundsxml.github.io/) allows direct navigation to any element via an XPath parameter in the URL. The general pattern is:

```
https://fundsxml.github.io/index.html?xpath=/FundsXML4/…
```

Table E.1 lists the most frequently needed entry points. Each URL opens the documentation page for the corresponding node, showing its type definition, cardinality, child elements, and schema annotations.

**Table E.1 — Key entry points into the FundsXML Online Schema Documentation**

| Schema Area | XPath | URL | Treated in |
|---|---|---|---|
| Root element | `/FundsXML4` | [fundsxml.github.io/…?xpath=/FundsXML4](https://fundsxml.github.io/index.html?xpath=/FundsXML4) | Chapter 3 |
| ControlData | `/FundsXML4/ControlData` | [fundsxml.github.io/…?xpath=/FundsXML4/ControlData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData) | Chapter 4 |
| Funds container | `/FundsXML4/Funds` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds) | Chapter 5 |
| Fund element | `/FundsXML4/Funds/Fund` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund) | Chapter 5 |
| FundStaticData | `/FundsXML4/Funds/Fund/FundStaticData` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/FundStaticData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData) | Chapter 5 |
| FundDynamicData | `/FundsXML4/Funds/Fund/FundDynamicData` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/FundDynamicData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData) | Chapters 5, 6 |
| Share Classes | `/FundsXML4/Funds/Fund/SingleFund/ShareClasses` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses) | Chapter 5 |
| Portfolio | `/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio) | Chapter 6 |
| Positions | `/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions) | Chapter 6 |
| AssetMasterData | `/FundsXML4/AssetMasterData` | [fundsxml.github.io/…?xpath=/FundsXML4/AssetMasterData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData) | Chapter 6 |
| Transactions (Flows) | `/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Flows` | [fundsxml.github.io/…?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Flows](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Flows) | Chapter 7 |
| RegulatoryReportings | `/FundsXML4/RegulatoryReportings` | [fundsxml.github.io/…?xpath=/FundsXML4/RegulatoryReportings](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings) | Chapter 8 |
| Documents | `/FundsXML4/Documents` | [fundsxml.github.io/…?xpath=/FundsXML4/Documents](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Documents) | Chapter 9 |
| CountrySpecificData | `/FundsXML4/CountrySpecificData` | [fundsxml.github.io/…?xpath=/FundsXML4/CountrySpecificData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/CountrySpecificData) | Chapter 9 |

Readers are encouraged to bookmark the root URL and explore the schema tree interactively. The documentation is generated directly from the XSD and therefore always reflects the structure of the published schema version.
