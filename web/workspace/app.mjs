import {Api,LocalStore,Sync,itemKey} from './sync.mjs';
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
let api,store,sync,workspace,state,selected,mode='browse',rows=[],page='',busy=false,connection;
const map=L.map('map',{zoomControl:true}).setView([29.735,-95.353],14);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:20,attribution:'© OpenStreetMap contributors'}).addTo(map);
const shapes=L.featureGroup().addTo(map),layouts=L.featureGroup().addTo(map);
function message(text) {$('message').textContent=text;$('message').style.display='block';clearTimeout(message.timer);message.timer=setTimeout(()=>$('message').style.display='none',6500);}
function persist(c) {localStorage.setItem('innerloop.connection',JSON.stringify(c));}
function validConnection(url,key) {
  const u=new URL(url);
  if(u.protocol!=='https:'||u.username||u.password||u.pathname!=='/'||u.search||u.hash)throw new Error('Enter the HTTPS project origin.');
  if(key.startsWith('sb_secret_'))throw new Error('Use the publishable key, not a server secret.');
  if(key.split('.').length===3) {
    try {if(JSON.parse(atob(key.split('.')[1].replaceAll('-','+').replaceAll('_','/'))).role==='service_role')throw new Error('Service-role keys cannot be used here.');}
    catch(e) {if(e.message.includes('Service-role'))throw e;}
  }
  return u.origin;
}
async function connect(c,online=true) {
  const nextApi=new Api(c,persist);
  const nextWorkspace=online?(await nextApi.rpc('open_workspace',{})).id:c.workspace;
  if(!nextWorkspace)throw new Error('Sign in once while online to initialize this device.');
  const nextStore=await new LocalStore(`innerloop:${c.url}:${c.session.user.id}:${nextWorkspace}`).open();
  connection=c;api=nextApi;workspace=nextWorkspace;store=nextStore;c.workspace=workspace;persist(c);
  sync=new Sync(api,store,workspace);await refreshLocal();
  await synchronize();await loadCatalog();
}
async function refreshLocal() {
  if(!store)return;
  state=await store.read();const old=$('lists').value;$('lists').replaceChildren();
  for(const list of Object.values(state.lists)) {$('lists').append(new Option(list.name,list.id));}
  if(state.lists[old])$('lists').value=old;
  const n=state.outbox.length,conflicts=state.outbox.filter(x=>x.conflict).length,problems=state.outbox.filter(x=>x.problem).length;
  $('sync-state').textContent=conflicts?`${conflicts} conflict${conflicts>1?'s':''} · tap to resolve`:problems?`${problems} changes need review · tap here`:n?`${n} saved locally · awaiting sync`:'Synced';
  if(mode==='saved')renderSaved();
  if(selected)renderDetail(selected);
}
async function synchronize() {
  if(!sync||busy)return;busy=true;$('sync').disabled=true;$('sync-state').textContent='Syncing…';
  try {await sync.run();await refreshLocal();}
  catch(e) {await refreshLocal();$('sync-state').textContent=`${state.outbox.length} pending · ${navigator.onLine?'sync unavailable':'offline'}`;message(e.message);}
  finally {busy=false;$('sync').disabled=false;}
}
async function loadCatalog() {
  if(!api)return;
  try {
    const c=await api.rpc('catalog_summary',{w:workspace});
    const old=$('neighborhood').value;$('neighborhood').replaceChildren(new Option('All neighborhoods',''));
    for(const n of c.neighborhoods)$('neighborhood').append(new Option(`${n.name} · ${n.fits} fits`,n.name));
    $('neighborhood').value=old;
    const oldArea=$('area').value;$('area').replaceChildren(new Option('Entire Loop',''));
    for(const n of c.areas||[])if(n.name)$('area').append(new Option(`${n.name} · ${n.fits} fits`,n.name));
    $('area').value=oldArea;
    $('catalog').textContent=c.run?`${c.run.expected_parcels.toLocaleString()} parcels · ${c.run.scope} · ${c.run.model.version}`:'Workspace ready. Import a screening snapshot to begin.';
    if(mode==='browse')await browse();
  }catch(e){$('catalog').textContent='Offline inventory: open Saved lists for downloaded sites.';message(e.message);}
}
async function browse(more=false) {
  if(!api)return;
  try {
    const bounds=map.getBounds();
    const next=await api.rpc('browse_sites',{w:workspace,neighborhood_filter:$('neighborhood').value,area_filter:$('area').value,
      fit_only:$('fit').checked,search_text:$('search').value.trim(),after_site:more?page:'',
      viewport:$('viewport').checked?[bounds.getWest(),bounds.getSouth(),bounds.getEast(),bounds.getNorth()]:null});
    rows=more?[...rows,...next]:next;page=next.at(-1)?.site_id||'';
    $('more').hidden=next.length<250;renderRows(rows);
    $('map-caption').textContent=`${rows.length.toLocaleString()} sites shown${next.length===250?' · load more or narrow the view':''}`;
    if(!more&&!$('viewport').checked&&!selected&&shapes.getBounds().isValid())map.fitBounds(shapes.getBounds().pad(.1));
  }catch(e){message(e.message);}
}
function effectiveItems() {
  const items={...state.items};
  for(const m of state.outbox)if(m.kind==='save')items[itemKey(m.payload)]={...m.payload,pending:true};
  return Object.values(items);
}
function renderSaved() {
  rows=effectiveItems().filter(i=>!i.deleted&&i.list_id===$('lists').value)
    .map(i=>({...state.sites[i.site_id],site_id:i.site_id,saved_status:i.status,pending:i.pending}));
  $('more').hidden=true;renderRows(rows);
}
function renderRows(sites) {
  $('results').replaceChildren();shapes.clearLayers();
  if(!sites.length)$('results').append(el('p',mode==='saved'?'No sites in this list yet.':'No sites match these filters.','site-row'));
  for(const s of sites) {
    const row=el('div',undefined,'site-row');row.tabIndex=0;row.dataset.site=s.site_id;
    row.append(el('strong',s.address||s.site_id),el('small',`${Number(s.area_sf||0).toLocaleString()} sq ft · ${s.neighborhood||''}`),
      el('span',s.pending?'Saved locally':s.saved_status||s.status?.replaceAll('_',' ')||'Saved','badge'+(s.fits?'':' review')));
    row.onclick=()=>select(s);row.onkeydown=e=>{if(e.key==='Enter')select(s);};$('results').append(row);
    if(s.geometry)L.geoJSON(s.geometry,{style:{color:s.fits?'#285746':'#aa8043',weight:1.5,fillOpacity:.24}}).on('click',()=>select(s)).addTo(shapes);
  }
}
async function select(s) {
  selected=s;renderDetail(s);layouts.clearLayers();
  if(s.geometry){const layer=L.geoJSON(s.geometry);map.fitBounds(layer.getBounds().pad(1));}
  try {
    const full=await api.rpc('site_detail',{w:workspace,s:s.site_id});
    if(full&&selected?.site_id===s.site_id) {selected=full;await store.change(x=>x.sites[s.site_id]=full);renderDetail(full);}
  }catch(e){if(!s.geometry)message('This site has not been downloaded for offline viewing.');}
}
function renderDetail(s) {
  const d=$('detail');d.hidden=false;d.replaceChildren();
  const close=el('button','×','close');close.onclick=()=>{selected=null;d.hidden=true;layouts.clearLayers();};
  d.append(close,el('h2',s.address||s.site_id),el('small',s.neighborhood||''));
  const facts=el('div',undefined,'facts');
  for(const [v,label] of [[Number(s.area_sf||0).toLocaleString(),'land sq ft'],
    [s.details?.transit_distance_ft!=null?(s.details.transit_distance_ft/5280).toFixed(2)+' mi':'—','nearest transit · straight line']]) {
    const f=el('div');f.append(el('strong',v),el('span',label));facts.append(f);
  }
  d.append(facts,el('p',s.details?.layout?.reason||s.status?.replaceAll('_',' ')||'Saved site'));
  const layout=s.details?.layout;
  if(layout?.frontage_ft!=null)d.append(el('p',`${layout.frontage_ft} ft street frontage · ${layout.depth_ft} ft depth`));
  const anchors=s.details?.anchor_straight_line_mi;
  if(anchors)d.append(el('p',Object.entries(anchors).map(([k,v])=>`${k} ${v} mi`).join(' · ')+' · straight line'));
  if(s.details?.block_quality?.repeat_violence_review)d.append(el('p','Field priority: inspect the block flagged for repeated serious violence.'));
  if(s.details?.mail_matches_site===true)d.append(el('p','Owner mailing address matches the site.'));
  d.append(el('small',(s.accounts||[]).join(' · ')));
  if(s.details?.flood_zone)d.append(el('p','Flood zone: '+s.details.flood_zone));
  const actions=el('div',undefined,'actions');const save=el('button','Save to list'),visit=el('button','Record visit');
  const listLabel=el('label','Save to');const choose=el('select');
  for(const l of Object.values(state.lists))choose.append(new Option(l.name,l.id));choose.value=$('lists').value;
  choose.onchange=()=>{$('lists').value=choose.value;renderDetail(s);};listLabel.append(choose);d.append(listLabel);
  save.onclick=async()=>{
    const list=$('lists').value;if(!list)return message('Sync to download or create your first list.');
    try {await sync.enqueue('save',{list_id:list,site_id:s.site_id,status:'saved',deleted:false},s);await refreshLocal();message('Saved locally');synchronize();}catch(e){message(e.message);}
  };
  visit.onclick=()=>{$('visit-address').textContent=s.address;$('visit').showModal();};actions.append(save,visit);d.append(actions);
  const saved=effectiveItems().find(i=>i.site_id===s.site_id&&i.list_id===$('lists').value&&!i.deleted);
  if(saved) {
    const label=el('label','List status');const status=el('select');status.setAttribute('aria-label','List status');
    for(const st of ['saved','visited','pursue','pass'])status.append(new Option(st,st));status.value=saved.status;
    status.onchange=async()=>{try {await sync.enqueue('save',{list_id:saved.list_id,site_id:s.site_id,status:status.value,deleted:false},s);await refreshLocal();synchronize();}catch(e){message(e.message);status.value=saved.status;}};
    label.append(status);d.append(label);
    const remove=el('button','Remove from this list');remove.onclick=async()=>{try {await sync.enqueue('save',{list_id:saved.list_id,site_id:s.site_id,status:saved.status,deleted:true},s);await refreshLocal();synchronize();}catch(e){message(e.message);}};d.append(remove);
  }
  const visitMap={...state.visits};
  for(const m of state.outbox)if(m.kind==='visit'&&!visitMap[m.id])visitMap[m.id]={...m.payload,id:m.id,pending:true};
  const visits=Object.values(visitMap)
    .filter(v=>v.site_id===s.site_id).sort((a,b)=>b.observed_at.localeCompare(a.observed_at));
  for(const v of visits){const n=el('div',v.note,'note');n.append(el('small',`${new Date(v.observed_at).toLocaleString()}${v.block_rating?' · Block '+v.block_rating+'/5':''}${v.pending?' · saved locally':''}`));d.append(n);}
  layouts.clearLayers();
  for(const overlay of s.details?.layout?.overlays||[])L.geoJSON(overlay.geometry,{style:{color:({building:'#173f5f',parking:'#bb8833',walk:'#648c4b',entry:'#648c4b',clearance:'#8a998a'})[overlay.kind]||'#999',weight:1,fillOpacity:overlay.kind==='clearance'?.06:.3}}).addTo(layouts);
}
function setMode(next) {mode=next;$('browse').classList.toggle('active',next==='browse');$('saved').classList.toggle('active',next==='saved');$('list-controls').hidden=next!=='saved';if(next==='saved'&&state)renderSaved();else browse();}
$('browse').onclick=()=>setMode('browse');$('saved').onclick=()=>setMode('saved');$('lists').onchange=renderSaved;
$('fit').onchange=()=>browse();$('neighborhood').onchange=()=>{selected=null;$('detail').hidden=true;browse();};
$('area').onchange=()=>{selected=null;$('detail').hidden=true;browse();};
$('search').onchange=()=>browse();$('more').onclick=()=>browse(true);$('viewport').onchange=()=>browse();
let moveTimer;map.on('moveend',()=>{if($('viewport').checked&&mode==='browse'){clearTimeout(moveTimer);moveTimer=setTimeout(()=>browse(),300);}});
$('sync').onclick=async()=>{await synchronize();await loadCatalog();};
$('connection').onclick=()=>{$('login').showModal();if(connection){$('login-form').elements.url.value=connection.url;$('login-form').elements.key.value=connection.key;$('login-form').elements.email.value=connection.session?.user?.email||'';}};
$('close-login').onclick=()=>$('login').close();
$('login-form').onsubmit=async e=>{
  e.preventDefault();const f=e.target.elements;$('login-error').textContent='';
  try {const c={url:validConnection(f.url.value.trim(),f.key.value.trim()),key:f.key.value.trim()};
    const a=new Api(c);await a.signIn(f.email.value.trim(),f.password.value);f.password.value='';
    await connect(c);$('login').close();
  }catch(error){$('login-error').textContent=error.message;}
};
$('new-list').onclick=async()=>{const name=prompt('List name');if(!name?.trim())return;try {await sync.enqueue('list',{name:name.trim()});await refreshLocal();await synchronize();}catch(e){message(e.message);}};
$('cancel-visit').onclick=()=>$('visit').close();
$('visit-form').onsubmit=async e=>{
  e.preventDefault();const f=e.target.elements;
  try {await sync.enqueue('visit',{site_id:selected.site_id,note:f.note.value.trim(),block_rating:f.rating.value?Number(f.rating.value):null,observed_at:new Date().toISOString()},selected);
    e.target.reset();$('visit').close();await refreshLocal();message('Visit saved on this device');synchronize();
  }catch(error){message(error.message);}
};
$('sync-state').onclick=()=>{
  if(!state)return;const c=state.outbox.filter(m=>m.conflict||m.problem);if(!c.length)return;
  $('conflict-rows').replaceChildren();for(const m of c){const row=el('div');row.append(el('p',m.problem?`${m.problem}\n${m.payload.note||m.payload.name||m.payload.site_id}`:`${state.sites[m.payload.site_id]?.address||m.payload.site_id}: this device ${m.payload.status}; server ${m.conflict.current?.status||'removed'}`));
    const options=m.problem?[['Retry this change',true],['Discard this local change',false]]:[['Use this device',true],['Keep server version',false]];
    for(const [text,keep] of options){const b=el('button',text);b.onclick=async()=>{await sync.resolve(m.id,keep);$('conflicts').close();await synchronize();};row.append(b);}$('conflict-rows').append(row);}$('conflicts').showModal();
};
$('close-conflicts').onclick=()=>$('conflicts').close();
window.addEventListener('online',()=>synchronize());
setInterval(()=>{if(document.visibilityState==='visible')synchronize();},30000);
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')synchronize();});
try {const saved=JSON.parse(localStorage.getItem('innerloop.connection')||'null');if(saved?.session)await connect(saved,false);else $('login').showModal();}
catch(e){message(e.message);$('login').showModal();}
if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(e=>message('Offline shell: '+e.message));
