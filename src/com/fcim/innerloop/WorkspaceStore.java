package com.fcim.innerloop;

import android.content.Context;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.util.Iterator;
import java.util.UUID;
import org.json.JSONArray;
import org.json.JSONObject;

/** Durable acquisition state, separated by project, account and workspace. */
final class WorkspaceStore extends SQLiteOpenHelper {
    interface Edit { void apply(JSONObject state) throws Exception; }
    WorkspaceStore(Context context,String scope) throws Exception {
        super(context,"workspace-"+UUID.nameUUIDFromBytes(scope.getBytes("UTF-8"))+".db",null,2);
        setWriteAheadLoggingEnabled(true);
    }
    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE entries (bucket TEXT NOT NULL, item_key TEXT NOT NULL, ordinal INTEGER NOT NULL, body TEXT NOT NULL, PRIMARY KEY(bucket,item_key))");
    }
    @Override public void onUpgrade(SQLiteDatabase db,int old,int next) {
        if(old!=1 || next!=2)throw new IllegalStateException("Unsupported workspace migration");
        try {
            JSONObject legacy;
            try(Cursor c=db.rawQuery("SELECT body FROM state WHERE id=1",null)) {
                legacy=c.moveToFirst()?new JSONObject(c.getString(0)):empty();
            }
            onCreate(db);write(db,empty(),legacy);db.execSQL("DROP TABLE state");
        } catch(Exception e){throw new IllegalStateException("Workspace migration failed",e);}
    }
    private JSONObject empty() throws Exception {
        return new JSONObject("{\"cursor\":0,\"lists\":{},\"items\":{},\"visits\":{},\"sites\":{},\"outbox\":[]}");
    }
    private JSONObject read(SQLiteDatabase db) throws Exception {
        JSONObject state=empty();
        // One record per row avoids Android CursorWindow's single-row size limit
        // as saved geometries and visit notes accumulate.
        try(Cursor c=db.rawQuery("SELECT bucket,item_key,body FROM entries ORDER BY bucket,ordinal,item_key",null)) {
            while(c.moveToNext()) {
                String bucket=c.getString(0),key=c.getString(1),body=c.getString(2);
                if(bucket.equals("meta"))state.put(key,Long.parseLong(body));
                else if(bucket.equals("outbox"))state.getJSONArray(bucket).put(new JSONObject(body));
                else state.getJSONObject(bucket).put(key,new JSONObject(body));
            }
        }
        return state;
    }
    private void put(SQLiteDatabase db,String bucket,String key,int ordinal,String body) {
        ContentValues values=new ContentValues();values.put("bucket",bucket);values.put("item_key",key);
        values.put("ordinal",ordinal);values.put("body",body);
        if(db.insertWithOnConflict("entries",null,values,SQLiteDatabase.CONFLICT_REPLACE)<0)
            throw new IllegalStateException("Unable to save workspace record");
    }
    private void write(SQLiteDatabase db,JSONObject before,JSONObject state) throws Exception {
        put(db,"meta","cursor",0,Long.toString(state.getLong("cursor")));
        for(String bucket:new String[]{"lists","items","visits","sites"}) {
            JSONObject previous=before.getJSONObject(bucket),records=state.getJSONObject(bucket);
            Iterator<String> oldKeys=previous.keys();
            while(oldKeys.hasNext()) {
                String key=oldKeys.next();
                if(!records.has(key))db.delete("entries","bucket=? AND item_key=?",new String[]{bucket,key});
            }
            Iterator<String> keys=records.keys();
            while(keys.hasNext()) {
                String key=keys.next(),body=records.getJSONObject(key).toString();
                if(!previous.has(key) || !body.equals(previous.getJSONObject(key).toString()))put(db,bucket,key,0,body);
            }
        }
        db.delete("entries","bucket=?",new String[]{"outbox"});
        JSONArray queue=state.getJSONArray("outbox");
        for(int i=0;i<queue.length();i++) {
            JSONObject record=queue.getJSONObject(i);put(db,"outbox",record.getString("id"),i,record.toString());
        }
    }
    synchronized JSONObject read() throws Exception { return read(getReadableDatabase()); }
    synchronized void change(Edit edit) throws Exception {
        SQLiteDatabase db=getWritableDatabase();db.beginTransaction();
        try {
            JSONObject before=read(db),s=new JSONObject(before.toString());edit.apply(s);
            write(db,before,s);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }
    static String itemKey(JSONObject p) throws Exception {return p.getString("list_id")+":"+p.getString("site_id");}
    String enqueue(final String kind, final JSONObject payload, final JSONObject site) throws Exception {
        if(kind.equals("list") && (payload.optString("name").trim().isEmpty() || payload.optString("name").length()>120))
            throw new Exception("List names must contain 1–120 characters");
        if(kind.equals("visit") && (payload.optString("note").trim().isEmpty() || payload.optString("note").length()>12000))
            throw new Exception("Enter a visit note of 1–12,000 characters");
        final String id=UUID.randomUUID().toString();
        change(s->{
            JSONArray q=s.getJSONArray("outbox");
            if(kind.equals("save")) {
                for(int i=0;i<q.length();i++)if(q.getJSONObject(i).getString("kind").equals("save") &&
                    itemKey(q.getJSONObject(i).getJSONObject("payload")).equals(itemKey(payload)))
                    throw new Exception("Sync the pending change to this site before changing it again.");
                JSONObject old=s.getJSONObject("items").optJSONObject(itemKey(payload));
                payload.put("expected_revision",old==null?0:old.getLong("revision"));
            }
            if(site!=null)s.getJSONObject("sites").put(site.getString("site_id"),site);
            q.put(new JSONObject().put("id",id).put("kind",kind).put("payload",payload));
        });
        return id;
    }
    void pull(final JSONArray events) throws Exception {
        change(s->{
            for(int i=0;i<events.length();i++) {
                JSONObject e=events.getJSONObject(i);long revision=e.getLong("revision");
                if(revision<=s.getLong("cursor"))continue;
                JSONObject p=e.getJSONObject("payload");String kind=e.getString("kind");
                JSONObject record=new JSONObject(p.toString());record.remove("site");
                if(kind.equals("list"))s.getJSONObject("lists").put(p.getString("id"),p);
                if(kind.equals("save"))s.getJSONObject("items").put(itemKey(p),record);
                if(kind.equals("visit"))s.getJSONObject("visits").put(p.getString("id"),record);
                if(p.optJSONObject("site")!=null)s.getJSONObject("sites").put(p.getString("site_id"),p.getJSONObject("site"));
                s.put("cursor",revision);
            }
        });
    }
    void acknowledge(final String id,final JSONObject response) throws Exception {
        change(s->{
            JSONArray next=new JSONArray(),old=s.getJSONArray("outbox");
            for(int i=0;i<old.length();i++) {
                JSONObject m=old.getJSONObject(i);
                if(!m.getString("id").equals(id))next.put(m);
                else if(response.optBoolean("conflict")){m.put("conflict",response);next.put(m);}
                else if(response.has("problem")){m.put("problem",response.getString("problem"));next.put(m);}
            }
            s.put("outbox",next);
        });
    }
    void resolve(final String id,final boolean local) throws Exception {
        change(s->{
            JSONArray next=new JSONArray(),q=s.getJSONArray("outbox");
            for(int i=0;i<q.length();i++) {
                JSONObject m=q.getJSONObject(i);
                if(m.getString("id").equals(id)) {
                    if(!local)continue;
                    if(m.has("conflict")) {
                        JSONObject current=m.getJSONObject("conflict").optJSONObject("current");
                        m.getJSONObject("payload").put("expected_revision",current==null?0:current.getLong("revision"));
                    }
                    m.remove("conflict");
                    m.remove("problem");
                }
                next.put(m);
            }
            s.put("outbox",next);
        });
    }
}
