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

import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.BufferedReader;
import java.net.HttpURLConnection;
import java.net.URL;

import java.util.Calendar;
import java.util.GregorianCalendar;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        String reqBody = req.getBody();

        Marketdata tMarketdata = new Marketdata(reqBody);
        Lastpx tLastpx = new Lastpx(reqBody);
        Side tSide = new Side(reqBody);
        Trddate tTrddate = new Trddate(reqBody);
        Volume tVolume = new Volume(reqBody);

        tMarketdata.start();
        tLastpx.start();
        tSide.start();
        tTrddate.start();
        tVolume.start();

        try {
            tMarketdata.join();
            tLastpx.join();
            tSide.join();
            tTrddate.join();
            tVolume.join();
        } catch (Exception e) {
            e.printStackTrace();
        }

        String[] midRes = new String[]{"", "", "", "", ""};
        midRes[0] = tMarketdata.getRes();
        midRes[1] = tLastpx.getRes();
        midRes[2] = tSide.getRes();
        midRes[3] = tTrddate.getRes();
        midRes[4] = tVolume.getRes();

        String midResStr = null;

        try {
            midResStr = mapper.writeValueAsString(midRes);
        } catch (Exception e) {
            e.printStackTrace();
        }

        MarginBalance tMarginBalance = new MarginBalance(midResStr);
        tMarginBalance.start();
        try {
            tMarginBalance.join();
        } catch (Exception e) {
            e.printStackTrace();
        }

        String MarginBalanceRes = tMarginBalance.getRes();

        Map<String, Object> rlt = new HashMap<>();
        rlt.put("start", start);
        rlt.put("result", MarginBalanceRes);

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

class Marketdata extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();

    public String doPost(String url, String param) {
        OutputStreamWriter out = null;
        BufferedReader in = null;
        StringBuilder sresult = new StringBuilder();

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
                sresult.append(line);
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
        return sresult.toString();
    }

    public Marketdata(String r) {
        req = r;
    }   

    public String getRes() {
        return result;
    }

    public void run() {
        long start = System.currentTimeMillis();

        Map<String, String[]> tickersForPortfolioTypes = new HashMap<String, String[]>();
        tickersForPortfolioTypes.put("S&P", new String[]{"GOOG", "AMZN", "MSFT"});

        String portfolioType = "S&P";
        String tickers[] = {"GOOG", "AMZN", "MSFT"};

        try {
            JsonNode inputNode = mapper.readTree(req);
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

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }   
}

class Lastpx extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public Lastpx(String r) {
        req = r;
    }   

    public String getRes() {
        return result;
    }   

    public void run() {
        long start = System.currentTimeMillis();

        String portfolio = "1234";

        try {
            JsonNode inputNode = mapper.readTree(req);
            portfolio = inputNode.get("body").get("portfolio").asText();
        } catch (Exception e) {
            e.printStackTrace();
        }   

        boolean valid = true;
        try {
            JsonNode fileNode = mapper.readTree(portfolios);
            JsonNode data = fileNode.get(portfolio);

            for (JsonNode trade: data) {
                String px = trade.get("LastPx").asText();
                if (px.contains(".")) {
                    String splits[] = px.split("\\.");
                    String a = splits[0];
                    String b = splits[1];
                    if (!((a.length() == 3 && b.length() == 6) || (a.length() == 4 && b.length() == 5) ||  
                          (a.length() == 5 && b.length() == 4) || (a.length() == 6 && b.length() == 3))) {
                        valid = false;
                        break;
                    }   
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

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }   
}

class Side extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public Side(String r) {
        req = r;
    }   

    public String getRes() {
        return result;
    }

    public void run() {
        long start = System.currentTimeMillis();

        String portfolio = "1234";

        try {
            JsonNode inputNode = mapper.readTree(req);
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

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

class Trddate extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public Trddate(String r) {
        req = r;
    }

    public String getRes() {
        return result;
    }

    public void run() {
        long start = System.currentTimeMillis();

        String portfolio = "1234";

        try {
            JsonNode inputNode = mapper.readTree(req);
            portfolio = inputNode.get("body").get("portfolio").asText();
        } catch (Exception e) {
            e.printStackTrace();
        }   

        boolean valid = true;
        try {
            JsonNode fileNode = mapper.readTree(portfolios);
            JsonNode data = fileNode.get(portfolio);

            for (JsonNode trade: data) {
                String trddate = trade.get("TradeDate").asText();
                if (trddate.length() == 6) {
                    int year = 2000 + Integer.valueOf(trddate.substring(0, 2)).intValue();
                    int month = Integer.valueOf(trddate.substring(2, 4)).intValue();
                    int day = Integer.valueOf(trddate.substring(4, 6)).intValue();
                    Calendar myCalendar = new GregorianCalendar(year, month, day);
                } else {
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

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

class Volume extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public Volume(String r) {
        req = r;
    }

    public String getRes() {
        return result;
    }

    public void run() {
        long start = System.currentTimeMillis();

        String portfolio = "1234";

        try {
            JsonNode inputNode = mapper.readTree(req);
            portfolio = inputNode.get("body").get("portfolio").asText();
        } catch (Exception e) {
            e.printStackTrace();
        }   

        boolean valid = true;
        try {
            JsonNode fileNode = mapper.readTree(portfolios);
            JsonNode data = fileNode.get(portfolio);

            for (JsonNode trade: data) {
                String qty = trade.get("LastQty").asText();
                if (qty.length() > 8 || qty.contains(".")) {
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
        
        long end = System.currentTimeMillis();
        
        rlt.put("end", end);
        
        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

class MarginBalance extends Thread {
    private String req;
    private String result;
    private ObjectMapper mapper = new ObjectMapper();
    private String portfolios = "{\"1234\": [{\"Security\": \"GOOG\", \"LastQty\": 10, \"LastPx\": 1363.85123, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}, {\"Security\": \"MSFT\", \"LastQty\": 20, \"LastPx\": 183.851234, \"Side\": 1, \"TrdSubType\": 0, \"TradeDate\": \"200507\"}]}";

    public MarginBalance(String r) {
        req = r;
    }

    public String getRes() {
        return result;
    }

    public void run() {
        long start = System.currentTimeMillis();

        Map<String, Double> marketData = new HashMap<>();
        String portfolio = "1234";
        boolean validFormat = true;

        try {
            JsonNode inputNode = mapper.readTree(req);
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

        long end = System.currentTimeMillis();

        rlt.put("end", end);

        try {
            result = mapper.writeValueAsString(rlt);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
