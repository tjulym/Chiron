import json
from time import time
import os

from minio import Minio

minioClient = Minio("minio-service.default.svc.cluster.local:9000", access_key="admin123", secret_key="admin123", secure=False)

path = "/tmp/data"

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = {}
    response = {"time": {"network-io": {"start_time": start}}}

    event = json.loads(req)

    minioClient.fget_object("network-io", object_name="data", file_path=path)
    minioClient.remove_object("network-io", "data")
    minioClient.fput_object("network-io", object_name="data", file_path=path)

    os.remove(path)

    response["body"] = event
    response["time"]["network-io"]["end_time"] = time()
    return json.dumps(response)
