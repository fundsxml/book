// Chapter 12, Section 12.5.3 — Import a FundsXML file into BaseX.
// Requires: BaseX (Maven: org.basex:basex)
// Compile and run: javac -cp ".:basex.jar" FundsXmlToBaseX.java
//                  java -cp ".:basex.jar" FundsXmlToBaseX ../europa_growth_fund.xml
import org.basex.core.*;
import org.basex.core.cmd.*;

public class FundsXmlToBaseX {
    public static void main(String[] args) throws Exception {
        try (var ctx = new Context()) {
            new CreateDB("fundsxml", args[0]).execute(ctx);
            System.out.println("Imported " + args[0]
                + " into database 'fundsxml'");
        }
    }
}
