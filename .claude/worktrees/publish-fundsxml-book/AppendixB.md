# Appendix B — XML Quick Reference

*A compact cheat sheet for XML syntax, XPath, and XSLT*

---

This appendix is a reference, not a tutorial. It assumes you have read Chapter 2 (or already know XML) and need to look up a specific piece of syntax quickly while working on a FundsXML problem. Conventions: syntax fragments are shown in `monospace`, operator and function tables are compact, and worked examples use short FundsXML snippets rather than abstract placeholders. Where XPath or XSLT behaviour differs between version 1.0 and version 2.0, the version is stated explicitly.

---

## B.1 XML Syntax

### B.1.1 Document Structure

A well-formed XML document has three parts: an optional XML declaration, an optional prolog (comments, processing instructions, doctype), and exactly one root element.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- optional comment -->
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <!-- content -->
</FundsXML4>
```

The XML declaration is optional but strongly recommended. `version` must be `"1.0"` for FundsXML. `encoding` should be `"UTF-8"` unless you have a specific reason to pick another encoding. A third optional attribute, `standalone="yes"`, declares that the document has no external dependencies; FundsXML does not set it.

### B.1.2 Elements and Attributes

| Form | Syntax |
|---|---|
| Open + close | `<Name>content</Name>` |
| Self-closing (empty) | `<Name/>` |
| With attributes | `<Name attr1="value1" attr2="value2">content</Name>` |
| Empty with attributes | `<Name attr="value"/>` |

Element names are case-sensitive. They must start with a letter or underscore, and may contain letters, digits, hyphens, underscores, and periods. Colons are reserved for namespace prefixes.

Attribute values must always be quoted (single or double quotes, consistently matched). Attributes may not appear more than once on the same element.

### B.1.3 Text Content and Character Escaping

Five characters have special meaning inside XML content and must be escaped:

| Character | Entity | Where required |
|---|---|---|
| `<` | `&lt;` | Always, in element content and attribute values |
| `>` | `&gt;` | Recommended, always safe |
| `&` | `&amp;` | Always, in element content and attribute values |
| `"` | `&quot;` | Inside double-quoted attribute values |
| `'` | `&apos;` | Inside single-quoted attribute values |

Numeric character references are also supported: `&#169;` for © (decimal), `&#xA9;` for © (hex).

**CDATA sections** are an alternative for blocks of text containing many special characters. Everything between `<![CDATA[` and `]]>` is treated literally, with no entity processing. Useful for embedded HTML, code samples, or regular expressions.

```xml
<Description><![CDATA[Returns > 5% if A < B && C]]></Description>
```

### B.1.4 Comments and Processing Instructions

```xml
<!-- a comment, cannot contain -- or end with - -->
<?xml-stylesheet type="text/xsl" href="style.xsl"?>
```

Comments may appear anywhere in the document except inside a tag. Processing instructions are of the form `<?target data?>`; the only one FundsXML practitioners usually encounter is `xml-stylesheet`, which tells a browser to apply an XSLT transformation when rendering.

### B.1.5 Namespaces

A namespace is declared with `xmlns` (default namespace) or `xmlns:prefix` (prefixed namespace), and it scopes the element and attribute names below the declaration to a specific vocabulary identified by a URI.

| Pattern | Meaning |
|---|---|
| `xmlns="URI"` | Elements in scope belong to this default namespace |
| `xmlns:p="URI"` | Prefix `p:` refers to this namespace |
| `xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"` | The XML Schema instance namespace (for `xsi:type`, `xsi:nil`, `xsi:schemaLocation`) |
| `xsi:noNamespaceSchemaLocation="file.xsd"` | Locate the schema when there is no target namespace |
| `xsi:schemaLocation="URI file.xsd"` | Locate the schema for a specific namespace |

**FundsXML is defined without a target namespace** — it uses `xsi:noNamespaceSchemaLocation`, not `xsi:schemaLocation`. This is unusual for a modern XML standard but deliberate: it keeps element names unprefixed and simplifies XPath expressions.

