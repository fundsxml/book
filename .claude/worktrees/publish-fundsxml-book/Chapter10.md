<img src="FundsXML-Logo.png" alt="FundsXML" width="140">

# Chapter 10 — Validation and Quality Assurance

*Ensuring correct FundsXML files*

---

## 10.1 Setting the Scene: Why Validation Matters

Part II of this book taught the reader to *read and produce* FundsXML documents. Part III, which this chapter opens, is about *running them in production*. The distinction matters: a document that parses cleanly in a text editor is not necessarily a document that will survive a production pipeline. Real deliveries cross network boundaries, pass through multiple systems, and are consumed by consumers whose tolerance for sloppy data ranges from "reject on first error" to "silently ignore and continue". The producer who does not validate every file before emitting it is pushing that tolerance onto someone else.

This chapter treats validation as an engineering discipline rather than an afterthought. It introduces the two-stage validation model that every production FundsXML pipeline should implement, shows how to run the first stage (schema validation) with the free `xmllint` tool and with the four programming languages most commonly found in production pipelines (Python, Java, C# and PowerShell), catalogues the five or six error patterns that account for the overwhelming majority of real-world validation failures, explains why schema validation alone is not enough, introduces Schematron as the standard tool for the second stage (business-rule validation) with runners in each of the same four languages, and assembles a complete validation workflow — in both Bash and PowerShell — that a producer can drop into its delivery pipeline as a gatekeeper. Every command shown in the chapter has been run against real FundsXML files, and every error message has been captured verbatim from the actual tool output.

By the end of this chapter, you should be able to:

- explain the two-stage validation model and name what each stage catches that the other misses;
- run `xmllint --noout --schema FundsXML4.xsd` against any FundsXML file and interpret the results;
- validate a FundsXML file using Python, Java, C# or PowerShell as an alternative to `xmllint`, choosing whichever language matches your production pipeline;
- read an `xmllint` error message and map it to one of the recurring error patterns the chapter catalogues;
- write a Schematron rule that expresses a business constraint the schema cannot enforce;
- compile and execute Schematron rules with the tooling the chapter introduces — in Python, Java, C# or PowerShell;
- assemble a validation gatekeeper script (Bash or PowerShell) that a production pipeline can use to accept or reject every outgoing delivery.

The tools used throughout the chapter are free and ubiquitous. `xmllint` comes with `libxml2` and is installed by default on virtually every Linux distribution, in the macOS developer tools, and in the Windows Subsystem for Linux. The language-specific validators use standard libraries and widely available open-source packages: Python's `lxml`, Java's `javax.xml.validation`, .NET's `System.Xml.Schema`, and PowerShell's access to the same .NET classes. Schematron validation is performed with `lxml.isoschematron` (Python), `ph-schematron` (Java), and the ISO Schematron XSLT stylesheets (C# and PowerShell). Appendix E lists the relevant installation paths for readers on other platforms; Chapter 11 treats the dedicated FundsXML tooling ecosystem (FreeXmlToolkit, Online Schema Viewer, and so on) that some readers may prefer for day-to-day work.

---

## 10.2 The Two-Stage Validation Model

The central architectural claim of this chapter is that every production FundsXML pipeline should validate every outgoing document in **two** distinct stages, using two different technologies, checking two different classes of correctness. Combining them into a single stage is possible but costs the pipeline the ability to give clear diagnostics when things go wrong; skipping either stage entirely is a recurring source of production incidents.

**Stage 1 is schema validation.** The input is the FundsXML file and the XSD schema (`FundsXML4.xsd` plus its included modules). The check is: does the file conform to the *structural* rules that XSD can express? Element names, element order, cardinality (which elements are required, which are optional, which are repeatable), data types (dates must look like dates, numbers must look like numbers, enumerations must take one of their allowed values), attribute types, and the basic hierarchical shape of the document. Stage 1 catches everything that can be expressed in XSD; the pass criterion is binary — the file either conforms or it does not.

**Stage 2 is business-rule validation.** The input is the same FundsXML file, plus a separate rule set written in Schematron (or in an equivalent rule language). The check is: does the file conform to the *semantic* rules that XSD cannot express? "A `DELETE` operation must carry a `RelatedDocumentIDs` pointing at the delivery being retracted." "A share class's `NumberOfShares` must be a positive integer." "The sum of the position market values in a portfolio must equal the fund's `TotalNetAssetValue` within a rounding tolerance." "A `Document` of type `PRIIPS-KID` must reference at least one share class, not a fund-level identifier only." None of these rules can be expressed in XSD, because they depend on comparisons between elements, on arithmetic, or on knowledge of the business domain that the schema language cannot capture.

The two stages are complementary, and each one catches errors that the other cannot see:

- A file with `DataOperation=UPDATE` (an obsolete enum value — see Chapter 4's retroactive correction) fails **Stage 1**: the enumeration rule catches it immediately. Stage 2 would not catch it because Schematron assumes the underlying structure is schema-valid when it runs.
- A file with `DataOperation=DELETE` and no `RelatedDocumentIDs` passes **Stage 1** (the schema allows `RelatedDocumentIDs` as optional even on `DELETE`) but fails **Stage 2** if the producer has written a Schematron rule that enforces the semantic constraint.

The operational implication is that a production pipeline should run Stage 1 *first* — because its failures are easier to interpret and its runtime is faster — and then run Stage 2 only if Stage 1 passed. Running Stage 2 against a structurally broken file produces cascading Schematron errors that are harder to read than the underlying XSD failures. The complete workflow in §10.9 codifies this ordering.

**Figure 10.1 — The two-stage validation pipeline**

```
   FundsXML file
         │
         ▼
   ┌─────────────────┐
   │ Stage 1:        │    ── FAIL ──▶ Report XSD errors, stop
   │ xmllint --schema│                (structural problem,
   │ (XSD)           │                 see §10.4 for reading)
   └─────────────────┘
         │ PASS
         ▼
   ┌─────────────────┐
   │ Stage 2:        │    ── FAIL ──▶ Report business errors, stop
   │ Schematron      │                (semantic problem,
   │ (business rules)│                 see §10.8 for rule catalogue)
   └─────────────────┘
         │ PASS
         ▼
   Delivery accepted; safe to emit
```

---

## 10.3 Schema Validation with xmllint

`xmllint` is the command-line XML tool that ships with `libxml2`, the XML library underlying a significant fraction of the open-source XML ecosystem. It can parse, format, query with XPath, and — critically for this chapter — validate XML documents against an XSD schema. For FundsXML it is the default Stage 1 tool because it is free, widely installed, well-documented, and quick; the single command required for validation is short enough to embed in shell scripts, Makefiles, and CI pipelines without overhead.

The command that validates a FundsXML document against the schema is:

```
xmllint --noout --schema FundsXML4.xsd delivery.xml
```

The flags decompose as follows. `--schema FundsXML4.xsd` tells `xmllint` to validate against the named XSD file; it accepts a path, either relative to the current working directory or absolute. `--noout` suppresses the normal output of `xmllint` (which would otherwise dump the parsed document to standard output after validation); since we are interested only in the pass/fail result and any error messages, `--noout` keeps the terminal clean. The positional argument is the FundsXML file to validate.

On success, `xmllint` prints a single line to standard output:

```
delivery.xml validates
```

and exits with code `0`. On failure, it prints one or more error messages to standard error — each one naming the offending line and the nature of the violation — followed by a final line:

```
delivery.xml fails to validate
```

and exits with code `3` (the `libxml2` convention for schema-validation failures; other non-zero exit codes indicate different categories of error, such as missing files or malformed XML). A CI pipeline or shell script can branch on the exit code to decide whether to proceed.

A few practical notes before the error catalogue in §10.4.

**Schema location.** The command above assumes that `FundsXML4.xsd` is in the current working directory. In production, the schema is almost always stored elsewhere — a shared schema directory, a container volume, a URL — and the command needs to point at it explicitly with a path. An equivalent invocation using an absolute path:

```
xmllint --noout --schema /opt/fundsxml/4.2.8/FundsXML4.xsd delivery.xml
```

**Included schemas.** `FundsXML4.xsd` imports `xmldsig-core-schema.xsd` for the digital-signature element (§9.3). The imported file must be reachable from the main schema file — usually by being in the same directory, because the `import` in the XSD uses a relative path. A pipeline that copies `FundsXML4.xsd` without also copying `xmldsig-core-schema.xsd` will produce a confusing "cannot locate schema" error on any file that uses `ds:Signature`, even though the file itself appears complete.

**Validation speed.** `xmllint` parses and validates at roughly 50 to 200 megabytes per second on a modern workstation, depending on the document's structural complexity. A typical month-end FundsXML delivery — 5 to 20 megabytes for a mid-sized asset manager — validates in well under one second. The performance is not usually a constraint; the failure diagnostics are the interesting part.

**Alternative tools.** Other validators exist: Apache Xerces (via the Java command-line `xmlvalidator`), Oracle's XDK, .NET's `XmlReader` with `XmlReaderSettings.Schemas`, Python's `lxml`, Go's `encoding/xml`. All of them validate against the same XSD and should produce equivalent pass/fail results, though their error messages vary. §10.5 presents complete validation scripts in each of the four most common production languages so that the reader can choose the tool that fits their pipeline.

---

## 10.4 Reading xmllint Error Messages — A Catalogue

Five classes of error account for the overwhelming majority of real-world FundsXML validation failures. This section walks through each class with a captured `xmllint` error message, an explanation of what the message means, and the fix. Every error shown in this section was produced by a real `xmllint` run against a real (deliberately broken) FundsXML file, and the output is reproduced verbatim.

### 10.4.1 Invalid Enumeration Value

A producer emits a file with `DataOperation=UPDATE`, a value that was legal in some older conventions (and appeared in early drafts of this book) but that is not in the current FundsXML 4.2.8 enumeration. The schema defines [`DataOperation`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataOperation) as an enumerated field with exactly three values: `INITIAL`, `AMEND`, `DELETE`. Running `xmllint` against the file produces:

```
bad-enum.xml:15: element DataOperation: Schemas validity error :
  Element 'DataOperation': [facet 'enumeration'] The value 'UPDATE' is
  not an element of the set {'INITIAL', 'AMEND', 'DELETE'}.
bad-enum.xml fails to validate
```

The message is unusually clear: it names the offending element, the exact line in the file, the nature of the constraint (`facet 'enumeration'`), the rejected value, and the full list of allowed values. A reader new to `xmllint` might expect every error message to be this helpful; most of them are.

The fix is to replace the enum value. In this case, `UPDATE` should become `AMEND`, following the correction that Chapter 4 was retroactively updated for. A producer pipeline that has shipped files with `UPDATE` in the past also needs to audit any downstream consumer that has been treating the invalid value permissively — production systems that silently coerce unknown enum values to a default (a bad practice, but a common one) may be silently misclassifying deliveries.

### 10.4.2 Wrong Element Order

The XSD `sequence` compositor requires children to appear in a specific order. [`ControlData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData), for example, must have `UniqueDocumentID`, then `DocumentGenerated`, then optionally `Version`, then `ContentDate`, then `DataSupplier`, then further elements — in exactly that sequence. A producer who writes `ContentDate` before `DocumentGenerated` violates the order, even though both elements are present and the data is correct. Running `xmllint`:

```
bad-order.xml:6: element ContentDate: Schemas validity error :
  Element 'ContentDate': This element is not expected.
  Expected is ( DocumentGenerated ).
bad-order.xml fails to validate
```

The message "This element is not expected. Expected is (DocumentGenerated)" is the canonical `xmllint` wording for an order violation. The word *expected* is deliberately precise: the validator was halfway through parsing the `ControlData` sequence, had just finished `UniqueDocumentID`, and was looking for the next element in the sequence — which should have been `DocumentGenerated`. Instead it found `ContentDate`, an element that legally belongs later in the sequence but not yet.

The fix is to reorder the elements to match the XSD's declared sequence. The schema itself is the authoritative source; Appendix C's XSD quick reference lists the sequence for every major type.

### 10.4.3 Missing Required Child

The XSD distinguishes required children (those with no `minOccurs` attribute, or `minOccurs="1"`) from optional ones (`minOccurs="0"`). A producer who omits a required child — because they thought it was optional, or because their generator had a bug — produces a file that `xmllint` rejects with a "Missing child element(s)" message. A [`DataSupplier`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataSupplier) block, for example, requires a `Type` element. Omit it and you get:

```
bad-missing.xml:9: element DataSupplier: Schemas validity error :
  Element 'DataSupplier': Missing child element(s). Expected is ( Type ).
bad-missing.xml fails to validate
```

The "Expected is (Type)" tells the reader exactly which required child was missing. When several children are missing, `xmllint` reports the *first* missing one it encounters rather than enumerating all of them; fixing that one and re-running the validation often reveals further missing children in subsequent runs. The iteration is mildly annoying but not difficult.

### 10.4.4 Invalid Type

XSD types enforce lexical constraints on the values of elements. A field declared as `xs:date` must carry a value that looks like `2026-03-31` (ISO 8601 date format); `xs:dateTime` requires a value like `2026-04-01T06:47:13Z`; `xs:integer` requires a string of digits; `xs:boolean` requires one of `true`, `false`, `1`, or `0`. A producer who writes a date in a local format — say, `31/03/2026` — breaks the type constraint:

```
bad-type.xml:8: element ContentDate: Schemas validity error :
  Element 'ContentDate': '31/03/2026' is not a valid value of the
  atomic type 'xs:date'.
bad-type.xml fails to validate
```

The fix is to convert the value to the expected ISO format. This error is particularly common in producers that have been built around European-locale date-picker libraries (which default to `DD/MM/YYYY`) without explicit format conversion at the XML-serialisation step. The producer's output layer should always emit ISO dates regardless of the system's display locale.

### 10.4.5 Unknown Element

The complement of the "wrong order" and "missing child" errors is the "unknown element" error: a producer emits an element that is not declared in the schema at all, at a position where the schema does not expect any element (or, more commonly, any element with that name). This is the error that revealed the `DataSupplier/LEI` inaccuracy in earlier drafts of this book. A producer who writes an `LEI` child inside `DataSupplier` — following the natural assumption that every organisation has an LEI — sees:

```
bad-unknown.xml:14: element LEI: Schemas validity error :
  Element 'LEI': This element is not expected. Expected is ( Contact ).
bad-unknown.xml fails to validate
```

The surprise here is that `DataSupplierType` in the FundsXML 4.2.8 schema has no `LEI` field at all. The `SystemCountry`, `Short`, `Name`, `Type`, and optional `Contact` children are the only ones it accepts. A producer who wants to convey the supplier's LEI has to put it somewhere else — typically through `CustomAttributes` (Chapter 9.4), or through the supplier's `Short` code if the code is in a format that includes the LEI by convention. The lesson is general: *read the schema before assuming what fields exist*, because some fields that feel natural are not actually in the standard.

### 10.4.6 What xmllint Does Not Catch

`xmllint` catches everything that XSD can express, which is a lot but not everything. Specifically, it does not check:

- Whether a `UniqueDocumentID` is actually unique across a producer's output stream (a cross-file semantic property).
- Whether the sum of portfolio market values matches the fund's total net assets within a tolerance (an arithmetic cross-element property).
- Whether a `DELETE` operation carries the `RelatedDocumentIDs` that the FundsXML documentation recommends (a conditional semantic rule; the schema leaves it optional).
- Whether a `Document` of type `PRIIPS-KID` actually points at an existing share class (a cross-reference property).
- Whether the PAI values in an EET block are consistent with the portfolio composition (a cross-module property).

None of these are XSD-expressible, and none of them are `xmllint`'s fault to miss. They are the subject of Stage 2, which the rest of this chapter develops.

---

## 10.5 Schema Validation in Python, Java, C# and PowerShell

While `xmllint` is the reference tool for XSD validation and the one this book recommends for interactive use, production pipelines are often built in general-purpose programming languages. A Java pipeline wants a Java validator; a .NET pipeline wants a C# validator; a Windows operations team wants a PowerShell script. This section presents a complete XSD validation script in each of the four most common production languages. Every script follows the same pattern as the `xmllint` command: it takes a schema path and a file path, reports errors with line numbers, and exits with a non-zero code on failure. Each script can be invoked directly from the command line — as a drop-in replacement for `xmllint` in the validation step — or imported as a module into a larger application.

**Table 10.1 — Schema validation commands at a glance**

| Tool       | Command                                                                  |
|------------|--------------------------------------------------------------------------|
| xmllint    | `xmllint --noout --schema FundsXML4.xsd delivery.xml`                   |
| Python     | `python3 validate-xsd.py FundsXML4.xsd delivery.xml`                    |
| Java       | `java ValidateXsd FundsXML4.xsd delivery.xml`                           |
| C#         | `dotnet run -- FundsXML4.xsd delivery.xml`                              |
| PowerShell | `.\Validate-XsdSchema.ps1 -SchemaPath FundsXML4.xsd -XmlPath delivery.xml` |

### 10.5.1 Python (lxml)

Python's `lxml` library wraps `libxml2` — the same library behind `xmllint` — in a Pythonic API. Schema validation is a two-step process: parse the XSD into an `XMLSchema` object, then call `validate()` on the target document. Errors are available in the schema's `error_log`, with line numbers and messages that closely mirror `xmllint`'s output.

```python
#!/usr/bin/env python3
"""validate-xsd.py — XSD schema validation for FundsXML files."""
import sys
from lxml import etree

if len(sys.argv) != 3:
    print("usage: validate-xsd.py <schema.xsd> <file.xml>", file=sys.stderr)
    sys.exit(2)

schema_path, xml_path = sys.argv[1], sys.argv[2]

schema_doc = etree.parse(schema_path)
schema = etree.XMLSchema(schema_doc)
doc = etree.parse(xml_path)

if schema.validate(doc):
    print(f"{xml_path} validates")
    sys.exit(0)

for error in schema.error_log:
    print(f"  line {error.line}: {error.message}")
print(f"{xml_path} fails to validate")
sys.exit(1)
```

The script is self-contained and can be run from the command line with `python3 validate-xsd.py FundsXML4.xsd delivery.xml`. The prerequisite is `lxml`, which is installed via `pip install lxml` (or `apt install python3-lxml` on Debian/Ubuntu).

To use the same logic in a larger application — say, a Django-based upload portal that validates incoming FundsXML deliveries — extract the core into a function:

```python
def validate_xsd(schema_path: str, xml_path: str) -> list[str]:
    """Return a list of error messages, empty on success."""
    schema = etree.XMLSchema(etree.parse(schema_path))
    doc = etree.parse(xml_path)
    schema.validate(doc)
    return [str(e) for e in schema.error_log]
```

### 10.5.2 Java (javax.xml.validation)

Java's standard library includes a full XSD validation API in the `javax.xml.validation` package, available in every JDK since Java 5. No third-party dependency is required. The validator is built from a `SchemaFactory`, which parses the XSD into a `Schema` object, and a `Validator`, which checks the target document against the schema. Errors are reported through an `ErrorHandler` callback.

```java
// ValidateXsd.java — XSD schema validation for FundsXML files
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class ValidateXsd {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("usage: java ValidateXsd <schema.xsd> <file.xml>");
            System.exit(2);
        }
        try {
            SchemaFactory factory = SchemaFactory.newInstance(
                XMLConstants.W3C_XML_SCHEMA_NS_URI);
            Schema schema = factory.newSchema(new File(args[0]));
            Validator validator = schema.newValidator();

            List<String> errors = new ArrayList<>();
            validator.setErrorHandler(new ErrorHandler() {
                @Override
                public void warning(SAXParseException e) { }
                @Override
                public void error(SAXParseException e) {
                    errors.add("line " + e.getLineNumber()
                        + ": " + e.getMessage());
                }
                @Override
                public void fatalError(SAXParseException e) {
                    errors.add("line " + e.getLineNumber()
                        + ": " + e.getMessage());
                }
            });

            validator.validate(new StreamSource(new File(args[1])));

            if (errors.isEmpty()) {
                System.out.println(args[1] + " validates");
            } else {
                for (String err : errors) {
                    System.out.println("  " + err);
                }
                System.out.println(args[1] + " fails to validate");
                System.exit(1);
            }
        } catch (Exception e) {
            System.err.println("error: " + e.getMessage());
            System.exit(2);
        }
    }
}
```

Compile and run with:

```
javac ValidateXsd.java
java ValidateXsd FundsXML4.xsd delivery.xml
```

No external library is needed — the JDK's built-in Xerces implementation handles the XSD parsing and validation. For larger applications, extract the validation logic into a utility method that returns the list of errors, and call it from wherever the pipeline needs a Stage 1 check.

### 10.5.3 C# (.NET)

.NET provides XSD validation through the `System.Xml.Schema` namespace. The pattern mirrors the Java approach: load the schema into an `XmlSchemaSet`, configure an `XmlReaderSettings` with that schema set and a `ValidationType` of `Schema`, then read the document through the validating reader. Errors are reported through the `ValidationEventHandler` delegate.

```csharp
// ValidateXsd.cs — XSD schema validation for FundsXML files
using System;
using System.Collections.Generic;
using System.Xml;
using System.Xml.Schema;

class ValidateXsd
{
    static int Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.Error.WriteLine(
                "usage: ValidateXsd <schema.xsd> <file.xml>");
            return 2;
        }

        var schemas = new XmlSchemaSet();
        schemas.Add(null, args[0]);

        var settings = new XmlReaderSettings
        {
            Schemas = schemas,
            ValidationType = ValidationType.Schema
        };

        var errors = new List<string>();
        settings.ValidationEventHandler += (sender, e) =>
            errors.Add($"line {e.Exception.LineNumber}: {e.Message}");

        using (var reader = XmlReader.Create(args[1], settings))
        {
            while (reader.Read()) { }
        }

        if (errors.Count == 0)
        {
            Console.WriteLine($"{args[1]} validates");
            return 0;
        }
        foreach (var err in errors)
            Console.WriteLine($"  {err}");
        Console.WriteLine($"{args[1]} fails to validate");
        return 1;
    }
}
```

To compile and run as a standalone console application:

```
dotnet new console -n ValidateXsd
# replace Program.cs with the code above
dotnet run --project ValidateXsd -- FundsXML4.xsd delivery.xml
```

No NuGet package is needed — `System.Xml` ships with every .NET installation. For integration into a larger application (an ASP.NET Core service, a WPF desktop tool), the same `XmlSchemaSet`/`XmlReaderSettings` pattern works as a library call.

### 10.5.4 PowerShell

PowerShell has native access to the .NET `System.Xml` classes, so XSD validation requires no external module. The script below uses the same `XmlSchemaSet` and `XmlReaderSettings` pattern as the C# example, wrapped in PowerShell syntax. It is the natural choice for Windows operations teams and for pipelines orchestrated with PowerShell scripts.

```powershell
# Validate-XsdSchema.ps1 — XSD schema validation for FundsXML files
# Usage: .\Validate-XsdSchema.ps1 -SchemaPath FundsXML4.xsd -XmlPath delivery.xml
param(
    [Parameter(Mandatory)][string]$SchemaPath,
    [Parameter(Mandatory)][string]$XmlPath
)

