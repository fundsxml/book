<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 5 — Funds, Sub-Funds, and Share Classes

*Static and dynamic fund information*

---

## 5.1 Setting the Scene: Inside the Envelope

At the end of Chapter 4 we had a ControlData block for the Europa Growth Fund's month-end delivery on 31 March 2026. We knew who had sent it, whom it was meant for, which day it referred to, and that it was the first delivery of its stream. What we did not know was anything about the fund itself. This chapter fills that gap. It is the longest chapter in the book — forty pages — because the `Fund` element is the element about which everything else in a FundsXML delivery eventually revolves, and because it is also the element where newcomers most often get lost.

Before we begin, one pedagogical decision deserves to be stated up front. The Europa Growth Fund, as we learned in Chapter 1, is a European UCITS equity fund distributed across eleven countries. In reality it has three distinct share classes: a retail euro-denominated accumulating class, a retail Swiss-franc-denominated currency-hedged accumulating class, and an institutional euro-denominated distributing class. Every field we discuss in this chapter exists at one of two levels: either at the level of the fund as a whole, or at the level of an individual share class. The two levels are easy to mix up, and a reader who has to track both at once while also learning about identifiers, classification, and fees is going to struggle.

We therefore take the chapter in four parts. **Part I** (§5.2 to §5.7) pretends the Europa Growth Fund has exactly one share class and treats every topic as though it lived cleanly on the fund element. **Part II** (§5.8 to §5.11) relaxes the pretence, puts the three share classes back, and walks through the topics on which the fund-level picture branches. **Part III** (§5.12 and §5.13) treats the dynamic data — NAVs, total net assets, performance figures — in the light of the share-class structure we have just built. **Part IV** (§5.14 to §5.17) covers umbrella funds, assembles the complete `Fund` element, lists the common pitfalls, and summarises the chapter. By the end of Part I the reader should feel comfortable reading a fund's identity; by the end of Part II the reader should be able to talk fluently about share classes; by the end of the chapter the reader should be able to read a complete `Fund` element on sight and know which of the remaining chapters of Part II of the book each fragment of it belongs to.

By the end of this chapter, you should be able to:

- identify which information in FundsXML belongs to a fund and which belongs to a share class;
- produce and populate every mandatory field of the `Fund` element for a realistic European UCITS;
- choose the right identifier for every jurisdiction in which a fund is distributed;
- model multilingual fund data without duplicating documents per language;
- distinguish fund-level, share-class-level, and regulatory-level representations of fees and risk indicators;
- read a complete `Fund` element with multiple share classes on sight and point at the pieces each later chapter of the book treats in depth.

---

## 5.2 The Fund Element in Context

Inside every FundsXML delivery, immediately after the ControlData envelope, sits a [`<Funds>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds) container. The container is a simple list: it contains one or more [`<Fund>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund) elements, each representing a single fund. The list is the schema's way of saying that one delivery may describe more than one fund at a time.

Two production patterns dominate in practice. The first pattern, **one fund per file**, is the one we have been assuming so far: the Europa Growth Fund is delivered in its own FundsXML file, the `<Funds>` container holds exactly one `<Fund>`, and the distributor's dispatcher routes the file by looking at the DataSupplier and the fund's ISIN. This pattern is common when the producer wants fine-grained control over who receives which fund — particularly where distribution agreements vary by country or share class. The second pattern, **several funds per file**, is more common in fund-administrator batches: a single file carries every fund the administrator serves for a given asset-management client, often several dozen at a time. The container form of `<Funds>` exists precisely so that the second pattern does not require a wrapper document of its own. Both patterns are valid FundsXML; the choice between them is a pipeline design decision, not a schema decision, and Chapter 12 will come back to it when it discusses integration into system landscapes.

Whichever pattern is used, each `<Fund>` element has the same shape. Four elements are mandatory and appear at the very top of every `<Fund>`; the rest follow the separation of static and dynamic data that we named in Chapter 3 as design principle 1, and are wrapped into an optional `<SingleFund>` container (for non-umbrella funds) or a `<Subfunds>` container (for umbrella structures, §5.14):

```xml
<Fund>
  <Identifiers>
    <!-- LEI of the fund and any other fund-level identifier -->
  </Identifiers>
  <Names>
    <!-- OfficialName, optionally MarketingName, ShortName, LanguageNames -->
  </Names>
  <Currency>EUR</Currency>
  <SingleFundFlag>true</SingleFundFlag>
  <FundStaticData>
    <!-- domicile, legal structure, classifications, benchmarks, ongoing costs, ... -->
  </FundStaticData>
  <FundDynamicData>
    <!-- fund-level total net assets, portfolio, fund-level benchmark values, ... -->
  </FundDynamicData>
  <SingleFund>
    <!-- SingleFundStaticData and the list of ShareClasses -->
  </SingleFund>
</Fund>
```

The shape deserves two observations. First, `Identifiers`, `Names`, `Currency`, and `SingleFundFlag` are **mandatory** and appear before the static/dynamic split. They establish the fund's identity before anything else; a `<Fund>` element that omits them is not schema-valid. Second, the static/dynamic split is not cosmetic. Many real pipelines ship `FundStaticData` only when something has changed — perhaps once a month, perhaps only when a new share class is launched or a fee is revised — while shipping a fresh `FundDynamicData` block every valuation day. Doing so is entirely legal: both [`FundStaticData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData) and [`FundDynamicData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData) are optional, a delivery may contain one, the other, or both, and consumers are expected to maintain the last-known state of each half independently. The DataOperation semantics of Chapter 4 apply to whichever half is present.

The [`<SingleFund>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund) wrapper is where the share-class structure lives. Newcomers often expect [`<ShareClasses>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses) to hang off `FundStaticData`, but the schema puts them one level higher: `Fund/SingleFund/ShareClasses`, as a sibling of the static/dynamic blocks rather than a child of the static one. The reason is that `<SingleFund>` is one of two alternatives — the other being `<Subfunds>` for umbrella structures — and making the choice a first-class sibling keeps the two cases symmetric. We take `<SingleFund>` as the running case for the whole chapter and return to `<Subfunds>` in §5.14.

**Figure 5.1 — `Funds` as a list**

```
                 <Funds>
                    │
     ┌──────────────┼──────────────┬──────────────┐
     │              │              │              │
  <Fund>         <Fund>         <Fund>         <Fund>
     │              │              │              │
  Static         Static         Static         Static
  Dynamic        Dynamic        Dynamic        Dynamic
```

Each of the `<Fund>` boxes is structurally independent of the others: a consumer that cares only about one fund can read that fund and stop without loss of correctness. The AssetMasterData library (Chapter 6) lives outside the `<Funds>` container, as we saw in Chapter 3, so that instruments shared between several funds in the same delivery can be described once and referenced many times. That cross-fund sharing is the subject of Chapter 6, not this one; Chapter 5 treats each `<Fund>` as though it were the only fund in the file.

---

## 5.3 FundStaticData vs FundDynamicData Revisited

Chapter 3 introduced the static/dynamic split as design principle 1. Now that we are about to populate each half, it is worth pausing to ask a more operational question: *which field goes where?* The principle is intuitive in the limit — a fund's legal name is static, its NAV is dynamic — but the middle is less obvious. Is the *launch date* of the fund static or dynamic? It never changes, so it sounds static, but many reference systems store it alongside performance data for historical calculations, which makes it feel dynamic. Is the fund's *ongoing charges* figure static? It is published once a year and does not move between publications, so it is static by default, but a producer that recomputes it on demand at every delivery could reasonably place it in the dynamic half. FundsXML takes a position on each of these questions, and the position is worth understanding because it is the organising principle of every `Fund` element in the book.

The rule of thumb is straightforward. A field belongs in `FundStaticData` if, in the ordinary course of operating a fund, it would *not* need to be re-transmitted to downstream consumers on every valuation day. A field belongs in `FundDynamicData` if, in the ordinary course of operating a fund, it *would*. Table 5.1 summarises where the commoner fields land.

**Table 5.1 — Where the commoner fields of a fund live**

| Mandatory header | `FundStaticData` | `FundDynamicData` | `SingleFund` / `<ShareClass>` |
|---|---|---|---|
| `Identifiers/LEI` (fund-level) | `DomicileCountry` | Fund-level `TotalAssetValues` | Per-class `Identifiers` (ISIN, GermanWKN, SwissValorenCode) |
| `Names` | `ListedLegalStructure` | Fund-level benchmark values | Per-class `Names`, `Currency`, `ShareClassType` |
| `Currency` | `InceptionDate` (fund) | Portfolio composition *(→ Chapter 6)* | `SubscriptionRestrictions`, `CurrencyHedgedFlag` |
| `SingleFundFlag` | `FundTexts` (strategy, risk, …) | | `Prices` and per-class `TotalAssetValues` |
| | `Classifications` | | `Fees`, `Distributions`, `Flows` *(→ Chapter 7)* |
| | `Benchmarks` (static) | | `PerformanceFigures` |
| | `OngoingCosts` | | `HighWatermark`, `InceptionDate` (per class) |
| | `SFDRProductType` | | `RegistrationCountries` |

Three lines of the table need commentary. **Portfolio composition** lives inside `FundDynamicData/Portfolios` — that is the reason the table lists it in the third column — but it is a large enough topic to deserve its own chapter, and this chapter does not treat it. Chapter 6 walks through every asset class and every position-level field. **Transactions** (subscriptions, redemptions, distributions, corporate actions) live at the share-class level: subscriptions and redemptions under `ShareClass/Flows`, dividend events under `ShareClass/Distributions`. They are the subject of Chapter 7. Sections §5.12 and §5.13 of this chapter will cover per-class NAVs, fund-level totals, and performance figures, and will elide portfolio and flow detail when we get there.

A fourth observation is worth stating while the table is in view. **Per-class dynamic data lives on each class, not in `FundDynamicData`.** NAV per unit, shares outstanding, per-class total net assets, per-class performance, per-class cash flows and distributions, and per-class portfolios all live inside the individual `<ShareClass>` element under `SingleFund/ShareClasses`. `FundDynamicData/TotalAssetValues` carries a single aggregate figure for the whole fund, and `FundDynamicData/Portfolios` carries a shared fund-level portfolio where classes are backed by a common asset pool. The split is not always intuitive at first reading; §5.12 returns to it with concrete examples.

The operational consequence of the split is worth stating plainly. In a pipeline designed with static/dynamic separation in mind, the producer's batch job runs in two phases. The first phase, triggered only when something in the fund's identity changes, emits a `FundStaticData` update — a new share class was launched, a fee was revised, a benchmark was switched. The second phase, triggered on every valuation day, emits a `FundDynamicData` update — today's NAVs, today's shares outstanding, today's portfolio, today's transactions. The two streams flow through the same FundsXML documents, are sequenced by the same DataOperation mechanics from Chapter 4, and are reconciled by the consumer into a single current-state picture. It is perfectly legal under the schema to ship both halves in every delivery — and many producers do, because the redundancy is cheap and the operational simplification is real. But the ability to split them is available when it matters.

---

## 5.4 Fund Identifiers — ISIN, WKN, LEI, Valor, and Friends

The first substantive field group of the chapter is the one most likely to trip up a first-time implementer. FundsXML carries *several* identifiers for each fund, and the reason is that no single identifier universe covers all of the jurisdictions and all of the consumers that European fund data touches. A German investor needs a WKN. A Swiss investor needs a Valor. A regulator needs an LEI. A cross-border distribution agreement is written around ISINs. A legacy Bloomberg terminal may only accept its own proprietary ticker. All of these identifiers coexist, none of them is individually sufficient, and the schema supports all of them at once.

### 5.4.1 The Hierarchy of Identifiers

