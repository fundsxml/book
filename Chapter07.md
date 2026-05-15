<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 7 — Transactions and Orders

*Flows, distributions, and income events*

---

## 7.1 Setting the Scene: How the Fund Got Where It Is

At the end of Chapter 6 we knew exactly what the Europa Growth Fund held on 31 March 2026 — the one hundred and fifty European equity positions, the three cash accounts, the two currency forwards of the CHF hedge overlay, the 464.5 million euros of total net assets. What we did not know was *how it got there*. Between the previous valuation point on 28 February 2026 and the present one, the fund lived through twenty-three trading days of small and not-so-small changes. Investors bought units and sold them back. A handful of investors moved from one share class to another. European companies paid dividends on the shares the fund holds. Each of these events is a *transaction*, and transactions are the part of fund data that make the dynamic half dynamic.

The chapter walks through the three real schema containers that FundsXML uses to carry these events. The first surprise for a newcomer — and the single most important fact of the chapter — is that **transactions do not live in one central place**. The real schema distributes them across three distinct containers at two different levels of the fund element:

- **`ShareClass/Flows/Flow`** (schema type `FlowType`) carries subscriptions and redemptions. It lives on the **share-class** side of `SingleFund/ShareClasses`, not inside `FundDynamicData`, because subscriptions and redemptions are by definition share-class-specific events.
- **`ShareClass/Distributions/Distribution`** (schema type `DistributionType`) carries dividend payout events in which a distributing share class pays its accumulated income out to its investors. Also share-class-specific.
- **`Portfolio/Earnings/Earning`** (schema type `EarningType`) carries the income events the fund receives from its portfolio holdings — dividends on shares the fund owns, coupons on bonds, interest on cash. These belong to the fund-level **portfolio** inside `FundDynamicData/Portfolios/Portfolio`, because they are properties of the fund's underlying asset pool, not of a specific share class.

Per-security portfolio trading — the portfolio manager buying and selling individual securities — has its own container, `Portfolio/Transactions/Transaction` (schema type `TransactionType`), and is not treated in this chapter; its explicit representation is a topic for Chapter 12 on system landscapes and Chapter 13 on implementation projects. The effect of portfolio trading is visible implicitly in the difference between consecutive portfolio snapshots, which we covered in Chapter 6.

The chapter structure reflects the schema. §7.2 walks through the three containers and their position in the fund element. §7.3 treats the common fields of `FlowType` — the schema type used for subscriptions, redemptions, and the two legs of a switch. §7.4 and §7.5 cover subscriptions and redemptions as the two values of `FlowType/TransactionType` (`SUB` and `RED`). §7.6 treats switches, which the schema represents as a **pair** of linked Flow entries rather than as a first-class transaction type. §7.7 treats distributions through `DistributionType`. §7.8 treats income events through `EarningType`. §7.9 honestly describes the order-execution concepts — cut-off times, forward pricing, swing pricing — that the core schema does **not** model and points at the producer-side mechanisms (`CustomAttributes`, EMT regulatory templates from Chapter 8) for carrying them where they matter. §7.10 assembles the complete transaction block for the Europa Growth Fund's March 2026 period; §7.11 and §7.12 close with pitfalls and takeaways.

One honest disclosure deserves to be made up front. The Europa Growth Fund's I-EUR-DIST share class pays its annual distribution in mid-May, not in March, and the 31 March 2026 delivery therefore contains *no* distribution-paid events. Rather than fabricate one for pedagogical convenience, the chapter treats the absence as a teachable moment: §7.7 shows a hypothetical May distribution to illustrate the structure, and §7.10's complete block honestly omits distributions. This respects both the integrity of the running example and the didactic need to show every event type.

By the end of this chapter, you should be able to:

- identify which of the three schema containers a given transaction belongs to and explain why;
- populate the fields of a `FlowType` entry (subscription or redemption), a `DistributionType` entry, and an `EarningType` entry correctly for a realistic scenario;
- distinguish the four date fields of `FlowType` — `TradeDate`, `AccountingDate`, `SettlementDate`, `ValueDate` — and choose the right one for each operational purpose;
- recognise the difference between distributions *paid* to investors (on `ShareClass/Distributions`) and income *received* from portfolio holdings (in `Portfolio/Earnings`), and never conflate the two;
- represent an intra-fund switch as the two linked `<Flow>` entries the schema actually demands;
- recognise that cut-off times, forward pricing, swing pricing, entry loads, and order-execution variants are operational concepts that the core FundsXML 4.2.8 schema does not model directly, and know where to carry them instead;
- read a complete transaction block for a European UCITS and cross-reference every event to its effect on NAV, shares outstanding, and the portfolio.

---

## 7.2 Where Transactions Live in the Schema

Before we look at any transaction in detail, the structural question: *where, inside a FundsXML document, do transactions live?* The answer is surprising to a newcomer and is the single most important thing to internalise before reading the per-type sections.

**Transactions are not centralised.** There is no single fund-level container for investor flows, distributions, and income events. Each event type lives in its own dedicated container, and each container is attached to a different parent element. The three containers are:

```xml
<Fund>
  <Identifiers>...</Identifiers>
  <Names>...</Names>
  <Currency>EUR</Currency>
  <SingleFundFlag>true</SingleFundFlag>
  <FundDynamicData>
    <Portfolios>
      <Portfolio>
        <NavDate>2026-03-31</NavDate>
        <!-- (1) Income received from portfolio holdings -->
        <Earnings from="2026-03-01" to="2026-03-31">
          <Earning>...</Earning>
          ...
        </Earnings>
      </Portfolio>
    </Portfolios>
  </FundDynamicData>
  <SingleFund>
    <ShareClasses>
      <ShareClass>
        <Identifiers>...</Identifiers>
        <Names>...</Names>
        <Currency>EUR</Currency>
        <!-- (2) Subscriptions and redemptions on this share class -->
        <Flows from="2026-03-01" to="2026-03-31">
          <Flow>...</Flow>
          ...
        </Flows>
        <!-- (3) Distributions paid by this share class to its investors -->
        <Distributions>
          <Distribution>...</Distribution>
        </Distributions>
      </ShareClass>
      <!-- more share classes, each with their own Flows and Distributions -->
    </ShareClasses>
  </SingleFund>
</Fund>
```

Three structural points matter for the rest of the chapter.

**First, investor flows and distributions are share-class-specific.** A subscription into the R-EUR-ACC class of the Europa Growth Fund goes into the [`<Flows>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Flows) container of that specific share class, not into a fund-level flow list. A fund with three share classes has three `<Flows>` blocks, each carrying the flows of its own class. Likewise for [`<Distributions>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Distributions): the distributing I-EUR-DIST class has its own `<Distributions>` block that the two accumulating classes do not share.

**Second, portfolio income belongs to the fund-level portfolio, not to any share class.** When the fund receives a dividend from an Allianz or BNP Paribas position in its portfolio, the event goes into the fund-level `Portfolio/Earnings` container. All three share classes benefit pro-rata from the income through their share of the fund's total net assets — the income is not re-attributed at the share-class level in the transaction data, only in the NAV roll-forward on valuation day.

**Third, the `Flows` container carries two optional date attributes, `@from` and `@to`.** They declare the reporting period covered by the aggregated flow data. For a monthly delivery with `ContentDate` 31 March 2026, a typical declaration is `<Flows from="2026-03-01" to="2026-03-31">`. The [`<Earnings>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio/Earnings) container carries the same pair of attributes for the same purpose. `<Distributions>` does not — a distribution is a single event with its own ex-date, not a period-aggregated collection.

**Figure 7.1 — The transaction timeline**

```
 Valuation point            Reporting period            Valuation point
 28 Feb 2026     ──────────────────────────────────→    31 Mar 2026
    │                                                        │
  TNAV:                                                     TNAV:
 461.2 M EUR            Flows (share-class)              464.6 M EUR
 Shares:                  7 SUB / 4 RED / 1 switch          Shares:
 4.01 M                     (11 Flow entries total          4.04 M
                             across three ShareClasses;
                             the switch = 2 linked Flows)

                         Earnings (portfolio)
                           3 dividend events

                         Distributions (share-class)
                           none (next in mid-May)

                              ↓
                         Schema locations:
                        Fund/FundDynamicData/Portfolios/
                             Portfolio/Earnings
                        Fund/SingleFund/ShareClasses/
                             ShareClass/Flows
                        Fund/SingleFund/ShareClasses/
                             ShareClass/Distributions
```

Between the two valuation points lie the events that explain the transition: `TotalAssetValues` and `Portfolios` (Chapters 5 and 6) give the *states* at either end, and the three transaction containers collectively give the *transitions* that connect them. A consumer that reconciles the fund's movement from one month to the next reads the opening state from the previous delivery, walks every `<Flow>` in every share class's `<Flows>`, every `<Distribution>` in every share class's `<Distributions>`, and every `<Earning>` in the fund-level `<Earnings>`, and checks that the resulting computed state matches the current delivery's `TotalAssetValues` and `Portfolios`. The reconciliation will almost always have small rounding artefacts, but any material discrepancy is a data-quality signal that deserves investigation.

One short remark to close the section: any of the three containers may legitimately be *empty* or absent — if no subscriptions or redemptions took place on a given class during the reporting period, its `<Flows>` block is either omitted entirely or present with no `<Flow>` children. Consumers should accept empty blocks without treating them as errors. A distribution-less month on the I-EUR-DIST class means no `<Distributions>` block at all — or, equivalently, a `<Distributions>` block with no children. Both are valid.

---

## 7.3 The Fields of `FlowType`

Symmetrical to §6.4 and §6.5 from Chapter 6: the fields that appear on every [`<Flow>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass/Flows/Flow) element. Subscriptions, redemptions, and both legs of a switch all use the same schema type, `FlowType`, and differ only in the value of one mandatory discriminator child. This section walks through the common field set; §§7.4 through 7.6 look at the per-case idioms.

**Table 7.1 — Children of `<Flow>` (schema type `FlowType`, XSD §25393), in sequence order**

| Child element | Schema type | Mandatory | Purpose |
|---|---|---|---|
| `<ActionCode>` | enum `C`/`D`/`M` | **yes** | Create, Delete, or Modify; `C` for all new transactions |
| `<DataGroupedBy>` | enum (repeatable) | no | Declares whether the data is aggregated by AccountingDate, TradeDate, Channel, InvestorType, etc. `Nothing` means single-transaction granularity. |
| `<DataGroupedByFrequency>` | `FrequencyType` | no | Period of the aggregation when `<DataGroupedBy>` names a date field |
| `<TransactionID>` | `Text256Type` | no | Unique identifier within the delivery (stable across deliveries by convention) |
| `<TradeDate>` | `xs:date` | no | Day the order was placed by the investor |
| `<AccountingDate>` | `xs:date` | **yes** | Day the transaction was booked into the producer's accounting system |
| `<SettlementDate>` | `xs:date` | no | Day cash and units actually change hands |
| `<ValueDate>` | `xs:date` | no | Day the transaction is effective on the customer account |
| `<TransactionType>` | enum `SUB`/`RED` | **yes** | The critical discriminator: subscription or redemption — there are only two values |
| `<TransactionSubtype>` | `xs:string` | no | Free-text annotation for sub-variants; used for *switch*, *reinvested dividend*, *restructuring plan*, etc. |
| `<Netted>` | `xs:boolean` | no | Whether the data is already netted against other flows |
| `<Cancellation>` | `xs:boolean` | no | Indicator for cancellation of a previously reported transaction |
| `<OriginalTransactionID>` | `Text256Type` | no | ID of a cancelled transaction, for reversal records |
| `<Units>` | `xs:decimal` | no | Number of units moved. **Schema convention: always positive.** Direction is expressed through `<TransactionType>`, not through the sign of `<Units>`. |
| `<FXRate>` | `FXRatesType` | no | FX rate used when the transaction currency differs from the class currency |
| `<TotalValue>` | `FundAmountType` | **yes** | Total value of the transaction, in the fund's base currency (and optionally also in the class currency) |
| `<Channel>` | `Text256Type` | no | Free text: *Retail*, *Institutional*, *Wholesale*, *Web*, *Distribution partner*, … |
| `<InvestorID>` | `Text256Type` | no | Opaque ID of the investor (hash or internal customer number, never a plain name) |
| `<InvestorTypes>` | `InvestorTypesType` | no | Structured investor-type classification (ECB, EMIR, AIFMD categories) |
| `<InvestorCountry>` | `ISOCountryCodeType` | no | Country of the investor |

