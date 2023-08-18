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
        int count = 1000;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});

            if(null != mapFromStr && mapFromStr.containsKey("pi")) {
                count = Integer.parseInt(String.valueOf(mapFromStr.get("pi")));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return count;
    }

    private double pi(int count) {
        double fRes = 0.0;
        double termx = 0.0;
        for(int i = 1; i <= count + 1; i++) {
            if(i%2 == 0) {
                termx = (double)-4/(2*i-1);
            } else {
                termx=(double)4/(2*i-1);
            }
            fRes += termx;
        }
        return fRes;
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int count = getPara(req);

        double fRes = pi(count);

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
