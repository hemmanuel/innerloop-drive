# Architecture

## Shared acquisition layer (0.6)

Supabase stores stable parcel/site membership, versioned screening runs and a
separate human activity log. Both the desktop and native app use the same
transactional mutation/change-feed API. Lists and visits survive screening updates.
The desktop uses IndexedDB and a service worker; Joying uses SQLite and an
Android-Keystore-encrypted session. See [cross-device-workflow.md](cross-device-workflow.md).

The native binary is now `ILP3`: address, canonical site ID, all constituent HCAD
accounts, neighborhood and screening status accompany the original geometry and
render fields. `tools/build_native_data.py` accepts either the old generated JS
directory or the same `sites.jsonl.gz` snapshot uploaded to Supabase.

Parcel taps use the current map transform and actual polygon paths. The workspace
opens saved lists, records visits, changes status and resolves synchronization
conflicts. Saved highlights are read from local state, not queried while drawing.
The counts below describe the original 0.5 bundle.

## Native Drive runtime (0.4+)

```text
Android LocationManager.GPS_PROVIDER
  └─ dedicated innerloop-gnss HandlerThread
       └─ immutable Location posted to UI
            └─ motion estimator
                 ├─ bounded position prediction between physical fixes
                 ├─ eased correction when a new fix arrives
                 ├─ circular course interpolation
                 └─ explicit stale-fix state
                      ↓
             hardware-accelerated native Canvas
                 ├─ offline satellite tile cache
                 ├─ viewport-culled parcel paths
                 ├─ labels
                 └─ synchronized camera, parcels, and vehicle
```

There is no WebView or JavaScript in the Drive runtime. GPS collection cannot be
blocked by parcel drawing because callbacks use a dedicated `HandlerThread`.

The receiver currently supplies physical GNSS fixes at approximately 1 Hz. The
renderer runs between those fixes, predicts no more than two seconds ahead, and
eases each correction rather than starting independent marker, pan, and rotation
animations. Prediction stops when fixes are stale.

## Parcel storage and rendering

`tools/build_native_data.py` converts both generated datasets into
`assets/drive/parcels.bin` during the build:

- all 19,947 context parcels;
- all 21,722 candidate parcels;
- priority, pick, area-label, and abbreviated address fields;
- polygon rings encoded as local Web Mercator floats.

All 41,669 parcels remain available offline. Runtime rendering culls by bounding
box to a padded viewport; it does not instantiate or redraw off-screen parcels.
Android `Path` objects are created once when the binary loads and reused.

The camera and every map layer share one transform per frame. In POV mode the
vehicle is anchored below center and position/course move together. North-up is
available from the on-screen toggle.

Drag gestures invert the current rotated map transform to pan in geographic
space. Pinch zoom preserves the geographic point beneath the gesture focus.
Either gesture suspends vehicle following; the Follow control restores the live
camera.

## Basemap

The native app packages the existing 2,098 USGS/USDA satellite JPEG tiles.
The Satellite/Map control switches to Esri World Street Map raster tiles for a
regular basemap. Street tiles are cached in application storage after first use;
the initial view therefore requires connectivity.

A three-worker background loader and 32 MiB bitmap LRU prevent asset, network,
or disk decoding on the UI thread. Zoom levels above the satellite pack's native
zoom 16 enlarge those tiles while parcel paths remain vector-sharp.

## Legacy implementation

`web/` retains the former Leaflet/Leaflet.Rotate implementation as source and
fallback reference. It is no longer packaged by `build.sh`. Its old pipeline
combined UI-thread JavaScript injection, marker jumps, independent pan/rotation
animations, and periodic polygon reconstruction; that architecture caused the
field-observed stalls and jitter.
