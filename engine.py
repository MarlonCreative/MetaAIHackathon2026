"""CasaOS demonstrator: conservative deterministic planner; no physical actuators."""
import json, urllib.request
from secure_http import tls_context

SCENARIOS = {
 'normal': {'label':'Normal Day','grid':True,'battery':82,'solar_kw':2.5,'water':78,'internet':True,'temp_c':31,'pump_fault':False},
 'outage': {'label':'Power Outage','grid':False,'battery':42,'solar_kw':0.1,'water':68,'internet':False,'temp_c':32,'pump_fault':False},
 'water': {'label':'Low Water','grid':True,'battery':64,'solar_kw':1.5,'water':16,'internet':True,'temp_c':33,'pump_fault':False},
 'compound': {'label':'Compound Emergency','grid':False,'battery':17,'solar_kw':0,'water':12,'internet':False,'temp_c':35,'pump_fault':True}
}
LOADS = [
 {'name':'Refrigerator','watts':160,'priority':1,'house':'Main house'},
 {'name':'Connectivity / router','watts':30,'priority':1,'house':'Main house'},
 {'name':'Laptop 1','watts':65,'priority':2,'house':'Main house'},
 {'name':'Laptop 2','watts':65,'priority':2,'house':'Small house'},
 {'name':'Water pump','watts':550,'priority':2,'house':'Shared infrastructure'},
 {'name':'AC 1','watts':850,'priority':3,'house':'Main house'},
 {'name':'AC 2','watts':850,'priority':3,'house':'Main house'},
 {'name':'AC 3','watts':850,'priority':3,'house':'Small house'},
 {'name':'AC 4','watts':850,'priority':3,'house':'Small house'},
]
CAPACITY_KWH=10.0  # hypothetical, NOT installed battery

def validate(s):
 if not isinstance(s,dict): raise ValueError('Readings must be an object')
 for k in ['grid','internet','pump_fault']:
  if type(s.get(k)) is not bool: raise ValueError(f'{k} must be boolean')
 for k,lo,hi in [('battery',0,100),('solar_kw',0,20),('water',0,100),('temp_c',0,55)]:
  if type(s.get(k)) not in (int,float) or not lo <= s[k] <= hi: raise ValueError(f'{k} must be between {lo} and {hi}')
 return s

def evaluate(s):
 validate(s)
 alerts=[]; actions=[]; status='STABLE'; enabled=[]; deferred=[]
 def add(level,category,message): alerts.append({'severity':level,'category':category,'message':message})
 if not s['grid']:
  status='WATCH';add('warning','Power','Grid unavailable; operating on hypothetical solar/battery backup')
 if s['battery']<30:
  status='CRITICAL';add('critical','Energy','Battery below 30%; protect essential loads')
 elif s['battery']<55 and not s['grid']:
  add('warning','Energy','Limit nonessential electricity usage')
 if s['water']<20:
  status='CRITICAL';add('critical','Water','Cistern critically low; restrict nonessential usage')
 elif s['water']<35:add('warning','Water','Water supply low; plan refill')
 if s['pump_fault']:
  status='CRITICAL';add('critical','Water','Pump fault simulated; do not attempt automatic reset')
 if not s['internet']: add('warning','Connectivity','Internet unavailable; local policy evaluation remains available')
 for load in LOADS:
  name=load['name']; reason=None
  if name.startswith('AC') and (not s['grid'] or s['battery']<45): reason='Defer cooling to conserve backup energy'
  if name=='Water pump' and (s['pump_fault'] or s['water']<20 or (not s['grid'] and s['battery']<35)):
   reason='No pumping: fault, low cistern, or energy preservation'
  if name.startswith('Laptop') and not s['grid'] and s['battery']<25:reason='Reserve remaining power for refrigerator and communications'
  if reason:deferred.append({**load,'reason':reason})
  else:enabled.append(load)
 if not s['grid']:
  actions.append({'risk':'low','action':'Recommend keeping refrigeration and communications prioritized','why':'Protect food and basic communications'})
 if any(x['name'].startswith('AC') for x in deferred):actions.append({'risk':'low','action':'Recommend delaying air conditioning','why':'Reduce battery draw during shortage'})
 if s['water']<35:actions.append({'risk':'low','action':'Recommend conserving stored water and arranging refill','why':'Cistern below reserve threshold'})
 if s['pump_fault']: actions.append({'risk':'requires-human','action':'Request a manual pump inspection','why':'Automatic restart is prohibited in this prototype'})
 if not actions:actions.append({'risk':'low','action':'Continue monitoring; no intervention recommended','why':'Inputs remain within scenario thresholds'})
 total=sum(x['watts'] for x in enabled)
 # Estimated run time uses 80% usable capacity, no solar/charging input and fixed loads; not an engineering prediction
 runtime=round((CAPACITY_KWH*(s['battery']/100)*0.8)/(total/1000),1) if total else None
 return {'status':status,'alerts':alerts,'recommendations':actions,'enabled':enabled,'deferred':deferred,'estimated_watts':total,'illustrative_runtime_hours':runtime,'energy_model':'Illustrative 10 kWh battery, 80% usable factor, constant assumed loads; excludes solar input and real-world losses. Not validated system sizing.','policy_rules':['Never directly switch real equipment','Do not auto-reset a failed pump','Conserve refrigeration and communication power during outage','Defer air conditioning without grid','Require human review of any high-risk actuation']}

def muse_analysis(s,decision,key):
 prompt='''You are CasaOS, a safety-conscious rural home resilience assistant for a TWO-house property in coastal El Salvador. Inputs are SIMULATED. NEVER imply you control equipment. The deterministic policy result is authoritative; do not override it. Give a concise response with three sections: Situation, Why, What the homeowner should do. Focus on off-grid resilience, seasonal heat, cistern water, and remote management. Distinguish measured from hypothetical assumptions. Avoid asserting backup runtime as an exact estimate.\n\n'''+json.dumps({'readings':s,'policy':decision},ensure_ascii=False)
 req=urllib.request.Request('https://api.meta.ai/v1/responses',data=json.dumps({'model':'muse-spark-1.3','instructions':'Be accurate, practical, and clear. Do not propose unsafe automatic actuation.','input':prompt,'store':False,'max_output_tokens':256}).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=20,context=tls_context()) as resp:
  obj=json.load(resp)
 return '\n'.join(part.get('text','') for item in obj.get('output',[]) if item.get('type')=='message' for part in item.get('content',[]) if part.get('type')=='output_text')

def demo_analysis(s,decision):
 message=('The grid is down. ' if not s['grid'] else 'Grid power is available. ')+f"Stored water is at {s['water']}% and the hypothetical battery at {s['battery']}%. "
 if decision['status']=='CRITICAL': message+='At least one critical reserve or equipment fault requires attention. '
 elif decision['status']=='WATCH':message+='The house is operating in a conservation state. '
 else:message+='Current indicators appear stable. '
 message+='This analysis uses deterministic local rules; enable Muse Spark for an AI-generated explanation.'
 return message