Identifiers in FundsXML live at two levels, and both levels use exactly the same container: a [`<Identifiers>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/Identifiers) element (of schema type `IdentifiersType`) that carries a fixed set of named children — `ISIN`, `Bloomberg`, `CUSIP`, `GermanWKN`, `LEI`, `MexID`, `ReutersRIC`, `SEDOL`, `SwissValorenCode`, `SwiftBIC` — plus a repeatable `OtherID` escape hatch for everything the schema does not name. One `<Identifiers>` block sits at the top of the `<Fund>` element and carries the fund-level identifiers; a separate `<Identifiers>` block sits at the top of each `<ShareClass>` element and carries the share-class-level identifiers. The two use the same vocabulary but populate different fields.

Some identifiers — principally the **LEI**, together with any regulator-issued fund number — identify the fund as a legal entity. These are *fund-level* identifiers; they exist once per fund and do not care how many share classes the fund has, and they sit inside the fund's own `<Identifiers>` container. Others — **ISIN**, **GermanWKN**, **SwissValorenCode**, **CUSIP**, **Bloomberg ticker** — identify a separately investable unit, which in practice means a single share class. These are *share-class-level* identifiers; a fund with three share classes has three `<Identifiers>` blocks, one per class, each populated with the instrument codes of its own class.

For the remainder of Part I we are pretending that the Europa Growth Fund has exactly one share class, so the distinction does not yet matter for narrative purposes: whenever we talk about *the fund's ISIN* in this part, what we really mean is *the ISIN of its only share class*. Part II (§5.9) will put the share-class-level identifiers in their proper place inside each `<ShareClass>`. The only identifier that actually *belongs* at the fund level is the LEI, and it will remain there throughout. Note that **FundsXML uses the name `GermanWKN` for what German market participants usually call a WKN**, and **`SwissValorenCode` for what the Swiss call a Valor**. The rest of this chapter uses the short names *WKN* and *Valor* in prose and the schema names in XML fragments; readers writing code against the schema should prefer the long forms.

One point deserves to be made now, even before we look at any single identifier in detail: the **LEI of the fund is not the LEI of its asset manager**. Chapter 4 introduced the LEI of *Europa Asset Management S.A.* (`529900T8BM49AURSDO55`) as part of the `DataSupplier` block. The Europa Growth Fund itself, as a separate legal entity, has its own LEI — `549300ABCDEFGHIJKL34` — and it is this second identifier that appears in `Fund/Identifiers/LEI`, not the first. Confusing the two is a surprisingly common mistake among producers who have built their pipelines around a single "company LEI" and forgotten that a fund is a legal entity in its own right.

### 5.4.2 The Core Identifiers in Detail

We take the five most important identifier families in turn. Each entry below gives the structure of the identifier, its issuing body, the level at which FundsXML carries it, and the single most important operational rule associated with it.

**ISIN** (International Securities Identification Number) is a twelve-character alphanumeric code defined by ISO 6166. The first two characters are the country of issue, the next nine are a national identifier, and the twelfth is a check digit computed by the Luhn-like algorithm of the standard. ISINs are issued by national numbering agencies — in Luxembourg, the *Clearstream Banking* numbering agency — and are the primary key of cross-border fund distribution in Europe. Every separately investable share class has its own ISIN; a fund with three share classes has three ISINs. At the fund level, strictly speaking, there is no single ISIN — only the collection of its share classes' ISINs — but many producers expose the principal class's ISIN at `FundStaticData` level as a shortcut for display purposes. The schema tolerates this as long as the same ISIN also appears on its owning share class.

**WKN** (Wertpapierkennnummer) is a six-character alphanumeric code assigned by the German central numbering agency. It predates the ISIN by several decades and remains mandatory in German fact sheets, German regulator filings, and the displays of German retail broker systems. Every German-distributed share class has a WKN in addition to its ISIN; the two coexist and the same share class carries both. Producers who serve German consumers at any volume populate WKN for every distributed share class automatically.

**Valor** is a five- to nine-digit numeric code issued by SIX Financial Information in Switzerland. It is the Swiss counterpart to WKN: mandatory for distribution into Switzerland, mandatory for Swiss stock-exchange listings, and expected by every Swiss consumer of fund data. The Europa Growth Fund, which is distributed into Switzerland, carries Valor numbers on its CHF-hedged share class (and often on its EUR classes as well, since Valor can identify any security that a Swiss intermediary may hold on behalf of a client).

**LEI** (Legal Entity Identifier) is a twenty-character alphanumeric code defined by ISO 17442, issued by local operating units of the Global Legal Entity Identifier Foundation (GLEIF). Unlike ISIN, WKN, and Valor, the LEI identifies a *legal entity*, not a financial instrument. At the fund level, the LEI uniquely identifies the fund itself; at the umbrella level (which we will come to in §5.14), each sub-fund under the umbrella carries its own LEI and the umbrella carries another. LEIs are required for regulatory reporting under MiFID II, EMIR, AIFMD Annex IV, and SFDR, and producers who forget to populate them will find their deliveries rejected by regulator-facing consumers. Unlike the instrument identifiers, the LEI is also stable across corporate events — a rebranding, a merger, a translation of a legal name — which is why Chapter 4 recommended matching allowlists on LEI rather than on name.

**CUSIP** (nine-character, North-American) and **SEDOL** (seven-character, British) appear occasionally on European funds that are marketed to international investors or listed outside Europe. They are less common than the first four, and FundsXML carries them as optional fields when they apply.

**Table 5.2 — Fund identifier families**

| Schema element | Issuer | Level | Typical use |
|---|---|---|---|
| `ISIN` | National numbering agencies (ISO 6166) | Share class | Cross-border distribution, trading, reference data |
| `GermanWKN` | German WM-Datenservice | Share class | German factsheets, retail broker systems, BaFin filings |
| `SwissValorenCode` | SIX Financial Information (Switzerland) | Share class | Swiss distribution, SIX Swiss Exchange listings |
| `LEI` | GLEIF local operating units | Fund / sub-fund | Regulatory reporting under MiFID II, EMIR, AIFMD, SFDR |
| `CUSIP` | CUSIP Global Services (US/Canada) | Share class | Funds marketed to North-American investors |
| `SEDOL` | London Stock Exchange (UK) | Share class | British listings and broker systems |

### 5.4.3 OtherID — the Escape Hatch

No schema can enumerate every identifier that every consumer in every jurisdiction will ever need, and FundsXML does not try. For everything that the schema does not define explicitly — internal fund-administrator reference codes, national regulator codes, proprietary distributor identifiers, Morningstar fund IDs — there is the **`OtherID`** mechanism. An `OtherID` element sits inside `<Identifiers>` alongside the named children, carries a text value, and takes one of two attributes: `ListedType`, whose value is drawn from a long enumeration of recognised schemes (among them `INTERNAL FUND CODE`, `CSSF FUND CODE`, `BAFIN ID`, `AUSTRIAN FUND CODE`, `CNMV CODE`, `INAV BLOOMBERG LISTING CODE`, `REUTERS LISTING CODE`, and many others), or `FreeType`, an open string for schemes the enumeration does not cover. Consumers read the attribute to decide whether they recognise the scheme and, if so, how to interpret the value.

The escape hatch is valuable precisely because it is structured: unlike a generic "extra fields" blob, `OtherID` forces the producer to declare the scheme of every extra identifier, so that a consumer can decide field by field whether it knows what to do with each one. A typical production `<Identifiers>` block at the fund level carries the LEI and one or two `OtherID` entries — the producer's internal fund code under `ListedType="INTERNAL FUND CODE"`, perhaps the national regulator's fund code under `ListedType="CSSF FUND CODE"` for a Luxembourg fund. For producer-internal reference codes, `OtherID ListedType="INTERNAL FUND CODE"` is the idiomatic way to transport what some producers historically called a *DataSupplierFundID*; there is no dedicated element with that name in the schema.

The rule of discipline that matters is that an `OtherID` must **never** be used for an identifier that has a dedicated field. Writing the ISIN into an `<OtherID ListedType="...">ISIN</OtherID>` element instead of into the proper `<ISIN>` element is a recurring mistake — often the result of a mechanical generator that was configured before the producer learned about the dedicated element — and it breaks downstream consumers who look for ISIN at its expected location. The symptom is a consumer that "cannot find" the ISIN of a fund even though it is right there in the document; the fix is to move the identifier into its proper place and, often, to audit the producer for the same mistake on other fields.

---

## 5.5 Multilingual Names and Descriptions

Design principle 4 from Chapter 3 — *multi-language by design* — meets the practicalities of European fund distribution in this section. A single UCITS may be sold in eleven countries under the same ISIN with the same portfolio and the same investment policy, but with eleven different marketing names, eleven translations of its investment objective, and eleven versions of its risk-and-reward narrative. Producing eleven separate FundsXML documents, one per language, would defeat the point of a standard; FundsXML therefore allows every textual field to carry several language variants side by side, so that a single delivery can serve every distribution country at once.

### 5.5.1 The `Names` Container and the Language Attribute

FundsXML models fund names through a single [`<Names>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/Names) container (schema type `NamesType`) whose children are **named** rather than polymorphic. A producer that wants several language variants does *not* repeat a generic `<Name>` element with different `language` attributes at the top of `<Names>`. Instead, `<Names>` holds a sequence of specifically named children — `OfficialName`, `FullName`, `MarketingName`, `ShortName`, `PreviousName`, `DynLenNames`, `LanguageNames` — and only the last of these, `LanguageNames`, is a repeatable container in which individual `<Name>` elements each carry a `language` attribute. The design keeps the single-language fast path simple (one `<OfficialName>` and done) and concentrates the multilingual machinery in one place.

A complete Europa Growth Fund `<Names>` block therefore looks like this:

```xml
<Names>
  <OfficialName>Europa Asset Management Investments — Europa Growth Sub-Fund</OfficialName>
  <MarketingName>Europa Growth Fund</MarketingName>
  <ShortName>EGF</ShortName>
  <LanguageNames>
    <Name language="de">Europa Wachstumsfonds</Name>
    <Name language="fr">Europa Fonds de Croissance</Name>
    <Name language="it">Europa Fondo di Crescita</Name>
  </LanguageNames>
</Names>
```

Three things about this block are worth stating explicitly. First, the `<OfficialName>` is **mandatory** — every `<Names>` container must have exactly one, and it is the only element inside `<Names>` that is required. It carries the fund's primary canonical name in the producer's canonical language, typically the language of the governing jurisdiction. Second, `<MarketingName>` and `<ShortName>` are optional fields for the public-facing name and its compact abbreviation; when they are present they apply *across languages*, because a single marketing name and a single short code are what distributors and broker systems actually display. Third, the `language` attribute inside `<LanguageNames>` takes an ISO 639-1 code — *en*, *de*, *fr*, *it*, *es*, *nl*, and so on — and each `<Name language="xx">` element carries exactly one translation.

A consumer that needs a localised variant picks the matching `LanguageNames/Name`; if no variant matches its preferred locale, it falls back to the `<MarketingName>` (for display purposes), to the `<OfficialName>` (for legal purposes), or to a configured default language. The fallback discipline is a consumer-side concern; the producer's job is simply to populate as many language variants as the fund's distribution agreements require, and to populate them consistently. Producers should populate *all* relevant languages in every delivery, not only the language of the intended recipient. A single FundsXML file routed to a French distributor should still carry the German and Italian names alongside the French one, because downstream the distributor may feed the same file into a factsheet engine that renders in any of those languages. Filtering to a single language on the producer side is tempting and wrong.

### 5.5.2 Types of Names

The children of `<Names>` come in several shades, and they mean subtly different things. Confusing them is a routine cause of factsheets that display the wrong text.

**`OfficialName`** is the fund's full legal name as it appears in the prospectus and in any court or regulatory filing. It is mandatory, and it is the only name that the producer is obliged to populate. For the Europa Growth Fund the official name is *Europa Asset Management Investments — Europa Growth Sub-Fund*, reflecting the sub-fund relationship even in the standalone-looking listings of this chapter. The official name is typically held in a single canonical language matching the governing jurisdiction; when a jurisdiction requires translations of the legal name, the translations go into `LanguageNames` alongside the marketing translations.

**`FullName`** is an optional longer form that is used in umbrella structures to disambiguate a sub-fund from its umbrella. When a producer prefers to keep `OfficialName` as just the sub-fund's own name — *Europa Growth Sub-Fund* — the fully qualified *Umbrella SICAV — Europa Growth Sub-Fund* form goes into `FullName`. The two coexist and serve different display contexts.

**`MarketingName`** is the marketing or commercial name of the fund — the name that appears on fact sheets, client portals, and advertising. For the Europa Growth Fund this is simply *Europa Growth Fund*. It is the name the producer wants end-users to see; it is typically shorter and friendlier than the legal name and may differ from it substantially.

**`ShortName`** is an abbreviation or short code, used in compact displays such as tables and trading screens. For the Europa Growth Fund it is *EGF*. The short name is *not* intended to be multilingual: short codes are typically culturally neutral, and a single string serves all languages.

**`PreviousName`** carries the most recent previous name of the fund after a rebranding, along with an `@until` attribute that names the date on which the previous name ceased to apply. Consumers that maintain historical reference-data joins read the previous name alongside the current one so that older data with the old name can still be matched to the fund.

**`DynLenNames`** carries several length-constrained variants of the current name for display systems that truncate at fixed widths — a 16-character short form, a 32-character medium form, a 64-character long form. Producers use it when their consumers include legacy terminals that would otherwise butcher the marketing name. It is optional and rarely populated in modern deliveries.

**`LanguageNames`** is the container for translated variants, as we saw in §5.5.1. Each `<Name>` child inside it carries a two-letter ISO 639-1 `language` attribute and one translation.

Producer-internal reference codes — what some producers historically called a *DataSupplierFundID* — do **not** live inside `<Names>`. They live inside `<Identifiers>` as an `OtherID` entry with `ListedType="INTERNAL FUND CODE"`, as §5.4.3 described. This is worth saying twice because the historical name of the field misled an entire generation of integrators into looking for it in the wrong place.

### 5.5.3 `FundTexts` — Investment Objectives, Policies, and Narratives

Longer textual fields — *investment objective*, *investment policy*, *risk profile narrative*, *investor profile description* — do not live inside `<Names>`. They live in a separate container, `FundStaticData/FundTexts`, whose `<FundText>` children each carry one piece of free-form text alongside its metadata. These are the fields that feed factsheet generators and client-portal descriptions, and their quality determines whether a fund reads like a carefully prepared product or like a machine translation.

Each `<FundText>` element has the following shape. A `<Language>` child (mandatory) names the language of the content using an ISO 639 code. A `<Date>` child (mandatory) names the date on which the text is valid — important because investment-policy wording is revised periodically and consumers need to know which version they are reading. One of `<ListedType>` or `<UnlistedType>` (a mandatory choice) names the kind of text: the listed enumeration covers the most common regulated categories — `INVESTMENT STRATEGY`, `INVESTOR PROFILE`, `RISK DESCRIPTION`, `RISK MANAGEMENT`, `FEES`, `BENCHMARK`, `SUBS REDS`, `LEGAL INFORMATION`, `TAX INFORMATION`, `ANNUAL REPORT`, `SEMI ANNUAL REPORT` — and `<UnlistedType>` takes a short free-form label for text categories that the enumeration does not cover. An optional `<Title>` supplies a display title in the chosen language. A `<Content>` element (mandatory) carries the text itself. An optional `<CountriesWhereApplicable>` lists the distribution countries in which this text variant is permitted, for producers that ship jurisdiction-specific wording.

A fund that carries an investment objective in English and German therefore emits two `<FundText>` elements as siblings inside `<FundTexts>`, one per language, each with the same `<ListedType>INVESTMENT STRATEGY</ListedType>` and the same `<Date>`. A fund that additionally carries a risk description emits further `<FundText>` elements with `<ListedType>RISK DESCRIPTION</ListedType>`. A single `<FundTexts>` block in a realistic delivery typically contains between six and twenty entries, covering the main text categories in the main distribution languages.

Two rules of practice are worth following.

First, **the first sentence of `<Content>` must stand alone**. Many downstream consumers — compact fact-sheet templates, distributor search results, one-line product cards — truncate longer descriptions after a fixed number of characters, typically one hundred and fifty to two hundred. A description whose first sentence only makes sense in the context of the second will look mangled in every such consumer. Producers should write the first sentence as a self-contained summary and use the remaining sentences for elaboration.

Second, **do not embed HTML or other markup** in `<Content>`. Some consumers escape the markup, some pass it through, and some strip it entirely, and the resulting inconsistency is a well-known source of visible bugs. If a description needs formatting, handle the formatting on the consumer side, or use the root-level `<Documents>` section (Chapter 9) to deliver a separate rich-text version as a PDF or as structured `<BinaryData>`.

One interaction is worth noting here for later reference. Chapter 8 treats the FinDatEx regulatory templates (EMT, EPT, EET), and these templates define their own normalised text fields for certain regulated disclosures — the PRIIPs risk narrative, the SFDR sustainability statement, the MiFID target-market description. Where a regulated text field exists, its regulatory version *overrides* the informal `<FundText>` entries for the purpose of regulatory consumers, but the informal version continues to serve unregulated consumers such as marketing factsheets. Producers should populate both consistently; consumers should read whichever is appropriate to their use case.

---

## 5.6 Fund Classification

Every fund in FundsXML carries a set of classification fields that describe what the fund *is* — in legal, geographic, and investment terms. The classification fields are not the same as the regulatory templates of Chapter 8; they are the fund's own self-description, used by factsheet engines, by distributor search and filter tools, and by internal reference systems. We treat them in three groups: legal form and origin, investment characteristics, and risk-and-benchmark indicators. Almost everything in this section lives inside `FundStaticData`, at the fund level; registration countries are the one exception and belong to each individual share class (§5.10).

### 5.6.1 Legal Form, Domicile, and Inception

The first group answers the question *where does this fund come from, and under what legal form?*

**`DomicileCountry`** is the ISO 3166-1 alpha-2 code of the jurisdiction in which the fund is legally domiciled, carried as the very first child of `FundStaticData`. For the Europa Growth Fund this is `LU` — Luxembourg, the European fund domicile of choice for cross-border UCITS. The domicile determines which supervisor regulates the fund, which legal form it can take, and which tax regime applies at the fund level.

**Registration countries are not a fund-level field.** A fund may be domiciled in one country and *registered for distribution* in several others; in fact, cross-border distribution is the whole point of the UCITS regime. The Europa Growth Fund is domiciled in Luxembourg and registered for distribution in eleven countries: Luxembourg itself, France, Germany, Italy, Spain, the Netherlands, Austria, Belgium, Portugal, Switzerland, and Sweden. A natural first instinct is to model this as a list of `CountryOfRegistration` children on the fund, but the schema puts the list one level lower: `ShareClass/RegistrationCountries/RegistrationCountry`, with each entry naming a country code and an operational status (`Registered` or `De-registered`). The reason is that two share classes of the same fund may be registered in different countries — the institutional class may be authorised in fewer jurisdictions than the retail class — and a single fund-level list cannot express that. §5.10 returns to this.

