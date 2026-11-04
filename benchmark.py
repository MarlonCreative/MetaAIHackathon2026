"""python3 benchmark.py [--meta] -- live runs incur Meta API usage."""
import argparse, json
from dataclasses import asdict
from pathlib import Path
from simulation import Equipment, configured_scenario, run
from agent import MetaAgent

def compare_scenario(name, live=False, configuration=None):
    scenario=configured_scenario(name, configuration); base=run(scenario)
    result=dict(scenario=name, baseline=base, agent=None, delta=None,
                configuration={'equipment':asdict(Equipment(**scenario.get('equipment',{}))),
                               'initial':scenario.get('initial',{})},
                status='baseline_only')
    if live:
        agent=MetaAgent(); candidate=run(scenario,agent)
        candidate['audit']=agent.audit
        candidate['model']=getattr(agent.transport,'model','test_transport')
        tool_records=[a for a in agent.audit if 'tool' in a]
        writes=[a for a in tool_records if a['tool']['function']['name']=='request_control_action']
        changes=[a for a in writes if a['result'].get('accepted') and a['result'].get('before')!=a['result'].get('after')]
        failure=next((a for a in agent.audit if a.get('mode')=='rules_fallback' and a.get('error')),None)
        candidate['evidence']={'model_selected_tool_calls':len(tool_records),'accepted_state_changes':len(changes),
            'decision_hours':len([a for a in agent.audit if a.get('mode')=='observation']),
            'decision_budget_exhaustions':len([a for a in agent.audit if a.get('mode')=='decision_budget_exhausted']),
            'controls_held_hours':len([a for a in agent.audit if a.get('mode')=='controls_held']),
            'model_requests':getattr(agent.transport,'requests',None),
            'fallback_http_status':failure.get('http_status') if failure else None,
            'fallback_error_code':failure.get('error_code') if failure else None,
            'fallback_error_type':failure.get('error_type') if failure else None,
            'fallback_provider_status':failure.get('provider_response_status') if failure else None,
            'fallback_incomplete_reason':failure.get('provider_incomplete_reason') if failure else None,
            'minimum_tool_action_acceptance_met':len(tool_records)>=3 and bool(changes),
            'note':'Acceptance counts do not establish useful adaptation or improvement; inspect the failure trace and metrics.'}
        limited=bool(candidate['evidence']['decision_budget_exhaustions'])
        result.update(agent=candidate,status='mixed_meta_rules_fallback' if agent.failed else 'meta_decision_limits' if limited else 'meta_completed')
        result['delta']={k:candidate['metrics'][k]-v for k,v in base['metrics'].items()}
        result['same_initial_conditions']=base['input_sha256']==candidate['input_sha256']
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--meta',action='store_true')
    parser.add_argument('--scenario',choices=('sunny','downpour','storm72'))
    args=parser.parse_args()
    if args.meta and not args.scenario: parser.error('--meta requires one --scenario to bound credit use')
    Path('reports').mkdir(exist_ok=True)
    for name in ((args.scenario,) if args.scenario else ('sunny','downpour','storm72')):
        result=compare_scenario(name,args.meta)
        output=Path(f'reports/{name}-meta.json' if args.meta else f'reports/{name}.json')
        output.write_text(json.dumps(result,indent=2)+'\n')
        print(name, result['status'], json.dumps(result['baseline']['metrics']))