$schemaSet = New-Object System.Xml.Schema.XmlSchemaSet
$schemaSet.Add($null, (Resolve-Path $SchemaPath).Path) | Out-Null

$settings = New-Object System.Xml.XmlReaderSettings
$settings.Schemas = $schemaSet
$settings.ValidationType = [System.Xml.ValidationType]::Schema

$script:errors = @()
$handler = [System.Xml.Schema.ValidationEventHandler]{
    param($sender, $e)
    $script:errors += "line $($e.Exception.LineNumber): $($e.Message)"
}
$settings.add_ValidationEventHandler($handler)

$reader = [System.Xml.XmlReader]::Create(
    (Resolve-Path $XmlPath).Path, $settings)
try {
    while ($reader.Read()) { }
}
finally {
    $reader.Close()
}

if ($errors.Count -eq 0) {
    Write-Output "$XmlPath validates"
    exit 0
}
foreach ($err in $errors) {
    Write-Output "  $err"
}
Write-Output "$XmlPath fails to validate"
exit 1
```

Run it from a PowerShell prompt (or from a Windows Terminal session) with:

```powershell
.\Validate-XsdSchema.ps1 -SchemaPath FundsXML4.xsd -XmlPath delivery.xml
```

The exit code convention follows `xmllint`: `0` for success, `1` for validation failure, `2` for usage errors. A CI/CD pipeline running on Windows (Azure DevOps, GitHub Actions with a `windows-latest` runner) can use the exit code to gate subsequent steps.

**A note on choosing.** All five tools — `xmllint`, Python, Java, C#, PowerShell — validate against the same XSD and will produce the same pass/fail verdict on any given file. The error messages differ in wording but describe the same underlying violations. Choose the tool that matches the language of your pipeline: a Python ETL job should use `lxml`, a Java microservice should use `javax.xml.validation`, a .NET data hub should use `System.Xml.Schema`, and a Windows operations script should use PowerShell. There is no correctness advantage to any of them over the others.

---

## 10.6 Business Validation: Where Schema Ends

The limits of Stage 1 are the boundaries of what XSD can express. Those boundaries are well-defined — XSD is a formal specification, and the set of constraints it can enforce is known precisely — but they leave out whole categories of correctness that matter in production. Business validation is the discipline of closing the gap.

Three broad classes of rule live outside XSD's reach.

**Class 1: Conditional presence rules.** "If X is set, Y must also be set." The schema can express required-versus-optional as a fixed property of an element, but it cannot say "this element is required when some *other* element takes a specific value". The `DataOperation` example from §10.4.6 is the classic case: the enum has three values, and for one of them (`DELETE`) the documentation recommends that `RelatedDocumentIDs` be present. The schema allows `RelatedDocumentIDs` as optional for all three values. Enforcing the conditional rule requires a separate language.

**Class 2: Cross-element arithmetic.** "The sum of children must equal a parent figure, or must match to within a tolerance." The fund's portfolio has individual position market values, and the fund also has a `TotalNetAssetValue`. In a well-built delivery, the sum of the positions (after currency conversion) should equal the total net assets; a mismatch suggests a data quality problem. XSD cannot express arithmetic over element values; it treats each element as an independent value with its own lexical constraints.

**Class 3: Cross-reference integrity.** "This identifier must point at a record that exists elsewhere in the file." A portfolio position references an [`AssetMasterData`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData) entry through a `UniqueID`; the entry must exist for the reference to be meaningful. A `Document` references a share class through an `ISIN`; the share class must be one that the fund actually has. XSD has a limited facility for this through `xs:key` and `xs:keyref`, and the FundsXML schema uses it for a few specific cases (we saw one in Chapter 5 — the benchmark ID link between static and dynamic data), but the general case is beyond what XSD can express.

The standard tool for expressing all three classes of rule — together with many others — is **Schematron**, a rule language designed specifically for business validation of XML documents. §10.7 introduces the language; §10.8 shows a library of concrete rules for FundsXML.

---

## 10.7 Schematron as a Business-Rule Language

Schematron is an ISO/IEC standard (ISO/IEC 19757-3:2016) for rule-based XML validation. Its design is deliberately simple: a Schematron file is an XML document that contains a set of **rules**, each of which names a **context** (an XPath expression identifying the elements the rule applies to) and a set of **assertions** (further XPath expressions that must evaluate to true when the rule fires). If any assertion fails, Schematron reports the failure together with a human-readable message that the rule author supplied.

The approach is complementary to XSD's structural approach. XSD describes what a valid document *looks like*; Schematron describes what a valid document *satisfies*. Both approaches are necessary, because they catch different kinds of error, and neither can substitute for the other. A Schematron rule running against a structurally broken document produces confusing errors (because the document does not have the shape the XPath expressions assume); an XSD-only pipeline misses all of the semantic rules that XSD cannot express.

### 10.7.1 The Structure of a Schematron File

A minimal Schematron file has three levels of nesting:

- A top-level `<sch:schema>` element, containing
- one or more `<sch:pattern>` elements (logical groupings of related rules), each containing
- one or more `<sch:rule>` elements, each of which has a `context` attribute and one or more `<sch:assert>` children.

A single rule looks like this:

```xml
<sch:rule context="ControlData">
  <sch:assert test="DataOperation != 'DELETE' or RelatedDocumentIDs">
    A DELETE operation must name the delivery being retracted in
    RelatedDocumentIDs. Delivery <sch:value-of select="UniqueDocumentID"/>
    violates this rule.
  </sch:assert>
