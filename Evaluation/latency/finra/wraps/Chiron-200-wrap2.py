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
    
def handle(req):
	psutil.Process().cpu_affinity([6])
	start_index = 6

	ps = []
	parent_conns = []

	ps_fss = [[marketdata, marketdata, marketdata, trddate, trddate, trddate, trddate, lastpx, lastpx, lastpx, volume, volume, volume, volume, side, side, side, side], [marketdata, marketdata, marketdata, marketdata, trddate, trddate, trddate, trddate, lastpx, lastpx, lastpx, lastpx, volume, volume, volume, volume, side, side], [marketdata, trddate, trddate, lastpx, lastpx, marketdata, lastpx, trddate, side, trddate, side, volume, marketdata, side, marketdata, volume, lastpx, volume], [trddate, marketdata, marketdata, marketdata, volume, side, side, lastpx, marketdata, trddate, lastpx, lastpx, lastpx, volume, trddate, side, trddate, side]]
	for i, fs in enumerate(ps_fss):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[fs, req, start_index+i+1, child_conn]))

	for p in ps:
		p.start()

	psutil.Process().cpu_affinity([start_index])

	ts = []
	main_fs = [marketdata, marketdata, marketdata, marketdata, trddate, trddate, trddate, lastpx, lastpx, lastpx, lastpx, volume, volume, volume, side, side, side, side]
	for f in main_fs:
		ts.append(MyThread(runt, args=[f, req]))

	for t in ts:
		t.start()

	for p in ps:
		p.join()

	for t in ts:
		t.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.extend(parent_conn.recv())
	for t in ts:
		parallel_res.append(t.recv())

	parallel_res = json.dumps(parallel_res)

	return parallel_res

