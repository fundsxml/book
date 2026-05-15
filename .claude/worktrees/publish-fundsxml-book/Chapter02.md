<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 2 — XML and XSD — The Technological Basis

*Foundational knowledge for working with FundsXML*

---

## 2.1 From "Why" to "How": A Short Hop

Chapter 1 built the case for a single, shared standard for fund data. It did so deliberately without a single line of XML: the argument there was economic and operational, not technical. This chapter begins the technical half of the journey. It introduces XML and XSD — the two technologies on which FundsXML rests — and it does so from the perspective of a fund professional who needs to *read*, *validate*, *query*, and *transform* fund-data documents, not from the perspective of a software engineer building an XML parser from scratch.

Return, for a moment, to the Europa Growth Fund. At the end of Chapter 1, the operations team had decided — at least in principle — to adopt FundsXML as the canonical representation of its fund-product data. The next question on the team's mind is very practical: *what does such a FundsXML file actually look like?* When a colleague drops a 2-megabyte document on the desk and says "this is the monthly delivery", what should we expect to see? How do we confirm that the file is correct before we send it out? How do we extract the twenty fields that the fact-sheet engine needs? How do we turn the same file into the CSV that a Swiss distributor still insists on?

Those are the questions this chapter answers in general terms. Chapter 3 will then apply the answers to the specific shape of the FundsXML schema; Chapters 4 to 9 will walk through the schema module by module; Chapter 10 will explain the two-stage validation discipline that keeps production deliveries healthy. Everything from here on depends on the vocabulary of XML and XSD being second nature, and so the investment of thirty pages at this point is repaid many times over in the chapters that follow.

The chapter is deliberately practical. XML is a large specification with many corners that FundsXML does not use, and this book does not visit them. Where a topic is genuinely optional for a fund practitioner, we say so and move on. Where a topic matters every day — element-versus-attribute design, schema validation, namespaces, the basic XPath idiom — we spend the time.

By the end of this chapter, you should be able to:

- read and write well-formed XML documents and recognise the most common syntactic mistakes;
- explain the purpose of XML namespaces and interpret a namespaced document;
- read an XSD schema and map its declarations to the instance documents they constrain;
- describe the difference between well-formedness and schema validity, and between schema validation and business-rule validation;
- navigate an XML document with elementary XPath expressions;
- understand what an XSLT transformation does and follow a simple stylesheet end to end;
- name the tools a fund-industry practitioner typically uses for day-to-day XML work and know which later chapter treats each of them in depth.

No prior XML experience is assumed. Readers who already write XSLT 3.0 in their sleep may skim the first half of the chapter and rejoin us at §2.10.

---

## 2.2 XML in One Page

At its heart, XML is a notation for writing down trees of data as plain text. A document is a single tree with a single root. Every branch of the tree is an *element*. Each element has a name, may carry *attributes*, may contain other elements, and may contain text. That is essentially the whole data model; everything else in this chapter is either syntax that expresses this model or a schema language that constrains it.

The Europa Growth Fund, stripped to its bare essentials, looks like this in real FundsXML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-001</UniqueDocumentID>
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
  <Funds>
    <Fund>
      <Identifiers>
        <LEI>549300ABCDEFGHIJ1234</LEI>
      </Identifiers>
      <Names>
        <OfficialName>Europa Growth Fund</OfficialName>
      </Names>
      <Currency>EUR</Currency>
      <SingleFundFlag>true</SingleFundFlag>
      <FundDynamicData>
        <TotalAssetValues>
          <TotalAssetValue>
            <NavDate>2026-03-31</NavDate>
            <TotalAssetNature>OFFICIAL</TotalAssetNature>
            <TotalNetAssetValue>
              <Amount ccy="EUR">464552848.78</Amount>
            </TotalNetAssetValue>
          </TotalAssetValue>
        </TotalAssetValues>
      </FundDynamicData>
      <SingleFund>
        <ShareClasses>
          <ShareClass>
            <Identifiers>
              <ISIN>LU1234567890</ISIN>
            </Identifiers>
            <Names>
              <OfficialName>Europa Growth Fund I EUR Acc</OfficialName>
            </Names>
            <Currency>EUR</Currency>
          </ShareClass>
          <ShareClass>
            <Identifiers>
              <ISIN>LU1234567892</ISIN>
            </Identifiers>
            <Names>
              <OfficialName>Europa Growth Fund R CHF Acc Hedged</OfficialName>
            </Names>
            <Currency>CHF</Currency>
          </ShareClass>
        </ShareClasses>
      </SingleFund>
    </Fund>
  </Funds>
</FundsXML4>
```

Three observations are worth making before going further. First, this is a minimal but **schema-valid** FundsXML document — it validates against the real `FundsXML4.xsd` without errors (Appendix D contains the full set of progressively richer examples). The document carries a [`ControlData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData) envelope that identifies the delivery, followed by a [`Funds`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds) block with a single fund and its two share classes. Chapters 4 and 5 explain every element in this document in depth; for now, read it as a map of the territory ahead.

Second, the document is entirely human-readable. A fund operations analyst can inspect it with any text editor and, after a minute of orientation, understand it without tooling. The element names — `ControlData`, `Fund`, `Names`, `OfficialName`, `Currency`, `ShareClass`, `ISIN` — read almost like a structured form. This readability is one of XML's enduring strengths and is a large part of why regulators and industry bodies have chosen XML-based formats for durable disclosures.

Third, the tree structure is visible in the indentation but does not depend on it. XML ignores most whitespace between elements; the indentation is a convenience for humans. Parsers see the same tree regardless of how the file is formatted.

A note on the examples in this chapter. The document above and the share-class examples later in this chapter are real FundsXML validated against the 4.2.8 schema. A small number of examples in the XML-syntax and namespace sections (§2.3–§2.5) use simplified, hand-rolled elements to illustrate general XML concepts in isolation; where this is the case, the text says so. Every example that claims to be FundsXML is schema-valid.

With this much in hand, we can now be precise about the syntactic rules that make a document well-formed.

---

## 2.3 XML Syntax — Elements, Attributes, Text

### 2.3.1 Well-formedness

An XML document is *well-formed* if it obeys a small number of strict rules. A well-formed document can be parsed by any conforming XML processor, regardless of whether it matches any schema. The rules are:

