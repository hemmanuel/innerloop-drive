// Run with NODE_PATH pointing at Playwright, and serve_test_workspace.py running.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.INNERLOOP_TEST_URL||'http://127.0.0.1:18781';
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const errors=[];
  async function device(){
    const context=await browser.newContext({viewport:{width:1365,height:900},serviceWorkers:'allow'});
    await context.route('https://innerloop-test.supabase.co/**',async route=>{
      try {const response=await route.fetch({url:route.request().url().replace('https://innerloop-test.supabase.co',base)});await route.fulfill({response});}
      catch(e){await route.abort();}
    });
    await context.route('https://tile.openstreetmap.org/**',route=>route.abort());
    const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto(base);
    await page.locator('[name=url]').fill('https://innerloop-test.supabase.co');
    await page.locator('[name=key]').fill('sb_publishable_fixture');
    await page.locator('[name=email]').fill('fixture@example.test');await page.locator('[name=password]').fill('fixture');
    await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.locator('#login').waitFor({state:'hidden'});
    await page.locator('.site-row').first().waitFor();return {context,page};
  }
  const desktop=await device(),field=await device();
  const a=desktop.page,b=field.page;
  await a.locator('.site-row').first().click();await a.getByRole('button',{name:'Save to list',exact:true}).click();
  await a.getByText('Remove from this list',{exact:true}).waitFor();
  await a.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  await b.locator('#sync').click();await b.getByRole('button',{name:'Saved lists',exact:true}).click();
  await b.locator('.site-row strong').filter({hasText:'100 Workflow Test St'}).click();
  // Offline queue survives a page reload, then appears on the other device.
  let disconnected=true,loseAcknowledgment=false;
  await field.context.route('https://innerloop-test.supabase.co/**',async route=>{
    if(disconnected)return route.abort();
    const response=await route.fetch({url:route.request().url().replace('https://innerloop-test.supabase.co',base)});
    if(loseAcknowledgment&&route.request().url().endsWith('/mutate')){loseAcknowledgment=false;return route.abort();}
    await route.fulfill({response});
  });
  await b.getByRole('button',{name:'Record visit',exact:true}).click();
  const note='Offline visit '+Date.now();await b.locator('[name=note]').fill(note);await b.locator('[name=rating]').selectOption('4');
  await b.getByRole('button',{name:'Save visit',exact:true}).click();await b.getByText(note,{exact:false}).first().waitFor();
  await b.evaluate(()=>navigator.serviceWorker.ready);await b.waitForFunction(()=>!!navigator.serviceWorker.controller);
  await field.context.setOffline(true);await b.reload();await b.getByRole('button',{name:'Saved lists',exact:true}).click();await b.locator('.site-row').first().click();
  await b.getByText(note,{exact:false}).first().waitFor();
  await field.context.setOffline(false);disconnected=false;loseAcknowledgment=true;
  await b.locator('#sync').click();await b.waitForFunction(()=>!document.querySelector('#sync').disabled);
  await b.locator('#sync').click();await b.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  await a.locator('#sync').click();await a.locator('.note').filter({hasText:note}).waitFor();
  assert.equal(await a.locator('.note').filter({hasText:note}).count(),1);
  await a.locator('#sync').click();assert.equal(await a.locator('.note').filter({hasText:note}).count(),1);
  await a.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  // Two devices edit the same revision. Neither silently overwrites the other.
  disconnected=true;
  await b.locator('#detail label').filter({hasText:'List status'}).locator('select').selectOption('pursue');
  await a.locator('#detail label').filter({hasText:'List status'}).locator('select').selectOption('pass');
  await a.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  disconnected=false;await b.locator('#sync').click();
  await b.waitForFunction(()=>document.querySelector('#sync-state').textContent.includes('conflict'));
  await b.locator('#sync-state').click();await b.getByRole('button',{name:'Keep server version',exact:true}).click();
  await b.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  assert.equal(await b.locator('#detail label').filter({hasText:'List status'}).locator('select').inputValue(),'pass');
  // A stale bundle's unknown site must not block later valid field notes.
  const recovery=await a.evaluate(async()=>{
    const {LocalStore,Api,Sync}=await import('./sync.mjs');const c=JSON.parse(localStorage.getItem('innerloop.connection'));
    const store=await new LocalStore(`innerloop:${c.url}:${c.session.user.id}:${c.workspace}`).open();
    const sync=new Sync(new Api(c),store,c.workspace);
    const bad=await sync.enqueue('visit',{site_id:'S0000000000000',note:'Unmatched bundle fixture',observed_at:new Date().toISOString()});
    const good=await sync.enqueue('visit',{site_id:'S9999999999991',note:'Valid note after a rejected operation',observed_at:new Date().toISOString()});
    await sync.run();const result=await store.read();
    const check={problem:!!result.outbox.find(m=>m.id===bad)?.problem,saved:!!result.visits[good]};
    await sync.resolve(bad,false);return check;
  });
  assert.deepEqual(recovery,{problem:true,saved:true});
  await a.locator('#sync').click();await a.waitForFunction(()=>document.querySelector('#sync-state').textContent==='Synced');
  fs.mkdirSync('.local/qa',{recursive:true});await a.screenshot({path:'.local/qa/desktop-workflow.png',fullPage:true});
  await b.setViewportSize({width:1024,height:600});await b.screenshot({path:'.local/qa/field-workflow.png',fullPage:true});
  assert.deepEqual(errors,[]);console.log('PASS: desktop save, second device, offline shell reload, lost acknowledgment, single observation, edit conflict resolution, rejected-operation recovery');
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
