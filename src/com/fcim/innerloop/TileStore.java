package com.fcim.innerloop;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.LruCache;
import android.view.View;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class TileStore {
    private final Context context;
    private final View view;
    private final ExecutorService loader = Executors.newFixedThreadPool(3);
    private final Set<String> pending = Collections.synchronizedSet(new HashSet<String>());
    private final LruCache<String, Bitmap> cache = new LruCache<String, Bitmap>(32 * 1024 * 1024) {
        @Override protected int sizeOf(String key, Bitmap value) { return value.getByteCount(); }
    };

    TileStore(Context context, View view) {
        this.context = context.getApplicationContext();
        this.view = view;
    }

    Bitmap getSatellite(final int z, final int x, final int y) {
        return get("sat", z, x, y, false);
    }

    Bitmap getMap(final int z, final int x, final int y) {
        return get("map", z, x, y, true);
    }

    private Bitmap get(final String source, final int z, final int x, final int y, final boolean online) {
        final String key = source + "/" + z + "/" + x + "/" + y;
        Bitmap found = cache.get(key);
        if (found != null) return found;
        if (!pending.add(key)) return null;
        loader.execute(new Runnable() {
            @Override public void run() {
                InputStream input = null;
                try {
                    if (online) input = openMapTile(z, x, y);
                    else input = context.getAssets().open("drive/sat/" + z + "/" + x + "/" + y + ".jpg");
                    if (input != null) {
                        BitmapFactory.Options options = new BitmapFactory.Options();
                        options.inPreferredConfig = online ? Bitmap.Config.ARGB_8888 : Bitmap.Config.RGB_565;
                        Bitmap bitmap = BitmapFactory.decodeStream(input, null, options);
                        if (bitmap != null) cache.put(key, bitmap);
                    }
                } catch (IOException ignored) {
                    // Satellite coverage is bounded and the regular map may temporarily be offline.
                } finally {
                    if (input != null) try { input.close(); } catch (IOException ignored) {}
                    pending.remove(key);
                    view.postInvalidateOnAnimation();
                }
            }
        });
        return null;
    }

    private InputStream openMapTile(int z, int x, int y) throws IOException {
        File file = new File(context.getCacheDir(), "esri-streets/" + z + "/" + x + "/" + y + ".png");
        if (file.isFile() && file.length() > 0) return new BufferedInputStream(new FileInputStream(file));
        File parent = file.getParentFile();
        if (parent != null) parent.mkdirs();
        HttpURLConnection connection = (HttpURLConnection)new URL(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/"
                        + z + "/" + y + "/" + x).openConnection();
        connection.setConnectTimeout(7000);
        connection.setReadTimeout(10000);
        connection.setRequestProperty("User-Agent", "FCIM-InnerLoopDrive/0.5");
        connection.connect();
        if (connection.getResponseCode() != HttpURLConnection.HTTP_OK) {
            connection.disconnect();
            throw new IOException("Map tile HTTP " + connection.getResponseCode());
        }
        InputStream network = new BufferedInputStream(connection.getInputStream());
        File temporary = new File(file.getPath() + ".part");
        FileOutputStream output = new FileOutputStream(temporary);
        byte[] buffer = new byte[16384];
        int count;
        try {
            while ((count = network.read(buffer)) >= 0) output.write(buffer, 0, count);
        } finally {
            output.close();
            network.close();
            connection.disconnect();
        }
        if (!temporary.renameTo(file)) {
            temporary.delete();
            throw new IOException("Could not cache map tile");
        }
        return new BufferedInputStream(new FileInputStream(file));
    }

    void close() {
        loader.shutdownNow();
        cache.evictAll();
    }
}