</sch:rule>
```

The `context="ControlData"` attribute tells Schematron: "for every `ControlData` element anywhere in the document, run the assertions inside this rule." The `test` attribute of `<sch:assert>` is an XPath expression that must evaluate to `true` for the assertion to pass. If the expression evaluates to `false`, Schematron reports the contained text as a failure message, substituting any `<sch:value-of>` elements with the corresponding XPath values from the document.

The rule above reads informally: *for each `ControlData`, either the `DataOperation` is not `DELETE`, or a `RelatedDocumentIDs` sibling element exists.* This is the logically equivalent rewriting of "if `DataOperation` is `DELETE`, then `RelatedDocumentIDs` must be present"; the disjunction form is how conditional rules are typically expressed in Schematron, because the XPath language does not have a direct "if-then" operator at the predicate level.

### 10.7.2 Running Schematron with Python

Schematron rules are not executed directly. The canonical execution model is to **compile** the Schematron file into an XSLT stylesheet, then apply the stylesheet to the target XML document. The output is an SVRL (Schematron Validation Report Language) document listing each failed assertion with its location and message. This two-step pipeline — Schematron compilation followed by XSLT execution — is standardised, portable, and supported by every major XML toolchain.

For Python, we use **`lxml.isoschematron`**, which wraps the compilation and execution in a single API call. The module is free, widely installed, and produces results equivalent to any XSLT-based Schematron processor. A minimal runner script:

```python
#!/usr/bin/env python3
"""run-schematron.py — Run ISO Schematron rules against a FundsXML file."""
import sys
from lxml import etree
from lxml.isoschematron import Schematron

