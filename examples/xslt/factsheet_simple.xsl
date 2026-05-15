<?xml version="1.0" encoding="UTF-8"?>
<!-- Chapter 2, Section 2.12.3 — FundsXML to fact-sheet HTML
     Run: xsltproc factsheet_simple.xsl ../europa_growth_fund.xml > factsheet.html -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <xsl:template match="/">
    <xsl:variable name="fund" select="/FundsXML4/Funds/Fund"/>
    <xsl:variable name="nav"
      select="$fund/FundDynamicData/TotalAssetValues/TotalAssetValue
              /TotalNetAssetValue/Amount"/>
    <html>
      <head><title><xsl:value-of select="$fund/Names/OfficialName"/></title></head>
      <body>
        <h1><xsl:value-of select="$fund/Names/OfficialName"/></h1>
        <table border="1" cellpadding="4">
          <tr><td>LEI</td>
              <td><xsl:value-of select="$fund/Identifiers/LEI"/></td></tr>
          <tr><td>Currency</td>
              <td><xsl:value-of select="$fund/Currency"/></td></tr>
          <tr><td>NAV</td>
              <td><xsl:value-of select="$nav"/>
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="$nav/@ccy"/></td></tr>
          <tr><td>NAV Date</td>
              <td><xsl:value-of select="$fund/FundDynamicData
                    /TotalAssetValues/TotalAssetValue/NavDate"/></td></tr>
          <tr><td>Content Date</td>
              <td><xsl:value-of
                    select="/FundsXML4/ControlData/ContentDate"/></td></tr>
        </table>

        <h2>Share classes</h2>
        <table border="1" cellpadding="4">
          <tr><th>ISIN</th><th>Name</th><th>Currency</th></tr>
          <xsl:for-each select="$fund/SingleFund/ShareClasses/ShareClass">
            <tr>
              <td><xsl:value-of select="Identifiers/ISIN"/></td>
              <td><xsl:value-of select="Names/OfficialName"/></td>
              <td><xsl:value-of select="Currency"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