**Legal structure** is expressed through a choice between `ListedLegalStructure` (an enumerated field covering the common European vehicle types) and `UnlistedLegalStructure` (a free-text fallback). Both alternatives are declared with `minOccurs="0"`, which means the schema accepts a `FundStaticData` block that omits the legal structure entirely — producers may do so for funds whose legal nature is carried in country-specific extensions instead. In practice every realistic European fund populates one of the two, and for the Europa Growth Fund we always pick `ListedLegalStructure`. The enumeration is specific and combines the regulatory regime with the corporate form in single values: `UCITS`, `UCITS - SICAV`, `UCITS - SICAF`, `UCITS - CONTRACTUAL TYPE`, `AIF`, `AIF - HEDGE FUND`, `AIF - PRIVATE EQUITY FUND`, `AIF - VENTURE CAPITAL FUND`, `AIF - REAL ESTATE FUND`, `AIF - REIT`, `AIF - INFRASTRUCTURE FUND`, `AIF - COMMODITY FUND`, `AIF - SOVEREIGN WEALTH FUND`, `AIF - ELTIF`, `AIF - EUVECA`, `AIF - EUSEF`, and `SPV`. Because the values already combine regime and corporate form, a producer does **not** emit two separate entries for *UCITS* and *SICAV*: the Europa Growth Fund, which is a UCITS operating as a SICAV, is represented by a single `<ListedLegalStructure>UCITS - SICAV</ListedLegalStructure>`. The enumeration is the tricky part of this field — producers that try to model the regulatory regime and the corporate form as two independent fields invariably drift away from the schema, and consumers that try to parse the enumerated value into its two halves regret the effort.

**`InceptionDate`**, a direct child of `FundStaticData`, is the date on which the fund first opened for subscription. It is a single `xs:date` value, and it never changes once the fund is live. The inception date is the anchor for every *since-launch* performance figure, and consumers that compute annualised returns rely on it. One subtlety deserves an early mention: the fund-level inception date may be earlier than the inception dates of some of the fund's *share classes*, because share classes can be added to an existing fund long after the fund itself was launched. Every `<ShareClass>` element therefore also carries its own `<InceptionDate>`, and Part II (§5.10.3) will treat share-class-level inception in detail.

The schema also carries a handful of adjacent date and status fields that a full `FundStaticData` block is likely to populate: `StartOfFiscalYear` and `EndOfFiscalYear` (as a `DayMonthType` pair), `OpenClosedEnded` (`OPEN` or `CLOSED`), `ClosedType` (`HARD` or `SOFT`) for funds that have stopped accepting new subscriptions, and `MaturityDate`/`LiquidationDate`/`LiquidationReason` for funds with a planned end. These are all optional, and we do not populate them for the Europa Growth Fund, which is an open-ended UCITS with no fixed maturity and no liquidation date in sight.

### 5.6.2 Investment Classification via `Classifications`

The second group of classification fields describes *what* the fund invests in. Here the schema takes a deliberately indirect approach: instead of defining a single closed vocabulary for asset class, geography, sector, and management style — which would drift out of date every time an industry body published a new taxonomy — FundsXML lets producers declare their classifications in terms of **external classification systems**. The container is `FundStaticData/Classifications`, and each child `<Classification>` carries the source of the classification, its internal type, a language, and one or more values, optionally tagged with a level attribute for hierarchical taxonomies.

The structure of each `<Classification>` is:

- a choice between `<ListedGroup>` (a known classification provider, drawn from an enumeration that includes `EFAMA`, `MORNINGSTAR`, `LIPPER`, `BLOOMBERG`, `MIFID`, `BVI`, `VOEIG`, `ESMA`, `AMF`, `WM`, `GERMAN CBCL`, `CIC`, and `CFI`) and `<UnlistedGroup>` (a free-text fallback for classifications from bodies the enumeration does not cover);
- an optional `<Type>` giving the specific taxonomy within the provider (for EFAMA, for example, *EFC* for the European Fund Classification; for Morningstar, *Global Category*);
- an optional `<Language>` attributing the language of the value strings;
- one or more `<Value>` elements, each with the classification label and an optional `level` attribute for hierarchies.

The Europa Growth Fund carries two classifications in parallel — one from EFAMA and one from Morningstar:

```xml
<Classifications>
  <Classification>
    <ListedGroup>EFAMA</ListedGroup>
    <Type>EFC</Type>
    <Language>en</Language>
    <Value level="1">Equity</Value>
    <Value level="2">Equity Europe</Value>
  </Classification>
  <Classification>
    <ListedGroup>MORNINGSTAR</ListedGroup>
    <Type>Global Category</Type>
    <Language>en</Language>
    <Value>Europe Large-Cap Growth Equity</Value>
  </Classification>
</Classifications>
```

The advantage of this approach is that it lets each consumer read the classification it recognises. A European distributor that drives its product universe from EFAMA categories reads the `EFAMA` entry and ignores the Morningstar one; a research analyst whose watchlists are organised by Morningstar category reads the Morningstar entry and ignores the EFAMA one. A consumer that recognises neither can fall back to inspecting `OfficialName` or `Fund/Currency` as a last resort, but the `Classifications` block is what exists for the purpose. The cost is that a reader cannot simply ask *"is this an equity fund?"* with a single schema-level field: the answer depends on which classification system they read. That trade-off is deliberate, and it reflects the reality of European fund distribution, where no single classification taxonomy has ever achieved the status of the canonical one.

A handful of related flags live one level deeper, under `SingleFund/SingleFundStaticData`, because they describe the fund as a *single* (non-umbrella) vehicle: `ExchangeTradedFlag`, `FundOfFundFlag`, `SocialResponsibleFlag`, and — most importantly for classification purposes — `ManagementType`, which takes the two values `ACTIVE` and `PASSIVE`. The Europa Growth Fund is `ACTIVE`. Producers that want to express finer distinctions such as `EnhancedIndex` or `IndexTracking` do so through the `Classifications` block with an appropriate `<ListedGroup>` entry.

### 5.6.3 Risk Indicators and Benchmarks

The third group of classification fields quantifies risk and names the benchmark against which the fund measures itself.

**`SFDRProductType`** is a fund-level field inside `FundStaticData` that names the SFDR (Sustainable Finance Disclosure Regulation) regime under which the fund is classified. It takes integer values `0`, `6`, `8`, or `9`: *6* for a fund that qualifies under Article 6 (no sustainability characteristics), *8* for an Article 8 fund (promotes environmental or social characteristics), *9* for an Article 9 fund (has sustainable investment as its objective), and *0* for funds that do not fall under SFDR at all. The Europa Growth Fund is a conventional Article 6 product and therefore carries `<SFDRProductType>6</SFDRProductType>`. The SFDR classification is the single most consequential ESG-related field in modern European fund disclosure, and consumers that drive ESG product filters read it directly.

The PRIIPs **Summary Risk Indicator** — the 1-to-7 scale familiar from KIDs and factsheets — does *not* live at the fund level as a dedicated element in the main schema. The reason is that the SRI is properly a share-class-level figure (different share classes of the same fund can sit at different SRI values, because hedging changes risk characteristics), and the regulated version of the SRI is expressed through the FinDatEx regulatory templates that Chapter 8 treats. Where producers want to carry the SRI alongside `FundStaticData` for legacy reasons, they do so through `CustomAttributes` with a name such as *SRI* and a numeric value. Consumers that need the authoritative SRI read the EMT or the PRIIPs-KID from the `<Documents>` section.

**Benchmark identification** lives in `FundStaticData/Benchmarks/Benchmark`, as a repeatable element whose content follows `BenchmarkStaticDataType`. Each benchmark entry carries a `<BenchmarkID>` (an internal key used to link the static description to the dynamic values in `FundDynamicData/Benchmarks`), a mandatory `<Name>` and `<Currency>`, an optional `<Provider>` (a `CompanyType` subclass with its own `<Identifiers>` and `<Name>`), an optional `<BenchmarkType>` drawn from an enumeration (`Market Index`, `Blended Benchmark`, `Custom`, `Peer Groups and Universes`, and others), and an optional `<BenchmarkComponents>` block for composite benchmarks. The Europa Growth Fund carries a single benchmark entry:

```xml
<Benchmarks>
  <Benchmark>
    <BenchmarkID>MSCI-EUR-NR</BenchmarkID>
    <Name>MSCI Europe Net Total Return EUR</Name>
    <Currency>EUR</Currency>
    <Provider>
      <Identifiers>
        <LEI>549300YZUBM5UFHQKY25</LEI>
      </Identifiers>
      <Name>MSCI Limited</Name>
    </Provider>
    <BenchmarkType>Market Index</BenchmarkType>
  </Benchmark>
</Benchmarks>
```

The `<BenchmarkID>` is not itself a public identifier — it is a producer-chosen string that a later `FundDynamicData/Benchmarks/Benchmark` entry will reuse to tie dynamic level data to the static description. The schema enforces this relationship as a `key`/`keyref` pair: a dynamic benchmark block whose `BenchmarkID` does not match a static one is a schema violation, which is the schema's way of preventing a category of reference errors.

A consumer that computes relative performance — alpha, tracking error, information ratio — reads the benchmark's name and currency from the static block and joins against its own market-data source. §5.13 will pick up the dynamic side, where the actual benchmark level on 31 March 2026 is transported inside `FundDynamicData/Benchmarks` as a `<Value>` per date.

One forward pointer is worth placing here. Chapter 8 treats the regulatory templates that the fund embeds in the `<RegulatoryReportings>` root element, and EMT/EPT contain their own versions of the risk indicators, the cost aggregates, and the benchmark references that we are discussing now. Where both layers exist in the same delivery, the regulatory-template version takes precedence for regulatory consumers and the fund-level version serves everyone else. Producers populate both consistently. Consumers read whichever is appropriate to their use case and never try to reconcile one against the other at the millisecond level.

### 5.6.4 Country-Specific Extensions

A final word on classification: FundsXML is a pan-European standard, but European fund distribution is full of national idiosyncrasies that no single taxonomy can cover gracefully. The schema handles this through **`CountrySpecificData`**, an extension container that appears at two levels of a delivery. Inside `FundStaticData`, a `<CountrySpecificData>` element carries national reporting extensions that apply to the fund as a whole — Austrian OeNB reporting codes, French AMF sub-classifications, German BVI internal categories, and so on. The national schemas are maintained in separate files (`FundsXML4_CountrySpecificData_xx.xsd`) that follow the main schema's release cycle. A similar mechanism exists on each individual share class for class-level national extensions. The companion root-level `<CountrySpecificData>` element, which is a sibling of `<Funds>` rather than a child, carries country-specific content that is not structurally tied to a single fund. We do not populate `CountrySpecificData` for the Europa Growth Fund in this chapter — the running example deliberately stays inside the core schema — but producers that serve regulated pipelines in any one European country will almost always end up populating the relevant national extension, and the reader who meets such a block in a real delivery should recognise it as an extension point rather than as data the core schema has somehow mis-named.

---

## 5.7 Fund-Level Costs and Key Figures

The last section of Part I treats the costs that a fund charges its investors, to the extent that they apply at the fund level rather than at the share-class level. FundsXML splits the cost story into two places. **Fund-level aggregate figures** — the retrospective per-annum ongoing charges and transaction costs that regulators require on KIDs and factsheets — live in `FundStaticData/OngoingCosts`. **Per-class detailed fees** — management fees and other charges that differ between share classes — live inside each `<ShareClass>` element under `Fees/Fee`. We introduce the fund-level side here; §5.10 will pick up the per-class side once the share-class structure is in place.

### 5.7.1 Types of Costs

European fund costs come in several flavours, and the vocabulary has accumulated enough layers over the years that it is worth naming them precisely before we model them.

**Management fee** is the annual percentage charged by the asset manager for managing the portfolio. It is expressed as a fraction of the fund's net assets and is typically deducted daily in arrears. For a European equity UCITS aimed at retail investors the management fee might be 1.50% per annum; for an institutional class of the same fund it might be 0.75%. Management fees almost always differ between share classes and therefore live on the class.

**Administration fee** and **depositary fee** are the charges levied by the fund's administrator and by its custodian bank, respectively. They are often bundled under a single "administration" line in marketing material but are structurally distinct in the fund's cost ledger. They are typically uniform across share classes, and producers can either absorb them into the fund-level ongoing charges figure or carry them as separate fee entries on each class, depending on whether the underlying contracts actually differ between classes.

**Performance fee**, where it applies, is the share of the fund's out-performance that the asset manager retains as an incentive payment. A typical structure is *"20% of out-performance above benchmark, subject to a high watermark, crystallised annually"*. The three main parameters — rate, hurdle, and the high watermark — together define a complete performance-fee model. FundsXML handles the high watermark explicitly through `ShareClass/HighWatermark`, and the rate and basis through a fee entry whose `Type` names the performance fee structure. Producers that omit either the watermark or the fee entry leave consumers unable to reconstruct the actual charge.

**TER** (Total Expense Ratio) and **Ongoing Charges** are the retrospective aggregate figures that sum the annual cost of running the fund — management fee, administration, depositary, audit, legal, and every other charge that the fund's investors collectively pay. The two terms are often used interchangeably; strictly speaking, *Ongoing Charges* (under UCITS KIID and PRIIPs) is slightly narrower than *TER* (the older EFAMA definition) in that it excludes performance fees, but the numeric values are usually similar. FundsXML carries the value through the `OngoingCosts/OngoingCost` structure described below, whose `<CostType>` field names which of the two variants the value represents.

**Entry load** and **exit load**, when they apply, are one-time charges levied when an investor buys into or sells out of the fund. They are almost always set at the share-class level — one class of the same fund may charge a 3% entry load while another charges none — and we will return to them in §5.10.

### 5.7.2 How Fund-Level Costs Are Modelled

The fund-level cost block lives at `FundStaticData/OngoingCosts` and contains one or more `<OngoingCost>` children. Each child has a fixed shape: a mandatory `<CostType>` drawn from a short enumeration (`Ongoing Costs`, `Ongoing Charges`, `Performance Fee`, `Transaction Costs`), a mandatory `<PublicationDate>` (the date the figure was computed and published), optional `<ValidFrom>` and `<ValidTo>` dates for the period to which the value applies, a mandatory `<Percentage>` (the value itself, expressed as a decimal percentage — `1.85` means 1.85%, *not* 0.0185), and an optional `<YearlyAmount>` for the absolute amount per 10,000 units of investment in the fund's currency. A typical block for a fund whose annual ongoing charges have just been refreshed at the start of the new fiscal year looks like this:

```xml
<OngoingCosts>
  <OngoingCost>
    <CostType>Ongoing Charges</CostType>
    <PublicationDate>2025-06-30</PublicationDate>
    <ValidFrom>2025-07-01</ValidFrom>
    <ValidTo>2026-06-30</ValidTo>
    <Percentage>1.85</Percentage>
  </OngoingCost>
</OngoingCosts>
```

A fund that also discloses a separate transaction-costs figure (common for PRIIPs-KID purposes) would add a second `<OngoingCost>` entry with `<CostType>Transaction Costs</CostType>` and its own percentage. The structure is deliberately flat: there is no place for hurdle rates or fee-waiver schedules at this layer, because the layer is designed to carry headline figures that feed factsheets and KIDs, not the full computational machinery behind a fee.

One observation about `OngoingCost` is worth making explicitly. The `Percentage` value is given in **human-readable percent notation**: `1.85` means 1.85 per cent per annum. This matches every other percentage in the schema (type `PercentageType`), and consumers that treat the value as a fraction (0.0185) will be off by a factor of a hundred — a spectacular error and, unfortunately, a recurring one. The rule of thumb is: if the number in `<Percentage>` looks like a reasonable management fee when you read it as a percent, it probably is; if it looks like a reasonable management fee after you divide by 100, you are about to make a mistake.

The fund-level block we have just assembled is the producer's own representation of its headline costs — the representation that feeds factsheet engines and distributor search tools. Chapter 8 treats the EMT (European MiFID Template), which defines a *different* and more detailed representation of the same charges, designed specifically for cost disclosure to retail investors under MiFID II. The EMT version is the definitive one for regulatory purposes; `OngoingCosts` in `FundStaticData` is the fund's operational view. Both exist in the same delivery, are populated consistently, and serve different consumers. The per-share-class detailed fee structure — `ShareClass/Fees/Fee` with its `ShareClassFeeType` — is the third layer, covered in §5.10, and it is where management fees and any class-specific surcharges actually live.

---

## 5.8 From One Share Class to Many