if len(sys.argv) != 3:
    print("usage: run-schematron.py <rules.sch> <file.xml>", file=sys.stderr)
    sys.exit(2)

rules_path, xml_path = sys.argv[1], sys.argv[2]

rules_doc = etree.parse(rules_path)
schematron = Schematron(rules_doc, store_report=True)

xml_doc = etree.parse(xml_path)
ok = schematron.validate(xml_doc)

report = schematron.validation_report
failed_asserts = report.findall(
    ".//{http://purl.oclc.org/dsdl/svrl}failed-assert"
)

if ok and not failed_asserts:
    print(f"{xml_path}: Schematron validation passed")
    sys.exit(0)

print(f"{xml_path}: Schematron validation FAILED")
for fa in failed_asserts:
    loc = fa.get("location", "?")
    text_node = fa.find("{http://purl.oclc.org/dsdl/svrl}text")
    msg = " ".join(text_node.text.split()) if text_node is not None else "(no message)"
    print(f"  at {loc}")
    print(f"    {msg}")
sys.exit(1)
```

The script reads a Schematron rule file and an XML document from the command line, compiles the rules, runs them against the document, and prints either a success line or a list of failed assertions with their locations and messages. Exit code `0` signals success, `1` signals business-rule failures, `2` signals argument errors. Production pipelines can use this exit code exactly as they use `xmllint`'s exit code to decide whether to proceed.

A note on the query binding. Schematron supports several XPath versions through its `queryBinding` attribute on the `<sch:schema>` element; the two we care about are `xslt` (XSLT 1.0, which means XPath 1.0) and `xslt2` (XSLT 2.0, which means XPath 2.0 and a richer expression language). `lxml.isoschematron` supports only the default `xslt` binding, so the rules in this chapter are written in XPath 1.0. This is occasionally awkward — XPath 1.0 has no sequence literals, for example, so a membership test must be written as a `contains()` expression over a space-separated string — but is otherwise adequate for the rules most producers need. Readers who prefer XPath 2.0 can substitute an XSLT-2.0-capable processor such as Saxon, at the cost of a heavier dependency.

### 10.7.3 Running Schematron with Java

Java's most widely used Schematron library is **ph-schematron** by Philip Helger, the same library that powers Schematron validation in the European e-invoicing (EN 16931) ecosystem. It provides a pure-Java implementation that compiles and executes Schematron rules without an external XSLT processor, producing SVRL output through a clean API. The library is available as a Maven dependency:

```xml
<dependency>
    <groupId>com.helger.schematron</groupId>
    <artifactId>ph-schematron-pure</artifactId>
    <version>8.0.2</version><!-- check for latest release -->
