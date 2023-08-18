import threading
import multiprocessing as mp
import psutil
import json
import time
from function.margin_balance_handler import handle as margin_balance
from function.trddate_handler import handle as trddate
from function.lastpx_handler import handle as lastpx
from function.volume_handler import handle as volume
from function.side_handler import handle as side
from function.marketdata_handler import handle as marketdata
import requests

def run(fs, event, index, conn):
	psutil.Process().cpu_affinity([index])
	results = []
	ps = []
	for f in fs:
		ps.append(MyThread(runt, args=[f, event]))
	for p in ps:
		p.start()
	for p in ps:
		p.join()
		results.append(p.recv())
	
	conn.send(results)
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

def remote(index, req):
        url = "http://gateway.openfaas.svc.cluster.local:8080/function/finra-wrap%d" % index
        result = requests.post(url, data=req).json()
        return result
    
def handle(req):
	start = time.time()

	psutil.Process().cpu_affinity([0])

	ts = []
	ps = []
	parent_conns = []

	ps_fss = [[marketdata, marketdata, trddate, trddate, lastpx, lastpx, side, side, side], [marketdata, marketdata, trddate, trddate, lastpx, volume, side, side], [marketdata, marketdata, trddate, trddate, trddate, lastpx, lastpx, lastpx], [volume, volume, volume, volume, volume, volume, marketdata, marketdata], [volume, marketdata, volume, side, side, side, volume, side]]
	for i, fs in enumerate(ps_fss):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[fs, req, 1+i, child_conn]))

	for p in ps:
		p.start()

	psutil.Process().cpu_affinity([0])

	main_fs = [marketdata, trddate, trddate, trddate, lastpx, lastpx, lastpx, lastpx, side]
	for f in main_fs:
		ts.append(MyThread(runt, args=[f, req]))

	for t in ts:
		t.start()

	for t in ts:
		t.join()

	for p in ps:
		p.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.extend(parent_conn.recv())
	for t in ts:
		parallel_res.append(t.recv())

	parallel_res = json.dumps(parallel_res)

	p = MyThread(runt, args=[margin_balance, parallel_res])

	p.start()
	p.join()

	margin_balance_res = p.recv()

	margin_balance_res = json.dumps(margin_balance_res)

	result = {"result": margin_balance_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

