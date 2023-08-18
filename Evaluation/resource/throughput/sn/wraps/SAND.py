import threading
import multiprocessing as mp
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

def run(f, event, index, conn):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
	conn.send(result)
	conn.close()
    
def handle(req):
	start = time.time()

	parent_conn, child_conn = mp.Pipe()
	p = mp.Process(target=run, args=[compose_post, req, 0, child_conn])

	p.start()
	p.join()

	compose_res = parent_conn.recv()

	ps = []	
	parent_conns = []
	for i, f in enumerate([upload_user_mentions, upload_creator, upload_media, upload_text, upload_unique_id]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, compose_res, i, child_conn]))	

	for p in ps:
		p.start()

	for p in ps:
		p.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.append(parent_conn.recv())

	parallel_res = json.dumps(parallel_res)

	parent_conn, child_conn = mp.Pipe()
	p = mp.Process(target=run, args=[compose_and_upload, parallel_res, 0, child_conn])

	p.start()
	p.join()

	compose_and_upload_res = parent_conn.recv()

	ps = []
	parent_conns = []
	for i, f in enumerate([post_storage, upload_home_timeline, upload_user_timeline]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, compose_and_upload_res, i, child_conn]))

	for p in ps:
		p.start()

	for p in ps:
		p.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.append(parent_conn.recv())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

