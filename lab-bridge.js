// Replay authoritative backend state into the existing Three.js renderer.
const panel=document.createElement('div');panel.className='section';
panel.innerHTML=`<h2>Measured resilience runs</h2><p>Hourly Python simulation · illustrative virtual upgrades · no physical controls</p><select id="labScenario"><option value="sunny">Sunny day · 24 h</option><option value="downpour">Tropical downpour · 24 h</option><option value="storm72" selected>Storm + failure · 72 h</option></select><select id="labController"><option value="baseline">Rules baseline</option><option value="meta">Meta agent + baseline A/B</option></select><button id="labRun">Run scenario</button><p id="labStatus"></p><input id="labTime" type="range" min="0" max="0" value="0" style="width:100%"><pre id="labScore" style="white-space:pre-wrap"></pre><pre id="labTrace" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>`;
document.querySelector('aside').prepend(panel);
let report=null;
const el=id=>document.getElementById(id);
function showTick(){
 if(!report)return;
 const run=report.agent||report.baseline;const row=run.history[Number(el('labTime').value)];
 if(!row)return;
 if(timer){clearInterval(timer);timer=null;document.getElementById('auto').textContent='▶ Auto-run'}
 s={...s,hour:row.hour,day:1+Math.floor((8+row.tick)/24),storm:row.weather_factor<.5,grid:row.grid,installedSolar:true,installedGen:true,generator:row.generator_kw>0,fuel:row.fuel_l,battery:row.battery_kwh/10*100,water:row.cistern_l,solarKw:row.solar_kw,loadsKw:row.used_kw,served:row.critical,router:row.network,ac:row.optional,pumpRequested:row.pump_on,serviceHours:run.history.slice(0,row.tick+1).filter(x=>x.critical&&x.network&&x.pump_on).length,gridOutageHours:run.history.slice(0,row.tick+1).filter(x=>!x.grid).length};
 render(); // Override legacy derived labels with measured backend outcomes.
 document.getElementById('statusText').textContent=`${row.grid?'DELSUR online':'DELSUR OUTAGE'} · ${row.pump_on?'water delivered':'no water delivery'} · Cabal ${row.network?'up':'down'}`;
 document.getElementById('metrics').textContent=`Authoritative tick ${row.tick}: ${row.battery_kwh.toFixed(2)} kWh battery · ${row.fuel_l.toFixed(2)} L fuel · ${row.cistern_l.toFixed(0)} L stored · ${row.delivered_water_l.toFixed(0)} L delivered`;
 const entries=run.audit?run.audit.filter(x=>x.tick===row.tick):run.actions.filter(x=>x.tick===row.tick);
 el('labTrace').textContent=JSON.stringify({events:row.events,controller:report.status,trace:entries},null,2);
}
el('labTime').oninput=showTick;
el('labRun').onclick=async()=>{
 el('labRun').disabled=true;el('labStatus').textContent=el('labController').value==='meta'?'Running; at most 16 Meta requests, 512 output tokens each. API credits are used.':'Running offline baseline.';
 try{
 const response=await fetch('/api/lab/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scenario:el('labScenario').value,controller:el('labController').value})});
 const job=await response.json();if(!response.ok)throw Error(job.error);
 for(;;){
 const state=await (await fetch('/api/lab/jobs/'+job.job)).json();
 if(state.status==='failed'||state.status==='unknown')throw Error(state.error||state.status);
 if(state.status==='complete'){report=state.result;break}
 await new Promise(r=>setTimeout(r,1200));
 }
 el('labStatus').textContent=report.status;
 el('labScore').textContent=JSON.stringify({baseline:report.baseline.metrics,agent:report.agent?.metrics||'Not run',delta:report.delta},null,2);
 el('labTime').max=(report.agent||report.baseline).history.length-1;el('labTime').value=0;showTick();
 }catch(error){el('labStatus').textContent=error.message}finally{el('labRun').disabled=false}
};
