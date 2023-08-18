package com.openfaas.function;

import com.openfaas.model.IHandler;
import com.openfaas.model.IResponse;
import com.openfaas.model.IRequest;
import com.openfaas.model.Response;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.HashMap;
import java.util.Map;
import java.lang.System;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        String portfolio = "1234";

        try {
            JsonNode inputNode = mapper.readTree(req.getBody());
            portfolio = inputNode.get("body").get("portfolio").asText();
        } catch (Exception e) {
            e.printStackTrace();
        }

        boolean valid = true;
        try {
            JsonNode fileNode = mapper.readTree(portfolios);
            JsonNode data = fileNode.get(portfolio);

            for (JsonNode trade: data) {
                int side = Integer.parseInt(trade.get("Side").asText());
                if (!(side == 1 || side == 2 || side == 8)) {
                    valid = false;
                    break;
                }
            }
        } catch (Exception e) {
            valid = false;
            e.printStackTrace();
        }

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("valid", valid);
        rlt.put("portfolio", portfolio);

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
