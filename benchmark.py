"""python3 benchmark.py [--meta] -- live runs incur Meta API usage."""
import argparse, json
from pathlib import Path
from simulation import load_scenario, run
from agent import MetaAgent

def compare_scenario(name, live=False):
    scenario=load_scenario(name); base=run(scenario)
    result=dict(scenario=name, baseline=base, agent=None, delta=None,
                status='NOT RUN: Meta credentials/inference required; no AI improvement claimed')
    if live:
        agent=MetaAgent(); candidate=run(scenario,agent)
        candidate['audit']=agent.audit
        candidate['model']=getattr(agent.transport,'model','test_transport')
        tool_records=[a for a in agent.audit if 'tool' in a]
        writes=[a for a in tool_records if a['tool']['function']['name']=='request_control_action']
        changes=[a for a in writes if a['result'].get('accepted') and a['result'].get('before')!=a['result'].get('after')]
        candidate['evidence']={'model_selected_tool_calls':len(tool_records),'accepted_state_changes':len(changes),
            'minimum_tool_action_acceptance_met':len(tool_records)>=3 and bool(changes),
            'note':'Acceptance counts do not establish useful adaptation or improvement; inspect the failure trace and metrics.'}
        result.update(agent=candidate,status='mixed_meta_rules_fallback' if agent.failed else 'meta_completed')
        result['delta']={k:candidate['metrics'][k]-v for k,v in base['metrics'].items()}
        result['same_initial_conditions']=base['input_sha256']==candidate['input_sha256']
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--meta',action='store_true'); args=parser.parse_args()
    Path('reports').mkdir(exist_ok=True)
    for name in ('sunny','downpour','storm72'):
        result=compare_scenario(name,args.meta)
        Path(f'reports/{name}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(name, result['status'], json.dumps(result['baseline']['metrics']))
