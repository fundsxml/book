# Appendix D — Complete Example Files

*Complete, schema-valid FundsXML sample files for the Europa Growth Fund*

---

This appendix contains four complete [FundsXML](https://fundsxml.github.io/index.html?xpath=/FundsXML4) documents for the fictional Europa Growth Fund, progressing from minimal to production-grade. Every document in this appendix has been **validated against the real `FundsXML4.xsd` (version 4.2.8)** using `xmllint --schema` and passes without errors. A reader can copy any of these documents into a file, place it alongside the schema, and reproduce the validation result.

The four documents are:

- **D.1 — Minimal Delivery.** The smallest possible valid FundsXML document: ControlData, one Fund with identifiers, names, currency, and a single TNAV. Start here to understand the bare structure.
- **D.2 — Monthly NAV Delivery.** A mid-sized delivery with FundStaticData, a portfolio containing four positions (two equities, one bond, one cash account), and the matching AssetMasterData block.
- **D.3 — Full Production Delivery.** A realistic producer output: extended FundStaticData with Custodian, Administrator, Auditor, OngoingCosts, and SFDRProductType; eight portfolio positions including an FX forward; two transactions; three share classes; two document references; and CustomAttributes in ControlData.
- **D.4 — AMEND Delivery.** A correction delivery that references D.2 via RelatedDocumentIDs, demonstrating the AMEND data operation with a corrected TNAV.

**What is not included.** The [RegulatoryReportings](https://fundsxml.github.io/index.html?xpath=/FundsXML4/RegulatoryReportings) block (EMT, EPT, EET, EFT, TPT) is omitted because each FinDatEx template contains 60–180 fields that would consume many pages without adding structural insight beyond what Chapter 8 already provides. XML Digital Signatures are omitted because they require real cryptographic keys and cannot be meaningfully reproduced from a book listing. Readers who need RegulatoryReportings or Signature examples should consult the FundsXML association's sample-file repository.

---

## D.1 Minimal Delivery

The simplest valid FundsXML document: [ControlData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData) with all required fields, and a single [Fund](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund) carrying only identifiers, names, currency, the SingleFundFlag, and one TotalAssetValue. This is the baseline that every more complex delivery builds upon.

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
    </Fund>
  </Funds>
</FundsXML4>
```

---

## D.2 Monthly NAV Delivery

A delivery that a typical producer might emit at month-end: ControlData, [FundStaticData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData) with domicile, legal structure, inception date, fiscal-year boundaries, custodian, investment company, and SFDR classification; [FundDynamicData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundDynamicData) with a TotalAssetValue and a portfolio of four positions; and the matching [AssetMasterData](https://fundsxml.github.io/index.html?xpath=/FundsXML4/AssetMasterData) block. Each position uses the `UniqueID` / `xs:IDREF` mechanism to reference its asset in AssetMasterData.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-002</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T07:15:00Z</DocumentGenerated>
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
        <ShortName>EGF</ShortName>
      </Names>
      <Currency>EUR</Currency>
      <SingleFundFlag>true</SingleFundFlag>
      <FundStaticData>
        <DomicileCountry>LU</DomicileCountry>
        <ListedLegalStructure>UCITS</ListedLegalStructure>
        <InceptionDate>2012-06-15</InceptionDate>
        <StartOfFiscalYear>
          <Day>1</Day>
          <Month>1</Month>
        </StartOfFiscalYear>
        <EndOfFiscalYear>
          <Day>31</Day>
          <Month>12</Month>
        </EndOfFiscalYear>
        <OpenClosedEnded>OPEN</OpenClosedEnded>
        <Custodian>
          <Identifiers>
            <LEI>RCNB21CWBJ8HYAFVEL56</LEI>
          </Identifiers>
          <Name>Banque Internationale à Luxembourg S.A.</Name>
        </Custodian>
        <InvestmentCompany>
          <Identifiers>
            <LEI>549300ABCDEFGHIJ1234</LEI>
          </Identifiers>
          <Name>Europa Asset Management S.A.</Name>
        </InvestmentCompany>
        <SFDRProductType>8</SFDRProductType>
      </FundStaticData>
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
        <Portfolios>
          <Portfolio>
            <NavDate>2026-03-31</NavDate>
            <Positions>
              <Position>
                <UniqueID>ASSET-EQ-001</UniqueID>
                <Identifiers>
                  <ISIN>DE0007164600</ISIN>
                </Identifiers>
                <Currency>EUR</Currency>
                <TotalValue>
                  <Amount ccy="EUR">52340000.00</Amount>
                </TotalValue>
                <Equity>
                  <Units>250000</Units>
                  <Price>
                    <Amount ccy="EUR">209.36</Amount>
                  </Price>
                </Equity>
              </Position>
              <Position>
                <UniqueID>ASSET-BO-001</UniqueID>
                <Identifiers>
                  <ISIN>DE0001102481</ISIN>
                </Identifiers>
                <Currency>EUR</Currency>
                <TotalValue>
                  <Amount ccy="EUR">30125000.00</Amount>
                </TotalValue>
                <Bond>
                  <Nominal>30000000</Nominal>
                  <Price>
                    <Amount ccy="EUR">100.4167</Amount>
                  </Price>
                </Bond>
              </Position>
              <Position>
                <UniqueID>ASSET-AC-001</UniqueID>
                <Currency>EUR</Currency>
                <TotalValue>
                  <Amount ccy="EUR">8750000.00</Amount>
                </TotalValue>
                <Account>
                  <MarketValue>
                    <Amount ccy="EUR">8750000.00</Amount>
                  </MarketValue>
                </Account>
              </Position>
              <Position>
                <UniqueID>ASSET-EQ-002</UniqueID>
                <Identifiers>
                  <ISIN>FR0000120271</ISIN>
                </Identifiers>
                <Currency>EUR</Currency>
                <TotalValue>
                  <Amount ccy="EUR">41875000.00</Amount>
                </TotalValue>
                <Equity>
                  <Units>125000</Units>
                  <Price>
                    <Amount ccy="EUR">335.00</Amount>
                  </Price>
                </Equity>
              </Position>
            </Positions>
          </Portfolio>
        </Portfolios>
      </FundDynamicData>
    </Fund>
  </Funds>
  <AssetMasterData>
    <Asset>
      <UniqueID>ASSET-EQ-001</UniqueID>
      <Identifiers>
        <ISIN>DE0007164600</ISIN>
      </Identifiers>
      <Currency>EUR</Currency>
      <Country>DE</Country>
      <Name>SAP SE</Name>
      <AssetType>EQ</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-BO-001</UniqueID>
      <Identifiers>
        <ISIN>DE0001102481</ISIN>
      </Identifiers>
      <Currency>EUR</Currency>
      <Country>DE</Country>
      <Name>Bundesrepublik Deutschland 0.00% 2026-02-15</Name>
      <AssetType>BO</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-AC-001</UniqueID>
      <Currency>EUR</Currency>
      <Country>LU</Country>
      <Name>BIL Custody Account EUR</Name>
      <AssetType>AC</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-EQ-002</UniqueID>
      <Identifiers>
        <ISIN>FR0000120271</ISIN>
      </Identifiers>
      <Currency>EUR</Currency>
      <Country>FR</Country>
      <Name>TotalEnergies SE</Name>
      <AssetType>EQ</AssetType>
    </Asset>
  </AssetMasterData>
</FundsXML4>
```

---

## D.3 Full Production Delivery

A realistic monthly production delivery. This document exercises:

- **ControlData** with Contact details and two [CustomAttributes](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/FundStaticData/CustomAttributes) (delivery sequence number and generator version).
- **FundStaticData** with Administrator, Auditor, Custodian, InvestmentCompany, OngoingCosts (Ongoing Charges and Transaction Costs), and SFDRProductType.
- **FundDynamicData** with a portfolio of eight positions: four equities (including one CHF-denominated position with dual-currency TotalValue), two bonds, one FX forward (CHF/EUR hedge), and one custody account.
- **Transactions** with a BUY and a SELL, each carrying the required NominalOrUnitsOrContracts.
- **SingleFund/[ShareClasses](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Funds/Fund/SingleFund/ShareClasses)** with three share classes (I-EUR-ACC, R-EUR-DIS, R-CHF-ACC-HEDGED).
- **AssetMasterData** with eight assets matching the portfolio positions (AssetType codes EQ, BO, FX, AC).
- **[Documents](https://fundsxml.github.io/index.html?xpath=/FundsXML4/Documents)** with a Prospectus reference at fund level and a PRIIPS-KID reference at share-class level.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-003</UniqueDocumentID>
    <DocumentGenerated>2026-04-01T08:30:00Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
      <Contact>
        <Name>Fund Data Operations</Name>
        <Email>fundsxml@eam-lu.example.com</Email>
      </Contact>
    </DataSupplier>
    <DataOperation>INITIAL</DataOperation>
    <Language>en</Language>
    <CustomAttributes>
      <Attribute>
        <Name>eam.delivery.sequenceNumber</Name>
        <Type>N</Type>
        <ValueNumber>42</ValueNumber>
      </Attribute>
      <Attribute>
        <Name>eam.delivery.generatorVersion</Name>
        <Type>T</Type>
        <ValueText>EAM-Pipeline 2.1.0</ValueText>
      </Attribute>
    </CustomAttributes>
  </ControlData>
  <Funds>
    <Fund>
      <Identifiers>
        <LEI>549300ABCDEFGHIJ1234</LEI>
      </Identifiers>
      <Names>
        <OfficialName>Europa Growth Fund</OfficialName>
        <ShortName>EGF</ShortName>
      </Names>
      <Currency>EUR</Currency>
      <SingleFundFlag>true</SingleFundFlag>
      <FundStaticData>
        <DomicileCountry>LU</DomicileCountry>
        <ListedLegalStructure>UCITS</ListedLegalStructure>
        <InceptionDate>2012-06-15</InceptionDate>
        <StartOfFiscalYear>
          <Day>1</Day>
          <Month>1</Month>
        </StartOfFiscalYear>
        <EndOfFiscalYear>
          <Day>31</Day>
          <Month>12</Month>
        </EndOfFiscalYear>
        <OpenClosedEnded>OPEN</OpenClosedEnded>
        <Administrator>
          <Identifiers>
            <LEI>529900HNOAA1KXQJUQ27</LEI>
          </Identifiers>
          <Name>European Fund Administration S.A.</Name>
        </Administrator>
        <Auditor>
          <Identifiers>
            <LEI>1RVNBN7QG3CEEKYN6T68</LEI>
          </Identifiers>
          <Name>PricewaterhouseCoopers Société coopérative</Name>
        </Auditor>
        <Custodian>
          <Identifiers>
            <LEI>RCNB21CWBJ8HYAFVEL56</LEI>
          </Identifiers>
          <Name>Banque Internationale à Luxembourg S.A.</Name>
        </Custodian>
        <InvestmentCompany>
          <Identifiers>
            <LEI>549300ABCDEFGHIJ1234</LEI>
          </Identifiers>
          <Name>Europa Asset Management S.A.</Name>
        </InvestmentCompany>
        <OngoingCosts>
          <OngoingCost>
            <CostType>Ongoing Charges</CostType>
            <PublicationDate>2025-12-31</PublicationDate>
            <Percentage>1.45</Percentage>
          </OngoingCost>
          <OngoingCost>
            <CostType>Transaction Costs</CostType>
            <PublicationDate>2025-12-31</PublicationDate>
            <Percentage>0.12</Percentage>
          </OngoingCost>
        </OngoingCosts>
        <SFDRProductType>8</SFDRProductType>
      </FundStaticData>
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
        <Portfolios>
          <Portfolio>
            <NavDate>2026-03-31</NavDate>
            <Positions>
              <Position>
                <UniqueID>ASSET-EQ-001</UniqueID>
                <Identifiers><ISIN>DE0007164600</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">52340000.00</Amount></TotalValue>
                <Equity>
                  <Units>250000</Units>
                  <Price><Amount ccy="EUR">209.36</Amount></Price>
                </Equity>
              </Position>
              <Position>
                <UniqueID>ASSET-EQ-002</UniqueID>
                <Identifiers><ISIN>FR0000120271</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">41875000.00</Amount></TotalValue>
                <Equity>
                  <Units>125000</Units>
                  <Price><Amount ccy="EUR">335.00</Amount></Price>
                </Equity>
              </Position>
              <Position>
                <UniqueID>ASSET-EQ-003</UniqueID>
                <Identifiers><ISIN>NL0010273215</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">89600000.00</Amount></TotalValue>
                <Equity>
                  <Units>100000</Units>
                  <Price><Amount ccy="EUR">896.00</Amount></Price>
                </Equity>
              </Position>
              <Position>
                <UniqueID>ASSET-EQ-004</UniqueID>
                <Identifiers><ISIN>CH0012221716</ISIN></Identifiers>
                <Currency>CHF</Currency>
                <TotalValue>
                  <Amount ccy="EUR">74250000.00</Amount>
                  <Amount ccy="CHF">71280000.00</Amount>
                </TotalValue>
                <Equity>
                  <Units>300000</Units>
                  <Price><Amount ccy="CHF">237.60</Amount></Price>
                </Equity>
              </Position>
              <Position>
                <UniqueID>ASSET-BO-001</UniqueID>
                <Identifiers><ISIN>DE0001102481</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">30125000.00</Amount></TotalValue>
                <Bond>
                  <Nominal>30000000</Nominal>
                  <Price><Amount ccy="EUR">100.4167</Amount></Price>
                </Bond>
              </Position>
              <Position>
                <UniqueID>ASSET-BO-002</UniqueID>
                <Identifiers><ISIN>FR0014007L00</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">50312848.78</Amount></TotalValue>
                <Bond>
                  <Nominal>50000000</Nominal>
                  <Price><Amount ccy="EUR">100.6257</Amount></Price>
                </Bond>
              </Position>
              <Position>
                <UniqueID>ASSET-FX-001</UniqueID>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">-125000.00</Amount></TotalValue>
                <FXForward>
                  <FxRateForEvaluation>1.0416</FxRateForEvaluation>
                </FXForward>
              </Position>
              <Position>
                <UniqueID>ASSET-AC-001</UniqueID>
                <Currency>EUR</Currency>
                <TotalValue><Amount ccy="EUR">126175000.00</Amount></TotalValue>
                <Account>
                  <MarketValue>
                    <Amount ccy="EUR">126175000.00</Amount>
                  </MarketValue>
                </Account>
              </Position>
            </Positions>
            <Transactions>
              <Transaction>
                <TransactionID>TXN-20260328-001</TransactionID>
                <AssetUniqueID>ASSET-EQ-003</AssetUniqueID>
                <Identifiers><ISIN>NL0010273215</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TransactionKind>BUY</TransactionKind>
                <ClosingDate>2026-03-28</ClosingDate>
                <NominalOrUnitsOrContracts>10000</NominalOrUnitsOrContracts>
              </Transaction>
              <Transaction>
                <TransactionID>TXN-20260330-001</TransactionID>
                <AssetUniqueID>ASSET-EQ-001</AssetUniqueID>
                <Identifiers><ISIN>DE0007164600</ISIN></Identifiers>
                <Currency>EUR</Currency>
                <TransactionKind>SELL</TransactionKind>
                <ClosingDate>2026-03-30</ClosingDate>
                <NominalOrUnitsOrContracts>5000</NominalOrUnitsOrContracts>
              </Transaction>
            </Transactions>
          </Portfolio>
        </Portfolios>
      </FundDynamicData>
      <SingleFund>
        <ShareClasses>
          <ShareClass>
            <Identifiers><ISIN>LU1234567890</ISIN></Identifiers>
            <Names>
              <OfficialName>Europa Growth Fund I EUR Acc</OfficialName>
            </Names>
            <Currency>EUR</Currency>
          </ShareClass>
          <ShareClass>
            <Identifiers><ISIN>LU1234567891</ISIN></Identifiers>
            <Names>
              <OfficialName>Europa Growth Fund R EUR Dis</OfficialName>
            </Names>
            <Currency>EUR</Currency>
          </ShareClass>
          <ShareClass>
            <Identifiers><ISIN>LU1234567892</ISIN></Identifiers>
            <Names>
              <OfficialName>Europa Growth Fund R CHF Acc Hedged</OfficialName>
            </Names>
            <Currency>CHF</Currency>
          </ShareClass>
        </ShareClasses>
      </SingleFund>
    </Fund>
  </Funds>
  <AssetMasterData>
    <Asset>
      <UniqueID>ASSET-EQ-001</UniqueID>
      <Identifiers><ISIN>DE0007164600</ISIN></Identifiers>
      <Currency>EUR</Currency>
      <Country>DE</Country>
      <Name>SAP SE</Name>
      <AssetType>EQ</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-EQ-002</UniqueID>
      <Identifiers><ISIN>FR0000120271</ISIN></Identifiers>
      <Currency>EUR</Currency>
      <Country>FR</Country>
      <Name>TotalEnergies SE</Name>
      <AssetType>EQ</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-EQ-003</UniqueID>
      <Identifiers><ISIN>NL0010273215</ISIN></Identifiers>
      <Currency>EUR</Currency>
      <Country>NL</Country>
      <Name>ASML Holding N.V.</Name>
      <AssetType>EQ</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-EQ-004</UniqueID>
      <Identifiers><ISIN>CH0012221716</ISIN></Identifiers>
      <Currency>CHF</Currency>
      <Country>CH</Country>
      <Name>ABB Ltd</Name>
      <AssetType>EQ</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-BO-001</UniqueID>
      <Identifiers><ISIN>DE0001102481</ISIN></Identifiers>
      <Currency>EUR</Currency>
      <Country>DE</Country>
      <Name>Bundesrepublik Deutschland 0.00% 2026-02-15</Name>
      <AssetType>BO</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-BO-002</UniqueID>
      <Identifiers><ISIN>FR0014007L00</ISIN></Identifiers>
      <Currency>EUR</Currency>
      <Country>FR</Country>
      <Name>République Française 0.00% 2027-02-25</Name>
      <AssetType>BO</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-FX-001</UniqueID>
      <Currency>EUR</Currency>
      <Country>LU</Country>
      <Name>FX Forward CHF/EUR 2026-04-30</Name>
      <AssetType>FX</AssetType>
    </Asset>
    <Asset>
      <UniqueID>ASSET-AC-001</UniqueID>
      <Currency>EUR</Currency>
      <Country>LU</Country>
      <Name>BIL Custody Account EUR</Name>
      <AssetType>AC</AssetType>
    </Asset>
  </AssetMasterData>
  <Documents>
    <Document>
      <Type><ListedType>Prospectus</ListedType></Type>
      <Language>en</Language>
      <Fund>
        <Identifiers><LEI>549300ABCDEFGHIJ1234</LEI></Identifiers>
        <Name>Europa Growth Fund</Name>
      </Fund>
      <Format>PDF</Format>
      <CreationDate>2026-01-15</CreationDate>
      <DocumentURL>https://www.eam-lu.example.com/docs/egf-prospectus-2026.pdf</DocumentURL>
    </Document>
    <Document>
      <Type><ListedType>PRIIPS-KID</ListedType></Type>
      <Language>en</Language>
      <ShareClasses>
        <ShareClass>
          <Identifiers><ISIN>LU1234567890</ISIN></Identifiers>
          <Name>Europa Growth Fund I EUR Acc</Name>
        </ShareClass>
      </ShareClasses>
      <Format>PDF</Format>
      <CreationDate>2026-02-01</CreationDate>
      <DocumentURL>https://www.eam-lu.example.com/docs/egf-kid-i-eur-acc-2026.pdf</DocumentURL>
    </Document>
  </Documents>
</FundsXML4>
```

---

## D.4 AMEND Delivery

A correction delivery that supersedes D.2. The [`DataOperation`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/DataOperation) is set to `AMEND`, and the `RelatedDocumentIDs` element references the original document's [`UniqueDocumentID`](https://fundsxml.github.io/index.html?xpath=/FundsXML4/ControlData/UniqueDocumentID). The corrected content — a revised TNAV — replaces the earlier value. Consumers that implement the three-operation protocol from Chapter 4 will locate the original delivery by its ID and apply the correction.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FundsXML4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="FundsXML4.xsd">
  <ControlData>
    <UniqueDocumentID>EGF-20260331-004</UniqueDocumentID>
    <DocumentGenerated>2026-04-02T09:15:00Z</DocumentGenerated>
    <Version>4.2.8</Version>
    <ContentDate>2026-03-31</ContentDate>
    <DataSupplier>
      <SystemCountry>LU</SystemCountry>
      <Short>EAM</Short>
      <Name>Europa Asset Management S.A.</Name>
      <Type>IC</Type>
    </DataSupplier>
    <DataOperation>AMEND</DataOperation>
    <RelatedDocumentIDs>
      <RelatedDocumentID>EGF-20260331-002</RelatedDocumentID>
    </RelatedDocumentIDs>
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
              <Amount ccy="EUR">464589123.45</Amount>
            </TotalNetAssetValue>
          </TotalAssetValue>
        </TotalAssetValues>
      </FundDynamicData>
    </Fund>
  </Funds>
</FundsXML4>
```

---

## D.5 Validation Instructions

To validate any of the files in this appendix, place the file and the FundsXML schema (`FundsXML4.xsd`, along with its dependency `xmldsig-core-schema.xsd`) in the same directory and run:

```bash
xmllint --schema FundsXML4.xsd filename.xml --noout
```

The expected output for each file is:

```
filename.xml validates
```

If validation fails, check that the `xsi:noNamespaceSchemaLocation` attribute points to the correct schema file relative to the XML file's location, and that both schema files are present.

The files in this appendix were validated against FundsXML schema version 4.2.8 at the time of writing. Newer schema versions may introduce additional required elements or tighten existing constraints; if a file that validated against 4.2.8 fails against a later version, consult the release changelog for the specific change that caused the failure.
