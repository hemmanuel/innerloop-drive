# Inner Loop Drive

Android drive-mode map for the Joying head unit. It packages the existing Inner Loop parcel application in a hardware-accelerated WebView while obtaining position and course directly from Android's GPS provider.

## Why an APK

Firefox 100 and Chrome browser tests had unstable browser geolocation, excessive camera jitter, and expensive redraws. The APK preserves the existing parcel UI and offline map assets but bypasses browser geolocation and removes the Termux HTTP-server dependency.

## Current behavior

- Direct `LocationManager.GPS_PROVIDER` updates.
- Follow camera with stationary-drift rejection and throttled animated movement.
- North-up / heading-up (`POV`) toggle.
- In POV mode, direction of travel is held at the top of the screen.
- Rotating compass dial shows north relative to the display.
- GPS course drives orientation; noisy browser orientation events are disabled in APK mode.
- All candidate lots, detailed parcel data, offline Protomaps basemap, and optional satellite tiles remain available.
- The 20,000-feature context-parcel layer is delayed until zoom 18 in drive mode to reduce rendering load.
- Screen stays awake and the activity uses immersive landscape mode.

## Installed application

Package and activity:

```text
com.fcim.innerloop/.MainActivity
```

Launcher label: **Inner Loop Drive**. The manifest contains a standard launcher intent and a custom map/compass icon, so it appears in the Joying apps menu.

Current distributable:

```text
/sdcard/Download/innerloop-drive.apk
```

## Repository layout

```text
AndroidManifest.xml             Android package, permissions, launcher entry
src/.../MainActivity.java      WebView lifecycle and native GPS bridge
web/index.html                 Version-controlled map UI/drive modifications
web/lib/leaflet-rotate-src.js  Offline Leaflet rotation support
res/drawable/ic_launcher.xml   Launcher icon
build.sh                       Reproducible local APK build
 docs/                          Architecture, assets, and implementation history
```

Generated/private data and build products are intentionally ignored by Git.

## Build

Prerequisites in Termux:

```sh
pkg install aapt2 apksigner d8 gradle zip openssl-tool
```

The build expects:

- Android API 33 compile jar at `sdk/platforms/android-33/android.jar`.
- Generated map package at `/sdcard/Download/innerloop/innerloop`.
- Existing local signing key, or it creates one on the first build.

Build and install:

```sh
cd ~/innerloop-android
./build.sh
adb install -r build/innerloop-drive.apk
```

Copy the release APK:

```sh
cp build/innerloop-drive.apk /sdcard/Download/innerloop-drive.apk
```

Do not delete or replace the signing key after distributing the application; Android requires future updates to use the same key.

## Data privacy

`data.js` contains public-record owner names. It and the generated parcel/basemap packages are excluded from this repository. Do not publish them unintentionally.
