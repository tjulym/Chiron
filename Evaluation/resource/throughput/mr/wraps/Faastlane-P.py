from concurrent.futures import ProcessPoolExecutor
import psutil
import json
import time
from function.compose_review_handler import handle as compose_review
from function.mr_upload_text_handler import handle as mr_upload_text
from function.mr_upload_unique_id_handler import handle as mr_upload_unique_id
from function.upload_user_id_handler import handle as upload_user_id
from function.upload_movie_id_handler import handle as upload_movie_id
from function.mr_compose_and_upload_handler import handle as mr_compose_and_upload
from function.upload_user_review_handler import handle as upload_user_review
from function.store_review_handler import handle as store_review
from function.upload_movie_review_handler import handle as upload_movie_review

Pools = ProcessPoolExecutor(max_workers=4)

def run(f, event, index):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

def handle(req):
	start = time.time()
	#psutil.Process().cpu_affinity([0])

	p = Pools.submit(run, compose_review, req, 0)

	compose_res = p.result()

	ps = []	
	for i, f in enumerate([upload_user_id, upload_movie_id, mr_upload_text, mr_upload_unique_id]):
		ps.append(Pools.submit(run, f, compose_res, i))	

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	p = Pools.submit(run, mr_compose_and_upload, parallel_res, 0)

	compose_and_upload_res = p.result()

	ps = []
	for i, f in enumerate([store_review, upload_user_review, upload_movie_review]):
		ps.append(Pools.submit(run, f, compose_and_upload_res, i))

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