Four points about the table deserve to be made explicitly in running text rather than left implicit.

**Four date fields, not three, and their semantic is subtly different from the textbook model.** `FlowType` has `<TradeDate>`, `<AccountingDate>`, `<SettlementDate>`, and `<ValueDate>` — and only `<AccountingDate>` is mandatory. There is no element called `EffectiveDate`. The naming map to the operational concepts goes roughly as follows:

- **`<TradeDate>`** — the day the investor placed the order, as observed by the distributor. A subscription that reaches the distributor on Monday 16 March 2026 at 11:30 CET has `TradeDate=2026-03-16`.
- **`<AccountingDate>`** — the day the transaction was booked into the producer's accounting system. In the European forward-pricing model this is typically the same day as the trade date *if* the order arrived before the fund cut-off; orders that arrived after the cut-off get the next trading day's accounting date, and this is how the schema captures the "which NAV did the investor actually pay?" question. `AccountingDate` is the field that maps to the day whose NAV was applied, and it is the one mandatory date on every flow.
- **`<SettlementDate>`** — the day cash and units actually change hands at T+2 or T+3. A subscription booked on Monday 16 March 2026 settles on Wednesday 18 March (T+2, the Luxembourg standard) or Thursday 19 March (T+3).
- **`<ValueDate>`** — the day on which the transaction is effective on the investor's account for interest-accrual purposes. Often identical to `AccountingDate` in the European UCITS world, distinct only in specialised structures.

Consumers that compute NAV adjustments read `AccountingDate`; consumers that post cash movements to custodian accounts read `SettlementDate`; consumers that archive audit logs and timestamp orders read `TradeDate`. Only `AccountingDate` is mandatory, but producers should populate all four where they are known, because a consumer that finds one of them missing has to guess. The legacy textbook term *effective date* corresponds to `AccountingDate` in FundsXML vocabulary, and the safest reading discipline is to remember that the schema uses the word *accounting*, not *effective*, for the pricing-date field.

**The `<TransactionType>` enumeration has only two values.** `SUB` for subscription, `RED` for redemption. That is the entire schema-level taxonomy of flow events. There is no dedicated value for *switch*, *distribution*, *income*, or anything else — those event types either live in other containers (`<Distributions>`, `<Earnings>`) or are modelled as a pair of `SUB`/`RED` records tied together through `<TransactionSubtype>` and `<TransactionID>` conventions (§7.6 on switches). A producer that invents a `FlowType` enumeration with English labels is writing a different format, not FundsXML.

**`<Units>` is always positive on FlowType — direction comes from `<TransactionType>`.** The schema documentation states this explicitly: "Number of shares/units bought or sold (should be always positive)." A redemption of 15,000 units carries `<Units>15000.0000</Units>`, not `-15000`. The *direction* of the flow — is the fund receiving or paying out cash? — is carried exclusively by `<TransactionType>`. A consumer that infers direction from the sign of `<Units>` is reading a convention that the schema does not define and that many producers will not supply.

**`<TotalValue>` is the one mandatory money amount, and it follows the fund-currency convention of Chapter 6.** `TotalValue` is of type `FundAmountType`, so it can carry several `<Amount ccy="…">` children at once — one in the fund's base currency (marked `isFundCcy="true"`) and optionally one in the share class's native currency (marked `isShareClassCcy="true"`). For a subscription into the R-CHF-ACC-HEDGED class, a producer who wants to transport both figures writes two `<Amount>` children — one `ccy="CHF" isShareClassCcy="true"` for the investor's view and one `ccy="EUR" isFundCcy="true"` for the fund's reconciliation. There are **no** `GrossAmount`/`NetAmount`/`EntryLoad`/`ExitLoad`/`NavUsed` fields on `FlowType`. Entry loads and swing-pricing adjustments are operational concepts that the core schema does not model; producers that need to carry them use `<CustomAttributes>` on the share class or the regulatory-template cost fields of Chapter 8 (§7.9 returns to this).

**`<TransactionID>` follows the same logic as `UniqueID` in Chapter 6** in the *conventional* sense: producers should make it unique within the delivery and stable across consecutive deliveries, so that consumers can reconcile. Unlike `UniqueID` on `Asset`, though, `TransactionID` is **not** declared as `xs:ID` in the schema — it is a plain `Text256Type`. This means the parser does not enforce uniqueness, and two `<Flow>` entries with the same `TransactionID` will schema-validate; the uniqueness discipline is purely a business convention. The recommended project-level convention is a deterministic string derived from the producer's order-management-system identifier, the event type, and the date — something like `EGF-TX-20260316-0024`. Chapter 13 will formalise this.

---

## 7.4 Subscriptions

The canonical `<Flow>` with `<TransactionType>SUB</TransactionType>`. Three subsections.

### 7.4.1 The Economic Model

A subscription is the operation in which an investor gives the fund cash and, in exchange, receives newly issued units of one of the fund's share classes. The economic flow is straightforward:

- The investor pays a cash amount into the share class's collection account.
- The share class computes how many units that cash amount buys at the relevant settlement NAV.
- New units are created; the class's total shares outstanding (which we saw in §5.12 as `ShareClass/TotalAssetValues/TotalAssetValue/SharesOutstanding`) increases by that count.
- The fund now has more cash to deploy — the portfolio manager will put the inflow to work in the next trading cycle by buying additional portfolio positions.

At the schema level, subscriptions are `<Flow>` entries inside the target share class's `<Flows>` container, with `<TransactionType>SUB</TransactionType>` as the discriminator. All of the common `FlowType` fields of §7.3 apply.

### 7.4.2 Pricing: When Is the NAV Struck

The critical conceptual question for subscriptions is *which NAV does the investor pay?* Three variants exist in the fund industry, but in the European UCITS world one of them dominates.

**Forward pricing** (the European standard): The investor places the order before a cut-off time (typically 13:00 CET for UCITS with daily valuation), and the NAV used to settle the order is the NAV that is computed at the *end* of the same trading day. At the moment the order is placed, the investor therefore does *not* know the price they are paying — they find out only after the markets close and the NAV has been computed. This is deliberate: forward pricing prevents "market timing", a practice in which an investor who already knows what the day's market movement will be exploits the stale NAV of the historic-pricing model to buy at yesterday's quote.

**Historic pricing** (rare, not UCITS-compatible): The investor buys at the last published NAV. This model is still used in a handful of AIFs and in some legacy structures, but it is effectively barred for UCITS by the regulation that followed the market-timing scandals of the early 2000s.

**Market pricing** (only for exchange-traded share classes): The investor buys the units on a stock exchange at the market quote, not at the fund's NAV. Creation and redemption by authorised participants happens in parallel through NAV-based processes, but ordinary retail investors in listed classes trade on the exchange at bid/ask prices that reflect, but are not identical to, the underlying NAV.

The Europa Growth Fund uses forward pricing on all three share classes. The cut-off is 13:00 CET on every Luxembourg trading day; orders received before the cut-off are settled at the NAV of the same day, and orders received after the cut-off are settled at the NAV of the next trading day. The consequence for the four date fields of §7.3 is concrete: `<TradeDate>` is the day the order was placed, `<AccountingDate>` equals `<TradeDate>` if the order was before the cut-off or equals `<TradeDate> + 1 business day` if it was after (the schema models the pricing-day decision through the accounting date, not through a dedicated field), and `<SettlementDate>` equals `<AccountingDate> + 2 business days` — T+2, the Luxembourg standard.

**A note on what the schema does not model.** FundsXML 4.2.8 does not carry the NAV that was actually applied to the subscription as an element on the `<Flow>`. The NAV is looked up indirectly by the consumer: the consumer reads the `<AccountingDate>` from the flow, then reads the NAV for that date from the share class's `<Prices>/<Price>` history (Chapter 5 §5.12.2). This decoupling is deliberate — the NAV history lives in one place, the transactions in another — and it keeps both halves small and composable. Similarly, entry loads, gross-versus-net breakdowns, and order-execution variants are **not** schema fields on `<Flow>`. §7.9 revisits why and explains what producers do when they need to carry them.

### 7.4.3 Subscription Example: A Retail Investor Subscribes to R-EUR-ACC

A complete XML example for a realistic subscription transaction. On Monday 16 March 2026 a retail investor subscribes 10,000 EUR to the R-EUR-ACC class of the Europa Growth Fund. The order is placed at 11:30 CET, comfortably before the 13:00 cut-off, so it is settled at the Monday evening NAV of 16 March 2026 — let us say 123.9504 EUR, representing a mid-March level between the February month-end and the 31 March figure of 124.5078 we saw in Chapter 5. The investor receives `10000 / 123.9504 = 80.6852` units. The `<Flow>` entry lives inside `<ShareClass>/<Flows>` for the R-EUR-ACC class (ISIN `LU2100000011`).

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000011]/Flows -->
<Flow>
  <ActionCode>C</ActionCode>
  <TransactionID>EGF-TX-20260316-0024</TransactionID>
  <TradeDate>2026-03-16</TradeDate>
  <AccountingDate>2026-03-16</AccountingDate>
  <SettlementDate>2026-03-18</SettlementDate>
  <ValueDate>2026-03-16</ValueDate>
  <TransactionType>SUB</TransactionType>
  <Units>80.6852</Units>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">10000.00</Amount>
  </TotalValue>
  <Channel>Retail</Channel>
