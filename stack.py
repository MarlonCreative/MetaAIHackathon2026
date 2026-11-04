"""CasaOS Home Stack scenario comparisons. Illustrative planning only; no equipment control."""
from math import ceil

DEFAULT_STACK = {
    'property': 'Two-house property · La Libertad, El Salvador',
    'installed': [
        {'id':'grid','name':'DELSUR electrical service','category':'energy','status':'existing','detail':'Utility service; outage frequency not yet measured'},
        {'id':'cistern','name':'Cistern supplied by ATAMI Residential','category':'water','status':'existing','detail':'Private residential water provider; cistern capacity and pump rating unconfirmed; electric pump required for household water delivery'},
        {'id':'internet','name':'Cabal internet service','category':'connectivity','status':'existing','detail':'Access technology, modem/router power draw, uptime unconfirmed'}
    ],
    'planned': [
        {'id':'solar','name':'Solar array + battery','category':'energy','status':'proposed','detail':'Hypothetical solar and storage; not currently installed'},
        {'id':'generator','name':'Backup generator','category':'energy','status':'proposed','detail':'Fuel-dependent backup; not currently installed; transfer switch and ventilation require professional design'},
        {'id':'starlink','name':'Starlink internet alternative','category':'connectivity','status':'proposed','detail':'Possible second connection; needs power, local service availability and sky visibility'},
        {'id':'well','name':'Well + pump','category':'water','status':'proposed','detail':'Requires groundwater feasibility, yield, quality tests, permitting, and pump design'}
    ]
}
DEFAULT_ASSUMPTIONS = {
  'outage_hours':24,
  'essential_kwh_day':5.0,
  'solar_kwp':5.0,
  'peak_sun_hours':4.5,
  'solar_performance':0.75,
  'battery_kwh':10.0,
  'battery_usable_fraction':0.8,
  'water_liters_day':400,
  'cistern_liters':5000,
  'cistern_fill_fraction':0.6,
  'well_liters_hour':300,
  'well_pump_kw':0.75,
  'well_pump_hours_day':2,
  'well_water_usable':False,
  'generator_kw':3.0,
  'generator_fuel_liters':20.0,
  'generator_liters_per_hour':1.2,
  'generator_hours_day':8.0
}
BOUNDS={
 'outage_hours':(1,168),'essential_kwh_day':(0.5,60),'solar_kwp':(0,25),
 'peak_sun_hours':(0,8),'solar_performance':(0.2,0.95),'battery_kwh':(0,100),
 'battery_usable_fraction':(0.1,0.95),'water_liters_day':(10,5000),
 'cistern_liters':(100,100000),'cistern_fill_fraction':(0,1),
 'well_liters_hour':(0,10000),'well_pump_kw':(0,15),
 'well_pump_hours_day':(0,24),
 'generator_kw':(0,30),'generator_fuel_liters':(0,500),
 'generator_liters_per_hour':(0.1,12),'generator_hours_day':(0,24)
}

def validate_assumptions(data):
 if not isinstance(data,dict): raise ValueError('Assumptions must be an object')
 out={**DEFAULT_ASSUMPTIONS}
 for k,v in data.items():
  if k not in out: raise ValueError('Unknown field: '+k)
  if k=='well_water_usable':
   if type(v) is not bool:raise ValueError('well_water_usable must be boolean')
  else:
   low,high=BOUNDS[k]
   if type(v) not in (int,float) or not low<=v<=high:raise ValueError(f'{k} must be between {low} and {high}')
  out[k]=v
 return out

