# Appendix C — FundsXML Schema Overview

*Structured reference for elements, types, and enumerations*

---

This appendix is a structured reference to the FundsXML 4.2 schema (version 4.2.8 as of the time of writing). Chapters 4 through 8 introduced the same material narratively and with deliberate pedagogical simplifications; this appendix gives the authoritative structural view. Where the narrative chapters presented simplified element names or paths for teaching purposes, the tables below give the real schema names, types, cardinalities, and enumeration values.

**Scope.** The schema defines well over six hundred complex types. Most of those exist to model edge cases — specific corporate actions, niche asset classes, country-specific disclosures — and are rarely touched by a typical producer pipeline. This appendix covers the **curated subset** that every producer and consumer implementation encounters: the top-level structure, the ControlData envelope, the core Fund and FundStaticData/FundDynamicData blocks, the Portfolio and Position model, the Transactions model, the RegulatoryReportings block, the common reusable types, and the extension mechanisms. A full schema browser (the FreeXmlToolkit XSD view from Chapter 11, or an online schema viewer) should be consulted for anything beyond this subset.

**Conventions.**

- **Cardinality** is given as `1..1` (required, exactly one), `0..1` (optional), `0..n` (any number including zero), or `1..n` (at least one).
- **Type** is the schema type name where the element references a named type; simple built-in types (`xs:date`, `xs:decimal`, `xs:boolean`, `xs:dateTime`, `xs:string`, etc.) are shown with the `xs:` prefix.
- **⚑** marks enumerated values. For short enumerations the full list is shown inline; for longer ones the list is given in §C.7.
- **⊕** marks extension points (places where `CustomAttributes` or `CountrySpecificData` may be used).
- All element and type names are **case-sensitive** exactly as written. FundsXML does not use a target namespace, so the names below appear unprefixed in instance documents.

---

## C.1 Top-Level Structure

