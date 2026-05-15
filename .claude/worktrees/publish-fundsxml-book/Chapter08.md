<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 8 — Regulatory Modules

*EMT, EPT, EET, EFT, and TPT in FundsXML*

---

## 8.1 Setting the Scene: The Fifth Area

At the end of Chapter 7 we had covered four of the five main areas of a FundsXML delivery: `ControlData`, `Funds`, `AssetMasterData`, and the substructures inside `FundDynamicData`. The fifth main area — [`RegulatoryReportings`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings) — has been waiting since Chapter 3, mentioned in passing but never treated in its own right. This chapter fills that gap, and it fills it at length, because the regulatory modules that live inside `RegulatoryReportings` are both varied in their subject matter and unavoidable in their practical importance. A European fund that cannot deliver its EMT cannot be retailed under MiFID II. A fund that cannot deliver its EPT cannot publish a PRIIPs KID. A fund that cannot deliver its EET cannot qualify for SFDR-classified distribution. A fund that cannot deliver its TPT cannot be meaningfully held by insurance investors under Solvency II. The templates behind these acronyms are, collectively, the regulatory operating system of the European fund industry.

The chapter covers all five FinDatEx templates — EMT, EPT, EET, EFT, and TPT — together with the European Single Access Point (ESAP) that is in the process of becoming the EU-wide gateway for regulatory disclosures. The treatment is weighted by practical importance: EMT and EET, the two most operationally consequential templates, receive the most attention; EPT follows closely; TPT and EFT are lighter; ESAP rounds the chapter off with a short section.

Before we begin, one honest framing deserves to be stated up front. This is not a chapter about PRIIPs, SFDR, or MiFID II *as regulations*. Entire books are written about each of those topics, and readers who need the full regulatory depth should consult them; Appendix E lists the primary sources. This chapter treats the **FundsXML embedding** of the FinDatEx templates — the XML structure, the main field groups, the relationship to the rest of a FundsXML document, and enough regulatory context (a page or two per template) that the reader can populate the fields correctly for a realistic fund. For the deep regulatory interpretation of any particular field, the authoritative source is always the current FinDatEx template specification and the corresponding ESMA technical standards.

By the end of this chapter, you should be able to:

- explain how `RegulatoryReportings` sits in a FundsXML document and how it splits into `DirectReporting` and `IndirectReporting` branches;
- name the regulatory driver of each template (MiFID II for EMT, PRIIPs for EPT, SFDR for EET, product governance for EFT, Solvency II for TPT);
- populate the main fields of each template for a realistic European UCITS;
- distinguish the cost fields of EMT from the cost fields of EPT and know which consumer uses which;
- classify a fund as SFDR Article 6, 8, or 9 and populate the corresponding EET fields;
- explain what ESAP is and how FundsXML deliveries may reach it;
- read a complete regulatory-reporting block and recognise which templates are present, which are absent, and why.

The Europa Growth Fund continues as the running example through all five templates. The fund is natively well-suited to the regulatory agenda of this chapter: it is a UCITS sold across eleven distribution countries (EMT and EPT), it carries an SFDR Article 8 classification (EET), it is held by European insurance investors (TPT), and it receives regular feedback from its distributors (EFT, though EFT will not appear in the March 2026 delivery for reasons explained in §8.6).

---

## 8.2 RegulatoryReportings and the FinDatEx Consortium

Before we look at any individual template, the structural question: where, inside a FundsXML document, does `RegulatoryReportings` sit, and who decides what goes into it?

### 8.2.1 The Structural Location

`<RegulatoryReportings>` is a root-level element of a FundsXML document, a sibling of `<Funds>` and `<AssetMasterData>`. It does *not* live inside `<FundDynamicData>` alongside `TotalAssetValues`, `Portfolios`, and `SingleFundFlows`. The choice of position is deliberate: regulatory modules have their own release cadence, their own semantics, and their own consumer audiences, and coupling them tightly to the valuation-point-driven dynamic data would be the wrong design. A fund may emit a fresh EMT every month without changing its NAV, and a fund may publish a new daily NAV without changing its EMT. The two are decoupled, and the schema expresses the decoupling by placing them in separate branches of the document.

Inside `<RegulatoryReportings>` the schema immediately splits into two parallel branches — `DirectReporting` and `IndirectReporting` — and the five FinDatEx templates are distributed between them:

```xml
<FundsXML4>
  <ControlData>...</ControlData>                <!-- Chapter 4 -->
  <Funds>
    <Fund>
      <FundStaticData>...</FundStaticData>       <!-- Chapter 5 -->
      <FundDynamicData>
        <TotalAssetValues>...</TotalAssetValues> <!-- Chapter 5 -->
        <Portfolios>...</Portfolios>             <!-- Chapter 6 -->
        <SingleFundFlows>...</SingleFundFlows>   <!-- Chapter 7 -->
      </FundDynamicData>
    </Fund>
  </Funds>
  <AssetMasterData>...</AssetMasterData>         <!-- Chapter 6 -->
  <RegulatoryReportings>                         <!-- this chapter -->
    <DirectReporting>
      <EMT_V4_2>...</EMT_V4_2>                   <!-- MiFID II -->
      <EFTs>...</EFTs>                           <!-- product governance -->
      <EET1.1.3>...</EET1.1.3>                   <!-- SFDR -->
    </DirectReporting>
    <IndirectReporting>
      <TripartiteTemplateSolvencyII_V6>...
      </TripartiteTemplateSolvencyII_V6>         <!-- Solvency II -->
      <PRIIPS_V20>...</PRIIPS_V20>               <!-- PRIIPs KID -->
    </IndirectReporting>
  </RegulatoryReportings>
</FundsXML4>
```

**Figure 8.1 — The RegulatoryReportings block**

```
                  <RegulatoryReportings>
                            │
               ┌────────────┴────────────┐
               │                         │
       <DirectReporting>         <IndirectReporting>
               │                         │
       ┌───────┼───────┐          ┌──────┴──────┐
       │       │       │          │             │
   <EMT_V4_2> <EFTs> <EET1.1.3>   <TPT_V6>  <PRIIPS_V20>
       │       │       │          │             │
    MiFID II  EFT    SFDR      Solvency II    PRIIPs
    costs &  (rare)  ESG       lookthrough     KID
    target                    for insurers    data
    market
```

The split between `DirectReporting` and `IndirectReporting` reflects the intended distribution path of each template. `DirectReporting` contains the templates that flow directly between regulated counterparties — EMT from manufacturer to distributor, EFT from distributor to manufacturer, EET as an SFDR disclosure artefact shared bilaterally. `IndirectReporting` contains the templates that flow through an intermediated disclosure chain — PRIIPs data, which ultimately reaches retail investors via a KID generator or an aggregator; TPT, which reaches insurance investors via their Solvency II reporting pipeline. Both branches are optional, and a fund that emits only one branch (or neither) is still schema-valid.

The critical rule is that **each module is self-contained**. EMT does not depend on EPT; EET does not know about EFT; TPT is independent of all the others. A consumer that processes only EMT reads only the `<EMT_V4_2>` branch; a consumer that needs TPT for Solvency II purposes reads only the `<TripartiteTemplateSolvencyII_V6>` branch. The modules share the enclosing `<RegulatoryReportings>` container and nothing else. There is no cross-module linking, no shared lookup tables, no implicit dependencies between the five blocks.

A corollary of this independence is that a `<RegulatoryReportings>` block may contain any subset of the five modules. A fund that has no insurance investors omits TPT. A fund that receives no distributor feedback in the reporting period omits EFT. A fund that is not actively subject to SFDR disclosures (a rare case, but it exists for some AIFs) omits EET. The schema tolerates any combination of the five, and consumers are expected to cope with partial blocks.

A brief note on the versioned element names that will appear throughout this chapter. [`EMT_V4_2`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings/EMT) corresponds to FinDatEx European MiFID Template version 4.2 of April 2024. [`PRIIPS_V20`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings/EPT) is the FinDatEx European PRIIPs Template v2.0. [`EET1.1.3`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings/EET) is the European ESG Template v1.1.3. [`EFTs`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings/EFT) is the container for the European Feedback Template v1.0. [`TripartiteTemplateSolvencyII_V6`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings/TPT) is the Tripartite Template v6.0 of March 2022. Each versioned element has its own type definition in the FundsXML XSD, and the schema retains every historical version (`EMT`, `EMT_V3`, `EMT_V4`, `EMT_V4_1`, `EMT_V4_2`; `EET1.0`, `EET1.1`, `EET1.1.1`, `EET1.1.2`, `EET1.1.3`; and so on) so that older documents continue to validate. A producer targeting a contemporary consumer uses the latest version on each line.

### 8.2.2 The FinDatEx Consortium

A point of great importance that deserves to be stated plainly: **FinDatEx is not FundsXML**. FinDatEx is an independent industry body, formed in 2018 and 2019 by the principal European financial-services associations — EFAMA for the fund industry, EBF for banks, Insurance Europe for insurers, among others — with the single mission of defining and maintaining standardised data templates to meet the regulatory disclosure requirements of the European financial sector. The templates are published and governed by FinDatEx. FundsXML embeds them.

The division of labour is worth spelling out because it determines who is responsible for what:

- **FinDatEx** decides the *content* of the templates: which fields exist, what they mean, what enumerated values they take, which validation rules apply at the semantic level. When a new PRIIPs technical standard is adopted by ESMA, FinDatEx updates the EPT to reflect the new field set. When SFDR Level 2 RTS introduces a new mandatory PAI indicator, FinDatEx updates the EET. The changes are published as new template versions — typically annually, with hotfix releases when regulatory changes demand them — in the form of Excel specifications that list every field, its type, and its regulatory meaning.

- **FundsXML** decides the *form* in which the templates are embedded: the XML element structure, the complex types, the way enumerations are serialised, and how each new FinDatEx version is added as a new, side-by-side versioned element under `DirectReporting` or `IndirectReporting`. When FinDatEx publishes a new EMT version, FundsXML follows in its next minor release, incorporating the new fields into its XSD and exposing the new version as a sibling element next to the previous one.

The separation is clean and the two organisations work closely together. Chapter 3 introduced this relationship in §3.2.3 as one of the patterns of FundsXML's history — regulation drives a new payload, FundsXML absorbs the payload as a new module. This chapter is where the pattern becomes operational: the five templates that follow are each an example of a regulation-driven module absorbed into a stable envelope.

An important practical consequence of the separation: **disputes about field meaning are settled at FinDatEx, not at FundsXML**. A producer who is unsure how a particular EMT cost field should be populated for a complex fee structure should consult the current FinDatEx EMT specification and its field-level guidance, not the FundsXML schema documentation. The FundsXML schema tells the producer *where* to put the value; the FinDatEx specification tells the producer *what* value to put there.

### 8.2.3 Module Selection — What to Send When

Not every FundsXML delivery carries all five templates. Which templates are included depends on the purpose of the delivery and on the needs of its consumers. The conventions that govern module selection are stable enough to be summarised.

**EMT** is the most frequently updated of the five. A fund that is actively retailed across the European Union typically emits a fresh EMT in every monthly delivery, and more frequently when something in its cost structure or target market changes (a new share class is launched, a fee is revised, a distribution country is added). A consumer that runs a retail distribution platform expects to find EMT in every delivery from every manufacturer it has a contract with.

**EPT** follows the PRIIPs KID refresh cycle. The KID itself must be reviewed at least annually, and re-issued whenever anything material changes (a significant shift in SRI, a new fee structure, a change in recommended holding period). EPT is re-emitted at the same cadence — typically monthly, to keep the downstream KID-generation pipelines synchronised, but the material updates are yearly.

**EET** runs on a slower cycle than EMT and EPT. SFDR pre-contractual disclosures are updated as the regulatory situation evolves, and PAI values are published on a quarterly or semi-annual basis. A monthly FundsXML delivery usually carries an EET that has been refreshed at most once in the preceding three months; a reporting cycle of quarterly EET updates is common.

**EFT**, as §8.6 will explain, flows in the opposite direction — from distributor to manufacturer — and therefore appears almost never in a manufacturer-to-distributor delivery. A fund's own monthly delivery does not contain EFT, because the fund is not the one providing feedback to itself. EFT appears in deliveries *from* a distributor *to* the fund's manufacturer, and those are separate files.

**TPT** is driven by Solvency II reporting dates, which are quarterly and year-end-anchored. An insurance consumer that produces its Solvency II QRT (Quantitative Reporting Template) in the weeks following each quarter-end needs the TPT for the funds it holds. The Europa Growth Fund emits TPT in every monthly delivery, because some of its institutional investors — insurance companies holding the I-EUR-DIST class — need month-end data.

The Europa Growth Fund's delivery of 31 March 2026 contains **EMT, EPT, EET, and TPT** — the four templates that the Europa Asset Management team publishes each month. It does not contain EFT, because no distributor feedback arrived in March that needed to be forwarded. The complete block in §8.9 reflects this pattern.

---

## 8.3 EMT — European MiFID Template

The most operationally important of the five templates, and the one that first brought FinDatEx into the foreground of European fund-data exchange.

### 8.3.1 What EMT Is and Why It Exists

MiFID II — the second Markets in Financial Instruments Directive, in force across the European Union since January 2018 — fundamentally restructured European retail financial advice. Its central theme, repeated in every corner of the legislation, is **transparency**: retail investors should know what they are buying, what it costs, and whether it is appropriate for them. The regulation places concrete obligations on both sides of the distribution chain. Manufacturers (typically asset managers) must disclose their products in structured detail, and distributors (banks, independent financial advisers, insurance brokers) must pass the disclosures on to investors before a sale and must verify that the investor falls within the manufacturer's intended target market.

