# Implementation log

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
Version: 0.3.0 (versionCode 3)
APK: /sdcard/Download/innerloop-drive.apk
Package: com.fcim.innerloop
```

## Remaining field validation

- Confirm heading-up stays aligned through several real turns.
- Evaluate interpolation at low speed and stop/start transitions.
- Check sleep/wake behavior after a full ignition cycle.
- Decide whether POV/north-up preference should persist across launches.
- Consider a native MapLibre renderer only if WebView polygon rendering remains inadequate after GPS/camera fixes.
