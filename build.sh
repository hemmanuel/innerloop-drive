#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
P="$(cd "$(dirname "$0")" && pwd)"
ANDROID_JAR="$P/sdk/platforms/android-33/android.jar"
APP_SOURCE="/sdcard/Download/innerloop/innerloop"
rm -rf "$P/assets/app" "$P/build"
mkdir -p "$P/assets" "$P/build/classes" "$P/build/dex"
cp -a "$APP_SOURCE" "$P/assets/app"
rm -f "$P/assets/app/index.html.before-pov"
# Apply the version-controlled drive UI over the generated/private data package.
cp "$P/web/index.html" "$P/assets/app/index.html"
cp "$P/web/lib/leaflet-rotate-src.js" "$P/assets/app/lib/leaflet-rotate-src.js"
javac -source 8 -target 8 -Xlint:-options -bootclasspath "$ANDROID_JAR" -d "$P/build/classes" $(find "$P/src" -name '*.java')
d8 --lib "$ANDROID_JAR" --output "$P/build/dex" $(find "$P/build/classes" -name '*.class')
aapt2 compile --dir "$P/res" -o "$P/build/resources.zip"
aapt2 link -o "$P/build/innerloop-unsigned.apk" -I "$ANDROID_JAR" --manifest "$P/AndroidManifest.xml" -A "$P/assets" --min-sdk-version 23 --target-sdk-version 33 -0 jpg -0 js -0 css "$P/build/resources.zip"
(cd "$P/build/dex" && zip -q -0 "$P/build/innerloop-unsigned.apk" classes.dex)
if [[ ! -f "$P/innerloop-key.pk8" ]]; then
  openssl req -x509 -newkey rsa:2048 -keyout "$P/innerloop-key.pem" -out "$P/innerloop-cert.pem" -days 3650 -nodes -subj '/CN=Inner Loop Drive/O=FCIM/'
  openssl pkcs8 -topk8 -nocrypt -in "$P/innerloop-key.pem" -outform DER -out "$P/innerloop-key.pk8"
fi
apksigner sign --key "$P/innerloop-key.pk8" --cert "$P/innerloop-cert.pem" --out "$P/build/innerloop-drive.apk" "$P/build/innerloop-unsigned.apk"
apksigner verify "$P/build/innerloop-drive.apk"
echo "$P/build/innerloop-drive.apk"
