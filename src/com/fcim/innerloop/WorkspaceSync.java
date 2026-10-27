package com.fcim.innerloop;

import android.content.Context;
import android.util.Base64;
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

/** Sync while the app is open; SQLite keeps the outbox through network/process loss. */
final class WorkspaceSync {
    private static class HttpFailure extends Exception {
        final int code;
        HttpFailure(int code,String message){super(message);this.code=code;}
    }
    interface Listener { void changed(String status); }
    private final Context context;private final SessionVault vault;private final Listener listener;
    private final ScheduledExecutorService worker=Executors.newSingleThreadScheduledExecutor();
    private JSONObject connection;
    volatile WorkspaceStore store;
    volatile String status="Connect workspace";
    private volatile boolean active=true;
    private volatile boolean closed;
    WorkspaceSync(Context c,Listener l) {
        context=c;vault=new SessionVault(c);listener=l;
        worker.execute(()->{
            try {connection=vault.read();if(connection!=null)openStore();}
            catch(Exception e){report("Sign-in needed: "+e.getMessage());}
            syncNow();
        });
        worker.scheduleWithFixedDelay(()->{if(active)syncNow();},30,30,TimeUnit.SECONDS);
    }
    void active(boolean value){active=value;if(value)sync();}
    void sync(){worker.execute(this::syncNow);}
    private void report(String value){status=value;if(!closed)listener.changed(value);}
    private void openStore() throws Exception {
        if(store!=null)store.close();
        store=new WorkspaceStore(context,connection.getString("url")+":"+
            connection.getJSONObject("session").getJSONObject("user").getString("id")+":"+connection.getString("workspace"));
    }
    void signIn(final String url,final String key,final String email,final String password) {
        worker.execute(()->{
            JSONObject previous=connection;
            try {
                URL parsed=new URL(url);
                if(!parsed.getProtocol().equals("https") || parsed.getUserInfo()!=null || parsed.getQuery()!=null || parsed.getRef()!=null ||
                   !(parsed.getPath().isEmpty() || parsed.getPath().equals("/")))throw new Exception("Use the HTTPS project origin");
                if(key.startsWith("sb_secret_"))throw new Exception("Use a publishable key");
                String[] jwt=key.split("\\.");
                if(jwt.length==3 && new JSONObject(new String(Base64.decode(jwt[1],Base64.URL_SAFE),"UTF-8")).optString("role").equals("service_role"))
                    throw new Exception("Service-role keys cannot be used on the device");
                connection=new JSONObject().put("url",url.replaceAll("/$","")).put("key",key);
                JSONObject session=(JSONObject)request("/auth/v1/token?grant_type=password",new JSONObject().put("email",email).put("password",password),false,false);
                connection.put("session",session);
                JSONObject w=(JSONObject)request("/rest/v1/rpc/open_workspace",new JSONObject(),true,true);
                connection.put("workspace",w.getString("id"));vault.write(connection);openStore();report("Connected");syncNow();
            } catch(Exception e){connection=previous;report("Sign-in failed: "+e.getMessage());}
        });
    }
    private Object request(String path,JSONObject payload,boolean auth,boolean retry) throws Exception {
        HttpURLConnection http=(HttpURLConnection)new URL(connection.getString("url")+path).openConnection();
        http.setConnectTimeout(15000);http.setReadTimeout(30000);http.setRequestMethod("POST");http.setDoOutput(true);
        http.setRequestProperty("Content-Type","application/json");http.setRequestProperty("apikey",connection.getString("key"));
        if(auth)http.setRequestProperty("Authorization","Bearer "+connection.getJSONObject("session").getString("access_token"));
        try {
            try(java.io.OutputStream out=http.getOutputStream()){out.write(payload.toString().getBytes("UTF-8"));}
            int code=http.getResponseCode();
            if(code==401 && auth && retry) {
                JSONObject session=(JSONObject)request("/auth/v1/token?grant_type=refresh_token",new JSONObject()
                    .put("refresh_token",connection.getJSONObject("session").getString("refresh_token")),false,false);
                connection.put("session",session);vault.write(connection);return request(path,payload,auth,false);
            }
            ByteArrayOutputStream bytes=new ByteArrayOutputStream();
            InputStream stream=code>=400?http.getErrorStream():http.getInputStream();
            if(stream==null)throw new Exception("Server returned HTTP "+code);
            try(InputStream in=stream){byte[] buf=new byte[8192];int n;while((n=in.read(buf))!=-1)bytes.write(buf,0,n);}
            String raw=new String(bytes.toByteArray(),"UTF-8");
            if(code>=400) {
                JSONObject error=new JSONObject(raw);
                throw new HttpFailure(code,error.optString("message",error.optString("error_description","HTTP "+code)));
            }
            return new JSONTokener(raw).nextValue();
        } finally {http.disconnect();}
    }
    private Object rpc(String name,JSONObject args) throws Exception {
        args.put("w",connection.getString("workspace"));return request("/rest/v1/rpc/"+name,args,true,true);
    }
    private void pull() throws Exception {
        for(;;) {
            JSONArray events=(JSONArray)rpc("pull_changes",new JSONObject().put("after_revision",store.read().getLong("cursor")));
            if(events.length()==0)return;store.pull(events);if(events.length()<250)return;
        }
    }
    private void syncNow() {
        if(connection==null || store==null)return;
        try {
            pull();JSONArray queue=store.read().getJSONArray("outbox");
            for(int i=0;i<queue.length();i++) {
                JSONObject m=queue.getJSONObject(i);if(m.has("conflict") || m.has("problem"))continue;
                try {
                    JSONObject result=(JSONObject)rpc("mutate",new JSONObject().put("mutation",m));
                    store.acknowledge(m.getString("id"),result);
                }catch(HttpFailure e) {
                    if(e.code!=400 && e.code!=404 && e.code!=409 && e.code!=422)throw e;
                    store.acknowledge(m.getString("id"),new JSONObject().put("problem",e.getMessage()));
                }
            }
            pull();int n=store.read().getJSONArray("outbox").length();report(n==0?"Synced":n+" changes need review");
        } catch(Exception e) {report("Saved locally · "+e.getMessage());}
    }
    void close(){active=false;closed=true;worker.execute(()->{if(store!=null)store.close();});worker.shutdown();}
}
