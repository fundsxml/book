<?xml version="1.0" encoding="UTF-8"?>
<!-- Chapter 2, Section 2.12.4 — Data-quality check: position sum vs fund NAV
     Run: xsltproc dq_nav_check.xsl ../europa_growth_fund.xml -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="/FundsXML4">
    <xsl:for-each select="Funds/Fund">
      <xsl:variable name="fundName" select="Names/OfficialName"/>
      <xsl:variable name="fundCcy"  select="Currency"/>
      <xsl:variable name="fundNAV"
        select="FundDynamicData/TotalAssetValues/TotalAssetValue
                /TotalNetAssetValue/Amount[@ccy = $fundCcy]"/>
      <xsl:variable name="positionSum"
        select="sum(FundDynamicData/Portfolios/Portfolio
                /Positions/Position/TotalValue/Amount[@ccy = $fundCcy])"/>
      <xsl:variable name="diff" select="$fundNAV - $positionSum"/>

      <xsl:value-of select="$fundName"/>
      <xsl:text>&#10;  Fund NAV:      </xsl:text>
      <xsl:value-of select="$fundNAV"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$fundCcy"/>
      <xsl:text>&#10;  Position sum:  </xsl:text>
      <xsl:value-of select="$positionSum"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="$fundCcy"/>
      <xsl:text>&#10;  Difference:    </xsl:text>
      <xsl:value-of select="$diff"/>
      <xsl:choose>
        <xsl:when test="$diff = 0">
          <xsl:text>&#10;  Result:        PASS&#10;</xsl:text>
        </xsl:when>
        <xsl:when test="$diff &gt; -1 and $diff &lt; 1">
          <xsl:text>&#10;  Result:        PASS (rounding)&#10;</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>&#10;  Result:        FAIL&#10;</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