</dependency>
```

A minimal runner:

```java
// ValidateSchematron.java — Schematron validation using ph-schematron
import com.helger.schematron.pure.SchematronResourcePure;
import com.helger.schematron.svrl.SVRLHelper;
import com.helger.schematron.svrl.SVRLFailedAssert;
import com.helger.schematron.svrl.jaxb.SchematronOutputType;
import javax.xml.transform.stream.StreamSource;
import java.io.File;
import java.util.List;

public class ValidateSchematron {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println(
                "usage: java ValidateSchematron <rules.sch> <file.xml>");
            System.exit(2);
        }

        SchematronResourcePure sch =
            SchematronResourcePure.fromFile(args[0]);
        if (!sch.isValidSchematron()) {
            System.err.println("Invalid Schematron file: " + args[0]);
            System.exit(2);
        }

        SchematronOutputType svrl =
            sch.applySchematronValidationToSVRL(
                new StreamSource(new File(args[1])));
        List<SVRLFailedAssert> failures =
            SVRLHelper.getAllFailedAssertions(svrl);

        if (failures.isEmpty()) {
            System.out.println(
                args[1] + ": Schematron validation passed");
        } else {
            System.out.println(
                args[1] + ": Schematron validation FAILED");
            for (SVRLFailedAssert fa : failures) {
                System.out.println("  at " + fa.getLocation());
                System.out.println("    " + fa.getText());
            }
            System.exit(1);
        }
    }
}
```

Build and run via Maven (or Gradle):

```
mvn compile exec:java \
    -Dexec.mainClass="ValidateSchematron" \
    -Dexec.args="egf-rules.sch delivery.xml"
```

The `SchematronResourcePure` class handles both the compilation (Schematron to an internal rule model) and the execution (evaluation against the target document) in a single `applySchematronValidationToSVRL` call. The `SVRLHelper.getAllFailedAssertions()` method extracts failed assertions from the SVRL output, each carrying a location string and a human-readable text message — the same information the Python runner prints.

For larger applications (a Spring Boot microservice, a Kafka consumer), extract the validation into a service method that returns the list of `SVRLFailedAssert` objects, and let the caller decide how to format the results.

### 10.7.4 Running Schematron with C# and PowerShell

The .NET ecosystem has no single dominant Schematron library comparable to Python's `lxml.isoschematron` or Java's `ph-schematron`. The standard approach is to use the **ISO Schematron XSLT stylesheets** — the reference implementation maintained at `github.com/Schematron/schematron` — to compile a `.sch` file into an XSLT stylesheet, then apply that stylesheet to the target document using .NET's built-in `XslCompiledTransform`. The result is an SVRL document that the code parses for failed assertions.

The process has two steps:

1. **Compile:** transform the `.sch` file using `iso_svrl_for_xslt1.xsl` → produces a validation XSLT.
2. **Validate:** apply the validation XSLT to the target XML → produces an SVRL report.

For simple Schematron files (no abstract patterns, no includes — like the rule file in §10.8), the single `iso_svrl_for_xslt1.xsl` stylesheet suffices. Complex Schematron files that use abstract patterns or `sch:include` require two preliminary steps (`iso_dsdl_include.xsl` and `iso_abstract_expand.xsl`); the ISO repository documents the full pipeline.

**C# implementation:**

```csharp
// ValidateSchematron.cs — Schematron validation via ISO XSLT stylesheets
using System;
using System.IO;
using System.Xml;
using System.Xml.Xsl;
using System.Xml.XPath;

