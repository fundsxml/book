#!/usr/bin/env python3
"""Chapter 12, Section 12.3.2 — Read a FundsXML file and print the fund LEI and total NAV.
Run: python3 read_fund.py ../europa_growth_fund.xml
Requires: pip install lxml
"""
import sys
from lxml import etree

def read_fund(path: str) -> None:
    doc = etree.parse(path)
    fund = doc.find("./Funds/Fund")
    if fund is None:
        print(f"{path}: no Fund element found", file=sys.stderr)
        sys.exit(1)

    lei = fund.findtext("Identifiers/LEI") or "(no LEI)"
    name = fund.findtext("Names/OfficialName") or "(unnamed)"

    tav = fund.find(
        "FundDynamicData/TotalAssetValues/TotalAssetValue/"
        "TotalNetAssetValue/Amount"
    )
    if tav is None:
        print(f"{name} ({lei}): no TotalNetAssetValue found")
        return

    amount = tav.text
    currency = tav.get("ccy")
    print(f"{name}")
    print(f"  LEI:  {lei}")
    print(f"  NAV:  {amount} {currency}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: read_fund.py <file.xml>", file=sys.stderr)
        sys.exit(2)
    read_fund(sys.argv[1])
