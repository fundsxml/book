<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 9 — Advanced Schema Areas

*Factsheets, digital signatures, and CustomDataFields*

---

## 9.1 Setting the Scene: The Rest of the Schema

At the end of Chapter 8 we had covered all five main areas of a FundsXML delivery — `ControlData`, `Funds`, `AssetMasterData`, the four substructures of `FundDynamicData`, and `RegulatoryReportings`. Those five areas carry the overwhelming majority of what every production FundsXML document transports, and they are the subject of every chapter of Part II up to this point. What remains are four quieter but operationally important schema areas: the [`Documents`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Documents) section for factsheets, KIDs, and other attachments; `ds:Signature`, the XML digital-signature element the schema imports from the W3C XMLDSig specification; the [`CustomAttributes`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData/CustomAttributes) extension mechanism; and the [`CountrySpecificData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/CountrySpecificData) branches that carry national regulatory extensions. This chapter treats all four, and it does so against the real schema.

A disclosure about this chapter's code listings is worth making up front, because it changes the rule that Chapters 4 through 8 followed. Every XML example in Chapters 4 to 8 was written for pedagogical clarity — element names, field orderings, and occasional attribute values were shaped around the narrative rather than against the current FundsXML 4.2.8 XSD. The corrections applied retroactively to those chapters fix the most egregious deviations (the `DataOperation` enumeration, the `CustomAttributes` name, the namespace declaration, and a few other structural issues), but the deeper element-by-element alignment with the production schema was not attempted. Chapter 9 changes that rule: **every XML listing in this chapter has been validated against `FundsXML4.xsd` using `xmllint`**, and the validation command is the same for every example:

```
xmllint --noout --schema FundsXML4.xsd <example>.xml
```

Readers who want to reproduce the validation can copy any listing into a file, run the command, and expect to see `<example>.xml validates` on standard output. The listings carry the full document root, including the namespace-less `FundsXML4` element with `xsi:noNamespaceSchemaLocation`, so that each one is a self-contained, schema-valid file rather than a fragment.

By the end of this chapter, you should be able to:

- populate the `Documents` section with factsheets, PRIIPs KIDs, and annual reports, choosing correctly between the `DocumentURL` and `BinaryData` content modes;
- add an enveloped XML digital signature (XMLDSig) to a FundsXML delivery and explain its relationship to the separate `Signature` flag on a `Document` entry;
- use `CustomAttributes` to carry proprietary extension data without breaking the schema, and recognise when a `CustomAttributes` entry is the right tool and when a schema change request is the right tool;
- populate the country-specific branches in both `ControlData` and at the root of the document for Austria, Luxembourg, and the other supported jurisdictions;
- read a FundsXML document whose root element contains all four advanced areas and explain which consumers read which parts.

The chapter proceeds from the biggest of the four topics to the smallest: Documents in §9.2, XML digital signatures in §9.3, `CustomAttributes` in §9.4, country-specific additions in §9.5. A short integrative section (§9.6) shows how the four advanced areas fit alongside the five main areas of Chapters 4 to 8, and the chapter closes with the usual pitfalls and takeaways.

---

## 9.2 The Documents Section — Factsheets, KIDs, Signed Attachments

The `Documents` element is a root-level sibling of `Funds` and `AssetMasterData` in a FundsXML document. It carries references to — or, in some deployments, the actual binary content of — fund-related documents that travel alongside the structured data: factsheets, prospectuses, key information documents, annual reports, audit reports, and anything else the asset manager wants to deliver as a formal document rather than as structured data. Chapter 3 introduced the `Documents` section as one of the five main areas of a FundsXML delivery; this section treats it in detail.

### 9.2.1 Why a Documents Section Exists at All

The first question a reader might reasonably ask is why FundsXML, which is already a structured-data format, bothers with a mechanism for carrying *documents* at all. The answer is that structured data and documents are not substitutes for each other. A PRIIPs KID is a regulatory artefact that has to be delivered to investors *as a formal document* — typically a PDF — regardless of whether the underlying data can also be delivered in structured form. The regulator does not accept the EPT (Chapter 8) as a replacement for the KID; the EPT is an input to the KID-generation process, but the KID itself is a PDF that must be delivered separately and that every retail investor has the right to see before they buy.

The same argument applies to prospectuses, annual reports, audit reports, and AIFMD filings. All of these are documents with formal legal status, and the FundsXML `Documents` section exists so that a single delivery can carry both the structured data *and* the formal documents that reference that data, without forcing the producer and the consumer to maintain two parallel delivery channels.

### 9.2.2 The Structure of a Document Entry

A `Documents` element contains one or more `Document` children. Each `Document` carries a set of fields that describe the document's type, language, applicability, and technical format, plus one of two alternative content representations — a URL pointing at the actual file, or the file's contents embedded directly inside the XML as base64-encoded binary data.

The main fields are:

- **`Type`** — a choice between a **`ListedType`** (an enumeration with the values *AIFMD*, *AnnualReport*, *AuditReport*, *Factsheet*, *KID*, *Prospectus*, and *PRIIPS-KID*) and an **`UnlistedType`** (a free-text string for document kinds not covered by the enumeration). Every `Document` must pick exactly one of the two.
- **`Version`** — an optional version string, typically a date (`2026-03-31`) or a release identifier (`2025`).
- **`Language`** — an `xs:language` code identifying the language of the document's content.
- **`TranslationsAvailable`** — a Boolean flag indicating whether the same document is available in other languages.
- **`PublicationCountries`** — a list of ISO country codes naming the countries for which the document is valid.
- **`Fund`**, **`Subfunds`**, **`ShareClasses`** — optional backward pointers to the fund, sub-funds, or share classes the document applies to. A PRIIPs KID is per-share-class and therefore references a specific `ShareClass`; an annual report is typically fund-level and references the `Fund`.
- **`Name`** — a human-readable name for the document.
- **`FileName`** — the name of the file (including extension), useful when a consumer needs to save the document to disk.
- **`ForPublicUsage`** — a Boolean indicating whether the document may be redistributed to the public.
- **`Format`** — the technical format: *PDF*, *XML*, *Excel*, *Word*, *Image*, and so on.
- **`Signature`** — an enumeration (*No*, *Digital*, *Scan*) indicating whether the document is signed, and if so by what method. This is a *flag*, not a signature itself; the cryptographic signature, if any, is carried separately (see §9.3).
- **`CreationDate`**, **`ModificationDate`**, **`ExpirationDate`** — the timestamps that govern the document's lifecycle.
- **`DataSupplier`** — the party that produced the document.
- **`SizeInBytes`** — the document's size (useful for consumers that need to budget download quotas).
- **`DocumentURL`** or **`BinaryData`** — the actual content.

### 9.2.3 URL versus Embedded Content

The choice between `DocumentURL` and `BinaryData` is the one operational decision a producer makes for every document. Both are legitimate in FundsXML, and each has clear advantages.

**`DocumentURL`** contains an HTTPS (or occasionally SFTP) URL pointing at a location where the consumer can download the document on demand. The advantages are: the FundsXML file itself stays small, regardless of how many multi-megabyte PDFs the delivery references; the document can be updated after the FundsXML file has been shipped, as long as the URL still resolves; and the producer retains control over who can access the document by managing the HTTPS endpoint's authentication. The disadvantage is that the FundsXML file and the documents it references are *not* self-contained — a consumer that archives the FundsXML file but fails to download the referenced documents at the same time may find later that the URLs have expired or been moved.

**`BinaryData`** embeds the document's bytes directly into the FundsXML file as base64-encoded content. The advantages are: perfect self-containedness (the consumer gets everything in one file); no dependency on any external HTTPS infrastructure; and the possibility of cryptographically binding the document to the FundsXML envelope through the enveloped signature mechanism of §9.3. The disadvantages are the file-size explosion (a 2-megabyte PDF becomes a 2.7-megabyte base64 blob inside the XML) and the rigidity (once embedded, the document cannot be updated without re-issuing the whole FundsXML delivery).

The Europa Growth Fund's production convention, which Chapter 13 will formalise as a project decision, is **`DocumentURL` for the fund's routine monthly deliveries** (where bandwidth matters and the documents rarely change between deliveries) and **`BinaryData` for the quarterly or annual ESAP submissions** (where self-containedness is a regulator requirement). The example in §9.2.4 shows `DocumentURL` because that is the more common case.

### 9.2.4 A Validated Example: Two Documents for the Europa Growth Fund

The complete FundsXML document below carries two entries in its `Documents` section: the PRIIPs KID for the R-EUR-ACC share class, and the fund's annual report for the 2025 financial year. Both entries use `DocumentURL` for the content. The full document validates against the current FundsXML 4.2.8 schema with `xmllint --noout --schema FundsXML4.xsd`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-DOC-001</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
    </DataSupplier>
    <DataOperation>INITIAL</DataOperation>
    <Language>en</Language>
  </ControlData>
  <Documents>
    <Document>
      <Type>
        <ListedType>PRIIPS-KID</ListedType>
      </Type>
      <Version>2026-03-31</Version>
      <Language>en</Language>
      <TranslationsAvailable>true</TranslationsAvailable>
      <PublicationCountries>
        <Country>LU</Country>
        <Country>DE</Country>
        <Country>FR</Country>
      </PublicationCountries>
      <ShareClasses>
        <ShareClass>
          <Identifiers>
            <ISIN>LU2100000011</ISIN>
          </Identifiers>
          <Name>Europa Growth Fund R EUR ACC</Name>
          <Currency>EUR</Currency>
        </ShareClass>
      </ShareClasses>
      <Name>Europa Growth Fund R EUR ACC — PRIIPs KID (English)</Name>
      <FileName>EGF_R_EUR_ACC_KID_en_20260331.pdf</FileName>
      <ForPublicUsage>true</ForPublicUsage>
      <Format>PDF</Format>
      <Signature>Digital</Signature>
      <CreationDate>2026-03-31</CreationDate>
      <ExpirationDate>2027-03-31</ExpirationDate>
      <DataSupplier>
        <SystemCountry>LU</SystemCountry>
        <Short>EAM</Short>
        <Name>Europa Asset Management S.A.</Name>
        <Type>IC</Type>
      </DataSupplier>
      <DocumentURL>https://docs.europa-asset-management.com/kids/LU2100000011_en_20260331.pdf</DocumentURL>
    </Document>
    <Document>
      <Type>
        <ListedType>AnnualReport</ListedType>
      </Type>
      <Version>2025</Version>
      <Language>en</Language>
      <Fund>
        <Identifiers>
          <LEI>549300ABCDEFGHIJ1234</LEI>
        </Identifiers>
        <Name>Europa Growth Fund</Name>
        <Currency>EUR</Currency>
      </Fund>
      <Name>Europa Growth Fund — Annual Report 2025</Name>
      <FileName>EGF_AnnualReport_2025.pdf</FileName>
      <ForPublicUsage>true</ForPublicUsage>
      <Format>PDF</Format>
      <Signature>Digital</Signature>
      <CreationDate>2026-03-15</CreationDate>
      <DocumentURL>https://docs.europa-asset-management.com/annual/EGF_2025.pdf</DocumentURL>
    </Document>
  </Documents>
</FundsXML4>
```

Reading the block in two passes.

The **first pass** looks at the PRIIPs KID entry. Its type is identified by the `ListedType` enumeration value `PRIIPS-KID`, one of the seven values the schema accepts. The version `2026-03-31` tags this as the version of the KID that was valid as of the quarter-end delivery date. The language is English; `TranslationsAvailable=true` tells a consumer that this KID exists in other languages too and can be requested separately. The KID applies to three distribution countries (Luxembourg, Germany, France — the countries where the R-EUR-ACC class is distributed to retail investors at the time of the delivery). The backward pointer to the share class uses the `ISIN` of R-EUR-ACC, matching the value introduced in Chapter 5. The file is a PDF, it is signed digitally, it was created at the valuation date, and it expires one year later — the PRIIPs regulatory cycle. The data supplier block is repeated inside the `Document` element, letting a consumer identify the producer of the document independently of the enclosing file's producer (in this case they are the same, but they need not be). Finally, `DocumentURL` gives the HTTPS location where the document can be retrieved on demand.

The **second pass** looks at the annual report entry. Its type is `AnnualReport`, another of the seven `ListedType` values. It is associated with the *fund as a whole* rather than with an individual share class, so the backward pointer uses the fund's `Fund/Identifiers/LEI` rather than a share-class ISIN. The `Language` is English, but no `PublicationCountries` list is given because an annual report is a fund-level document that is not restricted to particular distribution countries. No `ExpirationDate` is set because an annual report does not expire in the regulatory sense; it stays valid until superseded by the next year's report.

Both entries have `Signature=Digital`, indicating that the underlying PDFs are digitally signed. The actual cryptographic signatures, however, are on the PDFs themselves, not inside the FundsXML file. The next section treats the separate case of signing the entire FundsXML document.

---

## 9.3 XML Digital Signatures

The root element of a FundsXML document, after the five main content areas we have already covered and the optional `CountrySpecificData` branch that §9.5 treats, allows an optional `ds:Signature` element as its final child. This is the XML digital-signature element defined by the W3C XMLDSig specification, imported into the FundsXML schema through the `xmldsig-core-schema.xsd` file that sits alongside `FundsXML4.xsd`. When present, it signs the containing FundsXML document cryptographically, so that any downstream consumer can verify — with the usual public-key-infrastructure machinery — that the document was produced by the claimed signer and has not been tampered with since signing.

### 9.3.1 Why Sign FundsXML

The case for signing FundsXML documents rests on three distinct needs.

**Integrity** is the most obvious. A FundsXML file that passes through multiple hands between its producer and its final consumer — a fund administrator, a transfer mechanism, a distributor's staging system, a downstream analytics pipeline — can be subject to deliberate or accidental modification at any of those stages. A cryptographic signature binds the document's content to its producer's identity in a way that a verifier can check independently: if any byte of the signed content has changed since the signature was created, verification fails. Integrity matters particularly for regulatory submissions and for data that may later be used as evidence in a dispute.

**Non-repudiation** is the second case. In some bilateral relationships — particularly where fund data is used as the basis for financial settlement or regulatory filing — the consumer needs to be able to prove that a particular document came from a particular producer, *and* that the producer cannot later deny having sent it. A valid digital signature gives exactly this property: the signer, having used their private key to sign the document, cannot credibly claim that somebody else signed it in their name (provided the private key was properly protected, which is a key-management concern rather than a schema concern).

**Authentication**, the third case, overlaps with the first two but is worth naming separately. A consumer that receives a signed FundsXML document can determine the signer's identity from the certificate embedded in the signature — typically an `X509Certificate` or `X509SubjectName` field inside the `KeyInfo` block — and match that identity against an allowlist of approved producers. This is a stronger form of the sender-matching we discussed in Chapter 4 (where the allowlist matched on the `DataSupplier/LEI` text in the `ControlData` block); a signature-based allowlist cannot be forged simply by writing the right LEI into the XML, because the private key needed to produce a valid signature is held only by the real producer.

### 9.3.2 Enveloped, Enveloping, and Detached Signatures

XMLDSig defines three signature forms, and the choice between them matters for where the signature lives and what it signs.

In an **enveloped** signature, the `ds:Signature` element sits *inside* the document being signed, typically as its last child. The signature covers the enclosing document minus the signature element itself (the `enveloped-signature` transform excludes the signature from the content it signs, to avoid a circular dependency). This is the form FundsXML uses natively, because the FundsXML schema explicitly allows `ds:Signature` as the last optional child of the root `FundsXML4` element.

In an **enveloping** signature, the reverse applies: the signed content sits inside a `ds:Object` element *within* the signature. The top-level element is the signature itself. This form is useful when a signature needs to bundle arbitrary content together with its own metadata, but it does not fit FundsXML's document-centric design.

In a **detached** signature, the signature and the content are separate documents. The `ds:Reference` element inside `ds:SignedInfo` uses a URI to point at the content. Detached signatures are useful when the signing party cannot or does not want to modify the signed document at all — for example, when signing a PDF that has already been published and must remain bit-for-bit identical. FundsXML does not typically use detached signatures at the envelope level, but the individual `Document` entries in the `Documents` section frequently reference PDFs whose own signatures are detached (the `Signature=Digital` flag we saw in §9.2 indicates this case).

For the rest of this section we treat the enveloped form, which is the one natively supported by FundsXML at the root.

### 9.3.3 Canonicalization and Digest Algorithms

Cryptographic signatures operate on bytes, not on XML. When a consumer verifies a signature, it computes a hash of the signed content and compares it with the digest value in the signature. But XML has many equivalent byte-level representations of the same logical content — different whitespace, different attribute orderings, different namespace prefixes, different quote characters — and a naive hash would fail verification whenever the document passed through an intermediate parser that re-serialised it in a different form.

The XMLDSig standard solves this problem through **canonicalisation**: a well-defined procedure that converts any XML into a unique canonical byte form, such that two logically equivalent XML documents always produce the same bytes. The canonical form is the thing that actually gets hashed.

The FundsXML examples in this section use **Canonical XML 1.0** (`http://www.w3.org/TR/2001/REC-xml-c14n-20010315`) as the canonicalisation algorithm and **SHA-256** (`http://www.w3.org/2001/04/xmlenc#sha256`) as the digest algorithm. The signature itself uses **RSA-SHA256** (`http://www.w3.org/2001/04/xmldsig-more#rsa-sha256`). These are the current best-practice defaults in 2026; older FundsXML deliveries may use SHA-1 and RSA-SHA1, which are now deprecated but still legal under the schema.

### 9.3.4 A Validated Example: A Signed FundsXML Document

The listing below is a FundsXML document with a minimal `ControlData` block and an enveloped `ds:Signature` at the root. The signature structure is complete and schema-valid: it has a `SignedInfo` with canonicalisation, signature, and digest methods, a single `Reference` to the document root (`URI=""` means the whole document), the transforms that strip the signature itself from the signed content, and a `SignatureValue` block. The `SignatureValue` in this example is a placeholder — a real signature value is produced by running an actual signing key over the canonicalised content, not by hand-writing a base64 string. Consumers that validate signatures *cryptographically* (as opposed to just *schematically*) will reject the placeholder; consumers that only care about schema validation (as we do in this chapter) will accept it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-SIG-001</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
    </DataSupplier>
    <DataOperation>INITIAL</DataOperation>
    <Language>en</Language>
  </ControlData>
  <ds:Signature Id="EGF-DocumentSignature">
    <ds:SignedInfo>
      <ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <ds:Reference URI="">
        <ds:Transforms>
          <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
          <ds:Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        </ds:Transforms>
        <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <ds:DigestValue>9Fxs0VvC6QyzGx2rSc0oYQ3fwBp9tEjU5aKQUAJJSWM=</ds:DigestValue>
      </ds:Reference>
    </ds:SignedInfo>
    <ds:SignatureValue>
      Krl3V4o9E8mQy5q3FqJdqXmOr4qYvHhj3HwNpfqX7l+yXYQeJqmJ4t6VvZa0MwvFH+
      uk1OJmI7mYn3Wx2PcNpRaVFqEGxCDzYbLdmCqN6mTgVrJLmhd3QoJzTkYvNbXeZBqF
      LJK6y9V3ZX2mPvnRJU6C8XhQwdmFjW4Vx9M5P1XyJcHL3FtV1pnKZBXsh8fQKL2rL4
      PcZMnL5x3WfHpOYh2mN+tvQJkRBk1xC3D6oCqmYwHbKvO9pF8yA7jKL3vYQ5nNq3Yx
      fR2zHLnVqKbPjWcMpI3y0nM2oNpE4L3+kMwZg7HVQKrDzLJ0YJ9tPrX5wVpJ7hKy8Q
      ==
    </ds:SignatureValue>
    <ds:KeyInfo>
      <ds:X509Data>
        <ds:X509SubjectName>CN=Europa Asset Management S.A., O=Europa Asset Management, C=LU</ds:X509SubjectName>
      </ds:X509Data>
    </ds:KeyInfo>
  </ds:Signature>
</FundsXML4>
```

Reading the signature block in three passes.

The **first pass** looks at `SignedInfo`. It carries three critical algorithm declarations: the canonicalisation method (Canonical XML 1.0), the signature method (RSA with SHA-256), and the reference to the signed content. The reference URI is the empty string, which in XMLDSig convention means "the document containing this signature". The two transforms strip the signature itself from the content (so that the signature does not sign itself) and then canonicalise what remains.

The **second pass** looks at the digest and the signature value. `DigestValue` contains the base64-encoded SHA-256 hash of the canonicalised, enveloped-signature-stripped FundsXML document. A verifier computes the same hash from its local copy of the document and compares. `SignatureValue` contains the RSA-SHA256 signature of the `SignedInfo` block, computed with the producer's private key. A verifier uses the public key (from the `KeyInfo` block, or from a separately distributed certificate) to decrypt the signature and compare against its own hash of `SignedInfo`.

The **third pass** looks at `KeyInfo`. It carries an `X509SubjectName` identifying the signer — Europa Asset Management S.A., with its organisation and country. A full production signature typically includes an `X509Certificate` element with the base64-encoded certificate bytes, so that the verifier can check not only the signer's identity but also the certificate chain that vouches for it; we have omitted that for brevity. Consumers that match against an allowlist of approved signers look up the `X509SubjectName` (or the full certificate's fingerprint) and accept or reject accordingly.

### 9.3.5 The Signature Flag on Document Entries versus the Root Signature

The `Document` element in §9.2 carries a `Signature` field whose value is one of *No*, *Digital*, or *Scan*. This is **not** the same thing as the `ds:Signature` element we just discussed. The `Document/Signature` field is a *flag*: it tells the consumer whether the PDF (or other format) that the document references is itself signed, and if so whether the signature is cryptographic (`Digital`) or a scan of a hand-written signature (`Scan`). The cryptographic signature, if any, lives *inside the referenced document*, not inside the FundsXML file — typically as a PKCS#7 signature embedded in the PDF's own signature dictionary.

The root-level `ds:Signature` element, by contrast, signs *the FundsXML envelope* itself — everything inside the root `FundsXML4` element except the signature sub-tree. The two signature mechanisms are orthogonal: a FundsXML document can be signed at the root, it can contain signed PDFs (flagged by `Document/Signature=Digital`), it can do both, or it can do neither. Choosing which combination to use is a project-level decision that Chapter 13 will treat in the context of a full implementation project.

---

## 9.4 CustomAttributes — The Extension Mechanism

The final bespoke feature of FundsXML that we treat in this chapter is the schema's extension mechanism: a way for producers to attach arbitrary named key-value data to many of the standard element types without breaking the schema. The mechanism is called `CustomAttributes`, not `CustomDataFields` (an older and imprecise name that appeared in marketing material and that earlier chapters of this book have now been corrected to match the XSD).

### 9.4.1 Why an Extension Mechanism Exists

No standard can enumerate every field that every member firm, in every jurisdiction, will ever need. The FundsXML designers accepted this from the start and built an extensibility mechanism into the schema, so that producers with legitimate proprietary data could carry it through the standard without either forking the XSD or losing the data.

The extension mechanism is **structured**, not free-form. A producer cannot simply paste arbitrary XML into a reserved "extensions" region; the schema requires that every extension value be named, typed, and placed into a `CustomAttributes` element whose own structure is fixed. This deliberate constraint gives consumers a fighting chance of making sense of unknown fields: even if a consumer does not recognise a particular attribute name, it can still parse the attribute's name, type, and value according to the common structure, and decide individually whether to store, log, or ignore each one.

### 9.4.2 The Structure of a CustomAttributes Element

Every `CustomAttributes` element contains one or more `Attribute` children. Each `Attribute` has:

- **`Name`** — a `Text256Type` string identifying the attribute. Producers are encouraged to use a namespace-like convention (`eam.hedge.variantOf`, `distributor.channel.code`) to avoid name collisions.
- **`Type`** — a single-character enumeration with the values `T` (Text), `N` (Number), `D` (Date), or `B` (Boolean).
- **One of four value elements**, chosen to match the `Type`: `ValueText` for `T`, `ValueNumber` for `N`, `ValueDate` for `D`, `ValueBoolean` for `B`.

An `Attribute` that declares `Type=N` and then carries a `ValueText` child, or that declares `Type=T` and then carries a `ValueNumber`, is schema-invalid in spirit even though the XSD allows the mismatch through its `xs:choice` structure. Producers should always match the type flag to the value element.

The `CustomAttributes` element itself appears at many points in the FundsXML schema — as an optional last child of `ControlDataType`, `AssetType`, `FundStaticDataType`, and several other complex types. Consumers read it whenever they encounter it and treat the values according to their own knowledge of the attribute names. An unknown attribute is not an error; it is simply not interpreted.

### 9.4.3 A Validated Example

The listing below is a minimal FundsXML document whose `ControlData` block ends with a `CustomAttributes` element containing four entries: a text attribute identifying the producer's pipeline version, a numeric attribute naming the delivery's serial number within the month, a date attribute recording when the first-cut version of the delivery was produced, and a Boolean flag indicating whether the delivery is a replacement for an earlier one. The full document validates against the current schema.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-CA-001</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
    </DataSupplier>
    <DataOperation>INITIAL</DataOperation>
    <Language>en</Language>
    <CustomAttributes>
      <Attribute>
        <Name>eam.pipeline.generator</Name>
        <Type>T</Type>
        <ValueText>egf-batch v7.3.1</ValueText>
      </Attribute>
      <Attribute>
        <Name>eam.delivery.serial</Name>
        <Type>N</Type>
        <ValueNumber>472</ValueNumber>
      </Attribute>
      <Attribute>
        <Name>eam.delivery.firstCutSent</Name>
        <Type>D</Type>
        <ValueDate>2026-04-01</ValueDate>
      </Attribute>
      <Attribute>
        <Name>eam.amend.isReplacement</Name>
        <Type>B</Type>
        <ValueBoolean>false</ValueBoolean>
      </Attribute>
    </CustomAttributes>
  </ControlData>
</FundsXML4>
```

The four attributes above have no meaning to any generic FundsXML consumer, and that is the point. A consumer that recognises the `eam.*` prefix — presumably because it has an integration contract with Europa Asset Management S.A. — reads the values and uses them for whatever purpose the contract defines. A consumer that does not recognise the prefix ignores the attributes entirely, parses the rest of the FundsXML document normally, and continues. No conformance is broken.

### 9.4.4 Governance and Best Practices

The power of `CustomAttributes` is also its danger. Every attribute a producer adds is a local extension that only a consumer who knows about it can use, and every such extension makes the FundsXML dialect of that producer slightly different from the global standard. Four governance rules minimise the cost of extensions over time.

**Rule 1: Name attributes in a namespace-like convention.** A producer that uses bare names like `status` and `batchNo` invites collision with any other producer that uses the same names, and consumers that merge data from multiple producers will not know which producer a given attribute came from. Names like `eam.delivery.status` and `bnp.batch.number` make the producer visible in the attribute name itself.

**Rule 2: Use `CustomAttributes` for producer-specific operational metadata, not for fund content that has a real home in the schema.** A producer who writes the fund's management fee into a `CustomAttributes/Attribute` because the pipeline was written before the producer understood the schema's native fee fields is causing trouble for every consumer. Content that belongs in a first-class schema field should live there; `CustomAttributes` is for the long tail of operational, pipeline-level, and truly proprietary data that the schema does not cover.

**Rule 3: Prefer a schema change request over a permanent `CustomAttributes` entry.** If a producer finds itself shipping the same `CustomAttributes` entry on every delivery for several months, the need is probably not truly proprietary — it is a gap in the standard, and the right response is to propose the field to the FundsXML working groups (Chapter 3.3.2) so that a future schema release can absorb it as a first-class element. Long-lived `CustomAttributes` are a smell that the standard needs to evolve.

**Rule 4: Document every attribute the producer emits in a bilateral contract with each consumer that uses it.** Without documentation, a consumer receiving an attribute it does not know cannot reliably decide whether to store it, warn about it, or ignore it. A short specification document accompanying the FundsXML delivery stream — typically updated whenever the producer adds or retires an attribute — keeps consumers aligned without requiring them to reverse-engineer the producer's schema.

---

## 9.5 Country-Specific Additions

The last of the four advanced schema areas is `CountrySpecificData`. This is the mechanism by which FundsXML carries national regulatory extensions that apply only in specific jurisdictions — the Austrian OeKB master data sheet, the Luxembourg CSSF fund-registration identifiers, the French AMF reporting extensions, and so on. The mechanism appears in two structurally distinct places in the schema, and understanding both is essential to reading a real production document.

### 9.5.1 Two Places, Two Purposes

The first place is **inside `ControlData`**. The `ControlData/CountrySpecificData` element carries country-specific *control-layer* data — metadata about the delivery itself that is specific to a particular national regulator. The Austrian version, for example, carries fields that the Oesterreichische Kontrollbank (OeKB) fund data portal needs to accept or reject a delivery; the other national sub-branches typically carry their own national equivalents or, where no national control metadata is defined, appear as free-form containers.

The second place is **at the root of the FundsXML document**, as a top-level `CountrySpecificData` element that sits alongside `Funds`, `AssetMasterData`, `Documents`, and [`RegulatoryReportings`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings). The root-level `CountrySpecificData` carries country-specific *content* — national regulatory fields that are substantive rather than procedural. For Germany, this region is typed to carry PRIIPS-DE-EPT-Pia-specific characteristics (a national extension to the EPT regulatory template from Chapter 8). For other countries, the region is declared as `xs:anyType`, which gives producers the freedom to carry any XML content their national regulator requires, at the cost that consumers cannot validate the content without additional out-of-band schema knowledge.

Both places coexist in the same document: a FundsXML delivery can populate `ControlData/CountrySpecificData/AT` (for Austrian control-layer metadata) and `/CountrySpecificData/LU` (for Luxembourg content-layer extensions) in the same file, and consumers read each region independently.

### 9.5.2 The Country-Specific Module Architecture

The schema's `ModuleUsage` element inside `ControlData` (which we met in Chapter 4 and revisit here) lets a producer declare which country-specific sub-modules a delivery uses. Values include `CountrySpecificData_AT`, `CountrySpecificData_DE`, `CountrySpecificData_DK`, `CountrySpecificData_FR`, `CountrySpecificData_LU`, and `CountrySpecificData_NL`. A consumer that supports only a subset of these modules can read the `ModuleUsage` declaration and decide quickly whether the delivery is within its supported range, without having to parse the actual country-specific content first.

The modules themselves are defined in separate XSD files — `FundsXML4_CountrySpecificData_AT.xsd`, `FundsXML4_CountrySpecificData_LU.xsd`, and so on — that the main schema includes. In the project-local copy of `FundsXML4.xsd` used throughout this book, most country modules are declared with `xs:anyType`, giving producers maximum flexibility; the extended schemas in the full FundsXML distribution contain richer national-regulator-specific types that some producers and consumers use instead.

### 9.5.3 A Validated Example

The listing below shows a FundsXML document with `CountrySpecificData` populated in both places. The `ControlData` block carries an Austrian control-layer extension naming the OeKB fund data portal as the target registry, with two free-form information elements. The root-level `CountrySpecificData` carries a Luxembourg content extension with a fictional CSSF registration number and registration date for the fund. Both branches validate against the current schema.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-CS-001</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T06:47:13Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
    </DataSupplier>
    <DataOperation>INITIAL</DataOperation>
    <Language>en</Language>
    <CountrySpecificData>
      <AT>
        <FundDataPortalContent>OeKB Stammdatenblatt</FundDataPortalContent>
        <FundDataPortalInfos>
          <Info type="source">EAM-Luxembourg delivery gateway</Info>
          <Info type="note">Monthly month-end reporting</Info>
        </FundDataPortalInfos>
      </AT>
    </CountrySpecificData>
  </ControlData>
  <CountrySpecificData>
    <LU>
      <CSSFRegistration>
        <RegistrationNumber>O00001234</RegistrationNumber>
        <RegistrationDate>2012-01-15</RegistrationDate>
      </CSSFRegistration>
    </LU>
  </CountrySpecificData>
</FundsXML4>
```

Reading the two country-specific regions, the Austrian section inside `ControlData` is structurally typed: `FundDataPortalContent` is a defined element from `CountrySpecificControlDataATType` in the schema, and `FundDataPortalInfos/Info` has a defined complex type with a required `type` attribute. Every field in the Austrian block is checked against the schema during validation. The Luxembourg section at the root, by contrast, is declared as `xs:anyType` in the local schema, so the producer is free to invent element names like `CSSFRegistration` and `RegistrationNumber` — the schema accepts them without structural checking, and a consumer that understands the Luxembourg content conventions can parse them out. The document as a whole validates; the difference between the two country branches is in how much *structural* validation each branch imposes on its content.

---

## 9.6 How the Advanced Areas Fit Together

The four advanced areas treated in this chapter — `Documents`, `ds:Signature`, `CustomAttributes`, and `CountrySpecificData` — sit alongside the five main areas from Chapters 4 to 8. Figure 9.1 shows the complete set of possible children of the root `FundsXML4` element, in the order the schema requires.

**Figure 9.1 — The complete root structure of a FundsXML 4.2.8 document**

```
                          <FundsXML4>
                               │
   ┌──────────────┬────────────┼────────────┬──────────────────┐
   │              │            │            │                  │
<ControlData> <Funds>  <AssetMgmtCompany <AssetMaster    <Documents>
 (required)  (optional)   DynData>         Data>        (optional)
                         (optional)     (optional)          Ch. 9
   Ch. 4        Ch. 5                       Ch. 6
   │                                                            │
 + CustomAttributes                                    + DocumentURL /
   (embedded in                                          BinaryData
   ControlData)                                          + Signature flag
   │
 + CountrySpecificData
   (embedded in
   ControlData)

         ┌─────────────────────────┬───────────────────────┐
         │                         │                       │
  <RegulatoryReportings>   <CountrySpecificData>      <ds:Signature>
     (optional)                (optional)              (optional)
        Ch. 8                      Ch. 9                  Ch. 9
```

The figure makes three points. First, **all four advanced areas are optional**: a minimal valid FundsXML document needs only `ControlData`, and every other root child — including the main content in `Funds` and `AssetMasterData` — is optional at the schema level. Second, **`CustomAttributes` appears in two places**: as a last child of `ControlData` (where it typically carries delivery-level operational metadata) and as a last child of several of the main content types (where it carries content-level extensions). The two uses are orthogonal: a producer can populate `CustomAttributes` on any of the element types that allow it without interfering with the others. Third, **the signature, if present, must come last**: the XSD specifies `ds:Signature` as the final optional child of `FundsXML4`, so a document with a signature has the signature after every other section. This is structural, not decorative — it is what allows the enveloped-signature transform to compute correctly.

A production FundsXML delivery that uses all four advanced areas is not common, but it is possible. The Europa Growth Fund's quarterly ESAP submission (Chapter 8) uses three of them: a `Documents` section with the KID and the annual report, a top-level `CountrySpecificData` section with Luxembourg and German extensions for the destination regulators, and an enveloped `ds:Signature` at the root so that the regulator's ingestion pipeline can verify the source. `CustomAttributes` is used more sparingly, only where the Europa Asset Management ingestion pipeline needs to signal an internal metadata value that the schema's first-class fields do not cover.

---

## 9.7 Common Pitfalls

The following short list captures the mistakes that, in our experience, cause the greatest share of advanced-area-related production incidents.

- **`Documents` URLs stop resolving after an archive is retrieved.** A consumer archives a FundsXML file but not the PDFs it references, and six months later the URLs return 404. The fix is either to use `BinaryData` for content that must be archived atomically, or to run a consumer-side fetch-and-store step as part of every delivery's ingestion.
- **`Document/Signature=Digital` confused with a root-level `ds:Signature`.** The flag indicates that the *referenced PDF* is signed; the root `ds:Signature` would sign the *FundsXML envelope*. Mistaking the two produces the wrong expectations about what has and has not been cryptographically authenticated.
- **XMLDSig validation fails after a "cosmetic" edit.** A producer reformats the signed document (adds whitespace, re-orders attributes) without re-signing it, and the downstream verifier rejects the signature. The fix is: never touch a signed document after signing. If a change is needed, re-sign.
- **`CustomAttributes` used for content that has a native schema home.** The fund's management fee, its benchmark name, its ISIN — these all have first-class schema fields, and putting them into `CustomAttributes` breaks consumers that expect to find them at their proper location. Use the native fields.
- **`CustomAttributes` with unnamespaced names.** `status` is a terrible attribute name because it collides with every other producer that uses it. Use `producer.section.name` conventions.
- **A country-specific branch is populated in the wrong place.** A producer puts CSSF registration content inside `ControlData/CountrySpecificData/LU` when it belongs in the root-level `CountrySpecificData/LU`, or vice versa. Read §9.5.1 and pick the right region for the content.
- **`ds:Signature` placed before the content it should sign.** The schema is explicit that `ds:Signature` comes *last* in the sequence of root children. A file that puts the signature earlier does not validate.

---

## 9.8 Key Takeaways

- `Documents` is a root-level schema area that carries fund-related documents alongside the structured data. Each `Document` has a typed classification (*Factsheet*, *KID*, *PRIIPS-KID*, *Prospectus*, *AnnualReport*, *AuditReport*, *AIFMD*), language, applicability to fund/share-class, and one of two content modes — `DocumentURL` or `BinaryData`.
- The schema-imported `ds:Signature` element at the root of `FundsXML4` allows enveloped XML digital signatures over the whole document. The signature algorithm, canonicalisation method, and digest method are chosen through standard XMLDSig `Algorithm` URIs, with RSA-SHA-256 and Canonical XML 1.0 as the current defaults.
- `Document/Signature` (the enum flag with values *No*, *Digital*, *Scan*) and the root-level `ds:Signature` are orthogonal: the former signals whether a referenced PDF is signed, the latter signs the FundsXML envelope. A document can have either, both, or neither.
- `CustomAttributes` — not `CustomDataFields` — is the FundsXML extension mechanism. Each `Attribute` has a `Name`, a `Type` (T/N/D/B), and one of `ValueText` / `ValueNumber` / `ValueDate` / `ValueBoolean`. The mechanism appears at many points in the schema and lets producers carry proprietary metadata without forking the standard.
- `CountrySpecificData` appears in two structurally distinct places: inside `ControlData` for country-specific *control-layer* metadata, and at the root of the document for country-specific *content*. Austrian control-layer extensions are strongly typed; most other national regions use `xs:anyType` and accept free-form content.
- Every XML listing in this chapter validates against `FundsXML4.xsd` with `xmllint --noout --schema FundsXML4.xsd <file>`. The listings are self-contained FundsXML documents, not fragments, and can be copied verbatim into a file and validated as-is.

With the advanced schema areas covered, Part II of the book is complete. Chapter 10 opens Part III with a treatment of validation and quality assurance — the two-stage validation model (schema validation plus business validation), the tolerance rules that production pipelines should apply, and a complete validation workflow built around the Europa Growth Fund's monthly delivery. Chapter 11 follows with the principal tools of the FundsXML ecosystem.
