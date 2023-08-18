from concurrent.futures import ProcessPoolExecutor
import psutil
import json
import time
from function.margin_balance_handler import handle as margin_balance
from function.trddate_handler import handle as trddate
from function.lastpx_handler import handle as lastpx
from function.volume_handler import handle as volume
from function.side_handler import handle as side
from function.marketdata_handler import handle as marketdata

Pools = ProcessPoolExecutor(max_workers=50)

def run(f, event, index):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

def handle(req):
	start = time.time()

	#psutil.Process().cpu_affinity([0])

	ps = []	
	for i, f in enumerate([marketdata, lastpx, side, trddate, volume]*10):
		ps.append(Pools.submit(run, f, req, i))	

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	p = Pools.submit(run, margin_balance, parallel_res, 0)

	margin_balance_res = p.result()

	margin_balance_res = json.dumps(margin_balance_res)

	result = {"result": margin_balance_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)
