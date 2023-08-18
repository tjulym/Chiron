package com.openfaas.function;

import com.openfaas.model.IHandler;
import com.openfaas.model.IResponse;
import com.openfaas.model.IRequest;
import com.openfaas.model.Response;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;
import java.lang.System;

import io.minio.MinioClient;
import io.minio.UploadObjectArgs;
import io.minio.DownloadObjectArgs;
import io.minio.RemoveObjectArgs;

import org.apache.commons.lang3.RandomStringUtils;
import java.io.*;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

        int facCount = 10000000;
        int fibCount = 33;
        int diskCount = 1;
        int piCount = 10000000;
        int pbkdf2Count = 10000;

        try {
            Map<String, Object> mapFromStr = mapper.readValue(req.getBody(),
                    new TypeReference<Map<String, Object>>() {});
                    
            if(null != mapFromStr) {
                if(mapFromStr.containsKey("factorial")){
                    facCount = Integer.parseInt(String.valueOf(mapFromStr.get("factorial")));
                }
                if(mapFromStr.containsKey("fibonacci")){
                    fibCount = Integer.parseInt(String.valueOf(mapFromStr.get("fibonacci")));
                }
                if(mapFromStr.containsKey("disk-io")){
                    diskCount = Integer.parseInt(String.valueOf(mapFromStr.get("disk-io")));
                }
                if(mapFromStr.containsKey("pi")){
                    piCount = Integer.parseInt(String.valueOf(mapFromStr.get("pi")));
                }
                if(mapFromStr.containsKey("pbkdf2")){
                    pbkdf2Count = Integer.parseInt(String.valueOf(mapFromStr.get("pbkdf2")));
                }
            }   
        } catch (Exception e) {
            e.printStackTrace();
        }

        Factorial tFac = new Factorial(facCount);
        Fibonacci tFib = new Fibonacci(fibCount);
        Diskio tDisk = new Diskio(diskCount);
        Networkio tNet = new Networkio();

        tNet.start();
        tFac.start();
        tDisk.start();
        tFib.start();

        try {
            tNet.join();
            tFac.join();
            tDisk.join();
            tFib.join();
        } catch (Exception e) {
            e.printStackTrace();
        }

        Networkio tNet2 = new Networkio();
        Pi tPi = new Pi(piCount);
        Pbkdf2 tPbkdf2 = new Pbkdf2(pbkdf2Count);

        tNet2.start();
        tPi.start();
        tPbkdf2.start();
 
        try {
            tNet2.join();
            tPi.join();
            tPbkdf2.join();
        } catch (Exception e) {
            e.printStackTrace();
        }

        Map<String, Object> rlt = new HashMap<>();
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

class Factorial extends Thread {
    private int count;

    public Factorial(int n) {
        count = n;
    }

    public void run() {
        long fRes = 1;
        for(int i = 1; i <= count + 1; i++) {
            fRes = fRes * i;
        }   
    }
}

class Fibonacci extends Thread {
    private int count;

    public Fibonacci(int n) {
        count = n;
    }

    public long fib(int n) {
        if(n <= 1) {
            return n;
        }   
        else {
            return fib(n - 1) + fib(n - 2); 
        }
    }

    public void run() {
        long fRes = fib(count);
    }
}

class Diskio extends Thread {
    private int count;
    private static final String FILE_PATH = "/tmp/diskio";

    public Diskio(int n) {
        count = n;
    }

    public void run() {
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
    }
}

class Networkio extends Thread {
    private static final String FILE_PATH = "/tmp/data";
    private static final String URL = "http://minio-service.default.svc.cluster.local:9000";
    private static final String ACCESS_KEY = "admin123";
    private static final String SECRET_KEY = "admin123";

    public Networkio() {
    }

    public void run() {
        try {
            MinioClient minioClient =
                MinioClient.builder()
                    .endpoint(URL)
                    .credentials(ACCESS_KEY, SECRET_KEY)
                    .build();

            minioClient.downloadObject(
                DownloadObjectArgs.builder()
                    .bucket("network-io")
                    .object("data")
                    .filename(FILE_PATH)
                    .build());

            minioClient.removeObject(
                RemoveObjectArgs.builder().bucket("network-io").object("data").build());

            minioClient.uploadObject(
                UploadObjectArgs.builder()
                    .bucket("network-io")
                    .object("data")
                    .filename(FILE_PATH)
                    .build());

            File file = new File(FILE_PATH);
            file.delete();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

class Pi extends Thread {
    private int count;

    public Pi(int n) {
        count = n;
    }   

    public void run() {
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
    }
}

class Pbkdf2 extends Thread {
    private int count;

    public Pbkdf2(int n) {
        count = n;
    }

    public void run() {
        char[] password = "ServerlessAppPerfOpt".toCharArray();
        byte[] salt = "salt".getBytes();
        try {
            final PBEKeySpec spec = new PBEKeySpec(password, salt, count, 18 * 8); 
            final SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA512");
            byte[] hash = skf.generateSecret(spec)
                    .getEncoded();
            String res = new String(hash);
        } catch (Exception e) {
            e.printStackTrace();
        } 
    }
}
