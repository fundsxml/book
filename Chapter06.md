<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 6 — Portfolio and Positions

*Holdings and asset classes*

---

## 6.1 Setting the Scene: What the Fund Actually Holds

At the end of Chapter 5 we had a complete description of the Europa Growth Fund: its identity, its three share classes, its fees, its total net assets of 464,552,848.78 EUR on 31 March 2026. What we did not have was any knowledge of *how that money is invested*. The [`Portfolios`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios) substructure of `FundDynamicData`, which Chapter 5 left as a placeholder comment, is where the answer lives; and alongside it, outside the `<Funds>` container at the root level of the document, sits its indispensable companion, [`AssetMasterData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData). This chapter treats both.

It is the longest chapter in the book — forty-five pages — and it is long for three reasons. First, the portfolio is structurally the richest part of a FundsXML delivery: it carries every instrument the fund holds, one entry per position, and instruments come in seven or eight broad families (equities, bonds, funds, derivatives, cash, real estate, commodities, alternatives) each with their own specialised fields. Second, the linkage between [`Portfolio`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio) and `AssetMasterData` through [`UniqueID`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData/Asset/UniqueID) is the working expression of design principle 2 from Chapter 3 — *linkage by UniqueID, not by nesting* — and mastering that linkage is central to every subsequent chapter. Third, portfolio breakdowns, the pre-computed aggregates that feed fact sheets and regulatory reports, have their own structure and their own conventions. All three topics justify the space.

One editorial decision deserves to be stated up front. The Europa Growth Fund, as we have seen, is an actively managed European equity UCITS. It holds roughly 80 to 150 equity positions, a handful of cash accounts in several currencies, and the two currency forwards that implement the CHF hedge for the R-CHF-ACC-HEDGED share class. That is what its real portfolio looks like, and it is what the complete end-to-end example in §6.12 will show. For the asset classes the fund does not hold — bonds, investment funds held as positions, real estate, commodities — the per-asset-class sections use their own isolated examples drawn from generic illustrative funds, and the complete example in §6.12 does not attempt to force these classes into the Europa Growth Fund artificially. The reader who wants to see a bond position renders §6.7's example; the reader who wants to see a derivative in context renders §6.9.4 and the corresponding fragment of §6.12. The integrity of the running example and the coverage of the asset classes can both be preserved without compromise.

By the end of this chapter, you should be able to:

- explain why portfolio positions reference `AssetMasterData` entries rather than containing them;
- produce a valid `UniqueID` that links a position to its asset description and defend your choice of generator;
- recognise the common fields that appear on every position, regardless of asset class;
- populate the asset-class-specific fields for equities, bonds, funds, derivatives, cash, and real estate;
- distinguish a derivative's notional from its market value and never again confuse the two;
- compute portfolio breakdowns by sector, country, currency, rating, and maturity from a list of positions, and recognise where breakdowns legitimately differ from a naive recomputation;
- read a complete mixed portfolio of a European equity UCITS on sight and cross-reference every position to its `AssetMasterData` entry.

The chapter is organised into five parts. **Part I** (§6.2 and §6.3) establishes the shape of the problem and the linkage mechanism. **Part II** (§6.4 and §6.5) treats the common fields that appear on every position and every asset. **Part III** (§6.6 through §6.10) walks through the asset classes one at a time, each with its own specialised fields and a small isolated example. **Part IV** (§6.11) covers portfolio breakdowns. **Part V** (§6.12 through §6.14) assembles the complete portfolio of the Europa Growth Fund, lists the common pitfalls, and points at Chapter 7.

---

## 6.2 Portfolios and AssetMasterData — The Shape of the Problem

Before we look at any field, a step back. The portfolio representation in FundsXML is split into two physically separate blocks — `<Portfolios>` inside each fund's `<FundDynamicData>`, and `<AssetMasterData>` at the root of the document — and the split is the first thing a reader of a FundsXML document notices and the first thing that surprises them. Why not put the full asset description inside each position, as simpler formats do? The answer is the working expression of design principle 2 from Chapter 3, and the motivation is worth making concrete.

Imagine a fund administrator's nightly batch file: twenty funds, each with a hundred and fifty positions, all serialised into a single FundsXML document. Many of those positions reference the same instruments. Siemens is held by twelve of the twenty funds; SAP by eight; Nestlé by fifteen; the short list of European blue chips appears in almost every one of them. If the full asset description of Siemens — its name, its LEI, its GICS classification, its primary listing information, its forty or so static fields — were embedded in every position that referenced it, Siemens would be described twelve times in a single file, each time with the same forty fields, each time vulnerable to a transcription or classification mismatch between copies. A producer that rewrites one copy and forgets another creates a file in which two Siemens entries disagree about what Siemens *is*, and every downstream consumer that tries to reconcile them has a data-quality problem.

The solution is the one every relational database uses: describe each instrument *once*, in a central location, and have each position refer to it through an identifier. That central location is `<AssetMasterData>`, and it sits at the root level of the FundsXML document, outside the `<Funds>` container, precisely so that it can be shared between several funds in the same delivery. Each position in each fund's portfolio carries only a short pointer — a `UniqueID` — that tells the consumer where to find the full description. The file is smaller, the descriptions are consistent by construction, and the operational discipline is easier to enforce.

**Figure 6.1 — The portfolio/master-data split**

```
                       <FundsXML4>
                            │
          ┌─────────────────┼─────────────────┐
          │                                   │
       <Funds>                         <AssetMasterData>
          │                                   │
    ┌─────┴─────┐                        ┌────┴────┐
    │           │                        │         │
  <Fund>      <Fund>                   <Asset>   <Asset>
    │           │                        ▲         ▲
  Portfolio   Portfolio                  │         │
    │           │                        │         │
 <Position>──┐  │                        │         │
    │        │  │                        │         │
 <Position>──┼──┼──→ UniqueID reference──┘         │
    │        │  │                                  │
    │        └──┼──→ UniqueID reference────────────┘
    │           │
 <Position>─────┼──→ UniqueID reference (shared across funds)
                │
              (etc.)
```

The figure makes three points. First, both funds in the delivery reach into the same `<AssetMasterData>` block, and a single asset entry can be referenced by positions in several funds simultaneously. Second, the reference is *backward* — from position to asset — not forward; there is no "list of holders" on the asset side. Third, the containment hierarchy inside each fund (Portfolio → Position) and the containment hierarchy inside the root (AssetMasterData → Asset) are parallel, and the `UniqueID` is the only connection between them.

One clarification deserves to be made now, before it becomes a source of confusion later in the chapter: **`AssetMasterData` exists even when the delivery contains a single fund**. The Europa Growth Fund is delivered in its own FundsXML file each month-end, not as part of a twenty-fund batch, and yet every one of its deliveries carries a complete `<AssetMasterData>` block. The reason is not architectural consistency for its own sake; the reason is that the separation keeps positions slim. A Siemens position in the Europa Growth Fund's portfolio contains eight or nine fields (the `UniqueID` reference, the valuation currency, the single `TotalValue` in fund currency, the percentage weight, the price date, plus the equity-specific sub-block carrying the unit count, the price and the market value); the Siemens description in `AssetMasterData` contains forty or more fields covering identifiers, issuer, listing, classifications, ratings, and country-specific extensions. If the two were merged, a portfolio of 150 positions would carry 150 × 40 = 6,000 fields of description when 150 × 9 + 150 × 40 (one description per distinct asset, which, with overlap across funds, is often much smaller) would suffice. Even for a single fund, the separation is operationally meaningful.

Two architectural observations close this section. `<Portfolios>` lives inside `<FundDynamicData>` — it belongs to a specific valuation date and is re-emitted whenever a new portfolio snapshot is produced. `<AssetMasterData>` lives at the root level and applies to the entire delivery. The first is *dynamic* in the sense that its content changes every valuation day; the second is closer to *static*, even though in practice it also evolves as new instruments enter the fund's universe. Finally, **the two structures must be read together**. A portfolio position without its corresponding asset entry is meaningless; an asset entry with no position pointing at it is dead weight. The schema enforces the first half of this discipline directly at parse time — the `<UniqueID>` on each `<Asset>` is declared as `xs:ID` and the `<UniqueID>` on each `<Position>` as `xs:IDREF`, which means a position whose identifier does not match any asset is rejected by any conformant XML parser before any business-level validation even begins. The second half — orphaned asset entries — is not enforced by the schema and shows up only as a data-quality issue. Chapter 10 will formalise both halves as business-validation rules; for this chapter it is enough to carry the pairing in mind at every step.

---

## 6.3 The UniqueID Linkage in Detail

The `UniqueID` is the small glue that binds the two sides together. We treat it in three short subsections.

### 6.3.1 What a UniqueID Is

A `UniqueID` is a string, typically twenty to forty characters, that uniquely identifies each `<Asset>` entry inside `<AssetMasterData>` *within a single FundsXML delivery*. The schema does not declare it as a plain string — it declares it as `xs:ID` on the asset side and `xs:IDREF` on the position side. The practical consequence is twofold. First, the parser checks at load time that every position's `UniqueID` resolves to exactly one asset entry's `UniqueID`, and a mismatch is a schema-validation error rather than a business-rule error. Second, the value must conform to the XML Name syntax: it must begin with a letter or underscore, must not contain whitespace, and must be unique across the whole document. ISINs such as `DE0007236101` satisfy the syntax because they begin with a letter; purely numeric codes such as a raw five-digit internal reference would not, and producers using numeric internal codes typically prefix them with a letter (`EGF-12345`) to make them valid XML names.

The scope of uniqueness is important: unlike the `UniqueDocumentID` of Chapter 4, which must be unique across every delivery a producer has ever emitted, the `UniqueID` of an asset need only be unique within the file in which it appears. Two deliveries from the same producer may carry different `UniqueID` values for the same Siemens entry without violating anything, as long as each file is internally consistent. In practice, producers that care about cross-delivery consistency pick a generator that is stable over time (see §6.3.2), but this is a convention, not a schema requirement.

### 6.3.2 How to Generate a UniqueID

Two strategies dominate production usage, and each has its own strengths.

The first strategy is **to use the instrument's ISIN as its `UniqueID`**. The ISIN is already globally unique in the instrument universe, is already present on almost every asset the fund is likely to hold, and is human-readable enough that a debugger looking at a portfolio dump recognises each line at a glance. A position that references `DE0007236101` and an asset entry with `UniqueID=DE0007236101` are visibly the same instrument; no translation is required. The strategy is so natural that it is the default in most production pipelines.

The weakness of the ISIN strategy is that not every asset has an ISIN. Cash positions do not; over-the-counter derivatives do not; direct real estate holdings do not; some exotic private-equity commitments do not. For these assets, the producer needs a fallback, and that fallback is usually a UUID: a one hundred and twenty-eight-bit random or deterministically-derived identifier, long enough that collisions across producers are astronomically unlikely. The weakness of a UUID is the loss of readability; a debugger sees `7f8e3a2d-...` instead of a meaningful name and must perform a mental lookup.

The recommended convention, which Chapter 13 will formalise as a project-level decision, is a hybrid: **ISIN when the asset has one, UUID when it does not, and the choice must be deterministic across deliveries**. Deterministic means that the same Siemens asset, generated by the same producer on a different day, receives the same `UniqueID`. For ISIN-bearing assets this is automatic; for UUID-generated assets it requires a UUID v5 (name-based) computed from a stable internal identifier rather than a fresh random v4 on every run. A producer that emits fresh UUIDs every day makes it impossible for consumers to reconcile the same instrument across consecutive deliveries, which is not quite a correctness problem but is a significant operational nuisance.

### 6.3.3 The Linkage Mechanism in Action

A concrete pair of elements makes the linkage visible. The Europa Growth Fund holds 50,000 shares of Siemens AG. In the portfolio block, inside `Fund/FundDynamicData/Portfolios/Portfolio/Positions`, the position looks like this:

```xml
<Position>
  <UniqueID>DE0007236101</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">8125000.00</Amount>
  </TotalValue>
  <TotalPercentage>1.75</TotalPercentage>
  <PriceDate>2026-03-31</PriceDate>
  <Equity>
    <Units>50000</Units>
    <Price><Amount ccy="EUR">162.50</Amount></Price>
    <MarketValue>
      <Amount ccy="EUR" isFundCcy="true">8125000.00</Amount>
    </MarketValue>
  </Equity>
</Position>
```

Elsewhere in the same document, inside the root-level `<AssetMasterData>`, the corresponding asset entry carries the matching `UniqueID` and the full instrument description:

```xml
<Asset>
  <UniqueID>DE0007236101</UniqueID>
  <Identifiers>
    <ISIN>DE0007236101</ISIN>
  </Identifiers>
  <Currency>EUR</Currency>
  <Country>DE</Country>
  <Name>Siemens AG</Name>
  <AssetType>EQ</AssetType>
  <AssetDetails>
    <Equity>
      <StockMarket>XETR</StockMarket>
      <Issuer>
        <Identifiers>
          <LEI>W38RGI023J3WT1HWRP32</LEI>
        </Identifiers>
        <Name>Siemens Aktiengesellschaft</Name>
        <BusinessCountry>DE</BusinessCountry>
        <Type>Non-financial corporations</Type>
      </Issuer>
      <Listing>A</Listing>
    </Equity>
  </AssetDetails>
</Asset>
```

Four structural points about this pair are worth stating before we look at any single field. First, the position has a mandatory `<TotalValue>` (typed `FundAmountType`) that carries the consolidated value of the whole position in the fund's base currency. This is the one number against which the sum of all positions must reconcile to the fund's total net assets; the detail fields inside the asset-class-specific `<Equity>` child are there for transparency, not to replace the total. Second, the asset-class-specific child — here `<Equity>` — is one of a choice of twenty-one variants: `Equity`, `Bond`, `ShareClass`, `Warrant`, `Certificate`, `Option`, `Future`, `FXForward`, `Swap`, `Repo`, `FixedTimeDeposit`, `CallMoney`, `Account`, `Fee`, `RealEstate`, `REIT`, `Loan`, `Right`, `Commodity`, `PrivateEquity`, and `CommercialPaper`. Exactly one child of the choice is required at the end of every position. (The asset-master side of the linkage — `AssetDetails` — has two additional choice members, `Index` and `Crypto`, because the schema allows those instruments to be described as assets but not to be held as portfolio positions. §6.5 returns to this asymmetry.) Third, the asset side uses `<AssetType>` as a two-character discriminator code — `EQ` for Equity, `BO` for Bond, `SC` for fund share class, `FX` for FX forward, `AC` for account, and so on — and the asset's detailed fields live inside a separate `<AssetDetails>` child whose content mirrors the position-side choice by element name. Fourth, the `ISIN` lives inside `<Identifiers>`, not as a direct child of `<Asset>`; the container takes exactly the same shape as the fund-level and share-class-level `<Identifiers>` blocks of Chapter 5.

A consumer that reads the position finds `DE0007236101` in the `UniqueID` field, jumps to the `<AssetMasterData>` block, finds the matching `<Asset>` entry, and now knows everything it needs to know about Siemens as an instrument. It does this lookup once per distinct asset per delivery, caches the results in memory, and processes the whole portfolio without ever re-parsing the asset descriptions. The cost is linear in the number of distinct instruments, not in the number of position-instrument references.

**The key rule**: consumers never read `Portfolio` and `AssetMasterData` in isolation. Both structures together form the complete information about what the fund holds. A production pipeline that parses only one of the two is fundamentally broken, and any validation discipline (Chapter 10) treats the pair as atomic.

Two validation rules flow directly from the linkage. First, **every `UniqueID` in a `Position` must match exactly one `<Asset>` in `AssetMasterData`**. As we saw in §6.3.1, the schema enforces this at the parser level through its `xs:ID`/`xs:IDREF` pairing; a position whose `UniqueID` has no target is a schema-validation failure, not a business-rule failure, and the document does not load at all. Second, **every `<Asset>` in `AssetMasterData` should be referenced by at least one `Position`**. An orphaned asset entry is harmless from a consumer's perspective but is almost always a sign of a sloppy producer — typically the residue of a position that was deleted from the producer's database without a corresponding cleanup of the asset master. Chapter 10 lists this rule among the business-validation checks that a production consumer pipeline should run on every incoming file.

---

## 6.4 Position-Level Fields

We now descend into the fields. The common position-level fields, which appear on every [`<Position>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions/Position) element regardless of what asset class the position belongs to, are the subject of this section. Asset-class-specific extras come later in Part III.

