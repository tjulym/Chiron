import threading
import multiprocessing as mp
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

def run(f, event, index, conn):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
	conn.send(result)
	conn.close()

class MyThread(threading.Thread):
	def __init__(self, func, args=()):
		threading.Thread.__init__(self)
		self.func = func
		self.args = args

	def run(self):
		self.result = self.func(*self.args)

	def recv(self):
		try:
			return self.result
		except Exception:
			return None

def runt(f, event):
	result = f(event)
	return result
    
def handle(req):
	start = time.time()
	#psutil.Process().cpu_affinity([0])

	p = MyThread(runt, args=[compose_review, req])

	p.start()
	p.join()

	compose_res = p.recv()

	ps = []	
	parent_conns = []
	for i, f in enumerate([upload_user_id, upload_movie_id, mr_upload_text, mr_upload_unique_id]):
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

	p = MyThread(runt, args=[mr_compose_and_upload, parallel_res])

	p.start()
	p.join()

	compose_and_upload_res = p.recv()

	ps = []
	parent_conns = []
	for i, f in enumerate([store_review, upload_user_review, upload_movie_review]):
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

