# Architecture

## Runtime

```text
Inner Loop Drive Activity
  ├─ Android LocationManager.GPS_PROVIDER
  │    └─ WebView evaluateJavascript(fcimNativePosition(...))
  └─ Chromium WebView
       ├─ Leaflet 1.9.4
       ├─ Leaflet.Rotate 0.3.0
       ├─ offline PMTiles basemap embedded by basemap.js
       ├─ generated candidate/site data in data.js
       ├─ generated context parcels in parcels.js
       └─ offline XYZ satellite JPEG tiles under sat/
```

The APK loads `file:///android_asset/app/index.html?drive=1&z=17&native=1`. The `native=1` flag prevents the page from registering browser geolocation and device-orientation listeners.

## Native GPS bridge

`MainActivity` requests precise location permission and subscribes directly to `GPS_PROVIDER`. This matters on the Joying unit because Firefox's geolocation used the fused provider, timed out, and delivered updates inconsistently even though the OEM GPS services were receiving fixes.

Locations are dispatched to JavaScript no more often than every 750 ms. The payload includes latitude, longitude, accuracy, speed, GPS bearing when moving, and timestamp. Android currently supplies physical GNSS fixes at approximately 1 Hz even though the requested interval is 500 ms.

## Camera and orientation

The JavaScript camera:

- ignores small offsets attributable to stationary GPS wander;
- limits follow-camera work to approximately 1 Hz;
- animates ordinary movement and snaps only large jumps;
- uses raw native GPS course rather than slow averaging;
- animates between course updates;
- sets Leaflet.Rotate bearing to the negative GPS course for heading-up display.

Leaflet.Rotate's positive bearing rotates map content clockwise. Therefore, holding a geographic heading at screen-up requires:

```text
map bearing = -GPS course (normalized to 0–360)
```

The compass dial rotates by the current map bearing. In north-up mode its N marker remains at the top. In POV mode it shows where north lies relative to the vehicle-forward direction.

## Rendering controls

The primary 10,000+ sq-ft candidate polygons remain visible in drive mode. The much larger Third/Second Ward context parcel layer is retained but only drawn at zoom 18 or greater while driving. This avoids rebuilding hundreds of extra Leaflet polygons during routine zoom-17 following.

## Asset strategy

The generated map directory remains the authoritative data package. `build.sh` copies it into APK assets, then overlays the version-controlled `web/index.html` and rotation library. This keeps sensitive and large generated datasets out of Git while preserving reproducible application logic.

A future fully native MapLibre renderer could further improve graphics performance, but would require converting the generated JavaScript datasets and offline PMTiles/satellite integration. The current hybrid keeps every existing filter and detail screen while solving the GPS-provider problem natively.
