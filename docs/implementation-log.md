# Implementation log

## 2026-10-25 — Basemap and map interaction

Version 0.5 adds the controls needed outside strict vehicle following:

1. Added a Satellite/Map toggle. Satellite remains fully offline; the regular
   Esri street basemap downloads asynchronously and is cached after first use.
2. Added drag-to-pan with correct inverse transforms in both north-up and POV.
3. Added focal-point pinch zoom from zoom 15 through 19.5.
4. Panning or pinching suspends tracking, and a visible Follow control restores it.
5. Retained +/- controls for operation on a resistive or difficult touchscreen.

Pan and basemap tile retrieval were smoke-tested on the Joying unit. Multi-touch
pinch behavior still needs direct physical-screen validation.

## 2026-10-25 — Native renderer redesign

Road use showed that the WebView version remained extremely jittery, could lose
the vehicle for tens of seconds, snapped after stalls, and rotated poorly.
Throttle changes could not fix the underlying combination of approximately 1 Hz
GPS, independent Leaflet animations, JavaScript/UI-thread delivery, and polygon
reconstruction.

Version 0.4 therefore replaces the Drive runtime rather than tuning it:

1. Removed WebView and JavaScript from the packaged runtime.
2. Moved `GPS_PROVIDER` callbacks to a dedicated `HandlerThread`.
3. Added a continuous motion estimator with two-second maximum prediction,
   eased fix correction, smoothly interpolated course, and visible stale state.
4. Added a native hardware-accelerated renderer with one synchronized transform
   for camera, vehicle, imagery, and parcel geometry.
5. Compiled every context and candidate parcel—41,669 total—into a compact
   4.1 MiB binary. Only the padded viewport is drawn.
6. Reused the full offline satellite pack through asynchronous tile loading and
   a 24 MiB bitmap cache.
7. Installed and smoke-tested the signed upgrade on the Joying unit. Parcel
   geometry aligns with imagery and the process uses roughly 84 MiB PSS after load.

A moving road test remains required before declaring motion tuning final.

## 2026-10-25 — Browser investigation

1. Found that the extracted application was nested at:
   `/sdcard/Download/innerloop/innerloop/`.
2. Served it from Termux on `127.0.0.1:8765` because the original `file://sdcard/...` URL was malformed and pointed one directory too high.
3. Confirmed Firefox had Android fine/coarse location permission, but Firefox 100 used Android's fused provider and frequently reported `Position acquisition timed out`.
4. Verified the OEM GPS provider itself was healthy and continuously supplied the Joying car services.
5. Added an initial Leaflet heading cone and north-up/POV control using Leaflet.Rotate 0.3.0.
6. Tested newer Chrome/WebView. Rendering and camera behavior remained too jittery for driving.

## 2026-10-25 — First APK

1. Created package `com.fcim.innerloop` with a landscape, hardware-accelerated WebView activity.
2. Bundled the complete generated map application, including approximately:
   - 14 MB candidate data;
   - 5 MB context parcels;
   - 21 MB embedded offline vector basemap;
   - 76 MB / roughly 2,099 offline satellite tiles.
3. Added direct `LocationManager.GPS_PROVIDER` handling and injected fixes through `window.fcimNativePosition`.
4. Disabled browser geolocation and orientation events in native mode.
5. Added screen wake lock, immersive mode, runtime location permission handling, and an internal geolocation permission fallback.
6. Limited location dispatch and camera work, rejected very inaccurate fixes, and suppressed stationary GPS wander.
7. Reduced drive-mode load by showing the 20,000-feature context parcel layer only at zoom 18+.
8. Built, signed, installed, and verified direct high-power GPS ownership in `dumpsys location`.

## 2026-10-25 — POV correction and compass

Road testing showed that POV rotation was reversed/skewed and directional changes lagged.

Changes:

1. Corrected heading-up rotation from `map.setBearing(course)` to normalized `-course`.
2. Removed slow native-GPS heading averaging.
3. Reduced heading-change thresholds and animated between approximately 1 Hz hardware fixes.
4. Added a persistent lower-right compass with N/E/S/W dial and a fixed vehicle-forward marker.
5. Verified north-up rendering and compass display after reinstalling the updated APK.

## 2026-10-25 — Project/repository and launcher

1. Formalized `~/innerloop-android` as a standalone source project.
2. Added README, architecture documentation, this implementation log, and data/privacy exclusions.
3. Version-controlled the modified web UI independently of generated/private data.
4. Added a custom map/compass launcher icon.
5. Confirmed the launcher activity resolves as `com.fcim.innerloop/.MainActivity` with label **Inner Loop Drive**.

## Current release

```text
Version: 0.5.0-native (versionCode 5)
APK: `build/innerloop-drive.apk` (native field-test build)
Package: com.fcim.innerloop
```

## Remaining field validation

- Road-test fix continuity, turning, stop/start behavior, and POV alignment.
- Tune correction time constant and look-ahead distance from field results.
- Check sleep/wake behavior after a full ignition cycle.
- Decide whether POV/north-up and zoom preferences should persist.
- Add an online/vector street-map option only if satellite plus parcel outlines is insufficient.
