<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 4 — ControlData — The Metadata of a Delivery

*Document ID, reporting date, sender, and operation type*

---

## 4.1 Setting the Scene: Opening the Envelope

At the end of Chapter 3, the operations team at the Europa Growth Fund had a mental map of the five main areas of a FundsXML document. The most natural next question is not *"how do we describe the fund?"* — that is Chapter 5's subject — but rather *"how do we describe the delivery itself?"* Who sent it, when, on behalf of whom, for which reporting date, and — most importantly — *what kind of delivery is it?* A first-time load is not the same thing as an afternoon correction of a morning NAV; a regular monthly update is not the same thing as the retraction of a delivery that should never have gone out. FundsXML answers all of these questions in the small but disproportionately important structure that sits at the top of every document: [*ControlData*](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData).

Three reasons justify beginning Part II with the envelope rather than the fund itself. First, ControlData is the first element every consumer of a FundsXML file reads. A production pipeline that fails to understand ControlData never even gets to the fund data, let alone to the portfolios or regulatory modules. Second, ControlData is what makes a file identifiable, routable, and de-duplicable — without it, the same message arriving twice is indistinguishable from a genuine update, and a message arriving out of order is impossible to reconcile against what came before. Third, and most importantly, ControlData is where FundsXML takes its one explicit position on *time* — on how deliveries relate to one another across hours and days. That position is simple, deliberate, and not always what newcomers expect, and the six pages of §4.6 devoted to it are the conceptual core of this chapter.

By the end of this chapter, you should be able to:

- name every mandatory field of a ControlData block and explain what it identifies;
- produce a *UniqueDocumentID* that is unique across a producer's output stream for the life of the system;
- distinguish *INITIAL*, *AMEND*, and *DELETE* deliveries and choose the right one for a given operational situation;
- trace a chain of related deliveries backwards to the *INITIAL* that started it;
- recognise the half-dozen mistakes that cause the most production incidents in ControlData handling.

No prior knowledge of the FundsXML schema beyond Chapter 3 is assumed. The chapter proceeds from purpose to fields to operations: §4.2 describes what ControlData *does* in a live pipeline; §4.3 gives the field skeleton; §4.4 and §4.5 walk through the identification and addressing fields; §4.6 covers *DataOperation* and its consequences; §4.7 treats the inter-document references that bind a stream together; §4.8 assembles everything into a complete, schema-valid example for the Europa Growth Fund. A short pitfalls list and the key takeaways close the chapter.

---

## 4.2 The Role of ControlData in a Production Flow

Before we look at any field, it is worth asking what a real consumer *does* with an arriving FundsXML file in its first few milliseconds of existence. The answer turns out to be a short, ordered list, and every item on the list is answered by ControlData. Understanding the list first makes the fields that follow feel obvious rather than arbitrary.

Imagine the classic production setup at a distributor in Paris: an SFTP drop-box that receives FundsXML files from a dozen different asset managers, a dispatcher that triages every arriving file, and a family of downstream processors that each handle a particular kind of content. When a new file lands in the drop-box at 07:03 a.m. CET, the dispatcher does five things, strictly in this order:

1. **Recognise.** What kind of file is this, and which schema version does it claim to conform to? The root element and its schema reference answer both questions; `ControlData` is inspected immediately afterwards to confirm that the file is a well-structured FundsXML delivery.
2. **Authenticate at the business level.** Who sent this? The *DataSupplier* block inside ControlData is compared against an allowlist of approved senders. Transport-level authentication (TLS, SFTP keys) has already happened at this point; the dispatcher is now checking whether the *declared* sender is one it expects to receive data from.
3. **Deduplicate.** Have I seen this delivery before? The *UniqueDocumentID* is looked up in a persistent store of previously processed identifiers. If it is already there, the file is logged and silently discarded; if not, it is recorded and passed on.
4. **Sequence.** How does this delivery relate to what I already have? *DataOperation* and the *RelatedDocumentIDs* references decide whether the file is accepted as new, applied as an update, treated as a correction, or used to retract earlier content.

**Figure 4.1 — The first four things a consumer does with a FundsXML file**

```
 Recognise  →  Authenticate  →  Deduplicate  →  Sequence
 ─────────     ────────────     ───────────     ────────
 namespace     DataSupplier     DocumentID      DataOperation
 + schema ref                   lookup          + Related
                                                 Document IDs
```

Every one of these four steps runs *before* a single Fund, Portfolio, or RegulatoryReporting element has been read. That is why ControlData is small but disproportionately important: a mistake in the twenty lines of the envelope makes the two hundred thousand lines behind it undeliverable.

The rest of this chapter treats the same four steps in the same order. §4.4 fills in *Recognise* and *Deduplicate* (document identity and timestamps); §4.5 fills in *Authenticate* (sender and contact); §4.6 and §4.7 fill in *Sequence* (data operations and inter-document references). When we assemble the complete example in §4.8, the four steps above are the checklist against which the finished block can be read.

---

