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

import org.apache.commons.lang3.RandomStringUtils;
import java.io.*;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    private static final String FILE_PATH = "/tmp/diskio";

    private int getPara(IRequest req) {
        int count = 1;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});

            if(null != mapFromStr && mapFromStr.containsKey("disk-io")) {
                count = Integer.parseInt(String.valueOf(mapFromStr.get("disk-io")));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return count;
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int count = getPara(req);

        File file = new File(FILE_PATH);
        if(file.exists()) {
            try {
                file.delete();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        try {
            for(int i = 1; i <= count; i++) {
                String str = RandomStringUtils.randomAscii(1048576);
                BufferedWriter out = new BufferedWriter(new FileWriter(FILE_PATH));
                out.write(str);
                out.close();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

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
