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
 ('evaluate_action','Compare one virtual action with holding controls for up to twelve hours; no future injected events or real state changes.',CONTROLS),
 ('request_control_action','Change permitted simulated equipment settings through safety gate.',CONTROLS),
 ('inspect_outcome','Inspect last completed tick and accumulated service metrics.',{'type':'object','properties':{},'additionalProperties':False})]:
    TOOLS.append({'type':'function','function':{'name':name,'description':description,'parameters':parameters}})

class MetaTransport:
    def __init__(self):
        self.key = meta_key()
        if not self.key: raise ValueError('Meta credentials unavailable')
        self.model = settings().get('META_MODEL','muse-spark-1.3')
        self.requests = 0
        self.max_requests = 80  # whole run; decisions occur on events and after changed controls
        self.replay = []
        self.message_count = 0
        self.last_response_status = None
        self.last_incomplete_reason = None
    def start_tick(self):
        self.replay = []
        self.message_count = 0
    def __call__(self, messages):
        self.last_response_status = None
        self.last_incomplete_reason = None
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
                 'reasoning':{'effort':'low'},'max_output_tokens':2048,'parallel_tool_calls':False}
        req = urllib.request.Request('https://api.meta.ai/v1/responses',
            data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
        self.requests += 1
        with urllib.request.urlopen(req,timeout=30,context=tls_context()) as response:
            result=json.load(response)
        self.last_response_status=result.get('status')
        details=result.get('incomplete_details')
        if isinstance(details,dict) and details.get('reason') in ('max_output_tokens','content_filter'):
            self.last_incomplete_reason=details['reason']
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
        self.audit = []; self.failed = False; self.followup_tick = None
    def tool(self, sim, name, args):
        if name in ('request_control_action','evaluate_action'):
            if name == 'request_control_action': return sim.action(args)
            hold=deepcopy(sim); preview=deepcopy(sim)
            # Both branches share the current observation but cannot see future injected events.
            hold.scenario['events']=[]; preview.scenario['events']=[]
            result=preview.action(args)
            hours=min(12,sim.scenario['hours']-sim.t)
            def summary(rows):
                return dict(critical_uptime_h=sum(row['critical'] for row in rows),
                            water_uptime_h=sum(row['delivered_water_l']>=row['water_demand_lph'] for row in rows),
                            network_uptime_h=sum(row['network'] for row in rows),
                            delivered_water_l=sum(row['delivered_water_l'] for row in rows),
                            unmet_water_l=sum(row['water_demand_lph']-row['delivered_water_l'] for row in rows),
                            fuel_l=sum(row['fuel_used_l'] for row in rows),
                            ending_battery_kwh=rows[-1]['battery_kwh'],ending_cistern_l=rows[-1]['cistern_l'])
            unchanged=summary([hold.step() for _ in range(hours)])
            candidate=summary([preview.step() for _ in range(hours)])
            return dict(policy={'accepted':result['accepted'],'reason':result['reason'],
                                'state_changed':result['before']!=result['after']},
                        horizon_hours=hours,future_events_excluded=True,
                        hold=unchanged,candidate=candidate,
                        delta_vs_hold={key:candidate[key]-value for key,value in unchanged.items()})
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
        observation = sim.observe()
        followup = sim.t == self.followup_tick
        alerts=[]
        if sim.history:
            last=sim.history[-1]; previous=sim.history[-2] if len(sim.history)>1 else None
            threshold=.3*sim.eq.battery_kwh
            if (sim.eq.battery_kwh>0 and not observation['grid'] and not observation['generator']
                    and not observation['generator_fault'] and observation['fuel_l']>0
                    and last['battery_kwh']<=threshold
                    and (previous is None or previous['battery_kwh']>threshold)):
                alerts.append('Battery crossed 30% with backup generator available')
            if not last['critical'] and (previous is None or previous['critical']):
                alerts.append('Critical power was lost in the previous hour')
            if (last['water_demand_lph']>0 and last['delivered_water_l']==0
                    and (previous is None or previous['delivered_water_l']>0)):
                alerts.append('Water delivery stopped in the previous hour')
        if sim.t > 0 and not observation['events'] and not followup and not alerts:
            # Virtual settings persist. Save model calls for disturbances the agent can react to.
            self.audit.append(dict(tick=sim.t,mode='controls_held'))
            return
        self.followup_tick = None
        if hasattr(self.transport,'start_tick'): self.transport.start_tick()
        trigger = 'initial' if sim.t == 0 else 'event' if observation['events'] else 'action_followup' if followup else 'resource_alert'
        self.audit.append(dict(tick=sim.t,mode='observation',trigger=trigger,observation=deepcopy(observation)))
        prior_actions=[]
        if trigger=='action_followup':
            for entry in self.audit:
                if entry.get('tick')==sim.t-1 and entry.get('tool',{}).get('function',{}).get('name')=='request_control_action':
                    result=entry['result']
                    prior_actions.append(dict(action=result.get('action'),accepted=result.get('accepted'),
                                              changed=result.get('before')!=result.get('after')))
        messages=[{'role':'system','content':
            'You control ONLY a virtual two-house resilience simulation. Prioritize critical power, water delivery, and connectivity uptime; conserve fuel after protecting essential services. '
            'All capacities are illustrative. Use tools to inspect, forecast, preview and request controls. Changes persist. '
            'You are called at the start, after a changed control to inspect its next-hour outcome, when a resource alert occurs, and when a new disturbance arrives. Settings persist between calls. '
            'Use only the tools needed for this decision; at most two action previews. After one approved control request, finish unless another immediate action is essential. '
            'The user observation already includes current sensors, equipment, and last outcome; avoid rereading them unless necessary. '
            'On a follow-up, check the previous action and outcome before exploring new options. If no change is needed, finish without a tool call. '
            'Respond to current unexpected faults; never assume a request succeeded. Forecast excludes future surprises. '
            'Battery reserve must be 0.1–0.8. Essential circuits cannot be shed. Finish when ready to advance one hour.'},
            {'role':'user','content':json.dumps(dict(observation,decision_trigger=trigger,resource_alerts=alerts,prior_actions=prior_actions))}]
        deadline=time.monotonic()+120; calls=0; previews=0
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
                        if call['function']['name']=='evaluate_action':
                            previews+=1
                            result={'error':'Preview limit reached; request a control or finish this decision.'} if previews>2 else self.tool(sim,'evaluate_action',args)
                        else:
                            result=self.tool(sim,call['function']['name'],args)
                    except (ValueError,KeyError,TypeError) as exc: result={'error':str(exc)}
                    # Snapshot results: no mutable aliases to future state.
                    serialized=json.dumps(result,allow_nan=False)
                    self.audit.append(dict(tick=sim.t,tool=deepcopy(call),result=json.loads(serialized)))
                    if not followup and call['function']['name']=='request_control_action' and result.get('accepted') and result.get('before')!=result.get('after'):
                        self.followup_tick=sim.t+1
                    messages.append({'role':'tool','tool_call_id':call['id'],'content':serialized})
            # A decision can end without a final message; keep accepted controls and revisit later events.
            self.audit.append(dict(tick=sim.t,mode='decision_budget_exhausted'))
            return
        except Exception as exc:
            # Never persist provider exceptions that could contain request headers/secrets.
            self.failed=True
            known_errors={'Run request limit reached':'request_limit','Incomplete Meta response':'incomplete_response',
                          'Tool call budget exceeded':'tool_call_limit','Tick inference budget exceeded':'decision_timeout'}
            self.audit.append(dict(tick=sim.t,mode='rules_fallback',error='Inference failed or budget exhausted',
                                   error_code=known_errors.get(str(exc),'other'),
                                   error_type=type(exc).__name__,http_status=getattr(exc,'code',None)
                                   if type(getattr(exc,'code',None)) is int else None,
                                   provider_response_status=getattr(self.transport,'last_response_status',None),
                                   provider_incomplete_reason=getattr(self.transport,'last_incomplete_reason',None)))
            baseline(sim)