## 4.3 A First Look — Structure and Mandatory Fields

At its heart, a ControlData block is small. Reduced to its mandatory fields only, with generic placeholders in place of real values, it looks like this:

```xml
<ControlData>
  <UniqueDocumentID>...</UniqueDocumentID>
  <DocumentGenerated>...</DocumentGenerated>
  <ContentDate>...</ContentDate>
  <DataSupplier>...</DataSupplier>
</ControlData>
```

Four elements — that is the whole of the mandatory core. Table 4.1 summarises their purpose, together with the most commonly used optional fields.

**Table 4.1 — ControlData fields at a glance**

| Field | Required | Type | Purpose |
|---|---|---|---|
| [UniqueDocumentID](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/UniqueDocumentID) | yes | string | Identifies the delivery uniquely in the producer's output stream |
| [DocumentGenerated](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DocumentGenerated) | yes | dateTime (UTC) | Technical timestamp at which the file was created |
| [Version](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/Version) | no | enumeration | FundsXML schema version (e.g. 4.2.2) |
| [ContentDate](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/ContentDate) | yes | date | Business reporting date to which the content refers |
| [DataSupplier](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataSupplier) | yes | complex | Identifies the business sender of the delivery |
| [DataOperation](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataOperation) | no | enumeration | Classifies the delivery: INITIAL, AMEND, DELETE |
| [RelatedDocumentIDs](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/RelatedDocumentIDs) | no | complex | Links to the deliveries this one depends on or supersedes |
| [Language](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/Language) | no | ISO 639-1 code | Language of the textual content of the delivery |

Several other fields are available but optional, and will appear in the sections that follow. The most important of them are *DataOperation*, which classifies the delivery as initial, amendment, or deletion; *RelatedDocumentIDs*, which links the current delivery to the ones it depends on or supersedes; *Language*, which declares the language of the textual content; and *Contact* (inside *DataSupplier*), which records the team or alias to call if the delivery turns out to be broken. §4.5 through §4.7 treat these in turn.

One small but frequent source of confusion is worth mentioning now: the order in which the fields appear inside a real ControlData block is prescribed by the schema, and it is *not* the didactic order of this chapter. A validator will reject a file in which, for example, `ContentDate` appears before `DocumentGenerated` even if every value is correct. We treat the fields in the order that makes them easiest to understand; when we assemble the complete example in §4.8 we will rearrange them into the order the schema expects. The XSD in Appendix C is the authoritative reference for the exact sequence.

---

## 4.4 Identifying a Delivery — DocumentID, Timestamps, ContentDate

The first three mandatory fields answer the question *which delivery is this, and what does it refer to?* They look innocuous, but each of them carries a subtle design assumption that, if misunderstood, causes a surprising share of production incidents. We take them one at a time.

### 4.4.1 UniqueDocumentID — What Makes It Unique

The *UniqueDocumentID* is a string that identifies this particular FundsXML delivery. The schema places no structural constraint on the string other than that it exists; it is therefore tempting to treat the field as "some kind of identifier, the producer's choice". That reading is technically correct and operationally dangerous.

The guarantee a producer makes when it fills in *UniqueDocumentID* is stronger than XML validity. It is a *promise*, to every current and future consumer, that this exact value will never again appear on any other FundsXML delivery coming out of the producer's systems — not tomorrow, not next year, not after a system migration, not after a disaster-recovery restore from a six-month-old backup. The reason the promise matters is step 4 of §4.2: the consumer uses the *UniqueDocumentID* to recognise duplicates. If the producer reuses an identifier, even once, the consumer's deduplication logic either silently drops a real new delivery (thinking it is a duplicate) or silently accepts two different deliveries as one (corrupting its downstream data).

In practice, there are two sensible strategies.

The first, and the one we recommend as the default, is to use a random *UUID* — version 4 or the newer version 7. UUIDs are long enough that accidental collisions are astronomically unlikely, and they are trivial to generate in every programming language the fund industry uses. Version 7, which embeds a timestamp in the high bits, has the pleasant side effect that identifiers sort chronologically, which helps when browsing archives.

The second strategy is a *semantic* identifier constructed from known fields — something like `EGF-20260331-INITIAL-001`. Semantic identifiers are human-readable and sometimes useful during debugging. They are also fragile: the moment an operational situation demands that the same business day be processed twice (a restarted run, a re-export after a configuration fix), the naïve template collides with itself and the producer must invent an ad-hoc suffix. If you use a semantic scheme, build in a disambiguation suffix from the start — a sequence number, a UUID tail, or a timestamp to millisecond precision. Do not rely on "this can't happen twice".

> **Why not the filename?** A natural shortcut is to reuse the filename of the FundsXML file as its *UniqueDocumentID*. This is almost always a mistake. Filenames are renamed by transfer agents, case-folded by Windows file systems, rewritten by archive extractors, and silently truncated by legacy pipelines. The *UniqueDocumentID* is part of the document; it survives every transport. The filename is a property of the envelope around the document; it does not.

