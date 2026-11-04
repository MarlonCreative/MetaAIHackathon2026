import unittest, json
from copy import deepcopy
from simulation import Simulation, load_scenario, baseline, run
from agent import MetaAgent
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
        a.tool(s,'evaluate_action',{'control':'optional','value':False})
        self.assertEqual(s.__dict__,before)
        forecast=a.tool(s,'forecast_resources',{})
        self.assertFalse(any(h['generator_fault'] for h in forecast))
    def test_missing_agent_is_not_an_ai_score(self):
        result=compare_scenario('sunny');self.assertIsNone(result['agent']);self.assertIsNone(result['delta'])

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
    def test_tools_feedback_and_unexpected_failure(self):
        fake=FakeTransport();agent=MetaAgent(fake);s=Simulation(load_scenario('storm72'))
        agent(s);self.assertTrue(s.state['generator']);s.step()
        s.t=24;s.prepared=False;agent(s)
        self.assertTrue(s.state['generator_fault']);self.assertFalse(s.state['optional'])
        self.assertFalse(agent.failed)
        self.assertEqual(len([a for a in agent.audit if 'tool' in a]),6)
        returned=[m for m in fake.messages[1] if m['role']=='tool'];self.assertEqual(len(returned),3)
        self.assertTrue(json.loads(returned[-1]['content'])['accepted'])
    def test_failure_falls_back_explicitly(self):
        def fail(_):raise RuntimeError('private provider error')
        agent=MetaAgent(fail);s=Simulation(load_scenario('storm72'));agent(s)
        self.assertTrue(agent.failed);self.assertEqual(agent.audit[-1]['mode'],'rules_fallback')
        self.assertNotIn('private provider error',json.dumps(agent.audit))
    def test_unknown_tool(self):
        s=Simulation(load_scenario('sunny'));a=MetaAgent(lambda _:None)
        with self.assertRaises(ValueError):a.tool(s,'shell',{})

if __name__=='__main__':unittest.main()
