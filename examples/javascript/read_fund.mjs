// Chapter 12, Section 12.3.5 — Read a FundsXML file with fast-xml-parser and print LEI + NAV.
// Install: npm install fast-xml-parser
// Run: node read_fund.mjs ../europa_growth_fund.xml
import { readFileSync } from "node:fs";
import { XMLParser } from "fast-xml-parser";

function readFund(path) {
  const xml = readFileSync(path, "utf8");
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "@_",
  });
  const doc = parser.parse(xml);

  const fund = doc?.FundsXML4?.Funds?.Fund;
  if (!fund) {
    console.error(`${path}: no Fund element found`);
    process.exit(1);
  }

  const lei = fund.Identifiers?.LEI ?? "(no LEI)";
  const name = fund.Names?.OfficialName ?? "(unnamed)";
  const tav =
    fund.FundDynamicData?.TotalAssetValues?.TotalAssetValue
      ?.TotalNetAssetValue?.Amount;

  if (!tav) {
    console.log(`${name} (${lei}): no TotalNetAssetValue found`);
    return;
  }

  const amount = typeof tav === "object" ? tav["#text"] : tav;
  const currency = typeof tav === "object" ? tav["@_ccy"] : "";

  console.log(name);
  console.log(`  LEI:  ${lei}`);
  console.log(`  NAV:  ${amount} ${currency}`);
}

const path = process.argv[2];
if (!path) {
  console.error("usage: node read_fund.mjs <file.xml>");
  process.exit(2);
}
readFund(path);
