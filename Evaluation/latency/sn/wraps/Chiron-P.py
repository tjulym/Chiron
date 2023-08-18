import threading
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import psutil
import json
import time
from function.compose_post_handler import handle as compose_post
from function.upload_user_mentions_handler import handle as upload_user_mentions
from function.upload_creator_handler import handle as upload_creator
from function.upload_media_handler import handle as upload_media
from function.upload_text_handler import handle as upload_text
from function.upload_unique_id_handler import handle as upload_unique_id
from function.compose_and_upload_handler import handle as compose_and_upload
from function.post_storage_handler import handle as post_storage
from function.upload_home_timeline_handler import handle as upload_home_timeline
from function.upload_user_timeline_handler import handle as upload_user_timeline

Pools = ProcessPoolExecutor(max_workers=5)

def run(f, event, index):
	psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

def handle(req):
	start = time.time()

	psutil.Process().cpu_affinity([0])

	p = Pools.submit(run, compose_post, req, 0)


	compose_res = p.result()

	ps = []
	indexs = [0, 1, 1, 0, 0]
	funcs = [upload_user_mentions, upload_creator, upload_text, upload_unique_id, upload_media]	
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, compose_res, i))

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	p = Pools.submit(run, compose_and_upload, parallel_res, 0)

	compose_and_upload_res = p.result()

	ps = []
	indexs = [0, 1, 1]
	funcs = [upload_home_timeline, upload_user_timeline, post_storage]
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, compose_and_upload_res, i))

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