The *UniqueDocumentID* is also *not* the place to carry human-readable metadata such as the fund name, the reporting date, or the operation type. Those have their own fields. Loading them into the identifier tempts downstream consumers to parse the identifier instead of reading the proper fields — and parsing identifiers across producers is a well-known source of inter-operation bugs.

### 4.4.2 DocumentGenerated and ContentDate — Two Different Clocks

The most common mistake in ControlData handling is to confuse the two timestamps. The two fields look similar, they occupy adjacent positions in the schema, and under normal circumstances they carry values close to each other. They mean completely different things.

*DocumentGenerated* is a *technical* timestamp. It records the moment at which the FundsXML file was produced by the sending system — the point at which the serialiser finished writing bytes to disk or to a network socket. It is the clock that operations, monitoring, and audit pipelines care about. Its type is `xs:dateTime`, and it is almost always expressed in UTC with a `Z` suffix.

*ContentDate* is a *business* timestamp. It records the reporting date to which the content of the delivery refers — the day whose NAV is being reported, the day on which the portfolio was valued, the day on which the regulatory template is effective. Its type is `xs:date` (no time component), and it is interpreted in the business calendar of the subject of the delivery, not in the time zone of the producing system.

An example makes the difference concrete. The Europa Growth Fund closes its books for 31 March 2026 at its Luxembourg valuation point (13:00 CET on that same day). The fund administrator's batch job runs overnight and produces the monthly FundsXML delivery at 06:47 UTC on 1 April 2026. The file is placed on the SFTP drop the moment it is finished. The correct ControlData values are:

```xml
<ContentDate>2026-03-31</ContentDate>
<DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
```

Any other combination is wrong. Setting *ContentDate* to `2026-04-01` would claim that the content describes 1 April, which is untrue. Setting *DocumentGenerated* to `2026-03-31T…` would lie about when the file came into existence.

A word on time zones. *DocumentGenerated* should be expressed in UTC. XML Schema allows local time with an offset (`2026-04-01T08:47:13+02:00`), and the schema accepts such values, but international lieferbeziehungen are better served by the Z convention: it avoids every ambiguity and simplifies comparison across files from different producers. If your system has a strong reason to emit local time with an offset, make sure the offset is correct and constant across daylight-saving transitions, and make sure every consumer you talk to can parse it.

### 4.4.3 Practical Recipes

The following short recipes cover the four situations that account for almost every real-world ControlData creation.

- **Daily NAV, standard business day.** *ContentDate* = today's valuation date. *DocumentGenerated* = the UTC moment the batch finished. *UniqueDocumentID* = a fresh UUID.
- **Month-end delivery.** *ContentDate* = the last business day of the month (not the first of the next month, and not a calendar month-end that fell on a weekend). *DocumentGenerated* = whenever the month-end batch actually ran, which may be a day or two later. *UniqueDocumentID* = a fresh UUID.
- **Ad-hoc delivery outside the regular cycle.** *ContentDate* = the business date the content refers to, even if no regular delivery exists for that date. *DocumentGenerated* = now. *UniqueDocumentID* = a fresh UUID.
- **Backfill for a missed day.** *ContentDate* = the day that was originally missed, possibly weeks in the past. *DocumentGenerated* = the UTC moment the backfill run finished. *UniqueDocumentID* = a fresh UUID — it is *not* the identifier of the original missed delivery, because that delivery never existed. §4.6 covers how backfills interact with *DataOperation*.

---

## 4.5 Sender and Contact — DataSupplier

Once a consumer has identified *which* delivery is on the wire, its next question is *who is talking*. FundsXML answers this with a single mandatory structure: *DataSupplier*, which names the business sender and carries an optional *Contact* substructure for escalation.

### 4.5.1 DataSupplier — Who Is Sending, With What Authority