So far we have pretended that the Europa Growth Fund has exactly one share class. It does not. It has three, and they are different enough from each other that treating them as one would hide most of what makes real European fund distribution interesting. Part II relaxes the pretence and walks through the topics on which the fund-level picture branches.

The three share classes of the Europa Growth Fund are worth introducing by name, because we will use all three for the rest of the chapter and again in every subsequent chapter of Part II:

- **R-EUR-ACC** — the retail euro-denominated accumulating share class. Sold to individual investors across the eleven distribution countries, priced in EUR, and thesaurising all income into the NAV rather than paying dividends.
- **R-CHF-ACC-HEDGED** — the retail Swiss-franc-denominated currency-hedged accumulating share class. Aimed at Swiss retail investors who want exposure to European equities but do not want the EUR/CHF currency risk that would come with holding the ordinary euro class. The portfolio is the same as the R-EUR-ACC class; the difference is a currency overlay that hedges the EUR exposure into CHF.
- **I-EUR-DIST** — the institutional euro-denominated distributing share class. Aimed at pension funds, insurance companies, and other institutional investors who want predictable income distributions and who qualify for a lower fee schedule because of their minimum investment size.

All three of these share classes belong to the same fund, hold the same portfolio, follow the same investment policy, are managed by the same team, and share the same benchmark. In everything we covered in Part I — legal form, domicile, investment classification, benchmark — they are identical. What differs between them is a specific set of fields that we now need to place inside individual `<ShareClass>` elements rather than on the fund itself.

The rule that organises the placement is straightforward: **anything that differs between share classes lives on the `<ShareClass>` element; anything that is common to all classes stays on `<Fund>` and `<FundStaticData>`**. Table 5.3 shows where the main topics land when the rule is applied, using the schema names that actually appear in the XSD.

**Table 5.3 — Where the main fields live once share classes are in play**

| Stays on `<Fund>` / `FundStaticData` | Lives inside each `<ShareClass>` |
|---|---|
| `Fund/Identifiers/LEI` (fund LEI) | `ShareClass/Identifiers/ISIN`, `GermanWKN`, `SwissValorenCode` |
| `Fund/Currency` (fund base currency) | `ShareClass/Currency` (class currency) |
| `FundStaticData/DomicileCountry`, `ListedLegalStructure` | `ShareClass/RegistrationCountries/RegistrationCountry` |
| `FundStaticData/InceptionDate` (fund inception) | `ShareClass/InceptionDate` (class inception) |
| `FundStaticData/FundTexts` (investment strategy, risk) | `ShareClass/ShareClassType` (`Code`, `EarningUse`) |
| `FundStaticData/Classifications`, `Benchmarks` | `ShareClass/SubscriptionRestrictions/MinSubscriptionAmount` |
| `FundStaticData/OngoingCosts` (headline costs) | `ShareClass/Fees/Fee` (per-class management fees, …) |
| `FundStaticData/SFDRProductType` | `ShareClass/CurrencyHedgedFlag` |
| `FundDynamicData/TotalAssetValues` (fund aggregate) | `ShareClass/Prices/Price` (NAV per unit) |
| `FundDynamicData/Portfolios` *(→ Chapter 6)* | `ShareClass/TotalAssetValues` (class-level TNAV, shares outstanding) |
| `FundDynamicData/Benchmarks` (dynamic benchmark values) | `ShareClass/PerformanceFigures` (per-class returns) |
| `SingleFund/SingleFundStaticData` (`ManagementType`, flags) | `ShareClass/Flows`, `ShareClass/Distributions` *(→ Chapter 7)* |

Two consequences of the table deserve to be named explicitly. First, **everything from Part I still applies**. Share classes do not replace the fund-level fields; they add a new layer of per-class variation. A reader who has understood Part I does not need to unlearn anything in Part II; they just need to learn which of their understood fields now reappear, under schema-correct names, inside `<ShareClass>`. Second, **the portfolio is shared across all share classes**. Regardless of how many share classes a fund has, they all ultimately own shares of the same portfolio; the portfolio is a property of the fund, not of its share classes. Chapter 6 walks through the portfolio in detail, and the reader will notice that `FundDynamicData/Portfolios` hangs off the `Fund` level rather than off `ShareClass`. The share classes differ on how *claims* against the portfolio are structured — what currency the claims are denominated in, what fees they bear, whether they pay out income — but the portfolio itself is singular. (A share class *can* carry its own `ShareClass/Portfolios` if the producer reports the portfolio at share-class level, but this is an advanced pattern that the book does not pursue.)

**Figure 5.2 — Fund with three share classes**

```
                       <Fund>
        ┌───────┬────────┼─────────┬──────────┐
        │       │        │         │          │
 Identifiers  Names  Currency SingleFundFlag  │
                                              │
          ┌───────────────┬──────────────────┬┘
          │               │                  │
  FundStaticData  FundDynamicData     SingleFund
          │               │                  │
  DomicileCountry  TotalAssetValues    SingleFundStaticData
  LegalStructure   Portfolios (Ch. 6)        │
  InceptionDate    Benchmarks             ShareClasses
  FundTexts                                  │
  Classifications           ┌────────────────┼───────────────────┐
  Benchmarks                │                │                   │
  OngoingCosts       <ShareClass>       <ShareClass>         <ShareClass>
  SFDRProductType     R-EUR-ACC        R-CHF-ACC-HEDGED        I-EUR-DIST
                        ISIN                ISIN                  ISIN
                        EUR, EarningUse=R   CHF, EarningUse=R     EUR, EarningUse=D
                        Min €100            Min CHF 100           Min €1,000,000
                        Mgmt 1.50%          Mgmt 1.50%            Mgmt 0.75%
                        CurrencyHedgedFlag  CurrencyHedgedFlag    CurrencyHedgedFlag
                        =false              =true                 =false
                        Prices, NAVs        Prices, NAVs          Prices, NAVs
```

The remainder of Part II walks through the topics that the table and the figure put on the share-class side, in an order that mirrors the order of Part I. We begin with identity and currency (§5.9), because those are the topics that differ most visibly. We then treat the behavioural properties that distinguish share classes — earning use, hedging, minimum investment, inception, registration (§5.10). Finally, we look at the patterns that recur across funds and across asset managers when share classes multiply (§5.11), so that the reader leaves Part II with a catalogue of the commoner multi-share-class configurations and can recognise them in the wild.

---

## 5.9 ShareClass Identity and Currency

### 5.9.1 Identifiers at the Share Class Level

Each `<ShareClass>` element begins, just like `<Fund>`, with an `<Identifiers>` container. The container is the same schema type (`IdentifiersType`) as the one at fund level; it accepts the same children; and it is populated with whichever instrument-level codes name the class. ISIN, GermanWKN, SwissValorenCode, CUSIP, SEDOL, and the optional proprietary `OtherID` entries all live here.

The three share classes of the Europa Growth Fund carry three distinct ISINs:

- *R-EUR-ACC* — `LU2100000011`
- *R-CHF-ACC-HEDGED* — `LU2100000029`
- *I-EUR-DIST* — `LU2100000037`

Each of the three is a twelve-character ISO 6166 identifier; each is issued by the Luxembourg numbering agency (`LU` prefix); and each refers to exactly one share class. An investor subscribing to the retail euro class buys units whose ISIN is `LU2100000011`; that investor cannot, by owning units against that ISIN, gain exposure to the CHF-hedged variant without explicitly switching classes. The three ISINs are functionally three different products even though they are backed by the same portfolio.

GermanWKN, SwissValorenCode, CUSIP, and every other share-class-level identifier from §5.4.2 follow the same pattern: one entry per class inside the class's own `<Identifiers>` block. A German investor who receives a factsheet for the Europa Growth Fund sees three WKNs — one per class — and picks the one that matches the class they want to buy. A Swiss investor sees three Valors. A producer that gets this wrong, and writes a single WKN at the fund level when it should have been three at the class level, will find that German consumers cannot tell the classes apart and routinely route orders to the wrong class.

A rare but real edge case deserves a mention. A share class may, over its lifetime, carry *more than one* ISIN — for example when two funds merge, and the surviving class inherits the historical ISIN of the disappearing one alongside its own. FundsXML allows this: the class's `<Identifiers>` can hold a primary `<ISIN>` together with one or more historical ISINs represented as `<OtherID>` entries with a descriptive `FreeType` attribute. Consumers that need historical continuity look at the full set; consumers that need the current identity look only at the `<ISIN>` field.

Listed share classes — exchange-traded UCITS with public order books — carry additional identification that does not fit neatly into the standard identifier fields. The ticker symbol and the market identifier code (MIC) of the exchange on which the class is listed are carried via `ShareClass/MarketPlaces/MarketPlace`, which holds a four-character `<MarketIdentifierCode>`, a `<NAVCurrency>`, a `<TradingCurrency>`, and optionally a `<MarketMaker>` block. Exchange-traded UCITS are described through this block rather than through `OtherID`, and Chapter 13 returns to the full convention for listed-class metadata.

### 5.9.2 Currency of the Share Class

Currency is the second field that lives on the class as well as on the fund, and the distinction between *class currency* and *fund base currency* is one of the most important conceptual points of this chapter.

The **fund base currency** is the currency in which the fund's portfolio is primarily denominated and in which the fund's own books are kept. For the Europa Growth Fund this is EUR: the portfolio consists almost entirely of European equities priced in euros, the custody accounts are maintained in euros, and the fund-level total net assets figure is computed in euros. The base currency is a property of the fund, carried in `Fund/Currency` as a direct child of `<Fund>` (*not* inside `FundStaticData`), and it is one of the four mandatory fund-level elements we saw in §5.2.

The **share-class currency** is the currency in which the NAV of an individual share class is expressed and in which investors subscribe and redeem against that class. It lives in `ShareClass/Currency`, the direct counterpart of `Fund/Currency`, and it may or may not coincide with the base currency. For the Europa Growth Fund's R-EUR-ACC and I-EUR-DIST classes, the class currency is EUR, the same as the base currency; for the R-CHF-ACC-HEDGED class, the class currency is CHF, different from the base currency. All three classes ultimately hold claims against the same EUR-denominated portfolio, but the claims are denominated in different currencies and the claim-holders see different NAV numbers.

The mechanism that makes a CHF class possible when the underlying assets are in EUR is **currency hedging**. The fund enters into a rolling programme of currency forwards (or another hedging instrument) that converts the EUR exposure into CHF exposure for the purposes of the hedged class. The hedge costs money — interest-rate differentials, forward points, rolling frictions — and the cost is borne by the hedged class alone, which is why its NAV evolves differently from the ordinary euro class even though both classes hold the same underlying portfolio. §5.10 treats hedging as a behavioural property of the class in more detail.

A point of frequent confusion is worth stating plainly: **the base currency and the class currency are not interchangeable**. A consumer that reads a CHF NAV from an R-CHF-ACC-HEDGED class and treats it as a EUR number will get an answer that is wrong by the EUR/CHF exchange rate — several percent — and that error will propagate through every downstream calculation. The class element always names its own currency explicitly in `ShareClass/Currency`, and every `<Amount>` carrying a value in the class's currency has a mandatory `ccy` attribute that a consumer is expected to read and respect.

---

## 5.10 Earning Use, Hedging, Subscription, Inception, Registration, Fees

### 5.10.1 Earning Use: Accumulating and Distributing

The first of the behavioural properties that distinguish share classes is what happens to the income the fund's portfolio generates — dividends on equities, coupons on bonds, interest on cash. The choice is binary: the class either retains the income and reflects it in a higher NAV, or it pays the income out to investors at regular intervals.

**Accumulating** classes retain income. Every dividend received on the portfolio is added to the fund's net assets; since the share-class's NAV is computed as net assets divided by shares outstanding, and since the number of shares does not change when income is received, the NAV of an accumulating class rises by an amount reflecting the retained income. The investor benefits through capital appreciation of their units rather than through cash in hand. The R-EUR-ACC and R-CHF-ACC-HEDGED classes of the Europa Growth Fund are both accumulating.

**Distributing** classes pay income out. On a schedule defined in the prospectus — annually, semi-annually, quarterly, or in some cases monthly — the fund declares a dividend, the investors of the distributing class receive a cash payment equal to their pro-rata share of the accumulated income, and the NAV of the class drops on the ex-dividend date by the amount of the distribution. A consumer that renders the NAV of a distributing class over time sees a sawtooth pattern: smooth growth between distributions, a discrete drop on each ex-date. Both the growth and the drop are exactly as they should be — they reflect the same economic reality as the accumulating class's smoother curve, just expressed differently. The I-EUR-DIST class of the Europa Growth Fund is distributing, with an annual ex-date in mid-May each year.

FundsXML models the choice inside `ShareClass/ShareClassType`, a small structured element (schema type `ShareClassTypeType`) whose mandatory first child is `<Code>` — the producer's own class code (e.g. `R`, `I`, `X`, `Z`) — followed by three optional children: an `<EarningUse>` enumeration taking one of three single-character values (**`D`** for *Distributing*, **`P`** for *Partly distributing* — the rare hybrid case where some income streams are paid out and others reinvested — and **`R`** for *Reinvesting*, the schema's word for *Accumulating*), a short `<Name>` giving a human-readable label, and a longer `<Description>` text. The Europa Growth Fund's accumulating classes therefore carry `<EarningUse>R</EarningUse>`, and the distributing institutional class carries `<EarningUse>D</EarningUse>`. `<EarningUse>` is schema-optional, so a class whose accumulating-versus-distributing nature is communicated through other fields (e.g. a custom attribute, or implicit from the class code) can omit it; consumers should therefore treat a missing `<EarningUse>` as "unspecified" rather than as a default. Note the slight terminological mismatch: what the industry calls *accumulating* is what the schema calls *reinvesting* (`R`), because the income is reinvested into the fund rather than paid out. Producers that get the two letters the wrong way round create the single most damaging classification error in the chapter.

The actual dividend events for distributing classes are emitted as `Distribution` entries inside `ShareClass/Distributions`. Each `<Distribution>` has a mandatory `<ActionCode>` (`C`/`M`/`D` for create/modify/delete), `<DividendStatus>` (`OFFICIAL` or `ESTIMATED`), optional `<AnnouncementDate>` and `<RecordDate>`, mandatory `<ExDate>`, `<PaymentDate>`, and `<PaymentCurrency>`, and mandatory `<GrossDividendAmount>` and `<NetDividendAmount>` blocks each containing a per-share amount. Chapter 7 treats the flow side in full; the point here is simply that the dividend is *not* encoded on `ShareClassType` — the class is flagged *D*, but the actual events live in a separate time-series.

The consequence for performance comparison is worth naming because it is a routine source of confusion. Two share classes of the same fund, one accumulating and one distributing, have different NAV curves but the same *total return* — the cumulative performance including reinvested distributions. A consumer that compares raw NAV series between an accumulating and a distributing class will see a divergence that is purely an artefact of distribution treatment; a consumer that compares total returns will see, correctly, that the two classes are economically similar. Chapter 10 treats this as one of the validation rules that a performance-reporting pipeline should enforce.

### 5.10.2 Currency Hedging

Hedging is the second behavioural property that distinguishes share classes. We described the mechanism briefly in §5.9.2; here we look at how it is represented.

The primary hedging flag is **`CurrencyHedgedFlag`**, a Boolean that sits directly inside `<ShareClass>`. It is *true* if the class is currency-hedged, *false* otherwise. The Europa Growth Fund's R-CHF-ACC-HEDGED class has `<CurrencyHedgedFlag>true</CurrencyHedgedFlag>`, and the other two classes have `<CurrencyHedgedFlag>false</CurrencyHedgedFlag>` (or simply omit the element). There is no separate `HedgedCurrency` element: the currency into which the class is hedged **is** the class currency itself, carried in `ShareClass/Currency`, so a hedged CHF class naturally has `<Currency>CHF</Currency>`.