The practical consequence is a continuous stream of structured data flowing from every manufacturer to every distributor, for every product, in every jurisdiction. Before the EMT existed, this stream ran over bilateral Excel files in every conceivable format — the exact problem that Chapter 1 cited as the motivation for a standard. A German distributor expected one spreadsheet layout, a French distributor expected another, and a Luxembourg fund administrator maintained dozens of variant templates to keep every bilateral relationship functional. The situation was unsustainable, and FinDatEx published the EMT in 2018 as the common answer. Within two years the European distribution chain had adopted it almost universally, and EMT has since become the *de facto* standard for manufacturer-to-distributor data exchange under MiFID II.

What EMT covers:

- **Product identification** — ISINs, names, currency, manufacturer LEI. Much of this content is repeated from the `FundStaticData` block (Chapter 5), with minor formatting differences to match FinDatEx conventions.
- **Target market** — the five MiFID II dimensions (investor type, knowledge and experience, ability to bear losses, risk tolerance, client objectives). Each dimension is expressed through yes/no/neutral flags so that a distributor can determine which clients the product is intended for and which it is explicitly *not* intended for.
- **Costs and charges** — the full cost structure in the MiFID II format, with one-off costs, ongoing costs, transaction costs, and incidental costs each broken down into their constituent parts. The section splits into *ex ante* (forward-looking) and *ex post* (realised) blocks.
- **Product governance** — the distribution strategy (execution only, with check, investment advice, portfolio management), the recommended holding period, and other governance flags.

EMT is emitted at the **share-class level**, not at the fund level. The Europa Growth Fund, with its three share classes, emits three separate `<FinancialInstrument>` blocks inside the enclosing `<EMT_V4_2>` — one for R-EUR-ACC, one for R-CHF-ACC-HEDGED, and one for I-EUR-DIST — because the cost structure, the target market, and the distribution strategy differ between the classes. The retail classes are aimed at retail investors across eleven countries; the institutional class is aimed at professional investors with a 1,000,000 EUR minimum investment. The same fund, three different disclosures.

### 8.3.2 Structure of the EMT Module

In the FundsXML embedding, the EMT module is rooted at a `<EMT_V4_2>` element inside `<DirectReporting>`. Its content is a sequence of one or more `<FinancialInstrument>` children, each of which is of type `EMT_V42_FinancialInstrumentType`. The type is structurally rich — nested, not flat — and its sequence has five mandatory top-level sections that together hold the full FinDatEx EMT v4.2 payload:

1. `<DataSetInformation>` — metadata about the EMT delivery itself (version, producer, generation timestamp, and three `Data_Reporting_*` flags that declare which sections the delivery populates);
2. `<GeneralInformation>` — product identification and manufacturer information (ISIN, instrument name, currency, manufacturer name and LEI, product type, and the `Fund` sub-block for UCITS-specific fields);
3. `<TargetMarket>` — the five MiFID II target market dimensions;
4. `<CostsAndChargesExAnte>` — the forward-looking cost disclosure;
5. `<CostsAndChargesExPost>` — the realised cost disclosure (optional, populated only when the `DataReportingExPost` flag in `DataSetInformation` is set to `Y`).

A minimal skeleton of one `<FinancialInstrument>` block looks like this:

```xml
<EMT_V4_2>
  <FinancialInstrument>
    <DataSetInformation>
      <Version>V4</Version>
      <ProducerName>Europa Asset Management S.A.</ProducerName>
      <ProducerLEI>529900T8BM49AURSDO55</ProducerLEI>
      <ProducerEmail>emt@europa-am.lu</ProducerEmail>
      <FileGenerationDateTime>2026-03-31T18:00:00Z</FileGenerationDateTime>
      <DataReportingTargetMarket>Y</DataReportingTargetMarket>
      <DataReportingExAnte>Y</DataReportingExAnte>
      <DataReportingExPost>N</DataReportingExPost>
    </DataSetInformation>
    <GeneralInformation>
      <!-- product identification — see §8.3.3 -->
    </GeneralInformation>
    <TargetMarket>
      <!-- five MiFID II dimensions — see §8.3.4 -->
    </TargetMarket>
    <CostsAndChargesExAnte>
      <!-- cost structure — see §8.3.5 -->
    </CostsAndChargesExAnte>
    <!-- CostsAndChargesExPost is optional -->
  </FinancialInstrument>
</EMT_V4_2>
```

A few structural points are worth noting. The `<Version>` element inside `<DataSetInformation>` uses the FinDatEx internal version string (`V4`, `V4S1`, `V4S2` for EMT version 4 with semantic sub-variants), not the FundsXML element name `EMT_V4_2`. The two are related but serve different purposes: the element name identifies the XSD schema used, and the `<Version>` string identifies the FinDatEx specification being implemented. The three `DataReporting*` flags are a producer's declaration of completeness — they tell the consumer which of the three data sections (target market, ex-ante costs, ex-post costs) have been populated in this particular delivery.

### 8.3.3 General Information Fields

The `<GeneralInformation>` section carries the identification fields and the manufacturer information. Most of the mandatory content is a rearrangement of what the fund already has in `<FundStaticData>` (Chapter 5), but with FinDatEx-specific formatting conventions that are worth calling out.

```xml
<GeneralInformation>
  <Code>LU2031234567</Code>
  <CodificationSystem>1</CodificationSystem>
  <InstrumentName>Europa Growth Fund R EUR ACC</InstrumentName>
  <InstrumentCurrency>EUR</InstrumentCurrency>
  <InstrumentPerformanceFee>N</InstrumentPerformanceFee>
  <InstrumentDistributionCash>N</InstrumentDistributionCash>
  <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
  <ProductType>U</ProductType>
  <ManufacturerName>Europa Asset Management S.A.</ManufacturerName>
  <ManufacturerLEI>529900T8BM49AURSDO55</ManufacturerLEI>
  <LeveragedOrContingentLiability>N</LeveragedOrContingentLiability>
  <Fund>
    <FundShareClassWithoutRetrocession>N</FundShareClassWithoutRetrocession>
  </Fund>
</GeneralInformation>
```

The `<Code>` plus `<CodificationSystem>` pair replaces a single ISIN field: the code is the actual identifier value, and the codification system is an integer enumeration telling the consumer what kind of code was used. `1` means ISO 6166 ISIN, `2` CUSIP, `3` SEDOL, `4` WKN, `5` Bloomberg Ticker, `8` FIGI, and so on, up to `99` for a producer-attributed internal code. The priority rule in the FinDatEx specification is: use ISIN when available, otherwise fall back to the codification in order of preference. For a European UCITS like the Europa Growth Fund, ISIN is always available.

`<ProductType>` uses a single-letter enumeration. `U` is UCITS, `N` is Non-UCITS (AIF), `S` is Structured Security, `SF` is Structured Fund, `LM` is UCITS Money Market Fund, `NM` is Non-UCITS Money Market Fund, `ETC` is Exchange Traded Commodity, `B` is Bond. The Europa Growth Fund is `U`.

The `<Fund>` sub-block at the bottom of `<GeneralInformation>` is selected via an `xs:choice` between `<Fund>` and `<StructuredSecurity>`. The schema offers the two alternatives because the fields that matter for a fund (retrocession status, exit-cost calculation basis) are different from the fields that matter for a structured security (notional-based versus item-based pricing, EUSIPA product category, quotation mode). For any UCITS or AIF, the `<Fund>` branch is chosen. The only mandatory field inside it is `<FundShareClassWithoutRetrocession>`: `Y` means the share class pays no inducement to distributors in the MiFID II sense, `N` means it does.

`<LeveragedOrContingentLiability>` is a yes/no flag used for MiFID II Article 62 reporting on leveraged instruments. For an ordinary long-only equity UCITS it is `N`; the flag is relevant for synthetic leveraged products or certain derivative-heavy funds.

The `<InstrumentPerformanceFee>` and `<InstrumentDistributionCash>` flags are derived from the fund's charter and its distribution policy: the Europa Growth Fund R-EUR-ACC class has no performance fee and is accumulating, so both values are `N`.

### 8.3.4 Target Market Fields

MiFID II defines the target market along five dimensions, and the FundsXML `<TargetMarket>` element maps each dimension to one nested child element with yes/no/neutral flags inside it. The five dimensions are `<InvestorType>`, `<KnowledgeAndExperience>`, `<AbilityToBearLosses>`, `<RiskTolerance>`, and `<ClientObjectives>`, plus a `<DistributionStrategy>` child that captures the MiFID II distribution strategy matrix.

For the Europa Growth Fund R-EUR-ACC, the block looks like this:

```xml
<TargetMarket>
  <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
  <InvestorType>
    <Retail>Y</Retail>
    <Professional>Y</Professional>
    <EligibleCounterparty>Y</EligibleCounterparty>
  </InvestorType>
  <KnowledgeAndExperience>
    <BasicInvestor>Y</BasicInvestor>
    <InformedInvestor>Y</InformedInvestor>
    <AdvancedInvestor>Y</AdvancedInvestor>
  </KnowledgeAndExperience>
  <AbilityToBearLosses>
    <CompatibleWithClientsWhoCanNotBearCapitalLoss>N</CompatibleWithClientsWhoCanNotBearCapitalLoss>
    <CompatibleWithClientsWhoDoNotNeedCapitalGuarantee>Y</CompatibleWithClientsWhoDoNotNeedCapitalGuarantee>
    <CompatibleWithClientsWhoCanBearLossBeyondCapital>N</CompatibleWithClientsWhoCanBearLossBeyondCapital>
  </AbilityToBearLosses>
  <RiskTolerance>
    <PRIIPSMethodology>4</PRIIPSMethodology>
  </RiskTolerance>
  <ClientObjectives>
    <ReturnProfile>
      <ClientLookingForPreservation>N</ClientLookingForPreservation>
      <ClientLookingForCapitalGrowth>Y</ClientLookingForCapitalGrowth>
      <ClientLookingForIncome>N</ClientLookingForIncome>
    </ReturnProfile>
    <MinimumRecommendedHoldingPeriod>
      <Years>5</Years>
    </MinimumRecommendedHoldingPeriod>
    <IntendedCompatibleWithClientsHavingSustainabilityPreferences>Y</IntendedCompatibleWithClientsHavingSustainabilityPreferences>
  </ClientObjectives>
  <DistributionStrategy>
    <ExecutionOnly>B</ExecutionOnly>
    <ExecutionWithCheckOrNonAdvisedServices>B</ExecutionWithCheckOrNonAdvisedServices>
    <InvestmentAdvice>B</InvestmentAdvice>
    <PortfolioManagement>B</PortfolioManagement>
  </DistributionStrategy>
</TargetMarket>
```

The values above reflect a UCITS equity fund that is appropriate for a broad range of retail and professional investors and is distributed through all four MiFID II distribution modes. A few notes on the enumerations:

- The `<InvestorType>/<Professional>` field takes `Y`, `N`, `P`, or `E`: `Y` covers both professional-per-se and elective-professional clients; `P` means only per-se professionals are compatible; `E` means only elective professionals are compatible; `N` means neither. The Europa Growth Fund accepts both, so the value is `Y`.
- All three knowledge levels are marked `Y` because a long-only European equity UCITS does not require any specialised financial sophistication. A more complex product (a leveraged ETF, a structured note, a convertible arbitrage fund) would typically mark `BasicInvestor` as `N` because the risk profile is too sophisticated for a first-time investor.
- The `<AbilityToBearLosses>` block uses three yes/no/neutral flags that together describe the loss profile. An equity UCITS can lose up to the entire invested capital (but no more — there is no leverage or margin), so the values are: *not* compatible with clients who cannot bear capital loss (`N`), compatible with clients who need no capital guarantee (`Y`), *not* compatible with clients who could face losses beyond their invested capital (`N`, because that scenario does not occur for a regular UCITS). The fourth optional field `<CompatibleWithClientsWhoCanBearLimitedCapitalLoss>` is omitted because it applies only to capital-protected or money market funds.
- `<RiskTolerance>/<PRIIPSMethodology>` is the PRIIPs SRI on the 1-to-7 scale — the same number that also appears in the EPT (§8.4.3). The Europa Growth Fund's SRI is 4.
- `<ClientObjectives>/<ReturnProfile>` uses three flags for preservation, capital growth, and income. The Europa Growth Fund is a growth product, so only `<ClientLookingForCapitalGrowth>` is `Y`.
- The `<MinimumRecommendedHoldingPeriod>` is expressed as an `xs:choice` between `<Years>` (a decimal) and `<Category>` (a one-letter V/S/M/L/H code for Very short / Short / Medium / Long / Hold to maturity). For the Europa Growth Fund, the RHP is five years, so `<Years>5</Years>` is used.
- `<IntendedCompatibleWithClientsHavingSustainabilityPreferences>` is a yes-or-neutral flag (there is no "No" — the MiFID II sustainability preferences framework does not allow negative target market on this dimension). For the Europa Growth Fund, which is SFDR Article 8, the value is `Y`.
- `<DistributionStrategy>` uses a four-value enumeration per distribution channel: `R` (Retail only), `P` (Professional only), `B` (Both), `N` (Neither). The Europa Growth Fund is distributed through all channels to both segments, so every channel is marked `B`.

**Table 8.1 — The MiFID II target market dimensions for the Europa Growth Fund R-EUR-ACC**

| Dimension | FundsXML element | Positive values | Notes |
|---|---|---|---|
| Client type | `InvestorType` | Retail=Y, Professional=Y, EligibleCounterparty=Y | All three categories |
| Knowledge and experience | `KnowledgeAndExperience` | Basic=Y, Informed=Y, Advanced=Y | Non-complex UCITS |
| Ability to bear losses | `AbilityToBearLosses` | Full loss acceptable | No capital guarantee |
| Risk tolerance | `RiskTolerance/PRIIPSMethodology` | 4 | PRIIPs SRI value |
| Client objectives | `ClientObjectives/ReturnProfile` | Capital growth only | Accumulating class |

