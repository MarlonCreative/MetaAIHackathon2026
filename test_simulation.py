import unittest, json, io
from copy import deepcopy
from unittest.mock import patch
from simulation import Simulation, load_scenario, configured_scenario, baseline, run
from agent import MetaAgent, MetaTransport
from benchmark import compare_scenario

class SimulationTests(unittest.TestCase):
    def test_scenarios_reproducible_and_safe(self):
        for name in ('sunny','downpour','storm72'):
            a=run(load_scenario(name)); b=run(load_scenario(name))
            self.assertEqual(a,b);self.assertEqual(a['metrics']['safety_violations'],0)
            self.assertEqual(len(a['history']),load_scenario(name)['hours'])
            for h in a['history']:
                self.assertGreaterEqual(h['fuel_l'],0);self.assertGreaterEqual(h['battery_kwh'],0)
                self.assertLessEqual(h['battery_kwh'],10);self.assertGreaterEqual(h['cistern_l'],0)
                supply=h['solar_kw']+h['generator_kw']+h['grid_import_kwh']+h['battery_discharge_kwh']
                sinks=h['used_kw']+h['battery_charge_kwh']+h['curtailed_kwh']
                self.assertAlmostEqual(supply,sinks)
                self.assertAlmostEqual(h['battery_kwh'],h['battery_before_kwh']+h['battery_charge_kwh']*.92-h['battery_discharge_kwh']/.92)
    def test_full_cistern_without_power_has_no_delivery(self):
        spec=load_scenario('sunny');spec['initial'].update(grid=False,battery_kwh=1,weather_factor=0)
        s=Simulation(spec);out=s.step()
        self.assertGreater(out['cistern_l'],0);self.assertEqual(out['delivered_water_l'],0)
    def test_night_and_clouds(self):
        s=Simulation(load_scenario('sunny'));s.t=16
        self.assertEqual(s.observe()['solar_kw'],0)
        s.t=4;s.prepared=False;sun=s.observe()['solar_kw'];s.state['weather_factor']=.1
        self.assertAlmostEqual(s.observe()['solar_kw'],sun*.1)
    def test_reject_controls(self):
        s=Simulation(load_scenario('sunny'));s.state['generator_fault']=True
        for action in ({'control':'generator','value':True},{'control':'reserve','value':0},{'control':'reserve','value':float('nan')},{'control':'pump','value':'yes'},{'control':'mains','value':True}):
            before=deepcopy(s.state);self.assertFalse(s.action(action)['accepted']);self.assertEqual(s.state,before)
    def test_inverter_and_surge_limit(self):
        spec=load_scenario('sunny');spec['initial'].update(grid=False);spec['equipment']={'surge_kw':1}
        s=Simulation(spec);self.assertFalse(s.step()['pump_on'])
    def test_resource_conservation(self):
        for h in run(load_scenario('storm72'))['history']:
            self.assertLessEqual(h['used_kw'],h['solar_kw']+h['generator_kw']+3+1e-9)
            self.assertLessEqual(h['generator_kw'],3)
            self.assertGreaterEqual(h['battery_kwh'],1-1e-9)
        r=run(load_scenario('storm72'));self.assertGreater(r['metrics']['fuel_l'],0)
        self.assertTrue(all(not h['generator'] for h in r['history'][24:]))
    def test_preview_does_not_mutate_or_leak_events(self):
        s=Simulation(load_scenario('storm72'));a=MetaAgent(lambda m:{'role':'assistant','content':'done'})
        s.t=23;s.observe();before=deepcopy(s.__dict__)
        preview=a.tool(s,'evaluate_action',{'control':'optional','value':False})
        self.assertEqual(s.__dict__,before)
        self.assertTrue(preview['future_events_excluded'])
        self.assertEqual(preview['horizon_hours'],12)
        forecast=a.tool(s,'forecast_resources',{})
        self.assertFalse(any(h['generator_fault'] for h in forecast))
    def test_preview_compares_services_and_fuel(self):
        s=Simulation(load_scenario('storm72'));a=MetaAgent(lambda _:None)
        result=a.tool(s,'evaluate_action',{'control':'generator','value':True})
        self.assertTrue(result['policy']['accepted'])
        self.assertGreater(result['delta_vs_hold']['fuel_l'],0)
        self.assertGreater(result['delta_vs_hold']['ending_battery_kwh'],0)
        self.assertEqual(result['horizon_hours'],12)
    def test_missing_agent_is_not_an_ai_score(self):
        result=compare_scenario('sunny');self.assertIsNone(result['agent']);self.assertIsNone(result['delta'])
        self.assertEqual(result['configuration']['equipment']['battery_kwh'],10)
    def test_home_stack_configuration_changes_measured_run(self):
        original=compare_scenario('storm72')
        config={'equipment':{'solar_kwp':0,'battery_kwh':0,'inverter_kw':0,'surge_kw':0,'generator_kw':0},
                'initial':{'battery_kwh':0,'fuel_l':0}}
        without_backup=compare_scenario('storm72',configuration=config)
        self.assertNotEqual(original['baseline']['input_sha256'],without_backup['baseline']['input_sha256'])
        self.assertLess(without_backup['baseline']['metrics']['water_uptime_h'],original['baseline']['metrics']['water_uptime_h'])
        self.assertEqual(without_backup['baseline']['metrics']['fuel_l'],0)
        self.assertEqual(without_backup['configuration']['equipment']['generator_kw'],0)
    def test_home_stack_configuration_rejects_impossible_inputs(self):
        bad=[{'equipment':{'battery_kwh':2},'initial':{'battery_kwh':4}},
             {'equipment':{'cistern_l':1000}}, {'equipment':{'solar_kwp':float('nan')}},
             {'equipment':{'unknown':3}}, {'initial':{'grid':True}}]
        for config in bad:
            with self.subTest(config=config),self.assertRaises(ValueError):configured_scenario('storm72',config)

