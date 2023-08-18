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
        int count = 5000;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});

            if(null != mapFromStr && mapFromStr.containsKey("factorial")) {
                count = Integer.parseInt(String.valueOf(mapFromStr.get("factorial")));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return count;
    }

    private long factorial(int count) {
        long fRes = 1;
        for(int i = 1; i <= count + 1; i++) {
            fRes = fRes * i;
        }
        return fRes;
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int count = getPara(req);

        long fRes = factorial(count);

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("start", start);

        Response res = new Response();

        long end = System.currentTimeMillis();

        rlt.put("end", end);
        rlt.put("count", count);

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