</Flow>
```

Reading field by field: the `<ActionCode>C</ActionCode>` marks the entry as a new (create) record — the schema demands it, and every fresh transaction in a delivery carries `C`. The `<TransactionID>` is the producer's unique key. The four date fields reflect forward pricing: same-day trade and accounting (Monday pre-cut-off), T+2 settlement on Wednesday, and an explicit `<ValueDate>` for completeness. The **mandatory** `<TransactionType>SUB</TransactionType>` identifies the direction. `<Units>` is positive — the schema convention, regardless of direction — and carries the 80.6852 units the investor receives. The mandatory `<TotalValue>` carries the 10,000 EUR amount, flagged as being in the fund's base currency. The optional `<Channel>Retail</Channel>` annotates the customer segment.

Two observations are worth making. First, note what is *not* in the listing: no `FlowType`, no `ShareClassISIN` (the class is identified by the parent element), no `Amount`, no `GrossAmount`, no `NetAmount`, no `EntryLoad`, no `NavUsed`, no `OrderExecutionType`. All of those would be schema-invalid as direct children of `<Flow>`. Second, the consistency check `10000.00 / NavUsed = Units` still applies in spirit, but the consumer has to look up the NAV from a different container: it reads the NAV for `AccountingDate=2026-03-16` from `ShareClass/Prices/Price` and then verifies that `Units × NavPrice ≈ TotalValue`. The two halves of the check are in two different places, and that is by design.

---

## 7.5 Redemptions

The mirror operation of subscription, modelled as the second value of `<TransactionType>` — `RED` — in the same `FlowType` structure.

### 7.5.1 The Economic Model

A redemption is the operation in which an investor gives their units back to the fund and, in exchange, receives cash. The economic flow reverses the subscription:

- The investor submits a redemption order, typically for a specific number of units or for a specific cash amount.
- The share class computes how much cash those units are worth at the settlement NAV.
- The units are destroyed; the class's total shares outstanding decreases by that count.
- The fund pays out the amount and must source the cash for the payment, typically by selling portfolio positions in the next trading cycle.

At the schema level, a redemption is a `<Flow>` entry with `<TransactionType>RED</TransactionType>`. Every common `FlowType` field from §7.3 applies, with one important reminder: `<Units>` is still positive. The schema does not use the sign of `<Units>` to distinguish a redemption from a subscription — direction comes exclusively from `<TransactionType>`. A producer that writes a negative `<Units>` value on a redemption is fighting the schema's explicit convention.

### 7.5.2 Swing Pricing, Entry/Exit Loads, and the Concepts the Core Schema Does Not Model

A subtlety that distinguishes redemptions (and large subscriptions) from simple mirror arithmetic: when the fund has to redeem a large number of units at once, the payment produces *transaction costs* in the portfolio — the portfolio manager has to sell shares, and the sales themselves move the market slightly against the fund through the bid-ask spread and market impact. Without an adjustment, the *remaining* unit holders would bear the cost of the departing unit holders — a silent transfer of value from stayers to leavers that is known in the industry as "dilution".

**Swing pricing** is the standard mechanism to neutralise the dilution. When the net number of redemptions on a given trading day exceeds a threshold, the NAV used to settle *all* redemptions of that day is "swung" downward by a small amount — typically 10 to 50 basis points. The departing investors receive slightly less than the "normal" NAV, and the difference compensates for the transaction costs that will be incurred in the portfolio. Three swing-pricing variants exist in practice: **full swing** (applied to every transaction regardless of size), **partial swing** (applied only when net activity crosses a threshold), and **dual pricing** (separate bid and offer NAVs published permanently). The Europa Growth Fund operates partial swing with a 2% threshold.

**The FundsXML 4.2.8 core schema does not model swing pricing, dilution levies, entry loads, or exit loads on `FlowType`.** This is a deliberate architectural choice. The transaction container carries the *what happened* record — date, direction, unit count, total value — and leaves the pricing-adjustment details to other places in the document. Producers who need to carry these concepts have three options:

- **`<CustomAttributes>`** on the share class: Chapter 9 treats the `<CustomAttributes>` mechanism in detail, and for a share class with a swing-pricing regime a producer typically emits attributes such as `SwingPricingType` (with values *Full*/*Partial*/*Dual*), `SwingPricingThreshold` (a percentage), and `SwingPricingFactor` (basis points applied when the threshold is crossed). These attributes describe the *regime*, not individual swing events; the swing applied to a specific transaction is left implicit in the difference between `Flow/TotalValue` and `Units × Price` looked up from `ShareClass/Prices`.
- **The EMT regulatory templates** of Chapter 8 carry the full MiFID II cost disclosure, including entry and exit costs, ongoing charges, and performance fees. For regulatory consumers these are the authoritative source; for operational consumers the swing-pricing policy is a private contract between producer and distributor, carried through the custom attributes above.
- **Project-level convention.** Chapter 13 recommends specific `<CustomAttributes>` keys for swing pricing and entry-load carrying when producers and consumers agree on the convention.

There is therefore no XML example in this sub-section of a `FlowType` record that carries swing-pricing information directly — such an example would be schema-invalid. The operational concepts remain important, and Chapter 13 returns to them in the context of implementation projects; but readers who expect to find `<NavUsed>`, `<SwingAdjustment>`, `<NetNavUsed>`, `<EntryLoad>`, or `<ExitLoad>` on a FundsXML flow will not find them, because they are not there.

### 7.5.3 Redemption Gates and Deferred Redemptions

An extreme case: when a fund receives more redemption orders than it can serve in a single trading cycle (typically because the underlying positions are illiquid and cannot be sold fast enough), the fund can **hold back** redemptions. Two mechanisms exist. **Redemption gates** execute only a fraction of the orders on the current day and defer the rest to the next day (or over several days). **Suspensions** freeze redemptions entirely until the liquidity situation improves. Both mechanisms are provided for in UCITS prospectuses but are practically activated only in crises — the 2008 financial crisis, the March 2020 COVID shock, the 2022 UK gilt-market turbulence that hit LDI funds.

FundsXML has no dedicated fields for gates or suspensions either. Partial executions are modelled as separate `<Flow>` records — a redemption for the executed units today, a second redemption for the remaining units tomorrow, both tied together by a common `<TransactionID>` prefix or by referring to each other through `<OriginalTransactionID>` in the same spirit as the cancellation mechanism of §7.3. The Europa Growth Fund has never activated a gate, and the example block in §7.10 will not show one.

### 7.5.4 Redemption Example

An institutional redemption from the I-EUR-DIST class: on 20 March 2026 a pension fund submits an order to redeem 15,000 units. At the Friday evening NAV of that day — 107.8421 EUR, a mid-March value — the redemption is worth approximately 1.62 million EUR. No swing (the amount is well below the 2% threshold). Settlement T+2 puts the cash payment on 24 March. The `<Flow>` entry lives inside `<ShareClass>/<Flows>` for the I-EUR-DIST class (ISIN `LU2100000037`).

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000037]/Flows -->
<Flow>
  <ActionCode>C</ActionCode>
  <TransactionID>EGF-TX-20260320-0011</TransactionID>
  <TradeDate>2026-03-20</TradeDate>
  <AccountingDate>2026-03-20</AccountingDate>
  <SettlementDate>2026-03-24</SettlementDate>
  <ValueDate>2026-03-20</ValueDate>
  <TransactionType>RED</TransactionType>
  <Units>15000.0000</Units>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">1617631.50</Amount>
  </TotalValue>
  <Channel>Institutional</Channel>
</Flow>
```

Reading field by field, focusing on the differences from §7.4.3: the single mandatory change is `<TransactionType>RED</TransactionType>` — that one field is the entire difference between a subscription and a redemption at the schema level. `<Units>` is **positive** (15000.0000), following the schema's explicit convention, even though the economic direction is outflow. The `<Channel>Institutional</Channel>` annotates the customer segment differently from the retail subscription of §7.4.3. Everything else — the four date fields, the `<ActionCode>`, the `<TotalValue>` — follows the same pattern as the subscription example, which is the whole point: subscriptions and redemptions are the same schema shape distinguished by a single enum value.

---

## 7.6 Switches — Two Linked Flow Entries

The third transaction type conceptually, but **not** a third schema type. This is the single biggest surprise of the chapter for anyone coming from a textbook fund-data background.

### 7.6.1 The Schema Has No "Switch" Transaction Type

A switch is, economically, the combination of two events: a redemption from one share class (the *source*) and a simultaneous subscription to another share class (the *target*). The distinguishing feature is that both legs are settled at the *same* accounting date, at the *same* trade timestamp, and the two are economically linked — the proceeds of the redemption flow directly into the subscription, without the investor receiving cash in between.

**The FundsXML 4.2.8 schema has no dedicated *Switch* transaction type.** The `<TransactionType>` enumeration on `FlowType` has only two values, `SUB` and `RED`, and there is no third value for switches. Consequently, a switch is modelled as **two separate `<Flow>` entries**:

- one `<Flow>` with `<TransactionType>RED</TransactionType>` inside the source class's `<Flows>` container;
- one `<Flow>` with `<TransactionType>SUB</TransactionType>` inside the target class's `<Flows>` container.

The two entries are linked by convention, not by a first-class schema relationship. The two most common linking conventions are:

- **Shared `<TransactionID>` prefix**: both legs carry a `<TransactionID>` whose prefix identifies the switch (e.g. `EGF-SW-20260312-0007-SRC` and `EGF-SW-20260312-0007-TGT`) so that a consumer can pair them by string match.
- **`<TransactionSubtype>` annotation**: both legs carry a `<TransactionSubtype>` value starting with `switch` (the schema element is a free-text `xs:string`, so any convention is allowed) together with a reference to the paired leg's `<TransactionID>`. The schema documentation lists *restructuring plan* and similar free-text conventions as typical values.

Most producers use both conventions simultaneously. A consumer that wants to reconstruct switches walks every `<Flow>` across every share class, groups pairs by the prefix or by the subtype reference, and reports the combined event to its downstream pipeline as a single conceptual switch. A consumer that does *not* know to look for the pairing reads the two legs as an independent redemption and an independent subscription — and that is an acceptable reading for most use cases, because the two legs net to zero at the fund level. The switch interpretation matters only for consumers that track investor-level holdings across classes, and those consumers know to look for the pairing.

This two-record model is a genuine surprise for anyone coming from a format that models switches as first-class transactions. The schema's choice is deliberate: it avoids introducing a three-valued `<TransactionType>` that would need its own rules for quantity and cash-flow direction, and it lets every `<Flow>` continue to be a self-contained record that can be processed independently. The cost is that switch reconciliation is a consumer-side concern, and the quality of the pairing depends on the producer's naming discipline.

### 7.6.2 Intra-Fund Versus Inter-Fund Switches

Two variants exist, and they differ in operational meaning as well as in schema location.

An **intra-fund switch** moves an investor's holding from one share class to another of the *same* fund. Example: a retail investor in the R-EUR-ACC class of the Europa Growth Fund crosses the institutional threshold through portfolio growth and switches to the I-EUR-DIST class to benefit from the lower institutional fee schedule. The switch is economically a non-event for the fund itself — the underlying portfolio does not change; only the share-class attribution of one investor's stake shifts. `SharesOutstanding` of R-EUR-ACC decreases, `SharesOutstanding` of I-EUR-DIST increases, and the fund's total net assets remain unchanged.

In the schema, both legs of an intra-fund switch live in the **same fund**'s `<SingleFund>/<ShareClasses>` block — one in the source class's `<Flows>`, one in the target class's `<Flows>`. Both are in the same delivery and both refer to classes visible in the same document.

These switches are *cost-free* for the fund because they do not trigger any portfolio activity, and most asset managers therefore charge no switch fee on intra-fund moves. They are nevertheless transactions that must be reported, because they change the distribution of shares outstanding across the classes, and consumers that track per-class metrics need to see both legs.

An **inter-fund switch** moves an investor's holding between share classes of *different* funds that belong to the same umbrella. Example: an investor in the Europa Growth Fund wants to move to another sub-fund of the same SICAV — a hypothetical *Europa Asset Management Investments — Emerging Markets Sub-Fund*, for instance. The umbrella structure introduced in Chapter 5.14 permits this kind of switch, and many distributors offer it as a convenience feature that avoids the tax friction of a full market-exit-and-re-entry.

Inter-fund switches are more complex because they touch the portfolios of *both* funds: the source fund must raise cash (selling positions), the target fund must deploy cash (buying positions). In the schema, the two `<Flow>` legs live inside *different* `<Fund>` elements — one inside the source fund's `<SingleFund>/<ShareClasses>/<ShareClass>/<Flows>`, one inside the target fund's. Both affected funds report their own leg in their own delivery (or in different segments of the same multi-fund delivery), and a consumer that reconstructs the full switch needs to see both funds' data.

The Europa Growth Fund, as we established in Chapter 5.14, is shown as a standalone fund in the running example rather than as a sub-fund of a larger umbrella. Inter-fund switches are therefore not represented in the chapter's complete example; Chapter 13 will return to them when it treats umbrella implementation projects.

### 7.6.3 Switch Example

