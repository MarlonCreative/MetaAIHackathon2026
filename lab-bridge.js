// Measured runs come from the Python simulator; this module only presents them.
export function mountLab({getState, setState, stopTimer, render}) {
  const panel=document.createElement('div'); panel.className='product-panel';
  panel.innerHTML=`<div class="product-hero"><span class="eyebrow">HOME STORM PLANNER · EL SALVADOR</span>
    <h2>See what a storm could mean for your home.</h2>
    <p>Explore how a power outage affects water at the tap and internet. Try backup options here before making a purchase.</p></div>
    <div class="demo-card"><span class="eyebrow">START HERE · 1 MINUTE</span>
      <h3>Watch the Meta AI agent handle a storm</h3>
      <p>Replay a recorded 72-hour run. See what the model checked, which virtual changes it requested, and what happened next.</p>
      <button id="labSaved" class="primary demo-button">▶ Explore the storm demo</button>
      <small>Meta Muse Spark 1.3 · recorded run · no API credits used</small></div>
    <div class="ai-card"><span class="eyebrow">POWERED BY META AI</span><h3>How the agent helps</h3>
      <p id="labModelName" class="model-name">Recorded demo: Meta Muse Spark 1.3</p>
      <div class="agent-steps"><div><b>1 · Check</b><span>Read the simulated home's power, water, and fuel.</span></div>
      <div><b>2 · Plan</b><span>Forecast resources and preview a possible change.</span></div>
      <div><b>3 · Safety check</b><span>CasaOS reviews any requested virtual control.</span></div>
      <div><b>4 · Learn</b><span>See the next hour's outcome and compare with fixed rules.</span></div></div>
      <p id="labMode" class="muted">The demo replays real model tool calls; the house remains a simulation.</p></div>
    <div class="plan-card"><span class="eyebrow">YOUR TURN</span><h3>Try a different plan</h3>
      <p>Choose the weather, then compare Meta AI with a simple fixed-rule plan. A new Meta run uses API credits.</p>
      <label class="field-label">Weather to test<select id="labScenario"><option value="sunny">Sunny day · 24 hours</option><option value="downpour">Tropical downpour · 24 hours</option><option value="storm72" selected>Severe storm + equipment failure · 72 hours</option></select></label>
      <label class="field-label">Who makes the decisions?<select id="labController"><option value="baseline">Fixed rules · no model credits</option><option value="meta">Meta AI agent · uses credits</option></select></label>
      <button id="labRun" class="primary plan-button">Run this plan</button>
      <details class="equipment-settings"><summary>Adjust virtual solar, battery, generator, and water</summary><p class="muted">These are example equipment sizes. DELSUR power, an ATAMI-fed cistern and pump, and Cabal internet are the existing reference services; backup equipment is virtual.</p>
    <div class="lab-grid">
      <label>Solar · kWp<input id="labSolar" type="number" min="0" max="25" step="any" required value="3.8"></label>
      <label>Battery · kWh<input id="labBattery" type="number" min="0" max="100" step="any" required value="10"></label>
      <label>Starting charge · kWh<input id="labCharge" type="number" min="0" max="100" step="any" required value="4"></label>
      <label>Inverter · kW<input id="labInverter" type="number" min="0" max="30" step="any" required value="4"></label>
      <label>Surge ceiling · kW<input id="labSurge" type="number" min="0" max="60" step="any" required value="5"></label>
      <label>Generator · kW<input id="labGenerator" type="number" min="0" max="30" step="any" required value="3"></label>
      <label>Starting fuel · L<input id="labFuel" type="number" min="0" max="500" step="any" required value="15"></label>
      <label>Cistern size · L<input id="labCistern" type="number" min="100" max="100000" step="any" required value="3000"></label>
      <label>Starting water · L<input id="labWater" type="number" min="0" max="100000" step="any" required value="2700"></label>
      <label>Pump running · kW<input id="labPump" type="number" min="0.1" max="10" step="any" required value="0.65"></label>
      <label>Pump startup · kW<input id="labPumpSurge" type="number" min="0.1" max="30" step="any" required value="2"></label>
      <label>Water demand · L/h<input id="labDemand" type="number" min="0" max="1000" step="any" required value="40"></label>
    </div></details></div>
    <p id="labStatus" class="run-status" role="status" hidden></p>
    <div id="labResults" class="results-card" hidden><span id="labResultSource" class="eyebrow">WHAT HAPPENED</span><h3>Services through the scenario</h3>
      <div id="labEssentials" class="essentials"></div>
      <p id="labTakeaway" class="homeowner-takeaway"></p>
      <p id="labEvidence" class="agent-evidence"></p>
      <p id="labTimeHeading" class="timeline-heading"></p><label class="timeline-label">Move through the hours<input id="labTime" type="range" min="0" max="0" value="0"></label>
      <button id="labPlay" class="play-button">▶ Play the story</button>
      <div class="decision-card"><b>At this moment</b><p id="labAgentSummary" class="lab-output" role="status"></p></div>
      <div id="labMoments" class="story-moments"></div>
      <details><summary>Compare with fixed rules</summary><div id="labScore" class="lab-output"></div></details>
      <details><summary>Technical decision log</summary><pre id="labTrace" class="lab-output lab-trace"></pre></details>
      <button id="labDownload" class="download-button" disabled>Download full report</button></div>`;
  document.querySelector('aside').prepend(panel);
  panel.querySelector('.demo-card').after(panel.querySelector('#labStatus'),panel.querySelector('#labResults'));
  const el=id=>document.getElementById(id), num=id=>Number(el(id).value);
  let report=null, playback=null;
  el('labScenario').addEventListener('change',()=>{el('labCharge').value=el('labScenario').value==='storm72'?'4':'8'});
  function decisionSummary(entries,row){
    if(!report.agent) return `${row.events.length?`The simulation introduced: ${row.events.join(', ')}. `:''}Fixed rules managed the virtual home this hour. ${row.delivered_water_l.toFixed(0)} L of water reached the home; essential power was ${row.critical?'on':'off'}.`;
    const lines=[];
    if(row.events.length) lines.push(`New event: ${row.events.join(', ')}.`);
    const observation=entries.find(x=>x.mode==='observation');
    if(observation) lines.push(`Meta AI is ${observation.trigger==='action_followup'?'checking the last change':observation.trigger==='event'?'responding to the new event':observation.trigger==='resource_alert'?'checking a low resource':'making its first decision'}.`);
    const calls=entries.filter(x=>x.tool);
    if(entries.some(x=>x.mode==='controls_held')) lines.push('The previous virtual settings stayed in place; no new model call was needed.');
    else if(!calls.length) lines.push('No model tool call was recorded this hour.');
    const controls={optional:'nonessential electrical loads',pump:'the water pump',generator:'the virtual generator',reserve:'the battery reserve'};
    const state=value=>typeof value==='boolean'?(value?'on':'off'):String(value);
    for(const entry of calls){
      const name=entry.tool.function.name;
      let args={};try{args=JSON.parse(entry.tool.function.arguments)}catch{}
      if(name==='request_control_action'){
        const result=entry.result||{};
        const changed=result.accepted&&JSON.stringify(result.before)!==JSON.stringify(result.after);
        lines.push(`Meta AI asked to turn ${controls[args.control]||'a virtual setting'} ${state(args.value)}. CasaOS ${result.accepted?(changed?'approved and applied it in the simulation':'approved it; the setting was already in place'):`did not apply it${result.reason?` (${result.reason})`:''}`}.`);
      }else if(name==='evaluate_action') lines.push(`Meta AI previewed turning ${controls[args.control]||'a virtual setting'} ${state(args.value)} before requesting a change.`);
      else if(name==='inspect_home_stack'||name==='read_sensors'){
        const observation='Meta AI checked the home’s simulated equipment and status.';
        if(!lines.includes(observation))lines.push(observation);
      }
      else if(name==='forecast_resources') lines.push('Meta AI estimated how long power, water, and fuel could last.');
      else if(name==='inspect_outcome') lines.push('Meta AI checked what happened after an earlier change.');
      else lines.push(`Meta AI used ${name}.`);
    }
    const failure=entries.find(x=>x.mode==='rules_fallback');
    if(failure) lines.push(`Meta inference stopped${failure.http_status?` (HTTP ${failure.http_status})`:failure.provider_response_status?` (${failure.provider_response_status})`:''}; fixed rules took over.`);
    if(entries.some(x=>x.mode==='decision_budget_exhausted')) lines.push('The model reached this decision’s turn limit; accepted controls stayed in effect.');
    lines.push(`This hour: ${row.delivered_water_l.toFixed(0)} L of water delivered; essential power ${row.critical?'on':'off'}.`);
    return lines.join('\n');
  }
  function showScore(){
    const score=el('labScore');score.replaceChildren();
    const run=report.agent||report.baseline, essentials=el('labEssentials');essentials.replaceChildren();
    for(const [label,key] of [['Essential power','critical_uptime_h'],['Water at the tap','water_uptime_h'],['Internet','network_uptime_h']]){
      const card=document.createElement('div');card.className='essential';
      const name=document.createElement('span');name.textContent=label;
      const hours=document.createElement('strong');hours.textContent=`${run.metrics[key].toFixed(0)} / ${run.history.length} h`;
      card.append(name,hours);essentials.append(card);
    }
    const waterGap=Math.max(0,run.history.length-run.metrics.water_uptime_h);
    el('labTakeaway').textContent=waterGap
      ? `Homeowner takeaway: tap water was unavailable for ${waterGap.toFixed(0)} of ${run.history.length} simulated hours. Check both stored water and a pump-compatible backup power plan before spending on equipment.`
      : 'Homeowner takeaway: tap water remained available throughout this scenario. Test a harder storm to find the limits of this plan.';
    el('labEvidence').textContent=report.agent
      ? `Meta AI used ${report.agent.evidence.model_selected_tool_calls} tools and made ${report.agent.evidence.accepted_state_changes} approved virtual changes. Open any highlighted hour to see the decision and result.`
      : 'This run used fixed rules. Choose the recorded Meta demo to see model-selected tools and approved virtual changes.';
    showMoments(run);
    const table=document.createElement('table');table.style.cssText='width:100%;border-collapse:collapse;font-size:11px;text-align:right';
    const header=document.createElement('tr');
    for(const label of ['Outcome','Fixed rules','Meta AI','Difference']){
      const cell=document.createElement('th');cell.textContent=label;cell.style.cssText='padding:5px 3px;border-bottom:1px solid #5f8d85';header.append(cell);
    }
    header.firstChild.style.textAlign='left';table.append(header);
    const metrics=[['Essential power','critical_uptime_h','h',0],['Water at the tap','water_uptime_h','h',0],
      ['Internet','network_uptime_h','h',0],['Water delivered','delivered_water_l','L',0],
      ['Water needed but unavailable','unmet_water_l','L',0],['Electricity needed but unavailable','unmet_energy_kwh','kWh',2],
      ['Fuel used','fuel_l','L',2],['Safety violations','safety_violations','',0]];
    for(const [label,key,unit,digits] of metrics){
      const row=document.createElement('tr');const base=report.baseline.metrics[key],agent=report.agent?.metrics[key],delta=report.delta?.[key];
      for(const value of [label,`${base.toFixed(digits)} ${unit}`,agent===undefined?'—':`${agent.toFixed(digits)} ${unit}`,delta===undefined?'—':`${delta>=0?'+':''}${delta.toFixed(digits)} ${unit}`]){
        const cell=document.createElement('td');cell.textContent=value;cell.style.cssText='padding:5px 3px;border-bottom:1px solid #31534e';row.append(cell);
      }
      row.firstChild.style.textAlign='left';table.append(row);
    }
    score.append(table);
    const note=document.createElement('p');note.className='muted';
    const evidence=report.agent?.evidence;
    const serviceMatch=report.agent&&['critical_uptime_h','water_uptime_h','network_uptime_h'].every(key=>report.agent.metrics[key]===report.baseline.metrics[key]);
    note.textContent=report.agent
      ? `Both plans used ${report.same_initial_conditions?'the same':'different'} starting conditions. Meta AI made ${evidence.model_selected_tool_calls} tool calls and ${evidence.accepted_state_changes} approved changes. ${serviceMatch?'Essential power, water, and internet uptime matched fixed rules.':'Compare each service above to see where the plans differed.'} More activity does not necessarily mean a better outcome.${evidence.fallback_http_status?' A provider error caused fixed-rule fallback.':''}`
      : 'This run used fixed rules only. Choose Meta AI to compare both plans.';
    score.append(note);
  }
  function showMoments(run){
    const area=el('labMoments');area.replaceChildren();
    const moments=[];
    const changed=(run.audit||[]).filter(x=>x.tool?.function?.name==='request_control_action'&&x.result?.accepted&&JSON.stringify(x.result.before)!==JSON.stringify(x.result.after));
    const firstAction=changed[0];if(firstAction)moments.push([firstAction.tick,'First AI action']);
    const generator=changed.find(x=>{try{const a=JSON.parse(x.tool.function.arguments);return a.control==='generator'&&a.value===true}catch{return false}});
    if(generator)moments.push([generator.tick,'Virtual generator']);
    for(const row of run.history){
      for(const event of row.events){
        if(/generator failure/i.test(event))moments.push([row.tick,'Generator fault']);
        else if(/water demand/i.test(event))moments.push([row.tick,'More water needed']);
        else if(/rain easing/i.test(event))moments.push([row.tick,'Rain eases']);
      }
    }
    if(!moments.length){area.hidden=true;return}
    area.hidden=false;
    const title=document.createElement('b');title.textContent='Jump to a key moment';area.append(title);
    for(const [tick,label] of moments){
      const button=document.createElement('button');button.type='button';button.dataset.tick=tick;
      button.textContent=`Hour ${tick+1} · ${label}`;area.append(button);
    }
  }
  function configuration(){
    for(const input of panel.querySelectorAll('input[type=number]')) if(!input.validity.valid) throw Error(`Check ${input.parentElement.textContent.trim()}.`);
    return {equipment:{solar_kwp:num('labSolar'),battery_kwh:num('labBattery'),inverter_kw:num('labInverter'),surge_kw:num('labSurge'),generator_kw:num('labGenerator'),cistern_l:num('labCistern'),pump_kw:num('labPump'),pump_surge_kw:num('labPumpSurge')},initial:{battery_kwh:num('labCharge'),fuel_l:num('labFuel'),cistern_l:num('labWater'),water_demand_lph:num('labDemand')}};
  }
  function showTick(){
    if(!report)return;
    const run=report.agent||report.baseline,row=run.history[Number(el('labTime').value)];if(!row)return;
    stopTimer();const eq=report.configuration.equipment;
    setState({...getState(),hour:row.hour,day:1+Math.floor((8+row.tick)/24),storm:row.weather_factor<.5,weatherFactor:row.weather_factor,grid:row.grid,installedSolar:eq.solar_kwp>0||eq.battery_kwh>0,installedGen:eq.generator_kw>0,generator:row.generator_kw>0,fuel:row.fuel_l,batteryKwh:eq.battery_kwh,battery:eq.battery_kwh>0?100*row.battery_kwh/eq.battery_kwh:0,water:row.cistern_l,cisternCapacity:eq.cistern_l,solarKw:row.solar_kw,loadsKw:row.used_kw,served:row.critical,router:row.network,ac:row.optional,pumpRequested:row.pump_on});
    render();
    document.getElementById('statusText').textContent=`Grid ${row.grid?'on':'out'} · Essentials ${row.critical?'on':'off'} · Tap water ${row.delivered_water_l>0?'flowing':'off'} · Internet ${row.network?'on':'off'}`;
    document.getElementById('metrics').textContent=`Measured hour ${row.tick+1}: ${row.battery_kwh.toFixed(2)} kWh battery · ${row.fuel_l.toFixed(2)} L fuel · ${row.cistern_l.toFixed(0)} L stored · ${row.delivered_water_l.toFixed(0)} L delivered`;
    const hour=(row.hour%12)||12;
    el('labTimeHeading').textContent=`Day ${1+Math.floor((8+row.tick)/24)} · ${hour}:00 ${row.hour<12?'AM':'PM'} · hour ${row.tick+1} of ${run.history.length}`;
    const entries=run.audit?run.audit.filter(x=>x.tick===row.tick):run.actions.filter(x=>x.tick===row.tick);
    const cue=document.getElementById('sceneEvent');
    const changed=entries.find(x=>x.tool?.function?.name==='request_control_action'&&x.result?.accepted&&JSON.stringify(x.result.before)!==JSON.stringify(x.result.after));
    if(changed){
      let args={};try{args=JSON.parse(changed.tool.function.arguments)}catch{}
      const labels={optional:'NONESSENTIAL POWER',pump:'WATER PUMP',generator:'VIRTUAL GENERATOR',reserve:'BATTERY RESERVE'};
      cue.textContent=`META AI ACTION · ${labels[args.control]||'VIRTUAL SETTING'} ${typeof args.value==='boolean'?(args.value?'ON':'OFF'):args.value}`;
      cue.dataset.kind='agent';cue.hidden=false;
    }else if(row.events.length){
      cue.textContent=`SIMULATED EVENT · ${row.events.join(' · ')}`;
      cue.dataset.kind='weather';cue.hidden=false;
    }else cue.hidden=true;
    el('labAgentSummary').textContent=decisionSummary(entries,row);
    el('labTrace').textContent=JSON.stringify({events:row.events,controller:report.status,trace:entries},null,2);
  }
  function loadReport(result,source){
    stopPlayback();
    report=result;
    el('labResults').hidden=false;
    el('labStatus').hidden=false;
    el('labResultSource').textContent=source==='saved'?'RECORDED META AI RUN':source==='live'?'LIVE META AI RUN':'FIXED-RULE RUN';
    el('labStatus').textContent=source==='saved'?'Showing the recorded Meta AI storm run. Move the timeline to follow the decisions.':source==='live'?'Live Meta AI run complete. Explore each hour below.':'Fixed-rule run complete. Explore each hour below.';
    el('labModelName').textContent=report.agent?`Meta model: ${report.agent.model}`:'Meta AI available for a comparison run';
    el('labMode').textContent=source==='saved'?'Recorded Meta API responses · no new credits used':source==='live'?'Live Meta API run · credits used': 'This run used fixed rules; no Meta model calls were made.';
    showScore();
    el('labTime').max=(report.agent||report.baseline).history.length-1;
    el('labTime').value=0;
    el('labDownload').disabled=false;
    showTick();
    el('labResults').scrollIntoView({block:'start'});
  }
  function stopPlayback(){if(playback)clearTimeout(playback);playback=null;el('labPlay').textContent='▶ Play the story'}
  function playNext(){
    if(!report)return;
    const slider=el('labTime');
    if(Number(slider.value)>=Number(slider.max)){stopPlayback();return}
    slider.value=Number(slider.value)+1;showTick();
    const run=report.agent||report.baseline,row=run.history[Number(slider.value)];
    const entries=run.audit?run.audit.filter(x=>x.tick===row.tick):[];
    const action=entries.some(x=>x.tool?.function?.name==='request_control_action'&&x.result?.accepted&&JSON.stringify(x.result.before)!==JSON.stringify(x.result.after));
    playback=setTimeout(playNext,row.events.length||action?1300:320);
  }
  el('labPlay').addEventListener('click',()=>{
    if(playback){stopPlayback();return}
    if(!report)return;
    if(Number(el('labTime').value)>=Number(el('labTime').max)){el('labTime').value=0;showTick()}
    el('labPlay').textContent='■ Pause story';playback=setTimeout(playNext,850);
  });
  el('labMoments').addEventListener('click',event=>{
    const button=event.target.closest('button[data-tick]');if(!button)return;
    stopPlayback();el('labTime').value=button.dataset.tick;showTick();
  });
  el('labTime').addEventListener('input',()=>{stopPlayback();showTick()});
  el('labDownload').addEventListener('click',()=>{if(!report)return;const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`casaos-${report.scenario}-${report.status}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
  el('labSaved').addEventListener('click',async()=>{
    el('labSaved').disabled=true;
    try{
      el('labStatus').hidden=false;el('labStatus').textContent='Loading the recorded Meta AI run…';
      const response=await fetch('/api/lab/saved/storm72-meta');const result=await response.json();
      if(!response.ok)throw Error(result.error||'Saved run unavailable');
      loadReport(result,'saved');
    }catch(error){el('labStatus').textContent=error.message}finally{el('labSaved').disabled=false}
  });
  el('labRun').addEventListener('click',async()=>{
    el('labRun').disabled=true;
    try{
      el('labStatus').hidden=false;
      const payload={scenario:el('labScenario').value,controller:el('labController').value,configuration:configuration()};
      el('labStatus').textContent=payload.controller==='meta'?'Running event-triggered agent; at most 80 Meta requests. API credits are used.':'Running offline rules baseline.';
      const response=await fetch('/api/lab/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const job=await response.json();if(!response.ok)throw Error(job.error);
      for(;;){const state=await (await fetch('/api/lab/jobs/'+job.job)).json();if(state.status==='failed'||state.status==='unknown')throw Error(state.error||state.status);if(state.status==='complete'){report=state.result;break}await new Promise(resolve=>setTimeout(resolve,1200))}
      loadReport(report,payload.controller==='meta'?'live':'baseline');
    }catch(error){el('labStatus').textContent=error.message}finally{el('labRun').disabled=false}
  });
}
