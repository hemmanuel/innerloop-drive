package com.fcim.innerloop;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.HandlerThread;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Toast;

public class MainActivity extends Activity implements LocationListener {
    private static final int LOCATION_REQUEST = 41;
    private ParcelMapView map;
    private LocationManager locations;
    private HandlerThread gpsThread;
    private boolean listening;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setStatusBarColor(0xff000000);
        map = new ParcelMapView(this);
        setContentView(map);
        locations = (LocationManager)getSystemService(LOCATION_SERVICE);
        gpsThread = new HandlerThread("innerloop-gnss");
        gpsThread.start();
        requestLocationPermission();
    }

    private void requestLocationPermission() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) startGps();
        else requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_REQUEST);
    }

    @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(request, permissions, results);
        if (request == LOCATION_REQUEST && results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) startGps();
        else Toast.makeText(this, "Precise location is required for drive mode", Toast.LENGTH_LONG).show();
    }

    private void startGps() {
        if (listening || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try {
            // Location delivery stays off the render/UI thread. The receiver decides the
            // physical fix rate; the map's motion model supplies continuous frames between fixes.
            locations.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0L, 0f,
                    this, gpsThread.getLooper());
            listening = true;
            Location last = locations.getLastKnownLocation(LocationManager.GPS_PROVIDER);
            if (last != null) onLocationChanged(last);
        } catch (Exception error) {
            Toast.makeText(this, "GPS unavailable: " + error.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override public void onLocationChanged(final Location location) {
        if (location == null || (location.hasAccuracy() && location.getAccuracy() > 150f)) return;
        final Location copy = new Location(location);
        map.post(new Runnable() {
            @Override public void run() { map.setLocation(copy); }
        });
    }

    @Override protected void onResume() {
        super.onResume();
        immersive();
        startGps();
    }

    @Override protected void onPause() {
        if (locations != null && listening) {
            locations.removeUpdates(this);
            listening = false;
        }
        super.onPause();
    }

    @Override protected void onDestroy() {
        map.close();
        if (gpsThread != null) gpsThread.quitSafely();
        super.onDestroy();
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override public void onProviderEnabled(String provider) {}
    @Override public void onProviderDisabled(String provider) {}
    @Override public void onStatusChanged(String provider, int status, Bundle extras) {}
}
