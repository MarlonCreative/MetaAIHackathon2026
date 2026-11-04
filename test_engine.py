import unittest
from engine import SCENARIOS,evaluate
class EngineTests(unittest.TestCase):
 def test_all_scenarios(self):
  for s in SCENARIOS.values():self.assertIn(evaluate(s)['status'],['STABLE','WATCH','CRITICAL'])
 def test_outage_sheds_ac(self):
  d=evaluate(SCENARIOS['outage']);self.assertEqual(d['status'],'WATCH');self.assertEqual(sum(x['name'].startswith('AC') for x in d['deferred']),4)
 def test_critical(self):
  d=evaluate(SCENARIOS['compound']);self.assertEqual(d['status'],'CRITICAL');self.assertIn('Water pump',[x['name'] for x in d['deferred']])
 def test_no_real_control(self):self.assertIn('Never directly switch real equipment',evaluate(SCENARIOS['normal'])['policy_rules'])
if __name__=='__main__':unittest.main()
