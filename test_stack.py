import unittest
from stack import compare
class HomeStackTests(unittest.TestCase):
 def test_baseline_no_backup(self):
  r=compare(); self.assertEqual(r['comparisons'][0]['energy_coverage_pct'],0)
 def test_stored_water_not_deliverable_without_pump_power(self):
  r=compare({'cistern_fill_fraction':1})
  self.assertEqual(r['comparisons'][0]['water_available_liters'],0)
  self.assertGreater(r['comparisons'][0]['water_stored_liters'],0)
  self.assertIn('Unavailable',r['comparisons'][0]['water_access_status'])
 def test_solar_improves_coverage(self):
  r=compare(); self.assertGreater(r['comparisons'][1]['energy_coverage_pct'],r['comparisons'][0]['energy_coverage_pct'])
 def test_well_not_counted_without_quality_confirmation(self):
  r=compare(); self.assertEqual(r['comparisons'][1]['water_available_liters'],r['comparisons'][2]['water_available_liters'])
 def test_well_counts_with_confirmation(self):
  r=compare({'well_water_usable':True});self.assertGreater(r['comparisons'][2]['water_available_liters'],r['comparisons'][1]['water_available_liters'])
 def test_generator_improves_baseline(self):
  r=compare(); self.assertGreater(r["comparisons"][3]["energy_coverage_pct"],r["comparisons"][0]["energy_coverage_pct"])
 def test_generator_without_fuel(self):
  r=compare({"generator_fuel_liters":0}); self.assertEqual(r["comparisons"][3]["electricity_available_kwh"],0)
 def test_invalid_range(self):
  with self.assertRaises(ValueError):compare({'battery_kwh':999})
if __name__=='__main__':unittest.main()