A producer that wants to describe the hedging approach in more detail carries a `<FundHedgingStrategy>` element either at the fund level (as a child of `FundStaticData`) or on the individual share class. The element wraps a single `<HedgingStrategy>` enumeration whose values are `No hedge`, `Full NAV hedge`, `Full Portfolio hedge`, and `Partial hedge`. A typical retail CHF-hedged share class carries `<HedgingStrategy>Full NAV hedge</HedgingStrategy>`, meaning that the hedge is calibrated against the class's total net asset value rather than looking through to each underlying currency exposure separately. Full Portfolio hedges are rarer and appear mainly in institutional classes that want their hedge accurate at the instrument level.

One point that routinely surprises newcomers is that the hedge P&L — the profit or loss the class realises from its currency forwards — does not appear as a separate field in FundsXML. It is absorbed silently into the NAV of the hedged class, which is exactly where a disciplined investor expects it to show up: the whole purpose of the hedge is to modify the return pattern of the class, and the NAV is what captures that return. A consumer that wants to decompose the NAV into "portfolio return" and "hedge P&L" separately cannot do so from the FundsXML file alone; the decomposition is a producer-side analytic that is out of scope for the standard.

### 5.10.3 Subscription Restrictions, Inception, and Registration

The remaining behavioural fields concern the terms under which an investor can buy into the class, the history of the class itself, and the jurisdictions in which the class is authorised for distribution.

**Subscription restrictions** live in a dedicated `<SubscriptionRestrictions>` container inside each `<ShareClass>`. Its main children are:

- `MinSubscriptionAmount` — the smallest amount a new investor can subscribe to the class in their first transaction, carried as an `<Amount ccy="EUR">100</Amount>` (or the class's own currency). Retail classes typically set this at a small number — 100 EUR or 1,000 EUR — so that any individual investor can participate. Institutional classes set it much higher — 500,000 EUR, 1,000,000 EUR, 10,000,000 EUR — so that the class is effectively closed to retail participation and can justify its lower fee schedule.
- `MinSubscriptionShares` — the same restriction expressed in units of the class rather than in currency, for producers that prefer share-count thresholds.
- `MinSubscriptionAmountSubsequent` and `MinSubscriptionSharesSubsequent` — the equivalent thresholds for existing investors topping up their positions. They are typically smaller than the initial ones and are rarely zero.
- `MinRegularInvestmentAmount` and `MinRegularInvestmentShares` — the thresholds for savings-plan contributions, where a monthly direct-debit subscription has its own minimum.
- `OtherSubscriptionRestrictions` — a free-text fallback for anything the structured fields do not cover.

For the three share classes of the Europa Growth Fund the thresholds are:

- *R-EUR-ACC*: `MinSubscriptionAmount` 100 EUR, `MinSubscriptionAmountSubsequent` 50 EUR
- *R-CHF-ACC-HEDGED*: `MinSubscriptionAmount` 100 CHF (no subsequent minimum declared)
- *I-EUR-DIST*: `MinSubscriptionAmount` 1,000,000 EUR (no subsequent minimum declared)

A symmetric `<RedemptionRestrictions>` container carries the same kind of structure for the sell side — `MaxRedemptionAmount`, `MaxRedemptionShares`, `MinHoldingPeriod` (in months), and `OtherRedemptionRestrictions` — for classes that apply lock-ups or exit caps.

Investor-type restrictions are not a single flag. The schema carries them through two Booleans on `<ShareClass>` — `<RetailInvestorsOnly>` (true for classes that may not be sold to institutional investors, a rarity) and `<UK_RDR_Flag>` (true for classes that comply with the UK Retail Distribution Review, which bans trailing commissions on retail sales) — and, indirectly, through the minimum-subscription thresholds above. The *institutional* nature of the Europa Growth Fund's I-EUR-DIST class is communicated through its minimum subscription of 1,000,000 EUR rather than through a dedicated `IsInstitutional` flag — there is no such field in the schema. Producers that want to make the institutional character explicit can do so by populating `ShareClassType/Code` with a suggestive value (`I`) and `ShareClassType/Name` with a descriptive label (*Institutional Distributing*). Consumers should never infer investor eligibility purely from a class code — that would re-introduce the name-parsing mistake that §5.11 warns against.

**Inception date** at the class level lives in `ShareClass/InceptionDate` and is the date on which the class itself first opened for subscription. It may or may not coincide with the fund-level inception date from §5.6.1. The Europa Growth Fund was launched in 2012; the R-EUR-ACC class has been live since launch and carries `<InceptionDate>2012-01-15</InceptionDate>`, identical to the fund. The R-CHF-ACC-HEDGED class was added in 2018 to capture Swiss retail demand and carries `<InceptionDate>2018-06-01</InceptionDate>`. The I-EUR-DIST class was added in 2020 after an institutional anchor investor was secured and carries `<InceptionDate>2020-09-15</InceptionDate>`.

The distinction between fund inception and class inception matters for performance reporting. The fund's *since-launch* performance refers to the inception date of the fund and makes sense only for classes that have been live since then. For classes added later, performance from dates prior to class inception does not exist and should not be shown: a *since-launch* figure for the R-CHF-ACC-HEDGED class starts in June 2018, not in 2012. Consumers that render historical performance are expected to read the class inception date and honour it; producers that emit pre-inception performance are in error, and Chapter 10 will list this among the business-validation rules.

**Registration countries** at the class level live inside `ShareClass/RegistrationCountries/RegistrationCountry`. Each entry carries a mandatory `<CountryCode>` (an ISO 3166-1 alpha-2 code), an optional `<Status>` (`Registered` or `De-registered`), an optional `<StatusDate>`, an optional `<SubStatus>` for investor restrictions specific to that jurisdiction (e.g. *Institutional Investors only*), and an optional `<MarketingDistributionStatus>` that tracks whether active marketing is currently under way in the country. The retail R-EUR-ACC class of the Europa Growth Fund is registered in all eleven distribution countries; the I-EUR-DIST institutional class is registered in a smaller subset, because institutional distribution is often limited to the jurisdictions in which the producer has an institutional sales team on the ground. Modelling registration per share class rather than per fund is what allows two classes of the same fund to be available in different sets of countries.

### 5.10.4 Per-Class Fees

The last behavioural topic is the class-specific fee schedule. We introduced the general cost vocabulary in §5.7; here we see how the per-class variant is structured.

Fees that differ between classes live in `ShareClass/Fees/Fee`, with each `<Fee>` following the schema type `ShareClassFeeType`. The mandatory children of a `<Fee>` are:

- `<Type>` — a free-text label for the fee, such as *Management Fee*, *Distribution Fee*, *Entry Load*, *Performance Fee*;
- `<PayReceive>` — a single character, `P` for *paid by the fund* (the usual case) or `R` for *received by the fund* (rare);

optionally followed by `<Minimum>` and `<Maximum>` as percentages of total net assets, a `<CalculationMethod>` free-text description, and a `<DataByPeriods>` container that carries the numeric values per reporting period. Each `<DataByPeriod>` inside `<DataByPeriods>` names the period with a `<BeginDate>` and `<EndDate>`, optionally a `<CurrentDate>` for ongoing periods, and a mandatory `<Values>` block whose key field is `<FeeAsPercentageOfTNA>` — the percentage of total net assets that the fee represents over the named period. The result is a fee structure that can carry not only the headline rate but also the actual realised rate for every period the producer wants to publish.

A typical management-fee entry on the R-EUR-ACC class of the Europa Growth Fund looks like this:

```xml
<Fees>
  <Fee>
    <Type>Management Fee</Type>
    <PayReceive>P</PayReceive>
    <Maximum>1.50</Maximum>
    <CalculationMethod>Per annum of average net assets, accrued daily</CalculationMethod>
    <DataByPeriods>
      <DataByPeriod>
        <BeginDate>2025-07-01</BeginDate>
        <EndDate>2026-06-30</EndDate>
        <CurrentDate>2026-03-31</CurrentDate>
        <Values>
          <FeeAsPercentageOfTNA>1.50</FeeAsPercentageOfTNA>
        </Values>
      </DataByPeriod>
    </DataByPeriods>
  </Fee>
</Fees>
```

The same structure applies to every per-class fee: a distribution fee, an entry load (where `<CalculationMethod>` names it as a one-off rather than an annual rate), a performance fee (where `<CalculationMethod>` would describe the outperformance formula and the crystallisation schedule). For performance fees, the **high watermark** is carried separately in `ShareClass/HighWatermark`, whose fields are `<ExistingFlag>` (Boolean, true if the class has a watermark), `<Percentage>`, `<Amount>` (the reference NAV), `<Description>` (free text), `<PeriodicalResetFlag>`, and `<ResetFrequency>`. A full performance-fee specification therefore spans a `<Fee>` entry and a `<HighWatermark>` entry, each carrying the part of the story that belongs to it.

One point of confusion that often catches newcomers is the number format of `<FeeAsPercentageOfTNA>` and `<Maximum>`. Both use `PercentageType`, which is human-readable per-cent: `1.50` means 1.50%, not 0.0150. The same rule applies as for `OngoingCost/Percentage` in §5.7.2: if the number looks like a reasonable fee when read as a percent, it is; if it looks reasonable only after division by a hundred, the producer has emitted the value in the wrong format.

---

## 5.11 Multi-Share-Class Patterns in Practice

We close Part II with a short catalogue of the patterns that recur in real European fund structures when share classes multiply. The patterns are not defined by FundsXML; they are industry conventions that producers follow and that consumers should recognise. Knowing the patterns makes reading an unfamiliar fund's share-class structure much faster.

### 5.11.1 Share Class Families and Naming Conventions

The fund industry has evolved a rough alphabet of single-letter codes that mark families of share classes. The conventions vary slightly between asset managers but the common letters are stable enough to be a useful first filter.

- **A** — retail, often with an entry load of 3–5%
- **B** — retail, often distributing, and typically carrying the same fee structure as A
- **C** — retail, with no entry load but a higher management or ongoing-charges figure to compensate
- **D** — retail, specialised variants (distributing, hedged, clean-priced)
- **I** — institutional, lower fees, higher minimum investment
- **X** — super-institutional or omnibus, fees negotiated on a segregated mandate basis
- **Z** — zero-retrocession, for fee-based advisers who bill their clients directly
- **R** — retail, modern replacement for **A** in some post-MiFID-II structures with no entry loads

These letters appear in the fund's marketing material, in factsheets, and in the `OfficialName` or `ShortName` fields of the `<ShareClass>/Names` block, often combined with currency, earning use, and hedging flags: *"R-EUR-ACC"*, *"I-USD-DIST-HEDGED"*, *"A-CHF-ACC"*. The Europa Growth Fund's three classes fit the pattern: *R* for retail, *I* for institutional, currencies and earning-use policies spelled out.

One rule is worth stating loudly: **the letters are not schema-enforced enumerations, and consumers must not parse them**. A class called *R-EUR-ACC* is retail, euro-denominated, and accumulating not because of its name but because of its `Currency`, its `ShareClassType/EarningUse`, its `CurrencyHedgedFlag`, and its `SubscriptionRestrictions/MinSubscriptionAmount` fields. A consumer that tries to extract those properties from the name — by string-matching on "R", "EUR", and "ACC" — will eventually meet an asset manager whose naming convention uses different letters, or who combines letters in an order the consumer did not expect, or who simply does not follow a pattern at all. The schema fields exist precisely so that consumers can read the properties authoritatively. Producers populate the names for human eyes; producers populate the fields for machines.

### 5.11.2 Currency-Hedged Variants

The most common multi-class pattern in cross-border European distribution is a base class paired with one or more currency-hedged variants. The base class holds the fund's native currency (typically EUR for a European fund, USD for a global fund); the hedged variants cover the other major currencies in which the fund is distributed (CHF, GBP, JPY, occasionally SEK or NOK).

Structurally, the base class and its hedged siblings share everything that is a property of the fund — portfolio, investment policy, benchmark, fee schedule, team — and differ only on:

- `Identifiers` (ISIN, GermanWKN, SwissValorenCode: each variant has its own)
- `Currency` (EUR on the base, CHF/GBP/JPY/… on each hedged variant)
- `CurrencyHedgedFlag` (`false` on the base, `true` on each hedged variant)
- `FundHedgingStrategy` (typically `No hedge` on the base, `Full NAV hedge` on each hedged variant)
- `InceptionDate`, if the hedged variants were added later than the base
- NAV and per-class `TotalAssetValues`, which diverge from the base immediately after inception because of the hedge P&L

Note what does *not* differ: the per-class fee schedule is typically identical between the base class and its hedged variants, because the hedge cost is absorbed into the NAV rather than charged as a fee. A consumer that wants to identify the hedged siblings of a given class has no direct schema-level mechanism to do so — FundsXML does not define an `IsHedgedVariantOf` pointer — and has to rely on naming conventions or on producer-supplied metadata in `CustomAttributes`. Chapter 13 recommends a project-level convention for producers that have several hedged siblings per base class.

### 5.11.3 Accumulating and Distributing Twins

The second common pattern is a pair of twin classes that share everything except distribution policy: one accumulates income, the other distributes. The pattern is driven by tax treatment — in many jurisdictions, accumulation is more tax-efficient for long-term savers while distribution is preferred by retirees and institutions that need regular cash flow — and by the typical size of the two investor bases.

The twins share portfolio, fee schedule, and currency. They differ on:

- `Identifiers` (each has its own ISIN, GermanWKN, and so on)
- `ShareClassType/EarningUse` (`R` on the accumulating twin, `D` on the distributing twin)
- `Distributions` — populated on the distributing twin with the actual dividend events, empty on the accumulating one
- Often `InceptionDate` (one twin is typically added later than the other)
- NAV and per-class `TotalAssetValues`, which diverge on the first ex-dividend date and remain divergent thereafter even though total returns are the same

A common trap is to compare the NAVs of twin classes directly over time and conclude that one is outperforming the other. This is almost always an artefact of distribution treatment, not of actual economic divergence. The correct comparison is total return with reinvested distributions, and Chapter 13 will treat this as one of the validation rules that a performance-reporting pipeline should enforce.

### 5.11.4 When Share Classes Diverge More Deeply

The patterns we have discussed so far — currency variants, accumulating/distributing twins, retail/institutional splits — account for the great majority of real share-class structures. A minority of funds carry classes that differ more deeply: different fee structures, substantially different minimum investments, occasionally even different fee-distribution mechanisms (for example, an adviser class whose distribution commission is built into the NAV versus a clean class whose distribution commission is billed separately to clients). These configurations are all legal and all representable in FundsXML.

What is *not* legal, and not representable, is a configuration in which two share classes ultimately own different portfolios. The moment two claim groups diverge at the portfolio level, they are no longer two share classes of the same fund — they are two funds, each with its own portfolio. In legal terms this is a sub-fund structure, and it belongs under the umbrella construct that §5.14 treats. Producers occasionally try to model sub-funds as share classes for operational reasons; the result is a FundsXML document that appears internally inconsistent (two share classes, but reconciliation with the shared portfolio impossible) and that fails business validation at the consumer. The rule is straightforward: if the classes share a portfolio, they are share classes; if they do not, they are separate funds or separate sub-funds.

A forward pointer is worth placing here. Chapter 8 treats the EMT regulatory template, and EMT flattens the share-class structure further than FundsXML does: for MiFID cost disclosure purposes, each share class is represented as a separate "product" with its own cost structure, and the underlying fund-level relationships are mostly implicit. The two representations — FundsXML's hierarchical view and EMT's flattened view — serve different consumers and should be populated consistently. Chapter 8 explains how.

---

## 5.12 Dynamic Data — NAVs, Prices, and Total Net Assets

We now turn to the dynamic half of the `<Fund>` element. Up to this point we have treated it as "the fields that change every valuation day", which is a correct first approximation, and we have listed the topics it contains. With the share-class structure now in place, we can populate it with meaningful numbers — and, more importantly, we can say clearly where in the XML each figure lives, because the naive expectation that *everything dynamic lives inside `FundDynamicData`* is not quite right.

### 5.12.1 Where Dynamic Data Lives, and What Goes Where

Dynamic fund data is split between **three** places in the schema.

- **`FundDynamicData`** (sibling of `FundStaticData` under `<Fund>`) carries only three substructures: `TotalAssetValues` for **fund-level aggregate** totals, `Portfolios` for the shared portfolio composition, and `Benchmarks` for dynamic benchmark level values. It is deliberately small.
- **`ShareClass`** (each class inside `SingleFund/ShareClasses`) carries almost everything that varies per class: `Prices` (NAV per unit), `TotalAssetValues` (per-class aggregate), `Distributions` (dividend events), `Flows` (subscriptions and redemptions), `PerformanceFigures` (returns), and `Portfolios` if the producer reports the portfolio at share-class rather than fund level.
- **`SingleFund/SingleFundStaticData`** carries a handful of flags and classifications that are technically static but describe the single-fund identity (management type, exchange-traded flag, price-published flag).

This chapter treats the dynamic values that matter most to end-users: per-class NAVs (§5.12.2), fund-level totals (§5.12.3), and performance (§5.13). The two substructures we leave alone, *Portfolios* and *Flows / Distributions*, are big enough topics to justify chapters of their own: Chapter 6 for portfolio, Chapter 7 for flows and distributions.

### 5.12.2 NAV and Total Net Assets per Share Class

The net asset value per unit — the NAV that an investor sees in their statement — is the central dynamic figure of any fund. For a fund with multiple share classes, there is no single NAV: there is one NAV per class, and the schema therefore places it on the individual class rather than on the fund as a whole. Each `<ShareClass>` carries two related substructures.

`ShareClass/Prices/Price` holds one or more `<Price>` entries, each of type `ShareClassPriceType`, carrying the NAV per unit and adjacent price quantities. The mandatory children are `<ActionCode>` (`C`/`M`/`D`), `<NavDate>`, `<PriceCurrency>` (the ISO 4217 code for the class currency), `<PriceNature>` (`OFFICIAL`, `ESTIMATED`, or `TECHNICAL`), and `<NavPrice>` (the net asset value per unit, as a decimal with up to 15 total digits and 8 fractional digits). Optional children include `<SubscriptionPrice>` and `<RedemptionPrice>` — used when subscription and redemption happen at prices that differ from the mid-NAV, for example because of an entry load or a swing-pricing factor — and `<OtherPrices>` and `<SplitFactor>` for less common cases.

`ShareClass/TotalAssetValues/TotalAssetValue` holds the per-class aggregate: the class's total net asset value and its shares outstanding. The mandatory children are `<NavDate>` (the valuation date) and `<TotalAssetNature>` (again `OFFICIAL`/`ESTIMATED`/`TECHNICAL`). The optional but routinely populated children are `<TotalNetAssetValue>` (a `FundAmountType`, i.e. a currency-tagged decimal), `<TotalGrossAssetValue>` (for funds that distinguish the two), `<SharesOutstanding>` (the number of units of the class outstanding), and `<Ratio>` (the share of the fund's total net assets that this class represents, as a percentage). A producer that wants to carry alternative valuations — a swing-priced figure, a market-priced figure, a hold-to-maturity figure — adds them in `<OtherTotalAssetValues>`.