class ValidateSchematron
{
    static int Main(string[] args)
    {
        if (args.Length < 2 || args.Length > 3)
        {
            Console.Error.WriteLine(
                "usage: ValidateSchematron <rules.sch> <file.xml>"
                + " [iso-xslt-dir]");
            return 2;
        }
        string schPath = args[0], xmlPath = args[1];
        string isoDir = args.Length == 3 ? args[2] : ".";

        // Step 1: compile Schematron rules to XSLT
        string isoXslt = Path.Combine(isoDir,
            "iso_svrl_for_xslt1.xsl");
        var compiler = new XslCompiledTransform();
        compiler.Load(isoXslt);

        var compiledStream = new MemoryStream();
        using (var schReader = XmlReader.Create(schPath))
        using (var writer = XmlWriter.Create(compiledStream))
            compiler.Transform(schReader, writer);
        compiledStream.Position = 0;

        // Step 2: apply compiled XSLT to the target document
        var validator = new XslCompiledTransform();
        using (var xslReader = XmlReader.Create(compiledStream))
            validator.Load(xslReader);

        var svrlStream = new MemoryStream();
        using (var xmlReader = XmlReader.Create(xmlPath))
        using (var writer = XmlWriter.Create(svrlStream))
            validator.Transform(xmlReader, writer);
        svrlStream.Position = 0;

        // Step 3: parse SVRL for failed assertions
        var nav = new XPathDocument(svrlStream)
            .CreateNavigator();
        var mgr = new XmlNamespaceManager(nav.NameTable);
        mgr.AddNamespace("svrl",
            "http://purl.oclc.org/dsdl/svrl");

        var fails = nav.Select(
            "//svrl:failed-assert", mgr);
        if (fails.Count == 0)
        {
            Console.WriteLine(
                $"{xmlPath}: Schematron validation passed");
            return 0;
        }
        Console.WriteLine(
            $"{xmlPath}: Schematron validation FAILED");
        while (fails.MoveNext())
        {
            string loc = fails.Current
                .GetAttribute("location", "");
            var text = fails.Current
                .SelectSingleNode("svrl:text", mgr);
            string msg = text?.Value?.Trim()
                ?? "(no message)";
            Console.WriteLine($"  at {loc}");
            Console.WriteLine($"    {msg}");
        }
        return 1;
    }
}
```

**PowerShell implementation:**

The same three-step pipeline, using PowerShell's access to the .NET XML and XSLT classes:

```powershell
# Validate-Schematron.ps1 — Schematron validation via ISO XSLT stylesheets
# Usage: .\Validate-Schematron.ps1 -RulesPath egf-rules.sch -XmlPath delivery.xml
param(
    [Parameter(Mandatory)][string]$RulesPath,
    [Parameter(Mandatory)][string]$XmlPath,
    [string]$IsoXsltDir = "."
)

$ErrorActionPreference = "Stop"

# Step 1: compile Schematron rules to XSLT
$isoXslt = Join-Path $IsoXsltDir "iso_svrl_for_xslt1.xsl"
$compiler = New-Object System.Xml.Xsl.XslCompiledTransform
$compiler.Load($isoXslt)

$compiledStream = New-Object System.IO.MemoryStream
$schReader = [System.Xml.XmlReader]::Create(
    (Resolve-Path $RulesPath).Path)
$writer = [System.Xml.XmlWriter]::Create($compiledStream)
try { $compiler.Transform($schReader, $writer) }
finally { $writer.Close(); $schReader.Close() }
$compiledStream.Position = 0

# Step 2: apply compiled XSLT to the target document
$validator = New-Object System.Xml.Xsl.XslCompiledTransform
$xslReader = [System.Xml.XmlReader]::Create($compiledStream)
try { $validator.Load($xslReader) }
finally { $xslReader.Close() }

$svrlStream = New-Object System.IO.MemoryStream
$xmlReader = [System.Xml.XmlReader]::Create(
    (Resolve-Path $XmlPath).Path)
$svrlWriter = [System.Xml.XmlWriter]::Create($svrlStream)
try { $validator.Transform($xmlReader, $svrlWriter) }
finally { $svrlWriter.Close(); $xmlReader.Close() }
$svrlStream.Position = 0

# Step 3: parse SVRL for failed assertions
$doc = New-Object System.Xml.XPath.XPathDocument($svrlStream)
$nav = $doc.CreateNavigator()
$mgr = New-Object System.Xml.XmlNamespaceManager($nav.NameTable)
$mgr.AddNamespace("svrl", "http://purl.oclc.org/dsdl/svrl")

$fails = $nav.Select("//svrl:failed-assert", $mgr)
if ($fails.Count -eq 0) {
    Write-Output "${XmlPath}: Schematron validation passed"
    exit 0
}
Write-Output "${XmlPath}: Schematron validation FAILED"
while ($fails.MoveNext()) {
    $loc = $fails.Current.GetAttribute("location", "")
    $textNode = $fails.Current.SelectSingleNode("svrl:text", $mgr)
    $msg = if ($textNode) { $textNode.Value.Trim() } else { "(no message)" }
    Write-Output "  at $loc"
    Write-Output "    $msg"
}
exit 1
```

**Table 10.2 — Schematron validation commands at a glance**

| Language   | Command                                                                     |
|------------|-----------------------------------------------------------------------------|
| Python     | `python3 run-schematron.py egf-rules.sch delivery.xml`                      |
| Java       | `java ValidateSchematron egf-rules.sch delivery.xml`                        |
| C#         | `dotnet run -- egf-rules.sch delivery.xml`                                  |
| PowerShell | `.\Validate-Schematron.ps1 -RulesPath egf-rules.sch -XmlPath delivery.xml`  |

The C# and PowerShell implementations require one external file — `iso_svrl_for_xslt1.xsl` from the ISO Schematron reference implementation — which is a small (roughly 70 KB), stable, freely available XSLT stylesheet that rarely changes between ISO revisions. Download it once, place it alongside the rule file, and point the script at its directory. In a production deployment, the stylesheet and the compiled Schematron XSLT can be cached so that the compilation step runs only when the rule file changes.

---

## 10.8 A Library of Business Rules for FundsXML

This section presents a small but realistic library of Schematron rules that a production FundsXML pipeline might enforce before emitting a delivery. Every rule has been tested against real FundsXML files using the runner from §10.7.2, and the rule file shown below validates cleanly against its own intent: it passes for a correct delivery, and it fails with the expected messages for a broken one. The library is deliberately short — six rules in two patterns — so that the pedagogical point is visible without drowning in detail; production pipelines typically have several dozen rules organised into a larger number of patterns.

The complete rule file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:title>Europa Growth Fund — FundsXML business rules</sch:title>

  <sch:pattern id="delivery-semantics">
    <sch:title>ControlData semantic rules</sch:title>

    <sch:rule context="ControlData">
      <sch:assert test="DataOperation != 'DELETE' or RelatedDocumentIDs">
        A DELETE operation must name the delivery being retracted in RelatedDocumentIDs.
        Delivery <sch:value-of select="UniqueDocumentID"/> violates this rule.
      </sch:assert>
      <sch:assert test="DataOperation != 'AMEND' or RelatedDocumentIDs">
        An AMEND operation should reference the delivery it amends through RelatedDocumentIDs.
        Delivery <sch:value-of select="UniqueDocumentID"/> violates this rule.
      </sch:assert>
      <sch:assert test="number(substring(DocumentGenerated, 1, 4)) &gt;= number(substring(ContentDate, 1, 4))">
        DocumentGenerated (<sch:value-of select="DocumentGenerated"/>)
        cannot be in an earlier year than ContentDate (<sch:value-of select="ContentDate"/>).
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern id="producer-identity">
    <sch:title>Producer identity rules</sch:title>

    <sch:rule context="DataSupplier">
      <sch:assert test="string-length(Short) &gt;= 2">
        DataSupplier/Short must be at least 2 characters; found "<sch:value-of select="Short"/>".
      </sch:assert>
      <sch:assert test="contains(' AT DE CH LU FR IT ES NL BE PT SE DK NO FI GB IE ', concat(' ', SystemCountry, ' '))">
        DataSupplier/SystemCountry "<sch:value-of select="SystemCountry"/>"
        is outside the set of countries supported by this producer.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>
```

