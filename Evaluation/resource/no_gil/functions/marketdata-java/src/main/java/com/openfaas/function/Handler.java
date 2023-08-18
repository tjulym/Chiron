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

import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.BufferedReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    public String doPost(String url, String param) {
        OutputStreamWriter out = null;
        BufferedReader in = null;
        StringBuilder result = new StringBuilder();

        try {
            URL realUrl = new URL(url);
            HttpURLConnection conn =(HttpURLConnection) realUrl.openConnection();
            conn.setDoOutput(true);
            conn.setDoInput(true);
            conn.setRequestMethod("POST");
            //conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            conn.connect();
            out = new OutputStreamWriter(conn.getOutputStream(), "UTF-8");
            out.write(param);

            out.flush();
            in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
            String line;
            while ((line = in.readLine()) != null) {
                result.append(line);
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if(out != null){
                    out.close();
                }
                if(in != null){
                    in.close();
                }
            } catch(Exception e){
                e.printStackTrace();
            }
        }
        return result.toString();
    }

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        Map<String, String[]> tickersForPortfolioTypes = new HashMap<String, String[]>();
        tickersForPortfolioTypes.put("S&P", new String[]{"GOOG", "AMZN", "MSFT"});

        String portfolioType = "S&P";
        String tickers[] = {"GOOG", "AMZN", "MSFT"};

        try {
            JsonNode inputNode = mapper.readTree(req.getBody());
            portfolioType = inputNode.get("body").get("portfolioType").asText();

            String [] tarTickers = tickersForPortfolioTypes.get(portfolioType);

            for (int i = 0; i < tarTickers.length; i++) {
                tickers[i] = tarTickers[i];
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        Map<String, Double> prices = new HashMap<>();

        String url = "http://192.168.1.106:31112/function/yfinance";
        for (String ticker: tickers) {
            double price = 1000.0;
            String data = doPost(url, ticker);
            try {
                JsonNode dataNode = mapper.readTree(data);
                String priceStr = String.valueOf(dataNode.get("chart").get("result").get(0).get("indicators").get("quote").get(0).get("close").get(0));
                price = Double.parseDouble(priceStr);
                prices.put(ticker, price);
            } catch(Exception e){
                e.printStackTrace();
            }
        }

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("marketData", prices);

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
