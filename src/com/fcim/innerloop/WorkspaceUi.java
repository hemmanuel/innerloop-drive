package com.fcim.innerloop;

import android.app.Activity;
import android.app.AlertDialog;
import android.text.InputType;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.Toast;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import org.json.JSONObject;
import org.json.JSONArray;

/** Native list/visit dialogs; map rendering remains native Canvas. */
final class WorkspaceUi {
    private final Activity activity;private final ParcelMapView map;
    final WorkspaceSync sync;
    WorkspaceUi(Activity a,ParcelMapView m,Runnable changed) {
        activity=a;map=m;
        sync=new WorkspaceSync(a,value->a.runOnUiThread(()->{refreshHighlights();changed.run();}));
    }
    private void error(Exception e){Toast.makeText(activity,e.getMessage(),Toast.LENGTH_LONG).show();}
    private JSONObject state() throws Exception {
        if(sync.store==null)throw new Exception("Connect the workspace first");
        return sync.store.read();
    }
    private JSONObject items(JSONObject s) throws Exception {
        JSONObject items=new JSONObject(s.getJSONObject("items").toString());JSONArray q=s.getJSONArray("outbox");
        for(int i=0;i<q.length();i++)if(q.getJSONObject(i).getString("kind").equals("save")) {
            JSONObject p=q.getJSONObject(i).getJSONObject("payload");items.put(WorkspaceStore.itemKey(p),p);
        }
        return items;
    }
    private void refreshHighlights() {
        try {
            JSONObject items=items(state());Set<String> saved=new HashSet<>();Iterator<String> it=items.keys();
            while(it.hasNext()){JSONObject p=items.getJSONObject(it.next());if(!p.optBoolean("deleted"))saved.add(p.getString("site_id"));}
            map.setSavedSites(saved);
        }catch(Exception ignored){map.setSavedSites(new HashSet<>());}
    }
    void menu() {
        new AlertDialog.Builder(activity).setTitle("Workspace · "+sync.status)
            .setItems(new String[]{"Saved lists","Sync now","Review sync issues","Connection"},(d,n)->{
                if(n==0)lists();else if(n==1)sync.sync();else if(n==2)conflicts();else connection();
            }).setNegativeButton("Close",null).show();
    }
    private void connection() {
        LinearLayout body=new LinearLayout(activity);body.setOrientation(1);body.setPadding(24,12,24,12);
        EditText url=input(body,"https://project.supabase.co",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_URI);
        EditText key=input(body,"Publishable key",InputType.TYPE_CLASS_TEXT);
        EditText email=input(body,"Email",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        EditText password=input(body,"Password",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        new AlertDialog.Builder(activity).setTitle("Connect Supabase").setView(body)
            .setPositiveButton("Sign in",(d,n)->sync.signIn(url.getText().toString().trim(),key.getText().toString().trim(),
                email.getText().toString().trim(),password.getText().toString()))
            .setNegativeButton("Cancel",null).show();
    }
    private EditText input(LinearLayout parent,String hint,int type) {
        EditText v=new EditText(activity);v.setHint(hint);v.setInputType(type);parent.addView(v);return v;
    }
    private void lists() {
        try {
            JSONObject lists=state().getJSONObject("lists");ArrayList<String> ids=new ArrayList<>(),names=new ArrayList<>();
            Iterator<String> it=lists.keys();while(it.hasNext()){String id=it.next();ids.add(id);names.add(lists.getJSONObject(id).getString("name"));}
            new AlertDialog.Builder(activity).setTitle("Saved lists")
                .setItems(names.toArray(new String[0]),(d,n)->list(ids.get(n),names.get(n)))
                .setPositiveButton("New list",(d,n)->newList()).setNegativeButton("Close",null).show();
        }catch(Exception e){error(e);}
    }
    private void newList() {
        EditText name=new EditText(activity);name.setHint("List name");
        new AlertDialog.Builder(activity).setTitle("New list").setView(name).setPositiveButton("Create",(d,n)->{
            try {String text=name.getText().toString().trim();if(text.isEmpty())return;
                sync.store.enqueue("list",new JSONObject().put("name",text),null);sync.sync();
            }catch(Exception e){error(e);}
        }).setNegativeButton("Cancel",null).show();
    }
    private void list(String id,String name) {
        try {
            JSONObject s=state(),items=items(s);ArrayList<JSONObject> sites=new ArrayList<>();ArrayList<String> labels=new ArrayList<>();
            Iterator<String> it=items.keys();
            while(it.hasNext()) {
                JSONObject p=items.getJSONObject(it.next());if(p.optBoolean("deleted") || !p.getString("list_id").equals(id))continue;
                JSONObject site=s.getJSONObject("sites").optJSONObject(p.getString("site_id"));if(site==null)continue;
                sites.add(site);labels.add(site.optString("address",p.getString("site_id"))+" · "+p.getString("status"));
            }
            new AlertDialog.Builder(activity).setTitle(name+(sites.isEmpty()?" · no saved sites":""))
                .setItems(labels.toArray(new String[0]),(d,n)->{JSONObject site=sites.get(n);map.focusSite(site.optString("site_id"));card(site,id);})
                .setNegativeButton("Close",null).show();
        }catch(Exception e){error(e);}
    }
    void parcel(ParcelData.Feature f) {
        try {
            JSONObject site=new JSONObject().put("site_id",f.siteId).put("address",f.address).put("area_sf",f.area)
                .put("neighborhood",f.neighborhood).put("status",f.status);
            if(sync.store!=null) {
                JSONObject cached=state().getJSONObject("sites").optJSONObject(f.siteId);if(cached!=null)site=cached;
            }
            card(site,null);
        }catch(Exception e){error(e);}
    }
    private void card(JSONObject site,String listId) {
        try {
            StringBuilder text=new StringBuilder(site.optString("neighborhood")+"\n"+(int)site.optDouble("area_sf")+" sq ft · "+site.optString("status").replace('_',' '));
            JSONObject details=site.optJSONObject("details");
            if(details!=null) {
                if(details.has("transit_distance_ft"))text.append(String.format(java.util.Locale.US,"\nTransit %.2f mi · straight line",details.optDouble("transit_distance_ft")/5280));
                JSONObject layout=details.optJSONObject("layout");if(layout!=null)text.append("\n").append(layout.optString("reason"));
                JSONObject quality=details.optJSONObject("block_quality");
                if(quality!=null && quality.optBoolean("repeat_violence_review"))text.append("\nField priority: repeated-violence block review");
            }
            if(sync.store!=null) {
                JSONObject s=state(),visits=s.getJSONObject("visits");Iterator<String> it=visits.keys();
                while(it.hasNext()){JSONObject v=visits.getJSONObject(it.next());if(v.getString("site_id").equals(site.getString("site_id")))text.append("\n\n").append(v.getString("note"));}
                JSONArray q=s.getJSONArray("outbox");for(int i=0;i<q.length();i++) {
                    JSONObject m=q.getJSONObject(i),p=m.getJSONObject("payload");
                    if(m.getString("kind").equals("visit") && !visits.has(m.getString("id")) && p.getString("site_id").equals(site.getString("site_id")))
                        text.append("\n\nSaved locally: ").append(p.getString("note"));
                }
            }
            new AlertDialog.Builder(activity).setTitle(site.optString("address",site.optString("site_id"))).setMessage(text)
                .setPositiveButton("Record visit",(d,n)->visit(site))
                .setNeutralButton(listId==null?"Save to list":"List status",(d,n)->{if(listId==null)chooseList(site);else status(site,listId);})
                .setNegativeButton("Close",null).show();
        }catch(Exception e){error(e);}
    }
    private void chooseList(JSONObject site) {
        try {
            JSONObject lists=state().getJSONObject("lists");ArrayList<String> ids=new ArrayList<>(),names=new ArrayList<>();Iterator<String> it=lists.keys();
            while(it.hasNext()){String id=it.next();ids.add(id);names.add(lists.getJSONObject(id).getString("name"));}
            if(ids.isEmpty())throw new Exception("Sync to download the first list");
            new AlertDialog.Builder(activity).setTitle("Save to list").setItems(names.toArray(new String[0]),(d,n)->save(site,ids.get(n),"saved",false)).show();
        }catch(Exception e){error(e);}
    }
    private void status(JSONObject site,String listId) {
        String[] options={"saved","visited","pursue","pass","Remove from this list"};
        new AlertDialog.Builder(activity).setTitle("List status").setItems(options,(d,n)->save(site,listId,n==4?"saved":options[n],n==4)).show();
    }
    private void save(JSONObject site,String list,String status,boolean deleted) {
        try {
            sync.store.enqueue("save",new JSONObject().put("site_id",site.getString("site_id")).put("list_id",list)
                .put("status",status).put("deleted",deleted),site);
            refreshHighlights();Toast.makeText(activity,"Saved on this device",Toast.LENGTH_SHORT).show();sync.sync();
        }catch(Exception e){error(e);}
    }
    private void visit(JSONObject site) {
        if(sync.store==null){connection();return;}
        LinearLayout body=new LinearLayout(activity);body.setOrientation(1);body.setPadding(24,12,24,12);
        Spinner rating=new Spinner(activity);rating.setAdapter(new ArrayAdapter<>(activity,android.R.layout.simple_spinner_dropdown_item,
            new String[]{"Block impression: unrated","1 · Would repel buyer","2 · Significant concerns","3 · Mixed","4 · Good","5 · Strong tour candidate"}));body.addView(rating);
        EditText note=input(body,"Block, transit walk, access, neighboring uses, follow-up…",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE);note.setMinLines(3);
        AlertDialog dialog=new AlertDialog.Builder(activity).setTitle("Visit · "+site.optString("address")).setView(body)
            .setPositiveButton("Save visit",null).setNegativeButton("Cancel",null).create();
        dialog.setOnShowListener(d->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            try {
                String text=note.getText().toString().trim();if(text.isEmpty()){note.setError("Add a note");return;}
                if(text.length()>12000){note.setError("Keep the note under 12,000 characters");return;}
                SimpleDateFormat fmt=new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",java.util.Locale.US);fmt.setTimeZone(TimeZone.getTimeZone("UTC"));
                sync.store.enqueue("visit",new JSONObject().put("site_id",site.getString("site_id")).put("note",text)
                    .put("block_rating",rating.getSelectedItemPosition()==0?JSONObject.NULL:rating.getSelectedItemPosition()).put("observed_at",fmt.format(new Date())),site);
                dialog.dismiss();Toast.makeText(activity,"Visit saved on this device",Toast.LENGTH_SHORT).show();sync.sync();
            }catch(Exception e){error(e);}
        }));dialog.show();
    }
    private void conflicts() {
        try {
            JSONArray q=state().getJSONArray("outbox");
            for(int i=0;i<q.length();i++) {
                JSONObject m=q.getJSONObject(i);
                if(m.has("problem")) {
                    String id=m.getString("id");JSONObject p=m.getJSONObject("payload");
                    new AlertDialog.Builder(activity).setTitle("Change needs review")
                        .setMessage(m.getString("problem")+"\n"+p.optString("note",p.optString("name",p.optString("site_id"))))
                        .setPositiveButton("Retry",(d,n)->resolve(id,true)).setNeutralButton("Discard local change",(d,n)->resolve(id,false))
                        .setNegativeButton("Later",null).show();return;
                }
                if(!m.has("conflict"))continue;
                JSONObject p=m.getJSONObject("payload"),current=m.getJSONObject("conflict").optJSONObject("current");String id=m.getString("id");
                new AlertDialog.Builder(activity).setTitle("Status changed on another device")
                    .setMessage(p.getString("site_id")+"\nThis device: "+p.getString("status")+"\nServer: "+(current==null?"removed":current.optString("status")))
                    .setPositiveButton("Use this device",(d,n)->resolve(id,true)).setNeutralButton("Keep server",(d,n)->resolve(id,false))
                    .setNegativeButton("Later",null).show();return;
            }
            Toast.makeText(activity,"No conflicts",Toast.LENGTH_SHORT).show();
        }catch(Exception e){error(e);}
    }
    private void resolve(String id,boolean local){try{sync.store.resolve(id,local);sync.sync();}catch(Exception e){error(e);}}
}
