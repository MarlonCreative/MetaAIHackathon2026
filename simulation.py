"""Deterministic hourly planning sandbox. All capacities are illustrative, not site measurements."""
from dataclasses import dataclass, asdict
from copy import deepcopy
import math, json, hashlib
from pathlib import Path

@dataclass
class Equipment:
    battery_kwh: float = 10
    battery_kw: float = 3
    inverter_kw: float = 4
    surge_kw: float = 5
    solar_kwp: float = 3.8
    generator_kw: float = 3
    cistern_l: float = 3000
    pump_kw: float = .65
    pump_surge_kw: float = 2
    pump_lph: float = 600
    efficiency: float = .92

class Simulation:
    def __init__(self, scenario):
        self.scenario = deepcopy(scenario)
        self.eq = Equipment(**scenario.get('equipment', {}))
        self.t = 0
        self.state = dict(battery_kwh=8., fuel_l=15., cistern_l=2700., generator=False,
                          generator_fault=False, grid=True, upstream=True, weather_factor=1.,
                          water_inflow_lph=60., water_demand_lph=40., optional=True, pump=True, reserve=.1)
        self.state.update(scenario.get('initial', {}))
        self.trace = []; self.history = []; self.events = []
        self.metrics = dict(critical_uptime_h=0., water_uptime_h=0., network_uptime_h=0.,
                            full_service_uptime_h=0., delivered_water_l=0., unmet_water_l=0.,
                            unmet_energy_kwh=0., fuel_l=0., rejected_actions=0, safety_violations=0)
        self.prepared = False
    def prepare(self):
        if self.prepared: return
        self.events = []
        for event in self.scenario['events']:
            if event['tick'] == self.t:
                self.state.update(event['set']); self.events.append(event['label'])
        if self.state['generator_fault'] or self.state['fuel_l'] <= 0:
            self.state['generator'] = False
        self.prepared = True
    def observe(self):
        self.prepare()
        hour = (self.scenario['start_hour'] + self.t) % 24
        solar = max(0., math.sin(math.pi*(hour-6)/12)) if 6 <= hour <= 18 else 0.
        return dict(tick=self.t, hour=hour, events=self.events[:], **self.state,
                    solar_kw=solar*self.eq.solar_kwp*self.state['weather_factor'],
                    equipment=asdict(self.eq), last_outcome=self.history[-1] if self.history else None)
    def action(self, action):
        before = deepcopy(self.state)
        error = None
        if not isinstance(action, dict) or set(action) != {'control', 'value'}:
            error = 'Expected exactly control and value'
        else:
            k, v = action['control'], action['value']
            if k not in ('optional', 'pump', 'generator', 'reserve'): error = 'Unknown control'
            elif k == 'reserve':
                if type(v) not in (int, float) or not math.isfinite(v) or not .1 <= v <= .8: error = 'Reserve must be 0.1–0.8'
            elif type(v) is not bool: error = 'Control requires boolean'
            if not error and k == 'generator' and v and (self.state['generator_fault'] or self.state['fuel_l'] <= 0):
                error = 'Generator fault or empty fuel'
            if not error and k == 'pump' and v and self.state['cistern_l'] <= 0: error = 'Dry cistern'
            if not error: self.state[k] = v
        record = dict(tick=self.t, action=action, accepted=not error, reason=error, before=before, after=deepcopy(self.state))
        self.trace.append(record)
        if error: self.metrics['rejected_actions'] += 1
        return record
    def step(self):
        o = self.observe(); e = self.eq; s = self.state
        fuel_before = s['fuel_l']; battery_before = s['battery_kwh']
        # Generator output is bounded by fuel available for this entire one-hour tick.
        gen = 0.
        if s['generator']:
            idle = .18
            if s['fuel_l'] >= idle:
                gen = min(e.generator_kw, (s['fuel_l']-idle)/.24)
                s['fuel_l'] -= idle + .24*gen
            else: s['generator'] = False
        solar = o['solar_kw']; sources = solar + gen
        battery_available = min(e.battery_kw, max(0., s['battery_kwh']-e.battery_kwh*s['reserve'])*e.efficiency)
        remaining = 100. if s['grid'] else min(e.inverter_kw, sources+battery_available)
        used = 0.
        def serve(kw):
            nonlocal remaining, used
            granted = min(kw, remaining); remaining -= granted; used += granted
            return granted
        essential = serve(.2); router = serve(.03)
        available_water = min(e.cistern_l, s['cistern_l']+s['water_inflow_lph'])
        demand = s['water_demand_lph']
        volume = min(demand, available_water, e.pump_lph)
        pump_energy = e.pump_kw * volume/e.pump_lph
        surge_ok = s['grid'] or (e.surge_kw >= e.pump_surge_kw+.23 and sources+battery_available >= e.pump_surge_kw+.23)
        pump_on = bool(s['pump'] and volume > 0 and surge_ok and remaining+1e-9 >= pump_energy)
        delivered = volume if pump_on else 0.
        if pump_on: serve(pump_energy)
        optional_demand = 2.5  # Account for unmet comfort demand even when deliberately shed.
        if s['optional']: serve(optional_demand)
        charge = 0.; discharge = 0.
        if not s['grid']:
            discharge = max(0., used-sources)
            s['battery_kwh'] -= discharge/e.efficiency
            surplus = max(0., sources-used)
            charge = min(e.battery_kw, surplus, (e.battery_kwh-s['battery_kwh'])/e.efficiency)
            s['battery_kwh'] += charge*e.efficiency
        else:
            charge = min(e.battery_kw, (e.battery_kwh-s['battery_kwh'])/e.efficiency)
            s['battery_kwh'] += charge*e.efficiency
        s['battery_kwh'] = max(0., min(e.battery_kwh, s['battery_kwh']))
        s['fuel_l'] = max(0., s['fuel_l']); s['cistern_l'] = available_water-delivered
        critical = essential >= .2-1e-9; network = router >= .03-1e-9 and s['upstream']; water = delivered >= demand-1e-9
        m = self.metrics
        safe = (0 <= s['battery_kwh'] <= e.battery_kwh and s['fuel_l'] >= 0 and 0 <= s['cistern_l'] <= e.cistern_l and (not pump_on or surge_ok) and (s['grid'] or used <= e.inverter_kw+1e-9))
        m['safety_violations'] += int(not safe)
        if not safe: raise AssertionError('Simulation safety invariant failed')
        for key, value in [('critical_uptime_h', critical), ('network_uptime_h', network), ('water_uptime_h', water), ('full_service_uptime_h', critical and network and water)]: m[key] += float(value)
        m['delivered_water_l'] += delivered; m['unmet_water_l'] += demand-delivered
        m['unmet_energy_kwh'] += .23+pump_energy+optional_demand-used
        m['fuel_l'] += fuel_before-s['fuel_l']
        outcome = dict(tick=self.t, hour=o['hour'], events=o['events'], solar_kw=solar,
                       generator_kw=gen, used_kw=used, battery_before_kwh=battery_before,
                       battery_charge_kwh=charge, battery_discharge_kwh=discharge,
                       grid_import_kwh=max(0., used+charge-sources) if s['grid'] else 0.,
                       curtailed_kwh=max(0., sources-used-charge),
                       fuel_used_l=fuel_before-s['fuel_l'],
                       critical=critical, network=network, pump_on=pump_on, delivered_water_l=delivered,
                       **deepcopy(s))
        self.history.append(outcome); self.t += 1; self.prepared = False
        return outcome

def baseline(sim):
    o = sim.observe()
    # Competent static controller: conserve during outages; generator hysteresis.
    gen = o['generator']
    if o['grid'] or o['battery_kwh'] >= .8*sim.eq.battery_kwh or o['generator_fault'] or o['fuel_l'] <= 0: gen = False
    elif o['battery_kwh'] <= .3*sim.eq.battery_kwh: gen = True
    for k,v in [('optional', o['grid']), ('pump', o['cistern_l']>0), ('generator', gen)]:
        sim.action({'control':k, 'value':v})

def load_scenario(name):
    if name not in ('sunny', 'downpour', 'storm72'): raise ValueError('Unknown scenario')
    return json.loads((Path(__file__).parent/'scenarios'/f'{name}.json').read_text())

def run(scenario, controller=baseline):
    sim = Simulation(scenario)
    for _ in range(scenario['hours']): controller(sim); sim.step()
    return dict(metrics=sim.metrics, history=sim.history, actions=sim.trace,
                input_sha256=hashlib.sha256(json.dumps(scenario,sort_keys=True).encode()).hexdigest())
