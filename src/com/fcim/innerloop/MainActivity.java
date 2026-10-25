package com.fcim.innerloop;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.GeolocationPermissions;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import java.util.Locale;

public class MainActivity extends Activity implements LocationListener {
    private static final int LOCATION_REQUEST = 41;
    private WebView web;
    private LocationManager locations;
    private boolean pageReady;
    private Location pending;
    private long lastDispatch;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setStatusBarColor(0xff000000);

        web = new WebView(this);
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setBuiltInZoomControls(false);
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback cb) {
                cb.invoke(origin, true, false);
            }
        });
        web.setWebViewClient(new WebViewClient() {
            @Override public void onPageFinished(WebView view, String url) {
                pageReady = true;
                if (pending != null) dispatch(pending, true);
            }
        });
        web.loadUrl("file:///android_asset/app/index.html?drive=1&z=17&native=1");
        locations = (LocationManager)getSystemService(LOCATION_SERVICE);
        requestLocationPermission();
    }

    private void requestLocationPermission() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) startGps();
        else requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_REQUEST);
    }

    @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(request, permissions, results);
        if (request == LOCATION_REQUEST && results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) startGps();
        else Toast.makeText(this, "Precise location is required for drive mode", Toast.LENGTH_LONG).show();
    }

    private void startGps() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try {
            locations.requestLocationUpdates(LocationManager.GPS_PROVIDER, 500L, 0f, this);
            Location last = locations.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (last != null) onLocationChanged(last);
        } catch (Exception e) {
            Toast.makeText(this, "GPS unavailable: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override public void onLocationChanged(Location l) {
        if (l == null || (l.hasAccuracy() && l.getAccuracy() > 150f)) return;
        pending = l;
        long now = SystemClock.elapsedRealtime();
        if (pageReady && now - lastDispatch >= 750L) dispatch(l, false);
    }

    private void dispatch(Location l, boolean force) {
        if (!pageReady || l == null) return;
        long now = SystemClock.elapsedRealtime();
        if (!force && now - lastDispatch < 750L) return;
        lastDispatch = now;
        float accuracy = l.hasAccuracy() ? l.getAccuracy() : 20f;
        float speed = l.hasSpeed() ? l.getSpeed() : 0f;
        String heading = l.hasBearing() && speed >= 0.7f ? String.format(Locale.US, "%.2f", l.getBearing()) : "null";
        String js = String.format(Locale.US,
            "window.fcimNativePosition&&window.fcimNativePosition({latitude:%.7f,longitude:%.7f,accuracy:%.1f,speed:%.2f,heading:%s,timestamp:%d})",
            l.getLatitude(), l.getLongitude(), accuracy, speed, heading, l.getTime());
        web.evaluateJavascript(js, null);
    }

    @Override protected void onResume() {
        super.onResume();
        immersive();
        if (locations != null && checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) startGps();
    }

    @Override protected void onPause() {
        if (locations != null) locations.removeUpdates(this);
        super.onPause();
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    @Override public void onProviderEnabled(String provider) {}
    @Override public void onProviderDisabled(String provider) {}
    @Override public void onStatusChanged(String provider, int status, Bundle extras) {}
}