- **Exactly one root element.** The outermost pair of tags encloses everything. In the Europa Growth Fund example above, [`<FundsXML4>`](https://fundsxml.github.io/index.html?xpath=/FundsXML4) is the root.
- **Every start tag has a matching end tag.** `<Name>Europa Growth Fund</Name>` is well-formed; `<Name>Europa Growth Fund` is not.
- **Elements nest properly.** `<a><b></b></a>` is well-formed; `<a><b></a></b>` is not.
- **Element and attribute names are case-sensitive.** `<Fund>` and `<fund>` are different elements.
- **Attribute values are always quoted.** Single or double quotes are both allowed: `id="EGF-001"` and `id='EGF-001'` are equivalent.
- **Five characters are reserved and must be escaped** when they appear as text: `<` becomes `&lt;`, `>` becomes `&gt;`, `&` becomes `&amp;`, `"` becomes `&quot;`, and `'` becomes `&apos;`.

An element with no content can be written as `<ShareClass></ShareClass>` or, equivalently, as the empty-element form `<ShareClass/>`. Parsers treat the two forms as identical.

A well-formed document is not necessarily a *useful* document: it may still violate a schema, contain the wrong fields, or carry impossible values. Well-formedness is the bottom rung of the validation ladder, not the top.

### 2.3.2 Elements versus attributes

One of the oldest debates in XML design is the choice between expressing a piece of information as a child element or as an attribute. Consider two hypothetical ways of writing a fund's base currency (these are general XML illustrations, not FundsXML elements):

```xml
<!-- As a child element -->
<Fund>
  <BaseCurrency>EUR</BaseCurrency>
</Fund>

<!-- As an attribute -->
<Fund baseCurrency="EUR"/>
```

Both carry the same information. The working rules of thumb, applied consistently throughout FundsXML and throughout the examples in this book, are:

- **Use elements for data, attributes for metadata.** The currency of a fund is data; the version of a schema or the identifier of a document is metadata about the document itself.
- **Use elements when the value may later need sub-structure.** A fund name today is a string; tomorrow it might need a language tag or a sort form. Elements can grow children; attributes cannot.
- **Use attributes for values that qualify the enclosing element without being part of its content.** The `id` on a record, the unit of a measurement, the version of a format.
- **Prefer elements when in doubt.** FundsXML leans heavily towards elements, and the habit of reaching for an element first is the safer default for a practitioner.

Illustrated on a hypothetical share-class element (not the actual FundsXML element, which uses `Identifiers/ISIN` and `Names/OfficialName` instead):

```xml
<ShareClass id="EGF-001-ACC-EUR" currency="EUR">
  <ISIN>LU0000000001</ISIN>
  <Name xml:lang="en">Europa Growth Fund, Accumulating, EUR</Name>
  <Name xml:lang="de">Europa Growth Fund, Thesaurierend, EUR</Name>
</ShareClass>
```

Here `id` and `currency` are qualifiers — they tell us *which* share class and in *what unit* — while the `ISIN` and the two `Name` elements carry the share class's own data. Note how the element form of `Name` naturally accommodates two languages; an attribute form could not. The real FundsXML schema resolves this design question consistently in favour of elements: the currency is always a child element `<Currency>EUR</Currency>`, not an attribute.

### 2.3.3 Text, mixed content, CDATA, and comments

Element content falls into three categories. An element may contain only other elements (*element-only content*, the usual case for structured data such as a portfolio), only text (*text-only content*, typical for leaf fields such as `<ISIN>`), or a mixture (*mixed content*, in which text and child elements are interleaved). Mixed content is common in fact-sheet prose and regulatory narrative text, but rare in portfolio and transaction structures.

A short fact-sheet paragraph might look like this:

```xml
<InvestmentPolicy xml:lang="en">
  The fund invests primarily in large-capitalisation European equities
  and uses a <Benchmark>MSCI Europe NR</Benchmark> as its reference.
</InvestmentPolicy>
```

When text must contain characters that XML would otherwise interpret — for example, a literal `<` or `&` — two escape mechanisms are available. The first is the entity-reference mechanism already mentioned (`&lt;`, `&amp;`). The second is a `CDATA` section, which tells the parser "everything inside here is raw text, don't try to interpret it":

```xml
<LegalText><![CDATA[
  The management fee is 1.25% per annum of the NAV
  & is accrued daily.
]]></LegalText>
```

`CDATA` is most useful when embedding pre-formatted text, such as an HTML fragment or a legal notice, that contains many XML-special characters.

Comments are written `<!-- like this -->` and are ignored by parsers. They are invaluable in schemas and in hand-edited sample files, but should not be relied upon to carry information that downstream consumers need, because many XML tool chains discard them silently. Processing instructions of the form `<?target data?>` also exist; FundsXML does not use them beyond the XML declaration itself, and a practitioner need only recognise them.

---

## 2.4 Character Encoding and the XML Declaration

The first line of almost every XML file is the *XML declaration*:

```xml
<?xml version="1.0" encoding="UTF-8"?>
```

Three things are worth knowing about it.

First, the declaration is strictly optional under XML 1.0 when the encoding is UTF-8 or UTF-16, but in practice every serious tool chain emits it. Always include it.

Second, the `encoding` attribute tells the parser how the bytes in the file map onto characters. UTF-8 is the default in practice and should be the default in your own production of FundsXML files. The alternatives — ISO-8859-1, Windows-1252, UTF-16 — are legacy choices that cause avoidable pain, most commonly when a German umlaut, a French accent, or a non-breaking space survives a round trip through a tool chain that guesses the encoding wrongly.

Third, UTF-8 files may be preceded by a three-byte *byte-order mark* (the BOM, `EF BB BF`). Some Windows tools write the BOM by default; some Unix tools refuse to parse a file that begins with it. Neither behaviour is strictly wrong, but the combination is a reliable source of production incidents. The safe rule for FundsXML work is: **emit UTF-8 without a BOM**, and treat the appearance of a BOM in an incoming file as a yellow flag worth investigating.

Encoding is not an academic concern for the fund industry. Multi-lingual fund names, legal disclaimers with em-dashes and typographic quotes, and regulatory text with accented characters all pass through the same pipeline as the numbers. A single mis-configured character set turns *Société Générale* into *Société Générale*, and a downstream regulator is unlikely to laugh.

---

## 2.5 Namespaces

### 2.5.1 Why namespaces exist

As soon as XML documents began to combine data from multiple sources, a practical problem emerged. Two independently designed vocabularies might both use an element called `Name`, or `Address`, or `Type`. Without some way of telling them apart, a document that mixed them would be ambiguous.

XML namespaces solve this by giving every element and attribute a two-part name: a namespace URI (which acts as a globally unique identifier) and a local name (the short name used in the document). Two elements share a name only if both parts match.

### 2.5.2 Declaring and using namespaces

A namespace is bound to a prefix (or to the default) by an `xmlns` attribute:

```xml
<Fund xmlns="http://example.org/illustrative/fund"
      xmlns:sig="http://www.w3.org/2000/09/xmldsig#">
  <Name>Europa Growth Fund</Name>
  <sig:Signature>
    <!-- digital signature content, treated in Chapter 9 -->
  </sig:Signature>
</Fund>
```

Two namespaces are in play here. The default namespace, declared by `xmlns="..."` without a prefix, applies to `<Fund>` and `<Name>`. The second namespace is bound to the prefix `sig:` and applies to `<sig:Signature>`. A consumer that understands both vocabularies can process each subtree independently.

Three points deserve emphasis because they are the source of most namespace-related confusion:

- **The URI is an identifier, not an address.** Nothing lives at `http://example.org/illustrative/fund`. The URI is chosen for uniqueness, not for retrieval. FundsXML's own namespace URIs follow the same convention.
- **Prefixes are local aliases, not part of the name.** The same document could write `xmlns:f="http://example.org/illustrative/fund"` and then use `<f:Fund>` instead of `<Fund>`; both forms identify the same element. Tools that compare XML must compare the expanded names, not the prefixed ones.
- **Default namespaces propagate to descendants.** Once a default namespace is declared on an element, every unprefixed descendant element is in that namespace — until an inner element redeclares it. Attributes are not covered by the default namespace; an unprefixed attribute is in no namespace at all. This asymmetry surprises newcomers and is worth remembering.

### 2.5.3 Namespace-aware tooling

A recurring field-failure pattern around FundsXML is the use of a tool that is not namespace-aware. Such tools treat `<f:Fund>` and `<Fund>` as different elements purely on the basis of the textual prefix, and produce XPath queries that silently return empty results against files whose authors happen to have chosen a different prefix. Every tool shown in this book — xmllint, oXygen, IntelliJ, VS Code, and the FreeXmlToolkit treated in Chapter 11 — is namespace-aware. If you ever find yourself writing an XPath expression against a FundsXML document that matches nothing despite an obvious element being present, the first diagnosis should always be: *am I missing a namespace binding?*

---

## 2.6 From Well-Formed to Valid: Enter XSD

Well-formedness asks whether a document obeys XML's syntactic rules. *Validity* asks a stronger question: does the document obey the rules of some particular vocabulary? Those rules — which elements may appear, in what order, how often, with what types of content, and with what attributes — are written in a *schema*, and the act of checking a document against that schema is *schema validation*.

XML has more than one schema language. Three are worth knowing by name:

- **DTD (Document Type Definition)** is the original schema language, inherited from SGML. It is expressive but crude: it has no notion of data types beyond "string", no namespace support worth using, and a syntax that is not itself XML. DTDs survive in legacy corners of publishing and HTML but are a historical curiosity for FundsXML purposes.
- **Relax NG** is an elegant, pattern-based schema language that is technically superior to XSD in several ways and is used, for example, by OpenDocument. Its weaker tooling support in enterprise environments has limited its adoption in financial standards.
- **XSD (XML Schema Definition)**, governed by the W3C, is the schema language FundsXML uses. It is itself an XML vocabulary — meaning schemas can be parsed by the same tools that parse instance documents — and it supports a rich type system, namespaces, inheritance, and modularisation.

FundsXML chose XSD for pragmatic reasons. XSD is supported by every serious XML tool, every major programming language, and every enterprise integration platform. Its type system is expressive enough to enforce formats such as ISIN, date, and decimal precision, and its modularisation features scale to the dozens of schema files that make up a modern FundsXML release. No other schema language would have been as durable a choice in 2001, and none has meaningfully displaced it in the two decades since.

The rest of this chapter therefore teaches XSD, and only XSD. When the book speaks of "the schema" from Chapter 3 onwards, it means an XSD schema.

---

## 2.7 XSD Simple Types

XSD divides types into two categories. A *simple type* is a type that constrains a single leaf value — the text content of an element or the value of an attribute. A *complex type* describes the structure of an element with child elements and attributes. This section treats simple types; §2.8 treats complex types.

### 2.7.1 Built-in simple types

XSD provides several dozen built-in simple types. A fund-industry practitioner needs to recognise the following core set on sight:

**Table 2.1 — Core XSD built-in types for fund data**

| Type | Purpose | Example value |
|---|---|---|
| `xs:string` | Arbitrary text | `Europa Growth Fund` |
| `xs:normalizedString` | Text with whitespace normalised | `Europa Growth Fund` |
| `xs:token` | Text with leading, trailing, and multiple internal whitespace collapsed | `EUR` |
| `xs:boolean` | `true` / `false` (or `1` / `0`) | `true` |
| `xs:decimal` | Arbitrary-precision decimal number | `123.456789` |
| `xs:integer` | Whole number | `42` |
| `xs:double` | 64-bit floating point | `1.2345E3` |
| `xs:date` | ISO-8601 date | `2026-04-30` |
| `xs:dateTime` | ISO-8601 date with time and optional timezone | `2026-04-30T17:30:00+02:00` |
| `xs:gYear` | A four-digit year | `2026` |
| `xs:anyURI` | A URI (used for namespace references and links) | `http://example.org/f` |
| `xs:ID` / `xs:IDREF` | A unique identifier / a reference to one | `EGF-001` |

A few observations matter for fund data. `xs:decimal` is the correct type for monetary values and NAVs: it is arbitrary-precision and does not suffer from the rounding surprises of `xs:double`. `xs:date` and `xs:dateTime` require ISO-8601 format — year-month-day, not the assorted national variants; a pipeline that accepts `30/04/2026` is accepting something that is not a valid `xs:date`. `xs:boolean` accepts `true`, `false`, `1`, and `0`, and nothing else; values like `Y` or `Yes` are invalid.

### 2.7.2 Restricting built-in types

The real power of XSD simple types comes from *restrictions* (formally called *constraining facets*): building a new simple type by constraining an existing one. XSD defines twelve constraining facets, and each facet is applicable only to certain families of types. Table 2.2 gives the complete picture.

**Table 2.2 — XSD constraining facets at a glance**

| Facet | Applies to | Effect |
|---|---|---|
| `enumeration` | all types | Value must be one of a listed set |
| `pattern` | all types | Value must match a regular expression |
| `whiteSpace` | string types | Controls whitespace handling: `preserve`, `replace`, or `collapse` |
| `length` | string, binary, list types | Value must have exactly this length |
| `minLength` | string, binary, list types | Value must have at least this length |
| `maxLength` | string, binary, list types | Value must have at most this length |
| `minInclusive` | numeric, date/time types | Value must be ≥ this bound |
| `minExclusive` | numeric, date/time types | Value must be > this bound |
| `maxInclusive` | numeric, date/time types | Value must be ≤ this bound |
| `maxExclusive` | numeric, date/time types | Value must be < this bound |
| `totalDigits` | `xs:decimal` and derived | Maximum total number of digits |
| `fractionDigits` | `xs:decimal` and derived | Maximum number of fractional digits |

Several facets can be combined in a single restriction — for example, a `pattern` and a `maxLength` on the same type. The XSD processor checks every facet; the value must satisfy all of them.

The following worked examples, drawn from Europa Growth Fund data, illustrate each family of facets.

#### String restrictions: `pattern`, `length`, `minLength`, `maxLength`

**An ISIN pattern.** An ISIN is exactly twelve characters: two letters (the country code), followed by nine alphanumeric characters, followed by one decimal digit (the check digit). The XSD that expresses this is:

```xml
<xs:simpleType name="ISINType">
  <xs:restriction base="xs:string">
    <xs:pattern value="[A-Z]{2}[A-Z0-9]{9}[0-9]"/>
  </xs:restriction>
</xs:simpleType>
```

A value of `LU0000000001` validates; a value of `LU000000000` (eleven characters) does not, and neither does `lu0000000001` (lowercase country code). The `pattern` facet uses the regular-expression syntax defined by XSD, which is similar to — but not identical with — the Perl-style regular expressions most programmers know. The most important differences are that XSD patterns always match the *entire* value (no need for `^` and `$` anchors) and that some shorthand character classes differ.

**A bounded text field.** Many FundsXML text fields carry a maximum-length constraint to prevent absurdly long values from reaching the consumer. A typical text field limited to 256 characters:

```xml
<xs:simpleType name="Text256Type">
  <xs:restriction base="xs:string">
    <xs:maxLength value="256"/>
  </xs:restriction>
</xs:simpleType>
```

For an exact-length field — a two-letter ISO country code, for example — the `length` facet is more appropriate than the combination of `minLength` and `maxLength`:

```xml
<xs:simpleType name="ISOCountryCodeType">
  <xs:restriction base="xs:string">
    <xs:length value="2"/>
    <xs:pattern value="[A-Z]{2}"/>
  </xs:restriction>
</xs:simpleType>
```

Here `length` and `pattern` work together: the value must be exactly two characters *and* must consist of two uppercase letters. Either facet alone would be insufficient — `length` alone would accept `12`, and `pattern` alone would accept `ABC` if the expression were written carelessly.

#### Enumeration: `enumeration`

**A currency enumeration.** ISO 4217 defines the three-letter alphabetic currency codes. A minimal enumeration covering the currencies in which the Europa Growth Fund issues share classes might be:

```xml
<xs:simpleType name="CurrencyType">
  <xs:restriction base="xs:string">
    <xs:enumeration value="EUR"/>
    <xs:enumeration value="USD"/>
    <xs:enumeration value="CHF"/>
    <xs:enumeration value="GBP"/>
    <xs:enumeration value="JPY"/>
  </xs:restriction>
</xs:simpleType>
```

In production, the enumeration would cover the complete ISO 4217 list. The principle is the same: an enumeration is the correct way to pin a field to a closed set of values, and it costs nothing at runtime. Enumerations are not limited to strings — they work on any type. An enumeration of `xs:integer` values, for example, can restrict a field to a fixed set of numeric codes.

#### Numeric restrictions: `minInclusive`, `maxInclusive`, `minExclusive`, `maxExclusive`, `totalDigits`, `fractionDigits`

**A NAV decimal constraint.** A NAV per share must be non-negative, and a practitioner may reasonably insist on no more than eight fractional digits:

```xml
<xs:simpleType name="NavType">
  <xs:restriction base="xs:decimal">
    <xs:minInclusive value="0"/>
    <xs:fractionDigits value="8"/>
  </xs:restriction>
</xs:simpleType>
```

The schema rejects `-1.0` and `123.123456789` (nine fractional digits); it accepts `123.45` and `0`.

The difference between *inclusive* and *exclusive* bounds is exactly what the names suggest. `minInclusive value="0"` accepts zero; `minExclusive value="0"` does not. A percentage field that must be strictly between 0 and 100 would use:

```xml
<xs:simpleType name="PercentageType">
  <xs:restriction base="xs:decimal">
    <xs:minExclusive value="0"/>
    <xs:maxExclusive value="100"/>
  </xs:restriction>
</xs:simpleType>
```

The `totalDigits` facet limits the total number of significant digits (before *and* after the decimal point), which is useful for monetary amounts where the database column has a fixed precision:

```xml
<xs:simpleType name="MonetaryAmountType">
  <xs:restriction base="xs:decimal">
    <xs:totalDigits value="18"/>
    <xs:fractionDigits value="2"/>
  </xs:restriction>
</xs:simpleType>
```

This type accepts up to sixteen digits before the decimal point and exactly two after — sufficient for any fund-industry amount.

#### Date and time restrictions: range bounds on `xs:date` and `xs:dateTime`

The same `minInclusive`, `maxInclusive`, `minExclusive`, and `maxExclusive` facets that constrain numbers also constrain dates and date-times. A type for a ContentDate that must lie within the twenty-first century:

```xml
<xs:simpleType name="ReportingDateType">
  <xs:restriction base="xs:date">
    <xs:minInclusive value="2000-01-01"/>
    <xs:maxExclusive value="2100-01-01"/>
  </xs:restriction>
</xs:simpleType>
```

This catches the occasional data-entry error that produces a date in 1026 instead of 2026 — a surprisingly common incident in production.

#### Whitespace handling: `whiteSpace`

The `whiteSpace` facet controls how the XSD processor normalises whitespace before checking other constraints. Three values are available:

- `preserve` — whitespace is left untouched (the default for `xs:string`).
- `replace` — every tab, carriage return, and newline is replaced with a single space.
- `collapse` — like `replace`, but leading and trailing spaces are also stripped and sequences of multiple spaces are collapsed to one.

In practice, `collapse` is the most useful for fund data, because it prevents invisible whitespace from causing downstream mismatches:

```xml
<xs:simpleType name="CleanTokenType">
  <xs:restriction base="xs:string">
    <xs:whiteSpace value="collapse"/>
    <xs:maxLength value="64"/>
  </xs:restriction>
</xs:simpleType>
```

Note that the built-in type `xs:token` already applies `collapse` semantics, so a `whiteSpace` facet is typically needed only when restricting `xs:string` directly.

#### Combining facets

Facets compose freely within the limits of applicability. A real-world FundsXML type might combine several:

```xml
<xs:simpleType name="LEIType">
  <xs:restriction base="xs:string">
    <xs:length value="20"/>
    <xs:pattern value="[A-Z0-9]{18}[0-9]{2}"/>
  </xs:restriction>
</xs:simpleType>
```

A Legal Entity Identifier is exactly twenty characters: eighteen alphanumeric characters followed by two check digits. Both the length and the pattern are enforced; a value that satisfies one but not the other is rejected.

### 2.7.3 Lists and unions

Two further simple-type constructions are occasionally useful. An `xs:list` type describes a whitespace-separated list of values of another simple type — a natural fit for, say, a list of ISINs on a single line. An `xs:union` type describes a value that may belong to any of several simple types — a natural fit for a field that is either a known enumerated code or a free-form override. Both are used sparingly in FundsXML; you will encounter them rarely and should simply recognise the construction when you do.

---

## 2.8 XSD Complex Types and Structuring

A complex type describes an element that has structure: child elements, attributes, or both. It is where the shape of the document is defined. For fund data, almost every element beyond the leaves is a complex type.

### 2.8.1 The basic form

The workhorse complex type declaration uses `xs:sequence` to say "these children, in this order":

```xml
<xs:complexType name="FundType">
  <xs:sequence>
    <xs:element name="Name"          type="xs:string"/>
    <xs:element name="Domicile"      type="xs:string"/>
    <xs:element name="BaseCurrency"  type="CurrencyType"/>
    <xs:element name="ShareClasses"  type="ShareClassesType"/>
  </xs:sequence>
  <xs:attribute name="id" type="xs:ID" use="required"/>
</xs:complexType>
```

This type, together with the earlier `CurrencyType` and a `ShareClassesType` we will define in a moment, fully describes the `<Fund>` element from §2.2. The `use="required"` on the attribute says that the `id` attribute must be present.

Note the strong reminder: this `FundType` is an illustrative hand-rolled type for teaching XSD complex-type syntax. The real FundsXML `FundType`, with its `Identifiers`, `Names`, `Currency`, `SingleFundFlag`, [`FundStaticData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData), [`FundDynamicData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData), and `SingleFund`/`Subfunds` choice, is the subject of Chapter 5 and is documented precisely in Appendix C.

### 2.8.2 Occurrence constraints

Every element declaration can specify how many times it may appear by using `minOccurs` and `maxOccurs`. The defaults are `1` and `1` — exactly once, mandatory. Common variations are:

- `minOccurs="0"` — optional element;
- `minOccurs="0" maxOccurs="unbounded"` — zero or more, the typical shape for a repeated child such as a list of share classes;
- `minOccurs="1" maxOccurs="unbounded"` — one or more;
- explicit numbers — for example, a type that insists on exactly twelve monthly returns would use `minOccurs="12" maxOccurs="12"`.

A `ShareClassesType` that contains one or more `<ShareClass>` children is therefore:

```xml
<xs:complexType name="ShareClassesType">
  <xs:sequence>
    <xs:element name="ShareClass"
                type="ShareClassType"
                minOccurs="1" maxOccurs="unbounded"/>
  </xs:sequence>
</xs:complexType>
```

### 2.8.3 Sequence, choice, and all

`xs:sequence` is the most common compositor, but it is not the only one.

- `xs:sequence` specifies children in a fixed order.
- `xs:choice` specifies that exactly one of several alternatives must appear — used, for example, when a position can be described *either* by its ISIN *or* by a bundle of descriptive fields, but not both.
- `xs:all` specifies that a fixed set of children must each appear exactly once, in any order. It is less often useful than `xs:sequence` and has some restrictions in XSD 1.0 that have limited its adoption.

Compositors can nest: an `xs:sequence` can contain an `xs:choice` that contains another `xs:sequence`, and so on. FundsXML makes extensive use of this nesting to express "either a simple reference to an asset, or a full inline description".

### 2.8.4 Derivation: extension and restriction

XSD supports two forms of type derivation. *Extension* adds children or attributes to an existing type — the XSD equivalent of subclassing with additional fields. *Restriction* narrows an existing type — the equivalent of tightening a contract.

Extension is the more common of the two in fund data. For example, a hypothetical `EquityPositionType` might extend a generic `PositionType` by adding equity-specific fields:

```xml
<xs:complexType name="EquityPositionType">
  <xs:complexContent>
    <xs:extension base="PositionType">
      <xs:sequence>
        <xs:element name="Sector" type="xs:string"/>
        <xs:element name="DividendYield" type="xs:decimal" minOccurs="0"/>
      </xs:sequence>
    </xs:extension>
  </xs:complexContent>
</xs:complexType>
```

Derivation supports substitution groups and abstract types, which are the mechanism by which FundsXML models "many kinds of position" inside a single portfolio container. Chapter 6 returns to this pattern when it covers the portfolio section in detail.

### 2.8.5 Global, local, and anonymous

A simple or complex type can be declared *globally*, at the top level of the schema, with a `name` attribute, and then referenced by its name from wherever it is needed. It can also be declared *locally*, anonymously, inside the element declaration it describes. Global types are reusable and make a schema easier to read; anonymous inline types are briefer but cannot be referred to from elsewhere.

FundsXML leans towards global types for anything more than a one-off leaf, and this book follows the same convention in its examples.

---

## 2.9 Structuring Larger Schemas

A production schema for a complex domain is never a single file. FundsXML distributes its definitions across several dozen files grouped by concern — control data, funds, portfolios, regulatory modules, and so on. Two mechanisms allow XSD files to refer to one another.

`xs:include` merges another schema file into the current one, under the same namespace. It is the natural choice for splitting a single logical schema into multiple physical files for readability. If `Fund.xsd` defines the fund-level types and `ShareClass.xsd` defines share-class types, and both live in the same namespace, then `Fund.xsd` includes `ShareClass.xsd`:

```xml
<xs:include schemaLocation="ShareClass.xsd"/>
```

`xs:import` is used when the imported schema lives in a *different* namespace. This is the mechanism by which FundsXML references third-party vocabularies such as XMLDSig for digital signatures or the FinDatEx regulatory templates, each of which has its own namespace. An `import` must mention the foreign namespace explicitly:

```xml
<xs:import namespace="http://www.w3.org/2000/09/xmldsig#"
           schemaLocation="xmldsig-core-schema.xsd"/>
```

A third, more obscure mechanism — the *chameleon schema* — lets a schema without its own target namespace be included into another and take on the including schema's namespace. It is rare in modern practice and is mentioned here only so that you recognise the name if you encounter it.

Chapter 3 will walk through FundsXML's actual file layout and explain which files import which. For the present chapter, the takeaway is simpler: when you open a schema and see `xs:include` or `xs:import` at the top, you are looking at a composition of several files, and a complete picture of any element's definition may require following the links.

---

## 2.10 XML Validation in Practice

*Schema validation* is the act of checking that an instance document matches a schema. Every mainstream XML tool chain — every IDE plugin, every command-line utility, every library in every programming language — supports it. Performing validation early and often is the single most effective discipline a FundsXML practitioner can adopt.

### 2.10.1 Two error classes

Validation produces errors of two very different kinds, and learning to distinguish them is half the battle.

*Well-formedness errors* are syntactic: the file is not even XML. Typical messages are "mismatched tag", "attribute value not quoted", "premature end of data", or "encoding error". A well-formedness error means no further validation is possible — the parser cannot build a tree.

*Schema validity errors* are structural: the file is valid XML but does not match the schema. Typical messages are "element X not expected here", "attribute Y is required but missing", "value Z does not match pattern", or "element W has invalid child element V".

The distinction matters because the two classes of error are fixed differently. A well-formedness error is almost always the result of a tool that was not designed to emit XML — a template-based generator, a hand edit, a buggy library. A schema validity error is almost always a semantic mismatch: the producer's understanding of the vocabulary diverged from the schema's.

### 2.10.2 Validating from the command line

The simplest production-grade validator is `xmllint`, part of the libxml2 library that ships with every modern Linux and macOS system and is readily installed on Windows. A one-line validation against a schema looks like this:

```
xmllint --noout --schema Fund.xsd Fund.xml
```

The `--noout` flag suppresses the default behaviour of reprinting the document on success; without it, a successful validation floods the terminal with the document's content. On success, `xmllint` prints `Fund.xml validates`; on failure, it prints a line-numbered description of each error and exits with a non-zero status.

For continuous-integration pipelines, this is all that is needed. A shell script that loops over the outbound FundsXML files and runs `xmllint` against the schema catches the vast majority of problems at the cheapest possible point — before the files leave the building.

### 2.10.3 Reading a validation error

Consider a deliberately broken share class, in which the ISIN has been corrupted:

```xml
<ShareClass>
  <ISIN>LU000000000X</ISIN>
  <Currency>EUR</Currency>
</ShareClass>
```

Validated against the `ISINType` defined in §2.7.2, this produces an error along the following lines:

```
Fund.xml:7: element ISIN: Schemas validity error :
  Element 'ISIN': [facet 'pattern'] The value 'LU000000000X'
  is not accepted by the pattern '[A-Z]{2}[A-Z0-9]{9}[0-9]'.
```

Three pieces of information matter in this message. The file-and-line prefix (`Fund.xml:7`) points at the offending element. The bracketed facet name (`[facet 'pattern']`) says which restriction rejected the value — here, the regular expression pattern. The value itself (`LU000000000X`) is quoted back so you can compare it to your expectation. Together, these three are enough to diagnose most schema-level errors without reading the schema at all.

### 2.10.4 What schema validation does not catch

Schema validation is powerful but limited. It answers the question *is this document structurally correct?* — not the question *is this document semantically reasonable?* A well-formed, schema-valid FundsXML document may still:

- have a NAV that is positive but implausibly large;
- describe a share class whose currency does not match the base currency of the fund and whose hedged flag is `false`;
- reference an asset by UniqueID that does not appear elsewhere in the document;
- declare a fund-total that does not equal the sum of its position values.

Catching these requires a second layer of checking — *business-rule validation* — which FundsXML implementations typically perform using Schematron or hand-written code. Chapter 10 develops the two-stage validation model in full. For now, it is enough to note that schema validation is necessary but not sufficient, and that no FundsXML production pipeline should ever rely on schema validation alone.

---

## 2.11 XPath

Once you have a FundsXML document, you will want to pull specific values out of it. The tool for that job is **XPath**, a compact expression language for navigating the XML tree. XPath is the query language behind almost every XML technology: XSLT, XQuery, Schematron, and the XML facilities of every mainstream programming language. A solid understanding of XPath makes every later chapter of this book easier to follow.

### 2.11.1 The tree model

XPath sees an XML document as a tree. Every piece of the document is a *node*, and nodes come in seven kinds:

| Node type | Example | Notation in XPath |
|---|---|---|
| Document (root) | the document itself | `/` |
| Element | `<Fund>` | `Fund` |
| Attribute | `ccy="EUR"` | `@ccy` |
| Text | the characters between tags | `text()` |
| Comment | `<!-- … -->` | `comment()` |
| Processing instruction | `<?xml-stylesheet …?>` | `processing-instruction()` |
| Namespace | `xmlns:xsi="…"` | `namespace::xsi` |

For fund-data work, element, attribute, and text nodes account for 99 per cent of all queries. An XPath expression starts at a *context node* and walks the tree from there, producing a *node set* — a collection of zero or more nodes.

### 2.11.2 Navigation: paths, steps, and shortcuts

**Absolute paths** start with a single `/` at the document root and walk downward by element name:

- `/FundsXML4` — the root element.
- `/FundsXML4/ControlData/ContentDate` — the content date of the delivery.
- `/FundsXML4/Funds/Fund` — every `Fund` element under the root.

**Relative paths** start from the current context node. In most command-line tools, the context node is the document root, so the effect is the same as an absolute path; inside XSLT templates and predicates, the context node is whatever node the template is currently processing.

**The double-slash** `//` is the most-used shortcut in practice. It means "anywhere below", at any depth:

- `//ShareClass` — every `ShareClass` element, regardless of where it sits in the tree.
- `//ISIN` — every `ISIN`, however deeply nested.

**The dot `.`** refers to the current context node; **the double dot `..`** refers to the parent node. Both are used constantly inside predicates and XSLT:

- `.` — the current node.
- `..` — the parent of the current node.
- `../Currency` — the `Currency` sibling of the current node's parent.

**Attribute access** uses the `@` prefix:

- `//Amount/@ccy` — the `ccy` attribute of every `Amount` element.
- `//@ccy` — every `ccy` attribute anywhere in the document.

**Wildcards** select nodes regardless of name:

- `//Fund/*` — every direct child element of every `Fund`, whatever the element name.
- `//@*` — every attribute in the document.
- `//Fund/node()` — every child node (elements, text, comments) of every `Fund`.

**Text access** uses `text()`:

- `//ISIN/text()` — the string value of every ISIN element.

### 2.11.3 Predicates and filtering

Predicates, in square brackets, filter node sets by arbitrary conditions. They are the `WHERE` clause of XPath.

**Value comparisons:**

- `//ShareClass[Currency='EUR']` — share classes whose `Currency` child has text content `EUR`.
- `//Fund[Identifiers/LEI='549300ABCDEFGHIJ1234']` — the fund whose LEI matches.
- `//Position[MarketValue > 1000000]` — positions with a market value above one million.

**Positional predicates:**

- `//ShareClass[1]` — the first share class (XPath positions start at 1, not 0).
- `//ShareClass[last()]` — the last.
- `//ShareClass[position() <= 3]` — the first three.

**Existence tests** — a predicate that names a path is true if the path selects at least one node:

- `//ShareClass[Identifiers/ISIN]` — share classes that have an ISIN.
- `//Fund[not(FundDynamicData)]` — funds that have no dynamic data.

**Compound predicates** combine conditions with `and`, `or`, and `not()`:

- `//Position[MarketValue > 1000000 and Currency='EUR']` — EUR positions above one million.
- `//ShareClass[Currency='EUR' or Currency='CHF']` — EUR or CHF share classes.

**Chained predicates** apply successive filters:

- `//ShareClass[Currency='EUR'][1]` — the first EUR share class.

### 2.11.4 Axes: navigating in every direction

Each step in an XPath expression uses an *axis* that determines the direction of travel through the tree. Most of the time the axis is implicit — `Fund/Currency` is shorthand for `Fund/child::Currency` — but the full axis syntax is needed when you must navigate sideways or upward.

**Table 2.4 — XPath axes**

| Axis | Direction | Shorthand | Example |
|---|---|---|---|
| `child::` | direct children | *(default)* | `child::Fund` = `Fund` |
| `attribute::` | attributes | `@` | `attribute::ccy` = `@ccy` |
| `parent::` | parent node | `..` | `parent::Fund` |
| `self::` | current node | `.` | `self::Fund` |
| `descendant::` | all descendants | — | `descendant::ISIN` |
| `descendant-or-self::` | self + descendants | `//` | `descendant-or-self::node()` |
| `ancestor::` | all ancestors | — | `ancestor::Fund` |
| `ancestor-or-self::` | self + ancestors | — | `ancestor-or-self::Funds` |
| `following-sibling::` | later siblings | — | `following-sibling::ShareClass` |
| `preceding-sibling::` | earlier siblings | — | `preceding-sibling::ShareClass` |
| `following::` | everything after | — | `following::Fund` |
| `preceding::` | everything before | — | `preceding::Fund` |

The axes that matter most for fund-data work are `child` (the default), `attribute` (`@`), `parent` (`..`), `descendant-or-self` (`//`), and `following-sibling` / `preceding-sibling`. A practical example: given a `Position` element, find the fund it belongs to:

- `ancestor::Fund/Names/OfficialName` — walks up the tree to the enclosing `Fund` and then back down to its name.

### 2.11.5 Functions

XPath 1.0 provides a compact function library. The functions most relevant to fund-data work fall into four groups.

**String functions:**

| Function | Purpose | Example |
|---|---|---|
| `concat(a, b, …)` | Concatenate strings | `concat(//LEI, ' — ', //OfficialName)` |
| `contains(s, sub)` | Test if `s` contains `sub` | `//Fund[contains(Names/OfficialName, 'Growth')]` |
| `starts-with(s, pre)` | Test if `s` starts with `pre` | `//ISIN[starts-with(., 'LU')]` |
| `substring(s, pos, len)` | Extract substring | `substring(//ISIN, 1, 2)` → country code |
| `string-length(s)` | Length of string | `//Name[string-length(.) > 100]` |
| `normalize-space(s)` | Strip and collapse whitespace | `normalize-space(//OfficialName)` |
| `translate(s, from, to)` | Character-by-character replacement | `translate(//Currency, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')` |

**Numeric functions:**

| Function | Purpose | Example |
|---|---|---|
| `sum(node-set)` | Sum of numeric values | `sum(//Position/MarketValue)` |
| `count(node-set)` | Number of nodes | `count(//ShareClass)` |
| `round(n)` | Round to nearest integer | `round(//NavPerShare)` |
| `floor(n)` | Round down | `floor(//NavPerShare)` |
| `ceiling(n)` | Round up | `ceiling(//NavPerShare)` |
| `number(s)` | Convert to number | `number(//TotalNetAssetValue/Amount)` |

**Boolean functions:**

| Function | Purpose | Example |
|---|---|---|
| `not(expr)` | Logical negation | `//Fund[not(FundDynamicData)]` |
| `true()` / `false()` | Boolean constants | predicate building blocks |
| `boolean(expr)` | Convert to boolean | `boolean(//ISIN)` → true if any ISIN exists |

**Node functions:**

| Function | Purpose | Example |
|---|---|---|
| `name()` | Element name (with prefix) | `//Fund/*[name()='Currency']` |
| `local-name()` | Element name (without prefix) | useful in namespaced documents |
| `namespace-uri()` | Namespace URI of the node | debugging namespace issues |

Illustrated against the Europa Growth Fund document from §2.2: `count(//ShareClass)` returns `2`, `sum(//ShareClass/NavPerShare)` returns the sum of per-share NAVs, and `concat(//OfficialName, ' (', //Currency, ')')` returns `Europa Growth Fund (EUR)`.

### 2.11.6 Operators and expressions

XPath expressions support arithmetic, comparison, boolean logic, and the union operator.

**Arithmetic** — `+`, `-`, `*`, `div`, `mod`:

- `//MarketValue div //TotalNetAssetValue/Amount * 100` — position weight as a percentage.
- `count(//Position) mod 2` — is the number of positions odd or even?

Note that division uses `div`, not `/`, because `/` is already taken as the path separator.

**Comparison** — `=`, `!=`, `<`, `>`, `<=`, `>=`:

- `//Position[Quantity > 10000]` — positions with more than ten thousand units.
- `//TotalAssetValue[NavDate = '2026-03-31']` — the asset value for a specific date.

When used inside XML attributes (as in XSLT), the `<` character must be escaped as `&lt;`.

**Boolean logic** — `and`, `or`, `not()`:

- `//Position[Quantity > 10000 and MarketValue > 5000000]` — large positions by both measures.

**Union** — `|` combines two node sets:

- `//Fund/Names/OfficialName | //Fund/Names/ShortName` — all official and short names together.

### 2.11.7 XPath and namespaces

XPath 1.0 matches elements by their expanded name (namespace URI + local name), not by their textual prefix. When a document uses a namespace — as many real XML documents do — your XPath tooling must be told which prefix in the query stands for which namespace URI. Every XPath-capable tool has its own way of declaring the binding; the mechanism differs, but the obligation is the same. An XPath query written without a namespace binding against a namespaced document is the single most common source of "no results, but I can see the element right there" frustration.

### 2.11.8 XPath versions

XPath has evolved through several versions, and the differences matter for tool selection.

**XPath 1.0** (1999) is the version described in this section. It is universally supported by every XML library, every IDE, and every command-line tool. It works with node sets, strings, numbers, and booleans. For the purposes of reading and querying FundsXML, it is sufficient.

**XPath 2.0** (2007) adds a richer type system (sequences instead of node sets, typed values aligned with XSD), `if`/`then`/`else` expressions, `for` expressions, quantified expressions (`some`/`every`), and a much larger function library including regular-expression matching (`matches()`, `replace()`, `tokenize()`). It is the version used by XSLT 2.0, XQuery, and Schematron.

**XPath 3.0 / 3.1** (2014/2017) adds higher-order functions (functions as values), the `let` expression, arrow operator (`=>`), inline functions, and maps and arrays. It is used by XSLT 3.0 and XQuery 3.1.

For day-to-day FundsXML work, XPath 1.0 covers the vast majority of queries. XPath 2.0 becomes useful when writing Schematron business rules (Chapter 10) or complex XSLT transformations (§2.12), where its richer type system and `matches()` function simplify the work considerably.

---

## 2.12 XSLT Transformations

XSLT — the Extensible Stylesheet Language Transformations — is the standard way of turning one XML document into another document, which may itself be XML, HTML, CSV, plain text, or almost anything else. In a FundsXML context, XSLT is how a single canonical fund-data document becomes a fact-sheet HTML fragment, a distributor-specific CSV, a regulatory submission, or a formatted printout.

### 2.12.1 The mental model

An XSLT stylesheet is itself an XML document. It contains a set of *templates*, each of which says "when you encounter a node that matches *this pattern*, produce *this output*". The processor walks the input tree, matches each node against the templates in turn, and writes the output. The model is declarative, not imperative: you describe the mapping, and the processor decides how to traverse the source.

The three templates you will see most often are `xsl:template`, which defines a match rule; `xsl:apply-templates`, which tells the processor to recursively process child nodes; and `xsl:value-of`, which inserts the string value of a node into the output.

### 2.12.2 Example: FundsXML to CSV

Here is a minimal stylesheet that turns the Europa Growth Fund document from §2.2 into a two-column CSV of ISINs and currencies:

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="/FundsXML4">
    <xsl:text>ISIN;Currency&#10;</xsl:text>
    <xsl:apply-templates select="Funds/Fund/SingleFund/ShareClasses/ShareClass"/>
  </xsl:template>

  <xsl:template match="ShareClass">
    <xsl:value-of select="Identifiers/ISIN"/>
    <xsl:text>;</xsl:text>
    <xsl:value-of select="Currency"/>
    <xsl:text>&#10;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
```

The `xsl:output method="text"` declaration switches the processor into plain-text mode, so that the output is written directly without XML escaping. The root template matches the `FundsXML4` root element, writes a header line, and then delegates to the share-class template for each `ShareClass` child. The share-class template writes one CSV line per input share class. Against the §2.2 document the result is:

```
ISIN;Currency
LU1234567890;EUR
LU1234567892;CHF
```

A real counterparty feed, of course, requires more columns. The following stylesheet produces a richer export that includes the fund name, the share-class name, the LEI of the fund, and the NAV date — all the fields a distributor typically needs in a daily share-class listing:

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="/FundsXML4">
    <xsl:text>FundName;LEI;ISIN;ShareClassName;Currency;NavDate&#10;</xsl:text>
    <xsl:apply-templates select="Funds/Fund"/>
  </xsl:template>

  <xsl:template match="Fund">
    <xsl:variable name="fundName" select="Names/OfficialName"/>
    <xsl:variable name="lei"      select="Identifiers/LEI"/>
    <xsl:variable name="navDate"
      select="FundDynamicData/TotalAssetValues/TotalAssetValue/NavDate"/>
    <xsl:for-each select="SingleFund/ShareClasses/ShareClass">
      <xsl:value-of select="$fundName"/>
      <xsl:text>;</xsl:text>
      <xsl:value-of select="$lei"/>
      <xsl:text>;</xsl:text>
      <xsl:value-of select="Identifiers/ISIN"/>
      <xsl:text>;</xsl:text>
      <xsl:value-of select="Names/OfficialName"/>
      <xsl:text>;</xsl:text>
      <xsl:value-of select="Currency"/>
      <xsl:text>;</xsl:text>
      <xsl:value-of select="$navDate"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
```

Two new XSLT features appear. First, `xsl:variable` captures values from the enclosing `Fund` node so that they can be reused inside the inner `xsl:for-each` loop without repeating the full XPath each time. Second, `xsl:for-each` iterates over the share classes directly rather than delegating to a separate template — a stylistic choice that works well when the logic is short and self-contained. Against the §2.2 document the output is:

```
FundName;LEI;ISIN;ShareClassName;Currency;NavDate
Europa Growth Fund;549300ABCDEFGHIJ1234;LU1234567890;Europa Growth Fund I EUR Acc;EUR;2026-03-31
Europa Growth Fund;549300ABCDEFGHIJ1234;LU1234567892;Europa Growth Fund R CHF Acc Hedged;CHF;2026-03-31
```

This is the beating heart of the distribution pipeline. Every bilateral CSV feed in an unstandardised production, of the kind Chapter 1 catalogued, can be replaced by a single canonical FundsXML file plus one XSLT per counterparty. If Distributor A wants semicolons and Distributor B wants tabs, the difference is a single character in one `xsl:text` element. Changes to any one counterparty touch one stylesheet and nothing else.

### 2.12.3 Example: FundsXML to fact-sheet HTML

A second stylesheet produces a fact-sheet page from the same Europa Growth Fund document. Unlike the CSV, this time the output is a complete HTML document with a title, a summary table of fund-level metadata, and a share-class listing:

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <xsl:template match="/">
    <xsl:variable name="fund" select="/FundsXML4/Funds/Fund"/>
    <xsl:variable name="nav"
      select="$fund/FundDynamicData/TotalAssetValues/TotalAssetValue
              /TotalNetAssetValue/Amount"/>
    <html>
      <head><title><xsl:value-of select="$fund/Names/OfficialName"/></title></head>
      <body>
        <h1><xsl:value-of select="$fund/Names/OfficialName"/></h1>
        <table border="1" cellpadding="4">
          <tr><td>LEI</td>
              <td><xsl:value-of select="$fund/Identifiers/LEI"/></td></tr>
          <tr><td>Currency</td>
              <td><xsl:value-of select="$fund/Currency"/></td></tr>
          <tr><td>NAV</td>
              <td><xsl:value-of select="$nav"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="$nav/@ccy"/></td></tr>
          <tr><td>NAV Date</td>
              <td><xsl:value-of select="$fund/FundDynamicData
                    /TotalAssetValues/TotalAssetValue/NavDate"/></td></tr>
          <tr><td>Content Date</td>
              <td><xsl:value-of
                    select="/FundsXML4/ControlData/ContentDate"/></td></tr>
        </table>

        <h2>Share classes</h2>
        <table border="1" cellpadding="4">
          <tr><th>ISIN</th><th>Name</th><th>Currency</th></tr>
          <xsl:for-each select="$fund/SingleFund/ShareClasses/ShareClass">
            <tr>
              <td><xsl:value-of select="Identifiers/ISIN"/></td>
              <td><xsl:value-of select="Names/OfficialName"/></td>
              <td><xsl:value-of select="Currency"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
```

Several things are worth noting. The root template matches `/` rather than `/FundsXML4`; either form works, but matching the document root is slightly more idiomatic when the stylesheet produces a complete HTML page. The `$fund` and `$nav` variables keep the XPath expressions short and readable inside the template body. The `$nav/@ccy` expression reads the `ccy` attribute from the `Amount` element, so the currency appears next to the value without being hard-coded.

The `method="html"` output declaration switches the processor into HTML-serialisation mode, which is subtly different from XML: empty elements like `<br>` are written without the self-closing slash, boolean attributes are written bare, and character references are emitted in a form that browsers expect. Against the §2.2 document, the result is a self-contained HTML page whose summary table reads:

| | |
|---|---|
| LEI | 549300ABCDEFGHIJ1234 |
| Currency | EUR |
| NAV | 464552848.78 EUR |
| NAV Date | 2026-03-31 |
| Content Date | 2026-03-31 |

and whose share-class table lists both share classes with their ISINs, names, and currencies. A production fact sheet would add styling, logos, and far more data — but the principle is the same: the XSLT carries the layout logic, and the FundsXML document supplies the data.

### 2.12.4 Example: data-quality checks with XSLT

The examples so far transform FundsXML into a different *format* — CSV, HTML. But XSLT can just as well transform a document into a *report about itself*. This opens the door to a lightweight data-quality layer: encode your business rules as an XSLT stylesheet, run it against every incoming file, and inspect the output for violations.

Consider one of the most fundamental fund-data invariants: *the sum of the market values of all portfolio positions must equal the fund's total net asset value on the same date.* If a FundsXML file carries both a `TotalNetAssetValue` and a set of `Position` elements with `TotalValue` amounts, the following stylesheet checks whether they agree:

```xml
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="/FundsXML4">
    <xsl:for-each select="Funds/Fund">
      <xsl:variable name="fundName" select="Names/OfficialName"/>
      <xsl:variable name="fundCcy"  select="Currency"/>
      <xsl:variable name="fundNAV"
        select="FundDynamicData/TotalAssetValues/TotalAssetValue
                /TotalNetAssetValue/Amount[@ccy = $fundCcy]"/>
      <xsl:variable name="positionSum"
        select="sum(FundDynamicData/Portfolios/Portfolio
                /Positions/Position/TotalValue/Amount[@ccy = $fundCcy])"/>
      <xsl:variable name="diff" select="$fundNAV - $positionSum"/>

      <xsl:value-of select="$fundName"/>
      <xsl:text>&#10;  Fund NAV:      </xsl:text>
      <xsl:value-of select="$fundNAV"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$fundCcy"/>
      <xsl:text>&#10;  Position sum:  </xsl:text>
      <xsl:value-of select="$positionSum"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$fundCcy"/>
      <xsl:text>&#10;  Difference:    </xsl:text>
      <xsl:value-of select="$diff"/>
      <xsl:choose>
        <xsl:when test="$diff = 0">
          <xsl:text>&#10;  Result:        PASS&#10;</xsl:text>
        </xsl:when>
        <xsl:when test="$diff &gt; -1 and $diff &lt; 1">
          <xsl:text>&#10;  Result:        PASS (rounding)&#10;</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>&#10;  Result:        FAIL&#10;</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
