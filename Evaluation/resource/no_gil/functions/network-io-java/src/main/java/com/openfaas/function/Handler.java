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

import io.minio.MinioClient;
import io.minio.UploadObjectArgs;
import io.minio.DownloadObjectArgs;
import io.minio.RemoveObjectArgs;
import io.minio.errors.MinioException;

import java.io.*;

public class Handler implements com.openfaas.model.IHandler {
    private ObjectMapper mapper = new ObjectMapper();
    private static final String FILE_PATH = "/tmp/data";
    private static final String URL = "http://minio-service.default.svc.cluster.local:9000";
    private static final String ACCESS_KEY = "admin123";
    private static final String SECRET_KEY = "admin123";

    public IResponse Handle(IRequest req) {
        long start = System.currentTimeMillis();

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