The root element is [`FundsXML4`](https://fundsxml.github.io/index.html?xpath=/FundsXML4). Its children form the main content blocks of the document. `ControlData` is mandatory; everything else is optional, and a valid document may contain only `ControlData` together with one or more of the optional blocks appropriate to the delivery's purpose.

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| [`ControlData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData) | `ControlDataType` | 1..1 | Envelope metadata — document ID, date, supplier, operation. See §C.2. |
| [`Funds`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds) | (inline complex) | 0..1 | Container for [`Fund`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund) elements. See §C.3. |
| `AssetMgmtCompanyDynData` | `AssetMgmtCompanyDynDataType` | 0..1 | Dynamic data of asset management companies (sales, AuM, statistics). |
| [`AssetMasterData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData) | `AssetMasterDataType` | 0..1 | Reference data for instruments referenced by portfolio positions. See §C.4.4. |
| [`Documents`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Documents) | `DocumentsType` | 0..1 | References to fund-related documents (KID, prospectus, annual report). See §C.7.5. |
| [`RegulatoryReportings`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings) | `RegulatoryReportingsType` | 0..1 | FinDatEx templates (EMT, EPT, EET, EFT, TPT). See §C.6. |
| [`CountrySpecificData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/CountrySpecificData) | `CountrySpecificDataType` | 0..1 | Country-specific extensions at the document level. ⊕ |
| `ds:Signature` | XMLDSig | 0..1 | Enveloped XML Digital Signature. See Chapter 9. |

Note one detail that is occasionally surprising: `RegulatoryReportings` lives at the **document root**, not inside each `Fund`. A delivery that covers multiple funds with regulatory reporting data places the reporting block once at the top level, with internal references tying each report to the relevant fund.

---

## C.2 ControlData Block

`ControlData` is the envelope metadata of every FundsXML delivery. Every consumer inspects `ControlData` first to decide how to handle the incoming document: who sent it, when it was generated, what operation it represents, and which earlier delivery (if any) it relates to.

### C.2.1 Direct Children of ControlData

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| [`UniqueDocumentID`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/UniqueDocumentID) | `Text128Type` | 1..1 | Document identifier, unique per data supplier. |
| `DocumentGenerated` | `xs:dateTime` | 1..1 | Timestamp at which the document was created. |
| `Version` | (enum) | 0..1 | Schema version: `4.0.0` through `4.2.8`. ⚑ |
| `ContentDate` | `xs:date` | 1..1 | Main valuation date for the delivery. |
| [`DataSupplier`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataSupplier) | `DataSupplierType` | 1..1 | Organisation that produced the document. See §C.2.2. |
| [`DataOperation`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataOperation) | (enum) | 0..1 | `INITIAL`, `AMEND`, or `DELETE`. ⚑ |
| `RelatedDocumentIDs` | (inline) | 0..1 | Back-references to related deliveries. Required for `DELETE`. |
| `Language` | `xs:language` | 0..1 | Default language for text content. |
| `ModuleUsage` | (inline) | 0..1 | List of schema modules used. See §C.2.3. |
| `CountrySpecificData` | (inline) | 0..1 | Country-specific ControlData sections. ⊕ |
| `CustomAttributes` | `AttributesType` | 0..1 | Producer-specific extension data. ⊕ |

### C.2.2 DataSupplierType

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `SystemCountry` | `ISOCountryCodeType` | 1..1 | Two-character ISO country code. |
| `Short` | `Text64Type` | 1..1 | Short code of supplier (unique per country). |
| `Name` | `Text256Type` | 1..1 | Legal name of data supplier. |
| `Type` | `Text64Type` | 1..1 | Type of supplier: `IC` (investment company), `CB` (central bank), `NB` (national bank), `Vendor`, etc. |
| `Contact` | (inline) | 0..1 | Optional contact block (Name, Phone, Email). |

Note that `DataSupplierType` does **not** contain an `LEI` field directly; the supplier is identified by the country-scoped `Short` code, with the legal name as a human-readable label.

### C.2.3 ModuleUsage Enumeration

`ControlData/ModuleUsage/Module/Name` allows the producer to declare which schema modules the delivery exercises, so that consumers can skip parsing blocks that are not present. Valid values are:

`AssetMasterData` · `AssetMgmtCompDynData` · `CountrySpecificData_AT` · `CountrySpecificData_DE` · `CountrySpecificData_DK` · `CountrySpecificData_FR` · `CountrySpecificData_LU` · `CountrySpecificData_NL` · `FundDynamicData` · `FundStaticData` · `PortfolioData` · `RegulatoryReporting_EMIR` · `RegulatoryReporting_EMT` · `RegulatoryReporting_KIID` · `RegulatoryReporting_PRIIPS` · `RegulatoryReporting_SolvencyII` · `ShareClassData` · `TransactionData`

### C.2.4 RelatedDocumentIDs

```
RelatedDocumentIDs
  └── RelatedDocumentID (Text128Type) — 1..n
```

A single `RelatedDocumentIDs` element contains one or more `RelatedDocumentID` children, each of which is a `UniqueDocumentID` from a previous delivery. `DELETE` operations must specify which delivery is being retracted via this element; `AMEND` operations may optionally specify which delivery they supersede.

---

## C.3 Fund Block

`Funds` is a container with exactly one child element: `Fund`, which appears once per fund described by the delivery.

```
Funds
  └── Fund (FundType) — 1..n
```

### C.3.1 FundType — Direct Children

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `Identifiers` | `IdentifiersType` | 1..1 | Fund identifiers (LEI, ISIN, etc.). See §C.7.2. |
| `Names` | `NamesType` | 1..1 | Fund names. See §C.3.2. |
| `Currency` | `ISOCurrencyCodeType` | 1..1 | Base currency (ISO 4217). |
| `SingleFundFlag` | `xs:boolean` | 1..1 | `true` for standalone funds, `false` for umbrella structures. |
| `DataSupplier` | `DataSupplierType` | 0..1 | Fund-level supplier, if different from ControlData. |
| [`FundStaticData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData) | `FundStaticDataType` | 0..1 | Rarely-changing fund metadata. See §C.3.3. |
| [`FundDynamicData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData) | `FundDynamicDataType` | 0..1 | Valuation-date data. See §C.3.4. |
| `SingleFund` *or* `Subfunds` | (choice) | 0..1 | Choice between `SingleFundType` (standalone) and a `Subfunds` container holding one or more `SubfundType`. |
| `CountrySpecificData` | `CountrySpecificFundDataType` | 0..1 | Country-specific fund extensions. ⊕ |

The `SingleFund` / `Subfunds` choice reflects the umbrella-structure distinction: a standalone fund uses `SingleFund` (which holds `ShareClasses` and optional `Segments`); an umbrella fund uses `Subfunds` (which holds one or more `Subfund` elements, each with its own share classes and segments).

### C.3.2 NamesType

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `OfficialName` | `Text500Type` | 1..1 | Legal official name. |
| `FullName` | `Text500Type` | 0..1 | Full name (for sub-funds within an umbrella). |
| `MarketingName` | `Text500Type` | 0..1 | Marketing name. |
| `ShortName` | `Text100Type` | 0..1 | Short name (≤ 100 characters). |
| `PreviousName` | (inline) | 0..1 | Previous name with effective date range. |

### C.3.3 FundStaticDataType — Major Children

`FundStaticData` is large (roughly twenty direct children plus nested structures). The elements a typical producer populates are:

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `DomicileCountry` | `ISOCountryCodeType` | 0..1 | Two-character ISO country code. |
| `ListedLegalStructure` / `UnlistedLegalStructure` | (choice) | 0..1 | Either an enumerated legal structure or free text. See §C.7.4. |
| `InceptionDate` | `xs:date` | 0..1 | Date the fund was launched. |
| `StartOfFiscalYear` | `DayMonthType` | 0..1 | First day of fiscal year (day/month pair). |
| `EndOfFiscalYear` | `DayMonthType` | 0..1 | Last day of fiscal year (day/month pair). |
| `OpenClosedEnded` | (enum) | 0..1 | `OPEN` or `CLOSED`. ⚑ |
| `MaturityDate` | `xs:date` | 0..1 | Planned end date (for closed-ended funds). |
| `LiquidationDate` | `xs:date` | 0..1 | Date the fund was closed. |
| `Administrator` | `CompanyType` | 0..1 | Fund administrator. |
| `Auditor` | `CompanyType` | 0..1 | External auditor. |
| `Custodian` | `CompanyType` | 0..1 | Depositary / custodian bank. |
| `InvestmentCompany` | `CompanyType` | 0..1 | Asset management company. |
| `FundTexts` | (inline) | 0..1 | Multi-language marketing and descriptive text. |
| `Classifications` | `ClassificationsType` | 0..1 | Classification schemes (BVI, SRI, etc.). |
| `Benchmarks` | (inline) | 0..1 | Benchmark static data. |
| `FundHedgingStrategy` | `HedgingStrategyType` | 0..1 | Hedging approach. |
| `OngoingCosts` | (inline) | 0..1 | Fee structure (management fee, performance fee, transaction costs). |
| `SFDRProductType` | (enum) | 0..1 | `0`, `6`, `8`, or `9`. ⚑ See §C.7.3. |
| `CustomAttributes` | `AttributesType` | 0..1 | Extension data. ⊕ |

### C.3.4 FundDynamicDataType

`FundDynamicData` is surprisingly compact — it has only three direct children, each of which contains the real complexity:

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| [`TotalAssetValues`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/TotalAssetValues) | (inline) | 0..1 | Container for `TotalAssetValue` elements (one per NAV date / variant). |
| [`Portfolios`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios) | (inline) | 0..1 | Container for [`Portfolio`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio) elements (one per valuation date). |
| `Benchmarks` | (inline) | 0..1 | Container for `Benchmark` dynamic-data elements. |

### C.3.5 TotalAssetValueType

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `NavDate` | `xs:date` | 1..1 | Valuation date. |
| `TotalAssetNature` | (enum) | 1..1 | `OFFICIAL`, `ESTIMATED`, or `TECHNICAL`. ⚑ |
| `TotalNetAssetValue` | `FundAmountType` | 0..1 | Total net asset value (TNAV). |
| `TotalGrossAssetValue` | `FundAmountType` | 0..1 | Gross asset value (closed-ended and real-estate funds). |
| `SharesOutstanding` | `xs:decimal` | 0..1 | Number of shares used for NAV calculation. |
| `Ratio` | `PercentageType` | 0..1 | Share-class weight within the fund (sums to 100 %). |
| `OtherTotalAssetValues` | (inline) | 0..1 | Additional variants (swing NAV, hold-to-maturity, etc.). |

### C.3.6 SingleFundType

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `SingleFundStaticData` | `SingleFundStaticDataType` | 0..1 | Static data specific to the standalone fund structure. |
| [`ShareClasses`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses) | (inline) | 0..1 | Container for [`ShareClass`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass) elements. |
| `Segments` | (inline) | 0..1 | Container for `Segment` elements (for funds internally split by manager). |

### C.3.7 ShareClassType — Major Children

A share class has its own identifiers, names, currency, and a detailed set of dynamic data. The major children are:

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `Identifiers` | `IdentifiersType` | 1..1 | Share-class identifiers (ISIN, WKN, etc.). |
| `Names` | `NamesType` | 1..1 | Share-class names. |
| `Currency` | `ISOCurrencyCodeType` | 1..1 | Share-class currency. |
| `ShareClassType` | `ShareClassTypeType` | 0..1 | Share-class type designation (A, B, I, etc.). |
| `InceptionDate` | `xs:date` | 0..1 | Date the share class was launched. |
| `LiquidationDate` | `xs:date` | 0..1 | Date the share class was closed. |
| `StaticData` | (inline) | 0..1 | Share-class-specific static details. |
| `DynamicData` | (inline) | 0..1 | NAV, prices, flows, earnings. |

---

## C.4 Portfolio Block

The portfolio block lives inside `FundDynamicData/Portfolios`. Each `Portfolio` element represents a snapshot of holdings at a specific valuation date.

### C.4.1 PortfolioType

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `NavDate` | `xs:date` | 1..1 | Valuation date for all data in this portfolio block. |
| [`Positions`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions) | `PositionsType` | 0..1 | Holdings (securities, cash, accounts, fees). |
| `Transactions` | `TransactionsType` | 0..1 | Transactions within the portfolio. See §C.5. |
| `Earnings` | `EarningsType` (extended) | 0..1 | Earnings data (coupons, dividends, distributions). |
| `PositionsDecomposed` | `PositionsDecomposedType` | 0..1 | Look-through positions (underlying holdings of fund-of-fund positions). |
| `BreakDowns` | `BreakDownsType` | 0..1 | Aggregated breakdown statistics (by country, sector, currency). |

### C.4.2 PositionType — Major Children

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `UniqueID` | `xs:IDREF` | 1..1 | Reference to `AssetMasterData/Asset/UniqueID`. |
| `Identifiers` | `IdentifiersType` | 0..1 | Duplicate identifiers for convenience (ISIN, ticker). |
| `Currency` | `ISOCurrencyCodeType` | 0..1 | Valuation currency of the position. |
| `TotalValue` | `FundAmountType` | 1..1 | Total position value (sum across all positions equals fund TNAV). |
| `OtherTotalValues` | (inline) | 0..1 | Additional valuations (e.g. hold-to-maturity). |
| `Units` | `xs:decimal` | 0..1 | Number of units or nominal amount. |
| `PriceValue` | `AmountType` | 0..1 | Unit price at valuation. |
| `PricePercent` | `xs:decimal` | 0..1 | Price as a percentage of nominal (for bonds). |
| `AccruedInterest` | `AmountType` | 0..1 | Accrued interest amount (for interest-bearing instruments). |
| `Rates` | (inline) | 0..1 | FX rates used for currency translation. |
| `Account` | `AccountType` | 0..1 | Cash-account details (for account positions). |
| `Equity`, `Bond`, `Warrant`, ... | (inline) | 0..1 each | Instrument-type-specific position details. |

### C.4.3 Position Instrument Coverage

A `Position` element carries instrument-type-specific data in one of several optional sub-elements. The sub-element used depends on the `AssetType` of the referenced asset in `AssetMasterData`. The most-used sub-elements are:

| Sub-element | Covers |
|---|---|
| `Equity` | Equities, ordinary and preference shares. |
| `Bond` | Government bonds, corporate bonds, convertible bonds (basic fields). |
| `ConvertibleBond` | Convertible bond details (conversion dates, price, ratio). |
| `Warrant` | Warrants. |
| `Option` | Options (calls, puts, American, European). |
| `Future` | Futures contracts. |
| `FXForward` | FX forward contracts. |
| `Swap` | Interest-rate, currency, CDS, and total-return swaps. |
| `Repo` | Repo and reverse-repo contracts. |
| `FixedTimeDeposit` | Term deposits. |
| `RealEstate` | Direct real-estate holdings. |
| `REIT` | Real estate investment trusts. |
| `Fund` | Holdings of other funds (including ETFs). |
| `PrivateEquity` | Private-equity participations. |
| `Certificate` | Certificates and structured products. |
| `Commodity` | Commodity holdings. |
| `Crypto` | Cryptocurrency holdings. |

### C.4.4 AssetMasterData and AssetType

`AssetMasterData/Asset` is the reference data block. Each asset carries a `UniqueID` (schema type `xs:ID`) that position elements reference via `xs:IDREF`.

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `UniqueID` | `xs:ID` | 1..1 | Document-unique identifier (target of IDREF from positions). |
| `Identifiers` | `IdentifiersType` | 0..1 | ISIN, ticker, etc. |
| `Currency` | `ISOCurrencyCodeType` | 1..1 | Nominal currency of the instrument. |
| `Country` | `ISOCountryCodeType` | 0..1 | Country of the issuer or instrument. |
| `Name` | `Text256Type` | 1..1 | Human-readable name. |
| `AssetType` | (enum) | 1..1 | Two-character asset-type code. See below. ⚑ |
| `AssetDetails` | `AssetDetailsType` | 0..1 | Type-specific details. |
| `Ratings` | (inline) | 0..1 | Credit ratings. |
| `CountrySpecificData` | (inline) | 0..1 | Country-specific asset extensions. ⊕ |

The `AssetType` enumeration uses two-character codes:

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| `EQ` | Equity | `AC` | Account |
| `BO` | Bond (incl. convertibles) | `FE` | Fee |
| `SC` | Share Class (fund unit) | `RE` | Real Estate |
| `WA` | Warrant | `RT` | REIT |
| `CE` | Certificate | `LO` | Loan |
| `OP` | Option | `RI` | Right |
| `FU` | Future | `CO` | Commodity |
| `FX` | FX-Forward | `PE` | Private Equity |
| `SW` | Swap | `CP` | Commercial Paper |
| `RP` | Repo | `IX` | Index |
| `FT` | Fixed Time Deposit | `CR` | Crypto |
| `CM` | Call Money |   |   |

---

## C.5 Transactions

`Portfolio/Transactions` contains a list of `Transaction` elements. Each transaction has a unique `TransactionID` (enforced by a schema-level key constraint on the container) and one of five possible kinds.

### C.5.1 TransactionType — Major Children

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `TransactionID` | `Text256Type` | 1..1 | Unique transaction identifier. |
| `CancellationFlag` | `xs:boolean` | 0..1 | `true` if the transaction has been cancelled. |
| `OriginalTransactionID` | `Text256Type` | 0..1 | For cancellations, the ID of the original transaction. |
| `AssetUniqueID` | `xs:IDREF` | 0..1 | Reference to `AssetMasterData/Asset/UniqueID`. |
| `Identifiers` | `IdentifiersType` | 0..1 | Duplicate identifiers of the instrument. |
| `Currency` | `ISOCurrencyCodeType` | 0..1 | Instrument currency. |
| `TransactionKind` | (enum) | 1..1 | `BUY`, `SELL`, `LENDING_BUY`, `LENDING_SELL`, or `CORP_ACTION`. ⚑ |
| `SettlementCurrency` | `ISOCurrencyCodeType` | 0..1 | Settlement currency (may differ from instrument currency). |
| `EntryDate` | `xs:date` | 0..1 | Booking date. |
| `ValutaDate` | `xs:date` | 0..1 | Value date (effective date). |
| `ClosingDate` | `xs:date` | 0..1 | Trade date. |
| `OrderTimestamp` | `xs:dateTime` | 0..1 | Exact order time. |
| *(numerous amount and quantity fields)* | | | Quantity, price, gross/net values, commissions, taxes, FX rates. |

Note that the `TransactionKind` enumeration has exactly five values. The narrative in Chapter 7 used pedagogical labels (`SUBSCRIPTION`, `REDEMPTION`, etc.) that do not appear in the real schema — investor flows are modelled at the share-class level, not as portfolio transactions. The schema-accurate distinction is: **`Transaction` covers portfolio trading activity; investor flows are captured elsewhere in the share-class dynamic data.**

### C.5.2 EarningsType

`Portfolio/Earnings` carries coupons, dividends, and distributions resulting from portfolio positions. The block is attributed with `from` and `to` dates that bound the reporting period. The underlying `EarningsType` carries per-position earnings entries with amounts, dates, and tax treatment; the structure is too detailed for this overview — consult the schema browser if you need to populate it.

---

## C.6 RegulatoryReportings and FinDatEx Templates

`RegulatoryReportings` at the document root has exactly two children:

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `DirectReporting` | `DirectReportingType` | 0..1 | Direct regulatory reporting (EMIR, EMT, EFT, EET, KIIDs). |
| `IndirectReporting` | `IndirectReportingType` | 0..1 | Indirect reporting for downstream consumers (TPT, PRIIPS/EPT). |

The terminology reflects the distinction between reports that flow directly to regulators (direct) and reports that flow through distributors or insurance-company intermediaries (indirect).

### C.6.1 DirectReporting Children

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `EMIR` | `EMIRType` | 0..1 | OTC derivatives reporting per Regulation (EU) 648/2012. |
| `KIIDs` | `KIIDsType` | 0..1 | UCITS KIID data (predecessor of PRIIPs KID). |
| `EMT` | `EMTType` | 0..1 | EMT v1.0 (2017). |
| `EMT_V3` | `EMTType_V3` | 0..1 | EMT v3.0 (2019). |
| `EMT_V4` | `EMTType_V4` | 0..1 | EMT v4.0 (2022). |
| `EMT_V4_1` | `EMTType_V41` | 0..1 | EMT v4.1 (2023). |
| `EMT_V4_2` | `EMTType_V42` | 0..1 | EMT v4.2 (2024). |
| `EFTs` | `EFTType` | 0..1 | European Feedback Template v1.0. |
| `EET1.0` | `EETsType` | 0..1 | EET v1.0 (2022). |
| `EET1.1` | `EETsType1.1` | 0..1 | EET v1.1. |
| `EET1.1.1` | `EETsType1.1.1` | 0..1 | EET v1.1.1. |
| `EET1.1.2` | `EETsType1.1.2` | 0..1 | EET v1.1.2. |
| `EET1.1.3` | `EETsType1.1.3` | 0..1 | EET v1.1.3. |

Each template version is a distinct element with its own type. A producer emits one of the EMT versions and one of the EET versions — typically the most recent — and consumers accept whichever versions their systems support. The multiple versions enable the gradual cross-ecosystem upgrade cycle that Chapter 13 described.

### C.6.2 IndirectReporting Children

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `TripartiteTemplateSolvencyII` | `TripartiteTemplateSolvencyIIType` | 0..1 | TPT v4 (2018). |
| `TripartiteTemplateSolvencyII_V5` | `TripartiteTemplateSolvencyIIType_V5` | 0..1 | TPT v5 (2020). |
| `TripartiteTemplateSolvencyII_V6` | `TripartiteTemplateSolvencyIIType_V6` | 0..1 | TPT v6 (2022). |
| `PRIIPS` | `PRIIPSType` | 0..1 | EPT v1.0 / v1.1 (PRIIPs template). |
| `PRIIPS_V20` | `PRIIPSType_V20` | 0..1 | EPT v2.0 and Comfort-EPT v2.0. |

The PRIIPS element models both the EPT (European PRIIPs Template) used by distributors and the CEPT (Comfort EPT) used for review before publication. Newer EPT versions live in their own elements as they are published.

### C.6.3 Template Coverage

The internal structure of each FinDatEx template — the specific fields, enumerations, and value ranges — is published by FinDatEx and embedded in FundsXML. Each template has between 60 and 180 individual fields, far too many to enumerate here. Chapter 8 introduced the purpose and high-level structure of each template; for field-level detail, consult the FinDatEx specification for the relevant template version.

---

## C.7 Common Types and Enumerations

### C.7.1 AmountType and FundAmountType

```
AmountType
  └── Amount (xs:decimal) — 1..n
       └── @ccy (ISOCurrencyCodeType, required) — the currency code
```

`AmountType` can carry the same amount in multiple currencies (one `Amount` per currency, distinguished by the `ccy` attribute). `FundAmountType` is a variant used within fund- and portfolio-level values where the amount always includes one representation in the fund's base currency.

### C.7.2 IdentifiersType

The `IdentifiersType` is used wherever a fund, share class, or instrument is identified. The major children are:

| Element | Type | Cardinality | Purpose |
|---|---|---|---|
| `ISIN` | `ISINType` | 0..1 | 12-character ISIN. |
| `Bloomberg` | (inline) | 0..1 | Bloomberg Ticker, Exchange, Market, Yellow Key. |
| `Reuters` | (inline) | 0..1 | Reuters identifier. |
| `FIGI` | `Text32Type` | 0..1 | Financial Instrument Global Identifier. |
| `CFI` | `Text6Type` | 0..1 | Classification of Financial Instruments (ISO 10962). |
| `LEI` | `LEICodeType` | 0..1 | Legal Entity Identifier (20 characters, ISO 17442). |
| `WKN` | `Text6Type` | 0..1 | German Wertpapierkennnummer. |
| `SEDOL` | `Text7Type` | 0..1 | UK/Irish Stock Exchange Daily Official List code. |
| `CUSIP` | `Text9Type` | 0..1 | North American identifier. |
| `OtherID` | (inline) | 0..n | Container for proprietary identifiers. |

All identifier fields are optional; at least one is typically populated.

### C.7.3 Core Enumerations

**`DataOperation`** (in `ControlData/DataOperation`):

| Value | Meaning |
|---|---|
| `INITIAL` | First-time delivery of new data. |
| `AMEND` | Update or correction to previously delivered data. |
| `DELETE` | Retract a previous delivery. Requires `RelatedDocumentIDs`. |

**`TotalAssetNature`** (in `TotalAssetValue/TotalAssetNature`):

| Value | Meaning |
|---|---|
| `OFFICIAL` | Final NAV that investors will transact against. |
| `ESTIMATED` | Preliminary NAV, pending finalisation. |
| `TECHNICAL` | Internal technical value, not for external use. |

**`TransactionKind`** (in `Transaction/TransactionKind`):

| Value | Meaning |
|---|---|
| `BUY` | Purchase of an asset. |
| `SELL` | Sale of an asset. |
| `LENDING_BUY` | Securities-lending purchase. |
| `LENDING_SELL` | Securities-lending sale. |
| `CORP_ACTION` | Corporate-action-driven position change. |

**`OpenClosedEnded`** (in `FundStaticData/OpenClosedEnded`):

| Value | Meaning |
|---|---|
| `OPEN` | Open-ended fund (ongoing subscription/redemption). |
| `CLOSED` | Closed-ended fund (fixed capital). |

**`SFDRProductType`** (in `FundStaticData/SFDRProductType`):

| Value | Meaning |
|---|---|
| `0` | Unclassified or not applicable. |
| `6` | Article 6 product (no sustainability characteristics). |
| `8` | Article 8 product (promotes ESG characteristics). |
| `9` | Article 9 product (has sustainable investment objective). |

### C.7.4 Listed Legal Structure Enumeration

`FundStaticData/ListedLegalStructure` uses these values:

`UCITS` · `UCITS - SICAV` · `UCITS - SICAF` · `UCITS - CONTRACTUAL TYPE` · `AIF` · `AIF - HEDGE FUND` · `AIF - PRIVATE EQUITY FUND` · `AIF - VENTURE CAPITAL FUND` · `AIF - REAL ESTATE FUND` · `AIF - REIT` · `AIF - INFRASTRUCTURE FUND` · `AIF - COMMODITY FUND` · `AIF - SOVEREIGN WEALTH FUND` · `AIF - ELTIF` · `AIF - EUVECA` · `AIF - EUSEF` · `SPV`

If none of these fits, use `UnlistedLegalStructure` with free text.

### C.7.5 Documents Block

`Documents/Document` represents references to (or embedded content of) fund-related documents. The `Type/ListedType` enumeration is:

| Value |
|---|
| `AIFMD` |
| `AnnualReport` |
| `AuditReport` |
| `Factsheet` |
| `KID` |
| `Prospectus` |
| `PRIIPS-KID` |

Other document types are supported via `Type/UnlistedType` (free text). Documents are typically referenced by URL; inline content is also supported but uncommon.

### C.7.6 Reusable Text Types

The schema defines several `Text…Type` simple types that restrict element content by length:

| Type | Max length |
|---|---|
| `Text16Type` | 16 characters |
| `Text32Type` | 32 characters |
| `Text64Type` | 64 characters |
| `Text100Type` | 100 characters |
| `Text128Type` | 128 characters |
| `Text200Type` | 200 characters |
| `Text256Type` | 256 characters |
| `Text500Type` | 500 characters |

---

## C.8 Extension Points

### C.8.1 CustomAttributes

The [`CustomAttributes`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData/CustomAttributes) element uses `AttributesType`, the standard extension mechanism for producer-specific data that does not fit into any standard element. It is permitted inside `ControlData`, `FundStaticData`, and many other places throughout the schema.

```
CustomAttributes (AttributesType)
  └── Attribute — 1..n
        ├── Name (Text256Type) — 1..1
        ├── Type (enum T/N/D/B) — 1..1
        └── (choice) — 1..1
              ├── ValueText (xs:string)
              ├── ValueNumber (xs:decimal)
              ├── ValueDate (xs:date)
              └── ValueBoolean (xs:boolean)
```

The `Type` indicator and the chosen `Value*` element must agree: `Type="T"` pairs with `ValueText`, `Type="N"` with `ValueNumber`, `Type="D"` with `ValueDate`, `Type="B"` with `ValueBoolean`.

Use `CustomAttributes` sparingly. The first question before adding one should always be whether a standard element already exists; the second question should be whether the data belongs in the delivery at all. Permanent project conventions for naming the `Name` field (for example a `{producer}.{domain}.{fieldname}` scheme) prevent collisions between projects.

### C.8.2 CountrySpecificData

`CountrySpecificData` appears at several levels of the schema and allows country-specific extensions structured by ISO country code. The main locations are:

| Location | Type |
|---|---|
| `FundsXML4/CountrySpecificData` | Root-level country extensions. |
| `FundsXML4/ControlData/CountrySpecificData` | Country-specific ControlData. |
| `Funds/Fund/CountrySpecificData` | Fund-level country extensions. |
| `AssetMasterData/Asset/CountrySpecificData` | Asset-level country extensions. |

Within each of these, the sub-elements are named by ISO country code (`AT`, `DE`, `DK`, `FR`, `LU`, `NL`, and others as they are added). Each country sub-element has its own type that defines what country-specific structure is permitted. Country extensions are typically used for regulatory disclosures specific to one distribution country that do not fit into the FinDatEx templates.

---

## C.9 Schema Version Notes

This appendix documents FundsXML schema version **4.2.8**, the version current as of the book's writing in early 2026. The 4.2 minor-version series has been stable since 2019 and is backward-compatible within the series: a document valid against 4.2.0 is also valid against 4.2.8 unless it exercises an element that has been deprecated between the two versions. Producers upgrading between minor versions should consult the changelog published by the FundsXML association for the specific release they are moving to.

Earlier major versions (3.x and prior) are no longer maintained; the 4.0 transition was made many years ago and most elements in the book's target population predate the transition. Anticipated 2026 releases (4.2.9 is expected in November 2026, per the ongoing release cadence) are likely to add new fields to EET and EMT as FinDatEx publishes updated templates, but the structural overview presented in this appendix is expected to remain accurate for the foreseeable future.