### 10.8.1 Reading the Rules One by One

**Rule 1 — DELETE requires RelatedDocumentIDs.** The assertion `DataOperation != 'DELETE' or RelatedDocumentIDs` is the classic conditional-presence rewriting. In plain English: for every `ControlData`, it is either the case that the operation is not `DELETE`, or the `RelatedDocumentIDs` element is present. Both conditions fail only when the operation is `DELETE` *and* `RelatedDocumentIDs` is missing — exactly the case we want to catch. The failure message uses `<sch:value-of select="UniqueDocumentID"/>` to inject the offending document's ID into the error text, which helps a human operator identify the file without having to cross-reference line numbers.

**Rule 2 — AMEND should reference the prior delivery.** Structurally identical to Rule 1, but applies to `AMEND` rather than `DELETE`. This codifies the recommendation from Chapter 4 that every `AMEND` should point at the delivery it amends through `RelatedDocumentIDs`. The schema leaves this optional; the business rule makes it mandatory for the producer's own deliveries.

**Rule 3 — DocumentGenerated year cannot precede ContentDate year.** This is an arithmetic rule that XPath 1.0 can express only approximately. The full rule would be "the full `DocumentGenerated` date-time must be on or after the full `ContentDate` date", but XPath 1.0 has no date arithmetic, so we compare the year substrings as numbers. The approximation catches the common case (a pipeline that has been configured with the wrong content-date default and produces deliveries dated years in the past) but misses the edge case where the two dates differ within the same year. A production pipeline that needs the full check can either use an XSLT-2.0 Schematron binding with `xs:dateTime` comparison, or accept the approximation as an 80%-solution.

**Rule 4 — DataSupplier/Short must be at least 2 characters.** A lexical rule that XSD's `Text64Type` does not enforce. The rule reflects a project convention that single-character identifiers are too short to be useful and almost always indicate a default value that the producer forgot to replace. The failure message includes the offending value.

**Rule 5 — DataSupplier/SystemCountry must be in an allowlist.** An enumerated-membership rule that XSD's `ISOCountryCodeType` does not enforce: the ISO type accepts every valid country code in the world, but the Europa Growth Fund's pipeline only serves European distribution countries. The rule restricts the allowed set to the producer's actual footprint. The XPath 1.0 implementation uses `contains()` over a space-delimited string because there are no sequence literals in the query language.

### 10.8.2 Running the Rules

Saving the rule file as `egf-rules.sch` and the runner script as `run-schematron.py`, the full two-stage validation of a file looks like this:

```
$ xmllint --noout --schema FundsXML4.xsd good.xml
good.xml validates

$ python3 run-schematron.py egf-rules.sch good.xml
good.xml: Schematron validation passed
```

Both stages pass, and the file is safe to emit. A deliberately broken file — one that uses `DataOperation=DELETE` without a `RelatedDocumentIDs`, and a `DataSupplier/Short` of only one character — produces a different picture:

```
$ xmllint --noout --schema FundsXML4.xsd bad-business.xml
bad-business.xml validates

$ python3 run-schematron.py egf-rules.sch bad-business.xml
bad-business.xml: Schematron validation FAILED
  at /FundsXML4/ControlData
    A DELETE operation must name the delivery being retracted in
    RelatedDocumentIDs. Delivery EGF-20260331-VAL-006 violates this rule.
  at /FundsXML4/ControlData/DataSupplier
    DataSupplier/Short must be at least 2 characters; found "X".
```

The demonstration is the central point of this chapter: the broken file **passes XSD validation** — because neither of the rules can be expressed in XSD — but **fails business validation** with two specific, actionable error messages, each carrying enough context (the document ID, the offending short code) that a human operator can fix the producer immediately. Without the Schematron stage, the broken file would have been emitted, consumed downstream, and potentially caused a production incident before anyone noticed that the `DELETE` had nothing to delete.

The same test with the Java, C# or PowerShell runners produces equivalent output — the error messages come from the Schematron rules themselves, so any standards-compliant processor will report the same text and the same locations.

---

## 10.9 A Complete Validation Workflow

The tools of this chapter — `xmllint` (or any of the language-specific validators), the Schematron runners, and a thin wrapper script — can be assembled into a complete validation gatekeeper that a producer pipeline invokes before emitting every delivery. The workflow has three stages: parse (is the XML well-formed?), validate structure (stage 1), and validate business rules (stage 2). Each stage short-circuits the next on failure, and the script exits non-zero on any failure so that upstream callers can treat a non-zero exit as "do not emit this file".

### 10.9.1 Bash (Linux / macOS / WSL)

```bash
#!/usr/bin/env bash
# validate.sh — two-stage FundsXML validation gatekeeper
# Usage: validate.sh <delivery.xml>
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "usage: $0 <delivery.xml>" >&2
    exit 2
fi

XML_FILE="$1"
SCHEMA_FILE="${FUNDSXML_SCHEMA:-/opt/fundsxml/4.2.8/FundsXML4.xsd}"
RULES_FILE="${FUNDSXML_RULES:-/opt/fundsxml/4.2.8/egf-rules.sch}"
SCHEMATRON_RUNNER="${FUNDSXML_SCHEMATRON_RUNNER:-/opt/fundsxml/run-schematron.py}"

# Stage 0: well-formedness (this is cheap and gives the clearest error
# when the file is fundamentally broken).
if ! xmllint --noout "$XML_FILE" 2>&1; then
    echo "FAIL: $XML_FILE is not well-formed XML" >&2
    exit 11
fi

# Stage 1: schema validation against FundsXML4.xsd.
if ! xmllint --noout --schema "$SCHEMA_FILE" "$XML_FILE" 2>&1; then
    echo "FAIL: $XML_FILE failed XSD validation (stage 1)" >&2
    exit 12
fi

# Stage 2: Schematron business-rule validation.
if ! python3 "$SCHEMATRON_RUNNER" "$RULES_FILE" "$XML_FILE"; then
    echo "FAIL: $XML_FILE failed Schematron validation (stage 2)" >&2
    exit 13
fi

echo "OK: $XML_FILE passed both validation stages"
exit 0
```

### 10.9.2 PowerShell (Windows)

The following script is the PowerShell equivalent of the Bash gatekeeper above. It uses .NET's `System.Xml` for well-formedness and XSD validation (Stage 0 and Stage 1), and calls the Python Schematron runner for Stage 2. A purely native PowerShell pipeline can replace the Python call with the `Validate-Schematron.ps1` script from §10.7.4.

