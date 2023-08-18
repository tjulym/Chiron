package com.openfaas.function;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import com.openfaas.model.IHandler;
import com.openfaas.model.IResponse;
import com.openfaas.model.IRequest;
import com.openfaas.model.Response;

import java.util.HashMap;
import java.util.Map;
import java.lang.System;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    private int getPara(IRequest req) {
        int count = 23;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});

            if(null != mapFromStr && mapFromStr.containsKey("fibonacci")) {
                count = Integer.parseInt(String.valueOf(mapFromStr.get("fibonacci")));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return count;
    }

    private long fibonacci(int n) {
        if(n <= 1) {
            return n;
        }
        else {
            return fibonacci(n - 1) + fibonacci(n - 2);
        }
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int count = getPara(req);

        long fRes = fibonacci(count);

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("start", start);

        Response res = new Response();

        long end = System.currentTimeMillis();

        rlt.put("end", end);
        rlt.put("fibonacci", count);

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
