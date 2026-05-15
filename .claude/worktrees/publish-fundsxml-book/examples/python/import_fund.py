#!/usr/bin/env python3
"""Chapter 12, Section 12.5.1 — Import a FundsXML file into PostgreSQL.
Run: python3 import_fund.py ../europa_growth_fund.xml
Requires: pip install lxml psycopg
"""
from lxml import etree
import psycopg
import sys

def import_fundsxml(path, conn_string):
    tree = etree.parse(path)
    fund = tree.find(".//Fund")
    lei      = fund.findtext("Identifiers/LEI")
    name     = fund.findtext("Names/OfficialName")
    currency = fund.findtext("Currency")
    nav      = fund.find(".//TotalAssetValue")
    nav_date = nav.findtext("NavDate")
    nav_amt  = nav.findtext("TotalNetAssetValue/Amount")

    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO funds (lei, name, currency, nav_date, nav_amount)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING fund_id
            """, (lei, name, currency, nav_date, nav_amt))
            fund_id = cur.fetchone()[0]

            for pos in fund.findall(".//Portfolio/Position"):
                cur.execute("""
                    INSERT INTO positions
                           (fund_id, nav_date, isin, name,
                            quantity, market_value, currency)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (fund_id, nav_date,
                      pos.findtext("Identifiers/ISIN"),
                      pos.findtext("Name"),
                      pos.findtext("Quantity"),
                      pos.findtext("MarketValue"),
                      currency))
        conn.commit()
    print(f"Imported {lei}: fund_id={fund_id}")

if __name__ == "__main__":
    import_fundsxml(sys.argv[1], "postgresql://localhost/fundsxml")
