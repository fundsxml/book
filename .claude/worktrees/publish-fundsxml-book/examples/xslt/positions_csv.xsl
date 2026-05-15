<?xml version="1.0" encoding="UTF-8"?>
<!-- Chapter 12, Section 12.3.7 Example 2 — FundsXML portfolio to CSV
     Run: xsltproc positions_csv.xsl ../europa_growth_fund.xml > positions.csv -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>

  <xsl:key name="asset" match="/FundsXML4/AssetMasterData/Asset" use="UniqueID"/>

  <xsl:template match="/">
    <xsl:text>ISIN,Name,Currency,MarketValue&#10;</xsl:text>
    <xsl:for-each select="//Portfolio/Positions/Position">
      <xsl:variable name="master" select="key('asset', UniqueID)"/>
      <xsl:value-of select="$master/Identifiers/ISIN"/>
      <xsl:text>,</xsl:text>
      <xsl:value-of select="$master/Name"/>
      <xsl:text>,</xsl:text>
      <xsl:value-of select="TotalValue/Amount/@ccy"/>
      <xsl:text>,</xsl:text>
      <xsl:value-of select="TotalValue/Amount"/>
      <xsl:text>&#10;</xsl:text>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