### B.1.6 Well-Formedness Checklist

A document is **well-formed** if and only if:

- Exactly one root element contains all other content.
- Every opening tag has a matching closing tag (or is self-closing).
- Elements are properly nested — no overlapping tags.
- Attribute values are quoted.
- The five special characters are escaped in text content.
- Element and attribute names follow the naming rules.
- Comments and CDATA sections are well-formed.

Well-formedness is a prerequisite for validity. A document can be well-formed without being valid against a schema.

---

## B.2 XPath 1.0 and 2.0

### B.2.1 Location Paths — Abbreviated Syntax

XPath expressions select nodes in a document. The most common are **location paths**: a sequence of steps separated by `/`.

| Syntax | Meaning |
|---|---|
| `/` | Root of the document |
| `/FundsXML4` | Root element (absolute path) |
| `FundsXML4` | Relative path from the context node |
| `/FundsXML4/ControlData` | Child path |
| `//Fund` | All `Fund` elements anywhere in the document |
| `.` | Current context node |
| `..` | Parent of the context node |
| `@LEI` | The `LEI` attribute of the context node |
| `*` | All child elements of the context node |
| `@*` | All attributes of the context node |
| `text()` | Text content of the context node |
| `node()` | Any node (element, text, comment, PI) |

### B.2.2 Axes

XPath supports thirteen **axes** that control the direction of navigation from the context node. The most-used have abbreviated forms; the full axis syntax is `axis::node-test`.

| Axis | Abbreviated | Selects |
|---|---|---|
| `child::` | (default) | Direct children |
| `attribute::` | `@` | Attributes |
| `descendant::` | — | All descendants |
| `descendant-or-self::` | `//` | Descendants and the node itself |
| `parent::` | `..` | The parent |
| `ancestor::` | — | All ancestors |
| `ancestor-or-self::` | — | Ancestors and the node itself |
| `self::` | `.` | The node itself |
| `following-sibling::` | — | Siblings appearing later |
| `preceding-sibling::` | — | Siblings appearing earlier |
| `following::` | — | All later nodes in document order |
| `preceding::` | — | All earlier nodes in document order |
| `namespace::` | — | Namespace nodes (rarely used) |

### B.2.3 Predicates

A **predicate** is a filter expression in square brackets that narrows a node-set.

| Syntax | Meaning |
|---|---|
| `Fund[1]` | The first `Fund` child |
| `Fund[last()]` | The last `Fund` child |
| `Fund[position() = 2]` | The second `Fund` child |
| `Fund[@LEI]` | `Fund` elements that have a `LEI` attribute |
| `Fund[@LEI='549300ABCDEFGHIJ1234']` | `Fund` elements whose `LEI` attribute has that value |
| `Fund[Identifiers/LEI]` | `Fund` elements that contain an `Identifiers/LEI` child |
| `Position[MarketValue > 1000000]` | Positions with market value above one million |
| `Fund[Currency='EUR'][SingleFundFlag='true']` | Multiple predicates are AND-combined |

### B.2.4 Operators

| Category | Operators |
|---|---|
| Comparison | `=`, `!=`, `<`, `<=`, `>`, `>=` |
| Boolean | `and`, `or`, `not()` |
| Arithmetic | `+`, `-`, `*`, `div`, `mod` (note: `/` is path, not division) |
| Node-set | `\|` (union), `intersect`, `except` (XPath 2.0 only) |

In XPath 1.0, comparisons of node-sets are existential: `@x > 5` is true if *any* matching node has a value greater than 5. Be aware of this when writing predicates over collections.

### B.2.5 Core Functions

**Node-set functions:**

| Function | Returns |
|---|---|
| `count(node-set)` | Number of nodes |
| `position()` | Position of context node (1-based) |
| `last()` | Position of the last node in the current context |
| `name()` | Qualified name of the context node |
| `local-name()` | Local name without namespace prefix |
| `namespace-uri()` | Namespace URI of the context node |

