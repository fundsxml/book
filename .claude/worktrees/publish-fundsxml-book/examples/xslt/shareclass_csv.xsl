<?xml version="1.0" encoding="UTF-8"?>
<!-- Chapter 2, Section 2.12.2 — FundsXML to share-class CSV (extended)
     Run: xsltproc shareclass_csv.xsl ../europa_growth_fund.xml -->
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