def compare(data=None):
 a=validate_assumptions(data or {})
 days=a['outage_hours']/24
 energy_demand=a['essential_kwh_day']*days
 cistern_available=a['cistern_liters']*a['cistern_fill_fraction']
 water_need=a['water_liters_day']*days
 # Standalone battery starts full; solar generation is a daily illustrative average.
 solar_daily=a['solar_kwp']*a['peak_sun_hours']*a['solar_performance']
 battery_usable=a['battery_kwh']*a['battery_usable_fraction']
 energy_supply=battery_usable+solar_daily*days
 # Well has *potential* yield, but unavailable unless water usability explicitly confirmed.
 well_yield=a['well_liters_hour']*a['well_pump_hours_day']*days
 well_pump_energy=a['well_pump_kw']*a['well_pump_hours_day']*days
 def result(name, energy_kwh, water_l, notes):
  return {'name':name,'electricity_demand_kwh':round(energy_demand,1),
   'electricity_available_kwh':round(energy_kwh,1),
   'energy_coverage_pct':round(100*min(1,energy_kwh/energy_demand),1),
   'water_demand_liters':round(water_need),
   'water_available_liters':round(water_l),
   'water_coverage_pct':round(100*min(1,water_l/water_need),1),
   'notes':notes}
 baseline=result('Current home stack',0,0,[
  'During a DELSUR outage, no confirmed backup electricity has been specified.',
  'The cistern may contain stored water, but routine delivery needs the electric pump; no backup power is currently installed. Water coverage reflects unavailable pumped service, not an empty cistern.'])
 baseline['water_access_status']='Unavailable: pump depends on DELSUR'
 baseline['water_stored_liters']=round(cistern_available)
 solar=result('Add solar + battery',energy_supply,cistern_available,[
  'Water access is only potential: confirm that the backup circuit, inverter surge rating and pump power are compatible.',
  'Simple gross energy balance over the outage; not an hour-by-hour simulation.',
  'Weather, nighttime demand, inverter power, charging limits, battery reserve, and startup surges are not modeled.'])
 well_energy_need=energy_demand+well_pump_energy
 well_energy_fraction=min(1,energy_supply/well_energy_need) if well_energy_need else 1
 supported_well=well_yield*well_energy_fraction if a['well_water_usable'] else 0
 combined=result('Add solar + battery + well',energy_supply, cistern_available+supported_well,[
  'Well contribution is excluded unless usable water has been explicitly confirmed; both cistern and well pumping depend on verified backup electrical service.',
  'Well yield assumes sufficient aquifer recharge, water storage, and pumping time.',
  'Well pump consumes extra energy; combined energy coverage includes its load.'])
 combined['electricity_demand_kwh']=round(well_energy_need,1)
 combined['energy_coverage_pct']=round(100*min(1,energy_supply/well_energy_need),1)
 generator_runtime=min(a['generator_hours_day']*days,a['generator_fuel_liters']/a['generator_liters_per_hour']) if a['generator_kw'] else 0
 generator_kwh=a['generator_kw']*generator_runtime
 generator_only=result('Add backup generator',generator_kwh,cistern_available,[
  'Water access is only potential: generator must support the pump starting surge and distribution circuit.',
  'Uses hypothetical fuel stock, daily running hours and fuel burn rate; generator output also needs to meet peak loads.',
  'A safe generator installation requires outdoor ventilation, proper transfer equipment, and qualified electrical installation.'])
 solar_gen=result('Solar + battery + generator',energy_supply+generator_kwh,cistern_available,[
  'Water access is only potential until pump and backup circuit compatibility are verified.',
  'Combines gross modeled solar, usable battery and generator energy; dispatch logic and fuel resupply are not modeled.',
  'Generator operating costs, fuel storage, noise and safe placement require assessment.'])
 for scenario in [solar,combined,generator_only,solar_gen]:
  scenario['water_access_status']='Conditional: backup pump circuit not verified'
  scenario['water_stored_liters']=round(cistern_available)
 return {'stack':DEFAULT_STACK,'assumptions':a,'comparisons':[baseline,solar,combined,generator_only,solar_gen],
 'technical':{'solar_daily_kwh':round(solar_daily,1),'battery_usable_kwh':round(battery_usable,1),
  'well_potential_liters_during_outage':round(well_yield),'well_pump_kwh_during_outage':round(well_pump_energy,1),
  'generator_runtime_hours':round(generator_runtime,1),'generator_energy_kwh':round(generator_kwh,1)},
 'limitations':['Outputs are hypothetical, not measured readings or a system design.',
 'Solar, generator, well and Starlink are proposed, not installed.',
 'Well feasibility and potable use require local professional assessment and testing.',
 'Power is modeled as cumulative kWh, not continuous service; instantaneous loads can exceed inverter capacity.',
 'Confirmed: household delivery uses an electric pump. DELSUR outages interrupt ordinary pumped supply without suitable backup power; pump size/startup draw and plumbing configuration are not yet known.',
 'All consumption, solar yield, storage capacity, and well flow inputs are editable assumptions.']}