**String functions:**

| Function | Returns |
|---|---|
| `string(arg)` | String value of the argument |
| `concat(s1, s2, ...)` | Concatenation |
| `starts-with(s, prefix)` | Boolean |
| `contains(s, substring)` | Boolean |
| `substring(s, start, length)` | Substring (1-based) |
| `substring-before(s, delim)` | Part before the delimiter |
| `substring-after(s, delim)` | Part after the delimiter |
| `string-length(s)` | Character count |
| `normalize-space(s)` | Trims and collapses whitespace |
| `translate(s, from, to)` | Character-by-character substitution |

**Numeric functions:**

| Function | Returns |
|---|---|
| `number(arg)` | Numeric coercion |
| `sum(node-set)` | Sum of numeric values |
| `floor(n)`, `ceiling(n)`, `round(n)` | Rounding |

**Boolean functions:**

| Function | Returns |
|---|---|
| `true()`, `false()` | Boolean constants |
| `not(bool)` | Logical negation |
| `boolean(arg)` | Boolean coercion |

**XPath 2.0 additions** (partial list, for the functions FundsXML practitioners encounter most): `matches(string, regex)` for regular-expression matching; `tokenize(string, regex)` for splitting; `replace(string, regex, replacement)`; `upper-case()`, `lower-case()`; date/time functions `current-date()`, `year-from-date()`, `month-from-date()`, `day-from-date()`; `if (cond) then x else y` conditional expressions; and the `for $var in seq return expr` iteration construct.

### B.2.6 FundsXML XPath Recipes

**Select a fund by LEI:**

```
//Fund[Identifiers/LEI='549300ABCDEFGHIJ1234']
```

**Get the TNAV amount of that fund:**

```
//Fund[Identifiers/LEI='549300ABCDEFGHIJ1234']
      /FundDynamicData/TotalAssetValues/TotalAssetValue/TotalNetAssetValue/Amount
```

**Count all positions across all portfolios of a fund:**

```
count(//Fund[Identifiers/LEI='549300ABCDEFGHIJ1234']//Position)
```

**Sum the market values of all equity positions:**

```
sum(//Position[PositionType='EQUITY']/TotalValue/Amount)
```

**Find all deliveries that are corrections:**

```
/FundsXML4[ControlData/DataOperation='AMEND']
```

**List all ISINs in a portfolio:**

```
//Portfolio/Positions/Position/UniqueID[@IDType='ISIN']
```

**Find funds whose name contains "Europa":**

```
//Fund[contains(Names/OfficialName, 'Europa')]
```

**Select all positions valued above one million euros:**

```
//Position[TotalValue/Amount[@ccy='EUR'] > 1000000]
```

---

## B.3 XSLT 1.0 and 2.0

### B.3.1 Stylesheet Skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <xsl:template match="/">
    <!-- transformation logic -->
  </xsl:template>

</xsl:stylesheet>
```

Change `version="1.0"` to `version="2.0"` to use XSLT 2.0 features (which require an XSLT 2.0 processor such as Saxon). The `xsl:output` element controls serialisation: `method` is `"xml"`, `"html"`, or `"text"`; `indent="yes"` produces human-readable output; `encoding` sets the output encoding.

### B.3.2 Template Matching

```xml
<xsl:template match="pattern">
  <!-- body -->
