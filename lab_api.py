"""In-memory, bounded simulation jobs; no physical control adapters."""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import uuid
from benchmark import compare_scenario
POOL=ThreadPoolExecutor(max_workers=1)
JOBS={}; LOCK=Lock()
def submit(data):
    if set(data)-{'scenario','controller'}: raise ValueError('Unknown fields')
    name=data.get('scenario','storm72'); controller=data.get('controller','baseline')
    if name not in ('sunny','downpour','storm72') or controller not in ('baseline','meta'): raise ValueError('Invalid run configuration')
    if controller=='meta':
        from agent import MetaTransport
        MetaTransport()  # fail clearly before queuing when no key
    with LOCK:
        if any(not f.done() for f in JOBS.values()): raise ValueError('A run is already active')
        while len(JOBS)>=8: JOBS.pop(next(iter(JOBS)))
        key=uuid.uuid4().hex
        JOBS[key]=POOL.submit(compare_scenario,name,controller=='meta')
    return {'job':key}
def poll(key):
    with LOCK: future=JOBS.get(key)
    if future is None: return {'status':'unknown'}
    if not future.done(): return {'status':'running'}
    try: return {'status':'complete','result':future.result()}
    except Exception: return {'status':'failed','error':'Simulation job failed'}
