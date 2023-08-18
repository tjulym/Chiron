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

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    private int getPara(IRequest req) {
        int count = 1000;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});

            if(null != mapFromStr && mapFromStr.containsKey("pbkdf2")) {
                count = Integer.parseInt(String.valueOf(mapFromStr.get("pbkdf2")));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return count;
    }

    private String pbkdf2(int count) {
        char[] password = "ServerlessAppPerfOpt".toCharArray();
        byte[] salt = "salt".getBytes();
        try {
            final PBEKeySpec spec = new PBEKeySpec(password, salt, count, 18 * 8);
            final SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA512");
            byte[] hash = skf.generateSecret(spec)
                    .getEncoded();
            String res = new String(hash);
            return res;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "Done";
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int count = getPara(req);

        String fRes = pbkdf2(count);

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