The *DataSupplier* block is a small record that describes the business entity responsible for the delivery. Its fields are *SystemCountry* (the country of the authority that defines the supplier list), *Short* (a unique code within that country), *Name* (the full legal or commercial name), *Type* (indicating the supplier's role — asset manager, fund administrator, depositary, and so on), and an optional *Contact* substructure (a telephone number, an e-mail address, or a team alias for escalation).

**Table 4.2 — DataSupplier fields**

| Field | Required | Used by the consumer for | Typical value |
|---|---|---|---|
| SystemCountry | yes | Jurisdictional context | "LU" |
| Short | yes | Allowlist matching, compact display | "EAM" |
| Name | yes | Human display, audit logs | "Europa Asset Management S.A." |
| Type | yes | Categorisation of sender role | "AssetManager" |
| Contact | no | Incident escalation (Name, Phone, Email) | email or phone alias |

The operational rule that matters more than any other is that a consumer that needs to match a sender against an allowlist should match on the *Short* code (which is unique per *SystemCountry*), not on the *Name*. Names change — a corporate rebrand, a merger, a translation of a German legal suffix into its English form — and consumers that match on the name will silently start rejecting valid deliveries after each such change. The *SystemCountry* / *Short* pair is the stable identifier within the FundsXML ecosystem.

It is worth drawing a distinction that causes friction in complex delivery setups: the supplier is not necessarily the party that technically produced the file. A typical arrangement is that an asset manager contracts a fund administrator, who in turn runs the batch that emits the FundsXML document. In this arrangement, *DataSupplier* usually names the asset manager — the *business* originator of the content — rather than the administrator, which is merely the technical producer. Consumers authenticate against the asset manager because that is the party they have a contractual relationship with. The administrator's involvement is operational, not declarative. Chapter 13 returns to this distinction when it discusses implementation-project governance; for Chapter 4, the point is simply that "sender" and "producer" can legitimately be different, and ControlData models the sender.

### 4.5.2 Contact Information

*Contact*, which appears inside *DataSupplier*, records a telephone number, an e-mail address, or a team alias that the receiver can use if the delivery is broken and someone needs to be called. The content should be an *alias*, never an individual: the person who owns the inbox may change, but the alias survives. "fundsxml-support@europa-asset-management.com" is a good contact; "john.smith@europa-asset-management.com" is not.

---

## 4.6 DataOperation — Thinking Across Deliveries

We now arrive at the conceptual core of the chapter. The previous sections treated each delivery as an isolated object: it has an identity, a date, a sender, a receiver. In reality, every FundsXML delivery is part of a *stream* — a sequence of deliveries from the same producer to the same consumer, about the same fund, over time. *DataOperation* is the single field that FundsXML devotes to describing how one delivery relates to the ones that came before it. Six pages, the longest section of the chapter, are devoted to it, because it is also the single most common source of production incidents in FundsXML handling.

### 4.6.1 Why a Single Delivery Is Never the Whole Story

A live FundsXML interface is not a one-shot exchange. A fund administrator does not send a single file and never another one; it sends a daily NAV file every business day, a monthly portfolio file on the first working day of each month, an occasional correction when a mistake is discovered, and the occasional retraction when a file was emitted in error. Over a year, the same administrator–distributor pair exchanges hundreds of files, all referring to the same handful of funds, all sharing the same *DataSupplier*, and each of which changes the consumer's state in a specific way. The consumer's job is to reconstruct, at any given moment, the authoritative current picture of each fund — the most recent NAV, the most recent portfolio, the most recent regulatory template — from the accumulated history of deliveries.

FundsXML makes a deliberate decision about who manages that accumulation: *not the schema*. There is no schema-level notion of a session, a sequence number, a delivery counter, a heartbeat, or a replay acknowledgement. The schema does not tell the producer how often to send, and it does not tell the consumer what to do if a delivery is missing. Everything it provides is one enumerated field — *DataOperation* — and a set of optional backward references — *RelatedDocumentIDs* — that §4.7 treats separately.

This minimalism is intentional. FundsXML is a document format, not a workflow protocol. It describes *what is in a delivery*, not *how deliveries are orchestrated*. Orchestration — scheduling, retry, acknowledgement, exactly-once handling — lives at the transport and application layers, and is the subject of Chapters 12 and 13. What the schema gives us is a shared vocabulary for saying, about each individual file, *what kind of delivery this is*. The six pages that follow are about using that vocabulary correctly.

### 4.6.2 The Three Operation Types

*DataOperation* is an enumerated field with exactly three values: **`INITIAL`**, **`AMEND`**, and **`DELETE`**. Each value carries a precise semantic meaning that every conforming consumer is expected to implement in the same way. Table 4.3 summarises the three at a glance; the narrative below it explains each in turn.

**Table 4.3 — DataOperation semantics at a glance**

| Operation | Requires a previous delivery? | Consumer action | Typical trigger |
|---|---|---|---|
| INITIAL | no | Replace any existing data for the same subject and ContentDate | First delivery of a new reporting period |
| AMEND | yes | Modify the previously delivered data (extend, refine, or replace) | Late-arriving data, or a mistake detected after acceptance |
| DELETE | yes | Retract the previously delivered data as if it had never existed | A delivery was emitted in error |

**INITIAL** marks the beginning of a stream, or the beginning of the data for a particular *ContentDate* within a stream. When a consumer receives an *INITIAL* delivery, its expected action is to install the data as the authoritative state for that subject and date, replacing anything it may already hold for the same combination. Repeated *INITIAL* deliveries for the same *ContentDate* are permitted and, under the standard's convention, are idempotent: receiving the same *INITIAL* twice must produce the same end state as receiving it once, provided the content is the same. The deduplication logic of §4.2 exists precisely to let consumers discard the redundant second copy efficiently.

**AMEND** is FundsXML's single-value umbrella for every non-initial, non-deleting change to an earlier delivery. It covers two operationally distinct but schematically identical cases. The first case is **extension**: a late-arriving piece of data — a share class whose NAV was delayed by a corporate event, a regulatory template that could not be finalised until the close of a different market — is shipped as an addition to what the consumer already has. The second case is **replacement**: a figure in a previously delivered file turns out to have been wrong, and the producer ships the corrected value in a new file so that the consumer can overwrite the error. Some older conventions (and some non-FundsXML data standards) distinguish these cases through separate `UPDATE` and `CORRECTION` enum values, but FundsXML 4.2.8 folds them into a single `AMEND` and leaves the semantic distinction to producer-consumer convention. Producers that need to signal which case they are sending typically do so through a text-level marker — a field in `CustomAttributes`, a tag in the delivery filename, or an out-of-band note to the consumer — rather than through the schema enumeration itself.

The consumer's expected action on receiving an *AMEND* delivery is to modify its stored state for the referenced subject and `ContentDate` according to the semantic intent that the producer has signalled. A replacement *AMEND* overwrites the earlier values; an extension *AMEND* adds to them. Either way, the `RelatedDocumentIDs` field (§4.7) should point at the previous delivery in the stream, so that the consumer can chain the changes correctly.

**DELETE** is the rarest and the most consequential of the three. It tells the consumer to treat a previously delivered document as if it had never existed. The canonical use case is a delivery that should never have been sent — a wrong fund, a wrong date, a draft that was promoted to production by mistake. The consumer's expected action is to remove the affected data from its authoritative state. Because *DELETE* leaves a hole, it is almost always followed by a corresponding *INITIAL* or *AMEND* that restores the intended state. A *DELETE* that is not followed by a replacement leaves the consumer without data, which is sometimes genuinely what is wanted (a subscription that was never real, a phantom transaction) but more often is a sign that the producer's pipeline is being used defensively when an *AMEND* would be clearer.

### 4.6.3 Idempotency and Ordering

Two properties of a consumer's handling of a FundsXML stream matter so much that they deserve to be named explicitly: *idempotency* and *order tolerance*.

A consumer is **idempotent** if processing the same delivery twice produces the same end state as processing it once. Idempotency is not an optional refinement; it is the minimum contract a consumer owes its operational environment, because networks retry, pipelines restart, and drop-boxes occasionally hand the same file to two processing workers. The technical mechanism that makes idempotency achievable is the *UniqueDocumentID* from §4.4.1: a consumer that records every *UniqueDocumentID* it has ever successfully processed, and that rejects a second encounter as a duplicate, is idempotent by construction. This is why §4.4.1 spends more words on the identifier than its two lines of XML would seem to deserve.

A consumer is **order-tolerant** if it behaves correctly when deliveries arrive in an unexpected sequence. The ideal case is that they arrive in the order they were sent; the real case is that networks reorder, queues deliver out of order, and retries of an older file can arrive after a newer one has already been processed. FundsXML does not provide a monotonic sequence number — there is no field whose sole purpose is to say "this delivery is the seventeenth from me". Instead, order is reconstructed after the fact from three signals: *ContentDate* (which business date does the content refer to?), *DocumentGenerated* (when was the file physically created?), and *RelatedDocumentIDs* (which earlier delivery does this one refer to?). A good consumer uses all three: it sorts deliveries for the same subject by *ContentDate*, breaks ties within a *ContentDate* by *DocumentGenerated*, and validates the chain of references with *RelatedDocumentIDs*.

A short scenario illustrates why this matters. Suppose the producer emits an *INITIAL* for 31 March 2026 at 07:00 UTC, and ten minutes later emits an *AMEND* (intended as a correction of an erroneous NAV) for the same date at 07:10 UTC. The two files travel over different network paths, and the *AMEND* overtakes the *INITIAL*: the consumer sees the *AMEND* at 07:11 UTC and the *INITIAL* at 07:14 UTC. What should the consumer do?

Two strategies are both acceptable, and a well-built pipeline will implement one of them explicitly. The first strategy, *buffer and reorder*, holds the *AMEND* aside until its referenced *INITIAL* has arrived, then applies them in the correct order; this gives the cleanest audit trail. The second strategy, *apply and reconcile*, applies the *AMEND* immediately, effectively installing the corrected data on an empty base, and then, when the late *INITIAL* arrives, refuses to replace the already-corrected state with the older uncorrected data; this is simpler to implement but requires that the consumer's state machine knows the difference between "no data" and "already corrected". Either way, the consumer must not blindly overwrite corrected data with older uncorrected data. The *DocumentGenerated* timestamp on each delivery is what makes either strategy possible.

### 4.6.4 Anti-Patterns

The following short list of anti-patterns accounts for the majority of FundsXML production incidents we have seen or heard of. Each item is a rule, followed by its one-line justification.

- **Do not send an AMEND before the INITIAL it refers to exists.** The consumer has no base on which to apply the change, and will either reject the file or, worse, silently install partial data.
- **Do not reuse the same UniqueDocumentID for an INITIAL and a later AMEND.** Idempotent deduplication depends on uniqueness; a collision makes the consumer drop the second file as a duplicate even though its content differs.
- **Do not send two INITIAL deliveries for the same ContentDate without a clear resolution rule.** The consumer does not know which one is authoritative. If the second *INITIAL* is meant to replace the first, make it an *AMEND*.
- **Do not use DELETE without a follow-up.** A *DELETE* leaves a hole in the consumer's state. If the intent is to correct rather than to retract, use *AMEND*. If the intent is genuinely to retract, make the retraction explicit in the consumer's audit trail, ideally by following it with an *INITIAL* that restores the intended state (which may be "no data at all for this date").
- **Do not mislabel a replacement AMEND as a silent delta.** Because FundsXML collapses extensions and replacements into a single *AMEND* enum value, the producer must communicate the intent clearly — through a filename convention, a `CustomAttributes` flag, or an out-of-band note. A consumer that cannot tell a replacement from an extension will either lose data or fail to propagate corrections.

### 4.6.5 A Small Example Series — ControlData Only

To see the four operations working together, consider four successive ControlData blocks for the same Europa Growth Fund over a four-day period. The rest of the file — *Funds*, *Portfolios*, *AssetMasterData* — is elided, because the payload is the subject of later chapters. Only the envelope is shown.

Day 1, the first delivery of the month-end:

```xml
<ControlData>
  <UniqueDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b001</UniqueDocumentID>
  <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
  <ContentDate>2026-03-31</ContentDate>
  <DataSupplier>...</DataSupplier>
  <DataOperation>INITIAL</DataOperation>
  <Language>en</Language>
</ControlData>
```

Day 2, a late-arriving piece of data extends the previous delivery without replacing it:

```xml
<ControlData>
  <UniqueDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b002</UniqueDocumentID>
  <DocumentGenerated>2026-04-02T09:12:04Z</DocumentGenerated>
  <ContentDate>2026-03-31</ContentDate>
  <DataSupplier>...</DataSupplier>
  <DataOperation>AMEND</DataOperation>
  <RelatedDocumentIDs>
    <RelatedDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b001</RelatedDocumentID>
  </RelatedDocumentIDs>
  <Language>en</Language>
</ControlData>
```

Day 3, an NAV that was reported incorrectly on Day 1 is corrected:

```xml
<ControlData>
  <UniqueDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b003</UniqueDocumentID>
  <DocumentGenerated>2026-04-03T14:28:50Z</DocumentGenerated>
  <ContentDate>2026-03-31</ContentDate>
  <DataSupplier>...</DataSupplier>
  <DataOperation>AMEND</DataOperation>
  <RelatedDocumentIDs>
    <RelatedDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b002</RelatedDocumentID>
  </RelatedDocumentIDs>
  <Language>en</Language>
</ControlData>
```

Day 4, the producer discovers that the entire Day 1 delivery was emitted for the wrong fund and retracts it:

```xml
<ControlData>
  <UniqueDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b004</UniqueDocumentID>
  <DocumentGenerated>2026-04-04T08:03:22Z</DocumentGenerated>
  <ContentDate>2026-03-31</ContentDate>
  <DataSupplier>...</DataSupplier>
  <DataOperation>DELETE</DataOperation>
  <RelatedDocumentIDs>
    <RelatedDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b003</RelatedDocumentID>
  </RelatedDocumentIDs>
  <Language>en</Language>
</ControlData>
```

Several observations deserve to be made about this small series. First, every delivery has a *new* *UniqueDocumentID* — never a reused one, even though the subject and the *ContentDate* are the same throughout. Second, every non-*INITIAL* delivery populates *RelatedDocumentIDs* to point at the immediately preceding delivery in the stream, not at the *INITIAL* from Day 1. This is the linear-chain convention that §4.7 recommends: it makes the full history reconstructable by walking the chain backwards, and it avoids the question of what a *RelatedDocumentID* should mean when it points at a delivery that has itself been superseded. Third, the *DataSupplier* block is identical across all four deliveries, because the business sender has not changed — only the operational relationship between the deliveries has.

Finally, a meta-observation: most of the complexity in the *DataOperation* model lives on the consumer side, not on the producer side. A disciplined producer can set *DataOperation* correctly from a short rule set — "new data for a new date is *INITIAL*, any change to existing data is *AMEND*, retraction is *DELETE*" — and signal the fine distinction between an extension-*AMEND* and a replacement-*AMEND* through filename conventions or producer-consumer-specific metadata. A consumer, by contrast, must cope with every legal sequence the producer universe can throw at it, including ones the original producers did not anticipate. When in doubt, err on the side of the consumer: design *DataOperation* usage to make the consumer's life predictable, not the producer's life convenient.

---

## 4.7 Versioning and Related Documents

Where §4.6 treated the *kind* of a delivery, this section treats the *links* between deliveries. Two topics belong here: the *RelatedDocumentIDs* element, which binds non-*INITIAL* deliveries to the ones they depend on, and the schema version indicated by the root namespace, which binds every delivery to a specific release of the FundsXML standard.

### 4.7.1 RelatedDocumentIDs — The Backward Pointer

*RelatedDocumentIDs* is an optional structure that, when present, lists one or more *UniqueDocumentID* values referring to earlier deliveries. It appears in the *AMEND* and *DELETE* cases shown in §4.6.5 and is conventionally absent from *INITIAL* deliveries, which by definition do not refer to anything earlier. The schema even makes `RelatedDocumentIDs` mandatory on a *DELETE* operation — a *DELETE* that does not explicitly name the delivery being retracted is not a legal FundsXML file.

Three properties of *RelatedDocumentIDs* are worth naming explicitly. First, the pointer is *backward*: an amendment points at the delivery it changes, not the other way round. There is no forward "this-delivery-has-been-superseded-by" pointer in the schema. A consumer that wants to know "is this delivery still authoritative?" must either remember the answer as it processes each new arrival or walk the chain backward from the newest delivery. Second, the pointer is *informative*, not enforced at the schema level: the XSD does not check that the referenced *UniqueDocumentID* actually exists, that it belongs to the same subject, or that the referencing operation makes semantic sense against what was referenced. All of that is a business-rule concern, and Chapter 10 treats it in its discussion of two-stage validation. Third, the element is *potentially transitive*: a second *AMEND* can refer to the first *AMEND*, forming a chain, or it can refer directly back to the original *INITIAL*, skipping the intermediate step. Both conventions are seen in the wild, and neither is forbidden by the schema.

Because both conventions are possible, producers and consumers must agree on one. The convention we recommend — and that Chapter 13 will formalise as a project-level decision — is the *linear chain*: every non-*INITIAL* delivery refers to the immediately preceding delivery in the stream, regardless of operation type. The result is a singly-linked list stretching from the newest delivery back to the *INITIAL*; walking the list backwards always reconstructs the full history, and every intermediate step is explicitly represented. The alternative convention — always pointing at the *INITIAL* — is simpler to construct but hides intermediate steps and makes it harder to tell whether a replacement *AMEND* was applied before or after an extension *AMEND*. Pick one, document it, and stick to it.

One final note: *RelatedDocumentIDs* is plural because there are cases in which one delivery legitimately depends on more than one predecessor. The most common is a consolidated correction that replaces two or more earlier deliveries at once. These cases are rare enough that most implementations can treat the element as effectively singular, but the plural form is there when it is needed.

### 4.7.2 Schema Version Handling

A point of practical importance that often surprises first-time FundsXML implementers: the schema file does **not** declare a `targetNamespace`. This means instance documents live in the unnamed namespace, and the root element is written without a default namespace declaration. Instead, the root element carries an `xsi:noNamespaceSchemaLocation` attribute that points directly to the schema file for the version the producer is building against:

```xml
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:noNamespaceSchemaLocation="https://github.com/fundsxml/schema/releases/download/4.2.2/FundsXML.xsd">
```

Every released version of the schema is published as a GitHub release under the `fundsxml/schema` repository. The URL follows a predictable pattern — `https://github.com/fundsxml/schema/releases/download/{version}/FundsXML.xsd` — where `{version}` is the release tag (e.g. `4.2.2`). This gives every instance document a stable, publicly resolvable reference to the exact schema it was validated against, and it gives any consumer or validator a direct download path to that schema without needing a local copy.

**Upgrading to a newer schema version** is correspondingly straightforward: the producer updates the version number in the URL. Moving from 4.2.2 to 4.2.5, for example, requires nothing more than changing the root element to:

```xml
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:noNamespaceSchemaLocation="https://github.com/fundsxml/schema/releases/download/4.2.5/FundsXML.xsd">
```

All versions of FundsXML since 4.0.0 are designed to be backward compatible, so within the 4.x line such an upgrade is a smooth transition: a consumer built against 4.2.2 will usually accept files produced against 4.2.5, and vice versa. The backwards-compatibility discipline described in §3.3.2 ensures that *patch* releases add clarifications and non-breaking adjustments, while *minor* releases add new elements or modules but preserve compatibility for everything that was already present.

In addition to the schema reference in the root element, the schema version is also communicated *inside* the document, in `ControlData/Version`. A consumer can inspect this value before running schema validation to confirm which version the producer intended. Recording the version in the audit log alongside the delivery is a discipline worth following: mismatches between producer and consumer schema versions are a recurring source of "it worked yesterday, what changed?" incidents, and the audit log is often the only way to reconstruct what happened.

---

## 4.8 A Complete ControlData Block for the Europa Growth Fund

We are now ready to assemble the first complete, schema-valid example of the book. The block below is the actual *ControlData* envelope of the Europa Growth Fund's month-end delivery for 31 March 2026 — the same delivery from which every later chapter of Part II will show a fragment. Field order follows the sequence the schema requires, not the didactic order of this chapter.

```xml
<ControlData>
  <UniqueDocumentID>8a1c0e76-1b7d-4f55-9d2e-11f4a0c8b001</UniqueDocumentID>
  <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
  <ContentDate>2026-03-31</ContentDate>
  <DataSupplier>
    <SystemCountry>LU</SystemCountry>
    <Short>EAM</Short>
    <Name>Europa Asset Management S.A.</Name>
    <Type>AssetManager</Type>
    <Contact>
      <Email>fundsxml-support@europa-asset-management.com</Email>
    </Contact>
  </DataSupplier>
  <DataOperation>INITIAL</DataOperation>
  <Language>en</Language>
</ControlData>
```

Reading the block field by field, every design choice from the previous sections becomes visible. The *UniqueDocumentID* is a UUID, unique across the producer's output stream for the life of the system (§4.4.1). The *DocumentGenerated* timestamp is expressed in UTC and records the moment the batch job finished writing the file; the *ContentDate* is a plain date and refers to the business reporting day, which is the last business day of March 2026 (§4.4.2). The *DataSupplier* block names the fund's asset manager rather than the fund administrator that technically produced the file, using the *SystemCountry* / *Short* pair ("LU" / "EAM") as the stable identifier that a consumer's allowlist will match against (§4.5.1). The *DataOperation* is *INITIAL*, because this is the first month-end delivery for 31 March 2026; the next delivery in the same stream, whatever it turns out to be, will populate *RelatedDocumentIDs* to point back at this file's *UniqueDocumentID* (§4.6, §4.7). The *Language* is English, which indicates the language of the textual content inside the file — the fund's *marketing* names and descriptions may still appear in several languages, and Chapter 5 treats that case explicitly.

This block is short — and yet every one of the four steps from §4.2 is now answerable from it alone. A consumer that reads these lines and stops has enough information to decide whether to continue parsing the rest of the file, and in production that is exactly what the first stage of a real pipeline does. The complete end-to-end example of the Europa Growth Fund's month-end delivery — this *ControlData* block plus the *Funds*, *AssetMasterData*, *Documents*, and *RegulatoryReportings* sections — is printed in Appendix D, and each of the remaining chapters of Part II will take one piece of it for detailed treatment.

---

## 4.9 Common Pitfalls

The following short list captures the half-dozen mistakes that, in our experience, account for the majority of ControlData-related production incidents. Each entry gives the symptom, the underlying cause, and the fix.

- **A new delivery is silently dropped as a duplicate.** *UniqueDocumentID* has been reused, usually because it was generated from a non-unique source such as the filename or a timestamp at second precision. Switch to UUIDs.
- **Reports appear for the wrong day.** *ContentDate* has been set to the day the file was produced rather than to the business reporting date. Re-read §4.4.2 and fix the producer's timestamp derivation logic.
- **The consumer rejects a known sender as unknown.** The allowlist is matching on *Name* rather than on the *SystemCountry* / *Short* pair, and the sender's legal name has just changed (merger, rebrand, translation). Switch the match to the stable code pair.
- **An AMEND is rejected because the consumer sees no base state.** The *AMEND* was sent before its *INITIAL* was successfully processed, or the *RelatedDocumentIDs* pointer is missing or refers to a non-existent document. Re-issue the *INITIAL* first, or fix the pointer.
- **A correction reaches investors without triggering recalculation.** A replacement *AMEND* was emitted without the producer-consumer convention that distinguishes replacement from extension. The consumer's audit hooks assumed the *AMEND* was an additive extension rather than a correction and silently installed the new figures without re-issuing affected downstream documents. Agree on a replacement/extension signal between producer and consumer before going live.
- **A retracted delivery leaves a hole in the consumer's state.** A *DELETE* was sent without a follow-up *INITIAL* restoring the intended state. Either send the restoring *INITIAL*, or confirm explicitly that an empty state is intended and document the gap.

---

## 4.10 Key Takeaways

- ControlData is the envelope of every FundsXML delivery. It identifies, authenticates, deduplicates, and sequences the file — and all of this happens before any of the fund data behind it is read.
- Four mandatory fields form the core: *UniqueDocumentID*, *DocumentGenerated*, *ContentDate*, and *DataSupplier*. The optional *DataOperation*, *RelatedDocumentIDs*, and *Language* fields are essential in any production setup.
- *DocumentGenerated* (technical timestamp) and *ContentDate* (business reporting date) are two different clocks and must never be confused.
- *DataSupplier* is matched by its *SystemCountry* / *Short* pair, not by *Name*; an allowlist that matches on the name will silently break on every rebrand or translation.
- *DataOperation* — *INITIAL*, *AMEND*, *DELETE* — is the only bridge FundsXML provides between successive deliveries. The schema collapses both extensions and replacements into a single *AMEND* value; the producer-consumer relationship must carry the finer distinction through convention. Idempotency and order tolerance on the consumer side are what make the bridge usable in practice.
- *RelatedDocumentIDs* carries backward pointers; the recommended convention is a linear chain, in which every non-*INITIAL* delivery refers to the immediately preceding delivery in the same stream.
- The complete ControlData block in §4.8 is the first schema-valid FundsXML fragment of Part II, and the same values reappear in every subsequent example through to the end of the book.

With the envelope in place, we can now open it and look inside. Chapter 5 turns to the subject of every FundsXML message — the fund itself — and to the static and dynamic data that describe it.