```

The stylesheet iterates over every `Fund` in the document, computes the sum of position values in the fund's own currency, and compares it with the reported total NAV. A difference below one currency unit is accepted as a rounding tolerance; anything larger is flagged as `FAIL`. The output is plain text, easily piped into a log file or a monitoring system:

```
Europa Growth Fund
  Fund NAV:      464552848.78 EUR
  Position sum:  464552848.78 EUR
  Difference:    0
  Result:        PASS
```

The same principle scales to any business rule that can be expressed as a combination of XPath queries: *does every share class carry an ISIN?*, *is the NAV date consistent with the content date?*, *do percentage allocations sum to 100?* Each rule becomes one additional block in the stylesheet. The output can be plain text, as above, or HTML for a visual dashboard — or even XML, if the quality report is to be consumed by another automated step.

This approach has a practical advantage: it requires nothing beyond an XSLT 1.0 processor, which is already available on every platform (§2.12.6). There is no need to learn a separate validation language. For organisations that prefer a more formal, standards-based approach to business-rule validation, Schematron — which Chapter 10 covers in detail — provides a dedicated assertion language on top of XPath and can be compiled to XSLT automatically. But for teams that already know XSLT, writing quality checks directly is a natural and effective starting point.

The FundsXML working group maintains a public repository of ready-to-use XSLT stylesheets for data-quality checking at [github.com/fundsxml/examples](https://github.com/fundsxml/examples/). It includes both a basic five-section check (XSLT 2.0) and a comprehensive ten-section HTML dashboard (XSLT 1.0) that covers NAV reconciliation, share-class price verification, percentage-allocation checks, asset-specific validations, and more. These stylesheets can be used as-is against any FundsXML 4.x document or adapted to an organisation's specific rules.

### 2.12.5 The identity transform

One small but powerful idiom deserves mention. The *identity transform* is a stylesheet that simply copies its input to its output unchanged:

```xml
<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>
```

Combined with one or two additional templates that override specific nodes, the identity transform is the standard way of making surgical changes to a FundsXML document — for example, renaming a single element or stripping a specific attribute — without touching anything else. Any XSLT tutorial that goes beyond a few pages will show it again and again.

### 2.12.6 Versions

XSLT exists in three main versions. XSLT 1.0 is universally supported and is enough for almost every practical FundsXML transformation a fund practitioner will write. XSLT 2.0 adds sequences, richer types, and grouping constructs. XSLT 3.0 adds streaming (important for very large documents) and higher-order functions. The code in this book uses XSLT 1.0 unless explicitly noted; if you have access to a 2.0 or 3.0 processor, you lose nothing by running 1.0 stylesheets on it.

---

## 2.13 Tools for Day-to-Day XML Work

A practitioner need not build tools from scratch; a rich ecosystem already exists. This section gives the lie of the land; Chapter 11 revisits the tools in depth, with installation guides, configuration advice, and feature-by-feature comparisons.

**Table 2.2 — XML tooling at a glance**

| Tool | Kind | Strengths | Treated in depth |
|---|---|---|---|
| **xmllint** | Command-line | Validation, formatting, XPath; ships with libxml2; free | §2.10, Chapter 10 |
| **oXygen XML Editor** | Commercial IDE | Visual schema design, schema-aware editing, XSLT debugging | Chapter 11 |
| **Altova XMLSpy** | Commercial IDE | Visual design, generation, data mapping | Chapter 11 |
| **IntelliJ IDEA / Ultimate** | General IDE | Strong XML and XSD support, integrated validation | Chapter 11 |
| **VS Code (+ XML plugins)** | General editor | Free; lightweight; good validation with the Red Hat XML plugin | Chapter 11 |
| **Eclipse (+ Web Tools)** | General IDE | Schema view, XML editors, free | Chapter 11 |
| **FreeXmlToolkit** | FundsXML-aware | Purpose-built for FundsXML workflows | Chapter 11 |

Two points about this table matter now. First, all of these tools are namespace-aware and all support XSD validation against the FundsXML schemas. The choice between them is, to a first approximation, a choice of ergonomics and cost, not of capability. Second, the free options — `xmllint`, VS Code with the Red Hat plugin, and the FreeXmlToolkit — are enough to reach a fully operational FundsXML pipeline. The commercial IDEs become attractive when schema *authoring* and visual *data mapping* become part of the daily workflow, not merely schema *consumption*.

**Beyond this chapter.** A knowledgeable reader will notice that this chapter has stopped short of several valid XML topics: XML Catalogs, XInclude, XPointer, XQuery, Schematron, the XSD 1.1 assertion facility, SOAP and WSDL, and XSLT 2.0/3.0 features. None of them are needed to read, validate, or transform FundsXML, and each has been omitted deliberately to keep the chapter short. Where a later chapter reaches for one of them — Schematron in Chapter 10, XMLDSig in Chapter 9 — we will introduce it at that point, in the context where it matters.

---

## 2.14 Common Pitfalls

Every experienced FundsXML practitioner keeps a mental list of recurring traps. The list below is not exhaustive, but it covers the failures that appear most frequently in production.

- **Encoding mismatches.** A file declared as UTF-8 but actually written as Windows-1252 will parse — until the first accented character. Always emit UTF-8, always read it with a UTF-8-aware parser, and never paste text between editors that disagree on their default encoding.
- **The byte-order mark.** A BOM at the start of a UTF-8 file is legal but is rejected by some downstream tools and silently corrupts some others. Configure your editor to save UTF-8 without a BOM.
- **Namespace-unaware XPath.** If an XPath query returns an empty result set against a document in which the element is clearly present, the first check is whether the namespace has been declared to the XPath processor. It almost always has not.
- **Attribute vs element confusion.** Two producers of the same logical data choose differently — one writes `<Currency>EUR</Currency>`, the other `<Amount currency="EUR">100</Amount>` — and a consumer that expects one form silently ignores the other. The schema is authoritative; read it.
- **Decimal-separator locale.** A decimal number written as `1.234,56` is not an `xs:decimal`. European locales that use the comma for the decimal separator and the period for the thousands separator must convert before emitting XML.
- **Whitespace and the silent trim.** `xs:token` collapses internal whitespace; `xs:string` preserves it. An ISIN that someone has appended a stray trailing space to will fail a pattern validation but can pass an `xs:token` comparison — or vice versa, depending on the order.
- **Case-sensitivity of enumerations.** `EUR`, `eur`, and `Eur` are three different values to an XSD enumeration. Converting incoming free text to a normalised form before validating is a defensive habit worth acquiring.
- **Comments as data.** Comments are stripped by many processors. Do not put anything in a comment that you expect to be available downstream.
- **Large files and memory.** A DOM-based parser loads the entire document into memory. For the hundreds-of-megabytes files that a fund-of-funds look-through can produce, a streaming parser (SAX, StAX, or XSLT 3.0 streaming) is the right tool.

Each of these pitfalls has cost someone a production incident at some point. Recognising the pattern in your own pipelines is half the defence.

---

## 2.15 Key Takeaways

- XML represents data as a tree of named elements that may carry attributes and contain text; the whole technical apparatus of this chapter is layered on top of this simple model.
- A document is *well-formed* if it obeys XML's syntactic rules, and *valid* if it additionally matches a schema. Well-formedness is a precondition for validation; validation is the first line of defence against production errors.
- XML namespaces give elements and attributes globally unique identities, and XSD is the schema language in which FundsXML is written; together they enable the composition of independently maintained vocabularies into a single document.
- XSD simple types — with restrictions such as `pattern`, `enumeration`, `minInclusive`, and `fractionDigits` — are the correct mechanism for enforcing formats like ISIN, currency, and NAV precision.
- XSD complex types, built from `xs:sequence`, `xs:choice`, `xs:all`, and element occurrences, describe the shape of every non-leaf element. Type derivation lets specialised types extend or restrict general ones, and `xs:include` and `xs:import` stitch large schemas together from many files.
- Schema validation is powerful but partial; semantic rules that XSD cannot express belong to a second, business-rule validation layer that Chapter 10 develops in full.
- XPath in its 1.0 dialect is enough for almost every fund-data query a practitioner will need to write, and XSLT 1.0 is enough for almost every transformation.
- A small, well-chosen toolchain — a namespace-aware editor, a command-line validator such as `xmllint`, and a FundsXML-aware tool such as the FreeXmlToolkit — is all the equipment required to work productively with FundsXML. Chapter 11 revisits each tool in depth.

With the XML and XSD vocabulary in place, we are ready to look at FundsXML itself — its history, its organisation, its architecture, and its schema layout — which is the subject of Chapter 3.
