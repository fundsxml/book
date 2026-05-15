// Chapter 12, Section 12.3.3 — Read a FundsXML file with JAXP + XPath and print LEI + NAV.
// Compile and run: javac ReadFund.java && java ReadFund ../europa_growth_fund.xml
import java.io.File;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Node;

public class ReadFund {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.err.println("usage: java ReadFund <file.xml>");
            System.exit(2);
        }

        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        dbf.setNamespaceAware(false);
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document doc = db.parse(new File(args[0]));

        XPath xpath = XPathFactory.newInstance().newXPath();
        Node fund = (Node) xpath.evaluate("/FundsXML4/Funds/Fund", doc,
                javax.xml.xpath.XPathConstants.NODE);
        if (fund == null) {
            System.err.println(args[0] + ": no Fund element found");
            System.exit(1);
        }

        String lei = xpath.evaluate("Identifiers/LEI", fund);
        String name = xpath.evaluate("Names/OfficialName", fund);
        Node amt = (Node) xpath.evaluate(
            "FundDynamicData/TotalAssetValues/TotalAssetValue/"
            + "TotalNetAssetValue/Amount", fund,
            javax.xml.xpath.XPathConstants.NODE);

        if (amt == null) {
            System.out.println(name + " (" + lei + "): no TotalNetAssetValue");
            return;
        }

        String amount = amt.getTextContent();
        String currency = amt.getAttributes().getNamedItem("ccy").getNodeValue();

        System.out.println(name);
        System.out.println("  LEI:  " + lei);
        System.out.println("  NAV:  " + amount + " " + currency);
    }
}
