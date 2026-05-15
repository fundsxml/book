// Chapter 12, Section 12.5.2 — Export a fund from MongoDB to FundsXML.
// Requires: mongodb-driver-sync (Maven: org.mongodb:mongodb-driver-sync:5.x)
import com.mongodb.client.*;
import static com.mongodb.client.model.Filters.eq;
import org.bson.Document;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.util.List;

public class MongoToFundsXml {
    public static void main(String[] args) throws Exception {
        Document fund;
        try (var client = MongoClients.create(
                "mongodb://localhost:27017")) {
            fund = client.getDatabase("fundsxml")
                         .getCollection("funds")
                         .find(eq("lei", args[0])).first();
        }

        var dbf = DocumentBuilderFactory.newInstance();
        var doc = dbf.newDocumentBuilder().newDocument();
        var root = doc.createElement("Fund");
        doc.appendChild(root);
        appendTextElement(doc, appendElement(doc, root,
            "Identifiers"), "LEI", fund.getString("lei"));
        appendTextElement(doc, appendElement(doc, root,
            "Names"), "OfficialName", fund.getString("name"));
        appendTextElement(doc, root, "Currency",
            fund.getString("currency"));
        var dyn = appendElement(doc, root, "FundDynamicData");
        var tav = appendElement(doc, appendElement(doc, dyn,
            "TotalAssetValues"), "TotalAssetValue");
        appendTextElement(doc, tav, "NavDate",
            fund.getString("navDate"));
        var amt = appendTextElement(doc, appendElement(doc, tav,
            "TotalNetAssetValue"), "Amount",
            String.valueOf(fund.getDouble("navAmount")));
        amt.setAttribute("ccy", fund.getString("currency"));
        var port = appendElement(doc, appendElement(doc, dyn,
            "PortfolioData"), "Portfolio");
        for (var p : fund.getList("positions", Document.class)) {
            var pos = appendElement(doc, port, "Position");
            appendTextElement(doc, appendElement(doc, pos,
                "Identifiers"), "ISIN", p.getString("isin"));
            appendTextElement(doc, pos, "Name",
                p.getString("name"));
            appendTextElement(doc, pos, "Quantity",
                String.valueOf(p.getDouble("quantity").intValue()));
            var mv = appendTextElement(doc, pos, "MarketValue",
                String.valueOf(p.getDouble("marketValue")));
            mv.setAttribute("ccy", fund.getString("currency"));
        }

        var tf = TransformerFactory.newInstance().newTransformer();
        tf.setOutputProperty(OutputKeys.INDENT, "yes");
        tf.transform(new DOMSource(doc),
            new StreamResult(new File(args[1])));
        System.out.println("Exported " + args[0] + " to " + args[1]);
    }

    static org.w3c.dom.Element appendElement(
            org.w3c.dom.Document doc,
            org.w3c.dom.Element parent, String name) {
        var el = doc.createElement(name);
        parent.appendChild(el);
        return el;
    }

    static org.w3c.dom.Element appendTextElement(
            org.w3c.dom.Document doc,
            org.w3c.dom.Element parent, String name, String text) {
        var el = appendElement(doc, parent, name);
        el.setTextContent(text);
        return el;
    }
}
