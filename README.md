# Inner Loop Drive

Native Android drive-mode parcel map for the Joying head unit.

## Current design

Version 0.5 replaces the Leaflet WebView runtime with a hardware-accelerated
native renderer designed around continuous vehicle motion:

- GPS callbacks run on a dedicated thread.
- A bounded motion estimator fills the intervals between approximately 1 Hz GNSS fixes.
- Position corrections and turns are eased in one synchronized frame loop.
- Stale fixes are shown explicitly and are never extrapolated for more than two seconds.
- All 41,669 context and candidate parcels remain available offline.
- Only parcels intersecting the current viewport are drawn.
- Existing offline satellite imagery is decoded asynchronously and cached.
- A regular Esri street-map basemap is available and cached after first use.
- Drag-to-pan and focal-point pinch zoom are supported.
- Panning or pinching suspends tracking; **Follow** returns to the vehicle.
- POV and north-up modes plus native zoom controls remain available.

The former browser research interface is retained under `web/`, but it is not
part of the native Drive APK.

## Installed application

```text
Package:  com.fcim.innerloop
Activity: com.fcim.innerloop/.MainActivity
Label:    Inner Loop Drive
```

The native test build uses the same signing identity and upgrades the existing
application in place.

## Repository layout

```text
AndroidManifest.xml                     package, permissions, activity
src/com/fcim/innerloop/MainActivity.java GPS lifecycle and dedicated GNSS thread
src/com/fcim/innerloop/ParcelMapView.java motion model and native renderer
src/com/fcim/innerloop/ParcelData.java   compact parcel loader
src/com/fcim/innerloop/TileStore.java    asynchronous satellite tile LRU
tools/build_native_data.py               generated JS → native parcel binary
docs/sync-navigation-plan.md             planned PC/Joying sync and routing
docs/ai-acquisitions-plan.md             planned AI-assisted acquisitions ecosystem
web/                                     legacy WebView implementation
build.sh                                 reproducible APK build
```

Generated/private parcel data, imagery, keys, and build products are excluded
from Git.

## Build and install

The build imports generated source assets from:

```text
/sdcard/Download/innerloop/innerloop
```

Build and install:

```sh
cd ~/innerloop-android
./build.sh
adb install -r build/innerloop-drive.apk
```

The resulting APK is approximately 68 MiB, mostly offline satellite imagery.
Do not replace the signing key after distribution; Android requires subsequent
updates to use the same key.

## Field validation

The native renderer has been installed and smoke-tested on the Joying unit. It
loads all 41,669 parcels with aligned satellite imagery. A road test is still
required to tune prediction/correction timing and POV look-ahead distance against
the unit's real GNSS behavior.

## Data privacy

The generated source data includes public-record owner names. It and generated
map assets are intentionally excluded from this repository.
