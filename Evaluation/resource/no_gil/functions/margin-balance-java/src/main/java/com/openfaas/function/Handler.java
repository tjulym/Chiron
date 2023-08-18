package com.openfaas.function;

import com.openfaas.model.IHandler;
import com.openfaas.model.IResponse;
import com.openfaas.model.IRequest;
import com.openfaas.model.Response;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.HashMap;
import java.util.Map;
import java.util.Iterator;
import java.lang.System;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        Map<String, Double> marketData = new HashMap<>();
        String portfolio = "1234";
        boolean validFormat = true;

        try {
            JsonNode inputNode = mapper.readTree(req.getBody());
            for (JsonNode strNode: inputNode) {
                JsonNode node = mapper.readTree(strNode.asText());
                if (node.has("marketData")) {
                    JsonNode marketDataNode = node.get("marketData");
                    Iterator<Map.Entry<String, JsonNode>> fields = marketDataNode.fields();
                    fields.forEachRemaining(field -> {
                        marketData.put(field.getKey(), Double.parseDouble(field.getValue().asText()));
                    });
                } else {
                    portfolio = node.get("portfolio").asText();
                    boolean valid = node.get("valid").asBoolean();
                    if (!valid) {
                        validFormat = false;
                    }
                }
            }
        } catch (Exception e) {
            validFormat = false;
            e.printStackTrace();
        }

        boolean marginSatisfied = false;
        double portfolioMarketValue = 0.0;
        try {
            JsonNode porNode = mapper.readTree(portfolios);
            JsonNode data = porNode.get(portfolio);

            for (JsonNode trade: data) {
                String security = trade.get("Security").asText();
                int qty = trade.get("LastQty").asInt();
                portfolioMarketValue += (marketData.get(security) * qty);
            }

            if (!(4500 < 0.25 * portfolioMarketValue)) {
                marginSatisfied = true;
            }
        } catch (Exception e) {
            e.printStackTrace();
        } 

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("validFormat", validFormat);
        rlt.put("marginSatisfied", marginSatisfied);

        rlt.put("start", start);

        Response res = new Response();

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        String rltStr = null;

        try {
            rltStr = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }

        res.setBody(rltStr);

        return res;
    }
}