```powershell
# Validate-Pipeline.ps1 — two-stage FundsXML validation gatekeeper
# Usage: .\Validate-Pipeline.ps1 -XmlFile delivery.xml
param(
    [Parameter(Mandatory)][string]$XmlFile,
    [string]$SchemaFile  = "C:\fundsxml\4.2.8\FundsXML4.xsd",
    [string]$RulesFile   = "C:\fundsxml\4.2.8\egf-rules.sch",
    [string]$SchematronRunner = "C:\fundsxml\run-schematron.py"
)

$ErrorActionPreference = "Stop"

# Stage 0: well-formedness
try {
    $null = [xml](Get-Content -Raw $XmlFile)
    Write-Output "$XmlFile is well-formed"
}
catch {
    Write-Error "FAIL: $XmlFile is not well-formed XML — $_"
    exit 11
}

# Stage 1: schema validation using .NET XmlReader
$schemas = New-Object System.Xml.Schema.XmlSchemaSet
$schemas.Add($null, (Resolve-Path $SchemaFile).Path) | Out-Null

$settings = New-Object System.Xml.XmlReaderSettings
$settings.Schemas = $schemas
$settings.ValidationType = [System.Xml.ValidationType]::Schema

$script:xsdErrors = @()
$settings.add_ValidationEventHandler({
    param($sender, $e)
    $script:xsdErrors += $e.Message
})

$reader = [System.Xml.XmlReader]::Create(
    (Resolve-Path $XmlFile).Path, $settings)
try { while ($reader.Read()) { } }
finally { $reader.Close() }

if ($xsdErrors.Count -gt 0) {
    foreach ($err in $xsdErrors) { Write-Output "  $err" }
    Write-Error "FAIL: $XmlFile failed XSD validation (stage 1)"
    exit 12
}
Write-Output "$XmlFile passes XSD validation"

# Stage 2: Schematron business-rule validation
& python3 $SchematronRunner $RulesFile $XmlFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "FAIL: $XmlFile failed Schematron validation (stage 2)"
    exit 13
}

Write-Output "OK: $XmlFile passed both validation stages"
exit 0
```

Both scripts use the same exit-code convention: `2` for invocation errors, `11` for well-formedness failures, `12` for XSD failures, `13` for Schematron failures, `0` for success. An upstream pipeline that sees `12` knows that the failure was structural and can route the file to the producer for immediate re-generation; a pipeline that sees `13` knows the failure was semantic and can route the file to a producer-side business-rule review workflow.

The environment variables in the Bash script (`FUNDSXML_SCHEMA`, `FUNDSXML_RULES`, `FUNDSXML_SCHEMATRON_RUNNER`) and the parameter defaults in the PowerShell script let deployers override the paths without editing the script. In a typical deployment, these are set in the pipeline orchestrator's configuration and point at versioned schema and rule files that live alongside the pipeline code.

A production variant of either script would also log its results to a structured audit log (so that incident investigation later can find every validation failure), might run Stage 1 and Stage 2 in parallel for speed on large deliveries (though the serial version shown above is easier to reason about), and could apply differential rules for different delivery categories (ESAP submissions might use a stricter rule set than bilateral distributor files). None of these variations change the underlying two-stage model; they refine how the pipeline is wired around it.

**Fully native alternatives.** The PowerShell script above calls Python for Stage 2. A team that wants to avoid a Python dependency on its Windows servers can replace the Python call with the native PowerShell Schematron validator from §10.7.4, or with the Java runner from §10.7.3 invoked via `java -jar`. Similarly, the Bash script's Stage 1 can be replaced with the Python XSD validator from §10.5.1 if `xmllint` is not available. The validation logic is the same regardless of the tool; what changes is the runtime dependency.

---

## 10.10 Common Pitfalls

- **Running Stage 2 without Stage 1.** A pipeline that skips XSD validation on the assumption that Schematron will catch everything gets confusing error cascades when the underlying structure is broken. Schematron's XPath expressions assume the document has the shape they describe; a missing `ControlData` produces an empty match set rather than a clear "ControlData missing" error.
- **Relying on Stage 1 alone.** The complementary mistake: skipping Schematron and hoping that XSD validation is enough. It is not. Every business rule from §10.6 — conditional presence, cross-element arithmetic, cross-reference integrity — lives outside XSD and is caught only by Stage 2. A pipeline that passes Stage 1 but has no Stage 2 still ships files with the kind of semantic bugs that cause production incidents.
- **Using the wrong schema version.** `xmllint` validates against whichever schema you give it. Validating a FundsXML 4.2.8 file against a 4.2.3 schema may either pass (if the file uses only 4.2.3 features) or fail with confusing "element not expected" errors (if it uses any of the fields that were added between 4.2.3 and 4.2.8). Keep a single canonical schema version in the pipeline, versioned in lockstep with the producer's generator.
- **Copying `FundsXML4.xsd` without `xmldsig-core-schema.xsd`.** Any document with a `ds:Signature` will fail validation with a misleading "cannot locate schema" error that does not immediately point at the missing dependency. Copy both files together.
- **Treating Schematron as a substitute for code review.** Business rules encoded in Schematron are mechanically checkable, which is valuable, but they express only what the rule author thought to check. Rules caught by human review — "this number seems unusually high", "this field was not populated before" — complement automated rules rather than replacing them. A mature pipeline has both.
- **Accepting Schematron failures as warnings rather than errors.** A validation stage whose failures do not block emission is not a validation stage; it is a logging stage. If a rule is worth writing, it is worth enforcing. If a rule is too aggressive to enforce, either relax the rule or remove it from the pipeline entirely — do not run it as a "warning".
- **Forgetting to validate the validation.** Schematron rules are themselves XML files, and they can contain bugs (incorrect XPath expressions, typos in context selectors, assertions that are always true). A mature pipeline includes unit tests for every rule: a small set of deliberately-broken fixture files that each rule is expected to catch, run automatically every time the rule file changes. Without those tests, the rule file quietly drifts away from its intent.
- **Mixing validators across stages.** Using `xmllint` on a Linux build server and .NET `XmlReader` on a Windows staging server is fine — but be aware that error *messages* differ between tools, even though the pass/fail verdict is the same. Automated log parsers that match specific `xmllint` error patterns will break if the pipeline switches to a different validator. Parse exit codes, not error messages, in automation.

---

## 10.11 Key Takeaways

- Every production FundsXML pipeline should validate every outgoing document in two distinct stages: **Stage 1** is schema validation against the XSD (expressing structural rules), **Stage 2** is business-rule validation against a Schematron rule file (expressing semantic rules). The two stages catch disjoint classes of error and are both necessary.
- **Stage 1** can be executed with `xmllint --noout --schema FundsXML4.xsd delivery.xml`, or with equivalent validators in Python (`lxml`), Java (`javax.xml.validation`), C# (`System.Xml.Schema`), or PowerShell (the same .NET classes). All five tools validate against the same XSD and produce the same pass/fail verdict; choose the one that matches your pipeline's language. §10.4 catalogues the five most common error patterns with captured examples.
- **Stage 2** is executed with Schematron rules compiled from a `.sch` file. Python uses `lxml.isoschematron`; Java uses `ph-schematron`; C# and PowerShell use the ISO Schematron XSLT stylesheets with .NET's `XslCompiledTransform`. Schematron expresses conditional presence rules, cross-element arithmetic, cross-reference integrity, and enumerated-membership constraints that XSD cannot capture. The rules are written as XPath assertions inside `<sch:rule context="...">` blocks and produce human-readable failure messages with document context via `<sch:value-of>`.
- A complete validation gatekeeper script (§10.9) combines well-formedness checking, XSD validation, and Schematron validation into a single wrapper — available in both **Bash** (for Linux, macOS, WSL) and **PowerShell** (for Windows) — with distinct exit codes for each failure category, so that upstream pipelines can route failures to the right remediation workflow.
- The most common pitfalls are running either stage in isolation (each has known blind spots), using the wrong schema version, forgetting to copy the imported XMLDSig schema alongside the main XSD, mixing validators without accounting for error-message differences, and running Schematron rules without unit tests — the last is a subtle failure mode that quietly accumulates drift.
