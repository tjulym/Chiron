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

Pools = ProcessPoolExecutor(max_workers=200)

def run(f, event, index):
	psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

def handle(req):
	start = time.time()

	# psutil.Process().cpu_affinity([0])

	ps = []	
	indexs = [1, 4, 2, 5, 3, 6, 9, 7, 10, 8, 11, 14, 12, 15, 13, 16, 19, 17, 20, 18, 0, 3, 1, 4, 2, 5, 8, 6, 9, 7, 10, 13, 11, 14, 12, 15, 18, 16, 19, 17, 20, 2, 0, 3, 1, 4, 7, 5, 8, 6, 9, 12, 10, 13, 11, 14, 17, 15, 18, 16, 19, 1, 20, 2, 0, 3, 6, 4, 7, 5, 8, 11, 9, 12, 10, 13, 16, 14, 17, 15, 18, 0, 19, 1, 20, 2, 5, 3, 6, 4, 7, 10, 8, 11, 9, 12, 15, 13, 16, 14, 17, 20, 18, 0, 19, 1, 4, 2, 5, 3, 6, 9, 7, 10, 8, 11, 14, 12, 15, 13, 16, 19, 17, 20, 18, 0, 3, 1, 4, 2, 5, 8, 6, 9, 7, 10, 13, 11, 14, 12, 15, 18, 16, 19, 17, 20, 2, 0, 3, 1, 4, 7, 5, 8, 6, 9, 12, 10, 13, 11, 14, 17, 15, 18, 16, 19, 1, 20, 2, 0, 3, 6, 4, 7, 5, 8, 11, 9, 12, 10, 13, 16, 14, 17, 15, 18, 0, 19, 1, 20, 2, 5, 3, 6, 4, 7, 10, 8, 11, 9]
	base_funcs = [marketdata, trddate, lastpx, volume, side]
	funcs = []
	for i in range(5):
		funcs.extend([base_funcs[i]]*40)
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, req, indexs[i]))	

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	p = Pools.submit(run, margin_balance, parallel_res, 0)

	margin_balance_res = p.result()

	margin_balance_res = json.dumps(margin_balance_res)

	result = {"result": margin_balance_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)
