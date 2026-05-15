#!/usr/bin/env python3
"""Chapter 12, Section 12.5.1 — Export a fund from PostgreSQL to FundsXML.
Run: python3 export_fund.py 549300ABCDEFGHIJ1234 output.xml
Requires: pip install lxml psycopg
"""
from lxml import etree
import psycopg
import sys

def export_fundsxml(lei, conn_string, output_path):
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, currency, nav_date, nav_amount "
                "FROM funds WHERE lei = %s", (lei,))
            f = cur.fetchone()
            cur.execute(
                "SELECT isin, name, quantity, market_value "
                "FROM positions p JOIN funds f ON f.fund_id = p.fund_id "
                "WHERE f.lei = %s ORDER BY p.market_value DESC", (lei,))
            positions = cur.fetchall()

    fund = etree.Element("Fund")
    ids = etree.SubElement(fund, "Identifiers")
    etree.SubElement(ids, "LEI").text = lei
    names = etree.SubElement(fund, "Names")
    etree.SubElement(names, "OfficialName").text = f[0]
    etree.SubElement(fund, "Currency").text = f[1]
    dyn = etree.SubElement(fund, "FundDynamicData")
    tavs = etree.SubElement(dyn, "TotalAssetValues")
    tav = etree.SubElement(tavs, "TotalAssetValue")
    etree.SubElement(tav, "NavDate").text = str(f[2])
    etree.SubElement(tav, "TotalAssetNature").text = "OFFICIAL"
    tnav = etree.SubElement(tav, "TotalNetAssetValue")
    amt = etree.SubElement(tnav, "Amount", ccy=f[1])
    amt.text = str(f[3])
    port = etree.SubElement(
        etree.SubElement(dyn, "PortfolioData"), "Portfolio")
    for isin, name, qty, mv in positions:
        pos = etree.SubElement(port, "Position")
        p_ids = etree.SubElement(pos, "Identifiers")
        etree.SubElement(p_ids, "ISIN").text = isin
        etree.SubElement(pos, "Name").text = name
        etree.SubElement(pos, "Quantity").text = str(qty)
        etree.SubElement(pos, "MarketValue", ccy=f[1]).text = str(mv)

    tree = etree.ElementTree(fund)
    tree.write(output_path, pretty_print=True,
               xml_declaration=True, encoding="UTF-8")
    print(f"Exported {lei} to {output_path}")

if __name__ == "__main__":
    export_fundsxml(sys.argv[1], "postgresql://localhost/fundsxml",
                    sys.argv[2])