A small intra-fund switch: on 12 March 2026 an investor moves a 50,000 EUR stake from the R-EUR-ACC class to the I-EUR-DIST class. The amount is in reality below the institutional minimum of 1,000,000 EUR and the switch would be rejected by a well-configured order-management system, but for the purpose of illustrating the structure we let it through. The source NAV is 123.7021 EUR (a 12 March value for R-EUR-ACC), the target NAV is 107.7413 EUR (the same day for I-EUR-DIST). The investor gives up `50000 / 123.7021 = 404.2156` units of R-EUR-ACC and receives `50000 / 107.7413 = 464.0882` units of I-EUR-DIST.

**Leg 1 — source redemption, inside the R-EUR-ACC class's `<Flows>`:**

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000011]/Flows -->
<Flow>
  <ActionCode>C</ActionCode>
  <TransactionID>EGF-SW-20260312-0007-SRC</TransactionID>
  <TradeDate>2026-03-12</TradeDate>
  <AccountingDate>2026-03-12</AccountingDate>
  <SettlementDate>2026-03-16</SettlementDate>
  <ValueDate>2026-03-12</ValueDate>
  <TransactionType>RED</TransactionType>
  <TransactionSubtype>switch — source leg; paired with EGF-SW-20260312-0007-TGT on LU2100000037</TransactionSubtype>
  <Units>404.2156</Units>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">50000.00</Amount>
  </TotalValue>
  <Channel>Intra-fund switch</Channel>
</Flow>
```

**Leg 2 — target subscription, inside the I-EUR-DIST class's `<Flows>`:**

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000037]/Flows -->
<Flow>
  <ActionCode>C</ActionCode>
  <TransactionID>EGF-SW-20260312-0007-TGT</TransactionID>
  <TradeDate>2026-03-12</TradeDate>
  <AccountingDate>2026-03-12</AccountingDate>
  <SettlementDate>2026-03-16</SettlementDate>
  <ValueDate>2026-03-12</ValueDate>
  <TransactionType>SUB</TransactionType>
  <TransactionSubtype>switch — target leg; paired with EGF-SW-20260312-0007-SRC on LU2100000011</TransactionSubtype>
  <Units>464.0882</Units>
  <TotalValue>
    <Amount ccy="EUR" isFundCcy="true">50000.00</Amount>
  </TotalValue>
  <Channel>Intra-fund switch</Channel>
</Flow>
```

Four points are worth noting about this pair.

