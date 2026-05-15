// Chapter 12, Section 12.3.4 — Read a FundsXML file with LINQ to XML and print LEI + NAV.
// Build: dotnet run --project ReadFund.csproj ../europa_growth_fund.xml
using System;
using System.Xml.Linq;

class ReadFund {
    static int Main(string[] args) {
        if (args.Length != 1) {
            Console.Error.WriteLine("usage: ReadFund <file.xml>");
            return 2;
        }

        var doc = XDocument.Load(args[0]);
        var fund = doc.Root?.Element("Funds")?.Element("Fund");
        if (fund == null) {
            Console.Error.WriteLine($"{args[0]}: no Fund element found");
            return 1;
        }

        string lei = (string?)fund.Element("Identifiers")?.Element("LEI") ?? "(no LEI)";
        string name = (string?)fund.Element("Names")?.Element("OfficialName") ?? "(unnamed)";

        var amount = fund
            .Element("FundDynamicData")?
            .Element("TotalAssetValues")?
            .Element("TotalAssetValue")?
            .Element("TotalNetAssetValue")?
            .Element("Amount");

        if (amount == null) {
            Console.WriteLine($"{name} ({lei}): no TotalNetAssetValue found");
            return 0;
        }

        string value = amount.Value;
        string currency = (string?)amount.Attribute("ccy") ?? "";

        Console.WriteLine(name);
        Console.WriteLine($"  LEI:  {lei}");
        Console.WriteLine($"  NAV:  {value} {currency}");
        return 0;
    }
}
