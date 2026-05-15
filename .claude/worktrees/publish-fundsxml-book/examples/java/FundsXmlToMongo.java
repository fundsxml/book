// Chapter 12, Section 12.5.2 — Import a FundsXML file into MongoDB.
// Requires: mongodb-driver-sync (Maven: org.mongodb:mongodb-driver-sync:5.x)
// Compile and run: javac -cp ".:mongodb-driver-sync-5.x.jar:*" FundsXmlToMongo.java
//                  java -cp ".:mongodb-driver-sync-5.x.jar:*" FundsXmlToMongo ../europa_growth_fund.xml
import com.mongodb.client.*;
import org.bson.Document;
import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.xpath.*;
import java.util.*;

public class FundsXmlToMongo {
    public static void main(String[] args) throws Exception {
        var dbf = DocumentBuilderFactory.newInstance();
        var doc = dbf.newDocumentBuilder().parse(args[0]);
        var xp  = XPathFactory.newInstance().newXPath();

        String lei  = xp.evaluate("//Fund/Identifiers/LEI", doc);
        String name = xp.evaluate("//Fund/Names/OfficialName", doc);
        String ccy  = xp.evaluate("//Fund/Currency", doc);
        String date = xp.evaluate("//TotalAssetValue/NavDate", doc);
        String nav  = xp.evaluate("//TotalNetAssetValue/Amount", doc);

        var positions = new ArrayList<Document>();
        var nodes = (NodeList) xp.evaluate(
            "//Portfolio/Position", doc, XPathConstants.NODESET);
        for (int i = 0; i < nodes.getLength(); i++) {
            var pos = nodes.item(i);
            positions.add(new Document()
                .append("isin", xp.evaluate("Identifiers/ISIN", pos))
                .append("name", xp.evaluate("Name", pos))
                .append("quantity", Double.parseDouble(
                    xp.evaluate("Quantity", pos)))
                .append("marketValue", Double.parseDouble(
                    xp.evaluate("MarketValue", pos))));
        }

        var fund = new Document()
            .append("lei", lei).append("name", name)
            .append("currency", ccy).append("navDate", date)
            .append("navAmount", Double.parseDouble(nav))
            .append("positions", positions);

        try (var client = MongoClients.create(
                "mongodb://localhost:27017")) {
            client.getDatabase("fundsxml")
                  .getCollection("funds")
                  .insertOne(fund);
            System.out.println("Imported " + lei);
        }
    }
}