class FakeTransport:
    """Contract test double, explicitly NOT model performance evidence."""
    def __init__(self): self.turn=0;self.messages=[]
    def __call__(self,messages):
        self.messages.append(deepcopy(messages)); self.turn+=1
        if self.turn%2==0:return {'role':'assistant','content':'Advance tick.'}
        obs=json.loads(messages[-1]['content'])
        # Test feedback-driven switch after injected failure, not a demo controller.
        action={'control':'optional' if obs['generator_fault'] else 'generator','value':False if obs['generator_fault'] else True}
        calls=[]
        for i,(name,args) in enumerate([('read_sensors',{}),('inspect_outcome',{}),('request_control_action',action)]):
            calls.append({'id':f'{self.turn}-{i}','type':'function','function':{'name':name,'arguments':json.dumps(args)}})
        return {'role':'assistant','content':None,'tool_calls':calls}

class AgentTests(unittest.TestCase):
    def test_responses_contract_and_bounded_replay(self):
        captured=[]
        responses=[
            {'status':'completed','id':'resp_1','usage':{'total_tokens':10},'output':[
                {'type':'reasoning','summary':[],'encrypted_content':'opaque-test-data'},
                {'type':'function_call','call_id':'call_1','name':'read_sensors','arguments':'{}'}]},
            {'status':'completed','id':'resp_2','usage':{'total_tokens':12},'output':[
                {'type':'message','role':'assistant','content':[{'type':'output_text','text':'Done'}]}]}]
        def fake_open(request, **_):
            captured.append(json.loads(request.data));return io.BytesIO(json.dumps(responses.pop(0)).encode())
        with patch('agent.meta_key',return_value='fake-test-token'),patch('agent.settings',return_value={}),patch('agent.urllib.request.urlopen',side_effect=fake_open):
            transport=MetaTransport();transport.start_tick()
            messages=[{'role':'system','content':'Simulation only'},{'role':'user','content':'{}'}]
            first=transport(messages)
            messages.extend([first,{'role':'tool','tool_call_id':'call_1','content':'{}'}])
            transport(messages)
        self.assertEqual(len(captured),2)
        self.assertEqual(captured[0]['store'],False)
        self.assertEqual(captured[0]['reasoning'],{'effort':'low'})
        self.assertEqual(captured[0]['max_output_tokens'],2048)
        self.assertEqual([item['type'] for item in captured[1]['input'][-3:]],['reasoning','function_call','function_call_output'])
        self.assertNotIn('opaque-test-data',json.dumps(first))
    def test_incomplete_provider_response_is_classified(self):
        response={'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},'output':[]}
        with patch('agent.meta_key',return_value='fake-test-token'),patch('agent.settings',return_value={}),patch('agent.urllib.request.urlopen',return_value=io.BytesIO(json.dumps(response).encode())):
            transport=MetaTransport()
            with self.assertRaisesRegex(ValueError,'Incomplete Meta response'):
                transport([{'role':'user','content':'{}'}])
        self.assertEqual(transport.last_response_status,'incomplete')
        self.assertEqual(transport.last_incomplete_reason,'max_output_tokens')
    def test_tools_feedback_and_unexpected_failure(self):
        fake=FakeTransport();agent=MetaAgent(fake);s=Simulation(load_scenario('storm72'))
        agent(s);self.assertTrue(s.state['generator']);s.step()
        s.t=24;s.prepared=False;agent(s)
        self.assertTrue(s.state['generator_fault']);self.assertFalse(s.state['optional'])
        self.assertFalse(agent.failed)
        self.assertEqual(len([a for a in agent.audit if 'tool' in a]),6)
        returned=[m for m in fake.messages[1] if m['role']=='tool'];self.assertEqual(len(returned),3)
        self.assertTrue(json.loads(returned[-1]['content'])['accepted'])
    def test_event_triggered_agent_reaches_late_disturbances(self):
        agent=MetaAgent(FakeTransport())
        result=run(load_scenario('storm72'),agent)
        decision_ticks=[a['tick'] for a in agent.audit if a.get('mode')=='observation']
        held_ticks=[a['tick'] for a in agent.audit if a.get('mode')=='controls_held']
        self.assertTrue({0,1,24,25,32,48}.issubset(decision_ticks))
        self.assertEqual(len(held_ticks),72-len(decision_ticks))
        triggers={a['tick']:a['trigger'] for a in agent.audit if a.get('mode')=='observation'}
        self.assertEqual(triggers[1],'action_followup')
        self.assertEqual(triggers[24],'event')
        self.assertFalse(agent.failed)
        self.assertEqual(len(result['history']),72)
        self.assertTrue(any(a.get('tick')==24 and a.get('tool',{}).get('function',{}).get('name')=='request_control_action'
                            for a in agent.audit))
    def test_resource_alert_triggers_without_new_event(self):
        agent=MetaAgent(lambda _:{'role':'assistant','content':'Hold controls.'})
        run(load_scenario('storm72'),agent)
        alerts=[a['tick'] for a in agent.audit if a.get('trigger')=='resource_alert']
        self.assertTrue(any(1<tick<24 for tick in alerts))
    def test_failure_falls_back_explicitly(self):
        def fail(_):raise RuntimeError('private provider error')
        agent=MetaAgent(fail);s=Simulation(load_scenario('storm72'));agent(s)
        self.assertTrue(agent.failed);self.assertEqual(agent.audit[-1]['mode'],'rules_fallback')
        self.assertEqual(agent.audit[-1]['error_type'],'RuntimeError')
        self.assertNotIn('private provider error',json.dumps(agent.audit))
    def test_decision_limit_does_not_prevent_later_event(self):
        calls=0
        def preview(_):
            nonlocal calls
            calls+=1
            return {'role':'assistant','content':None,'tool_calls':[{'id':str(calls),'type':'function',
                'function':{'name':'evaluate_action','arguments':'{"control":"optional","value":false}'}}]}
        agent=MetaAgent(preview);s=Simulation(load_scenario('storm72'))
        agent(s)
        self.assertFalse(agent.failed)
        self.assertEqual(calls,8)
        self.assertEqual(agent.audit[-1]['mode'],'decision_budget_exhausted')
        s.t=24;s.prepared=False;agent(s)
        self.assertEqual(calls,16)
        self.assertEqual([a['tick'] for a in agent.audit if a.get('mode')=='observation'],[0,24])
    def test_unknown_tool(self):
        s=Simulation(load_scenario('sunny'));a=MetaAgent(lambda _:None)
        with self.assertRaises(ValueError):a.tool(s,'shell',{})

if __name__=='__main__':unittest.main()
