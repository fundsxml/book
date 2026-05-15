// Chapter 12, Section 12.5.3 — Query and export from BaseX.
// Requires: BaseX (Maven: org.basex:basex)
// Compile and run: javac -cp ".:basex.jar" BaseXQuery.java
//                  java -cp ".:basex.jar" BaseXQuery
import org.basex.core.*;
import org.basex.core.cmd.*;

public class BaseXQuery {
    public static void main(String[] args) throws Exception {
        try (var ctx = new Context()) {
            new Open("fundsxml").execute(ctx);

            // Export: extract fund and positions as XML
            String export = new XQuery("""
                for $fund in //Fund
                let $name := $fund/Names/OfficialName/text()
                let $lei  := $fund/Identifiers/LEI/text()
                let $nav  := $fund/FundDynamicData/TotalAssetValues
                                  /TotalAssetValue
                                  /TotalNetAssetValue/Amount/text()
                return
                  <Fund>
                    <Identifiers><LEI>{$lei}</LEI></Identifiers>
                    <Names>
                      <OfficialName>{$name}</OfficialName>
                    </Names>
                    {
                      for $pos in $fund/FundDynamicData
                                      /PortfolioData/Portfolio/Position
                      return $pos
                    }
                  </Fund>
                """).execute(ctx);
            System.out.println(export);

            // Analytical query: portfolio weights
            String weights = new XQuery("""
                let $fund := //Fund
                let $nav  := xs:decimal($fund/FundDynamicData
                                 /TotalAssetValues/TotalAssetValue
                                 /TotalNetAssetValue/Amount)
                for $pos in $fund/FundDynamicData
                                /PortfolioData/Portfolio/Position
                let $mv := xs:decimal($pos/MarketValue)
                order by $mv descending
                return concat($pos/Identifiers/ISIN, '  ',
                              $pos/Name, '  ',
                              round($mv div $nav * 10000)
                                div 100, '%')
                """).execute(ctx);
            System.out.println(weights);
        }
    }
}
