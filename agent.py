"""Actual Meta function-call loop. No generated plan is executed as prose."""
import json, os, urllib.request, time
from copy import deepcopy
from simulation import baseline
from local_config import meta_key, settings
from secure_http import tls_context

CONTROLS = {'type':'object','properties':{'control':{'type':'string','enum':['optional','pump','generator','reserve']},'value':{'anyOf':[{'type':'boolean'},{'type':'number'}]}},'required':['control','value'],'additionalProperties':False}
TOOLS = []
for name, description, parameters in [
 ('read_sensors','Read current virtual sensors and unexpected events.',{'type':'object','properties':{},'additionalProperties':False}),
 ('inspect_home_stack','Inspect illustrative equipment and dependencies.',{'type':'object','properties':{},'additionalProperties':False}),
 ('forecast_resources','Estimate next six hours, holding current weather; does not reveal future faults.',{'type':'object','properties':{},'additionalProperties':False}),
 ('evaluate_action','Preview one action and next tick without changing the real simulation.',CONTROLS),
 ('request_control_action','Change permitted simulated equipment settings through safety gate.',CONTROLS),
 ('inspect_outcome','Inspect last completed tick and accumulated service metrics.',{'type':'object','properties':{},'additionalProperties':False})]:
    TOOLS.append({'type':'function','function':{'name':name,'description':description,'parameters':parameters}})

class MetaTransport:
    def __init__(self):
        self.key = meta_key()
        if not self.key: raise ValueError('Meta credentials unavailable')
        self.model = settings().get('META_MODEL','muse-spark-1.3')
    def __call__(self, messages):
        req = urllib.request.Request('https://api.meta.ai/v1/chat/completions',
            data=json.dumps(dict(model=self.model,messages=messages,tools=TOOLS,tool_choice='auto',temperature=0)).encode(),
            headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=30,context=tls_context()) as response:
            return json.load(response)['choices'][0]['message']

class MetaAgent:
    def __init__(self, transport=None):
        self.transport = transport or MetaTransport()
        self.audit = []; self.failed = False
    def tool(self, sim, name, args):
        if name in ('request_control_action','evaluate_action'):
            if name == 'request_control_action': return sim.action(args)
            preview = deepcopy(sim); result = preview.action(args)
            return dict(policy=result, next_tick=preview.step())
        if args != {}: raise ValueError('Read tools require empty arguments')
        if name == 'read_sensors': return sim.observe()
        if name == 'inspect_home_stack': return dict(equipment=sim.observe()['equipment'],dependencies=['DELSUR -> pump -> both houses','ATAMI -> cistern','power + Cabal upstream -> internet'],provenance='simulated upgrades; installed utilities user-confirmed')
        if name == 'inspect_outcome': return dict(last=sim.history[-1] if sim.history else None,metrics=sim.metrics)
        if name == 'forecast_resources':
            preview=deepcopy(sim)
            # Remove unrevealed events: this forecast cannot know the injected failure tape.
            preview.scenario['events']=[]
            return [preview.step() for _ in range(min(6,sim.scenario['hours']-sim.t))]
        raise ValueError('Unknown tool')
    def __call__(self, sim):
        if self.failed:
            baseline(sim); self.audit.append(dict(tick=sim.t,mode='rules_fallback')); return
        self.audit.append(dict(tick=sim.t,mode='observation',observation=deepcopy(sim.observe())))
        messages=[{'role':'system','content':
            'You control ONLY a virtual two-house resilience simulation. Maximize refrigeration, water delivery and connectivity uptime while conserving fuel. '
            'All capacities are illustrative. Use tools to inspect, forecast, preview and request controls. Changes persist. '
            'Respond to current unexpected faults; never assume a request succeeded. Forecast excludes future surprises. '
            'Battery reserve must be 0.1–0.8. Essential circuits cannot be shed. Finish when ready to advance one hour.'},
            {'role':'user','content':json.dumps(sim.observe())}]
        deadline=time.monotonic()+90; calls=0
        try:
            for _ in range(8):
                if time.monotonic() >= deadline: raise TimeoutError('Tick inference budget exceeded')
                message=self.transport(messages)
                messages.append(message)
                self.audit.append(dict(tick=sim.t,mode='model',message=deepcopy(message)))
                tool_calls=message.get('tool_calls',[])
                if not tool_calls: return
                for call in tool_calls:
                    calls += 1
                    if calls > 16: raise ValueError('Tool call budget exceeded')
                    try:
                        args=json.loads(call['function']['arguments'])
                        result=self.tool(sim,call['function']['name'],args)
                    except (ValueError,KeyError,TypeError) as exc: result={'error':str(exc)}
                    # Snapshot results: no mutable aliases to future state.
                    serialized=json.dumps(result,allow_nan=False)
                    self.audit.append(dict(tick=sim.t,tool=deepcopy(call),result=json.loads(serialized)))
                    messages.append({'role':'tool','tool_call_id':call['id'],'content':serialized})
            raise ValueError('Model turn budget exceeded')
        except Exception:
            # Never persist provider exceptions that could contain request headers/secrets.
            self.failed=True
            self.audit.append(dict(tick=sim.t,mode='rules_fallback',error='Inference failed or budget exhausted'))
            baseline(sim)
