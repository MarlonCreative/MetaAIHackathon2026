from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json,os
from local_config import meta_key
from lab_api import submit,poll
from engine import SCENARIOS,evaluate,validate,muse_analysis,demo_analysis
from stack import DEFAULT_STACK,DEFAULT_ASSUMPTIONS,compare
ROOT=Path(__file__).resolve().parent
class Handler(BaseHTTPRequestHandler):
 def reply(self,n,obj):
  b=json.dumps(obj).encode();self.send_response(n);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  route=urlparse(self.path).path
  if route.startswith('/api/lab/jobs/'): return self.reply(200,poll(route.rsplit('/',1)[-1]))
  if route=='/api/lab/status': return self.reply(200,{'meta_configured':bool(meta_key())})
  if route=='/lab-bridge.js':
   b=(ROOT/'lab-bridge.js').read_bytes();self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
  if route=='/api/home-stack': return self.reply(200,{'stack':DEFAULT_STACK,'assumptions':DEFAULT_ASSUMPTIONS})
  if route=='/api/scenarios': return self.reply(200,{'scenarios':SCENARIOS,'live_available':bool(meta_key())})
  if route=='/digital-twin.html':
   b=(ROOT/'digital-twin.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
  if route in ['/','/index.html']:
   b=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
  return self.reply(404,{'error':'Not found'})
 def do_POST(self):
  route=urlparse(self.path).path
  if route not in ('/api/evaluate','/api/compare-stack','/api/lab/run'):return self.reply(404,{'error':'Not found'})
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<10000:return self.reply(413,{'error':'Invalid payload size'})
   data=json.loads(self.rfile.read(n))
   if not isinstance(data,dict): raise ValueError('Expected an object')
   if route=='/api/lab/run': return self.reply(202,submit(data))
   if route=='/api/compare-stack':return self.reply(200,compare(data.get('assumptions',{})))
   s=validate(data.get('readings'));decision=evaluate(s)
   mode=data.get('mode','demo')
   if mode=='live':
    if not meta_key():return self.reply(400,{'error':'Set MODEL_API_KEY in the ignored local .env file.'})
    analysis=muse_analysis(s,decision,meta_key())
   else:analysis=demo_analysis(s,decision)
   return self.reply(200,{'decision':decision,'analysis':analysis,'readings':s,'mode':mode})
  except ValueError as e:return self.reply(400,{'error':str(e)})
  except Exception:return self.reply(502,{'error':'Provider or simulation request failed'})
if __name__=='__main__':
 port=int(os.getenv('PORT','8766'));print(f'CasaOS on http://127.0.0.1:{port} | live Meta configured: {bool(meta_key())}');ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