Table 6.1 lists the common children of `<Position>` in the order they must appear.

**Table 6.1 — Common children of `<Position>`**

| Child element | Schema type | Purpose | Example value |
|---|---|---|---|
| `<UniqueID>` | `xs:IDREF` (max 256 chars) | Reference to the matching `<Asset>` in `<AssetMasterData>` | `DE0007236101` |
| `<Identifiers>` | `IdentifiersType` | Optional copy of key instrument codes — redundant with the asset's own `Identifiers`, present in some pipelines for debugging | — |
| `<Currency>` | `ISOCurrencyCodeType` | Valuation currency of the instrument (its native trading currency, not the fund's base currency) | `EUR` |
| `<TotalValue>` | `FundAmountType` | The consolidated value of the whole position, in the fund's base currency. **Mandatory.** | `<Amount ccy="EUR">8125000.00</Amount>` |
| `<OtherTotalValues>` | container | Additional valuations (Hold-To-Maturity, Swing-adjusted, Market, …) | — |
| `<TotalPercentage>` | `PercentageType` | The position's weight in the fund, as a percentage of total net assets | `1.75` |
| `<AveragePurchasePrice>` | `FundAmountType` | The weighted-average cost basis of the position across all buys | — |
| `<AveragePurchaseFXRate>` | `FXRatesType` | The weighted-average FX rate at which the position was entered | — |
| `<Exposures>` | `ExposureType` | Exposure values under different regulatory approaches (commitment, AIFMD) | — |
| `<FXRates>` | `FXRatesType` | FX rates used in evaluating this position | — |
| `<PriceDate>` | `xs:date` | The date of the price used for this valuation | `2026-03-31` |
| `<PricingSource>` | choice(`Listed`/`Unlisted`) | Pricing source — either a listed enumeration (`BLOOMBERG`, `REUTERS`, `FACTSET`, `MARKIT`, `BARCLAYS`, `JPMORGAN`, `MERRILL`, `BROKERS`, `LPC`, `NTRS`) or free text | `BLOOMBERG` |
| *asset-class choice* | — | Exactly one of `<Equity>`, `<Bond>`, `<ShareClass>`, `<Warrant>`, `<Certificate>`, `<Option>`, `<Future>`, `<FXForward>`, `<Swap>`, `<Repo>`, `<FixedTimeDeposit>`, `<CallMoney>`, `<Account>`, `<Fee>`, `<RealEstate>`, `<REIT>`, `<Loan>`, `<Right>`, `<Commodity>`, `<PrivateEquity>` or `<CommercialPaper>` — **mandatory, exactly one** | see Part III |
| `<CapitalYieldsTaxClaim>` | container | Tax-accrual details at the position level — rarely populated for non-German funds | — |
| `<InflationaryAdjustment>` | container | Inflation-linked adjustment fields for index-linked instruments | — |
| `<RiskCodes>` | list | Risk indicator values attached to this individual position | — |
| `<Underlyings>` | list | Underlying-instrument references for derivatives and structured products | — |
| `<CustomAttributes>` | `AttributesType` | Producer-specific extensions | — |

All children except `<UniqueID>`, `<TotalValue>`, and the asset-class choice are optional. The three mandatory members carry all the work of position identity, valuation, and asset-class branching, and everything above and below them in the table is supporting detail that producers populate when it matters.

Note on vocabulary: there is **no** `<Quantity>` element anywhere on `<Position>` and no `<PositionType>` element distinguishing long from short. The schema element named `<Position>` is of schema type `PositionType` — the latter being the name of the complex type in the XSD, not a tag name that ever appears in a FundsXML document. The word "quantity" in the prose that follows always refers to the generic concept of "how many of the instrument does the fund hold"; the actual XML tag depends on the asset class and takes its name from the specific choice child (`<Units>`, `<Nominal>`, `<Shares>`, `<Contracts>`).

Four points about the table deserve to be emphasised in plain text rather than left implicit.

**`<TotalValue>` is mandatory on every position and is the one figure that reconciles against the fund total net assets from Chapter 5.** A `<Position>` element with no `<TotalValue>` is a schema-validation failure; a `<Position>` whose `<TotalValue>` does not match the fund's `<TotalNetAssetValue>` when summed across all positions is a business-validation failure. The consolidated total lives on the position, not on the asset-class-specific child, because the producer is the authoritative source for how the position rolls up into the fund currency and any downstream consumer should accept that roll-up without recomputing.

**The asset-class-specific child is mandatory and the schema offers twenty-one variants.** Every `<Position>` must end with exactly one of `<Equity>`, `<Bond>`, `<ShareClass>`, `<Warrant>`, `<Certificate>`, `<Option>`, `<Future>`, `<FXForward>`, `<Swap>`, `<Repo>`, `<FixedTimeDeposit>`, `<CallMoney>`, `<Account>`, `<Fee>`, `<RealEstate>`, `<REIT>`, `<Loan>`, `<Right>`, `<Commodity>`, `<PrivateEquity>` or `<CommercialPaper>`. This is where the per-class unit count, the per-unit price, and the detail fields live — *not* at the top of the position. An equity's `<Units>` field, for example, is a child of `<Equity>`, not of `<Position>`. A bond's `<Nominal>` field is a child of `<Bond>`. A cash account's balance lives in `<Account>/<MarketValue>`. The rule is strict and it organises everything that follows in Part III. (Producers describing an index or a crypto asset populate `AssetType=IX` or `AssetType=CR` on the asset-master side, but no corresponding choice exists on the position side; a fund holding such instruments emits them as `<Equity>` or `<CommercialPaper>` positions, depending on the operational convention.)

**The concept of "quantity" does not correspond to a single schema element.** Different asset classes describe their unit count with different tag names, each living inside the asset-class choice child:

- For an equity, `<Equity>/<Units>` carries the number of shares held.
- For a bond, `<Bond>/<Nominal>` carries the nominal value in the issue currency. A `<Nominal>1000000</Nominal>` means one million euros face value of bonds, which might be a single bond certificate or a thousand of them depending on the issue's denomination.
- For a fund held as a position, `<ShareClass>/<Shares>` carries the number of fund units.
- For an option or a future, `<Option>/<Contracts>` (respectively `<Future>/<Contracts>`) carries the number of contracts, and the value may be negative to indicate a short position — **FundsXML has no separate long/short flag**. The same applies to `<Swap>` legs.
- For cash accounts there is no unit count at all, because an account balance is already a total value carried in `<Account>/<MarketValue>`.

Section 6.7 will return to the bond case, which is the one that most frequently trips up implementers. The rule to remember is that each asset class has its own idiom and the element name is chosen to reflect it; **no element called `<Quantity>` exists anywhere in the schema**, and a producer writing `<Quantity>` will fail schema validation.

**`<Amount>` elements always carry a `ccy` attribute.** The FundsXML `<Amount>` element — whether inside `<TotalValue>`, `<Price>`, `<MarketValue>`, `<AveragePurchasePrice>`, or any other amount-bearing field — names its currency explicitly. In addition, optional boolean attributes `isFundCcy`, `isSubfundCcy`, and `isShareClassCcy` let the producer flag which amount is the fund-base, sub-fund, or share-class currency when several are present. A position holding Swiss Nestlé shares may therefore carry its `<TotalValue>` with two `<Amount>` entries — one `ccy="EUR" isFundCcy="true"` for the fund-base figure, and one `ccy="CHF"` for the native currency figure — both describing the same economic value at different FX rates. A consumer that ignores the `ccy` attribute and assumes "everything in the fund's base currency" will misread the Swiss position's native amount and the error will propagate into any downstream calculation.

One final remark before moving to the asset side. Every asset-class-specific field (coupon rate on a bond, strike on an option, counterparty LEI on a cash position) lives **inside the asset-class child**, not as a direct sibling of `<UniqueID>` or `<TotalValue>`. A bond position has `<TotalValue>` *and* a `<Bond>` sub-block containing `<Nominal>`, `<Price>`, `<DirtyPrice>`, `<MarketValue>`, `<InterestClaimGross>`, `<AccruedInterestDays>`, and so on. A cash account position has `<TotalValue>` *and* an `<Account>` sub-block containing `<MarketValue>` and `<Interests>`. The asset-class sections in Part III walk through each sub-block in detail; Table 6.1 is the contract for everything *outside* them.

---

## 6.5 Asset-Level Fields in AssetMasterData

Symmetrical to §6.4, but from the other side of the linkage: the fields that appear on every `<Asset>` entry in `<AssetMasterData>` regardless of asset class. The division of labour between position and asset is straightforward: **the position answers the question "how much?", the asset answers the question "what is it?"**

Table 6.2 lists the common asset-level fields and their schema types, in the exact order in which they must appear inside `<Asset>`.

**Table 6.2 — Common asset-level fields (schema type `AssetType`)**

| Field | Schema type | Mandatory | Purpose |
|---|---|---|---|
| `UniqueID` | `xs:ID` | yes | Globally unique identifier within the delivery; target of `Position/UniqueID` |
| `Identifiers` | `IdentifiersType` | no | ISIN, LEI, GermanWKN, SwissValorenCode, CUSIP, SEDOL, Bloomberg, ReutersRIC, OtherID |
| `DataSupplier` | `DataSupplierType` | no | Producer of this asset record (usually inherited from `ControlData`) |
| `Currency` | `ISOCurrencyCodeType` | **yes** | Nominal currency of the instrument (three-letter ISO 4217 code) |
| `IncomeCurrency` | `ISOCurrencyCodeType` | no | Currency in which the instrument's income is paid, if different |
| `Country` | `ISOCountryCodeType` | no | Country of issue (*Emissionsland*) |
| `Name` | `Text256Type` | **yes** | Human-readable instrument name |
| `FISN` | `xs:string` (128) | no | ISO 18774 Financial Instrument Short Name |
| `AssetType` | enum (2 chars) | **yes** | Discriminator: `EQ`/`BO`/`SC`/`WA`/`CE`/`OP`/`FU`/`FX`/`SW`/`RP`/`FT`/`CM`/`AC`/`FE`/`RE`/`RT`/`LO`/`RI`/`CO`/`PE`/`CP`/`IX`/`CR` |
| `AssetDetails` | `AssetDetailsType` | no | A choice of 23 inline types carrying the asset-class-specific fields |
| `CountrySpecificData` | container | no | National reporting extensions (AT, DE, DK, FR, LU, NL) |
| `Securitized` | `xs:boolean` | no | Whether the asset is securitised |
| `IsInfrastructureInvestment` | `xs:boolean` | no | Infrastructure investment flag |
| `InfrastructureInvestmentType` | enum | no | Infrastructure category |
| `Ratings` | `RatingsType` | no | Credit ratings from agencies (one entry per agency) |
| `RealEstateCompany` | `CompanyType` | no | Corresponding real-estate company (for direct property holdings) |
| `Classifications` | `ClassificationsType` | no | Sector/industry/style classifications, same structure as in Chapter 5 |
| `CustomAttributes` | `AttributesType` | no | Producer-specific extensions |

Four points about the table deserve to be emphasised in plain text.

**The `AssetType` element is a two-character code, not an English word.** The values are `EQ` for equity, `BO` for bond, `SC` for fund share class, `WA` for warrant, `CE` for certificate, `OP` for option, `FU` for future, `FX` for FX forward, `SW` for swap, `RP` for repo, `FT` for fixed-time deposit, `CM` for call money, `AC` for account, `FE` for fee, `RE` for real estate, `RT` for REIT, `LO` for loan, `RI` for right, `CO` for commodity, `PE` for private equity, `CP` for commercial paper, `IX` for index, `CR` for crypto. These are the operational codes used by fund accounting systems across Europe, and producers coming from such systems usually have the mapping built in already. A consumer that reads `AssetType` branches its parser on the two-letter code, loads the corresponding `AssetDetails` child, and applies the asset-class-specific logic. There is no enumeration with English labels anywhere in the schema.

**The ISIN is not a direct child of `<Asset>`.** The ISIN lives inside `<Identifiers>`, the same container we met at the fund and share-class level in Chapter 5. So does the LEI (used for issuers, not for the asset itself), the GermanWKN, the SwissValorenCode, and every other instrument code. A typical equity asset entry begins with `<UniqueID>`, then `<Identifiers><ISIN>...</ISIN><GermanWKN>...</GermanWKN></Identifiers>`, then `<Currency>`, then `<Country>`, then `<Name>`, then `<AssetType>`, then `<AssetDetails>`. Producers that write the ISIN as a top-level child will fail schema validation.

**`AssetDetails` is the home of asset-class-specific fields, not a collection of siblings of `<Asset>`.** Everything that distinguishes an equity from a bond — the issuer block, the stock market, the coupon, the maturity, the strike, the counterparty of a forward, the counterparty of a cash account — lives one level below, inside an `<AssetDetails>` child whose content is exactly one of twenty-three sub-elements (`Equity`, `Bond`, `ShareClass`, `Warrant`, `Certificate`, `Option`, `Future`, `FXForward`, `Swap`, `Repo`, `FixedTimeDeposit`, `CallMoney`, `Account`, `Fee`, `RealEstate`, `REIT`, `Loan`, `Right`, `Commodity`, `PrivateEquity`, `CommercialPaper`, `Index`, `Crypto`). The element names match the ones on the position-side choice of §6.4 deliberately, so that the discriminator on both sides is the same word, not a mapping a consumer has to learn.

**Issuer and instrument are distinct, and the schema respects that distinction.** An asset entry has two identity layers. The *instrument* is the tradable unit — a specific equity share class, a specific bond issue, a specific derivative contract — and it is identified at the top of `<Asset>` by its own `<Identifiers>` block, whose `<ISIN>` (or `<UniqueID>`, for instruments without an ISIN) is the primary key. The *issuer* is the legal entity that issued the instrument — and it is identified by a separate `<Issuer>` block of schema type `CompanyType` that lives **inside** `AssetDetails/<Equity>` or `AssetDetails/<Bond>`. `CompanyType` carries its own `<Identifiers>` container with the issuer's LEI, a mandatory `<Name>`, optional `<LegalName>`, `<LegalForm>`, `<Address>`, `<BusinessCountry>`, `<ParentCompany>` for corporate hierarchies, an `<OtherClassification>` container, and a `<Type>` enumeration covering the ECB sector categories (`Non-financial corporations`, `Central bank`, `Deposit-taking corporations except the central bank`, `General government`, `Insurance corporations`, `Pension funds`, `Money market funds`, `Non-MMF investment funds`, and five others). For equities the instrument-issuer relationship is typically one-to-one: the Siemens AG legal entity has one LEI, and `DE0007236101` is the ordinary common stock of that entity. For bonds the relationship is one-issuer-to-many-instruments: the Federal Republic of Germany has one LEI but hundreds of bund series, each with its own ISIN, all backed by the same `<Issuer>` block carrying the Federal Republic's LEI and `Type="General government"`. Section 6.7 returns to this point in the context of bond-specific fields.

All asset-class-specific fields — the strike of an option, the maturity of a bond, the counterparty of a forward — live *inside `<AssetDetails>`* below the common fields of Table 6.2. The five sections that follow treat them one asset class at a time.

---

## 6.6 Equities

The primary case for the Europa Growth Fund. Three subsections.

### 6.6.1 The Equity Asset Model

An equity asset entry in `AssetMasterData` describes a tradable share class of a public company. Its structure has two layers: the generic asset-level fields of Table 6.2, populated with `AssetType=EQ`, followed by an `AssetDetails/Equity` child whose content follows the schema type `EquityType`. The generic fields carry identity and classification; the equity-specific fields carry listing, issuer, and equity-specific metadata.

**Identifiers** live inside the top-level `<Identifiers>` block of Table 6.2, not inside `<Equity>`. The primary identifier is the ISIN, twelve characters, ISO 6166. For securities that also trade in non-ISIN-using markets, FundsXML carries additional identifier fields in the same container: `SEDOL` for UK listings, `CUSIP` for North-American instruments, and `GermanWKN` for German securities. Bloomberg tickers and Reuters RICs have their own dedicated fields (`Bloomberg` with `Ticker`, `Exchange`, `Market`, `BBGID` sub-children; `ReutersRIC` with a `type` attribute).

**Inside `<Equity>`**, the schema type `EquityType` (XSD §25059) carries the following children in order:

- `ClassOfBusiness` — a structured `IndustryProviderType` block with `Offeror`, `Date`, `Value`, and optional `Text`, naming the sector classification provider (e.g. *Bloomberg*, *GICS*) and the value.
- `StockMarket` — one or more `MICCodeType` values (ISO 10383 four-character market identifier codes) naming the exchanges on which the equity is listed. `XETR` for Xetra, `XPAR` for Euronext Paris, `XVTX` for SIX Swiss Exchange, `XAMS` for Euronext Amsterdam, `XLON` for the London Stock Exchange, `XMAD` for Bolsa de Madrid. The element repeats for multi-listed stocks.
- `Issuer` — a structured `CompanyType` block identifying the issuing legal entity: `<Identifiers>` with the issuer's LEI, a mandatory `<Name>`, an optional `<LegalForm>`, an optional `<BusinessCountry>`, and an optional `<Type>` from the ECB sector enumeration.
- `Listing` — an enumeration `A`/`B`/`G`/`K`/`M`/`S`/`V`/`Y`/`Z` indicating the kind of exchange listing. `A` (official market) is the ordinary case for blue-chip European stocks; `K` means *not listed*, used for private or unlisted issues.
- `ParValue` — the nominal value of the share in the instrument's currency (often 1.00 for modern no-par-value shares).
- `WithholdingTaxRate` — the producer's default withholding tax rate on dividends from this instrument.
- `MarketCapitalization` — a `Date`/`Value` pair carrying the full market capitalisation of the issuer as at that date.
- `CustomMarketCapitalization` — a `Name`/`Date`/`Value` triple where `Name` is drawn from the enumeration `Small Cap`, `Small & Mid Cap`, `Mid Cap`, `Mid & Large Cap`, `Large Cap`, `All Cap`, `Other`. This is the field a factsheet engine reads when it needs a size bucket.
- `Industries` — a container for one or more `IndustryCode` entries, each with `Name` (the classification scheme, e.g. `GICS`), `Date`, and `Value` (the numeric or textual code within that scheme).

**Classification through `AssetType/Classifications`.** The generic-asset `<Classifications>` block from Table 6.2 is the more idiomatic place to carry sector-classification values for downstream consumers. Following the same pattern as in Chapter 5, each `<Classification>` entry names a provider via `<ListedGroup>` (`EFAMA`, `MORNINGSTAR`, `LIPPER`, `BLOOMBERG`, `MIFID`, `BVI`, `VOEIG`, `ESMA`, `AMF`, `WM`, `CIC`, `CFI`) or `<UnlistedGroup>` (free text, used for `GICS` and `ICB` which are not in the enumeration) and supplies one or more `<Value>` elements with optional `level` attributes for hierarchies. The `<Industries>` and `<ClassOfBusiness>` fields inside `<Equity>` are historical and mostly populated by legacy fund-accounting systems; modern producers prefer `<Classifications>`.

**Table 6.3 — Equity-specific fields inside `AssetDetails/Equity` (schema type `EquityType`)**

| Field | Schema type | Example | Mandatory |
|---|---|---|---|
| `ClassOfBusiness` | `IndustryProviderType` | Offeror=*Bloomberg*, Value=*BICS* | optional |
| `StockMarket` | `MICCodeType` (repeats) | `XETR` | optional |
| `Issuer` | `CompanyType` | see text above | optional |
| `Listing` | enum `A`/`B`/`G`/`K`/`M`/`S`/`V`/`Y`/`Z` | `A` | optional |
| `ParValue` | `xs:decimal` | `1.00` | optional |
| `WithholdingTaxRate` | `xs:decimal` | `26.375` | optional |
| `MarketCapitalization` | Date + Value | *2026-03-31*, 145 bn | optional |
| `CustomMarketCapitalization` | Name enum + Date + Value | `Large Cap` | optional |
| `Industries` | list of `IndustryCode` | GICS 20106010 | optional |

All equity-level fields are optional; an `<Equity>` element with no children at all is schema-valid (an empty but schema-valid element). In practice, producers populate `Issuer`, `StockMarket`, and at least one classification entry for every equity in the portfolio; the rest depend on the producer's downstream consumers.

### 6.6.2 Position-Level Fields Specific to Equities

At the position level, an equity entry ends with an `<Equity>` child (defined inline as an anonymous complex type within `<Position>`, XSD §28571) whose mandatory first child is `<Units>`. Its sequence is:

- `<Units>` (mandatory, `xs:decimal`) — the number of shares the fund holds. Almost always a whole number for traditional long-only UCITS; fractional shares exist in a few specialised vehicles (robo-advisors offering fractional investment, some unit-linked wrappers) but do not appear in the Europa Growth Fund or in most European institutional portfolios.
- `<Price>` (optional, `FundAmountType`) — the last available quote, in the listing currency, typically the closing price on the valuation date at the primary listing. If the stock was suspended for the day, the price holds at the last valid quote and the position's `<PriceDate>` (inside the parent `<Position>`) reflects the age of the quote.
- `<OtherPrices>` (optional) — additional prices (hold-to-maturity-style alternatives, rarely used for equities).
- `<MarketValue>` (optional, `FundAmountType`) — `Units × Price`, converted into the fund's base currency if the listing currency differs. The conversion rate is the producer's reference rate at the valuation point.
- `<BookRate>` (optional, `FundAmountType`) — the book value used for capital-gains accounting.
- `<PurchaseValue>` (optional, `FundAmountType`) — the historical cost of the position.
- `<DividendsDue>` (optional, `FundAmountType`) — the dividend income that has accrued between the last ex-dividend date and the valuation date but has not yet been paid out. Most producers do not populate it; they treat dividends as discrete events that flow through `Distributions` on the share class (Chapter 7) rather than accruing into the equity position.
- `<LendedFlag>` (optional, `xs:boolean`) — whether part of the position is out on loan to a counterparty.
- `<LendedUnits>` (optional, `xs:decimal`) — the number of shares out on loan.
- `<IndicatorRaffled>` (optional, `xs:boolean`) — whether the security has been drawn by lot in a corporate action.

Note what is **not** a child of `<Equity>` but lives one level up on `<Position>`: `TotalValue`, `TotalPercentage`, `Currency`, `PriceDate`, `PricingSource`. Those are position-level concerns and are common to every asset class. A producer that writes `<TotalValue>` as a sibling of `<Units>` inside `<Equity>` is wrong; the field must appear at `<Position>` level.

### 6.6.3 Equity Example: A Siemens Position

A complete pair — position and asset entry — for the Europa Growth Fund's Siemens holding on 31 March 2026.

```xml
<!-- Inside Fund/FundDynamicData/Portfolios/Portfolio/Positions -->
<Position>
  <UniqueID>DE0007236101</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">8125000.00</Amount>
  </TotalValue>
  <TotalPercentage>1.75</TotalPercentage>
  <PriceDate>2026-03-31</PriceDate>
  <Equity>
    <Units>50000</Units>
    <Price>
      <Amount ccy="EUR">162.50</Amount>
    </Price>
    <MarketValue>
      <Amount ccy="EUR" isFundCcy="true">8125000.00</Amount>
    </MarketValue>
  </Equity>
</Position>

<!-- Elsewhere, inside the root AssetMasterData block -->
<Asset>
  <UniqueID>DE0007236101</UniqueID>
  <Identifiers>
    <ISIN>DE0007236101</ISIN>
    <GermanWKN>723610</GermanWKN>
  </Identifiers>
  <Currency>EUR</Currency>
  <Country>DE</Country>
  <Name>Siemens AG</Name>
  <AssetType>EQ</AssetType>
  <AssetDetails>
    <Equity>
      <StockMarket>XETR</StockMarket>
      <Issuer>
        <Identifiers>
          <LEI>W38RGI023J3WT1HWRP32</LEI>
        </Identifiers>
        <Name>Siemens Aktiengesellschaft</Name>
        <BusinessCountry>DE</BusinessCountry>
        <Type>Non-financial corporations</Type>
      </Issuer>
      <Listing>A</Listing>
      <CustomMarketCapitalization>
        <Name>Large Cap</Name>
        <Date>2026-03-31</Date>
        <Value>145000000000</Value>
      </CustomMarketCapitalization>
      <Industries>
        <IndustryCode>
          <Name>GICS</Name>
          <Date>2026-03-31</Date>
          <Value>20106010</Value>
        </IndustryCode>
      </Industries>
    </Equity>
  </AssetDetails>
  <Classifications>
    <Classification>
      <UnlistedGroup>GICS</UnlistedGroup>
      <Type>Sector</Type>
      <Language>en</Language>
      <Value level="1">Industrials</Value>
      <Value level="2">Industrial Conglomerates</Value>
    </Classification>
  </Classifications>
</Asset>
```

Reading field by field: the position's `<UniqueID>` is the ISIN, following the convention of §6.3.2 (and satisfying the `xs:ID` constraint because `DE0007236101` begins with a letter). The consolidated `<TotalValue>` is 8.125 million euros — approximately 1.75% of the fund's total net assets from Chapter 5 — and lives in the fund's base currency, flagged `isFundCcy="true"`. Inside `<Equity>`, the position says the fund holds 50,000 Siemens shares, last priced at 162.50 EUR at Xetra's close on 31 March 2026, with a market value equal to `Units × Price` also in euros.

The asset entry confirms the instrument identity. `<Identifiers>` carries the ISIN and the six-character German WKN (723610, the historical code that German retail systems still use alongside the ISIN). The top-level `<Currency>` names the instrument's nominal currency (EUR) and `<Country>` names the country of issue (DE). `<AssetType>EQ</AssetType>` signals the asset-class to consumers. Inside `<AssetDetails>/<Equity>`, the listing information — Xetra (`XETR`) as the stock market, `A` (official market) as the listing category — sits above the issuer block. The issuer block is a full `<Issuer>` element of schema type `CompanyType`, with Siemens AG's LEI (20 characters, ISO 17442), a mandatory name, a business country, and an ECB-sector classification of `Non-financial corporations`. A `<CustomMarketCapitalization>` entry places Siemens in the `Large Cap` bucket as at 31 March 2026 with a rounded-EUR figure, and an `<Industries>` entry carries the GICS industry code 20106010 (Industrial Conglomerates) for downstream consumers that speak that taxonomy.

The top-level `<Classifications>` block — sibling of `<AssetDetails>` — duplicates the GICS classification in the idiomatic form that the rest of the book uses: an `<UnlistedGroup>GICS</UnlistedGroup>` (because `GICS` is not a listed provider in the schema's enumeration), a `<Type>Sector</Type>`, a `<Language>en</Language>`, and two `<Value>` elements with `level` attributes walking the hierarchy from Industrials down to Industrial Conglomerates. A consumer that reads this block picks whichever scheme it recognises.

A consumer that produces a factsheet for the fund renders Siemens as "Siemens AG, 1.75%, Industrials, Germany" using five or six of the visible fields. A consumer that produces a regulatory report reads the LEI and the GICS code for their respective disclosures. The same pair serves every downstream use case without any additional data.

This pair is the template that §6.12 will repeat fifteen times with different companies, sectors, and countries. The fields are always the same; the values vary.

---

## 6.7 Bonds

The Europa Growth Fund holds no bonds, but any treatment of FundsXML portfolios must cover them because bonds are structurally the most different asset class from equities and because most European fund portfolios outside pure equity mandates contain at least some. The example in this section comes from a generic European bond fund rather than from the Europa Growth Fund.

Bonds are more complex than equities for one overriding reason: a bond carries two identities rather than one. The *instrument* is a specific bond issue with a specific maturity and coupon; the *issuer* is the legal entity that issued it. Where an equity share class is in one-to-one correspondence with its issuer's LEI, a single issuer may have issued dozens or hundreds of distinct bonds, each with its own ISIN and its own behaviour, all backed by the same credit. The bond asset model must represent both layers.

### 6.7.1 The Bond Asset Model

An `<Asset>` entry for a bond carries `AssetType=BO`, and its bond-specific details live inside `<AssetDetails>/<Bond>` (schema type `BondType`, XSD §2012). The type is large — thirty or more optional children — and the sequence below lists only the fields that matter for a typical European fund portfolio.

**Convertible flag.** The one *mandatory* child of `BondType` is `<ConvertibleFlag>` (`xs:boolean`). Every bond must state whether it carries equity conversion rights, even if the answer is trivially *false* for a straight government bond. Convertible bonds have an additional `<ConvertibleBond>` sub-block with strike and conversion ratio details.

**Issuer.** A structured `CompanyType` block identifying the issuing legal entity — the same type we saw for equities in §6.6.1, but the issuer for a bond is almost always populated more richly because rating agencies, regulatory reporting, and concentration limits all hang on it. `Issuer/Identifiers/LEI` is the single most important field on the whole entry.

**Listing.** `<StockMarket>` (repeatable MIC codes) and `<Listing>` (the same A/B/G/K/M/S/V/Y/Z enumeration as for equities) identify the exchanges on which the bond trades. A `<ListingUnit>` field, unique to bonds, distinguishes `P` (pieces — bonds denominated in whole certificates) from `N` (nominal amount — the more common case in Europe). For a typical German bund, `ListingUnit=N`.

**Maturity and key dates.**

- `IssueDate` — the date the bond was originally issued.
- `MaturityDate` — the date on which the principal is repaid to investors.
- `DateFirstCoupon` and `DateLastCoupon` — the boundary coupon dates.
- `CouponDate` — the next scheduled coupon payment.

**Coupon.** The cash flow the bond pays to investors during its life is carried inside a `<Coupon>` sub-block with four children:

- `<Type>` — an enumeration `fix`/`float`/`zero`/`others`. Note the lowercase spelling; the schema uses `fix`, not `Fixed`.
- `<PaymentFrequency>` (`FrequencyType`) — a SWIFT-style four-letter code: `DAIL` (daily), `WEEK` (weekly), `TWWK` (two-weekly), `MNTH` (monthly), `TWMN` (two-monthly), `QURT` (quarterly), `SEMI` (semi-annual), `YEAR` (annual). Most European government bonds pay `YEAR`, most corporate bonds `SEMI`. These are the same codes the EMT/EPT regulatory templates of Chapter 8 use, so producers coming from that side of the house have the mapping already.
- `<InterestRate>` (`xs:decimal`) — the nominal coupon rate as a percentage of nominal value (`2.50` for a 2.50% coupon).
- For floating-rate notes, `<BaseIndex>` (`IdentifiersType`) and `<OffsetBPS>` (`xs:decimal`) describe the floating rate formula.

**Redemption.** A `<RedemptionRate>` (`xs:decimal`) carries the price at which the bond will be redeemed at maturity — typically `100.00` (par). An optional `<Redemption>` sub-block carries the redemption type (`Bullet` or `Sinkable`), any call/put option date, the direction of the option (`Issuer`, `Bearer`, or `Both`), and the option strike price where relevant.

**Tax fields.** `<WithholdingTaxRate>`, `<EUWithholdingTaxRate>`, `<EUWithholdingTaxCategory>` (`A`/`B`/`C`) and `<CapitalYieldsTaxKind>` cover the various European withholding regimes. Most producers populate only the first.

**The single biggest surprise in the bond type.** There is *no* `BondType` enumeration. The schema does not distinguish a *Government* bond from a *Corporate* bond from a *Covered* bond at the `<Bond>` level; that distinction is carried through `Issuer/Type` (the ECB-sector enumeration: `General government`, `Non-financial corporations`, `Deposit-taking corporations`, and so on) and through the `<Classifications>` block on `<Asset>`. Similarly, there is *no* `CountryOfRisk` element, *no* `DayCountConvention` enumeration, and *no* `Seniority` field. The producer who needs these concepts must carry them in `<Classifications>` or `<CustomAttributes>`.

**Credit ratings** live on `<Asset>` itself (not inside `<Bond>`) under `<Ratings>`, schema type `RatingsType`. The structure is slightly unusual: the outer container has one `<Rating>` child per *agency*, and each agency `<Rating>` wraps a `RatingCompany` name and one or more inner `<Rating>` entries carrying the actual rating values. An agency's rating history is a sequence of inner entries; the current rating is the most recent one. A bond rated by three agencies therefore has three outer `<Rating>` entries, one per agency, each with at least one inner `<Rating>` entry.

**Table 6.4 — Key bond-specific fields inside `AssetDetails/Bond` (schema type `BondType`)**

| Field | Schema type | Example | Mandatory |
|---|---|---|---|
| `ConvertibleFlag` | `xs:boolean` | `false` | **yes** |
| `Issuer` | `CompanyType` | Federal Republic of Germany | optional but expected |
| `StockMarket` | `MICCodeType` (repeats) | `XETR` | optional |
| `Listing` | enum `A`/`B`/`G`/`K`/`M`/`S`/`V`/`Y`/`Z` | `A` | optional |
| `ListingUnit` | enum `P`/`N` | `N` | optional |
| `IssueDate` | `xs:date` | `2024-02-15` | optional |
| `MaturityDate` | `xs:date` | `2034-02-15` | optional |
| `CouponDate` | `xs:date` | `2027-02-15` | optional |
| `Coupon/Type` | enum `fix`/`float`/`zero`/`others` | `fix` | optional |
| `Coupon/PaymentFrequency` | `FrequencyType` | `YEAR` | optional |
| `Coupon/InterestRate` | `xs:decimal` | `2.50` | optional |
| `RedemptionRate` | `xs:decimal` | `100.00` | optional |
| `Redemption/Type` | enum `Bullet`/`Sinkable` | `Bullet` | optional |
| `InterestRate` | `xs:decimal` | `2.50` | optional |
| `InterestsStartDate` | `xs:date` | `2026-02-15` | optional |

### 6.7.2 Position-Level Fields Specific to Bonds

At the position level, a bond entry ends with a `<Bond>` child (defined inline as an anonymous complex type within `<Position>`, XSD §28640) whose mandatory first child is `<Nominal>`. Its sequence is:

- `<Nominal>` (mandatory, `xs:decimal`) — the nominal value of the bonds held, in the issue currency. **`<Nominal>1000000</Nominal>` means one million of nominal value, not one million pieces.** This is the single most confusing convention in bond accounting for first-time implementers, and it is worth stating three times: bond `<Nominal>` is nominal, bond `<Nominal>` is nominal, bond `<Nominal>` is nominal. The total value of a bond position at par is therefore `Nominal × (Price / 100)`, because `Price` is expressed as a percentage of nominal.
- `<OriginalFace>` (optional) — the par value at the time of purchase, used for sinking-fund bonds whose nominal has been reduced through partial redemptions.
- `<Price>` (optional, `FundAmountType`) — the **clean price**, expressed as a percentage of nominal value. A bond trading at par has price 100.00, a bond at a five-point discount has price 95.00.
- `<OtherPrices>` (optional) — additional price quotes (hold-to-maturity, for example).
- `<DirtyPrice>` (optional, `FundAmountType`) — the clean price plus accrued interest, expressed as a percentage of nominal.
- `<MarketValue>` (optional, `FundAmountType`) — the market value of the position *without interest*, computed as `Nominal × (Price / 100)`.
- `<InterestClaimNet>` and `<InterestClaimGross>` (optional, `FundAmountType`) — the net and gross accrued interest in the bond's currency. The net/gross distinction reflects withholding tax treatment.
- `<AccruedInterestDays>` (optional, `xs:integer`) — the number of days of interest that have accrued, as an audit field for consumers that want to verify the producer's computation.
- `<ZeroBondInterestClaimNet>`, `<ZeroBondInterestClaimGross>`, `<ZeroBondCapitalYieldsTaxClaim>`, `<ZeroBondYield>` — analogues for zero-coupon bonds.
- `<Indexfactor>`, `<Poolfactor>` — for index-linked and pass-through bonds.
- `<BookRate>`, `<PurchaseValue>` — cost basis fields.
- `<LendedFlag>`, `<LendedUnits>`, `<IndicatorRaffled>`, `<CollateralValue>` — loan and corporate-action fields shared with equities.

**Clean price, dirty price, and position total.** Bonds trade on clean price in European markets — a price that excludes accrued interest. The clean price is what gets quoted on trading screens and in newspaper tables. When an investor actually buys a bond, they pay the clean price plus the accrued interest since the last coupon date — the *dirty price* — because the seller is entitled to the portion of the next coupon that has accumulated during their ownership. FundsXML follows the clean-price convention for `<Bond>/<Price>` and models the accrued interest through `<Bond>/<InterestClaimGross>` (or `InterestClaimNet`) as a separate field, and optionally through `<Bond>/<DirtyPrice>` as the combined figure.

The position's consolidated `<TotalValue>` at the `<Position>` level is therefore:

```
TotalValue = Nominal × (Price / 100) + InterestClaimGross
```

A consumer that computes the total as `Nominal × Price` without the percentage scaling will get an answer that is wrong by a factor of one hundred. A consumer that reads only `<Bond>/<MarketValue>` and omits the accrued interest will understate the position by the coupon accrual — small in absolute terms but meaningful for yield and duration calculations. In practice, the producer emits all three fields (`MarketValue`, `InterestClaimGross`, and the parent `<Position>/<TotalValue>` as the sum), and the consumer reads whichever it needs.

**Optional analytics** such as yield-to-maturity, modified duration, and convexity are not first-class fields of `<Bond>`. A producer that wants to ship them does so either through `<OtherPrices>` with a descriptive type label or through `<CustomAttributes>` on the asset entry. Most producers do not populate them; consumers who need them compute them locally from the bond's characteristics.

### 6.7.3 Bond Example: A German Bund Position

A generic European bond fund holds a position in a ten-year German federal government bond: nominal value 1,000,000 EUR, coupon 2.50%, maturity 15 February 2034, clean price 98.75 at the 31 March 2026 valuation. The accrued interest since the last coupon payment on 15 February 2026 is approximately 3,150 EUR (44 days at 2.50% on 1,000,000 EUR nominal).

```xml
<!-- Portfolio position -->
<Position>
  <UniqueID>DE0001102614</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">990650.68</Amount>
  </TotalValue>
  <TotalPercentage>0.99</TotalPercentage>
  <PriceDate>2026-03-31</PriceDate>
  <Bond>
    <Nominal>1000000</Nominal>
    <Price>
      <Amount ccy="EUR">98.75</Amount>
    </Price>
    <DirtyPrice>
      <Amount ccy="EUR">99.06507</Amount>
    </DirtyPrice>
    <MarketValue>
      <Amount ccy="EUR" isFundCcy="true">987500.00</Amount>
    </MarketValue>
    <InterestClaimGross>
      <Amount ccy="EUR">3150.68</Amount>
    </InterestClaimGross>
    <AccruedInterestDays>44</AccruedInterestDays>
  </Bond>
</Position>

<!-- Corresponding asset entry -->
<Asset>
  <UniqueID>DE0001102614</UniqueID>
  <Identifiers>
    <ISIN>DE0001102614</ISIN>
  </Identifiers>
  <Currency>EUR</Currency>
  <Country>DE</Country>
  <Name>Bundesrepublik Deutschland 2.50% 02/2034</Name>
  <AssetType>BO</AssetType>
  <AssetDetails>
    <Bond>
      <ConvertibleFlag>false</ConvertibleFlag>
      <Issuer>
        <Identifiers>
          <LEI>529900PY3MOXO1E5MD14</LEI>
        </Identifiers>
        <Name>Federal Republic of Germany — Finance Agency</Name>
        <BusinessCountry>DE</BusinessCountry>
        <Type>General government</Type>
      </Issuer>
      <ListingUnit>N</ListingUnit>
      <IssueDate>2024-02-15</IssueDate>
      <MaturityDate>2034-02-15</MaturityDate>
      <CouponDate>2027-02-15</CouponDate>
      <Coupon>
        <Type>fix</Type>
        <PaymentFrequency>YEAR</PaymentFrequency>
        <InterestRate>2.50</InterestRate>
      </Coupon>
      <RedemptionRate>100.00</RedemptionRate>
      <Redemption>
        <Type>Bullet</Type>
      </Redemption>
      <InterestRate>2.50</InterestRate>
      <InterestsStartDate>2026-02-15</InterestsStartDate>
    </Bond>
  </AssetDetails>
  <Ratings>
    <Rating>
      <RatingCompany>MOODYS</RatingCompany>
      <Rating>
        <Date>2025-06-15</Date>
        <Value>Aaa</Value>
        <Description>Long-term issuer credit rating — stable outlook</Description>
      </Rating>
    </Rating>
    <Rating>
      <RatingCompany>STANDARD-POORS</RatingCompany>
      <Rating>
        <Date>2025-05-20</Date>
        <Value>AAA</Value>
        <Description>Long-term foreign currency — stable outlook</Description>
      </Rating>
    </Rating>
    <Rating>
      <RatingCompany>FITCH</RatingCompany>
      <Rating>
        <Date>2025-07-02</Date>
        <Value>AAA</Value>
        <Description>Long-term issuer default rating — stable outlook</Description>
      </Rating>
    </Rating>
  </Ratings>
  <Classifications>
    <Classification>
      <ListedGroup>ESMA</ListedGroup>
      <Type>Bond Type</Type>
      <Language>en</Language>
      <Value>Sovereign</Value>
    </Classification>
  </Classifications>
</Asset>
```

Reading this pair: the position holds one million euros nominal of the 2.50% bund maturing 15 February 2034. The clean price is 98.75 (a small discount to par, reflecting a yield slightly above the coupon). The accrued interest of 3,150.68 EUR is the coupon income earned in the forty-four days since the 15 February 2026 payment, expressed as `<InterestClaimGross>` inside `<Bond>`. The position-level `<TotalValue>` is 990,650.68 EUR — the sum of `<Bond>/<MarketValue>` (987,500.00 EUR = 1,000,000 × 0.9875) and the interest claim. The `<DirtyPrice>` of 99.06507 is the clean price plus accrued expressed as a percentage, and consumers that prefer to read a single price number use it.

The asset entry carries the mandatory `<ConvertibleFlag>false</ConvertibleFlag>` as the first child of `<Bond>` — even for a vanilla government bond. The `<Issuer>` block names the Federal Republic's bond-issuing agency with its LEI, a business country of `DE`, and an ECB sector classification of `General government`; this is where the "sovereign" nature of the bond is encoded, not in any `BondType` enumeration. The `<ListingUnit>N</ListingUnit>` declares that the bond trades by nominal, matching the position-level `<Nominal>` idiom. The `<Coupon>` sub-block uses the `<PaymentFrequency>YEAR</PaymentFrequency>` code for an annual coupon, and `<Type>fix</Type>` (lowercase, as the schema demands) for the fixed-rate nature. The `<Redemption><Type>Bullet</Type></Redemption>` declares that the bond is redeemed in a single payment at maturity, not in a sinking-fund pattern.

The `<Ratings>` block carries three agency entries — Moody's, Standard & Poor's, and Fitch — each wrapping a `<RatingCompany>` name and one inner `<Rating>` entry with date, value, and description. All three agree on `AAA` (or `Aaa` in Moody's scale), as one would expect for German government paper. A consumer that needs the *middle* of the three ratings can read all three and apply its own logic; a consumer that wants the *most conservative* picks the lowest. A `<Classifications>` entry under `<ListedGroup>ESMA</ListedGroup>` classifies the bond as `Sovereign` for downstream consumers that want a textual label without walking into the issuer type.

The bond example shows every structural feature that distinguishes bonds from equities: the nominal-quantity convention, the clean/dirty price split, the rich issuer information, the multiple rating agencies, and the surprising absence of a `BondType` enumeration in favour of issuer-sector and classifications-based categorisation. A European bond fund's portfolio is a long list of entries of this shape, one per issue.

---

## 6.8 Investment Funds

The case in which a fund holds another fund's shares as a position. For a pure equity UCITS like the Europa Growth Fund this is a minor pattern — the fund occasionally holds a European equity ETF as a liquidity substitute — but for a fund-of-funds it is the dominant pattern, and either way the asset class deserves its own treatment.

### 6.8.1 The Fund-as-an-Asset Model

A held fund is represented in `AssetMasterData` as an `<Asset>` element whose `<AssetType>` is `SC` (*Share Class*), not a nested `<Fund>` element. The discriminator is a deliberate reminder that from the holder's perspective, what is owned is always a *specific share class* of a fund — the euro-distributing class, the CHF-hedged class, the institutional class — never the fund as an abstraction. In Chapter 5 we spent twenty pages establishing that investable units are share classes; here we see the same principle applied from the other side.

A fund-of-funds that holds six underlying funds therefore carries six `<Asset>` entries with `AssetType=SC`, not six nested `<Fund>` elements. Each position in the portfolio has a `<ShareClass>` child carrying its unit count and valuation, and each asset entry describes the held share class as an instrument. The portfolio-asset linkage mechanism is uniform across all asset classes, and introducing a nested-fund exception would complicate every consumer's parsing logic for no benefit.

**Share-class details** inside `AssetDetails/<ShareClass>` (schema type `ShareClassDetailsType`, XSD §32804) are surprisingly minimal. The schema treats a held share class as just another tradable instrument, and most of the rich fund-level metadata from Chapter 5 (legal structure, domicile, benchmarks, classifications, SFDR product type) is *not* duplicated on the holder's side. `ShareClassDetailsType` carries only:

- `Issuer` — a `CompanyType` block identifying the fund's management company or promoter.
- `StockMarket` — one or more MIC codes for the exchanges on which the share class trades (relevant only for listed share classes such as ETFs).
- `Listing` — the same A/B/G/K/M/S/V/Y/Z enumeration as for equities.
- `ListingUnit` — `U` (units) or `N` (nominal), almost always `U`.
- `IssueDate` — the share class's inception date.
- `MaturityDate` — the share class's maturity date, for closed-ended vehicles.
- `WithholdingTaxRate` — the tax rate applied to distributions.
- `ShareClassType` — a `ShareClassTypeType` block with `Code`, `EarningUse` (D/P/R), and short/long names, mirroring the structure we met at `ShareClass/ShareClassType` in Chapter 5.
- `ExchangeTradedFundFlag` (`xs:boolean`) — a dedicated flag for ETFs, distinct from the generic listing enumeration.

**Fields that the schema does not carry on a held share class** are, notably, `FundLegalType`, `FundCategory`, `OngoingCharges`, and any explicit *lookthrough* flag. The legal type of a held fund, where relevant, lives in `<Classifications>` on the outer `<Asset>` (for example `<ListedGroup>ESMA</ListedGroup>` with `<Value>UCITS</Value>`). The held fund's ongoing charges figure — relevant for the holding fund's own MiFID II cost disclosure — is not a field on the instrument at all; it is delivered through the regulatory templates of Chapter 8, specifically the EMT section that aggregates per-instrument charges, and through `<CustomAttributes>` on the asset entry for producers that want to carry it inline.

The *lookthrough* concept deserves a short explanation. For certain regulatory calculations — concentration limits, ESG exposure aggregation, Solvency II capital charges — the regulator asks not "what funds does this fund hold?" but "what underlying assets does this fund ultimately hold?" Lookthrough requires the holder to obtain the underlying composition of each held fund and aggregate it into its own exposure calculation. FundsXML carries the decomposition data itself through `Portfolio/PositionsDecomposed`, a dedicated sibling of [`<Positions>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Positions) that replaces held share classes with the scaled-down positions of the underlying fund. A producer that wants to offer lookthrough data to its consumers populates `<PositionsDecomposed>` with the underlying positions and a `<LookThroughLevels>` count stating how deep the decomposition went; a consumer that needs lookthrough reads from `<PositionsDecomposed>` rather than from `<Positions>`. There is no boolean "lookthrough required" flag anywhere on the share-class instrument.

### 6.8.2 Fund Position Example

A small illustrative example — not from the Europa Growth Fund, because a pure equity UCITS rarely holds ETFs of its own asset class, but from a generic European multi-asset fund that parks liquidity in the *iShares Core MSCI Europe UCITS ETF EUR (Acc)* (ISIN IE00B4K48X80) while awaiting deployment.

```xml
<!-- Portfolio position -->
<Position>
  <UniqueID>IE00B4K48X80</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">2000250.00</Amount>
  </TotalValue>
  <TotalPercentage>0.43</TotalPercentage>
  <PriceDate>2026-03-31</PriceDate>
  <ShareClass>
    <Shares>22500</Shares>
    <Price>
      <Amount ccy="EUR">88.90</Amount>
    </Price>
    <PurchaseValue>
      <Amount ccy="EUR">1987420.00</Amount>
    </PurchaseValue>
  </ShareClass>
</Position>

<!-- Asset entry -->
<Asset>
  <UniqueID>IE00B4K48X80</UniqueID>
  <Identifiers>
    <ISIN>IE00B4K48X80</ISIN>
  </Identifiers>
  <Currency>EUR</Currency>
  <Country>IE</Country>
  <Name>iShares Core MSCI Europe UCITS ETF EUR (Acc)</Name>
  <AssetType>SC</AssetType>
  <AssetDetails>
    <ShareClass>
      <Issuer>
        <Identifiers>
          <LEI>549300MS535KC2WH4Z30</LEI>
        </Identifiers>
        <Name>BlackRock Asset Management Ireland Limited</Name>
        <BusinessCountry>IE</BusinessCountry>
        <Type>Non-MMF investment funds</Type>
      </Issuer>
      <StockMarket>XETR</StockMarket>
      <Listing>A</Listing>
      <ListingUnit>U</ListingUnit>
      <IssueDate>2009-09-29</IssueDate>
      <ExchangeTradedFundFlag>true</ExchangeTradedFundFlag>
    </ShareClass>
  </AssetDetails>
  <Classifications>
    <Classification>
      <ListedGroup>MORNINGSTAR</ListedGroup>
      <Type>Global Category</Type>
      <Language>en</Language>
      <Value>Europe Large-Cap Blend Equity</Value>
    </Classification>
  </Classifications>
</Asset>
```

Three points about this example. First, the `<ShareClass>` child at the position level carries `<Shares>` (the number of fund units held, `xs:decimal`), `<Price>` (the last NAV of the held share class, in its native currency), and `<PurchaseValue>` (the historical cost). Unlike `<Equity>`, the share-class inner block has no `<MarketValue>` field — the consolidated value of the position lives at the `<Position>/<TotalValue>` level, not inside `<ShareClass>`. A producer that wants to carry the held fund's own NAV-times-units figure for debugging purposes can do so in `<OtherPrices>`.

Second, the asset entry marks the held fund as an ETF through `<ExchangeTradedFundFlag>true</ExchangeTradedFundFlag>` inside `<AssetDetails>/<ShareClass>` — a dedicated boolean that is *in addition to* the generic `Listing` enumeration. Consumers that want to identify ETFs read the flag directly rather than parsing the MIC code or the listing status. The `<Classifications>` block carries the Morningstar global category — a real Morningstar label that Europe-large-cap blend ETFs actually occupy — through the idiomatic `<ListedGroup>MORNINGSTAR</ListedGroup>` path.

Third, the holding fund's own cost disclosure under MiFID II does need to aggregate the held ETF's ongoing charges on a proportional basis, but the mechanism is not through a field on the share-class instrument. The aggregation happens in the regulatory templates of Chapter 8, where the EMT provides its own per-instrument cost structure and the consumer rolls them up. For the purposes of the portfolio block, the held ETF is just another position valued at its current NAV.

---

## 6.9 Derivatives

Derivatives are the most conceptually complex asset class in FundsXML, and they deserve the pages they are about to receive. For the Europa Growth Fund, derivatives appear in a single place: the two currency forwards that implement the CHF hedge for the R-CHF-ACC-HEDGED share class from Chapter 5. Other funds hold futures, options, and swaps in much larger proportions, and the general framework this section establishes applies to all of them.

### 6.9.1 Notional versus Market Value — the Key Concept

Derivatives differ from every other asset class because they have *two* value figures, and the figures can differ by orders of magnitude.

**Notional** is the *economic exposure* of the contract — the amount on which the contract's payoffs are based. A currency forward to buy 59 million CHF and sell 56.7 million EUR at a rate of 1.0420 has a notional of 56.7 million EUR on the sell side and 59 million CHF on the buy side — two valid representations of the same contract, related by the agreed forward rate. A futures contract on 10,000 units of a DAX index future has a notional equal to the index level times the contract multiplier times 10,000. A swap has a notional equal to the principal on which the periodic payments are computed.

**Market value** (also called *fair value*) is the *present value of the contract itself* as a tradable instrument — the amount a market participant would pay today to take the contract off the fund's hands. When a contract is first entered into, its market value is zero (because both parties agreed it was fair). As the underlying moves, the market value moves away from zero: a currency forward to sell EUR becomes valuable to the seller if the EUR weakens against the bought currency, and worthless or negative if the EUR strengthens. The absolute value of the market value is typically tiny compared to the notional — perhaps one-hundredth to one-thousandth of it, depending on the time remaining to expiry and the volatility of the underlying.

The difference matters enormously. The Europa Growth Fund's CHF hedge forwards have notional amounts in the tens of millions of euros but market values in the hundreds of thousands or less. A consumer that reads the notional and treats it as the position's contribution to market value will overstate the fund's portfolio by tens of millions of euros, and the fund's NAV calculation will be impossible to reconcile.

**Where the two numbers live in FundsXML.** The schema does not have dedicated *`Notional`* and *`MarketValue`* fields at the position level — this is the single most important difference from the generic derivative model a newcomer might expect. Instead:

- The **fair value** of the contract, in the fund's base currency, lives in the position's mandatory `<TotalValue>` element (schema type `FundAmountType`, at the top of `<Position>`, as for every other asset class). For an FX forward, `TotalValue` is the mark-to-market of the contract, and can be positive or negative depending on whether the trade is in or out of the money.
- The **notional amounts** live on the asset side, inside `AssetDetails/<FXForward>/<AmountBuy>` and `<AmountSell>`, paired with the two currencies (`CurrencyBuy` and `CurrencySell`). These are the contractual quantities of each currency, not valuations — they do not change over the life of the contract, while `TotalValue` moves with the spot rate.
- An optional `<Exposures>` container at the position level (schema type `ExposureType`) carries additional exposure figures computed under specific regulatory methodologies — the AIFMD commitment approach, the gross commitment approach, a custom producer method — each as a labelled `<Exposure>` entry with its own amount. This is the field producers populate when they need to carry a notional-style exposure figure explicitly rather than leaving it implicit in the asset-side `AmountSell`.

The discipline is therefore subtly different from the "Notional vs MarketValue" framing one finds in textbook descriptions. A consumer reads `<TotalValue>` for the mark-to-market contribution to the fund's NAV, reads the asset-side `AmountBuy`/`AmountSell` for the contractual notional amounts, and reads `<Exposures>/<Exposure>` for any regulatory exposure figure the producer chose to publish. Substituting one for another is still a catastrophic error — it is just that the labels the schema uses are different from the ones the textbook story suggests.

**Table 6.5 — Key derivative-related fields, where they live**

| Purpose | Field location | Type |
|---|---|---|
| Mark-to-market in fund currency | `Position/TotalValue` | `FundAmountType` |
| Regulatory exposure | `Position/Exposures/Exposure` | labelled `Type`+`Value` |
| Asset-class discriminator | `Asset/AssetType` | 2-char: `FX`/`OP`/`FU`/`SW` |
| Position-side sub-block | `Position/FXForward` \| `/Option` \| `/Future` \| `/Swap` | inline type |
| Contract details | `Asset/AssetDetails/FXForward` \| `/Option` \| `/Future` \| `/Swap` | `FXForward` carries `ForeignExchangeTradeType` |
| Contract currencies and notionals (FX) | `AssetDetails/FXForward/CurrencyBuy` + `AmountBuy` + `CurrencySell` + `AmountSell` | decimal + ISO currency |
| Agreed forward rate (FX) | `AssetDetails/FXForward/AgreedFxRate` | `xs:decimal` |
| Maturity (FX) | `AssetDetails/FXForward/MaturityDate` | `xs:date` (mandatory) |
| Counterparty | `AssetDetails/FXForward/Counterparty` | `CompanyType` (mandatory for FX, must have LEI) |
| Strike (options) | `AssetDetails/Option/StrikePrice` | `xs:decimal` |
| Contract size (futures, options) | `AssetDetails/Future/ContractSize` / `AssetDetails/Option/ContractSize` | `xs:decimal` |

### 6.9.2 FX Forwards

The derivative type the Europa Growth Fund actually holds, and the simplest class of all.

A currency forward is a contract to exchange a fixed amount of one currency for a fixed amount of another currency at a specific date in the future, at a rate agreed when the contract was entered into. In FundsXML, an FX forward is modelled as `AssetType=FX`, and the contract details live in `AssetDetails/<FXForward>`, which is an element of schema type `ForeignExchangeTradeType` (XSD §25529). Its mandatory children, in order, are:

- `<CurrencyBuy>` — the currency the fund is contractually buying (ISO 4217 code). An optional `@isBaseCCY` boolean attribute flags this as the fund's base currency.
- `<AmountBuy>` — the amount in the buy currency, as a plain `xs:decimal`. Note that this is **not** an `<Amount ccy="...">` wrapper; it is a bare decimal, with the currency given by the sibling `<CurrencyBuy>` element. This is a deliberate asymmetry with the position-side amounts, driven by the schema's choice to model the FX trade as a contract rather than a valuation.
- `<CurrencySell>` — the currency the fund is contractually selling.
- `<AmountSell>` — the amount in the sell currency, again as a plain `xs:decimal`.
- `<AgreedFxRate>` — the forward rate agreed at trade time, as a decimal (e.g. `1.0420` for EUR/CHF at 1.0420 Swiss francs per euro).
- `<StartDate>` (optional) — the trade date.
- `<MaturityDate>` — the value date / settlement date. **Mandatory**; this is the date on which the actual currency exchange takes place.
- `<Counterparty>` — a `CompanyType` block naming the bank on the other side of the trade, with its LEI inside `<Identifiers>`. **Mandatory**; every FX forward in FundsXML must name its counterparty.
- `<Deliverable>` (optional, `xs:boolean`) — whether the currencies will be physically exchanged at maturity (*true*) or only the profit/loss will be transferred (*false*, a non-deliverable forward or *NDF*).

The notional of an FX forward is thus **two amounts**, not one: the `AmountBuy` and the `AmountSell`. Producers pick whichever side corresponds to the fund's base currency as the "economic" notional and ignore the other; for a CHF-hedge forward on a EUR-base fund, the EUR-side `AmountSell` (the amount the fund has committed to sell) is the operational notional.

The market value of an FX forward at any time between trade and maturity is a function of the current spot rate and the agreed forward rate: when the current rate is favourable to the fund's side of the trade, the value is positive; when unfavourable, it is negative. The producer computes the mark-to-market using standard present-value techniques and writes the result into the **position's** `<TotalValue>` in the fund's base currency. Consumers do not attempt to recompute.

**The position-side `<FXForward>` sub-block carries almost no content.** The only fields it defines are `<HedgeRatio>` (an optional `PercentageType` stating how much of the target exposure the forward covers) and `<FxRateForEvaluation>` (an optional `xs:decimal` with the spot rate used for today's valuation). Everything else — the currencies, the amounts, the maturity, the counterparty — lives on the asset side. The reason is that the same contract is usually described once per delivery in `AssetMasterData` and may be held by several funds in the same file; the per-position data is only the fund-specific hedge ratio and today's valuation.

The Europa Growth Fund's CHF hedge consists of one or two overlapping forward contracts at any time: a currently-active forward that was rolled from the previous month and is due to settle at the end of the current month, and sometimes a just-entered forward for the next period. The structure is simple: approximately 56.7 million EUR (equal to the EUR equivalent of the R-CHF-ACC-HEDGED class's total net assets from §5.12) is sold forward against CHF at a forward rate close to the current spot. The forward is rolled at the end of each month, closing out the old contract and opening a new one.

### 6.9.3 Futures, Options, and Swaps

The remaining derivative types appear more briefly because they are not held by the Europa Growth Fund. Each gets a short paragraph naming its distinguishing fields.

**Futures** (`AssetType=FU`, asset-side details in `AssetDetails/<Future>` with schema type `FutureType`) are standardised, exchange-listed derivative contracts. Unlike forwards, they are margined daily — the fund pays or receives a cash amount each day equal to the change in the contract's mark-to-market value, so the position's `<TotalValue>` is conventionally zero or close to it (yesterday's margin movement has already moved into the cash balance). The `FutureType` fields that matter are `<Type>` (an enumeration covering `BF` Bond Future, `CF` Currency Future, `EF` Equity Future, `FRA` Forward Rate Agreement, `IF` Index Future, `IRF` Interest Rate Future, `MMF` Money Market Future, and `OTHER`), `<ContractSize>`, `<MaturityDate>`, and `<BasePrice>`. The position-side `<Future>` sub-block carries `<Contracts>` (the number of contracts, which may be negative for a short position) and a few supporting fields.

**Options** (`AssetType=OP`, asset-side details in `AssetDetails/<Option>` with schema type `OptionType`) carry additional fields because they are asymmetric contracts. `OptionType/<Type>` distinguishes the option family through a twelve-value enumeration: `BFO` Bond Future Option, `BO` Bond Option, `CFO` Currency Future Option, `EFO` Equity Future Option, `CO` Currency Option, `IFO` Index Future Option, `IO` Index Option, `IRFO` Interest Rate Future Option, `IRO` Interest Rate Option, `OTCIB` OTC Index-basket Option, `SO` Stock Option, `OTHER`. Strike price lives in `OptionType/<StrikePrice>`, contract size in `<ContractSize>`, expiry in `<MaturityDate>`, the call/put distinction in `<CallPutIndicator>` (`C` or `P`), and the exercise style in `<ExecutionStyle>` (American or European). The position-side `<Option>` sub-block carries `<Contracts>` (negative for a written option) and `<Price>` (the option premium). The market value of a long option is its premium times the number of contracts; the notional is the strike times the contract size times the number of contracts. A short option contributes the premium negatively.

**Swaps** (`AssetType=SW`, asset-side details in `AssetDetails/<Swap>` with schema type `SwapType`) are a family rather than a single type. `SwapType/<Type>` is an enumeration that covers `Currencyswap`, `Crosscurrencyswap`, `Creditdefaultswap`, `Indexswap`, `Totalreturnswap`, `Assetswap`, `Commodityswap`, `Interestrateswap`, `Inflationswap`, and `Other`. The rest of `SwapType` carries the shared metadata — `StartDate`, `MaturityDate`, `SettlementDate`, `Counterparty`, `FXRate`, `AgreedFxRate` — and the per-leg detail lives in a `<Legs>` container holding one or more `<Leg>` entries with their own rate, reference index, and payment-schedule fields. The position-side `<Swap>` sub-block carries `<HedgeRatio>`, `<CurrentSpread>` (relevant for Credit Default Swaps), `<PresentValueOfPayments>`, and a `<LegValues>` container with one entry per leg showing the current valuation of each side as `<Type>BUY</Type>` or `<Type>SELL</Type>` plus `<Value>`. For most European equity UCITS readers this chapter's treatment is enough; specialised bond and macro funds will need the detailed derivative documentation referenced in Appendix E.

### 6.9.4 FX Forward Example

The active CHF hedge forward of the Europa Growth Fund on 31 March 2026, as it would appear in the portfolio block and the asset master data block.

```xml
<!-- Portfolio position -->
<Position>
  <UniqueID>EGF-FXF-20260430-001</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">-142318.50</Amount>
  </TotalValue>
  <FXForward>
    <HedgeRatio>100.00</HedgeRatio>
    <FxRateForEvaluation>1.0395</FxRateForEvaluation>
  </FXForward>
</Position>

<!-- Asset entry -->
<Asset>
  <UniqueID>EGF-FXF-20260430-001</UniqueID>
  <Currency>EUR</Currency>
  <Name>EUR/CHF Forward 30/04/2026 (main hedge roll)</Name>
  <AssetType>FX</AssetType>
  <AssetDetails>
    <FXForward>
      <CurrencyBuy>CHF</CurrencyBuy>
      <AmountBuy>59107354.41</AmountBuy>
      <CurrencySell isBaseCCY="true">EUR</CurrencySell>
      <AmountSell>56724871.39</AmountSell>
      <AgreedFxRate>1.0420</AgreedFxRate>
      <StartDate>2026-02-28</StartDate>
      <MaturityDate>2026-04-30</MaturityDate>
      <Counterparty>
        <Identifiers>
          <LEI>O2RNE8IBXP4R0TD8PU41</LEI>
        </Identifiers>
        <Name>Société Générale S.A.</Name>
        <BusinessCountry>FR</BusinessCountry>
        <Type>Deposit-taking corporations except the central bank</Type>
      </Counterparty>
      <Deliverable>true</Deliverable>
    </FXForward>
  </AssetDetails>
</Asset>
```

Reading field by field: the position has no `<Currency>` override (the forward is already expressed in the fund's EUR base) and a mandatory `<TotalValue>` of *negative* 142,318.50 EUR, because the EUR has strengthened slightly against the CHF since the forward was entered into on 28 February, making the agreed sell rate slightly unfavourable to the fund. The negative sign on the `<Amount>` value is entirely schema-valid (the underlying `xs:decimal` type accepts negative values), and it is how the schema represents an out-of-the-money derivative position. Inside `<FXForward>`, the `<HedgeRatio>100.00</HedgeRatio>` declares that the forward fully covers its target exposure, and `<FxRateForEvaluation>1.0395</FxRateForEvaluation>` is the spot rate the producer used for today's mark-to-market.

The asset entry identifies the contract as an FX forward through `<AssetType>FX</AssetType>` and places the contract details inside `<AssetDetails>/<FXForward>`. The buy side is 59,107,354.41 CHF; the sell side is 56,724,871.39 EUR with `@isBaseCCY="true"` flagging it as the fund base currency; and the agreed forward rate is 1.0420 (close to the then-prevailing spot). `<MaturityDate>` is the settlement date on which the currencies will actually be exchanged (30 April 2026, one month out from the valuation point). The `<Counterparty>` is a full `CompanyType` block — the schema refuses anything less — with Société Générale's LEI inside `<Identifiers>` and the ECB sector classification identifying it as a deposit-taking corporation. The `<Deliverable>true</Deliverable>` flag declares that this is a standard deliverable forward, not a non-deliverable forward with cash settlement.

The `UniqueID` is a producer-generated string (`EGF-FXF-20260430-001`) rather than an ISIN, because over-the-counter forwards have no ISIN. The format is conventional: the fund short code, the instrument type, the maturity date, and a sequence number. Because `xs:ID` demands that the value begin with a letter, the `EGF-` prefix is mandatory; a raw numeric code would not pass schema validation.

The linkage to Chapter 5 is worth making explicit. The R-CHF-ACC-HEDGED share class from §5.10.2 carries `<CurrencyHedgedFlag>true</CurrencyHedgedFlag>`. That flag is the *declaration* that the class is currency-hedged; this forward is the *operational mechanism* by which the hedge is implemented. Without the forward, the CHF class would be exposed to EUR/CHF movements; with the forward, those movements are neutralised (imperfectly — the hedge cost absorbs into NAV, as §5.10.2 warned). The −142,318.50 EUR `<TotalValue>` is exactly the kind of small mark-to-market movement that gets absorbed into the CHF class's daily NAV.

---

## 6.10 Cash, Real Estate, and Other Asset Classes

The catchment section for everything that is neither equity, bond, fund, nor derivative. Three subsections of unequal importance.

### 6.10.1 Cash Positions

Cash is operationally the simplest asset class but deserves a careful discussion because FundsXML models it through a choice of three distinct asset-type codes, and picking the right one is the first decision.

**Three asset-type codes for cash.** The schema distinguishes:

- **`AC` — Account**: an ordinary bank account the fund maintains with its custodian. Details live in `AssetDetails/<Account>` (schema type `AccountType`, XSD §68). This is the most common cash asset class and covers current accounts, nostro accounts, and cash management accounts.
- **`FT` — Fixed Time Deposit**: a fixed-term deposit, typically thirty or ninety days, earning a rate above the current-account rate. Details live in `AssetDetails/<FixedTimeDeposit>` with schema type `FixedTimeDepositType`, which adds `StartDate`, `MaturityDate`, `MethodForCalculationOfInterest`, and `InterestRate` fields on top of the counterparty block.
- **`CM` — Call Money**: a short-term call money or call capital position, possibly used as collateral. Details live in `AssetDetails/<CallMoney>` with schema type `CallCapitalType`, which adds fields for `CollateralFlag` (whether the cash is pledged) and `CollateralDirection` (`PAID` or `RECEIVED`).

The generic *CurrentAccount / TimeDeposit / CashCollateral* trio one sees in textbook descriptions is therefore expressed through three separate asset-type codes, not through a single `CashType` enumeration on a single asset. A producer picks the code that best fits the account's operational nature and populates the corresponding details block.

**The `AccountType` details block** is the one most fund administrators actually use, and its children are minimal: an optional `<IndicatorCreditDebit>` (`Credit` or `Debit`) naming the account's default balance direction, optional `<AccountNumber>` and `<IBAN>` for regulatory reporting, optional `<InterestRateDebit>` and `<InterestRateCredit>` for overdraft and credit rates, and a **mandatory** `<Counterparty>` block of type `CompanyType` identifying the bank holding the account.

**One position per currency.** A fund with positions in EUR, GBP, and CHF has three cash positions, each representing one currency balance, each with its own `<Asset>` entry. There is no mechanism for aggregating multi-currency cash into a single position; the model forces the producer to name each currency explicitly. The position's `<Currency>` element and the asset's top-level `<Currency>` element must agree.

**Counterparty and concentration limits.** The bank holding the cash matters operationally because concentration limits under UCITS and AIFMD are applied against the counterparty, not the currency; a fund that holds 50 million EUR at a single bank has a 50 million EUR concentration against that bank, regardless of what other banks it also uses. For a custodian-held account the counterparty is the custodian itself; for cash collateral it is whichever party holds the collateral account (often a different bank). The counterparty's LEI is the single most important field on the whole cash asset entry.

**Position-side fields.** At the position level, a cash entry ends with an `<Account>` child (or `<FixedTimeDeposit>`, `<CallMoney>` for the other types). The `<Account>` inner block is the simplest of all choice children: both its children are optional — an `<MarketValue>` (the current balance, in the account's currency) and an `<Interests>` (accrued interest not yet credited). In practice producers populate `<MarketValue>` because it carries the operational balance, but the schema does not insist. There is no `<Units>`, no `<Shares>`, no `<Contracts>` — cash has no unit count, only a balance — and the authoritative fund-currency value lives at the position's `<TotalValue>` as always.

Example: the Europa Growth Fund's primary EUR cash position at its Luxembourg custodian on 31 March 2026.

```xml
<!-- Portfolio position -->
<Position>
  <UniqueID>EGF-CASH-EUR-001</UniqueID>
  <Currency>EUR</Currency>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">3247819.45</Amount>
  </TotalValue>
  <TotalPercentage>0.70</TotalPercentage>
  <Account>
    <MarketValue>
      <Amount ccy="EUR" isFundCcy="true">3247819.45</Amount>
    </MarketValue>
  </Account>
</Position>

<!-- Asset entry -->
<Asset>
  <UniqueID>EGF-CASH-EUR-001</UniqueID>
  <Currency>EUR</Currency>
  <Country>LU</Country>
  <Name>EUR Current Account — BGL BNP Paribas</Name>
  <AssetType>AC</AssetType>
  <AssetDetails>
    <Account>
      <IndicatorCreditDebit>Credit</IndicatorCreditDebit>
      <InterestRateCredit>0.15</InterestRateCredit>
      <Counterparty>
        <Identifiers>
          <LEI>549300CL2K1QUOZK7T97</LEI>
        </Identifiers>
        <Name>BGL BNP Paribas S.A.</Name>
        <BusinessCountry>LU</BusinessCountry>
        <Type>Deposit-taking corporations except the central bank</Type>
      </Counterparty>
    </Account>
  </AssetDetails>
</Asset>
```

Reading this pair: the position says the fund holds a euro current-account balance of 3.25 million euros at its Luxembourg custodian, representing 0.70% of total net assets. The `<Account>` inner block at the position level carries only the same balance as the position's consolidated `<TotalValue>` — for cash, the two are identical by construction, and the apparent redundancy is a schema artefact. The asset entry uses `<AssetType>AC</AssetType>` to signal *Account*, places the counterparty block inside `<AssetDetails>/<Account>` as the schema requires, and populates the counterparty's LEI (the critical field for concentration-limit reporting) inside `<Identifiers>` following the `CompanyType` convention. An optional `<InterestRateCredit>` of 0.15% indicates the rate the custodian is currently paying on the credit balance.

The Europa Growth Fund also holds small balances in GBP (from sterling dividend receipts on UK-listed holdings) and in CHF (for the CHF-hedge operational account). Both follow the same pattern, each as its own position with its own asset entry, both held at the same BGL BNP Paribas custodian.

### 6.10.2 Real Estate

The Europa Growth Fund holds no real estate, and this chapter does not attempt a detailed treatment. The structural essentials are worth naming briefly so that a reader who one day meets a real-estate fund delivery recognises the pattern.

Real estate comes in two forms. **Indirect real estate** — shares in listed REITs, units in property funds, private real-estate vehicles — is modelled through the ordinary `EQ` or `SC` asset types; the "real estate" nature shows up in the issuer's business and in classifications, not in a new asset class. **Direct real estate** — the fund owns the physical building — is modelled through `AssetType=RE` with `AssetDetails/<RealEstate>`, which carries property-specific fields for location, valuation method, and occupancy. Open-ended German and Luxembourg property funds are the usual populators of this branch; the schema's `RealEstateType` runs to several pages and its detail is outside the scope of this chapter. Readers interested in real-estate-specific reporting should consult the specialised documentation referenced in Appendix E.

### 6.10.3 Commodities, Private Equity, and Alternatives

A short catch-all for asset classes that do not appear in the Europa Growth Fund and are not treated in detail in this chapter. The schema has dedicated types for each:

- **Commodities** — `AssetType=CO`, details in `AssetDetails/<Commodity>`. Physical commodities are effectively excluded from UCITS portfolios by eligibility rules; they appear in specialised AIFs. Commodity futures are derivatives (§6.9), commodity-linked structured notes are bonds (§6.7).
- **Private equity** — `AssetType=PE`, details in `AssetDetails/<PrivateEquity>`. Holdings in non-listed companies, typically held through a limited partnership structure. Valued by mark-to-model rather than by market quote, updated quarterly or semi-annually. AIF territory.
- **Hedge funds** use `AssetType=SC` (share class, like any other fund) but with additional operational complications around redemption gates, lock-up periods, and side pockets that the position-level schema does not model directly. Producers extend through `<CustomAttributes>`.
- **Rights, warrants, certificates, crypto** — `AssetType=RI`/`WA`/`CE`/`CR` respectively, each with a dedicated details block in `AssetDetailsType`.

None of these asset classes appears in the Europa Growth Fund's portfolio, and none appears in the complete example of §6.12. They are named for completeness and for the reader who one day encounters an AIF delivery and needs to know that the mechanism exists — the branch in `AssetDetailsType` is already there, waiting for the asset.

---

## 6.11 Portfolio Breakdowns by Dimension

We close Part III of the chapter with a topic that sits alongside positions rather than inside them: the pre-computed aggregates that FundsXML delivers in its `<BreakDowns>` element. The capitalisation is deliberate — the element name is `BreakDowns` with a capital D, the container is a child of `Portfolio` (not of `FundDynamicData` or a separate root), and the structure is surprisingly more flexible than most readers expect.

### 6.11.1 Why Breakdowns Exist

A portfolio with 150 positions can be sliced along many dimensions — by sector, by country, by currency, by rating, by maturity, by instrument type. A consumer that wants to render a sector chart on a factsheet does not want to re-aggregate 150 position records every time the factsheet regenerates; it wants a ready-made list of "Healthcare 17.50%, Financials 17.20%, Industrials 14.40%, …". The `<BreakDowns>` element carries exactly this: pre-computed slices of the portfolio along standard dimensions, each containing a list of buckets with labels and percentages.

Two more substantive reasons justify the pre-computation. First, **classification conventions are producer-specific**. Two consumers that re-aggregate the same 150 positions may apply different sector classifications (GICS vs ICB), different country assignments (country of issue vs country of risk), or different lookthrough rules for held funds. The producer, being the single authoritative source, emits *one* classification, and every consumer using the producer's breakdowns sees the same picture. Consumers that want a different classification can still re-aggregate themselves, but the default is to trust the producer.

Second, **some breakdowns cannot be re-computed from positions alone**. A fund's currency breakdown, if it takes hedging into account, cannot be derived from the position-level currency fields alone — it requires knowledge of which forwards hedge which exposures, and the producer computes the net result after applying the hedges. A consumer recomputing from raw positions would get a pre-hedge exposure, which is not what the factsheet shows.

### 6.11.2 Structure of a Breakdown

The schema type is `BreakDownsType` (XSD §2390), and it is multi-dimensional by design. A single `<BreakDowns>` element contains one or more `<BreakDown>` children; each `<BreakDown>` carries:

- A `<Dimensions>` container holding one or more `<Dimension>` strings naming the dimensions along which the breakdown slices the portfolio. Common values are `Sector`, `Country`, `Currency`, `Rating`, `Duration`, `AssetType`, `Region`, `Size`. A single `<Dimension>` gives a one-dimensional breakdown; two `<Dimension>` entries (`Currency` and `AssetType`) produce a two-dimensional cross-tabulation.
- An optional `<CalculationMethod>` free-text field naming the basis of the calculation (`Market Value`, `Exposure`, `Brutto`, `Netto`, and so on).
- A mandatory `<Values>` container holding one or more `<Value>` entries. Each `<Value>` is one cell of the breakdown table and carries:
  - A `<DimValues>` container with one `<DimValue>` per dimension, each labelled by a `@dim` attribute identifying which dimension the value belongs to. For a one-dimensional sector breakdown, each `<Value>` has one `<DimValue dim="Sector">Financials</DimValue>` element; for a two-dimensional breakdown, each `<Value>` has two `<DimValue>` elements, one per dimension.
  - A mandatory `<Percentage>` (PercentageType, in per cent) giving the cell's share of the portfolio, from 0 to 100.
  - An optional nested `<BreakDowns>` element, allowing a breakdown cell to carry its own sub-breakdowns — the structure is recursive. A *Financials* sector cell, for example, can carry an inner breakdown into *Banks*, *Insurance*, *Diversified Financials*, each with its own percentage relative to the parent cell's share of the portfolio.

The completeness rule is that the sum of percentages across all `<Value>` entries within a single `<BreakDown>` should equal 100, subject to a rounding tolerance of a few basis points. A breakdown that sums to 99.95% or 100.03% is acceptable; a breakdown that sums to 92% is missing a cell and is a data-quality issue.

A concrete example — a one-dimensional sector breakdown for a generic European equity fund, shortened to four cells:

```xml
<BreakDowns>
  <BreakDown>
    <Dimensions>
      <Dimension>Sector</Dimension>
    </Dimensions>
    <CalculationMethod>Market Value</CalculationMethod>
    <Values>
      <Value>
        <DimValues>
          <DimValue dim="Sector">Financials</DimValue>
        </DimValues>
        <Percentage>22.50</Percentage>
      </Value>
      <Value>
        <DimValues>
          <DimValue dim="Sector">Industrials</DimValue>
        </DimValues>
        <Percentage>18.75</Percentage>
      </Value>
      <Value>
        <DimValues>
          <DimValue dim="Sector">Consumer Discretionary</DimValue>
        </DimValues>
        <Percentage>15.20</Percentage>
      </Value>
      <Value>
        <DimValues>
          <DimValue dim="Sector">Healthcare</DimValue>
        </DimValues>
        <Percentage>14.15</Percentage>
      </Value>
      <!-- further cells elided -->
    </Values>
  </BreakDown>
</BreakDowns>
```

A producer typically emits several `<BreakDown>` entries inside one `<BreakDowns>` container — one for each dimension the fund's consumers need. The Europa Growth Fund's monthly delivery emits breakdowns by sector, country, and currency at a minimum, and its complete `<BreakDowns>` block in §6.12 shows all three as sibling `<BreakDown>` entries.

**Two-dimensional breakdowns.** The multi-dimensional design shines when a consumer needs a cross-tabulation. A `<BreakDown>` with two `<Dimension>` children (*Country* and *Sector*) has one `<Value>` per country-sector cell, each with two `<DimValue>` elements carrying the two labels. The German Financials cell, the French Industrials cell, the Swiss Healthcare cell, and so on — each appears as a separate `<Value>` entry with its own percentage. This flexibility is largely unused in current production pipelines because most consumers prefer simpler one-dimensional breakdowns, but it is there when the need arises.

### 6.11.3 The Common Breakdown Types in Practice

**Sector breakdown** uses GICS by default for European equity funds, ICB for some British contexts, NACE for regulatory reporting. A diversified European equity fund typically shows Financials, Industrials, Consumer Discretionary, Healthcare, Technology, and Consumer Staples as the five or six largest sectors, each in the 10% to 25% range, followed by Utilities, Energy, Materials, Real Estate, and Communication Services in smaller allocations. The precise weights shift with the benchmark and the manager's active bets.

**Country breakdown** is based on the issuer's country of domicile (for equities) or country of risk (for bonds). A typical European equity fund is weighted heavily toward France and Germany — together 40% to 50% — with Switzerland, the Netherlands, Spain, Italy, and Scandinavia filling the remainder. The Europa Growth Fund's breakdown in §6.12 will show exactly this pattern.

**Currency breakdown** shows the currencies in which the portfolio is denominated, typically before hedging effects. For a European equity fund the dominant currency is EUR, with CHF (Swiss stocks), GBP (UK stocks), and smaller allocations to DKK, NOK, and SEK from Nordic holdings.

**Rating breakdown** matters for bond portfolios and is largely irrelevant for pure equity funds. The standard cells are *AAA*, *AA+* through *AA-*, *A+* through *A-*, *BBB+* through *BBB-*, *BB and below*, *Not Rated*. The producer picks a convention for which agency's rating to use (typically the middle of the three main agencies, or the lowest for conservatism).

**Duration breakdown** likewise matters for bonds. Cells are typically *0–1 year*, *1–3 years*, *3–5 years*, *5–10 years*, *10–20 years*, *20+ years*, or a shorter set for short-duration funds. The dimension name in the schema is `Duration`, and the convention is to put the same bucket labels that the factsheet uses into the `<DimValue dim="Duration">` elements. Equity funds do not emit duration breakdowns.

### 6.11.4 Producer versus Consumer Computation

A consumer that re-computes breakdowns from the raw positions will often find small differences from the producer's figures. Three sources account for almost all of the differences.

**Rounding**. Position-level percentages are rounded to two decimal places; summing rounded values gives a total that can differ from the producer's figure (which was computed at full precision before rounding) by a few basis points. This is an artefact of rounding, not a data error.

**Classification ambiguity**. A company like Siemens is both an industrial conglomerate and a technology provider, and different classification schemes place it differently. The producer's breakdown reflects the producer's chosen classification; a consumer using its own classification library will get different numbers. Neither is wrong; they are answers to slightly different questions.

**Lookthrough**. When the fund holds another fund (§6.8) and the producer has populated `<PositionsDecomposed>` to apply lookthrough to the held fund's underlying holdings, the producer's sector breakdown is computed from the decomposed positions and reflects the underlying holdings rather than the held fund as a single *Fund* cell. A consumer that reads `<Positions>` directly but reads the producer's breakdown will see a different picture than one that re-aggregates `<Positions>` itself. The difference is the lookthrough effect.

The operational rule is straightforward: **consumers trust the producer's breakdowns and recompute only for validation purposes, with appropriate tolerance**. Chapter 10 will formalise the tolerances that production validators should apply to breakdown reconciliation.

---

## 6.12 The Complete Europa Growth Fund Portfolio

We are now ready to assemble the largest example in the book. The Europa Growth Fund on 31 March 2026 holds approximately 150 distinct positions: 145 European equity positions across eleven countries and eleven sectors, three cash positions (EUR, GBP, CHF), and two currency forwards implementing the CHF hedge. The complete portfolio appears in Appendix D; this section shows a representative sample of fifteen equity positions, the three cash positions, and the two forwards, together with their `AssetMasterData` entries and the resulting portfolio breakdowns.

### 6.12.1 The Real Portfolio

Before looking at the XML, a word on what the real portfolio looks like. The fund's 145 equity positions are not uniform in size; the largest ten or so positions account for thirty to forty percent of the portfolio (the manager's conviction picks), while the remaining 130-plus positions form a long tail of smaller holdings for diversification. The sample of fifteen positions shown below is drawn from the larger end of the portfolio, so that each position is meaningful in size (between five and fifteen million euros), and is distributed across sectors and countries so that the portfolio breakdowns at the end of the section are meaningful.

The combined market value of the fifteen sample positions plus the three cash positions comes to approximately 130 million EUR — roughly 28% of the fund's total net assets of 464.55 million EUR. The remaining 72% lives in the 130 positions that are not shown here. The currency forwards do not add materially to the portfolio market value (their market values are in the low hundreds of thousands, positive or negative, absorbed into the hedged class's NAV).

### 6.12.2 The Portfolio Block

```xml
<Portfolio>
  <NavDate>2026-03-31</NavDate>
  <Positions>
    <!-- Equity positions (fifteen representative entries) -->
    <Position>
      <UniqueID>DE0007236101</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">8125000.00</Amount></TotalValue>
      <TotalPercentage>1.75</TotalPercentage>
      <PriceDate>2026-03-31</PriceDate>
      <Equity>
        <Units>50000</Units>
        <Price><Amount ccy="EUR">162.50</Amount></Price>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">8125000.00</Amount></MarketValue>
      </Equity>
    </Position>
    <Position>
      <UniqueID>DE0007164600</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">8538000.00</Amount></TotalValue>
      <TotalPercentage>1.84</TotalPercentage>
      <PriceDate>2026-03-31</PriceDate>
      <Equity>
        <Units>60000</Units>
        <Price><Amount ccy="EUR">142.30</Amount></Price>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">8538000.00</Amount></MarketValue>
      </Equity>
    </Position>
    <Position>
      <UniqueID>DE0008404005</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">7964800.00</Amount></TotalValue>
      <TotalPercentage>1.72</TotalPercentage>
      <PriceDate>2026-03-31</PriceDate>
      <Equity>
        <Units>32000</Units>
        <Price><Amount ccy="EUR">248.90</Amount></Price>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">7964800.00</Amount></MarketValue>
      </Equity>
    </Position>
    <!-- LVMH, TotalEnergies, BNP Paribas (FR) and Nestlé, Roche, Novartis (CH)
         follow the same pattern; the three Swiss positions carry their prices in
         CHF and their TotalValue in EUR (isFundCcy="true") alongside a CHF-native
         Amount for transparency -->
    <Position>
      <UniqueID>CH0038863350</UniqueID>
      <Currency>CHF</Currency>
      <TotalValue>
        <Amount ccy="EUR" isFundCcy="true">6017500.00</Amount>
        <Amount ccy="CHF">6270290.00</Amount>
      </TotalValue>
      <TotalPercentage>1.30</TotalPercentage>
      <PriceDate>2026-03-31</PriceDate>
      <Equity>
        <Units>65000</Units>
        <Price><Amount ccy="CHF">96.40</Amount></Price>
        <MarketValue>
          <Amount ccy="EUR" isFundCcy="true">6017500.00</Amount>
          <Amount ccy="CHF">6270290.00</Amount>
        </MarketValue>
      </Equity>
    </Position>
    <!-- ASML (NL), Shell, Unilever, AstraZeneca (GB), Iberdrola, Banco Santander (ES)
         follow the pattern. Cash positions come next. -->

    <!-- Cash accounts (one position per currency) -->
    <Position>
      <UniqueID>EGF-CASH-EUR-001</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">3247819.45</Amount></TotalValue>
      <TotalPercentage>0.70</TotalPercentage>
      <Account>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">3247819.45</Amount></MarketValue>
      </Account>
    </Position>
    <Position>
      <UniqueID>EGF-CASH-GBP-001</UniqueID>
      <Currency>GBP</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">208541.30</Amount></TotalValue>
      <TotalPercentage>0.04</TotalPercentage>
      <Account>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">208541.30</Amount></MarketValue>
      </Account>
    </Position>
    <Position>
      <UniqueID>EGF-CASH-CHF-001</UniqueID>
      <Currency>CHF</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">156217.80</Amount></TotalValue>
      <TotalPercentage>0.03</TotalPercentage>
      <Account>
        <MarketValue><Amount ccy="EUR" isFundCcy="true">156217.80</Amount></MarketValue>
      </Account>
    </Position>

    <!-- FX forwards implementing the CHF hedge for R-CHF-ACC-HEDGED -->
    <Position>
      <UniqueID>EGF-FXF-20260430-001</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">-142318.50</Amount></TotalValue>
      <FXForward>
        <HedgeRatio>100.00</HedgeRatio>
        <FxRateForEvaluation>1.0395</FxRateForEvaluation>
      </FXForward>
    </Position>
    <Position>
      <UniqueID>EGF-FXF-20260430-002</UniqueID>
      <Currency>EUR</Currency>
      <TotalValue><Amount ccy="EUR" isFundCcy="true">18420.75</Amount></TotalValue>
      <FXForward>
        <HedgeRatio>100.00</HedgeRatio>
        <FxRateForEvaluation>1.0395</FxRateForEvaluation>
      </FXForward>
    </Position>
  </Positions>
  <!-- BreakDowns follow in §6.12.4 -->
</Portfolio>
```

### 6.12.3 The AssetMasterData Block (Representative Entries)

At the root level of the document, the `AssetMasterData` block carries one entry per unique position referenced above. We show three representative entries in full — a German equity, a Swiss equity, and a cash account — together with one FX forward, and list the remainder in summary form.

```xml
<AssetMasterData>
  <Asset>
    <UniqueID>DE0007236101</UniqueID>
    <Identifiers>
      <ISIN>DE0007236101</ISIN>
      <GermanWKN>723610</GermanWKN>
    </Identifiers>
    <Currency>EUR</Currency>
    <Country>DE</Country>
    <Name>Siemens AG</Name>
    <AssetType>EQ</AssetType>
    <AssetDetails>
      <Equity>
        <StockMarket>XETR</StockMarket>
        <Issuer>
          <Identifiers><LEI>W38RGI023J3WT1HWRP32</LEI></Identifiers>
          <Name>Siemens Aktiengesellschaft</Name>
          <BusinessCountry>DE</BusinessCountry>
          <Type>Non-financial corporations</Type>
        </Issuer>
        <Listing>A</Listing>
        <CustomMarketCapitalization>
          <Name>Large Cap</Name>
          <Date>2026-03-31</Date>
          <Value>145000000000</Value>
        </CustomMarketCapitalization>
        <Industries>
          <IndustryCode>
            <Name>GICS</Name>
            <Date>2026-03-31</Date>
            <Value>20106010</Value>
          </IndustryCode>
        </Industries>
      </Equity>
    </AssetDetails>
    <Classifications>
      <Classification>
        <UnlistedGroup>GICS</UnlistedGroup>
        <Type>Sector</Type>
        <Language>en</Language>
        <Value level="1">Industrials</Value>
        <Value level="2">Industrial Conglomerates</Value>
      </Classification>
    </Classifications>
  </Asset>

  <Asset>
    <UniqueID>CH0038863350</UniqueID>
    <Identifiers>
      <ISIN>CH0038863350</ISIN>
      <SwissValorenCode>3886335</SwissValorenCode>
    </Identifiers>
    <Currency>CHF</Currency>
    <Country>CH</Country>
    <Name>Nestlé S.A.</Name>
    <AssetType>EQ</AssetType>
    <AssetDetails>
      <Equity>
        <StockMarket>XVTX</StockMarket>
        <Issuer>
          <Identifiers><LEI>549300DLLUD0PKVWST52</LEI></Identifiers>
          <Name>Nestlé S.A.</Name>
          <BusinessCountry>CH</BusinessCountry>
        </Issuer>
      </Equity>
    </AssetDetails>
    <Classifications>
      <Classification>
        <UnlistedGroup>GICS</UnlistedGroup>
        <Type>Sector</Type>
        <Language>en</Language>
        <Value>Consumer Staples</Value>
      </Classification>
    </Classifications>
  </Asset>

  <Asset>
    <UniqueID>EGF-CASH-EUR-001</UniqueID>
    <Currency>EUR</Currency>
    <Country>LU</Country>
    <Name>EUR Current Account — BGL BNP Paribas</Name>
    <AssetType>AC</AssetType>
    <AssetDetails>
      <Account>
        <IndicatorCreditDebit>Credit</IndicatorCreditDebit>
        <InterestRateCredit>0.15</InterestRateCredit>
        <Counterparty>
          <Identifiers><LEI>549300CL2K1QUOZK7T97</LEI></Identifiers>
          <Name>BGL BNP Paribas S.A.</Name>
          <BusinessCountry>LU</BusinessCountry>
          <Type>Deposit-taking corporations except the central bank</Type>
        </Counterparty>
      </Account>
    </AssetDetails>
  </Asset>

  <!-- Remaining equity asset entries (summary): -->
  <!-- SAP SE (DE0007164600, LEI 529900D6BF99LW9F3487, IT, DE, XETR)             -->
  <!-- Allianz SE (DE0008404005, LEI 529900K9B0N5BT694847, Insurance, DE, XETR)  -->
  <!-- LVMH (FR0000121014, LEI 96950065LBWY0APQIM86, Cons. Discr., FR, XPAR)     -->
  <!-- TotalEnergies (FR0000120271, LEI 529900S21EQ1BO4ESM68, Energy, FR, XPAR)  -->
  <!-- BNP Paribas (FR0000131104, LEI R0MUWSFPU8MPRO8K5P83, Financials, FR, XPAR)-->
  <!-- Roche (CH0012032048, LEI 549300D3OHVV27GBHI46, Healthcare, CH, XVTX)      -->
  <!-- Novartis (CH0012005267, LEI 549300D9YI2R72XBBM14, Healthcare, CH, XVTX)   -->
  <!-- ASML (NL0010273215, LEI 724500Y6DUVHQD6OXN27, IT, NL, XAMS)               -->
  <!-- Shell (GB00BP6MXD84, LEI 21380068P1DRHMJ8KU70, Energy, GB, XLON)          -->
  <!-- Unilever (GB00B10RZP78, LEI 549300MKFYEKVRWML317, Cons. Staples, GB, XLON)-->
  <!-- Iberdrola (ES0144580Y14, LEI K2RJR3UR2UQIYOV1YS65, Utilities, ES, XMAD)   -->
  <!-- Santander (ES0113900J37, LEI 5493006QMFDDMYWIAM13, Financials, ES, XMAD)  -->
  <!-- AstraZeneca (GB0009895292, LEI 213800ZCSBQL7LI8DI47, Healthcare, GB, XLON)-->

  <!-- Cash asset entries (summary): -->
  <!-- EGF-CASH-GBP-001 (AC, GBP, custodian BGL BNP Paribas LEI 549300CL2K1QUOZK7T97) -->
  <!-- EGF-CASH-CHF-001 (AC, CHF, custodian BGL BNP Paribas LEI 549300CL2K1QUOZK7T97) -->

  <!-- FX Forward asset entries -->
  <Asset>
    <UniqueID>EGF-FXF-20260430-001</UniqueID>
    <Currency>EUR</Currency>
    <Name>EUR/CHF Forward 30/04/2026 (main hedge roll)</Name>
    <AssetType>FX</AssetType>
    <AssetDetails>
      <FXForward>
        <CurrencyBuy>CHF</CurrencyBuy>
        <AmountBuy>59107354.41</AmountBuy>
        <CurrencySell isBaseCCY="true">EUR</CurrencySell>
        <AmountSell>56724871.39</AmountSell>
        <AgreedFxRate>1.0420</AgreedFxRate>
        <StartDate>2026-02-28</StartDate>
        <MaturityDate>2026-04-30</MaturityDate>
        <Counterparty>
          <Identifiers><LEI>O2RNE8IBXP4R0TD8PU41</LEI></Identifiers>
          <Name>Société Générale S.A.</Name>
          <BusinessCountry>FR</BusinessCountry>
          <Type>Deposit-taking corporations except the central bank</Type>
        </Counterparty>
        <Deliverable>true</Deliverable>
      </FXForward>
    </AssetDetails>
  </Asset>
  <!-- Second FX forward (EGF-FXF-20260430-002) is structurally identical with
       AmountBuy=2918000.00, AmountSell=2800000.00, AgreedFxRate=1.0421,
       StartDate=2026-03-15, same MaturityDate and counterparty. -->
</AssetMasterData>
```

The elided entries follow the same pattern as the fully-shown ones; each equity entry carries its `<Identifiers>` block with the ISIN (and where present the GermanWKN or SwissValorenCode), its `<Currency>`, its `<Country>`, its `<Name>`, its `AssetType=EQ`, and an `<AssetDetails>/<Equity>` block with the stock market MIC, the issuer's LEI inside a `CompanyType` block, the listing status, and an optional `<CustomMarketCapitalization>` size bucket; each cash entry carries its counterparty in `<AssetDetails>/<Account>`; the second FX forward is structurally identical to the first with different amounts and rates. Appendix D prints the full block with every entry populated.

### 6.12.4 Portfolio Breakdowns for the Sample

Computed from the fifteen equity positions shown above (scaled to 100% of the equity portion, excluding cash and forwards), three breakdowns are representative. They sit inside the same `<Portfolio>` element as the positions, as a sibling of `<Positions>` rather than at the root.

```xml
<BreakDowns>
  <BreakDown>
    <Dimensions><Dimension>Sector</Dimension></Dimensions>
    <CalculationMethod>Market Value</CalculationMethod>
    <Values>
      <Value>
        <DimValues><DimValue dim="Sector">Healthcare</DimValue></DimValues>
        <Percentage>17.50</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Financials</DimValue></DimValues>
        <Percentage>17.20</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Industrials</DimValue></DimValues>
        <Percentage>14.40</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Technology</DimValue></DimValues>
        <Percentage>14.30</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Consumer Staples</DimValue></DimValues>
        <Percentage>11.90</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Consumer Discretionary</DimValue></DimValues>
        <Percentage>9.80</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Energy</DimValue></DimValues>
        <Percentage>8.90</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Sector">Utilities</DimValue></DimValues>
        <Percentage>6.00</Percentage>
      </Value>
    </Values>
  </BreakDown>
  <BreakDown>
    <Dimensions><Dimension>Country</Dimension></Dimensions>
    <CalculationMethod>Market Value</CalculationMethod>
    <Values>
      <Value>
        <DimValues><DimValue dim="Country">GB</DimValue></DimValues>
        <Percentage>24.70</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Country">FR</DimValue></DimValues>
        <Percentage>20.20</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Country">DE</DimValue></DimValues>
        <Percentage>19.90</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Country">CH</DimValue></DimValues>
        <Percentage>13.40</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Country">ES</DimValue></DimValues>
        <Percentage>12.00</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Country">NL</DimValue></DimValues>
        <Percentage>9.80</Percentage>
      </Value>
    </Values>
  </BreakDown>
  <BreakDown>
    <Dimensions><Dimension>Currency</Dimension></Dimensions>
    <CalculationMethod>Market Value</CalculationMethod>
    <Values>
      <Value>
        <DimValues><DimValue dim="Currency">EUR</DimValue></DimValues>
        <Percentage>61.90</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Currency">GBP</DimValue></DimValues>
        <Percentage>24.70</Percentage>
      </Value>
      <Value>
        <DimValues><DimValue dim="Currency">CHF</DimValue></DimValues>
        <Percentage>13.40</Percentage>
      </Value>
    </Values>
  </BreakDown>
</BreakDowns>
```

The breakdowns above are computed from the fifteen-position sample. The breakdowns for the full 150-position portfolio in Appendix D are somewhat different: the UK weighting, in particular, is far less pronounced in the real portfolio (our sample overweights UK blue chips for illustrative purposes), and the sector distribution is more evenly spread across Financials, Industrials, Consumer, and Healthcare without the healthcare dominance that our sample shows. Note also that the country breakdown uses ISO 3166-1 alpha-2 codes (`DE`, `FR`, `CH`, `GB`, `ES`, `NL`) as `DimValue` labels — a producer convention that keeps the breakdown language-independent; a factsheet engine that wants to render "Germany" rather than "DE" applies its own localised mapping at display time. The *structural* lesson is the same either way: a breakdown is a cell-by-cell summary of the portfolio along one or more dimensions, and consumers read it directly rather than re-computing from positions.

### 6.12.5 A Three-Pass Reading

The example is best understood in three passes, each focusing on one of the asset classes the fund holds.

**First pass — equities.** Each of the fifteen equity positions follows the pattern of §6.6: a `<Position>` with mandatory `<UniqueID>` (the ISIN), optional `<Currency>` (the instrument's native currency), mandatory `<TotalValue>` (the consolidated value in the fund's EUR base, flagged `isFundCcy="true"`), optional `<TotalPercentage>` (the position's weight), optional `<PriceDate>`, and a mandatory `<Equity>` child carrying the per-unit detail fields (`<Units>`, `<Price>`, `<MarketValue>`). The asset entries populate the instrument's identifiers, the `<Equity>` details block with issuer LEI and stock market, and one or more `<Classifications>` entries. Three of the fifteen positions are Swiss companies priced in CHF (Nestlé, Roche, Novartis) and three are British companies priced in GBP (Shell, Unilever, AstraZeneca); the remaining nine are priced in EUR. The `<TotalValue>` on every position is EUR-tagged with `isFundCcy="true"`, with the non-EUR positions carrying a second `<Amount>` in their native currency for transparency.

**Second pass — cash.** Three cash positions, one per currency, each with `AssetType=AC` in the master-data entry and an `<Account>` child at both the position level and inside `AssetDetails`. The `<Account>` inner block at the position level contains only a `<MarketValue>` (the account balance), and the consolidated `<TotalValue>` at the position's top level carries the same balance expressed in the fund's base currency. Each cash asset entry names the custodian (BGL BNP Paribas S.A., the Europa Growth Fund's Luxembourg custodian) inside `AssetDetails/Account/Counterparty`, with the counterparty's LEI embedded in `CompanyType/Identifiers`. The GBP and CHF balances are small — residues from dividend receipts and hedge-operational needs — while the EUR balance of 3.24 million is the fund's main working cash.

**Third pass — derivatives.** Two currency forwards implementing the CHF hedge for the R-CHF-ACC-HEDGED share class. Each appears in `<Positions>` with an almost-empty `<FXForward>` sub-block (just a `<HedgeRatio>` and the spot rate used for today's valuation) and a position-level `<TotalValue>` that is the mark-to-market of the contract in EUR — *negative* 142,318.50 EUR for the main forward and a small positive 18,420.75 EUR for the secondary forward. The actual contract details — who is buying what from whom, at what rate, for settlement on which date, with whose LEI — live on the asset side under `AssetDetails/FXForward`. The main forward has an `AmountSell` of 56.7 million EUR and a matching `AmountBuy` of 59.1 million CHF at the `AgreedFxRate` of 1.0420 (matching the EUR-equivalent of the hedged class's total net assets from Chapter 5). The secondary forward is a much smaller residual covering a change in the class's AUM since the last monthly roll, with `AmountSell` 2.8 million EUR. Together the two forwards represent the hedge that makes the `<CurrencyHedgedFlag>true</CurrencyHedgedFlag>` on the share class operational, and their `TotalValue` figures absorb directly into the CHF class's NAV as part of its daily valuation.

The sum of `<TotalValue>` across the fifteen equities, three cash positions, and two forwards is approximately 116.8 million EUR — roughly 25% of the fund's total net assets of 464.55 million EUR. The remaining 75% lives in the 130 equity positions that our sample does not show, and the complete portfolio in Appendix D reconciles exactly to the 464.55 million EUR figure. The structural lesson remains the same: every position, every asset entry, every breakdown follows the same patterns established in the earlier sections of this chapter, and those patterns scale from fifteen positions to one hundred and fifty without modification.

---

## 6.13 Common Pitfalls

The following short list captures the mistakes that, in our experience, cause the greatest share of portfolio-related production incidents.

- **Schema validation fails at load time because a position references a `UniqueID` that no asset carries.** The parser raises an `xs:IDREF` error — a schema-validation error, not a business-validation error — and the document does not load at all. This is usually the residue of a pipeline in which the position writer and the asset writer ran out of sync. The fix is to emit positions and assets from the same producer pass and to validate every file against the schema before shipping it; Chapter 10 lists this as the first of the mandatory checks.
- **Orphaned `<Asset>` entries in `AssetMasterData`.** Asset entries appear with no position pointing at them — typically the residue of a position that was removed from the portfolio without a cleanup of the master data. Harmless for consumers (the parser does not complain), but a sign of a sloppy producer; pipelines should clean up orphans before emitting.
- **`TotalValue` is missing on a position.** A producer writes the position with `<Equity>/<MarketValue>` but forgets the position-level `<TotalValue>`. The file fails schema validation — `<TotalValue>` is mandatory — and the fund's NAV reconciliation cannot proceed. The fix is to populate `<TotalValue>` on every position without exception, with the position's consolidated market value in the fund's base currency.
- **Bond nominal written as pieces instead of nominal amount.** A producer writes `<Nominal>1000</Nominal>` meaning "one thousand pieces" for a bond whose face value is one million EUR total, when the correct representation is `<Nominal>1000000</Nominal>`. The resulting `Bond/MarketValue` (computed as `Nominal × Price / 100`) is off by a factor of a thousand. The fix is to treat bond `<Nominal>` as a nominal amount without exception and to verify, on every bond position, that `Bond/MarketValue + Bond/InterestClaimGross ≈ Position/TotalValue` to within a rounding tolerance.
- **Market value amount in the wrong currency.** The Nestlé position's price is in CHF, and a careless producer writes `<Equity>/<MarketValue>` in CHF while leaving the position-level `<TotalValue>` empty. A consumer that reads `<TotalValue>` to compute the fund total gets a missing value; a consumer that reads `<Equity>/<MarketValue>` and adds it to the EUR totals of other positions gets an answer that is wrong by the EUR/CHF rate. The fix is to always populate `<TotalValue>` with at least one `<Amount>` in the fund's base currency, tagged `isFundCcy="true"`, and to let the asset-class-specific `<MarketValue>` carry whichever currency suits the producer's internal accounting.
- **FX forward `<TotalValue>` confused with the notional.** A consumer reads the `<AmountSell>` of 56.7 million EUR from `AssetDetails/FXForward` and treats it as the forward's contribution to the fund's total net assets. The fund's NAV suddenly appears to be 56 million EUR larger than reality, and reconciliation fails. The fix is to always read `<Position>/<TotalValue>` for the mark-to-market contribution (which is the small positive or negative mark-to-market value, not the notional) and to use `<AmountBuy>`/`<AmountSell>` only for exposure reporting, not for valuation.
- **`<AssetType>` is written as `Equity` or `Bond` instead of the two-character code.** The schema enforces a two-character enumeration (`EQ`, `BO`, `SC`, `FX`, `AC`, …) on `<AssetType>`, and anything else is a schema-validation failure at load time. Producers migrating from formats with English type names must run a mapping pass before emitting the file.
- **Breakdown cell percentages do not sum to 100.** A sector breakdown sums to 93% because a cell for *Utilities* is missing from the `<Values>` list even though some positions belong there. The consumer sees the breakdown as incomplete and either refuses to render it or renders it with a suspicious gap. The fix is to emit every non-empty cell and to include an "Other" catch-all `<Value>` for positions that do not fit the standard categories.
- **Cash position without a counterparty LEI.** A cash asset's `AssetDetails/Account/Counterparty` is a `CompanyType`, which requires `<Identifiers>` *before* `<Name>`. A producer that writes `<Counterparty><Name>BGL BNP Paribas S.A.</Name></Counterparty>` without the `<Identifiers>/<LEI>` child fails schema validation immediately — `Identifiers` is mandatory on `CompanyType`. Even if validation somehow passed, a regulatory consumer could not apply counterparty concentration limits to the position because it cannot identify the counterparty unambiguously. The fix is to populate the counterparty LEI on every cash, derivative, and collateral position without exception.

---

## 6.14 Key Takeaways

- Portfolio positions and `AssetMasterData` entries together describe what a fund holds. Positions answer the question *how much*; asset entries answer *what*. Neither is complete without the other, and consumers always read the two structures together.
- The linkage between positions and asset entries runs through the `UniqueID` field, declared `xs:ID` on the asset side and `xs:IDREF` on the position side. The pairing is enforced by the parser at load time, not by business validation at a later stage. The value must conform to XML Name syntax (must not begin with a digit), and the recommended convention is *ISIN when available, deterministic producer-generated string otherwise*, so that the same asset receives the same identifier across consecutive deliveries.
- A `<Position>` has a fixed head of common children — `<UniqueID>`, optional `<Identifiers>`, optional `<Currency>`, mandatory `<TotalValue>`, optional `<TotalPercentage>`, optional cost and FX fields, optional `<PriceDate>`, optional `<PricingSource>` — followed by a **mandatory choice** of exactly one asset-class-specific child from twenty-one options (`<Equity>`, `<Bond>`, `<ShareClass>`, `<Warrant>`, `<Certificate>`, `<Option>`, `<Future>`, `<FXForward>`, `<Swap>`, `<Repo>`, `<FixedTimeDeposit>`, `<CallMoney>`, `<Account>`, `<Fee>`, `<RealEstate>`, `<REIT>`, `<Loan>`, `<Right>`, `<Commodity>`, `<PrivateEquity>`, `<CommercialPaper>`), and optionally a trailing block (`<CapitalYieldsTaxClaim>`, `<InflationaryAdjustment>`, `<RiskCodes>`, `<Underlyings>`, `<CustomAttributes>`). The unit count, per-unit price, and market value of the position live inside the chosen asset-class child (for example `<Equity>/<Units>`, `<Bond>/<Nominal>`, `<ShareClass>/<Shares>`, `<Option>/<Contracts>`), not on the position element itself. There is **no** element called `<Quantity>`, and no element called `<PositionType>` — the complex type `PositionType` is the XSD name of the type of `<Position>`, never a tag in the document.
- An `<Asset>` in `<AssetMasterData>` has its own fixed sequence — `UniqueID`, optional `Identifiers`, optional `DataSupplier`, mandatory `Currency`, optional `IncomeCurrency`, optional `Country`, mandatory `Name`, optional `FISN`, mandatory `AssetType` (as a two-character code), and optional `AssetDetails` carrying the asset-class-specific choice. `Ratings`, `Classifications`, and `CustomAttributes` follow at the bottom.
- For bonds, `<Bond>/<Nominal>` is the nominal value in the issue currency, not the number of pieces. The clean price is expressed as a percentage of nominal, so `MarketValue ≈ Nominal × (Price / 100)`, plus `InterestClaimGross` for the accrued coupon, sums to `Position/TotalValue` in the fund's base currency. There is no `BondType` enumeration; the sovereign-versus-corporate distinction lives on `Issuer/Type` (ECB sector codes) or in `Classifications`.
- For FX forwards, the mark-to-market lives in `Position/TotalValue` and may be positive or negative. The notional amounts live on the asset side in `AssetDetails/FXForward/AmountBuy` and `AmountSell`, paired with `CurrencyBuy` and `CurrencySell`. The position-side `<FXForward>` sub-block is almost empty — just `HedgeRatio` and `FxRateForEvaluation`. The mandatory `Counterparty` on the asset side uses `CompanyType` and must carry an LEI.
- For cash, one position per currency, `AssetType=AC` (or `FT` for fixed-term deposits, `CM` for call money), and the counterparty's LEI on `AssetDetails/Account/Counterparty/Identifiers/LEI`. There is no `CashType` enumeration — the account type is expressed through the two-character `AssetType` code.
- Portfolio breakdowns live in `Portfolio/BreakDowns` (not a separate root-level element) and are multi-dimensional by design. Each `<BreakDown>` names one or more `<Dimension>` strings and carries `<Value>` cells, each with a `<DimValues>` container (one `<DimValue dim="...">` per dimension) and a mandatory `<Percentage>`. The structure is recursive: a cell can carry its own nested `<BreakDowns>`. Trust the producer's breakdowns and tolerate small rounding discrepancies; Chapter 10 formalises the tolerance.
- The Europa Growth Fund's portfolio consists of roughly 150 European equity positions, three cash accounts in three currencies, and two currency forwards implementing the CHF hedge from Chapter 5. The complete representation appears in Appendix D and anchors every fragment treated in the remaining chapters of Part II.

We know what the Europa Growth Fund holds on 31 March 2026. What we do not yet know is *how it got there*. Chapter 7 turns to the events that flow in and out of the fund every business day — subscriptions, redemptions, distributions, and corporate actions — and shows how each of them reshapes the portfolio from one valuation point to the next.
