"""Actual Meta function-call loop. No generated plan is executed as prose."""
import json, urllib.request, time
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
        self.requests = 0
        self.max_requests = 16  # whole run, including every scenario tick
        self.replay = []
        self.message_count = 0
    def start_tick(self):
        self.replay = []
        self.message_count = 0
    def __call__(self, messages):
        if self.requests >= self.max_requests: raise RuntimeError('Run request limit reached')
        for message in messages[self.message_count:]:
            if message['role'] == 'tool':
                self.replay.append({'type':'function_call_output','call_id':message['tool_call_id'],'output':message['content']})
            elif message['role'] == 'assistant':
                continue  # the Responses output was already added, including reasoning
            else:
                self.replay.append({'role':message['role'],'content':[{'type':'input_text','text':message['content']}]})
        self.message_count = len(messages)
        payload={'model':self.model,'input':self.replay,'tools':[{'type':'function',**t['function']} for t in TOOLS],
                 'tool_choice':'auto','store':False,'include':['reasoning.encrypted_content'],
                 'max_output_tokens':512,'parallel_tool_calls':False}
        req = urllib.request.Request('https://api.meta.ai/v1/responses',
            data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
        self.requests += 1
        with urllib.request.urlopen(req,timeout=20,context=tls_context()) as response:
            result=json.load(response)
        if result.get('status') != 'completed' or not isinstance(result.get('output'),list):
            raise ValueError('Incomplete Meta response')
        self.replay.extend(result['output'])  # encrypted reasoning stays in memory, never in audit
        calls=[{'id':item['call_id'],'type':'function','function':{'name':item['name'],'arguments':item['arguments']}}
               for item in result['output'] if item.get('type')=='function_call']
        return {'role':'assistant','content':None,'tool_calls':calls,
                '_audit':{'response_id':result.get('id'),'usage':result.get('usage'),
                          'output_types':[item.get('type') for item in result['output']]}}

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
        if hasattr(self.transport,'start_tick'): self.transport.start_tick()
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
                self.audit.append(dict(tick=sim.t,mode='model',metadata=deepcopy(message.get('_audit',{})),
                                       tool_names=[c['function']['name'] for c in message.get('tool_calls',[])]))
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
