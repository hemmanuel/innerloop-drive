// Durable, account-scoped outbox. Acknowledgment can be lost without duplicating
// an observation: the original UUID and exact request are retained until accepted.
export const emptyState = () => ({cursor:0, lists:{}, items:{}, visits:{}, sites:{}, outbox:[]});
export const itemKey = (p) => `${p.list_id}:${p.site_id}`;

export class LocalStore {
  constructor(name) { this.name=name; }
  async open() {
    this.db=await new Promise((resolve,reject)=>{
      const r=indexedDB.open(this.name,1);
      r.onupgradeneeded=()=>r.result.createObjectStore('state');
      r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);
    });
    return this;
  }
  async read() {
    return new Promise((resolve,reject)=>{
      const r=this.db.transaction('state').objectStore('state').get('current');
      r.onsuccess=()=>resolve(r.result||emptyState());r.onerror=()=>reject(r.error);
    });
  }
  async change(fn) {
    return new Promise((resolve,reject)=>{
      const tx=this.db.transaction('state','readwrite');const store=tx.objectStore('state');
      const r=store.get('current');let value;
      r.onsuccess=()=>{
        try {const s=r.result||emptyState();value=fn(s);store.put(s,'current');}
        catch(e) {reject(e);tx.abort();}
      };
      tx.oncomplete=()=>resolve(value);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error||new Error('Local write aborted'));
    });
  }
}

export class Api {
  constructor(connection, saveSession=()=>{}) {this.c=connection;this.saveSession=saveSession;this.refreshing=null;}
  async request(path,body,auth=true,retry=true) {
    const headers={'apikey':this.c.key,'Content-Type':'application/json'};
    if(auth)headers.Authorization=`Bearer ${this.c.session.access_token}`;
    const res=await fetch(this.c.url+path,{method:'POST',headers,body:JSON.stringify(body)});
    const data=await res.json();
    if(res.status===401&&auth&&retry&&this.c.session.refresh_token) {
      await this.refresh();return this.request(path,body,auth,false);
    }
    if(!res.ok){const error=new Error(data.message||data.error_description||data.msg||`HTTP ${res.status}`);error.status=res.status;throw error;}
    return data;
  }
  async refresh() {
    if(!this.refreshing)this.refreshing=this.request('/auth/v1/token?grant_type=refresh_token',
      {refresh_token:this.c.session.refresh_token},false).then(s=>{this.c.session=s;this.saveSession(this.c);})
      .finally(()=>this.refreshing=null);
    return this.refreshing;
  }
  async signIn(email,password) {
    this.c.session=await this.request('/auth/v1/token?grant_type=password',{email,password},false);
    this.saveSession(this.c);return this.c.session;
  }
  rpc(name,args) {return this.request('/rest/v1/rpc/'+name,args);}
}

export class Sync {
  constructor(api,store,workspace) {this.api=api;this.store=store;this.w=workspace;this.running=null;}
  async enqueue(kind,payload,site=null) {
    if(kind==='visit'&&(!payload.note?.trim()||payload.note.length>12000))throw new Error('Enter a visit note of 1–12,000 characters.');
    if(kind==='list'&&(!payload.name?.trim()||payload.name.length>120))throw new Error('List names must contain 1–120 characters.');
    const mutation={id:crypto.randomUUID(),kind,payload};
    await this.store.change(s=>{
      if(site)s.sites[site.site_id]=site;
      if(kind==='save') {
        if(s.outbox.some(x=>x.kind==='save'&&itemKey(x.payload)===itemKey(payload)))
          throw new Error('This site has an unsynced change. Sync it before changing its status again.');
        mutation.payload.expected_revision=s.items[itemKey(payload)]?.revision||0;
      }
      s.outbox.push(mutation);
    });
    return mutation.id;
  }
  async resolve(id,useLocal) {
    await this.store.change(s=>{
      const pending=s.outbox.find(x=>x.id===id);if(!pending)return;
      if(useLocal) {
        if(pending.conflict)pending.payload.expected_revision=pending.conflict?.current?.revision||0;
        delete pending.conflict;
        delete pending.problem;
      } else s.outbox=s.outbox.filter(x=>x.id!==id);
    });
  }
  async pull() {
    for(;;) {
      const state=await this.store.read();
      const events=await this.api.rpc('pull_changes',{w:this.w,after_revision:state.cursor});
      if(!events.length)return;
      await this.store.change(s=>{
        for(const e of events) {
          if(e.revision<=s.cursor)continue;
          const p=e.payload;
          const {site,...record}=p;
          if(e.kind==='list')s.lists[p.id]=p;
          if(e.kind==='save')s.items[itemKey(p)]=record;
          if(e.kind==='visit')s.visits[p.id]=record;
          if(p.site)s.sites[p.site_id]=p.site;
          s.cursor=e.revision;
        }
      });
      if(events.length<250)return;
    }
  }
  async run() {
    if(this.running)return this.running;
    this.running=this._run().finally(()=>this.running=null);return this.running;
  }
  async _run() {
    await this.pull();
    const state=await this.store.read();
    for(const entry of state.outbox) {
      if(entry.conflict||entry.problem)continue;
      const {conflict,problem,...mutation}=entry;
      let response;
      try {response=await this.api.rpc('mutate',{w:this.w,mutation});}
      catch(error) {
        if([400,404,409,422].includes(error.status)) {
          await this.store.change(s=>{const row=s.outbox.find(x=>x.id===entry.id);if(row)row.problem=error.message;});
          continue;
        }
        throw error;
      }
      await this.store.change(s=>{
        if(response.conflict) {
          const row=s.outbox.find(x=>x.id===entry.id);if(row)row.conflict=response;
        } else s.outbox=s.outbox.filter(x=>x.id!==entry.id);
      });
    }
    await this.pull();
  }
}