**Precision and rounding** follow industry convention. NAVs are typically reported to four decimal places (occasionally to eight, as the schema allows); shares outstanding are reported as integers (occasionally to three decimal places for funds that issue fractional shares); total values are reported to two decimal places. A consumer that re-computes `NavPrice × SharesOutstanding` to verify the producer's total will often find a discrepancy of a cent or two, which is a rounding artefact rather than an error. Chapter 10 treats the tolerance rules that validation pipelines should apply.

The three share classes of the Europa Growth Fund, at the close of 31 March 2026, have the following values:

- **R-EUR-ACC**: NAV 124.5078 EUR, 1,234,567 shares outstanding, TNAV 153,712,654.83 EUR (ratio 33.09%)
- **R-CHF-ACC-HEDGED**: NAV 119.2011 CHF, 456,789 shares outstanding, TNAV 54,438,456.22 CHF (ratio 12.21%)
- **I-EUR-DIST**: NAV 108.3344 EUR, 2,345,678 shares outstanding, TNAV 254,115,322.56 EUR (ratio 54.70%)

In XML form, the NAV and total-asset-value blocks for the R-EUR-ACC class look like this (the other two classes are structurally identical, with their own currencies and amounts):

```xml
<ShareClass>
  <!-- Identifiers, Names, Currency, ShareClassType, InceptionDate, … -->
  <Prices>
    <Price>
      <ActionCode>C</ActionCode>
      <NavDate>2026-03-31</NavDate>
      <PriceCurrency>EUR</PriceCurrency>
      <PriceNature>OFFICIAL</PriceNature>
      <NavPrice>124.50780000</NavPrice>
    </Price>
  </Prices>
  <TotalAssetValues>
    <TotalAssetValue>
      <NavDate>2026-03-31</NavDate>
      <TotalAssetNature>OFFICIAL</TotalAssetNature>
      <TotalNetAssetValue>
        <Amount ccy="EUR" isShareClassCcy="true">153712654.83</Amount>
      </TotalNetAssetValue>
      <SharesOutstanding>1234567</SharesOutstanding>
      <Ratio>33.09</Ratio>
    </TotalAssetValue>
  </TotalAssetValues>
  <!-- Fees, Distributions, Flows, PerformanceFigures, … -->
</ShareClass>
```

Three observations deserve to be made about the block. First, **the link to the share class is structural, not nominal**. The NAV and the total-asset-value entry are inside the share class's own element; there is no `<ShareClassISIN>` link of the kind a newcomer might expect, because the ISIN is already the class's own identifier at the top of the class, and a consumer reading the file walks the tree rather than matching by string.

Second, **every `<Amount>` element carries a mandatory `ccy` attribute** that names the currency of the value. The R-CHF-ACC-HEDGED class's NAV is in CHF, not EUR, and the attribute makes this unambiguous — any consumer that ignores it will produce wrong numbers, and Chapter 10 will treat the discipline of always checking currencies as a core validation rule. The `isShareClassCcy` attribute, a Boolean, is optional but useful: a producer that marks the class-currency amounts with `isShareClassCcy="true"` tells the consumer explicitly that this value is in the class's own currency, which removes any ambiguity when the same structure is reused in mixed-currency contexts.

Third, **the block is self-contained per class**. Given only the NAV, the shares outstanding, and the class currency, a consumer can compute every investor-facing value a factsheet needs for that class. The fund-level figures that come next in §5.12.3 are aggregates, not substitutes.

#### Delivering a daily price history

The examples so far have shown a single `<Price>` entry for a single valuation date, which is the normal case for a monthly delivery. But the `<Prices>` container can hold *multiple* `<Price>` children, each with its own `<NavDate>` — and this is exactly what happens when a producer delivers daily NAV history. A transfer agent that sends the complete March 2026 price series for the R-EUR-ACC class, for instance, would populate the container with one entry per business day. The following excerpt shows the first five trading days of the month:

```xml
<Prices>
  <Price>
    <ActionCode>C</ActionCode>
    <NavDate>2026-03-02</NavDate>
    <PriceCurrency>EUR</PriceCurrency>
    <PriceNature>OFFICIAL</PriceNature>
    <NavPrice>123.84210000</NavPrice>
  </Price>
  <Price>
    <ActionCode>C</ActionCode>
    <NavDate>2026-03-03</NavDate>
    <PriceCurrency>EUR</PriceCurrency>
    <PriceNature>OFFICIAL</PriceNature>
    <NavPrice>123.96550000</NavPrice>
  </Price>
  <Price>
    <ActionCode>C</ActionCode>
    <NavDate>2026-03-04</NavDate>
    <PriceCurrency>EUR</PriceCurrency>
    <PriceNature>OFFICIAL</PriceNature>
    <NavPrice>124.11030000</NavPrice>
  </Price>
  <Price>
    <ActionCode>C</ActionCode>
    <NavDate>2026-03-05</NavDate>
    <PriceCurrency>EUR</PriceCurrency>
    <PriceNature>OFFICIAL</PriceNature>
    <NavPrice>123.72480000</NavPrice>
  </Price>
  <Price>
    <ActionCode>C</ActionCode>
    <NavDate>2026-03-06</NavDate>
    <PriceCurrency>EUR</PriceCurrency>
    <PriceNature>OFFICIAL</PriceNature>
    <NavPrice>124.00170000</NavPrice>
  </Price>
  <!-- … 17 further business days through 2026-03-31 … -->
</Prices>
```

Two points are worth noting. First, the order of the `<Price>` entries within the container is not prescribed by the schema — a consumer must use `<NavDate>` to sort the series, not the document order. In practice most producers emit entries in chronological order, but a robust consumer does not rely on this. Second, the `<PriceCurrency>` and `<PriceNature>` are repeated in every entry, even though they are the same for all days; this is deliberate, because the schema allows a single `<Prices>` container to carry both an official and an estimated price for the same date, and the currency could in theory change after a redenomination. The repetition keeps each `<Price>` element self-describing.

### 5.12.3 Total Net Assets at the Fund Level

Beyond the per-class totals, the **fund-level** aggregate — the sum of all share-class net assets, expressed in the fund's base currency — lives at `FundDynamicData/TotalAssetValues/TotalAssetValue`, which reuses the same `TotalAssetValueType` we just saw but at the enclosing fund level. The per-class figures for the Europa Growth Fund on 31 March 2026 aggregate as follows:

- R-EUR-ACC: 153,712,654.83 EUR
- R-CHF-ACC-HEDGED: 54,438,456.22 CHF, converted at 1 CHF = 1.0420 EUR (the reference rate used by the fund administrator at the valuation point): 56,724,871.39 EUR
- I-EUR-DIST: 254,115,322.56 EUR
- **Total**: 464,552,848.78 EUR

In XML form, the fund-level aggregate block looks like this:

```xml
<FundDynamicData>
  <TotalAssetValues>
    <TotalAssetValue>
      <NavDate>2026-03-31</NavDate>
      <TotalAssetNature>OFFICIAL</TotalAssetNature>
      <TotalNetAssetValue>
        <Amount ccy="EUR" isFundCcy="true">464552848.78</Amount>
      </TotalNetAssetValue>
    </TotalAssetValue>
  </TotalAssetValues>
  <!-- Portfolios (→ Chapter 6), Benchmarks (dynamic values) -->
</FundDynamicData>
```

The structure is the same one we met at share-class level: the mandatory `<NavDate>` comes first, then the mandatory `<TotalAssetNature>`, then the optional `<TotalNetAssetValue>` with its currency-tagged amount. At fund level the amount carries the `isFundCcy="true"` attribute to declare it as being in the fund's base currency, which is `Fund/Currency` (EUR, in our case).

Two points need to be stated clearly. First, **the aggregate must respect currency**. The CHF total from the R-CHF-ACC-HEDGED class cannot be added directly to the EUR totals from the other two classes; it must first be converted at a reference rate, and the rate used must be consistent with whatever the fund administrator uses internally for the same purpose. A consumer that adds the raw numbers without conversion gets a result that is wrong by several percent and meaningless. Producers should never emit an aggregate that required an implicit currency conversion without being prepared to defend the rate used; consumers should, when reconciling, compute the aggregate from the per-class values themselves to verify.

Second, **the fund-level total is the figure that regulatory thresholds hang on**. AIFMD size limits, MiFID II cost-disclosure thresholds, national marketing thresholds, and internal concentration limits all use the fund-level `TotalNetAssetValue` rather than the per-class values. A consumer that implements threshold logic reads the aggregate directly and does not try to re-derive it; if the producer's aggregate disagrees with a reconciliation computation, the discrepancy is a data-quality issue to be raised with the producer, not a licence to pick one figure over the other silently.

---

## 5.13 Performance and Other Dynamic Figures

### 5.13.1 Performance Figures per Share Class

Performance — the total return that an investor in a share class has earned over a given period — is the most frequently consulted field in fund data and the one most prone to being reported in inconsistent ways. FundsXML carries performance at the **share-class level**, inside each `<ShareClass>` element under `ShareClass/PerformanceFigures`, with one entry per period per class. The container begins with a mandatory `<ActionCode>` (`C`/`M`/`D`), then carries three optional sibling lists — `<TotalReturns>`, `<Performances>`, and `<Ratings>` — each of which carries its own flavour of figure. Producers populate whichever combination their downstream consumers expect; none of the three is mandatory, but in practice every monthly delivery populates at least one. We walk through the first two here.

**`TotalReturns`** carries one or more `<TotalReturn>` entries (type `TotalReturnType`), each describing a total-return value over a specific calculation period, including the effect of reinvested distributions. All four of its core children are mandatory: `<Currency>`, `<Value>` (a nested element containing either an `<AbsoluteValue>` in the currency or a `<PercentageValue>` — the common case is a percentage), `<ValidityDate>` (the date at which the return is measured), and `<CalculationPeriod>` (an enumeration that names the period length). An optional `<AnnualizedFlag>` marks figures that have been annualised — as a rule, any period of a year or more is reported in annualised form so that three-year and five-year figures are directly comparable. Optional `<CalculationMethod>`, `<Investment>`, `<StartCalculationDate>`, `<CorrectionCoefficient>`, and `<ReinvestmentCoefficient>` fields let the producer carry computation provenance alongside the value itself.

The `<CalculationPeriod>` enumeration names the periods for which total returns are customarily reported:

- **`1 Day`** — one business day (yesterday's return)
- **`1 Week`** — one week
- **`1 Month`**, **`3 Months`**, **`6 Months`**, **`YTD`** — one month, three months, six months, year-to-date
- **`1 Year`**, **`3 Years`**, **`5 Years`**, **`10 Years`** — one year, three years, five years, ten years
- **`Since launch`** — from the share class's inception date to the current valuation date
- **`Specific`** — a custom period whose exact bounds are declared through `<StartCalculationDate>` and `<ValidityDate>`

A single entry for the R-EUR-ACC class's one-year return might therefore look like this:

```xml
<PerformanceFigures>
  <ActionCode>C</ActionCode>
  <TotalReturns>
    <TotalReturn>
      <Currency>EUR</Currency>
      <Value>
        <PercentageValue>9.4</PercentageValue>
      </Value>
      <ValidityDate>2026-03-31</ValidityDate>
      <CalculationPeriod>1 Year</CalculationPeriod>
    </TotalReturn>
    <TotalReturn>
      <Currency>EUR</Currency>
      <Value>
        <PercentageValue>6.8</PercentageValue>
      </Value>
      <ValidityDate>2026-03-31</ValidityDate>
      <CalculationPeriod>3 Years</CalculationPeriod>
      <AnnualizedFlag>true</AnnualizedFlag>
    </TotalReturn>
  </TotalReturns>
</PerformanceFigures>
```

Two structural points about this listing. First, the `<PercentageValue>` is in **human-readable per-cent**: 9.4 means 9.4%, not 0.094. The convention is the same as for every other percentage in the schema and differs from the fractional form that some numerical libraries default to. Second, the three-year entry carries `<AnnualizedFlag>true</AnnualizedFlag>`, making explicit that the 6.8% figure is a compound annual growth rate rather than a cumulative three-year return. A consumer that ignores the flag and treats the figure as a cumulative will understate the class's three-year performance by a factor of roughly three.

The **`Performances`** container is a near-twin of `TotalReturns` whose children (type `PerformanceType`) carry the same kind of information with slightly different shape. Its three mandatory children are `<ValidityDate>`, `<CalculationPeriod>`, and `<PercentageValue>`; optional children include `<AnnualizedFlag>`, `<CalculationMethod>`, `<StartCalculationDate>`, `<Investment>`, `<DateInterval>`, and a `<DataSeries>` block for producers that want to ship the underlying point series alongside the summary figure. In practice producers pick one of the two containers as their primary performance vehicle and use the other rarely; most pipelines we have seen populate `TotalReturns`.

The **net-versus-gross distinction** — is this return reported after fees or before them? — is *not* carried through a dedicated enumerated field in the schema. There is no `CalculationBasis` enum. Producers who need to transport the distinction do so through the free-text `<CalculationMethod>` child, using a short convention such as `Net of fees, includes reinvested distributions`. Consumers should read the `<CalculationMethod>` on every entry whose interpretation matters to them, and projects whose producers and consumers talk to each other should agree a project-level convention for the calculation-method text. Chapter 10 treats the validation rules that a performance-reporting pipeline should enforce, and Chapter 13 returns to the project-level convention question.

The three share classes of the Europa Growth Fund each carry their own `PerformanceFigures` block. At the close of 31 March 2026, a representative subset of the values (net of all fees, annualised where applicable) looks like this:

- **R-EUR-ACC**: 1 Year +9.4%, 3 Years +6.8% annualised, 5 Years +7.1% annualised, Since launch +6.3% annualised
- **R-CHF-ACC-HEDGED**: 1 Year +8.1%, 3 Years +5.2% annualised, 5 Years +6.0% annualised, Since launch +5.1% annualised
- **I-EUR-DIST**: 1 Year +10.2%, 3 Years +7.5% annualised, 5 Years +7.8% annualised, Since launch +6.9% annualised

Two patterns are visible in the numbers. First, the R-CHF-ACC-HEDGED class underperforms its base class by roughly one to one and a half percentage points per year, which is the typical order of magnitude for EUR/CHF hedging cost over a multi-year period. Second, the institutional class outperforms the retail class by roughly three-quarters of a percentage point per year, which is approximately the difference in management fees (0.75% for institutional versus 1.50% for retail). Neither pattern is accidental; both are expected consequences of the fee and hedging structure we described in Part II.

### 5.13.2 Ratings, Watermarks, Listed Prices

Beyond total returns, a handful of smaller dynamic figures deserve mention.

**Ratings** live in `PerformanceFigures/Ratings`, where each `<Rating>` carries a `<Note>` (the rating value as given by the agency — "5 stars", "AA+", "Silver"), optionally a `<NumericalValue>`, a `<ValidityStartDate>` and optional `<ValidityEndDate>`, and a choice between `<ListedAgency>` (drawn from an enumeration: `FERI`, `FITCH`, `MOODYS`, `MORNINGSTAR`, `STANDARD-POORS`) and `<UnlistedAgency>` (a `CompanyType` for other providers). A Morningstar five-star rating for the Europa Growth Fund's R-EUR-ACC class would be carried as `<Note>5</Note>` with `<ListedAgency>MORNINGSTAR</ListedAgency>`.

**Dividend events** for distributing share classes live in `ShareClass/Distributions`, as we mentioned in §5.10.1. Between ex-dates the class's portfolio continues to generate income; consumers that render client statements on arbitrary dates between distributions compute the accrual themselves from the portfolio income rather than reading a dedicated field, because the schema does not define one. The dividend *events* are the time-series in `Distributions`; the current accrual is derived from the portfolio (Chapter 6) and the most recent event.

**Bid and ask prices** apply to exchange-traded share classes — UCITS that are listed on a public market in addition to, or instead of, being traded through the fund's primary subscription/redemption process. They live inside `ShareClass/Prices/Price/OtherPrices`, alongside the mid-NAV, and are populated only for listed classes. The `ShareClass/MarketPlaces` block (§5.9.1) identifies the exchanges on which the class trades; the bid/ask, when needed, sits alongside the NAV in the price block.

**High watermarks** for share classes that charge a performance fee live in `ShareClass/HighWatermark`, which we already introduced in §5.10.4. The watermark is the reference NAV above which new performance fees accrue, and is typically reset annually on the fee crystallisation date or, in some structures, only when a drawdown is fully recovered. Consumers that show investors the performance-fee regime display the watermark alongside the current NAV so that the investor can see how close the class is to the next fee accrual.

Every one of these fields is optional. Producers that do not use performance fees omit the high watermark; producers whose classes are not listed omit the bid/ask; producers whose classes carry no external ratings omit the ratings block. The schema is permissive about which fields are populated, and consumers are expected to cope with partial blocks.

---

## 5.14 Umbrella Funds and Sub-Funds

We close Part IV of the chapter with a variation that we have, until now, deliberately avoided: the umbrella fund structure under which most real European UCITS actually live. Everything we have said about the Europa Growth Fund so far has treated it as a standalone fund — a single legal entity with a single portfolio, a single investment policy, and a set of share classes. In reality, a Luxembourg UCITS of its size would almost always be organised as a *sub-fund* within an *umbrella*: a single legal entity called *"Europa Asset Management Investments SICAV"* (the umbrella), inside which the Europa Growth Fund is one of several sub-funds, each with its own portfolio and each with its own share classes. The umbrella structure is legally efficient — one set of constitutional documents, one board of directors, one regulator — while giving each sub-fund its own investment mandate and its own economic identity.

FundsXML models this structure through the `<Subfunds>` alternative inside `<Fund>` that we deferred in §5.2. An umbrella is represented as a single `<Fund>` element whose `<SingleFundFlag>` is `false` and whose `<Subfunds>` container (instead of `<SingleFund>`) holds one `<Subfund>` element per sub-fund. Each `<Subfund>` is itself a fully-fledged unit — schema type `SubfundType` — with its own `Identifiers`, `Names`, `Currency`, `SubfundStaticData`, `SubfundDynamicData`, and its own `ShareClasses` list. The umbrella's fund-level `<Identifiers>/<LEI>` identifies the umbrella SICAV as a legal entity; each `<Subfund>/<Identifiers>/<LEI>` identifies the individual sub-fund. A consumer that walks the tree can therefore distinguish umbrella and sub-fund at the LEI level without ambiguity.

Two structural consequences deserve to be named. First, the **LEI hierarchy doubles**: the umbrella has its own LEI on the outer `<Fund>`, and each sub-fund has its own LEI on its `<Subfund>`. Regulators that report at the umbrella level read the umbrella LEI; regulators that report at the sub-fund level read the sub-fund LEI. The asset manager, meanwhile, has its own separate LEI from Chapter 4, and the three should never be confused. Second, the **share classes operationally attach to the sub-fund**: the `<ShareClass>` elements live inside `<Subfund>/<ShareClasses>` rather than inside `<SingleFund>/<ShareClasses>`, but they use the same `ShareClassType` and the same vocabulary we built up in Part II. For a consumer that already understands the standalone-fund case, the step up to an umbrella is therefore small: read `<Subfunds>/<Subfund>` instead of `<SingleFund>` as the container for share classes, and everything below that level is unchanged. This chapter does not build out a complete umbrella example; Chapter 13 returns to the umbrella form in production context when it discusses the operational implications of running a pipeline over a multi-sub-fund SICAV.

For the running example of this chapter we continue to show the Europa Growth Fund as a standalone fund — a `<Fund>` with `<SingleFundFlag>true</SingleFundFlag>` and a `<SingleFund>` child rather than a `<Subfunds>` child. This is a pedagogical simplification, not a representation of its real legal form. The simplification lets us focus on the share-class structure without also having to explain umbrella mechanics; the complete example in §5.15 is in the standalone form.

---

## 5.15 The Complete Fund Element for the Europa Growth Fund

We are now ready to assemble the first complete `<Fund>` element of the book. The listing below combines everything we have treated in Parts I, II, and III of this chapter: the mandatory identity header, the full `FundStaticData` block with classifications and benchmarks, the `FundDynamicData` fund-level aggregates, the `SingleFund` container, and three `<ShareClass>` entries. To keep the listing readable we show the R-EUR-ACC class in full and collapse the other two classes to their distinguishing fields; portfolio and flow sub-blocks are elided with comments because they belong to Chapters 6 and 7. The complete listing in its fully-populated form appears in Appendix D, and the fragment below has been validated against `FundsXML4.xsd` end-to-end when embedded in the standard `<FundsXML4>/<Funds>` envelope.

```xml
<Fund>
  <Identifiers>
    <LEI>549300ABCDEFGHIJKL34</LEI>
    <OtherID ListedType="INTERNAL FUND CODE">EAM-EGF-001</OtherID>
  </Identifiers>
  <Names>
    <OfficialName>Europa Asset Management Investments — Europa Growth Sub-Fund</OfficialName>
    <MarketingName>Europa Growth Fund</MarketingName>
    <ShortName>EGF</ShortName>
    <LanguageNames>
      <Name language="de">Europa Wachstumsfonds</Name>
      <Name language="fr">Europa Fonds de Croissance</Name>
    </LanguageNames>
  </Names>
  <Currency>EUR</Currency>
  <SingleFundFlag>true</SingleFundFlag>

  <FundStaticData>
    <DomicileCountry>LU</DomicileCountry>
    <ListedLegalStructure>UCITS - SICAV</ListedLegalStructure>
    <InceptionDate>2012-01-15</InceptionDate>
    <FundTexts>
      <FundText>
        <Language>en</Language>
        <Date>2025-12-31</Date>
        <ListedType>INVESTMENT STRATEGY</ListedType>
        <Title>Investment Objective</Title>
        <Content>The Europa Growth Fund seeks long-term capital appreciation through investment in a diversified portfolio of European equities selected for their growth potential.</Content>
      </FundText>
      <!-- additional FundText entries in de, fr, it ... -->
    </FundTexts>
    <Classifications>
      <Classification>
        <ListedGroup>EFAMA</ListedGroup>
        <Type>EFC</Type>
        <Language>en</Language>
        <Value level="1">Equity</Value>
        <Value level="2">Equity Europe</Value>
      </Classification>
      <Classification>
        <ListedGroup>MORNINGSTAR</ListedGroup>
        <Type>Global Category</Type>
        <Language>en</Language>
        <Value>Europe Large-Cap Growth Equity</Value>
      </Classification>
    </Classifications>
    <Benchmarks>
      <Benchmark>
        <BenchmarkID>MSCI-EUR-NR</BenchmarkID>
        <Name>MSCI Europe Net Total Return EUR</Name>
        <Currency>EUR</Currency>
        <Provider>
          <Identifiers><LEI>549300YZUBM5UFHQKY25</LEI></Identifiers>
          <Name>MSCI Limited</Name>
        </Provider>
        <BenchmarkType>Market Index</BenchmarkType>
      </Benchmark>
    </Benchmarks>
    <FundHedgingStrategy>
      <HedgingStrategy>Full NAV hedge</HedgingStrategy>
    </FundHedgingStrategy>
    <OngoingCosts>
      <OngoingCost>
        <CostType>Ongoing Charges</CostType>
        <PublicationDate>2025-06-30</PublicationDate>
        <ValidFrom>2025-07-01</ValidFrom>
        <ValidTo>2026-06-30</ValidTo>
        <Percentage>1.85</Percentage>
      </OngoingCost>
    </OngoingCosts>
    <SFDRProductType>6</SFDRProductType>
  </FundStaticData>

  <FundDynamicData>
    <TotalAssetValues>
      <TotalAssetValue>
        <NavDate>2026-03-31</NavDate>
        <TotalAssetNature>OFFICIAL</TotalAssetNature>
        <TotalNetAssetValue>
          <Amount ccy="EUR" isFundCcy="true">464552848.78</Amount>
        </TotalNetAssetValue>
      </TotalAssetValue>
    </TotalAssetValues>
    <!-- Portfolios: see Chapter 6. Benchmarks: dynamic level values, elided. -->
  </FundDynamicData>

  <SingleFund>
    <SingleFundStaticData>
      <ExchangeTradedFlag>false</ExchangeTradedFlag>
      <FundOfFundFlag>false</FundOfFundFlag>
      <SocialResponsibleFlag>false</SocialResponsibleFlag>
      <ManagementType>ACTIVE</ManagementType>
      <PricePublishedFlag>true</PricePublishedFlag>
      <SalesCategory>PUBLIC</SalesCategory>
    </SingleFundStaticData>
    <ShareClasses>
      <ShareClass>
        <Identifiers>
          <ISIN>LU2100000011</ISIN>
          <GermanWKN>A2GROW</GermanWKN>
          <SwissValorenCode>54321001</SwissValorenCode>
        </Identifiers>
        <Names>
          <OfficialName>Europa Growth Fund — R EUR ACC</OfficialName>
          <ShortName>EGF R EUR ACC</ShortName>
        </Names>
        <Currency>EUR</Currency>
        <ShareClassType>
          <Code>R</Code>
          <EarningUse>R</EarningUse>
          <Name>Retail Accumulating</Name>
        </ShareClassType>
        <InceptionDate>2012-01-15</InceptionDate>
        <RegistrationCountries>
          <RegistrationCountry><CountryCode>LU</CountryCode><Status>Registered</Status></RegistrationCountry>
          <RegistrationCountry><CountryCode>DE</CountryCode><Status>Registered</Status></RegistrationCountry>
          <RegistrationCountry><CountryCode>FR</CountryCode><Status>Registered</Status></RegistrationCountry>
          <!-- IT, ES, NL, AT, BE, PT, CH, SE elided -->
        </RegistrationCountries>
        <SubscriptionRestrictions>
          <MinSubscriptionAmount>
            <Amount ccy="EUR">100</Amount>
          </MinSubscriptionAmount>
          <MinSubscriptionAmountSubsequent>
            <Amount ccy="EUR">50</Amount>
          </MinSubscriptionAmountSubsequent>
        </SubscriptionRestrictions>
        <OpenToNewInvestorsFlag>true</OpenToNewInvestorsFlag>
        <CurrencyHedgedFlag>false</CurrencyHedgedFlag>
        <IsReferenceShareClass>true</IsReferenceShareClass>
        <IsPublicFlag>true</IsPublicFlag>
        <Prices>
          <Price>
            <ActionCode>C</ActionCode>
            <NavDate>2026-03-31</NavDate>
            <PriceCurrency>EUR</PriceCurrency>
            <PriceNature>OFFICIAL</PriceNature>
            <NavPrice>124.50780000</NavPrice>
          </Price>
        </Prices>
        <TotalAssetValues>
          <TotalAssetValue>
            <NavDate>2026-03-31</NavDate>
            <TotalAssetNature>OFFICIAL</TotalAssetNature>
            <TotalNetAssetValue>
              <Amount ccy="EUR" isShareClassCcy="true">153712654.83</Amount>
            </TotalNetAssetValue>
            <SharesOutstanding>1234567</SharesOutstanding>
            <Ratio>33.09</Ratio>
          </TotalAssetValue>
        </TotalAssetValues>
        <Fees>
          <Fee>
            <Type>Management Fee</Type>
            <PayReceive>P</PayReceive>
            <Maximum>1.50</Maximum>
            <CalculationMethod>Per annum of average net assets, accrued daily</CalculationMethod>
            <DataByPeriods>
              <DataByPeriod>
                <BeginDate>2025-07-01</BeginDate>
                <EndDate>2026-06-30</EndDate>
                <CurrentDate>2026-03-31</CurrentDate>
                <Values><FeeAsPercentageOfTNA>1.50</FeeAsPercentageOfTNA></Values>
              </DataByPeriod>
            </DataByPeriods>
          </Fee>
        </Fees>
        <PerformanceFigures>
          <ActionCode>C</ActionCode>
          <TotalReturns>
            <TotalReturn>
              <Currency>EUR</Currency>
              <Value><PercentageValue>9.4</PercentageValue></Value>
              <ValidityDate>2026-03-31</ValidityDate>
              <CalculationPeriod>1 Year</CalculationPeriod>
            </TotalReturn>
            <TotalReturn>
              <Currency>EUR</Currency>
              <Value><PercentageValue>6.8</PercentageValue></Value>
              <ValidityDate>2026-03-31</ValidityDate>
              <CalculationPeriod>3 Years</CalculationPeriod>
              <AnnualizedFlag>true</AnnualizedFlag>
            </TotalReturn>
          </TotalReturns>
        </PerformanceFigures>
      </ShareClass>

      <ShareClass>
        <Identifiers>
          <ISIN>LU2100000029</ISIN>
          <GermanWKN>A2GRCH</GermanWKN>
          <SwissValorenCode>54321002</SwissValorenCode>
        </Identifiers>
        <Names>
          <OfficialName>Europa Growth Fund — R CHF ACC Hedged</OfficialName>
          <ShortName>EGF R CHF ACC H</ShortName>
        </Names>
        <Currency>CHF</Currency>
        <ShareClassType>
          <Code>R</Code><EarningUse>R</EarningUse>
          <Name>Retail Accumulating, Hedged</Name>
        </ShareClassType>
        <InceptionDate>2018-06-01</InceptionDate>
        <SubscriptionRestrictions>
          <MinSubscriptionAmount><Amount ccy="CHF">100</Amount></MinSubscriptionAmount>
        </SubscriptionRestrictions>
        <CurrencyHedgedFlag>true</CurrencyHedgedFlag>
        <FundHedgingStrategy>
          <HedgingStrategy>Full NAV hedge</HedgingStrategy>
        </FundHedgingStrategy>
        <IsPublicFlag>true</IsPublicFlag>
        <Prices>
          <Price>
            <ActionCode>C</ActionCode>
            <NavDate>2026-03-31</NavDate>
            <PriceCurrency>CHF</PriceCurrency>
            <PriceNature>OFFICIAL</PriceNature>
            <NavPrice>119.20110000</NavPrice>
          </Price>
        </Prices>
        <TotalAssetValues>
          <TotalAssetValue>
            <NavDate>2026-03-31</NavDate>
            <TotalAssetNature>OFFICIAL</TotalAssetNature>
            <TotalNetAssetValue>
              <Amount ccy="CHF" isShareClassCcy="true">54438456.22</Amount>
            </TotalNetAssetValue>
            <SharesOutstanding>456789</SharesOutstanding>
            <Ratio>12.21</Ratio>
          </TotalAssetValue>
        </TotalAssetValues>
        <!-- Fees identical in structure to R-EUR-ACC, elided.
             PerformanceFigures: own series, elided. -->
      </ShareClass>

      <ShareClass>
        <Identifiers>
          <ISIN>LU2100000037</ISIN>
          <GermanWKN>A2GRIN</GermanWKN>
        </Identifiers>
        <Names>
          <OfficialName>Europa Growth Fund — I EUR DIST</OfficialName>
          <ShortName>EGF I EUR DIST</ShortName>
        </Names>
        <Currency>EUR</Currency>
        <ShareClassType>
          <Code>I</Code><EarningUse>D</EarningUse>
          <Name>Institutional Distributing</Name>
        </ShareClassType>
        <InceptionDate>2020-09-15</InceptionDate>
        <SubscriptionRestrictions>
          <MinSubscriptionAmount><Amount ccy="EUR">1000000</Amount></MinSubscriptionAmount>
        </SubscriptionRestrictions>
        <CurrencyHedgedFlag>false</CurrencyHedgedFlag>
        <IsPublicFlag>true</IsPublicFlag>
        <Prices>
          <Price>
            <ActionCode>C</ActionCode>
            <NavDate>2026-03-31</NavDate>
            <PriceCurrency>EUR</PriceCurrency>
            <PriceNature>OFFICIAL</PriceNature>
            <NavPrice>108.33440000</NavPrice>
          </Price>
        </Prices>
        <TotalAssetValues>
          <TotalAssetValue>
            <NavDate>2026-03-31</NavDate>
            <TotalAssetNature>OFFICIAL</TotalAssetNature>
            <TotalNetAssetValue>
              <Amount ccy="EUR" isShareClassCcy="true">254115322.56</Amount>
            </TotalNetAssetValue>
            <SharesOutstanding>2345678</SharesOutstanding>
            <Ratio>54.70</Ratio>
          </TotalAssetValue>
        </TotalAssetValues>
        <Distributions>
          <Distribution>
            <ActionCode>C</ActionCode>
            <DividendStatus>OFFICIAL</DividendStatus>
            <AnnouncementDate>2025-05-02</AnnouncementDate>
            <RecordDate>2025-05-14</RecordDate>
            <ExDate>2025-05-15</ExDate>
            <PaymentDate>2025-05-22</PaymentDate>
            <PaymentCurrency>EUR</PaymentCurrency>
            <GrossDividendAmount>
              <PerShare><Amount ccy="EUR">2.1450</Amount></PerShare>
            </GrossDividendAmount>
            <NetDividendAmount>
              <PerShare><Amount ccy="EUR">1.8450</Amount></PerShare>
            </NetDividendAmount>
          </Distribution>
        </Distributions>
        <!-- Fees: Management Fee 0.75%, same structure as R-EUR-ACC, elided. -->
      </ShareClass>
    </ShareClasses>
  </SingleFund>
</Fund>
```

Reading the block is best done in three passes, matching the three parts of this chapter.

The **first pass** looks at the fund's mandatory header and its static data. The `<Identifiers>` block carries the fund's LEI (`549300ABCDEFGHIJKL34`), identifying the Europa Growth Fund as a legal entity distinct from the LEI of its asset manager (Chapter 4), together with a producer-internal reference code in an `OtherID` entry. The `<Names>` block carries the fund's full official name, its marketing name, a short code, and translations into German and French. The fund's base currency is EUR and the `<SingleFundFlag>` is *true*. Inside `<FundStaticData>` the domicile is Luxembourg; the legal structure is *UCITS - SICAV*; the fund was launched in 2012; investment-strategy text is carried under `<FundTexts>`; two parallel `<Classifications>` entries — EFAMA and Morningstar — describe the fund as a European equity product; a single `<Benchmark>` names the MSCI Europe Net Total Return EUR index; a single `<OngoingCost>` entry carries the fund-level headline ongoing charges figure of 1.85% for the current fiscal year; and the `<SFDRProductType>` is 6, marking the fund as an Article 6 product.

The **second pass** looks at the share-class structure, carried inside `<SingleFund>`. The `<SingleFundStaticData>` block labels the fund as actively managed, not exchange-traded, not a fund of funds, and classified as PUBLIC sales. The three share classes themselves are R-EUR-ACC, R-CHF-ACC-HEDGED, and I-EUR-DIST, each inside its own `<ShareClass>` element. Each carries its own `<Identifiers>` block with ISIN and adjacent codes, its own `<Names>` block, its own `<Currency>` (EUR or CHF), its own `<ShareClassType>` with `<Code>` and `<EarningUse>` (`R` for reinvesting, `D` for distributing), its own `<InceptionDate>`, and its own subscription minimum. The R-CHF-ACC-HEDGED class is the only one with `<CurrencyHedgedFlag>true</CurrencyHedgedFlag>`, and it carries a `<FundHedgingStrategy>Full NAV hedge</FundHedgingStrategy>` at class level in addition. The I-EUR-DIST class is the only one with `<EarningUse>D</EarningUse>` and is therefore the only one with a populated `<Distributions>` block — showing the 15 May 2025 dividend event in both its gross and net form.

The **third pass** looks at the dynamic figures. Each `<ShareClass>` carries its own `<Prices>/<Price>` entry — the NAV per unit at 31 March 2026 in the class's own currency — and its own `<TotalAssetValues>/<TotalAssetValue>` with the mandatory `<NavDate>` and `<TotalAssetNature>`, the class's total net asset value (EUR or CHF, marked with `isShareClassCcy="true"`), the shares outstanding, and a `<Ratio>` giving the class's share of the fund's total net assets. Alongside the per-class figures, `<FundDynamicData>/<TotalAssetValues>` carries a single fund-level aggregate entry: 464,552,848.78 EUR, marked with `isFundCcy="true"` to make clear that the currency is the fund's base currency after conversion of the CHF-denominated class. The `<PerformanceFigures>` block on R-EUR-ACC shows two total-return entries (one-year and three-year) to illustrate the shape; a fully populated class would carry six to eight entries covering the full set of standard periods.

This `<Fund>` element is the centrepiece of the Europa Growth Fund's month-end delivery for 31 March 2026, and it will appear — in its complete form, with the portfolio and flows fully populated — in Appendix D. Every subsequent chapter of Part II will take one fragment of the same element for detailed treatment, so that by the time we reach the end of Chapter 9 the reader has seen every part of it explained at least once.

---

## 5.16 Common Pitfalls

The following short list captures the mistakes that, in our experience, cause the greatest share of fund-element-related production incidents.

- **The ISIN is placed on the fund's `<Identifiers>` instead of on each share class's `<Identifiers>`.** Distributors consuming the delivery fail to distinguish the classes and route subscription orders to whichever class they find first. The fix is to move the ISIN into the `<Identifiers>` block of each `<ShareClass>` where it belongs.
- **The share-class currency is confused with the fund base currency.** A consumer reads 119.2011 from the R-CHF-ACC-HEDGED class and treats it as a EUR number, producing NAV values that are wrong by the EUR/CHF rate. The fix is to respect the `ccy` attribute on every `<Amount>` element, and to use the optional `isFundCcy` / `isShareClassCcy` attributes as additional self-description.
- **A share class is omitted from a delivery.** The consumer's current-state engine interprets the absence as a discontinuation and marks the class as closed, leading to factsheet errors and failed order routing. The rule is that every share class must appear in every full delivery even if its data has not changed since the last one.
- **The `EarningUse` code is the wrong letter.** The schema uses `R` for *reinvesting* (accumulating) and `D` for *distributing*; producers occasionally get them the wrong way round because *R* intuitively looks like *retail* or *return*. A class labelled `<EarningUse>R</EarningUse>` when it should be `D` causes every distributing-class consumer to misclassify the fund. The fix is to verify the letter on every class against the class's prospectus behaviour.
- **Performance figures are emitted without a calculation-method annotation.** The schema does not carry a net/gross flag as a structured field; the distinction rides in the free-text `<CalculationMethod>` child of `<TotalReturn>`. One downstream consumer treats the figures as net, another as gross, and the two disagree about how the fund is performing. The fix is to populate a short, project-stable calculation-method string on every entry and to document the convention at project level.
- **The inception date is inherited from the fund rather than set per share class.** A *since-launch* performance figure for the R-CHF-ACC-HEDGED class starts in 2012 (fund inception) rather than 2018 (class inception), showing six years of performance that the class did not experience. The fix is to populate `<InceptionDate>` inside each `<ShareClass>` and compute performance from there.
- **A consumer parses the share-class name to infer currency and earning use.** The consumer's logic breaks when it meets an asset manager whose naming convention differs. The fix is to read `ShareClass/Currency`, `ShareClass/ShareClassType/EarningUse`, `ShareClass/CurrencyHedgedFlag`, and `ShareClass/SubscriptionRestrictions/MinSubscriptionAmount` as structured fields and never depend on the name.
- **The fund-level `<Classifications>` block is used to transport ad-hoc strings rather than recognised classification systems.** A producer writes `<ListedGroup>EFAMA</ListedGroup>` but populates `<Value>` with a home-grown label that the EFAMA taxonomy does not use. Consumers that recognise EFAMA then mismatch. The fix is to populate each `<Classification>` with values from the taxonomy its `<ListedGroup>` names, and to use `<UnlistedGroup>` when the classification is proprietary.

---

## 5.17 Key Takeaways

- A FundsXML document may contain one or several `<Fund>` elements. Each `<Fund>` begins with four mandatory children — `Identifiers`, `Names`, `Currency`, `SingleFundFlag` — and then optionally carries `FundStaticData`, `FundDynamicData`, and a choice of `SingleFund` (for non-umbrella funds) or `Subfunds` (for umbrella structures). Share classes live inside `SingleFund/ShareClasses`, not inside `FundStaticData`.
- Fund identifiers live at two levels, both using the same `IdentifiersType` container. `Fund/Identifiers` carries fund-level codes (principally `LEI`); each `ShareClass/Identifiers` carries share-class-level codes (`ISIN`, `GermanWKN`, `SwissValorenCode`, `CUSIP`, `SEDOL`, and proprietary `OtherID` entries). Confusing the levels is the commonest structural mistake in the fund element.
- Names are modelled through the `NamesType` container with a mandatory `<OfficialName>`, optional `<MarketingName>`, `<ShortName>`, `<FullName>`, `<PreviousName>`, and a `<LanguageNames>` child that holds the multilingual translations as `<Name language="xx">` entries. Longer narrative text lives in `FundStaticData/FundTexts`, with a `<ListedType>` that names the kind of text and a free-form `<Content>`.
- Fund classification — domicile, legal structure, inception date, investment classification, benchmark, SFDR product type — lives in `FundStaticData`. Investment classification is expressed through `Classifications/Classification` entries that reference external taxonomies (EFAMA, Morningstar, MiFID, and others) rather than a single closed vocabulary. The regulatory templates in Chapter 8 provide richer versions of the same information for regulated use cases.
- Share classes are the structural branch of the fund element. Fields that differ between classes — identifiers, `Currency`, `ShareClassType/EarningUse`, `CurrencyHedgedFlag`, `SubscriptionRestrictions`, per-class `Fees`, `InceptionDate`, `Prices`, `TotalAssetValues`, `PerformanceFigures`, `RegistrationCountries` — live on the individual `<ShareClass>` element. Everything common to all classes stays on `<Fund>` or in `FundStaticData`.
- Fees are modelled at three layers. `FundStaticData/OngoingCosts` carries headline fund-level aggregate figures (TER, ongoing charges, transaction costs, performance fees) with `<Percentage>` in human-readable per-cent. `ShareClass/Fees/Fee` carries per-class management and distribution fees with mandatory `Type` and `PayReceive`, optional `Minimum`/`Maximum`/`CalculationMethod`, and `DataByPeriods/DataByPeriod/Values/FeeAsPercentageOfTNA` for the period values. `ShareClass/HighWatermark` carries the high-watermark reference for performance-fee classes.
- Per-class dynamic data lives inside each `<ShareClass>`: `Prices` for the NAV per unit, `TotalAssetValues` for the class aggregate with shares outstanding and ratio, `Distributions` for dividend events, `Flows` for subscriptions and redemptions, `PerformanceFigures` for total returns and ratings. `FundDynamicData/TotalAssetValues` carries only the single fund-level aggregate; consumers that need per-class dynamic figures read them from the classes themselves.
- Performance is carried in `ShareClass/PerformanceFigures` with `<TotalReturn>` entries that name their calculation period through a `<CalculationPeriod>` enumeration (`1 Day`, `1 Month`, `YTD`, `1 Year`, `3 Years`, `Since launch`, `Specific`) and carry their value as either `<AbsoluteValue>` or `<PercentageValue>`. The net-versus-gross distinction rides in free-text `<CalculationMethod>`; there is no dedicated enum for it in the schema.
- Umbrella funds are modelled through the `<Subfunds>/<Subfund>` alternative inside `<Fund>`, with each sub-fund carrying its own `Identifiers`, `Names`, `Currency`, `SubfundStaticData`, `SubfundDynamicData`, and `ShareClasses`. The running example in §5.15 is shown in the standalone `<SingleFund>` form for pedagogical clarity; Chapter 13 treats the umbrella form in production context.

We have now described the Europa Growth Fund: what it is, how its share classes differ, and what its NAVs look like on 31 March 2026. What we have not yet seen is what the fund actually holds. Chapter 6 opens the `Portfolios` substructure of `FundDynamicData` and walks, asset class by asset class, through the instruments that make up the roughly two hundred positions on the fund's books.