</xsl:template>
```

| Match pattern | Applies to |
|---|---|
| `"/"` | The document root |
| `"Fund"` | Every `Fund` element |
| `"Fund/Names/OfficialName"` | `OfficialName` elements with that parent chain |
| `"Fund[@LEI]"` | `Fund` elements with a `LEI` attribute |
| `"Position[TotalValue/Amount > 1000000]"` | Positions above one million |
| `"@*"` | Any attribute |
| `"text()"` | Any text node |
| `"node()"` | Any node |

Invocation is either by applying templates (let XSLT dispatch based on `match`) or by calling a named template explicitly:

```xml
<xsl:apply-templates/>                    <!-- apply to all children -->
<xsl:apply-templates select="Funds/Fund"/> <!-- apply to specific nodes -->
<xsl:call-template name="fund-summary"/>   <!-- call a named template -->
```

### B.3.3 Selecting and Copying Values

| Instruction | Purpose |
|---|---|
| `<xsl:value-of select="expr"/>` | Output the string value of an expression |
| `<xsl:copy-of select="expr"/>` | Deep-copy nodes (preserving structure) |
| `<xsl:copy/>` | Shallow-copy the context node (useful in identity transforms) |
| `<xsl:text>literal</xsl:text>` | Output literal text with controlled whitespace |

### B.3.4 Iteration and Conditionals

**Iteration:**

```xml
<xsl:for-each select="//Fund">
  <li><xsl:value-of select="Names/OfficialName"/></li>
</xsl:for-each>
```

**Simple condition:**

```xml
<xsl:if test="Currency='EUR'">
  <p>This is a euro-denominated fund.</p>
</xsl:if>
```

**Multi-branch condition:**

```xml
<xsl:choose>
  <xsl:when test="SingleFundFlag='true'">Standalone fund</xsl:when>
  <xsl:when test="SingleFundFlag='false'">Sub-fund of an umbrella</xsl:when>
  <xsl:otherwise>Unknown structure</xsl:otherwise>
</xsl:choose>
```

Sorting inside an iteration:

```xml
<xsl:for-each select="//Fund">
  <xsl:sort select="Names/OfficialName" order="ascending"/>
  <li><xsl:value-of select="Names/OfficialName"/></li>
</xsl:for-each>
```

### B.3.5 Variables and Parameters

```xml
<xsl:variable name="fund-lei" select="'549300ABCDEFGHIJ1234'"/>
<xsl:variable name="fund-count" select="count(//Fund)"/>

<xsl:param name="report-date" select="'2026-03-31'"/>

<xsl:value-of select="$fund-lei"/>
```

Variables are bound once and cannot be reassigned. Parameters behave like variables but can be passed into templates via `<xsl:with-param name="..." select="..."/>`.

### B.3.6 FundsXML XSLT Recipes

**Recipe 1 — Extract fund NAVs to an HTML table.**

```xml
<xsl:template match="/">
  <html><body>
    <h1>Fund NAV Summary</h1>
    <table border="1">
      <tr><th>Fund</th><th>LEI</th><th>NAV</th><th>Currency</th></tr>
      <xsl:for-each select="//Fund">
        <tr>
          <td><xsl:value-of select="Names/OfficialName"/></td>
          <td><xsl:value-of select="Identifiers/LEI"/></td>
          <td><xsl:value-of select=
            "FundDynamicData/TotalAssetValues/TotalAssetValue
             /TotalNetAssetValue/Amount"/></td>
          <td><xsl:value-of select="Currency"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </body></html>
</xsl:template>
```

**Recipe 2 — Identity transform with one exception (strip [`RegulatoryReportings`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings)).**

```xml
<!-- copy everything by default -->
<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<!-- but drop RegulatoryReportings blocks -->
<xsl:template match="RegulatoryReportings"/>
```

This is the standard pattern for a surgical transformation: a general identity template plus a small number of overriding templates that handle the specific cases you want to change.

**Recipe 3 — Sum all position values in a portfolio.**

```xml
<xsl:template match="Portfolio">
  <p>
    Portfolio total:
    <xsl:value-of select="sum(Positions/Position/TotalValue/Amount)"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="Positions/Position[1]/TotalValue/Amount/@ccy"/>
  </p>
</xsl:template>
```

The `<xsl:text> </xsl:text>` is an explicit single space — whitespace in the stylesheet source is not preserved unless wrapped in `xsl:text`, so forcing a space this way is the reliable idiom.
