package com.fcim.innerloop;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import org.json.JSONObject;

/** Refresh tokens remain encrypted with a key held by Android Keystore. */
final class SessionVault {
    private static final String ALIAS="innerloop-session-v1";
    private final Context context;
    SessionVault(Context c){context=c;}
    private SecretKey key() throws Exception {
        KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);
        if(!ks.containsAlias(ALIAS)) {
            KeyGenerator g=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
            g.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());g.generateKey();
        }
        return (SecretKey)ks.getKey(ALIAS,null);
    }
    void write(JSONObject value) throws Exception {
        Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,key());
        String iv=Base64.encodeToString(c.getIV(),Base64.NO_WRAP);
        String body=Base64.encodeToString(c.doFinal(value.toString().getBytes("UTF-8")),Base64.NO_WRAP);
        if(!context.getSharedPreferences(ALIAS,0).edit().putString("iv",iv).putString("body",body).commit())
            throw new Exception("Could not save the sign-in session");
    }
    JSONObject read() throws Exception {
        android.content.SharedPreferences p=context.getSharedPreferences(ALIAS,0);String body=p.getString("body",null);
        if(body==null)return null;
        Cipher c=Cipher.getInstance("AES/GCM/NoPadding");
        c.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Base64.decode(p.getString("iv",""),Base64.NO_WRAP)));
        return new JSONObject(new String(c.doFinal(Base64.decode(body,Base64.NO_WRAP)),"UTF-8"));
    }
}