The institutional class I-EUR-DIST has a different target market: the `<Retail>` flag drops to `N`, because the 1,000,000 EUR minimum investment effectively excludes retail investors. The other dimensions remain the same, because the underlying portfolio and risk profile are identical across share classes. A producer emits one `<FinancialInstrument>` block per share class and repeats the identification, target-market, and cost content with the per-class differences.

### 8.3.5 Cost and Charges Fields

The cost fields are the most conceptually intricate part of EMT, because they implement the MiFID II cost classification, which is itself elaborate. MiFID II divides the forward-looking cost disclosure into several categories, and the FundsXML `<CostsAndChargesExAnte>/<Fund>` block mirrors those categories field by field:

- **Entry costs** — `<GrossMaxEntryCostNonAcquired>` (entry load not acquired to the fund), `<MaxEntryCostAcquired>` (entry load acquired to the fund), plus two optional Italy-specific variants.
- **Exit costs** — `<MaxExitCost>`, `<MaxExitCostAcquired>`, `<TypicalExitCost>`, plus further optional fields for structured funds.
- **Ongoing costs** — `<OngoingCosts>` (the headline figure, equivalent to the Ongoing Charges Figure from Chapter 5), `<ManagementFee>` (the pure management fee component, which must be less than or equal to the total ongoing costs), and the optional `<DistributionFee>`.
- **Transaction costs** — `<TransactionCosts>`.
- **Incidental costs** — `<IncidentalCosts>`, primarily capturing performance fees.

All of these fields are decimals expressed as proportions of NAV in annualised terms: `0.0175` means 1.75% per year. A `<CostsReferenceDate>` element closes the block, recording the reference date of the cost figures (which may or may not coincide with the general reference date).

For the Europa Growth Fund R-EUR-ACC class, the forward-looking cost block looks like this:

```xml
<CostsAndChargesExAnte>
  <Fund>
    <GrossMaxEntryCostNonAcquired>0.0500</GrossMaxEntryCostNonAcquired>
    <MaxExitCost>0.0000</MaxExitCost>
    <OngoingCosts>0.0175</OngoingCosts>
    <ManagementFee>0.0150</ManagementFee>
    <TransactionCosts>0.0012</TransactionCosts>
    <IncidentalCosts>0.0000</IncidentalCosts>
  </Fund>
  <CostsReferenceDate>2026-03-31</CostsReferenceDate>
</CostsAndChargesExAnte>
```

Reading the block: the share class allows a maximum entry load of 5% (the contractual cap in the prospectus), although actual distributor agreements typically waive or reduce this figure. The exit cost is zero. The ongoing cost is 1.75% per year, of which 1.50% is the management fee and the remaining 0.25% covers administration, depositary, and other ongoing costs. The transaction cost estimate is 0.12% per year, computed according to the FinDatEx methodology from the fund's realised trading activity over the preceding period. The incidental cost is zero because the fund charges no performance fee. The total of 1.87% (ongoing + transaction + incidental, excluding the prospectus-cap entry load) is the headline annual cost figure that a consumer would show to a retail investor.

The `<CostsAndChargesExPost>` block, populated only when the `<DataReportingExPost>` flag is set to `Y`, carries the realised costs for a past reference period. Its structure mirrors the ex-ante block but with slightly different field names (`EntryCostAcquired`, `OngoingCosts`, `ManagementFee`, `TransactionCosts`, `IncidentalCosts`) and records actually incurred rather than contractually possible charges. A producer that publishes ex-post figures typically does so on an annual basis rather than monthly, because the computations depend on a full reporting period's trading data.

**An important relationship to Chapter 5**: the cost structure in EMT is *not* identical to the `<Fees>` block in `FundStaticData`. The `<Fees>` block is the fund's own representation of its charges, organised by fee type and computation basis. The EMT cost block is the MiFID II representation, organised by MiFID II's own categorisation. The two must be *consistent* — the management fee in EMT must equal the management fee in `<Fees>`, the total ongoing costs must equal the Ongoing Charges Figure, the transaction-cost methodologies must align — but they are not byte-for-byte copies of each other. Producers who generate both representations must take care that they reconcile, because a downstream consumer comparing the two will flag any discrepancy.

An even more important relationship concerns EPT, which we will treat in §8.4.4. EPT (inside `<PRIIPS_V20>`) also carries cost fields, but with a PRIIPs-specific breakdown and with horizon-dependent values computed at one year and at the recommended holding period. The EMT figures above are annual percentages; the EPT figures express the same underlying cost structure over the RHP, and the arithmetic of amortising one-off costs over five years versus one year produces different aggregated numbers. The two representations are both authoritative, and consumers must use the one that matches their disclosure horizon.

### 8.3.6 EMT in Context — Multiple Share Classes

The `<EMT_V4_2>` element contains a sequence of `<FinancialInstrument>` children, so a fund with multiple share classes emits one block per class under the same EMT wrapper:

```xml
<EMT_V4_2>
  <FinancialInstrument>
    <!-- R-EUR-ACC: ISIN LU2031234567 -->
    ...
  </FinancialInstrument>
  <FinancialInstrument>
    <!-- R-CHF-ACC-HEDGED: ISIN LU2031234641 -->
    ...
  </FinancialInstrument>
  <FinancialInstrument>
    <!-- I-EUR-DIST: ISIN LU2031234724 -->
    ...
  </FinancialInstrument>
</EMT_V4_2>
```

A consumer iterates the `<FinancialInstrument>` children and matches each one to its corresponding share class by `<Code>`. Nothing in the schema prevents mixing share classes from different funds inside a single `<EMT_V4_2>` element (the element is a flat list), but operational practice is to keep one EMT block per fund per delivery for clarity. Where a single delivery covers many funds — typical for large multi-manager platforms — the `RegulatoryReportings/DirectReporting/EMT_V4_2` branch can contain one `<FinancialInstrument>` per share class across all funds, and consumers split them at processing time by the `<Code>` field.

The complete EMT example for the Europa Growth Fund R-EUR-ACC class — combining the `DataSetInformation`, `GeneralInformation`, `TargetMarket`, and `CostsAndChargesExAnte` sections from §§8.3.2–8.3.5 — appears in full in §8.9 alongside the other templates.

---

## 8.4 EPT — European PRIIPs Template

The PRIIPs-focused counterpart to EMT, embedded in FundsXML under `<IndirectReporting>/<PRIIPS_V20>`.

### 8.4.1 The PRIIPs Regulation and the KID

PRIIPs — the Packaged Retail and Insurance-based Investment Products regulation — has governed European retail investment disclosure since its original entry into force in 2018 and has applied to UCITS since January 2023, when the transition period expired and the UCITS-specific KIID regime gave way to the PRIIPs-wide KID. The PRIIPs framework covers not only traditional funds but also structured products, unit-linked insurance products, and similar retail-accessible instruments, and it aims to make disclosures comparable across these otherwise very different product types.

The central output of PRIIPs is the **KID — the Key Information Document** — a three-page standardised document that every retail investor must be given *before* they invest. The KID is highly structured and, in practice, very nearly identical in layout across all PRIIPs products. It must include: the product's name and identification, its risk level (the SRI from 1 to 7), a set of performance scenarios over the recommended holding period, the costs the investor will bear, and a limited number of free-text sections that explain the product type and the intended target market.

The KID is a PDF that an end-investor reads. The *data* that populates the KID lives in a structured template — the **European PRIIPs Template, EPT** — which FinDatEx publishes and maintains. A manufacturer produces EPT; a distributor (or a specialised KID-generation service) consumes EPT and renders from it the final PDF document that goes into the investor's hands. EPT is the input; the KID is the output.

What the transition from UCITS KIID to PRIIPs KID changed:

- **Risk indicator**: the UCITS KIID used the SRRI (Synthetic Risk and Reward Indicator), a 1-to-7 scale based on past volatility of returns. The PRIIPs KID uses the SRI (Summary Risk Indicator), also 1 to 7, but computed as a combination of the Market Risk Measure (MRM, based on volatility and on the volatility-equivalent value) and the Credit Risk Measure (CRM). For most equity funds, CRM is 1 and the SRI is driven by MRM alone; for bond funds or structured products, the CRM contribution can dominate.
- **Performance presentation**: the UCITS KIID showed historical performance as a bar chart of the last ten years. The PRIIPs KID shows **four performance scenarios** — stress, unfavourable, moderate, favourable — as prospective outcomes over the recommended holding period, computed from the statistical distribution of the fund's historical returns.
- **Cost disclosure**: the UCITS KIID had a single Ongoing Charges figure. The PRIIPs KID has a detailed cost structure presented at multiple horizons (one year, half the RHP, and the full RHP), broken down into one-off, ongoing, and incidental categories.

EPT carries the structured data for all of these fields, and is therefore the template that any producer distributing UCITS to retail investors after January 2023 must emit alongside EMT.

### 8.4.2 Structure of the EPT Module

In FundsXML, EPT lives under `<IndirectReporting>/<PRIIPS_V20>`. The `PRIIPSType_V20` complex type has three children: a single `<EPTV2>` element that carries the core EPT payload, plus two optional `<CEPTV2History>` and `<CEPTV2Performance>` children that carry the Comfort EPT history and performance data (used primarily by insurance-linked products). For a plain UCITS like the Europa Growth Fund, only `<EPTV2>` is populated.

The `<EPTV2>` element groups the EPT fields into six mandatory sections:

1. `<DataSetInformation>` — the file-level metadata;
2. `<GeneralPortfolioInformation>` — product identification (the PRIIPs term "portfolio" refers to the *product* being disclosed, not to the fund's holdings portfolio from Chapter 6);
3. `<RiskAssessment>` — the SRI, MRM, CRM, and related indicators;
4. `<PerformanceScenario>` — the four PRIIPs performance scenarios;
5. `<Costs>` — the cost structure in the PRIIPs format;
6. `<Narratives>` — the standardised free-text fields that appear on the KID.

A skeleton:

```xml
<PRIIPS_V20>
  <EPTV2>
    <DataSetInformation>
      <Version>V21</Version>
      <!-- four Data_Reporting* flags -->
    </DataSetInformation>
    <GeneralPortfolioInformation>
      <!-- product identification — see §8.4.3 -->
    </GeneralPortfolioInformation>
    <RiskAssessment>
      <!-- SRI, MRM, CRM — see §8.4.4 -->
    </RiskAssessment>
    <PerformanceScenario>
      <!-- four scenarios — see §8.4.5 -->
    </PerformanceScenario>
    <Costs>
      <!-- cost structure — see §8.4.6 -->
    </Costs>
    <Narratives>
      <!-- KID free-text fields -->
    </Narratives>
  </EPTV2>
</PRIIPS_V20>
```

The `<Version>` element inside `<DataSetInformation>` takes the single value `V21`, reflecting EPT version 2.1 — the FinDatEx EPT revision that accompanies the PRIIPs technical standards currently in force. As with EMT, the element name (`PRIIPS_V20`) and the `<Version>` string (`V21`) refer to two different things: the former is the FundsXML-side XSD version, the latter is the FinDatEx-side template version.

One important schema quirk: the `DataSetInformation` block inside `<EPTV2>` uses yes/no fields of type `YesNoType`, which in this corner of the schema takes the string values `YES` and `NO` in full — not the single-letter `Y` and `N` used by EMT's `EMTYesNoType`. A producer who mechanically copies `Y`/`N` from one template to the other will hit a validation error. The fragments in this section use the correct `YES`/`NO` spelling.

### 8.4.3 General Portfolio Information

The `<GeneralPortfolioInformation>` block is the EPT equivalent of EMT's `<GeneralInformation>`: it identifies the product (manufacturer, LEI, group, the ISIN or internal code, the product name, currency, reference date, PRIIPs category, autocallable flag). For the Europa Growth Fund R-EUR-ACC class:

```xml
<GeneralPortfolioInformation>
  <PortfolioManufacturerName>Europa Asset Management S.A.</PortfolioManufacturerName>
  <PortfolioManufacturerGroupName>Europa Financial Group</PortfolioManufacturerGroupName>
  <PortfolioManufacturerLEI>529900T8BM49AURSDO55</PortfolioManufacturerLEI>
  <PortfolioID>
    <CodificationSystem>1</CodificationSystem>
    <Code>LU2031234567</Code>
  </PortfolioID>
  <PortfolioName>Europa Growth Fund R EUR ACC</PortfolioName>
  <PortfolioCurrency>EUR</PortfolioCurrency>
  <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
  <PortfolioPRIIPSCategory>2</PortfolioPRIIPSCategory>
  <IsAnAutocallableProduct>NO</IsAnAutocallableProduct>
</GeneralPortfolioInformation>
```

The `<PortfolioPRIIPSCategory>` field is a small integer on the closed enumeration 1 to 4, corresponding to the four PRIIPs product categories:

- **Category 1** — products where the retail investor could lose more than the amount invested (certain CFDs and derivative products) or where the product has no liquid market. Not applicable to traditional UCITS.
- **Category 2** — products whose return is linearly related to the performance of a diversified set of underlyings, and whose historical returns can be used directly for statistical modelling. Most long-only UCITS fall into Category 2. The Europa Growth Fund is Category 2.
- **Category 3** — products whose return depends non-linearly on the underlying (structured products with barriers, options, or path-dependency). These require Monte Carlo simulation for scenario generation.
- **Category 4** — products where the return depends on factors not observable in market data (with-profits insurance products, unit-linked wrappers with guarantees). These require their own scenario methodology.

The category choice drives much of the downstream scenario calculation, because the four categories use different methodologies for the performance scenario section. Most equity, bond, and balanced UCITS are Category 2; Category 3 is the natural home for structured funds.

### 8.4.4 Risk Assessment — SRI, MRM, and CRM

The `<RiskAssessment>` block carries the PRIIPs risk indicators and a handful of related fields. For the Europa Growth Fund:

```xml
<RiskAssessment>
  <ValuationFrequency>252</ValuationFrequency>
  <IS_Flexible>NO</IS_Flexible>
  <Existing_Credit_Risk>NO</Existing_Credit_Risk>
  <SRI>4</SRI>
  <IsSRIAdjusted>NO</IsSRIAdjusted>
  <MRM>4</MRM>
  <Recommended_Holding_Period>5</Recommended_Holding_Period>
  <HasAContractualMaturityDate>NO</HasAContractualMaturityDate>
  <Liquidity_Risk>L</Liquidity_Risk>
</RiskAssessment>
```

`<ValuationFrequency>` is the number of valuation days per year. The Europa Growth Fund values daily, so the value is 252 (business days). The field takes an enumeration — 1 (annual), 2 (biannual), 4 (quarterly), 12 (monthly), 24 (bimonthly), 52 (weekly), 104 (biweekly), 252 (daily) — and the producer chooses the one that matches the actual valuation cadence.

`<IS_Flexible>` marks whether the fund is a flexible fund under the PRIIPs Annex II clause 14. A flexible fund changes its asset-allocation profile over time and must disclose a historical VEV alongside a reference-allocation VEV. The Europa Growth Fund is a straight equity fund with a stable mandate and is therefore `NO`.

`<Existing_Credit_Risk>` is a yes/no flag. For a pure equity UCITS, the answer is `NO` because the fund holds no direct credit exposure. For a bond fund or a mixed fund with bond holdings, the answer is `YES` and the CRM (Credit Risk Measure) fields become load-bearing.

`<SRI>` is the headline 1-to-7 risk figure. For the Europa Growth Fund, the SRI is 4 — middle of the scale, consistent with a diversified European equity fund with moderate volatility and negligible credit risk.

`<MRM>` is the Market Risk Measure, also 1 to 7. The SRI is computed from the MRM and the CRM through a standardised matrix published in the PRIIPs regulatory technical standards; for a fund with no credit risk, MRM = SRI, and both are 4.

`<IsSRIAdjusted>` marks whether the manufacturer has exercised the regulatory option to increase the SRI beyond the value computed from the formula. This option exists for funds where the manufacturer believes the mechanical SRI understates the perceived investor risk — a rare occurrence, but the field is mandatory. For the Europa Growth Fund, the value is `NO`.

`<Recommended_Holding_Period>` is a decimal number of years, consistent with the EMT target market's `<MinimumRecommendedHoldingPeriod>/<Years>` field. Both say 5 for the Europa Growth Fund.

`<HasAContractualMaturityDate>` is `NO` for an open-ended UCITS and `YES` for a closed-ended or fixed-maturity product; the optional `<MaturityDate>` is populated only in the `YES` case.

`<Liquidity_Risk>` uses a single-letter enumeration: `M` (material liquidity risk), `I` (illiquid), or `L` (no liquidity issue). The Europa Growth Fund, invested in large-cap European equities, has no liquidity issue and is marked `L`.

### 8.4.5 Performance Scenarios

The `<PerformanceScenario>` block carries the four PRIIPs performance scenarios — **stress, unfavourable, moderate, favourable** — that appear on the KID. Each scenario is expressed as an annualised return (a decimal, e.g. `0.0540` for 5.40% per year) at the recommended holding period; the optional `<OneYear>` and `<HalfRHP>` children carry the shorter-horizon values.

For the Europa Growth Fund:

```xml
<PerformanceScenario>
  <ReturnUnfavorable>
    <RHPOrFirstCallDateOrFirstCallDate>-0.0120</RHPOrFirstCallDateOrFirstCallDate>
  </ReturnUnfavorable>
  <ReturnModerate>
    <RHPOrFirstCallDateOrFirstCallDate>0.0540</RHPOrFirstCallDateOrFirstCallDate>
  </ReturnModerate>
  <ReturnFavorable>
    <RHPOrFirstCallDateOrFirstCallDate>0.1080</RHPOrFirstCallDateOrFirstCallDate>
  </ReturnFavorable>
  <ReturnStress>
    <RHPOrFirstCallDateOrFirstCallDate>-0.2750</RHPOrFirstCallDateOrFirstCallDate>
  </ReturnStress>
  <PortfolioPastPerformanceDisclosureRequired>YES</PortfolioPastPerformanceDisclosureRequired>
</PerformanceScenario>
```

The child element name `<RHPOrFirstCallDateOrFirstCallDate>` is awkward — it is a schema artefact reflecting the fact that the same field is used for fixed-RHP products (where it carries the RHP value) and for autocallable products (where it carries the value at the first call date). For a straight UCITS, the interpretation is always "at RHP".

**The four values in turn**. A moderate annual return of +5.40% per year over the five-year RHP represents the median of the historical-return distribution — the honest central estimate of what an investor might expect. The unfavourable scenario at −1.20% per year represents the 10th percentile of the distribution: a plausible but pessimistic outcome. The favourable scenario at +10.80% per year is the 90th percentile. The stress scenario at −27.50% per year is the extreme tail, derived from the worst historical episodes in the measurement window; this scenario is deliberately much worse than the unfavourable one to illustrate that equity investments can suffer severe drawdowns.

A KID generator reads these four values, compounds them over the RHP, applies them to the standard 10,000 EUR illustrative investment, and renders the resulting monetary outcomes on the KID performance table. For the Europa Growth Fund, the moderate scenario of +5.40% per year over five years produces an outcome of approximately 13,000 EUR on a 10,000 EUR initial investment — the figure a retail investor sees in the "What could I get in return?" section of the KID.

`<PortfolioPastPerformanceDisclosureRequired>` is `YES` for any fund that meets the PRIIPs Annex VIII conditions (a UCITS with at least one year of history), requiring the KID to link to the past performance document. For the Europa Growth Fund, which has been operating for several years, the flag is `YES`.

### 8.4.6 Costs in the PRIIPs Format

The `<Costs>` block decomposes the PRIIPs cost structure into three sub-blocks: `<OneOff>`, `<Ongoing>`, and `<Incidental>`. Each sub-block carries the cost components in the PRIIPs-specific breakdown:

```xml
<Costs>
  <OneOff>
    <EntryCost>0.0500</EntryCost>
    <EntryCostsAcquired>0.0000</EntryCostsAcquired>
    <ExitCostAtRHP>0.0000</ExitCostAtRHP>
    <SlidingExitCostIndicator>NO</SlidingExitCostIndicator>
  </OneOff>
  <Ongoing>
    <OtherCost>0.0025</OtherCost>
    <ManagementCosts>0.0150</ManagementCosts>
    <Transaction>0.0012</Transaction>
  </Ongoing>
  <Incidental>
    <ExistringIncidentalCostsPortfolio>NO</ExistringIncidentalCostsPortfolio>
    <ExistingIncidentalCostsPortfolio>NO</ExistingIncidentalCostsPortfolio>
  </Incidental>
</Costs>
```

A few points that the naive reader should be warned about. The `<Transaction>` field inside `<Ongoing>` carries the portfolio transaction costs — the same concept as EMT's `<TransactionCosts>` but at the same decimal-percent scale. The `<ManagementCosts>` field carries the management fee plus other administrative and operational running costs, which is a *superset* of the `<ManagementFee>` field in EMT's `<CostsAndChargesExAnte>/<Fund>`. A producer filling both templates must take care that the EPT's `<ManagementCosts>` is at least as large as the EMT's `<ManagementFee>`, and the difference, if any, reflects non-management administrative running costs that PRIIPs bundles into the management bucket but MiFID II breaks out separately.

The two similarly named children of `<Incidental>` — `<ExistringIncidentalCostsPortfolio>` and `<ExistingIncidentalCostsPortfolio>` — are not a typo in this book: they are two separate elements in the schema, and both are mandatory. The FinDatEx specification uses them to distinguish two types of incidental cost indicator, and the nearly identical spelling reflects a historical quirk of the template's field naming. A producer must populate both, and, in the absence of performance fees or carried interest, both are `NO`.

The `<Narratives>` section of `<EPTV2>` — a block of short free-text fields that populate the KID's narrative sections (intended target market description, investment objective, exit cost description, and so on) — is mandatory for all PRIIPs products. Its content is closed to a maximum character count and is intended to be reused verbatim on the final KID. For the Europa Growth Fund, the narrative fields are drawn from the fund's prospectus with minimal editorial adaptation to fit the character limits.

### 8.4.7 The EPT and EMT Cost Relationship

A critical practical point that is worth restating. EMT expresses cost figures as annual percentages, which is the MiFID II cost disclosure horizon. EPT expresses some cost figures over the recommended holding period as well — notably through the KID generator's downstream calculations, which aggregate the annual figures over the fund's RHP and display the result on the KID's "Costs over time" table. The input fields in `<PRIIPS_V20>` are still annualised decimals, but the downstream KID output amortises one-off costs across the RHP: for a 5% entry load and a 5-year RHP, the KID shows approximately 1% per year, and a 5-year investment horizon sees the full 5% taken at entry.

A consumer that reads "total cost of 1.87% per year" from EMT and "reduction in yield of 2.87% per year" from the KID generator for the same share class is not seeing a contradiction: the EMT number excludes the amortised entry load and the KID number includes it. Both figures are individually valid in their own disclosure contexts, and the difference reflects the different treatment of one-off costs under the two regulations.

---

## 8.5 EET — European ESG Template

The largest of the five templates by field count, and the most rapidly evolving of them. Embedded under `<DirectReporting>/<EET1.1.3>`.

### 8.5.1 SFDR and the Sustainability Regulatory Wave

SFDR — the Sustainable Finance Disclosure Regulation — is the regulatory cornerstone of European sustainable finance, and arguably the most consequential single piece of fund regulation of the last five years. It entered into force in March 2021, with its technical standards (the Level 2 RTS) becoming applicable in January 2023. SFDR sits inside a larger sustainability framework that includes the EU Taxonomy Regulation (which defines what counts as "environmentally sustainable" at the activity level), the Corporate Sustainability Reporting Directive (CSRD, which requires companies to publish sustainability data that fund managers can then consume), and a growing body of country-specific national regulations.

The mechanics of SFDR run primarily through three articles that classify the intensity of a fund's sustainability integration:

- **Article 6** — no specific ESG orientation. The fund discloses sustainability risks that are material to its investment decisions (which every fund must do), but it does not claim to pursue any particular sustainability outcome. This is the default classification for funds that do not incorporate ESG considerations beyond risk management.
- **Article 8** — "light green". The fund *promotes* environmental or social characteristics among its investment decisions, without making sustainability the overriding objective. Most European actively managed funds that market themselves as ESG-integrated, best-in-class, or exclusion-based fall into this category. Article 8 is a broad tent, and the precise definition of "promoting" characteristics is the subject of continuous clarification from ESMA and national regulators.
- **Article 9** — "dark green". The fund has *sustainable investment* as its specific objective, in the sense defined by SFDR Article 2(17). This is a narrower category, with stricter disclosure and allocation requirements. Article 9 funds must invest predominantly in assets that meet the SFDR definition of sustainable investment, and must apply the "do no significant harm" (DNSH) test to their holdings.

The **EU Taxonomy** is a separate but related framework that defines, at the level of individual economic activities, which ones qualify as environmentally sustainable. It currently covers climate change mitigation and climate change adaptation as its two primary environmental objectives, with four further objectives (water, circular economy, pollution prevention, biodiversity) progressively being added. A fund's Taxonomy alignment is the percentage of its portfolio investments whose underlying economic activities are Taxonomy-aligned, and it is reported separately from the SFDR classification.

**Principal Adverse Impacts (PAI)** are a list of fourteen mandatory indicators of negative sustainability impacts, published by the European Supervisory Authorities as part of the SFDR Level 2 RTS. Asset managers must disclose PAI values both at the entity level (aggregate across all their products) and, for Article 8 and Article 9 products, at the product level. The fourteen indicators cover greenhouse gas emissions, exposure to fossil fuels, biodiversity damage, water emissions, hazardous waste, violations of international norms, gender pay gaps, and exposure to controversial weapons.

The collective data burden of SFDR, the Taxonomy, and PAI is large, and FinDatEx addressed it with the **EET** — a template with several hundred fields that carries all the structured data points a European distributor or pre-contractual-disclosure generator needs.

### 8.5.2 Structure of the EET Module

EET is embedded in FundsXML at `<DirectReporting>/<EET1.1.3>`. The outer `EET1.1.3` element is the template-version container, of type `EETsType1.1.3`, which carries one or more `<EET1.1.3>` children of type `EETReportType1.1.3`. The inner-outer element reuse is a schema quirk — FinDatEx uses the same versioned string for the wrapper and for each report entry — but the sequence is one wrapper, one or more report entries. Each report entry corresponds to one share class (or one product at whatever level the template specification requires).

The `EETReportType1.1.3` type arranges the EET payload into several top-level sections:

1. `<DataSetInformation>` — an outer wrapper (the doubly-nested name is intentional in the schema) that contains an inner `<DataSetInformation>` with the file-level metadata and a `<ManufacturerInformation>` block;
2. `<GeneralFinancialInstrumentInformation>` — product identification (ISIN, name, currency);
3. `<MainCriterias>` — the top-level SFDR product-type classification;
4. `<MiFIDIDDTargetMarket>` — how the product fits into the MiFID II sustainability preferences framework;
5. `<ScreeningCriteria>` — exclusion and screening strategies;
6. `<TaxonomyAlignedInvestments>` — the EU Taxonomy alignment percentages (optional but populated for Article 8 and Article 9 funds);
7. `<PrincipalAdverseIndicators>` — the fourteen mandatory PAI values and the optional additional indicators (optional but populated for Article 8 and Article 9 funds that consider PAIs).

Groups 6 and 7 are by far the largest by field count, because they carry the structured numerical data that SFDR Level 2 mandates. The mandatory minimum is a surprisingly small subset of the full template — most of the numerical PAI and Taxonomy fields are optional, conditional on the fund's SFDR article and its PAI-consideration flag. An Article 6 fund that does not consider PAIs can produce a valid EET with only a handful of fields populated; an Article 8 fund with full PAI consideration and a Taxonomy disclosure is where the file grows to its full size.

The minimal mandatory structure of one `<EET1.1.3>` entry is surprisingly compact:

```xml
<EET1.1.3>
  <EET1.1.3>
    <DataSetInformation>
      <DataSetInformation>
        <Version>V1.1.3</Version>
        <Producer>
          <Name>Europa Asset Management S.A.</Name>
          <LEI>529900T8BM49AURSDO55</LEI>
          <Email>eet@europa-am.lu</Email>
        </Producer>
        <FileGeneration>2026-03-31T18:30:00Z</FileGeneration>
        <DataReporting>
          <SFDRPreContractual>Y</SFDRPreContractual>
          <SFDRPeriodic>Y</SFDRPeriodic>
          <SFDREntityLevel>Y</SFDREntityLevel>
          <MiFID>Y</MiFID>
          <IDD>Y</IDD>
        </DataReporting>
      </DataSetInformation>
      <ManufacturerInformation>
        <Name>Europa Asset Management S.A.</Name>
        <CodeType>L</CodeType>
        <Code>529900T8BM49AURSDO55</Code>
        <Email>esg@europa-am.lu</Email>
        <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
      </ManufacturerInformation>
      <ManufacturerWebsiteInformationStewardshipAndEngagement>https://www.europa-am.lu/sustainability</ManufacturerWebsiteInformationStewardshipAndEngagement>
    </DataSetInformation>
    <GeneralFinancialInstrumentInformation>
      <IdentifyingData>LU2031234567</IdentifyingData>
      <TypeOfIdentification>1</TypeOfIdentification>
      <Name>Europa Growth Fund R EUR ACC</Name>
      <Currency>EUR</Currency>
    </GeneralFinancialInstrumentInformation>
    <MainCriterias>
      <SFDRProductType>8</SFDRProductType>
      <ConsidersPrincipleAdverseImpact>Y</ConsidersPrincipleAdverseImpact>
    </MainCriterias>
    <MiFIDIDDTargetMarket>
      <EndClientSustainabilityPreferences_Considered>Y</EndClientSustainabilityPreferences_Considered>
    </MiFIDIDDTargetMarket>
    <ScreeningCriteria>
      <ExistingNegativeScreeningStrategy>Y</ExistingNegativeScreeningStrategy>
    </ScreeningCriteria>
  </EET1.1.3>
</EET1.1.3>
```

Note the two features that are easy to stumble over. First, the double nesting of the version element name: the outer `<EET1.1.3>` is the wrapper, and each inner `<EET1.1.3>` is a single report entry. A file with several share classes emits several inner entries inside one outer wrapper. Second, the double nesting of `<DataSetInformation>` inside `<DataSetInformation>` — the outer is a section wrapper, the inner is the metadata block, and a `<ManufacturerInformation>` sibling of the inner `<DataSetInformation>` completes the outer section. The EET schema is, in this respect, more awkward than either EMT or EPT, and a producer building the block by hand benefits from keeping a validated template file as a copy source.

The `<DataReporting>` flags inside the inner `<DataSetInformation>` declare which regulatory contexts the EET instance supports. An `SFDRPreContractual=Y` value means the file is suitable to populate the SFDR pre-contractual disclosure; `SFDRPeriodic=Y` means it supports the annual periodic disclosure; `MiFID=Y` and `IDD=Y` mean the file carries the data needed for the MiFID II / IDD sustainability preferences assessment. The Europa Growth Fund supports all five regulatory uses.

### 8.5.3 SFDR Article Classification

The entry point for any EET consumer is the single field that determines which version of the disclosure the fund must produce: **under which SFDR article is the fund classified?**

The `<MainCriterias>/<SFDRProductType>` field carries the classification as a single-digit string: `0` for "not in SFDR scope" (some structured products and non-EU AIFs), `6` for Article 6, `8` for Article 8, or `9` for Article 9. The **Europa Growth Fund is an Article 8 fund**, so `<SFDRProductType>8</SFDRProductType>`.

The Europa Growth Fund promotes environmental and social characteristics through the integration of ESG criteria into its active investment process — specifically, it applies a best-in-class screen that tilts the portfolio towards companies with stronger ESG profiles relative to their sector peers, and it excludes companies in controversial sectors (tobacco, controversial weapons, thermal coal extraction above a certain threshold). It does not, however, have "sustainable investment" as its overriding objective in the Article 9 sense — the fund's primary investment objective remains the long-term capital appreciation of its investors through a diversified European equity portfolio, and the ESG integration is a *means* rather than the *end*.

The `<ConsidersPrincipleAdverseImpact>` flag alongside `<SFDRProductType>` is the second-most important field in the EET: it declares whether the fund considers Principal Adverse Impacts at the *product* level. For Article 8 and Article 9 products, setting this flag to `Y` opens the door to a much larger PAI section in the template; setting it to `N` tells the consumer that the fund does not report PAI at the product level and that the optional PAI section will be absent. The Europa Growth Fund considers PAIs, so the flag is `Y`.

Article 8 classification brings concrete disclosure obligations that the EET must carry:

- **Which environmental or social characteristics does the fund promote?** For the Europa Growth Fund: reduction of carbon intensity relative to the benchmark (MSCI Europe), avoidance of companies with major ESG controversies, and a tilt towards companies with diverse boards.
- **What methodology is used to measure and demonstrate the promotion?** For the Europa Growth Fund: a proprietary ESG scoring methodology that combines data from MSCI ESG, Sustainalytics, and the fund's own analyst assessments, applied at the security level in the portfolio construction process.
- **What minimum share of investments is sustainable within the meaning of SFDR?** For the Europa Growth Fund: 30% of the portfolio is committed to SFDR-sustainable investments, defined as companies whose primary economic activity meets the DNSH criteria and whose operations comply with minimum safeguards.
- **Which principal adverse impacts does the fund consider at the product level?** See §8.5.4.

All of these questions map to specific optional fields in the EET schema — each with its own FinDatEx field number (20200, 20210, 20220, and so on) and its own constraint on when it must be populated. A producer that fills the EET correctly for an Article 8 fund populates a substantial subset of the optional fields, even though none of them are schema-mandatory. A consumer that receives an Article 8 EET with only the five mandatory fields filled in would accept the file as schema-valid but flag it as semantically incomplete.

Article 9 funds would have additional and stricter disclosures: a description of the specific sustainability objective being pursued, the binding elements of the investment strategy, the reference benchmark (for passive Article 9 funds), and the methodology to demonstrate alignment with the Paris Agreement or other relevant international frameworks. The Europa Growth Fund, as an Article 8 fund, does not populate these fields; they appear in the EET schema but are left empty for Article 8 classifications.

### 8.5.4 PAI Fields and Taxonomy Alignment

The fourteen mandatory PAI indicators live inside the optional `<PrincipalAdverseIndicators>` section of `EETReportType1.1.3`, organised into subgroups by theme: `ClimateAndEnvironmentRelatedIndicators` (greenhouse gas emissions, carbon footprint, energy, biodiversity, water, waste) and `SocialAndEmployeeMatters` (UN Global Compact violations, gender pay gap, board diversity, controversial weapons).

The fourteen mandatory PAI indicators divide into two groups.

**Environmental PAIs** (nine indicators):

1. GHG emissions (Scope 1, Scope 2, Scope 3, and total) of investee companies
2. Carbon footprint of the portfolio
3. GHG intensity of investee companies
4. Exposure to companies active in the fossil fuel sector
5. Share of non-renewable energy consumption and production of investee companies
6. Energy consumption intensity per high impact climate sector
7. Activities negatively affecting biodiversity-sensitive areas
8. Emissions to water
9. Hazardous waste and radioactive waste ratio

**Social and employee-related PAIs** (five indicators):

10. Violations of the UN Global Compact principles and the OECD Guidelines for Multinational Enterprises
11. Lack of processes and compliance mechanisms to monitor compliance with those principles
12. Unadjusted gender pay gap of investee companies
13. Board gender diversity of investee companies
14. Exposure to controversial weapons (anti-personnel mines, cluster munitions, chemical weapons, biological weapons)

Each PAI is quantified either as a numerical value (for indicators with a natural numeric measure, such as GHG emissions or carbon intensity) or as a percentage exposure (for indicators that are effectively binary at the company level, such as controversial weapons exposure). The schema carries each indicator as a small structured type with sub-fields for value, strategy, and coverage — capturing the fact that a reported PAI value is only as reliable as the share of the portfolio for which underlying data was available.

A critical and practically difficult point: **not all portfolio companies report PAI data**. Asset managers must fill the gaps in their PAI coverage through a combination of issuer-reported data (where available), third-party data provider estimates (MSCI ESG, Sustainalytics, ISS ESG, Moody's ESG are the main providers), and modelled values from industry benchmarks. The EET distinguishes between measured and estimated values through dedicated flags, so that consumers can assess the data quality of each indicator. A PAI value marked as "estimated" is weaker evidence than a value marked as "reported", and a downstream consumer (for example, a sustainability-focused distributor) may treat the two differently in its own product evaluation.

**Taxonomy Alignment** is reported separately from PAI, inside the optional `<TaxonomyAlignedInvestments>` section, and is expressed as the percentage share of the portfolio whose underlying investments are Taxonomy-aligned. Fields include the minimum committed alignment (separately including and excluding sovereign bonds), the methodology used for the calculation (revenue-based, CapEx-based, or OpEx-based), the share of transitional and enabling activities, and the breakdown by the six environmental objectives. The calculation runs from the investee company's reported turnover, capital expenditure, or operational expenditure that comes from Taxonomy-eligible economic activities. For a European equity fund like the Europa Growth Fund, Taxonomy alignment typically falls in the range of 15% to 35%, depending on the sector allocation and on how many of the portfolio companies have begun to report their Taxonomy alignment (CSRD is progressively expanding the reporting population).

### 8.5.5 The EET in Practice

For the March 2026 delivery of the Europa Growth Fund, the EET instance contains the mandatory skeleton shown in §8.5.2 plus a populated `<TaxonomyAlignedInvestments>` section and a populated `<PrincipalAdverseIndicators>` section — together amounting to several dozen fields. The full instance is carried in Appendix D as part of the complete sample file. The abbreviated version in §8.9 below — showing only the mandatory skeleton — is the shape of the EET entry, with the understanding that a production-grade Article 8 fund emits substantially more content than the bare minimum.

---

## 8.6 EFT — European Feedback Template

The lightest of the five templates, and the one that runs in the reverse direction — from distributor to manufacturer rather than from manufacturer to distributor. Embedded under `<DirectReporting>/<EFTs>`.

### 8.6.1 What EFT Is and Why It Exists

MiFID II does not treat the manufacturer-distributor relationship as a one-way street. Beyond the manufacturer's obligation to deliver EMT, EPT, and EET *to* the distributor, there is a corresponding obligation on the distributor to provide **feedback** *back* to the manufacturer. The feedback covers questions that only the distributor can answer: how is the product selling in practice, do the actual buyers match the manufacturer's target market, are there client complaints, has the distributor identified any product governance issues?

The obligation sits within MiFID II's product governance framework — specifically, under the requirement that manufacturers and distributors work together to ensure ongoing product suitability. Without systematic feedback from distributors, a manufacturer cannot know whether its product is being sold to the clients it was designed for, and cannot update its target market definition or product governance arrangements in response to real-world evidence.

**EFT** is the FinDatEx template that standardises this feedback. It is created by the **distributor** and sent to the **manufacturer**, typically once a year (the minimum frequency under MiFID II) but sometimes more often when the manufacturer wants quarterly data. The content covers distribution statistics, target market alignment, and product governance observations.

The key operational consequence of the reverse direction is that **EFT does not appear in a fund's own monthly delivery**. The Europa Growth Fund's 31 March 2026 delivery flows from Europa Asset Management S.A. *to* its distributors, and it carries EMT, EPT, EET, and TPT but not EFT, because the fund's manufacturer is not the party producing feedback. EFT would appear in a separate delivery flowing from each of the fund's distributors *back* to Europa Asset Management S.A., on the distributor's own schedule. §8.9 will reflect this absence in the complete example block.

### 8.6.2 Structure of the EFT Module

The FundsXML embedding follows the same wrapper pattern as the other templates. The `<EFTs>` element (of type `EFTType`) is the container, and each child `<EFT>` (of type `EFTReportType`) is one feedback report. A report has three mandatory sections:

1. `<DataSetInformation>` — the file-level metadata, split into `ReportInformationAndScope` (version, generation timestamp, reporting period, and the `M`/`D`/`B` reference target market flag for whether the deviations are measured against the Manufacturer's, the Distributor's, or Both target markets), `SubmitterEntityInformation` (the distributor's name, identifier, identifier type, and position in the distribution chain), and `ManufacturerEntityInformation` (the recipient manufacturer's equivalent fields);
2. `<GeneralFinancialInstrumentInformation>` — product identification (ISIN, identification type, name, and total number of transactions for the period);
3. optional `<DeviationReportManufacturerTargetMarketPerspective>` and `<DeviationReportDistributorTargetMarketPerspective>` blocks — the actual feedback data, broken down into `Sales_OTM_NTM` (sales outside target market or in negative target market) and `Widening` sub-blocks.

The mandatory minimum is small. A distributor that observed no target-market deviations during the reporting period can emit a valid EFT with only the three mandatory sections populated and no deviation reports — effectively a "nil return" that communicates "we distributed the product, we reviewed the target market alignment, we observed no issues".

A complete minimal EFT entry:

```xml
<EFTs>
  <EFT>
    <DataSetInformation>
      <ReportInformationAndScope>
        <Version>V1</Version>
        <FileGeneration>2026-04-05T08:00:00Z</FileGeneration>
        <PeriodStartData>2026-01-01</PeriodStartData>
        <PeriodEndData>2026-03-31</PeriodEndData>
        <ReferenceTargetMarket>B</ReferenceTargetMarket>
      </ReportInformationAndScope>
      <SubmitterEntityInformation>
        <Name>Nordbank Privatkunden AG</Name>
        <Identifier>5299001NORDBANK00001</Identifier>
        <IdentifierType>L</IdentifierType>
        <PositionInTheDistributionChain>D</PositionInTheDistributionChain>
      </SubmitterEntityInformation>
      <ManufacturerEntityInformation>
        <Name>Europa Asset Management S.A.</Name>
        <Identifier>529900T8BM49AURSDO55</Identifier>
        <IdentifierType>L</IdentifierType>
      </ManufacturerEntityInformation>
    </DataSetInformation>
    <GeneralFinancialInstrumentInformation>
      <IdentifyingData>LU2031234567</IdentifyingData>
      <TypeOfIdentification>1</TypeOfIdentification>
      <Name>Europa Growth Fund R EUR ACC</Name>
      <TotalNumberOfTransactions>1243</TotalNumberOfTransactions>
    </GeneralFinancialInstrumentInformation>
    <DeviationReportManufacturerTargetMarketPerspective>
      <Sales_OTM_NTM>
        <RetailInvestorTypeAndSelfService>0</RetailInvestorTypeAndSelfService>
        <RetailInvestorTypeAndExecutionWithSuitabilityTest>0</RetailInvestorTypeAndExecutionWithSuitabilityTest>
        <KnowledgeAndExperienceAndSelfService>2</KnowledgeAndExperienceAndSelfService>
        <KnowledgeAndExperienceAndWithSuitabilityTest>0</KnowledgeAndExperienceAndWithSuitabilityTest>
      </Sales_OTM_NTM>
    </DeviationReportManufacturerTargetMarketPerspective>
  </EFT>
</EFTs>
```

Reading the block: a hypothetical distributor (Nordbank Privatkunden AG) reports on the Q1 2026 period. The reference target market is `B` (Both) — the distributor checked deviations against both the manufacturer's target market and its own refined distributor target market. The distributor processed 1,243 transactions in the R-EUR-ACC share class during the period. The deviation report shows that all 1,243 transactions were aligned on the Retail Investor Type dimension (0 deviations) but that 2 transactions were identified as deviations on the Knowledge and Experience dimension under self-service execution — presumably, two clients with "Basic" knowledge level bought the fund via the bank's online execution-only channel despite the product's target market being Informed / Advanced. The distributor is required to disclose this, and the manufacturer will read it during the annual product governance review.

This feedback, once processed by Europa Asset Management S.A., becomes one of the inputs to the fund's annual product governance review. If several distributors were reporting consistent misalignment on one of the target market dimensions, the manufacturer would be expected to investigate — perhaps the product's risk characteristics have drifted, or the target market definition was drawn too narrowly for the actual investor base.

For the purpose of this chapter, the important point is that EFT exists, runs in the reverse direction, and is absent from the 31 March 2026 delivery of the Europa Growth Fund produced by Europa Asset Management S.A. The next section, on TPT, returns to a template that *is* present in the delivery.

---

## 8.7 TPT — Tripartite Template for Solvency II

The template that gives insurance investors the data they need to hold fund positions under Solvency II. Embedded under `<IndirectReporting>/<TripartiteTemplateSolvencyII_V6>`.

### 8.7.1 Solvency II and Insurance Reporting

Solvency II is the European insurance regulation that has governed the capital adequacy of insurance companies since 2016. Its central mechanism is the **Solvency Capital Requirement (SCR)** — a risk-based capital charge calculated from the insurance company's asset and liability positions, designed to ensure that the insurer can survive a one-in-two-hundred-year adverse event over a one-year horizon. The SCR is updated at least annually and is reported to the national supervisor through the Quantitative Reporting Templates (QRTs) that Solvency II specifies.

Many European insurance companies hold fund positions as part of their investment portfolios. When a life insurer invests 50 million EUR in the Europa Growth Fund through an insurance mandate or a unit-linked wrapper, the Europa Growth Fund position becomes part of the insurer's asset base, and the insurer must calculate its SCR including that position. Solvency II requires this calculation to be done on a **lookthrough basis** — not by treating the fund as a single opaque asset with an estimated overall risk, but by looking through to the fund's underlying holdings (the individual European equities, cash positions, and currency forwards we met in Chapter 6) and applying the Solvency II risk modules to each underlying.

The problem is that the insurer does not have direct access to the fund's portfolio detail. Without a standardised data exchange, the insurer would have to approximate the lookthrough data or negotiate bilateral data-sharing arrangements with each fund manager it held positions with. The operational burden would be enormous.

**TPT** — the Tripartite Template — is the FinDatEx solution. The name comes from the three parties historically involved in defining the template: asset managers (who produce fund data), fund administrators (who hold the position details), and insurers (who need the data for Solvency II). TPT standardises the lookthrough data into a single well-defined format that every European insurer knows how to consume. An asset manager that produces TPT for each of its funds makes those funds "Solvency II ready" for any insurance investor, without needing bilateral negotiation.

TPT has become operationally critical for any fund that wants to be held by insurance money. The Europa Growth Fund carries insurance investors among its I-EUR-DIST class unit holders, and Europa Asset Management S.A. therefore emits TPT in every monthly delivery of the fund's data.

### 8.7.2 Structure of TPT V6

In FundsXML, TPT lives at `<IndirectReporting>/<TripartiteTemplateSolvencyII_V6>`. The element name carries the version number explicitly: `V6` is FinDatEx Tripartite Template version 6.0 of March 2022, which accompanies the current Solvency II technical standards. The earlier versions (`TripartiteTemplateSolvencyII`, `TripartiteTemplateSolvencyII_V5`) are still in the schema for backward compatibility.

The type `TripartiteTemplateSolvencyIIType_V6` is a thin wrapper whose content is a sequence of `<Portfolio>` children, each of type `SolvencyIIPortfolioType_V6`. The term "portfolio" here follows the Solvency II convention — one `<Portfolio>` corresponds to one fund or one share class — not the FundsXML convention where `<Portfolio>` refers to a holdings list inside `FundDynamicData`. The two uses of the same word are a source of confusion; within this section the Solvency II meaning prevails.

A `<Portfolio>` has the following mandatory fields at the top level:

- `<TPTVersion>` — must be exactly the string `V6.0`. This is a regulatory versioning marker inside the schema, distinct from the element name.
- `<PortfolioID>` — a `SIISecurityCodificationType_V6` pair (CodificationSystem integer plus Code string) identifying the fund.
- `<PortfolioName>` — the fund's name.
- `<PortfolioCurrency>` — an ISO 4217 currency code.
- `<TotalNetAssets>` — the fund's total net asset value in portfolio currency.
- `<ValuationDate>` — the date the portfolio inventory is valid for.
- `<ReportingDate>` — the date the data refers to (typically the end of the reporting period).
- `<CompleteSCRDelivery>` — `Y` if the producer has computed all SCR contributions for each position and included them in the file; `N` otherwise. The distinction matters because a `Y` file lets the insurance consumer use the pre-computed SCR inputs directly, whereas an `N` file requires the insurer to compute its own SCR from the raw positions.
- `<Positions>` — the holdings lookthrough, containing one or more `<Position>` children of type `SIIPositionType_V6`.

Each position inside `<Positions>` is itself a complex block with mandatory sub-fields including `InstrumentCIC` (the four-character CIC code classifying the instrument type and country), `InstrumentCode` (the ISIN or alternative identifier), `InstrumentName`, `Valuation` (with six mandatory monetary sub-fields in quotation currency and portfolio currency plus market-exposure figures), and `AdditionalInformation` (a structured block of optional QRT-specific sub-fields).

A position for a single equity holding — SAP SE — looks like this:

```xml
<Position>
  <InstrumentCIC>DE31</InstrumentCIC>
  <InstrumentCode>
    <CodificationSystem>1</CodificationSystem>
    <Code>DE0007164600</Code>
  </InstrumentCode>
  <InstrumentName>SAP SE</InstrumentName>
  <Valuation>
    <QuotationCurrency>EUR</QuotationCurrency>
    <MarketValueQC>7450000.00</MarketValueQC>
    <CleanValueQC>7450000.00</CleanValueQC>
    <MarketValuePC>7450000.00</MarketValuePC>
    <CleanValuePC>7450000.00</CleanValuePC>
    <PositionWeight>0.0300</PositionWeight>
    <MarketExposureQC>7450000.00</MarketExposureQC>
    <MarketExposurePC>7450000.00</MarketExposurePC>
    <MarketExposureWeight>0.0300</MarketExposureWeight>
  </Valuation>
  <AdditionalInformation/>
</Position>
```

The six mandatory monetary fields — `MarketValueQC`, `CleanValueQC`, `MarketValuePC`, `CleanValuePC`, `MarketExposureQC`, `MarketExposurePC` — carry the position's market value and market exposure in both quotation currency (QC, the currency the instrument is quoted in) and portfolio currency (PC, the fund's base currency). For an equity holding in a single-currency fund, the QC and PC values are identical, and the clean values equal the market values (there is no accrued interest on equity). For a foreign-currency equity or for a bond with accrued coupon, the QC and PC values differ and the clean and market values differ respectively. The `PositionWeight` expresses the share of the fund's net assets that the position represents, as a decimal (`0.0300` = 3% of NAV).

The four-character **CIC (Complementary Identification Code)** is an EIOPA-defined classification standardised in the Solvency II regulation. Its format is `CC` (ISO country code) followed by two digits, where the first digit identifies the asset category (1 = government bond, 2 = corporate bond, 3 = listed equity, 4 = unlisted equity, and so on) and the second digit refines it. `DE31` means "listed equity in Germany, asset sub-category 1"; `FR31` would be the French equivalent, `CH31` the Swiss equivalent. The CIC is the single most important classification field in TPT, because the Solvency II SCR calculation uses it as the primary key for applying the standard-formula shock factors — 39% for EEA listed equities, 49% for non-EEA listed equities, different percentages for different bond categories.

`<AdditionalInformation>` is mandatory but may be empty (as in the example), because all of its children are optional. Its optional children cover the fund custodian name, infrastructure investment flags, Type 1 private equity eligibility, counterparty sector codes, collateral eligibility, and collateral market value — fields that are relevant only for specific asset categories.

### 8.7.3 TPT in Practice

The **holdings lookthrough** section of TPT is by far the largest part of the template by row count: a fund with 150 equity positions plus three cash balances plus two FX forwards produces 155 `<Position>` entries, each with ten to twenty sub-fields. A full delivery of the Europa Growth Fund's TPT is therefore several thousand lines of XML, which is why the example in §8.9 shows only a single representative position.

The TPT lookthrough exists *in addition to* the native `<Portfolios>` block in `FundDynamicData` (Chapter 6). The two representations of the portfolio are not the same — they serve different consumers and use different field formats — but they describe the same economic reality. A consumer that reads both should find that the position list and the aggregate market values reconcile, within small rounding tolerances. Producers must maintain consistency between the two views: a mismatch between the native portfolio and the TPT holdings section is a data quality error that a validating consumer should flag.

An important decision for TPT producers: **should the holdings lookthrough be complete, or should it be aggregated?** The standard answer for Solvency II is *complete* — every individual holding should appear in TPT, not just sector or country aggregates. The reason is that precise SCR calculations depend on the characteristics of individual issuers (their rating, their country of risk, their sector) and aggregation would lose the information that the calculation needs. The cost of the full lookthrough is a much larger TPT section per fund, and deliveries covering many funds can reach tens or hundreds of thousands of TPT position rows. Producers who emit batched deliveries need to watch the file sizes and, where necessary, split batches into smaller chunks.

The Europa Growth Fund's TPT for 31 March 2026 carries the full 155-position lookthrough, with `<CompleteSCRDelivery>` set to `N` (the manufacturer provides the raw positions but leaves the SCR computation to each consuming insurer, which is the more common pattern because insurers prefer to run the calculation through their own internal models). An insurance consumer reads the block, runs its own SCR calculation, and determines the capital charge that the fund position adds to the insurer's overall SCR. The entire workflow is repeatable, auditable, and standardised — exactly what Solvency II requires.

---

## 8.8 ESAP — European Single Access Point

The final regulatory topic of the chapter is not a FinDatEx template but an EU infrastructure initiative that affects how FundsXML deliveries reach their ultimate consumers.

### 8.8.1 What ESAP Is

The **European Single Access Point** is an EU-wide regulatory disclosure portal whose phased rollout began in 2026. Its purpose is to provide a single, centralised point through which investors, analysts, regulators, and the general public can retrieve public financial and sustainability disclosures from across the European financial sector. Before ESAP, these disclosures were scattered across national regulators, company websites, industry databases, and private data vendors, with no common format, no common access protocol, and no way to aggregate them across borders without bilateral data integration.

ESAP is part of the **Capital Markets Union** (CMU), the longer-running EU initiative to reduce the fragmentation of European capital markets. The CMU goals include making it easier for companies to raise capital across borders, for investors to access cross-border investment opportunities, and for retail savers to compare products from different countries. ESAP supports the last of these goals by ensuring that the regulatory data needed for comparison is available in one place, in structured machine-readable formats.

For funds specifically, ESAP aggregates several kinds of regulatory disclosure: SFDR pre-contractual and periodic disclosures (the Article 6/8/9 information that every fund must provide under the sustainable finance regulation); PRIIPs KIDs (for retail products); prospectuses for regulated investment products; and sustainability reports under CSRD. Not every fund disclosure goes to ESAP — bilateral deliveries (a monthly FundsXML file from Europa Asset Management S.A. to Nordbank Privatkunden AG, for example) are private contractual exchanges and are outside ESAP's remit. What ESAP covers is the category of disclosures that are supposed to be publicly available under their respective regulations.

### 8.8.2 FundsXML and ESAP

ESAP is a consumer of regulatory disclosures rather than an element of the FundsXML schema. As of the current FundsXML 4.2.8 release there is **no dedicated ESAP metadata element inside `ControlData` or elsewhere in the schema**, and no schema-level mechanism that declares "this file is destined for ESAP". That is a conscious choice: ESAP's submission channel is a separate pipeline governed by ESMA-maintained specifications, and the FundsXML association has so far held back from adding ESAP-specific elements until the submission format stabilises across the phased rollout.

In practice, a producer that publishes to ESAP typically does so by transforming an existing FundsXML document (or a reg-reporting-only projection of it) into whatever format the ESAP gateway currently accepts for the category in question — which, depending on the category, may be XBRL, ESMA-specified XML, or increasingly a FundsXML subset aligned with the relevant FinDatEx template. The routing, the authentication, and the acceptance rules all live outside the FundsXML schema, in the pipeline code that sits between the producer's systems and the ESAP API.

A brief list of practical consequences for a fund data pipeline in 2026:

- **Private bilateral deliveries remain private**. The monthly FundsXML file from a manufacturer to one of its distributors is not automatically published to ESAP; it is a private contractual exchange.
- **SFDR disclosures are the main ESAP category that touches a typical fund pipeline today**. A manufacturer's quarterly SFDR pre-contractual disclosure — which overlaps substantially with the content of the EET in `DirectReporting` — is the document that goes to ESAP, typically through a separate submission channel.
- **Expect the situation to evolve**. Each FundsXML minor release since 4.2 has added hooks or allowed extensions for progressively more ESAP-oriented metadata, and future versions may well introduce dedicated ESAP elements. Chapter 10 will return to the operational pattern of publishing to ESAP as part of a production pipeline.

For the Europa Growth Fund, the 31 March 2026 delivery is a private bilateral delivery — from Europa Asset Management S.A. to one of its distributors — and does not go through ESAP. A separate quarterly SFDR disclosure, due at the end of Q1, is the artefact that reaches ESAP. The two artefacts share some underlying data but are routed, packaged, and authenticated differently.

---

## 8.9 The Complete RegulatoryReportings Block for the Europa Growth Fund

The integrative close of the chapter. A `<RegulatoryReportings>` block containing four of the five templates — EMT, EFT-free, EET, TPT, and PRIIPs — for the 31 March 2026 delivery of the Europa Growth Fund R-EUR-ACC share class.

**EFT is absent**, because this delivery flows from the manufacturer to distributors rather than in the reverse direction. The absence is structural and correct, and the block below reflects it. The four modules that *are* present — `EMT_V4_2`, `EET1.1.3`, `TripartiteTemplateSolvencyII_V6`, and `PRIIPS_V20` — have been introduced in the preceding sections; here we see them side by side in one container. Because the embedding uses the two branches `DirectReporting` and `IndirectReporting`, the templates appear in their respective branches rather than as flat siblings.

The abbreviated block is:

```xml
<RegulatoryReportings>

  <DirectReporting>

    <!-- EMT: MiFID II costs and target market -->
    <EMT_V4_2>
      <FinancialInstrument>
        <DataSetInformation>
          <Version>V4</Version>
          <ProducerName>Europa Asset Management S.A.</ProducerName>
          <ProducerLEI>529900T8BM49AURSDO55</ProducerLEI>
          <ProducerEmail>emt@europa-am.lu</ProducerEmail>
          <FileGenerationDateTime>2026-03-31T18:00:00Z</FileGenerationDateTime>
          <DataReportingTargetMarket>Y</DataReportingTargetMarket>
          <DataReportingExAnte>Y</DataReportingExAnte>
          <DataReportingExPost>N</DataReportingExPost>
        </DataSetInformation>
        <GeneralInformation>
          <Code>LU2031234567</Code>
          <CodificationSystem>1</CodificationSystem>
          <InstrumentName>Europa Growth Fund R EUR ACC</InstrumentName>
          <InstrumentCurrency>EUR</InstrumentCurrency>
          <InstrumentPerformanceFee>N</InstrumentPerformanceFee>
          <InstrumentDistributionCash>N</InstrumentDistributionCash>
          <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
          <ProductType>U</ProductType>
          <ManufacturerName>Europa Asset Management S.A.</ManufacturerName>
          <ManufacturerLEI>529900T8BM49AURSDO55</ManufacturerLEI>
          <LeveragedOrContingentLiability>N</LeveragedOrContingentLiability>
          <Fund>
            <FundShareClassWithoutRetrocession>N</FundShareClassWithoutRetrocession>
          </Fund>
        </GeneralInformation>
        <TargetMarket>
          <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
          <InvestorType>
            <Retail>Y</Retail>
            <Professional>Y</Professional>
            <EligibleCounterparty>Y</EligibleCounterparty>
          </InvestorType>
          <KnowledgeAndExperience>
            <BasicInvestor>Y</BasicInvestor>
            <InformedInvestor>Y</InformedInvestor>
            <AdvancedInvestor>Y</AdvancedInvestor>
          </KnowledgeAndExperience>
          <AbilityToBearLosses>
            <CompatibleWithClientsWhoCanNotBearCapitalLoss>N</CompatibleWithClientsWhoCanNotBearCapitalLoss>
            <CompatibleWithClientsWhoDoNotNeedCapitalGuarantee>Y</CompatibleWithClientsWhoDoNotNeedCapitalGuarantee>
            <CompatibleWithClientsWhoCanBearLossBeyondCapital>N</CompatibleWithClientsWhoCanBearLossBeyondCapital>
          </AbilityToBearLosses>
          <RiskTolerance>
            <PRIIPSMethodology>4</PRIIPSMethodology>
          </RiskTolerance>
          <ClientObjectives>
            <ReturnProfile>
              <ClientLookingForPreservation>N</ClientLookingForPreservation>
              <ClientLookingForCapitalGrowth>Y</ClientLookingForCapitalGrowth>
              <ClientLookingForIncome>N</ClientLookingForIncome>
            </ReturnProfile>
            <MinimumRecommendedHoldingPeriod>
              <Years>5</Years>
            </MinimumRecommendedHoldingPeriod>
            <IntendedCompatibleWithClientsHavingSustainabilityPreferences>Y</IntendedCompatibleWithClientsHavingSustainabilityPreferences>
          </ClientObjectives>
          <DistributionStrategy>
            <ExecutionOnly>B</ExecutionOnly>
            <ExecutionWithCheckOrNonAdvisedServices>B</ExecutionWithCheckOrNonAdvisedServices>
            <InvestmentAdvice>B</InvestmentAdvice>
            <PortfolioManagement>B</PortfolioManagement>
          </DistributionStrategy>
        </TargetMarket>
        <CostsAndChargesExAnte>
          <Fund>
            <GrossMaxEntryCostNonAcquired>0.0500</GrossMaxEntryCostNonAcquired>
            <MaxExitCost>0.0000</MaxExitCost>
            <OngoingCosts>0.0175</OngoingCosts>
            <ManagementFee>0.0150</ManagementFee>
            <TransactionCosts>0.0012</TransactionCosts>
            <IncidentalCosts>0.0000</IncidentalCosts>
          </Fund>
          <CostsReferenceDate>2026-03-31</CostsReferenceDate>
        </CostsAndChargesExAnte>
      </FinancialInstrument>
    </EMT_V4_2>

    <!-- EFT: absent — this delivery flows from manufacturer to distributor,
         not distributor to manufacturer, so there is no feedback content. -->

    <!-- EET: SFDR and sustainability data (mandatory minimum only) -->
    <EET1.1.3>
      <EET1.1.3>
        <DataSetInformation>
          <DataSetInformation>
            <Version>V1.1.3</Version>
            <Producer>
              <Name>Europa Asset Management S.A.</Name>
              <LEI>529900T8BM49AURSDO55</LEI>
              <Email>eet@europa-am.lu</Email>
            </Producer>
            <FileGeneration>2026-03-31T18:30:00Z</FileGeneration>
            <DataReporting>
              <SFDRPreContractual>Y</SFDRPreContractual>
              <SFDRPeriodic>Y</SFDRPeriodic>
              <SFDREntityLevel>Y</SFDREntityLevel>
              <MiFID>Y</MiFID>
              <IDD>Y</IDD>
            </DataReporting>
          </DataSetInformation>
          <ManufacturerInformation>
            <Name>Europa Asset Management S.A.</Name>
            <CodeType>L</CodeType>
            <Code>529900T8BM49AURSDO55</Code>
            <Email>esg@europa-am.lu</Email>
            <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
          </ManufacturerInformation>
          <ManufacturerWebsiteInformationStewardshipAndEngagement>https://www.europa-am.lu/sustainability</ManufacturerWebsiteInformationStewardshipAndEngagement>
        </DataSetInformation>
        <GeneralFinancialInstrumentInformation>
          <IdentifyingData>LU2031234567</IdentifyingData>
          <TypeOfIdentification>1</TypeOfIdentification>
          <Name>Europa Growth Fund R EUR ACC</Name>
          <Currency>EUR</Currency>
        </GeneralFinancialInstrumentInformation>
        <MainCriterias>
          <SFDRProductType>8</SFDRProductType>
          <ConsidersPrincipleAdverseImpact>Y</ConsidersPrincipleAdverseImpact>
        </MainCriterias>
        <MiFIDIDDTargetMarket>
          <EndClientSustainabilityPreferences_Considered>Y</EndClientSustainabilityPreferences_Considered>
        </MiFIDIDDTargetMarket>
        <ScreeningCriteria>
          <ExistingNegativeScreeningStrategy>Y</ExistingNegativeScreeningStrategy>
        </ScreeningCriteria>
        <!-- Additional Article 8 sections (TaxonomyAlignedInvestments,
             PrincipalAdverseIndicators, etc.) are elided here and carried
             in full in Appendix D. -->
      </EET1.1.3>
    </EET1.1.3>

  </DirectReporting>

  <IndirectReporting>

    <!-- TPT: Solvency II lookthrough (abbreviated to one representative position) -->
    <TripartiteTemplateSolvencyII_V6>
      <Portfolio>
        <TPTVersion>V6.0</TPTVersion>
        <PortfolioID>
          <CodificationSystem>1</CodificationSystem>
          <Code>LU2031234567</Code>
        </PortfolioID>
        <PortfolioName>Europa Growth Fund R EUR ACC</PortfolioName>
        <PortfolioCurrency>EUR</PortfolioCurrency>
        <TotalNetAssets>248500000.00</TotalNetAssets>
        <ValuationDate>2026-03-31</ValuationDate>
        <ReportingDate>2026-03-31</ReportingDate>
        <CompleteSCRDelivery>Y</CompleteSCRDelivery>
        <Positions>
          <Position>
            <InstrumentCIC>DE31</InstrumentCIC>
            <InstrumentCode>
              <CodificationSystem>1</CodificationSystem>
              <Code>DE0007164600</Code>
            </InstrumentCode>
            <InstrumentName>SAP SE</InstrumentName>
            <Valuation>
              <QuotationCurrency>EUR</QuotationCurrency>
              <MarketValueQC>7450000.00</MarketValueQC>
              <CleanValueQC>7450000.00</CleanValueQC>
              <MarketValuePC>7450000.00</MarketValuePC>
              <CleanValuePC>7450000.00</CleanValuePC>
              <PositionWeight>0.0300</PositionWeight>
              <MarketExposureQC>7450000.00</MarketExposureQC>
              <MarketExposurePC>7450000.00</MarketExposurePC>
              <MarketExposureWeight>0.0300</MarketExposureWeight>
            </Valuation>
            <AdditionalInformation/>
          </Position>
          <!-- Remaining 154 positions elided; full lookthrough in Appendix D. -->
        </Positions>
      </Portfolio>
    </TripartiteTemplateSolvencyII_V6>

    <!-- EPT (inside PRIIPS_V20): KID-input data for the PRIIPs disclosure -->
    <PRIIPS_V20>
      <EPTV2>
        <DataSetInformation>
          <Version>V21</Version>
          <Data_ReportingNarratives>YES</Data_ReportingNarratives>
          <DataReportingCosts>YES</DataReportingCosts>
          <DataReportingAdditionalRequirementsGermanMOPs>NO</DataReportingAdditionalRequirementsGermanMOPs>
          <AdditionalInformationStructuredProductsRIY>NO</AdditionalInformationStructuredProductsRIY>
        </DataSetInformation>
        <GeneralPortfolioInformation>
          <PortfolioManufacturerName>Europa Asset Management S.A.</PortfolioManufacturerName>
          <PortfolioManufacturerGroupName>Europa Financial Group</PortfolioManufacturerGroupName>
          <PortfolioManufacturerLEI>529900T8BM49AURSDO55</PortfolioManufacturerLEI>
          <PortfolioID>
            <CodificationSystem>1</CodificationSystem>
            <Code>LU2031234567</Code>
          </PortfolioID>
          <PortfolioName>Europa Growth Fund R EUR ACC</PortfolioName>
          <PortfolioCurrency>EUR</PortfolioCurrency>
          <GeneralReferenceDate>2026-03-31</GeneralReferenceDate>
          <PortfolioPRIIPSCategory>2</PortfolioPRIIPSCategory>
          <IsAnAutocallableProduct>NO</IsAnAutocallableProduct>
        </GeneralPortfolioInformation>
        <RiskAssessment>
          <ValuationFrequency>252</ValuationFrequency>
          <IS_Flexible>NO</IS_Flexible>
          <Existing_Credit_Risk>NO</Existing_Credit_Risk>
          <SRI>4</SRI>
          <IsSRIAdjusted>NO</IsSRIAdjusted>
          <MRM>4</MRM>
          <Recommended_Holding_Period>5</Recommended_Holding_Period>
          <HasAContractualMaturityDate>NO</HasAContractualMaturityDate>
          <Liquidity_Risk>L</Liquidity_Risk>
        </RiskAssessment>
        <PerformanceScenario>
          <ReturnUnfavorable>
            <RHPOrFirstCallDateOrFirstCallDate>-0.0120</RHPOrFirstCallDateOrFirstCallDate>
          </ReturnUnfavorable>
          <ReturnModerate>
            <RHPOrFirstCallDateOrFirstCallDate>0.0540</RHPOrFirstCallDateOrFirstCallDate>
          </ReturnModerate>
          <ReturnFavorable>
            <RHPOrFirstCallDateOrFirstCallDate>0.1080</RHPOrFirstCallDateOrFirstCallDate>
          </ReturnFavorable>
          <ReturnStress>
            <RHPOrFirstCallDateOrFirstCallDate>-0.2750</RHPOrFirstCallDateOrFirstCallDate>
          </ReturnStress>
          <PortfolioPastPerformanceDisclosureRequired>YES</PortfolioPastPerformanceDisclosureRequired>
        </PerformanceScenario>
        <Costs>
          <OneOff>
            <EntryCost>0.0500</EntryCost>
            <EntryCostsAcquired>0.0000</EntryCostsAcquired>
            <ExitCostAtRHP>0.0000</ExitCostAtRHP>
            <SlidingExitCostIndicator>NO</SlidingExitCostIndicator>
          </OneOff>
          <Ongoing>
            <OtherCost>0.0025</OtherCost>
            <ManagementCosts>0.0150</ManagementCosts>
            <Transaction>0.0012</Transaction>
          </Ongoing>
          <Incidental>
            <ExistringIncidentalCostsPortfolio>NO</ExistringIncidentalCostsPortfolio>
            <ExistingIncidentalCostsPortfolio>NO</ExistingIncidentalCostsPortfolio>
          </Incidental>
        </Costs>
        <Narratives>
          <ComprehensionAlert>NO</ComprehensionAlert>
          <IntendedTargetMarketRetailInvestor>Retail investors with basic or informed knowledge of equity funds, willing to accept market risk, seeking long-term capital growth over at least five years.</IntendedTargetMarketRetailInvestor>
          <InvestmentObjective>The fund aims to achieve long-term capital growth by investing primarily in European large-cap equities that meet the manager's sustainability criteria.</InvestmentObjective>
          <OtherMaterialyRelevantRiskNarrative>No other materially relevant risks beyond market and sustainability risk.</OtherMaterialyRelevantRiskNarrative>
          <TypeUnderlyingInvestmentOption>UCITS SICAV</TypeUnderlyingInvestmentOption>
          <CapitalGuarantee>NO</CapitalGuarantee>
          <OneOffCostPortfolioExitCostDescription>No exit cost is charged at redemption.</OneOffCostPortfolioExitCostDescription>
          <OngoingCostsPortfolioManagementCostsDescription>Ongoing management and operating costs deducted from fund NAV.</OngoingCostsPortfolioManagementCostsDescription>
          <DoCostsDependOnInvestedAmount>NO</DoCostsDependOnInvestedAmount>
        </Narratives>
      </EPTV2>
    </PRIIPS_V20>

  </IndirectReporting>

</RegulatoryReportings>
```

A three-pass reading of the block closes the example.

**First pass — presence and absence**. Four templates are present: EMT (MiFID II, under `DirectReporting`), EET (SFDR, also under `DirectReporting`), TPT (Solvency II, under `IndirectReporting`), and EPT inside `PRIIPS_V20` (PRIIPs, also under `IndirectReporting`). One template — EFT — is absent, and the absence is both visible (marked by a comment) and deliberate. A consumer who expects EFT in this delivery is confused about the delivery's direction; a consumer who correctly identifies the delivery as manufacturer-to-distributor accepts the absence as normal. The two-branch structure (`DirectReporting` versus `IndirectReporting`) is itself a structural feature that is worth highlighting: every FundsXML `RegulatoryReportings` block either places templates into these branches or is empty.

**Second pass — shared identification across modules**. Every one of the four present templates contains the same fund identifier (`LU2031234567`, the R-EUR-ACC share class) and the same manufacturer LEI (`529900T8BM49AURSDO55`, Europa Asset Management S.A.). A consumer can read any single module and verify which fund and which manufacturer it refers to. The reference date (31 March 2026) appears under each module's own date field and is implicit in the enclosing `ContentDate` from the `ControlData` block (Chapter 4). The four modules are, in this sense, different views of the same product at the same moment in time.

**Third pass — module-specific disclosures**. Each module contributes its own distinctive content. EMT provides the target market classification, the forward-looking cost disclosure (1.75% ongoing + 0.12% transaction), and the distribution strategy. EET provides the SFDR Article 8 classification, the PAI consideration flag, the MiFID II sustainability preferences flag, and the existence of a negative screening strategy — all in their mandatory minimum form, with the full Article 8 disclosures (Taxonomy alignment, detailed PAI indicators) deferred to the unabbreviated version in Appendix D. TPT provides the fund's total NAV (248.5 million EUR), the 155-position lookthrough (abbreviated here to a single SAP SE position), and the CIC-coded asset classification that drives the insurer's SCR calculation. EPT, inside `PRIIPS_V20`, provides the SRI of 4, the four PRIIPs performance scenarios (from −27.5% annualised in stress to +10.8% favourable), the PRIIPs-specific cost breakdown, and the nine mandatory narrative fields that populate the KID's text sections. Each consumer reads the module relevant to its own purpose and ignores the others.

The complete block — with all 120+ EMT fields, the full PRIIPs v2.0 field set, all several hundred EET fields, and the full 155-position TPT lookthrough — appears in Appendix D as part of the end-to-end Europa Growth Fund sample file. This chapter's version is deliberately compressed to focus on the structural patterns.

---

## 8.10 Common Pitfalls

The following short list captures the mistakes that, in our experience, cause the greatest share of regulatory-module-related production incidents.

- **Templates placed at the wrong level of `RegulatoryReportings`**. A producer places `<EMT_V4_2>` directly inside `<RegulatoryReportings>` instead of inside `<DirectReporting>`, or places `<TripartiteTemplateSolvencyII_V6>` inside `<DirectReporting>` instead of `<IndirectReporting>`. The file fails schema validation. The rule is fixed by the XSD: EMT, EFTs, and EET belong in `DirectReporting`; PRIIPS_V20 and TripartiteTemplateSolvencyII_V6 belong in `IndirectReporting`; and neither branch may be skipped by lifting its children up one level.

- **Mixing `Y`/`N` with `YES`/`NO`**. EMT's `EMTYesNoType` uses single-letter `Y`/`N`/`Neutral`; EPT's (and the PRIIPS_V20's) `YesNoType` uses `YES`/`NO` in full; EET's `EETYesNoType` uses `Y`/`N`. A producer that copies field values mechanically from one template to another will produce `Y` in a PRIIPs field where the schema expects `YES`, and the file fails validation. The fix is to use template-specific helpers when emitting the boolean fields and to test each template under xmllint.

- **EMT and EPT cost fields confused**. A consumer takes the annual total from EMT and treats it as the five-year-amortised figure that PRIIPs uses, or vice versa. The two figures are related (one-year costs × RHP, roughly) but they are not interchangeable, and the disclosure document generated will show the wrong figure. The rule: match the cost horizon to the disclosure horizon, and read the template appropriate to the disclosure being produced.

- **SFDR Article classification missing or wrong in EET**. A producer emits an EET block with `<SFDRProductType>` populated with the wrong digit — typically `6` (Article 6) on an Article 8 fund because an internal classification table had the wrong default. The consumer processes the fund as Article 6 and silently suppresses its ESG disclosures, misrepresenting the product. The field is mandatory and its value is business-critical; every EET must carry the correct value, and the producer's QA pipeline should cross-check against the fund's prospectus.

- **TPT lookthrough inconsistent with the native portfolio**. The `<Positions>` block inside TPT shows 155 positions, but the `<Portfolios>` block in the same delivery shows 153, because the TPT generator and the portfolio generator were run on different snapshots. An insurance consumer notices the discrepancy and raises a data quality flag. The fix is to produce both blocks from a single canonical source and to validate internal consistency before emitting.

- **Old template version in use**. A producer emits `<EMT_V4_1>` while its consumer expects `<EMT_V4_2>`. Both elements exist in the schema (FundsXML keeps every historical FinDatEx version), but a consumer's processing pipeline may only handle the current version, and the older element is silently ignored. The fix is to coordinate template version upgrades bilaterally and to migrate to the current version as soon as it is supported by all relevant consumers.

- **EFT included in a manufacturer delivery**. A producer (the asset manager) mistakenly includes an `<EFTs>` block in its own manufacturer-to-distributor delivery, perhaps because the producer's generator offers an "emit all templates" option and the operator forgot to deselect EFT. Consumers either reject the module as misplaced or log warnings. The fix is to enforce the direction rule in the producer's tooling: manufacturers produce EMT/EPT/EET/TPT; distributors produce EFT; neither produces the other's content.

- **Minimal EET emitted for an Article 8 fund**. A producer emits only the mandatory minimum of the EET — the skeleton shown in §8.9 — for an Article 8 fund that should carry a substantial additional payload of Taxonomy alignment and PAI data. The file passes schema validation but fails downstream semantic checks at the distributor, which expects the richer Article 8 content and flags the delivery as semantically incomplete. The fix is to populate the optional Article 8 / Article 9 sections whenever the fund is classified accordingly, even though the schema does not force the content.

---

## 8.11 Key Takeaways

- `RegulatoryReportings` is the fifth and final main area of a FundsXML delivery, a root-level sibling of `<Funds>` and `<AssetMasterData>`. Inside, it immediately splits into `<DirectReporting>` and `<IndirectReporting>`, and the five FinDatEx templates are distributed between the two branches.
- FinDatEx maintains the templates; FundsXML embeds them. The two organisations have clearly separated responsibilities — FinDatEx decides the *what*, FundsXML decides the *how*. Each FinDatEx template version appears in the FundsXML schema as its own versioned element (e.g. `EMT_V4_2`, `EET1.1.3`, `PRIIPS_V20`, `TripartiteTemplateSolvencyII_V6`).
- **EMT** (under `DirectReporting`, as `EMT_V4_2`) carries MiFID II cost and target market data at the share-class level and is the operationally most important template for retail distribution. Its `FinancialInstrument` complex type has five mandatory sections: `DataSetInformation`, `GeneralInformation`, `TargetMarket`, `CostsAndChargesExAnte`, and the optional `CostsAndChargesExPost`.
- **EPT** (under `IndirectReporting`, as `PRIIPS_V20/EPTV2`) provides the data that populates the PRIIPs KID: the SRI on the 1-to-7 scale, the four performance scenarios as annualised returns over the recommended holding period, the PRIIPs-specific cost breakdown, and the mandatory narrative fields. Several of the boolean fields use `YES`/`NO` in full, unlike EMT's single-letter flags.
- **EET** (under `DirectReporting`, as `EET1.1.3`) covers SFDR classification (Articles 6, 8, 9), the fourteen mandatory Principal Adverse Impacts, and the EU Taxonomy alignment. It is by far the largest template by field count, with several hundred mostly optional fields organised into sections for main criteria, MiFID/IDD target market, screening, Taxonomy alignment, and PAI. The mandatory minimum is compact, but Article 8 and Article 9 funds are expected to populate the optional sections substantively.
- **EFT** (under `DirectReporting`, as `EFTs`) flows in the reverse direction (distributor to manufacturer) and therefore does not appear in manufacturer deliveries like the Europa Growth Fund's monthly file. EFT carries distribution statistics, reference target market specification, and deviation reports under the manufacturer or distributor target market perspective.
- **TPT** (under `IndirectReporting`, as `TripartiteTemplateSolvencyII_V6`) provides lookthrough data for Solvency II SCR calculations by insurance investors. Each `Portfolio` entry carries mandatory top-level fields (`TPTVersion=V6.0`, `PortfolioID`, `PortfolioName`, `PortfolioCurrency`, `TotalNetAssets`, `ValuationDate`, `ReportingDate`, `CompleteSCRDelivery`) plus one or more `Position` entries, each with an InstrumentCIC classification and six mandatory valuation sub-fields.
- **ESAP** is the EU-wide access point for regulatory disclosures, live in phased rollout from 2026. FundsXML 4.2.8 has no schema-level ESAP metadata element; ESAP routing is handled by the production pipeline outside the schema, and producers publish SFDR disclosures, prospectuses, and similar public documents through a separate ESMA-specified channel.
- The Europa Growth Fund's 31 March 2026 delivery carries EMT, EPT, EET, and TPT — but not EFT — reflecting the direction of the delivery and the reporting needs of its consumers.

We have now covered all five main areas of a FundsXML delivery — `ControlData`, `Funds`, `AssetMasterData`, the four substructures of `FundDynamicData`, and `RegulatoryReportings`. What remains are the less-frequently-used but operationally important schema areas: the `Documents` section for factsheets and signed attachments, XML digital signatures, `CustomAttributes` for proprietary extensions, and country-specific additions. Chapter 9 closes Part II of the book with these advanced topics.