First, the two legs live in **different parent elements** — one inside the R-EUR-ACC [`<ShareClass>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses/ShareClass), one inside the I-EUR-DIST `<ShareClass>`. They are not siblings. A consumer that scans `<Flow>` entries in document order and looks for pairs has to walk across share classes.

Second, the two `<Units>` values are not equal, because the two classes have different NAVs — the investor gives up 404.2156 units of R-EUR-ACC and receives 464.0882 units of I-EUR-DIST, both corresponding to a 50,000 EUR value. The unit count changes, but the economic value does not. Both `<Units>` values are **positive**, following the schema convention, and the direction is carried through `<TransactionType>` (`RED` on the source, `SUB` on the target).

Third, both legs carry identical `<TotalValue>` — the 50,000 EUR common amount that ties the two legs together economically. A consumer that wants to compute the net flow for the fund sees the source leg as an outflow (because `<TransactionType>RED</TransactionType>`) and the target leg as an inflow (because `<TransactionType>SUB</TransactionType>`); the two cancel to zero at the fund level. A consumer that does not recognise the switch pairing still gets the right answer — because the +50,000 and −50,000 net to zero — but displays the move as two separate transactions on the investor's statement instead of as one.

Fourth, the `<TransactionSubtype>` free-text annotation starts with the word *switch* and names the paired leg's `<TransactionID>`. This is a project-level convention rather than a schema rule, but it is the standard way to make the pairing discoverable to a consumer that wants to reconstruct switches. Chapter 13 formalises the convention for projects that care about investor-level reconciliation.

---

## 7.7 Distributions Paid to Investors

The fourth event type — and one that, for the Europa Growth Fund on 31 March 2026, does not apply. The distribution for the I-EUR-DIST class is an annual event in mid-May, and no distribution event belongs to the March reporting period. This section treats the mechanics and the fields nonetheless, because other funds use distributions constantly and because the Europa Growth Fund will emit a distribution event in its May 2026 delivery.

### 7.7.1 The Schema Container

Distributions live in `ShareClass/Distributions/Distribution`, schema type `DistributionType` (XSD §7197). The container is attached to the individual distributing share class — in the Europa Growth Fund's case, to the I-EUR-DIST class only — and lists the distribution events that have been declared for that class. A delivery that carries no distribution event for the reporting period either omits the `<Distributions>` container entirely or emits it empty; both forms are schema-valid.

The container is **not** period-scoped the way `<Flows>` and `<Earnings>` are; there are no `@from`/`@to` attributes on `<Distributions>`. A delivery carries the distribution events whose announcement or ex-date falls inside the reporting period, but the scoping is purely by content, not by a container attribute.

### 7.7.2 The Mechanics of a Distribution and the Four Dates

A distribution is the operation in which a distributing share class pays a portion of its accumulated income out to its investors. The mechanics run through four distinct dates, all of which the schema models:

- **Announcement date** (`<AnnouncementDate>`, optional) — the day the fund's board resolves the distribution and publishes its amount. The schema calls this `AnnouncementDate` rather than the legacy industry term *declaration date*, and a producer writing `<DeclarationDate>` will fail validation.
- **Record date** (`<RecordDate>`, optional) — the day the list of distribution recipients is formally recorded. Typically one or two trading days after the ex-date.
- **Ex-date** (`<ExDate>`, **mandatory**) — the day the class's units trade "without entitlement to the distribution". Any investor holding units at the ex-date receives the distribution; anyone who buys units after the ex-date does not. The class's NAV drops on the ex-date by the per-unit distribution amount, because the class has booked the distribution as a liability to its investors.
- **Payment date** (`<PaymentDate>`, **mandatory**) — the day the cash actually flows to the investors' accounts. Several weeks after the ex-date in most jurisdictions.

The order in the schema sequence is unusual: `AnnouncementDate?`, `RecordDate?`, `ExDate`, `PaymentDate`. Note that `RecordDate` comes before `ExDate` in XML element order, even though operationally it happens after. A producer must emit the elements in schema order regardless of the operational sequence of events.

### 7.7.3 The Amount Structure

The distribution amount is carried through **two** mandatory amount blocks that mirror each other: `<GrossDividendAmount>` and `<NetDividendAmount>`. Each is a small structured element with two children:

- `<Total>` (optional, `PositiveAmountType`) — the total payout flowing out of the fund.
- `<PerShare>` (mandatory, `PositiveAmountType`) — the payout per unit of the share class.

Both amount blocks use `PositiveAmountType`, which is `FundAmountType` restricted to non-negative values. The element names are `DividendAmount` even for distributions that are not formally dividends — the schema uses *dividend* as a generic term for "payout to investors".

**There is no `<DistributionSubType>` element.** The schema does not distinguish `Interim`/`Final`/`CapitalGains`/`ReturnOfCapital` at the `DistributionType` level. A producer that needs to carry the distinction does so either through the free-text `<Comments>` field at the bottom of `DistributionType` or through `<CustomAttributes>` on the share class. In practice the subtype is a tax-reporting concern rather than a schema concern, and the distinction is carried in the regulatory reporting of Chapter 8.

**There is no `<SharesAtRecord>` element.** The shares outstanding at the record date are not a field of `DistributionType`. A consumer that needs the figure reads it from the share class's `<TotalAssetValues>/<SharesOutstanding>` as of the record date, or computes `Total / PerShare` from the two amount children.

### 7.7.4 Other Mandatory Fields

On top of the four dates and the two amount blocks, `DistributionType` carries three more mandatory children that a producer must populate on every entry:

- **`<ActionCode>`** — enum `C`/`D`/`M`, as on every other dynamic record in the schema.
- **`<DividendStatus>`** — enum `ESTIMATED` or `OFFICIAL`. `ESTIMATED` is used for distributions whose amount has been announced but not yet formally resolved; `OFFICIAL` for distributions whose amount is final. A delivery between announcement and formal resolution might carry the same distribution first with `ESTIMATED` and then, in a later delivery, with `OFFICIAL`.
- **`<PaymentCurrency>`** — ISO 4217 code. Usually matches the share class's currency but can differ for classes that pay out in a different currency than they are denominated in (rare).

Seven mandatory children in total, in this order: `ActionCode`, `DividendStatus`, `ExDate`, `PaymentDate`, `PaymentCurrency`, `GrossDividendAmount`, `NetDividendAmount`.

### 7.7.5 The Europa Growth Fund's Situation and a Hypothetical Example

Honest disclosure to the reader: **the 31 March 2026 delivery of the Europa Growth Fund contains no distribution events**. The reason is straightforward: the I-EUR-DIST class pays its annual distribution in mid-May, with an announcement date in early May, an ex-date around 15 May, a record date around 17 May, and a payment date around 27 May. The March delivery sees none of this. The complete example in §7.10 will respect this fact and will not contain a distribution entry, rather than fabricating one for pedagogical convenience.

For the purpose of illustrating the *structure*, however, this subsection shows the hypothetical May distribution as it would appear in the May 2026 delivery of the fund. The assumed values are: announcement date 5 May, record date 17 May, ex-date 15 May, payment date 27 May, gross per share 3.80 EUR, net per share 3.50 EUR (after 7.9% withholding at the fund level), shares outstanding 2,350,000 at record.

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000037]/Distributions -->
<Distribution>
  <ActionCode>C</ActionCode>
  <DividendStatus>OFFICIAL</DividendStatus>
  <AnnouncementDate>2026-05-05</AnnouncementDate>
  <RecordDate>2026-05-17</RecordDate>
  <ExDate>2026-05-15</ExDate>
  <PaymentDate>2026-05-27</PaymentDate>
  <PaymentCurrency>EUR</PaymentCurrency>
  <GrossDividendAmount>
    <Total>
      <Amount ccy="EUR" isFundCcy="true">8930000.00</Amount>
    </Total>
    <PerShare>
      <Amount ccy="EUR" isShareClassCcy="true">3.80</Amount>
    </PerShare>
  </GrossDividendAmount>
  <NetDividendAmount>
    <Total>
      <Amount ccy="EUR" isFundCcy="true">8225000.00</Amount>
    </Total>
    <PerShare>
      <Amount ccy="EUR" isShareClassCcy="true">3.50</Amount>
    </PerShare>
  </NetDividendAmount>
  <DistributionFlag>true</DistributionFlag>
</Distribution>
```

Reading field by field: `<ActionCode>C</ActionCode>` marks the entry as a create record. `<DividendStatus>OFFICIAL</DividendStatus>` signals that the distribution amount has been formally resolved by the board. The four dates — `AnnouncementDate`, `RecordDate`, `ExDate`, `PaymentDate` — are listed in schema order (not in operational order). `<PaymentCurrency>EUR</PaymentCurrency>` matches the I-EUR-DIST class's currency. The two mandatory amount blocks, `<GrossDividendAmount>` and `<NetDividendAmount>`, each carry the total payout and the per-share figure; the net is smaller because of a 7.9% fund-level withholding. `<DistributionFlag>true</DistributionFlag>` is an optional boolean that explicitly confirms the distribution will actually be distributed (as opposed to reinvested as an accrual).

One important corollary that the schema models indirectly: the NAV of the I-EUR-DIST class *drops* on the ex-date of 15 May 2026 by approximately 3.80 EUR per unit. If the NAV on 14 May was, say, 111.20 EUR, the NAV on 15 May would be approximately 107.40 EUR (111.20 minus 3.80), ignoring any other market movement between the two valuation points. The NAV time series carried in `ShareClass/Prices/Price` (Chapter 5 §5.12.2) shows this as a discrete downward jump — exactly the sawtooth pattern that distinguishes distributing classes from their accumulating counterparts, as §5.10.1 explained. The drop is not a loss; it is the mechanical consequence of moving accumulated income from "inside the NAV" to "inside the investors' cash accounts".

---

## 7.8 Income Received from the Portfolio

The fifth event type — and the counterpart to §7.7: money that flows *into* the fund from its portfolio holdings, rather than out from the fund to investors. The schema container is different, the schema type is different, and the wrapper element lives one level up — at the fund-level portfolio rather than inside a share class.

### 7.8.1 The Schema Container and the Fund-Portfolio-Not-Share-Class Rule

Income events live in `Portfolio/Earnings/Earning`, schema type `EarningType` (XSD §7556). The `<Earnings>` container is a child of [`Portfolio`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData/Portfolios/Portfolio) and appears inside `Fund/FundDynamicData/Portfolios/Portfolio` — the same fund-level portfolio where the positions and transactions of Chapter 6 live. The container carries two optional attributes, `@from` and `@to`, that bracket the reporting period.

The critical difference from §7.7 is the level of attachment. **Income events are attached to the fund's portfolio, not to any share class.** When the fund receives a dividend from a portfolio holding, the event is a property of the fund's asset pool, not of a specific class. All three share classes benefit pro-rata from the income through their share of the fund's total net assets; that pro-rata split is implicit in the valuation-day NAV calculation and is not re-recorded in the transaction data.

The distinction from §7.7 is important enough to repeat: **distributions in `ShareClass/Distributions` flow *out of* a share class to its investors; earnings in `Portfolio/Earnings` flow *into* the fund from its portfolio positions**. The two are economic opposites, live in different containers, and use different schema types. A producer that mislabels an income event as a distribution causes a pair of reconciliation failures: the fund appears to lose cash that it should have gained, and the distribution appears to come from an imaginary source.

### 7.8.2 The `EarningKind` Enumeration

Every `<Earning>` carries a mandatory `<EarningKind>` element drawn from a fixed six-value enumeration:

- **`Coupon`** — a coupon payment on a bond held by the fund. The bond pays its periodic coupon (annually, semi-annually, or quarterly depending on the coupon frequency from §6.7.1) and the fund receives the corresponding cash. Coupons are *contractually fixed* in the bond prospectus, not decided each year by the issuer. The `<InterestClaimGross>` from §6.7.2 resets to zero at the coupon payment date, and the accumulated amount flows as cash into the fund.
- **`Dividend`** — a dividend on an equity held by the fund. The most common case in an equity fund like the Europa Growth Fund. The workflow follows the usual ex-date / record / payment pattern, but from the fund's perspective the ex-date is the day the claim arises (booked as a receivable against the issuer) and the payment date is the day the cash arrives. The gap between the two is typically several weeks.
- **`Fund distribution`** — when the fund holds a position in another fund (§6.8), and that fund distributes to its holders, the received distribution is an income event from our fund's perspective.
- **`Interest deposit/giro`** — interest on cash balances. The custodian bank pays the fund periodically at the agreed rate on its balances (or charges negative interest, depending on the market environment). Most commonly settled monthly.
- **`Interest swap`** — interest payments arising from a swap contract's leg.
- **`Other`** — the catch-all for events that do not fit the first five.

Note the exact spelling of each value — the schema is case-sensitive and space-sensitive. `Interest deposit/giro` with its lowercase "deposit" and embedded slash is the real spelling; a producer that writes `InterestDeposit` or `Interest Deposit` will fail validation.

### 7.8.3 The Common `EarningType` Fields and the Typed Sub-Block

`EarningType` has two layers. The **common** layer carries fields that apply to every kind of earning; the **typed** layer is an optional choice of three sub-elements — `<Coupon>`, `<Dividend>`, `<FundDistribution>` — that carries kind-specific breakdowns.

The mandatory common fields, in schema order, are:

- **`<EarningID>`** — a `Text256Type` unique identifier for the earning record. Analogous to `<TransactionID>` on `FlowType` and the same conventions apply (unique within delivery, stable across deliveries, not declared as `xs:ID`).
- **`<EarningKind>`** — the six-value enumeration from §7.8.2.
- **`<EntryDate>`** — the date the earning was booked into the portfolio. Analogous to `<AccountingDate>` on `FlowType`.
- **`<EntryCurrency>`** — the currency in which the earning is booked in the fund's ledger. Usually the fund's base currency; can differ for funds that keep their books in multiple currencies.
- **`<EntryValue>`** — a `FundAmountType` carrying the consolidated value of the earning in the fund's base currency (and optionally also in the income currency).

Optional common fields include `<CancellationFlag>` and `<OriginalEarningID>` for reversal records, `<AssetUniqueID>` (an `xs:IDREF` pointing at the asset in `AssetMasterData` — the same IDREF mechanism as positions use), `<Identifiers>` for an inline copy of the instrument codes, `<ClosingDate>` (the trade date — earlier than `EntryDate` when the booking lags the trade), `<ValutaDate>` (the effective date for interest-accrual purposes), `<IncomeCurrency>` (the currency the issuer paid in, when different from `EntryCurrency`), `<Interests>` (interest value where applicable), `<NominalValueOrUnits>` (the shares or nominal amount the earning was based on), `<ReferenceNumber>`, `<AccountNumber>`, `<PostingText>`, and `<FinallySettled>`.

The **typed sub-block** at the end of `EarningType` is an optional choice of three inline complex types:

- **`<Dividend>`** — carries `<DividendPerUnitValue>`, `<DividendGrossValue>`, `<DividendNetValue>`, `<WithholdingTaxValue>`, `<ExDay>`, `<PayDay>`, `<WithholdingTaxQuota>`. All optional, but populated on every real dividend event.
- **`<Coupon>`** — carries `<UnitInterestsGrossValue>`, `<UnitInterestsNetValue>`, `<CapitalYieldsTaxValue>`, `<EUWithholdingTaxValue>`.
- **`<FundDistribution>`** — carries `<PayoutPerUnitValue>`, `<PayoutGrossValue>`, `<CapitalYieldsTaxUnitValue>`, `<CapitalYieldsTaxOverallValue>`, `<EUWithholdingTaxUnitValue>`, `<EUWithholdingTaxOverallValue>`, `<PayoutIdenticEarningsValue>`, `<ExDay>`.

Exactly one of the three may be present (the choice is optional), and its name matches the `<EarningKind>` value on the common layer: an `EarningKind=Dividend` entry carries a `<Dividend>` sub-block, a `Coupon` entry carries a `<Coupon>` sub-block, and so on. The three cash enumerations (`Interest deposit/giro`, `Interest swap`, `Other`) do not have their own sub-block and populate only the common layer.

### 7.8.4 Withholding Tax

A tax detail that sets income events apart from the other event types: **foreign dividends are typically taxed at source**. A Luxembourg-domiciled fund receiving dividends from a German share sees approximately 26.375% German withholding tax deducted before the net amount arrives in Luxembourg. Depending on the double-taxation treaty between the two countries and on the fund's legal structure, a portion of the withheld amount may later be reclaimable, but at the moment of the payment the fund sees only the net.

FundsXML models withholding tax inside the typed sub-block. For a dividend event, the relevant fields are `<DividendGrossValue>`, `<DividendNetValue>`, `<WithholdingTaxValue>`, and `<WithholdingTaxQuota>` — all inside `<Earning>/<Dividend>`. Consumers that compute fund performance use `<DividendGrossValue>`; consumers that reconcile cash balances use `<DividendNetValue>`. Both are authoritative for their respective use cases, and both should be populated on every dividend from a taxable source. `<WithholdingTaxValue>` is the absolute amount kept at source, and `<WithholdingTaxQuota>` is the rate as a percentage (in the schema's standard human-readable per-cent convention: `26.375` means 26.375%, not 0.26375).

The common-layer `<EntryValue>` typically carries the net amount — the amount that actually arrived in the fund's ledger. A producer that wants to reconcile cash balances reads `EntryValue`; a producer that wants the gross figure reads `Dividend/DividendGrossValue`. The two are both populated, intentionally, and the consumer picks whichever is appropriate.

### 7.8.5 Income Example: A BNP Paribas Interim Dividend

An example of an income event drawn from the actual portfolio of the Europa Growth Fund. BNP Paribas (ISIN `FR0000131104`, 110,000 shares in the portfolio per Chapter 6) pays an interim dividend in Q1, with an ex-date of 20 March 2026 and a payment date of 24 March 2026. The interim amount is 1.50 EUR per share. The gross cash flow to the fund is `110,000 × 1.50 = 165,000.00 EUR`. France applies a 25% withholding tax on dividends paid to foreign recipients under the France-Luxembourg tax treaty, so the fund receives `165,000.00 × 0.75 = 123,750.00 EUR` net.

```xml
<!-- Inside Fund/FundDynamicData/Portfolios/Portfolio/Earnings -->
<Earning>
  <EarningID>EGF-EARN-20260320-0012</EarningID>
  <AssetUniqueID>FR0000131104</AssetUniqueID>
  <EarningKind>Dividend</EarningKind>
  <ClosingDate>2026-03-20</ClosingDate>
  <EntryDate>2026-03-24</EntryDate>
  <ValutaDate>2026-03-24</ValutaDate>
  <EntryCurrency>EUR</EntryCurrency>
  <IncomeCurrency>EUR</IncomeCurrency>
  <EntryValue>
    <Amount ccy="EUR" isFundCcy="true">123750.00</Amount>
  </EntryValue>
  <NominalValueOrUnits>110000</NominalValueOrUnits>
  <PostingText>BNP Paribas Q1 interim dividend, net of 25% French withholding tax</PostingText>
  <Dividend>
    <DividendPerUnitValue>
      <Amount ccy="EUR">1.50</Amount>
    </DividendPerUnitValue>
    <DividendGrossValue>
      <Amount ccy="EUR" isFundCcy="true">165000.00</Amount>
    </DividendGrossValue>
    <DividendNetValue>
      <Amount ccy="EUR" isFundCcy="true">123750.00</Amount>
    </DividendNetValue>
    <WithholdingTaxValue>
      <Amount ccy="EUR">41250.00</Amount>
    </WithholdingTaxValue>
    <ExDay>2026-03-20</ExDay>
    <PayDay>2026-03-24</PayDay>
    <WithholdingTaxQuota>25.00</WithholdingTaxQuota>
  </Dividend>
</Earning>
```

Reading field by field: the `<EarningID>` is the producer's unique key for the earning. The `<AssetUniqueID>` is the back-pointer to the asset entry in `AssetMasterData` (Chapter 6) through an `xs:IDREF` — the consumer sees `FR0000131104` and knows immediately that the event concerns the BNP Paribas position. `<EarningKind>Dividend</EarningKind>` selects the `<Dividend>` sub-block at the bottom.

The three date fields on the common layer — `<ClosingDate>`, `<EntryDate>`, `<ValutaDate>` — tell different parts of the story. `ClosingDate=2026-03-20` is the dividend's ex-date, the day the claim arose. `EntryDate=2026-03-24` is the day the cash was booked into the fund's ledger (four days later, once the payment actually arrived). `ValutaDate=2026-03-24` is the day the amount was effective on the cash account for interest-accrual purposes. For a simple dividend received into a current account, `EntryDate` and `ValutaDate` are usually the same day.

`<EntryCurrency>EUR</EntryCurrency>` names the ledger currency; `<IncomeCurrency>EUR</IncomeCurrency>` names the currency the issuer paid in. For a French dividend paid to a euro-base fund, both are EUR; for a British dividend paid to the same fund, `IncomeCurrency` would be `GBP` and `EntryCurrency` would still be `EUR` (reflecting the custodian's FX conversion). `<EntryValue>` carries the consolidated net amount in the fund's base currency; `<NominalValueOrUnits>110000</NominalValueOrUnits>` records the 110,000 shares the fund held at the ex-date — and the schema annotation deliberately uses the *nominal or units* naming to cover both equities (units) and bonds (nominal).

The `<Dividend>` sub-block at the bottom carries the kind-specific breakdown. `DividendPerUnitValue=1.50 EUR`, `DividendGrossValue=165000.00 EUR`, `DividendNetValue=123750.00 EUR`, `WithholdingTaxValue=41250.00 EUR`, `ExDay=2026-03-20`, `PayDay=2026-03-24`, `WithholdingTaxQuota=25.00`. Note the duplication: `ExDay` in the sub-block mirrors `ClosingDate` on the common layer, and `PayDay` mirrors `EntryDate`. The duplication is deliberate — the sub-block names come from the dividend-specific vocabulary, the common-layer names come from the generic-earning vocabulary, and both are populated so that consumers reading either layer get a consistent picture.

One operational note: the `<NominalValueOrUnits>` field on the income event is the number of shares that *were* held at the record date of the dividend, not the number held on the delivery's valuation date. If the fund had bought additional BNP Paribas shares between the dividend's record date and the valuation date, the position from Chapter 6 would show the higher current count, while the earning event's `NominalValueOrUnits` would record the lower count that actually earned the dividend. The two figures therefore legitimately differ, and consumers that reconcile dividend receipts against positions need to use the record-date shares rather than the current shares.

---

## 7.9 Order Execution, Cut-offs, and the Operational Concepts the Core Schema Does Not Model

The concluding structural section of the chapter, and conceptually distinct from the preceding sections: it treats a set of operational concepts — forward pricing, cut-off times, order-execution variants, in-kind creation, market-traded execution — that **every** UCITS operates with, but that the FundsXML 4.2.8 core schema does not model on `<Flow>`. Producers that need to carry these concepts use mechanisms outside the core transaction containers, and this section walks through what exists, what doesn't, and where the operational data actually lives.

### 7.9.1 What the Schema Does and Does Not Carry on `<Flow>`

We said this in §7.4.2 and §7.5.2, but it deserves one more explicit statement: the core `FlowType` has no element called `OrderExecutionType`, no element called `NavUsed`, no element called `NetNavUsed`, and no element called `SwingAdjustment`. There are no enumeration values `AtNAV`, `ForwardDated`, `HistoricPriced`, `Market`, `Negotiated`, or `InKind` anywhere in the schema. A producer that writes any of these elements or values will fail schema validation.

The operational concepts these labels describe are real — forward pricing, cut-off times, dilution levies, in-kind creation, market-priced ETF trades, negotiated institutional blocks — and they matter every day in European fund distribution. The schema's position is that the `<Flow>` record captures the *outcome* of these mechanisms (the direction, the unit count, the total value, the dates) and not the *process* that produced them. If a consumer needs to know whether a specific trade was executed at NAV or on an exchange, that information lives somewhere else in the delivery or in a separate file entirely.

### 7.9.2 Cut-Off Times and the Forward-Pricing Model

The forward-pricing mechanism depends on a critical concept: the **cut-off time**, the moment in the trading day by which an order must be received in order to be settled at the NAV of *that* day. Orders received after the cut-off are rolled over to the *next* trading day.

The cut-off is understood at two levels in practice:

- The **fund cut-off** — specified in the prospectus, typically 12:00 or 13:00 in the time zone of the fund's domicile. For the Europa Growth Fund, this is 13:00 CET or CEST on Luxembourg trading days.
- The **distributor cut-off** — distributors typically set their own cut-offs a few hours *before* the fund cut-off, to give themselves enough time to aggregate and forward the collected orders to the fund. A German distributor might cut off at 10:30 CET, a French distributor at 11:00 CET.

The consequence: a subscription that reaches the distributor at 10:00 CET makes both the distributor cut-off and the fund cut-off and is settled at the same-day NAV. A subscription that reaches the distributor at 12:00 CET misses the distributor cut-off, even though it would have comfortably made the fund cut-off, and is rolled over to the next trading day's NAV. The distributor effectively adds a one-day delay.

**How the schema captures the result.** FundsXML captures the cut-off decision through the relationship between `<TradeDate>` and `<AccountingDate>` on `<Flow>`. For an order that made the cut-off, both dates are the same day. For an order that missed the distributor cut-off, `<TradeDate>` is the day the investor submitted the order and `<AccountingDate>` is the next trading day whose NAV was applied. A consumer that wants to detect "late" orders reads the difference between the two dates. The schema does not label the order as late or on-time — the dates speak for themselves.

**The prospectus cut-off time itself is not carried in the core schema on a per-flow basis.** Producers that want to transport cut-off metadata for each share class do so through `<CustomAttributes>` on the share class (Chapter 9), with attribute keys such as `CutOffTime` (a time value like `13:00`) and `CutOffTimezone` (`Europe/Luxembourg`). These attributes describe the *regime*; individual `<Flow>` records do not repeat them.

### 7.9.3 Market-Priced Trades, In-Kind Creation, and Exchange-Traded Share Classes

For exchange-traded share classes — UCITS whose units trade on a public market in addition to the NAV-based primary-market channel — the investor-facing trades are executed at the exchange quote, not at the fund's NAV. The creation and redemption process with authorised participants happens in parallel through a NAV-based primary-market channel, but ordinary retail investors in listed classes trade on the exchange at bid/ask prices that reflect, but are not identical to, the underlying NAV.

The FundsXML 4.2.8 core schema does not model exchange-traded flows on `<Flow>`. A producer running an ETF-style share class has two options:

- **Do not emit `<Flow>` records for exchange trades at all.** The exchange-driven creations and redemptions by authorised participants are the only events that meaningfully change the fund's shares outstanding and cash balance, and those events are processed NAV-based through the primary market. Secondary-market exchange trades between investors do not affect the fund's balance sheet and are not reported to the fund.
- **Use `<CustomAttributes>` on the individual `<Flow>`** to annotate the execution channel if the producer's business logic needs it.

For **in-kind creation and redemption** — where a large institutional subscriber delivers a basket of securities to the fund in exchange for units, rather than cash — the schema approach is to emit a `<Flow>` with `<TransactionType>SUB</TransactionType>` and the `<TotalValue>` expressed as the market value of the delivered basket. The basket itself is not listed on the `<Flow>`; the positions that arise from the in-kind subscription appear in the next portfolio snapshot (Chapter 6) and are conventionally annotated through `<TransactionSubtype>in-kind</TransactionSubtype>`.

For **negotiated institutional blocks** — very large trades priced individually between the fund and a counterparty rather than at the standard NAV — the same mechanism applies: an ordinary `<Flow>` carrying the negotiated value, with `<TransactionSubtype>negotiated</TransactionSubtype>` as annotation.

### 7.9.4 The EMT Regulatory Templates and Cost Disclosure

Chapter 8 treats the FinDatEx regulatory templates that the Europa Growth Fund embeds in the `<RegulatoryReportings>` root element. The **European MiFID Template** (EMT) is the relevant one for cost disclosure: it carries the entry costs, exit costs, ongoing charges, performance fees, and transaction costs that an investor in the share class is subject to, in the structure mandated by MiFID II's cost-disclosure rules.

For producers that need to carry entry-load, exit-load, and swing-pricing data in a **regulatory** context — and that is by far the most common reason for carrying them at all — the EMT fields of Chapter 8 are the authoritative place. For *operational* purposes (telling a distributor what fee to charge on a given subscription), the data lives in the producer's order-management system and is not carried in the FundsXML delivery at all.

The rule for readers of this chapter: if you expect to find entry-load or swing-pricing fields on a `<Flow>` record, you will not find them. The core schema captures the *outcome* of the transaction — the direction, the total value, the dates — and leaves the cost-disclosure mechanics to the regulatory templates.

---

## 7.10 The Complete Transaction Block for the Europa Growth Fund

The complete transaction data for the reporting period 1–31 March 2026. Because the schema distributes transactions across three containers at two levels of the fund element, the "complete transaction block" is not one listing — it is **four** separate listings: three `<Flows>` containers (one per share class) and one `<Earnings>` container (at the fund-level portfolio). Structured in four subsections.

### 7.10.1 Overview of the Period

During March 2026 the Europa Growth Fund saw normal transaction activity for a mid-sized European UCITS: seven subscriptions (a net inflow), four redemptions against them, one intra-fund switch, and three dividend income events from European portfolio holdings that paid in Q1. **No distribution-paid events** — the next one is in mid-May, as §7.7 explained.

The fifteen conceptual events map to sixteen schema records, because the one intra-fund switch is represented as two linked `<Flow>` entries in two different share classes. The full breakdown is:

- **R-EUR-ACC `<Flows>` (six `<Flow>` entries)**: 3 subscriptions (03, 16, 23 March), 2 redemptions (06, 13 March), 1 switch source leg (12 March, paired with the I-EUR-DIST target leg).
- **R-CHF-ACC-HEDGED `<Flows>` (three `<Flow>` entries)**: 2 subscriptions (05, 26 March), 1 redemption (19 March). No switch involvement.
- **I-EUR-DIST `<Flows>` (four `<Flow>` entries)**: 2 subscriptions (09, 30 March), 1 redemption (20 March), 1 switch target leg (12 March, paired with the R-EUR-ACC source leg).
- **Fund-level portfolio `<Earnings>` (three `<Earning>` entries)**: Q1 dividends from Allianz (11 March, German), BNP Paribas (20 March, French), and AstraZeneca (27 March, British).

The events are grouped by container below, not by chronological order across the whole delivery, because the schema nesting demands it. Within each container, entries are listed by date. The complete listing in its fully-populated form has been validated against `FundsXML4.xsd` as an end-to-end document with a matching AssetMasterData block carrying the three dividend-paying assets.

### 7.10.2 The R-EUR-ACC Flows Block

The six `<Flow>` entries inside the R-EUR-ACC share class's `<Flows>` container. Three subscriptions, two ordinary redemptions, and the source leg of the switch.

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000011] -->
<Flows from="2026-03-01" to="2026-03-31">
  <!-- Subscriptions -->
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260303-0001</TransactionID>
    <TradeDate>2026-03-03</TradeDate>
    <AccountingDate>2026-03-03</AccountingDate>
    <SettlementDate>2026-03-05</SettlementDate>
    <ValueDate>2026-03-03</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>202.1578</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">25000.00</Amount></TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260316-0024</TransactionID>
    <TradeDate>2026-03-16</TradeDate>
    <AccountingDate>2026-03-16</AccountingDate>
    <SettlementDate>2026-03-18</SettlementDate>
    <ValueDate>2026-03-16</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>80.6852</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">10000.00</Amount></TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260323-0032</TransactionID>
    <TradeDate>2026-03-23</TradeDate>
    <AccountingDate>2026-03-23</AccountingDate>
    <SettlementDate>2026-03-25</SettlementDate>
    <ValueDate>2026-03-23</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>402.4811</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">50000.00</Amount></TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <!-- Redemptions -->
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260306-0004</TransactionID>
    <TradeDate>2026-03-06</TradeDate>
    <AccountingDate>2026-03-06</AccountingDate>
    <SettlementDate>2026-03-10</SettlementDate>
    <ValueDate>2026-03-06</ValueDate>
    <TransactionType>RED</TransactionType>
    <Units>68.7247</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">8500.00</Amount></TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260313-0017</TransactionID>
    <TradeDate>2026-03-13</TradeDate>
    <AccountingDate>2026-03-13</AccountingDate>
    <SettlementDate>2026-03-17</SettlementDate>
    <ValueDate>2026-03-13</ValueDate>
    <TransactionType>RED</TransactionType>
    <Units>258.4821</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">32000.00</Amount></TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <!-- Switch, source leg (paired with EGF-SW-20260312-0007-TGT in the I-EUR-DIST class) -->
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-SW-20260312-0007-SRC</TransactionID>
    <TradeDate>2026-03-12</TradeDate>
    <AccountingDate>2026-03-12</AccountingDate>
    <SettlementDate>2026-03-16</SettlementDate>
    <ValueDate>2026-03-12</ValueDate>
    <TransactionType>RED</TransactionType>
    <TransactionSubtype>switch — source leg; paired with EGF-SW-20260312-0007-TGT on LU2100000037</TransactionSubtype>
    <Units>404.2156</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">50000.00</Amount></TotalValue>
    <Channel>Intra-fund switch</Channel>
  </Flow>
</Flows>
```

### 7.10.3 The R-CHF-ACC-HEDGED Flows Block

Three `<Flow>` entries inside the R-CHF-ACC-HEDGED share class's `<Flows>` container. Two subscriptions and one redemption, all in Swiss francs. The `<TotalValue>` carries *two* `<Amount>` children in each entry — one in CHF flagged `isShareClassCcy="true"`, one in EUR flagged `isFundCcy="true"` — so that consumers reading either currency see a consistent figure.

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000029] -->
<Flows from="2026-03-01" to="2026-03-31">
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260305-0003</TransactionID>
    <TradeDate>2026-03-05</TradeDate>
    <AccountingDate>2026-03-05</AccountingDate>
    <SettlementDate>2026-03-09</SettlementDate>
    <ValueDate>2026-03-05</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>125.8812</Units>
    <TotalValue>
      <Amount ccy="CHF" isShareClassCcy="true">15000.00</Amount>
      <Amount ccy="EUR" isFundCcy="true">14410.75</Amount>
    </TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260326-0038</TransactionID>
    <TradeDate>2026-03-26</TradeDate>
    <AccountingDate>2026-03-26</AccountingDate>
    <SettlementDate>2026-03-30</SettlementDate>
    <ValueDate>2026-03-26</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>335.6181</Units>
    <TotalValue>
      <Amount ccy="CHF" isShareClassCcy="true">40000.00</Amount>
      <Amount ccy="EUR" isFundCcy="true">38428.00</Amount>
    </TotalValue>
    <Channel>Retail</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260319-0022</TransactionID>
    <TradeDate>2026-03-19</TradeDate>
    <AccountingDate>2026-03-19</AccountingDate>
    <SettlementDate>2026-03-23</SettlementDate>
    <ValueDate>2026-03-19</ValueDate>
    <TransactionType>RED</TransactionType>
    <Units>180.4108</Units>
    <TotalValue>
      <Amount ccy="CHF" isShareClassCcy="true">21500.00</Amount>
      <Amount ccy="EUR" isFundCcy="true">20654.68</Amount>
    </TotalValue>
    <Channel>Retail</Channel>
  </Flow>
</Flows>
```

### 7.10.4 The I-EUR-DIST Flows Block

Four `<Flow>` entries inside the I-EUR-DIST share class's `<Flows>` container. Two institutional subscriptions, one institutional redemption, and the target leg of the switch.

```xml
<!-- Inside Fund/SingleFund/ShareClasses/ShareClass[ISIN=LU2100000037] -->
<Flows from="2026-03-01" to="2026-03-31">
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260309-0005</TransactionID>
    <TradeDate>2026-03-09</TradeDate>
    <AccountingDate>2026-03-09</AccountingDate>
    <SettlementDate>2026-03-11</SettlementDate>
    <ValueDate>2026-03-09</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>23202.5830</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">2500000.00</Amount></TotalValue>
    <Channel>Institutional</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260330-0043</TransactionID>
    <TradeDate>2026-03-30</TradeDate>
    <AccountingDate>2026-03-30</AccountingDate>
    <SettlementDate>2026-04-01</SettlementDate>
    <ValueDate>2026-03-30</ValueDate>
    <TransactionType>SUB</TransactionType>
    <Units>46151.2845</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">5000000.00</Amount></TotalValue>
    <Channel>Institutional</Channel>
  </Flow>
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-TX-20260320-0011</TransactionID>
    <TradeDate>2026-03-20</TradeDate>
    <AccountingDate>2026-03-20</AccountingDate>
    <SettlementDate>2026-03-24</SettlementDate>
    <ValueDate>2026-03-20</ValueDate>
    <TransactionType>RED</TransactionType>
    <Units>15000.0000</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">1617631.50</Amount></TotalValue>
    <Channel>Institutional</Channel>
  </Flow>
  <!-- Switch, target leg (paired with EGF-SW-20260312-0007-SRC in the R-EUR-ACC class) -->
  <Flow>
    <ActionCode>C</ActionCode>
    <TransactionID>EGF-SW-20260312-0007-TGT</TransactionID>
    <TradeDate>2026-03-12</TradeDate>
    <AccountingDate>2026-03-12</AccountingDate>
    <SettlementDate>2026-03-16</SettlementDate>
    <ValueDate>2026-03-12</ValueDate>
    <TransactionType>SUB</TransactionType>
    <TransactionSubtype>switch — target leg; paired with EGF-SW-20260312-0007-SRC on LU2100000011</TransactionSubtype>
    <Units>464.0882</Units>
    <TotalValue><Amount ccy="EUR" isFundCcy="true">50000.00</Amount></TotalValue>
    <Channel>Intra-fund switch</Channel>
  </Flow>
</Flows>
```

### 7.10.5 The Fund-Level Portfolio Earnings Block

Three `<Earning>` entries inside the fund-level `<Portfolio>/<Earnings>` container. These are the Q1 2026 dividend receipts from three European portfolio holdings, distinguished by source country through the different withholding-tax regimes. The German entry uses `WithholdingTaxQuota=26.375` (Germany's standard withholding rate), the French entry uses `25.00` (the France-Luxembourg tax-treaty rate), and the British entry uses `0.00` (the United Kingdom does not withhold tax on dividends paid to non-resident shareholders).

```xml
<!-- Inside Fund/FundDynamicData/Portfolios/Portfolio -->
<Earnings from="2026-03-01" to="2026-03-31">
  <Earning>
    <EarningID>EGF-EARN-20260311-0008</EarningID>
    <AssetUniqueID>DE0008404005</AssetUniqueID>
    <EarningKind>Dividend</EarningKind>
    <ClosingDate>2026-03-11</ClosingDate>
    <EntryDate>2026-03-13</EntryDate>
    <ValutaDate>2026-03-13</ValutaDate>
    <EntryCurrency>EUR</EntryCurrency>
    <IncomeCurrency>EUR</IncomeCurrency>
    <EntryValue>
      <Amount ccy="EUR" isFundCcy="true">362830.00</Amount>
    </EntryValue>
    <NominalValueOrUnits>32000</NominalValueOrUnits>
    <PostingText>Allianz SE 2026 annual dividend, net of 26.375% German withholding tax</PostingText>
    <Dividend>
      <DividendPerUnitValue><Amount ccy="EUR">15.40</Amount></DividendPerUnitValue>
      <DividendGrossValue><Amount ccy="EUR" isFundCcy="true">492800.00</Amount></DividendGrossValue>
      <DividendNetValue><Amount ccy="EUR" isFundCcy="true">362830.00</Amount></DividendNetValue>
      <WithholdingTaxValue><Amount ccy="EUR">129970.00</Amount></WithholdingTaxValue>
      <ExDay>2026-03-11</ExDay>
      <PayDay>2026-03-13</PayDay>
      <WithholdingTaxQuota>26.375</WithholdingTaxQuota>
    </Dividend>
  </Earning>
  <Earning>
    <EarningID>EGF-EARN-20260320-0012</EarningID>
    <AssetUniqueID>FR0000131104</AssetUniqueID>
    <EarningKind>Dividend</EarningKind>
    <ClosingDate>2026-03-20</ClosingDate>
    <EntryDate>2026-03-24</EntryDate>
    <ValutaDate>2026-03-24</ValutaDate>
    <EntryCurrency>EUR</EntryCurrency>
    <IncomeCurrency>EUR</IncomeCurrency>
    <EntryValue>
      <Amount ccy="EUR" isFundCcy="true">123750.00</Amount>
    </EntryValue>
    <NominalValueOrUnits>110000</NominalValueOrUnits>
    <PostingText>BNP Paribas Q1 interim dividend, net of 25% French withholding tax</PostingText>
    <Dividend>
      <DividendPerUnitValue><Amount ccy="EUR">1.50</Amount></DividendPerUnitValue>
      <DividendGrossValue><Amount ccy="EUR" isFundCcy="true">165000.00</Amount></DividendGrossValue>
      <DividendNetValue><Amount ccy="EUR" isFundCcy="true">123750.00</Amount></DividendNetValue>
      <WithholdingTaxValue><Amount ccy="EUR">41250.00</Amount></WithholdingTaxValue>
      <ExDay>2026-03-20</ExDay>
      <PayDay>2026-03-24</PayDay>
      <WithholdingTaxQuota>25.00</WithholdingTaxQuota>
    </Dividend>
  </Earning>
  <Earning>
    <EarningID>EGF-EARN-20260327-0015</EarningID>
    <AssetUniqueID>GB0009895292</AssetUniqueID>
    <EarningKind>Dividend</EarningKind>
    <ClosingDate>2026-03-27</ClosingDate>
    <EntryDate>2026-03-31</EntryDate>
    <ValutaDate>2026-03-31</ValutaDate>
    <EntryCurrency>GBP</EntryCurrency>
    <IncomeCurrency>GBP</IncomeCurrency>
    <EntryValue>
      <Amount ccy="GBP">69000.00</Amount>
      <Amount ccy="EUR" isFundCcy="true">81742.50</Amount>
    </EntryValue>
    <NominalValueOrUnits>75000</NominalValueOrUnits>
    <PostingText>AstraZeneca interim dividend, no UK withholding tax on non-resident dividends</PostingText>
    <Dividend>
      <DividendPerUnitValue><Amount ccy="GBP">0.92</Amount></DividendPerUnitValue>
      <DividendGrossValue><Amount ccy="GBP">69000.00</Amount></DividendGrossValue>
      <DividendNetValue><Amount ccy="GBP">69000.00</Amount></DividendNetValue>
      <WithholdingTaxValue><Amount ccy="GBP">0.00</Amount></WithholdingTaxValue>
      <ExDay>2026-03-27</ExDay>
      <PayDay>2026-03-31</PayDay>
      <WithholdingTaxQuota>0.00</WithholdingTaxQuota>
    </Dividend>
  </Earning>
</Earnings>
```

### 7.10.6 A Three-Pass Reading

The four blocks are best understood in three passes, one per conceptual group.

**First pass — investor-side flows.** Eleven `<Flow>` entries representing seven subscriptions and four redemptions, distributed across the three share classes' `<Flows>` containers. The net flow is positive: subscriptions total roughly 7.64 million EUR equivalent (counting the CHF figures via the embedded EUR Amounts in `<TotalValue>`), while redemptions total roughly 1.67 million EUR equivalent. The net inflow is therefore around 6 million EUR for the month. This explains why the `SharesOutstanding` of all three classes grew between 28 February (roughly 4.01 million shares total) and 31 March (the 1,234,567 + 456,789 + 2,345,678 figures from Chapter 5). The institutional class I-EUR-DIST saw the largest single inflows (a 2.5 million EUR subscription on 9 March and a 5 million EUR subscription on 30 March), consistent with the notion that institutional investors make larger but less frequent allocations than retail investors. None of the redemptions triggered swing pricing, because none of them approached the 2% net-outflow threshold — but as §7.5.2 noted, swing-pricing data does not appear in the schema-level `<Flow>` records anyway, so a consumer that wants to verify the no-swing condition reads a `<CustomAttributes>` field on the share class instead.

**Second pass — the switch as two linked Flows.** One intra-fund switch represented as two `<Flow>` entries with a `-SRC`/`-TGT` `<TransactionID>` pairing convention. The source leg sits in the R-EUR-ACC class's `<Flows>` (the fifth entry of §7.10.2's listing) with `<TransactionType>RED</TransactionType>` and 404.2156 units; the target leg sits in the I-EUR-DIST class's `<Flows>` (the fourth entry of §7.10.4's listing) with `<TransactionType>SUB</TransactionType>` and 464.0882 units. Both legs carry the same `<TotalValue>` of 50,000 EUR. The two `<Units>` values differ because the two classes have different NAVs, and both are positive — direction comes from `<TransactionType>`. The pairing convention lives in `<TransactionSubtype>`, which on each leg names the paired leg's ID. A consumer that walks the document linearly sees the two legs as a redemption and a subscription that happen to net to zero at the fund level; a consumer that recognises the pairing reconstructs the conceptual switch. It is technically unlikely that a 50,000 EUR stake would be allowed to cross into the institutional class (the minimum is 1,000,000 EUR), but the example is retained for structural illustration.

**Third pass — income events in the portfolio.** Three `<Earning>` entries inside the fund-level `<Portfolio>/<Earnings>` container, each representing a Q1 dividend from a different country. Each carries its own withholding-tax regime: 26.375% for Germany (Allianz), 25% for France (BNP Paribas), and 0% for the United Kingdom (AstraZeneca; the United Kingdom does not withhold tax on dividends paid to non-resident shareholders, a peculiarity of UK dividend taxation). The gross amounts total 492,800 EUR + 165,000 EUR + 69,000 GBP ≈ 740,000 EUR equivalent; the net amounts total around 570,000 EUR after withholding. These amounts increase the fund's cash balance and contribute to the Q1 income that will eventually feed the May distribution on the I-EUR-DIST class. Each `<Earning>` carries an `<AssetUniqueID>` IDREF pointing at the corresponding entry in `<AssetMasterData>` (Chapter 6), so that a consumer can join the dividend back to the position that earned it without ambiguity.

The four blocks as shown reconcile internally: the sum of `<TotalValue>` deltas across the eleven `<Flow>` entries and the cash inflows from the three `<Earning>` entries are consistent with the movements in `<TotalAssetValues>` between the two valuation points. The complete reconciliation — starting from the 28 February state, applying every flow and every earning in these blocks, arriving at the 31 March state — is printed in Appendix D as a worked example, using the validated end-to-end document this chapter is built from.

---

## 7.11 Common Pitfalls

The following short list captures the mistakes that, in our experience, cause the greatest share of transaction-related production incidents.

- **Looking for transactions in the wrong container.** A consumer expects investor flows under `FundDynamicData` and finds nothing, because the real container is `Fund/SingleFund/ShareClasses/ShareClass/Flows`. Or expects portfolio income events under a share class and finds nothing, because the real container is `Fund/FundDynamicData/Portfolios/Portfolio/Earnings`. The rule: `<Flows>` and `<Distributions>` live on each share class; `<Earnings>` lives on the fund-level portfolio; there is no fund-level `<SingleFundFlows>`-style aggregator.
- **Negative `<Units>` on a redemption.** A producer treats `<Units>` as a signed number to indicate direction. The schema explicitly demands positive values: "Number of shares/units bought or sold (should be always positive)." Direction comes from `<TransactionType>` (`SUB` or `RED`), not from the sign of `<Units>`. A consumer that sums signed units mis-handles the producer's positive-only data and gets the wrong inflow figure.
- **Missing `<ActionCode>`, `<AccountingDate>`, `<TransactionType>`, or `<TotalValue>` on a `<Flow>`.** All four are mandatory in `FlowType`. A producer that omits any of them fails schema validation at load time. The most common omission is `<AccountingDate>`, because legacy systems carry only a "trade date" concept and forget to map it to the schema's accounting-date field.
- **Switch counted as one transaction in either direction.** A consumer sees only the source leg (`<TransactionType>RED</TransactionType>`) of a switch and reports a redemption to the producer's records, without realising that the matching target leg lives in another share class's `<Flows>`. The net flow metric is wrongly negative. The rule: a switch is **two** linked `<Flow>` entries, and a consumer that wants to detect them looks for the `<TransactionSubtype>` annotation or for paired `<TransactionID>` prefixes across share classes.
- **`AnnouncementDate` written as `DeclarationDate`.** A producer migrating from a legacy "declaration date" vocabulary writes `<DeclarationDate>` on a `<Distribution>` and fails schema validation. The schema element is `<AnnouncementDate>`. Similar trap: the schema uses `ExDate`, `RecordDate`, `PaymentDate` as element names — the operational concepts have schema names that do not always match the textbook vocabulary.
- **`<DividendStatus>` missing on a distribution.** Mandatory enum (`ESTIMATED` or `OFFICIAL`). A producer that forgets it fails validation. A consumer that finds it set to `ESTIMATED` should expect the same distribution to reappear in a later delivery with `OFFICIAL` status; treating an `ESTIMATED` distribution as the final value is a recurring source of investor-statement errors.
- **`PerShare` written without the `Total` it pairs with.** `GrossDividendAmount` and `NetDividendAmount` each have an optional `<Total>` and a mandatory `<PerShare>`. The structure is *gross*: `<GrossDividendAmount><Total>...</Total><PerShare>...</PerShare></GrossDividendAmount>`. A producer that emits `<GrossDividendAmount>3.80</GrossDividendAmount>` flat (without the inner `<PerShare>` wrapper) fails validation.
- **Distributions confused with earnings.** A producer or consumer treats a dividend received from a portfolio holding (an `<Earning>` in the portfolio) as if it were a distribution paid to investors (a `<Distribution>` in a share class), or vice versa. The two are economic opposites and live in different containers. The rule: cash flows *into* the fund go into `Portfolio/Earnings`; cash flows *out of* a share class to its investors go into `ShareClass/Distributions`.
- **Withholding tax forgotten on income events.** A consumer sums the `<DividendGrossValue>` fields of `<Earning>` records without subtracting the `<WithholdingTaxValue>` and computes the fund's cash balance too high. Reconciliation with the custodian statement fails. The rule: use `<EntryValue>` (or `<DividendNetValue>`) for cash reconciliation, `<DividendGrossValue>` for income analysis.
- **`<EarningKind>` value misspelled.** The schema enumeration is `Coupon`, `Dividend`, `Fund distribution`, `Interest deposit/giro`, `Interest swap`, `Other`. Producers that write `Fund Distribution` (capital D), `InterestDeposit`, or `Interests` fail validation. The exact spelling — including the embedded slash and the lowercase second word — is part of the schema.
- **`<SettlementDate>` values treated as trade dates.** A consumer archives the `<SettlementDate>` of a `<Flow>` as the trade date, and later queries for "which orders came in on day X?" return wrong results. The rule: `<TradeDate>` for audit and reporting, `<AccountingDate>` for NAV pricing, `<SettlementDate>` only for cash movements.
- **`OrderExecutionType` written as a `<Flow>` child.** A producer migrating from another fund-data format writes `<OrderExecutionType>AtNAV</OrderExecutionType>` and fails schema validation, because no such element exists. The operational concept (forward pricing, cut-offs, in-kind subscription, exchange execution) is not modelled in the core schema; producers that need to carry it use `<CustomAttributes>` or the regulatory templates of Chapter 8.

---

## 7.12 Key Takeaways

- Transactions are not centralised in FundsXML. They live in three different containers attached to two different parents: subscriptions and redemptions in `ShareClass/Flows/Flow` (schema type `FlowType`), distributions paid to investors in `ShareClass/Distributions/Distribution` (`DistributionType`), and income received from portfolio holdings in `Portfolio/Earnings/Earning` (`EarningType`). There is no fund-level aggregator container.
- `FlowType` carries four mandatory children — `<ActionCode>`, `<AccountingDate>`, `<TransactionType>`, `<TotalValue>` — and a binary `<TransactionType>` enumeration with only two values: `SUB` and `RED`. The schema does not define a third value for switches, distributions, or income; those event types either live in other containers or are modelled as paired `SUB`/`RED` records.
- Every `<Flow>` carries up to four date fields: `<TradeDate>`, `<AccountingDate>`, `<SettlementDate>`, `<ValueDate>`. Only `<AccountingDate>` is mandatory. There is no element called `EffectiveDate`; the legacy textbook *effective date* maps to `<AccountingDate>`, the field whose value carries the cut-off decision in the European forward-pricing model.
- `<Units>` on `<Flow>` is always positive, by explicit schema convention. Direction comes from `<TransactionType>`. `<TotalValue>` is the one mandatory money amount and uses `FundAmountType`, so it can carry several `<Amount>` children at once — typically one in the fund's base currency and one in the share-class currency for hedged or non-base-currency classes.
- Switches are not a first-class schema construct. The schema has no `Switch` value in `<TransactionType>`; an intra-fund switch is modelled as **two linked `<Flow>` entries**, one with `RED` on the source class and one with `SUB` on the target class. The convention for linking the two is shared `<TransactionID>` prefix and matching `<TransactionSubtype>` annotations. Inter-fund switches use the same pattern across two different `<Fund>` elements.
- `DistributionType` (in `ShareClass/Distributions`) carries seven mandatory children: `<ActionCode>`, `<DividendStatus>` (`ESTIMATED`/`OFFICIAL`), `<ExDate>`, `<PaymentDate>`, `<PaymentCurrency>`, `<GrossDividendAmount>`, `<NetDividendAmount>`. The two amount blocks each contain an optional `<Total>` and a mandatory `<PerShare>`. The schema element is `<AnnouncementDate>`, not the legacy `DeclarationDate`. There is no `DistributionSubType` enumeration.
- `EarningType` (in `Portfolio/Earnings`) carries five mandatory children: `<EarningID>`, `<EarningKind>`, `<EntryDate>`, `<EntryCurrency>`, `<EntryValue>`. `<EarningKind>` is a six-value enumeration: `Coupon`, `Dividend`, `Fund distribution`, `Interest deposit/giro`, `Interest swap`, `Other`. Each of the first three has a typed sub-block (`<Coupon>`, `<Dividend>`, `<FundDistribution>`) carrying the kind-specific breakdown including withholding-tax fields.
- The `<AssetUniqueID>` field on an `<Earning>` is an `xs:IDREF` pointing at the matching `<Asset>` in `<AssetMasterData>` — the same parser-enforced linkage mechanism as `<Position>/<UniqueID>` from Chapter 6.
- The forward-pricing concepts (cut-off times, swing pricing, entry/exit loads, in-kind creation, exchange execution) are real and operationally important, but the FundsXML 4.2.8 core schema does not model them on `<Flow>`. Producers that need to carry them use `<CustomAttributes>` on the share class or the EMT regulatory templates of Chapter 8.
- The Europa Growth Fund's March 2026 transaction block consists of three `<Flows>` containers (six entries on R-EUR-ACC, three on R-CHF-ACC-HEDGED, four on I-EUR-DIST — sixteen Flow entries in total covering eleven trades and two switch legs) plus three `<Earning>` entries on the fund-level portfolio. There are no distributions, because the next one does not occur until mid-May.

We have now covered the three transaction containers — `ShareClass/Flows`, `ShareClass/Distributions`, and `Portfolio/Earnings` — together with the per-instrument trade container `Portfolio/Transactions` that we deferred to Chapter 12. What we have not yet covered is the fifth main area of a FundsXML delivery: `RegulatoryReportings`, where the five FinDatEx templates live. Chapter 8 opens that area and walks through EMT, EPT, EET, EFT, and TPT — the regulatory disclosures that modern European fund distribution depends on, and the place where many of the operational concepts of §7.9 actually find their FundsXML home.
