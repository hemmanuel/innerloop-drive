# Map and data assets

The APK build imports generated assets from:

```text
/sdcard/Download/innerloop/innerloop
```

Expected files:

| Path | Purpose |
|---|---|
| `data.js` | Candidate sites, attributes, centroids, and geometries |
| `parcels.js` | Third/Second Ward context parcels |
| `picks.js` | Selected/picked lots |
| `basemap.js` | Base64-embedded PMTiles vector basemap |
| `sat/satpack.js` | Offline satellite metadata |
| `sat/{z}/{x}/{y}.jpg` | Offline satellite XYZ tiles |
| `lib/leaflet.js` / `.css` | Leaflet runtime |
| `lib/pmtiles.js` | PMTiles reader |
| `lib/protomaps-leaflet.js` | Vector-map renderer |

`build.sh` copies this directory and then replaces `index.html` and `lib/leaflet-rotate-src.js` with repository-controlled versions.

These datasets are intentionally not committed because they are large and `data.js` contains public-record owner names. Keep the source directory available when rebuilding the APK.

Map attribution remains visible in the application:

- OpenStreetMap contributors / Protomaps for the vector basemap.
- USGS The National Map / USDA NAIP for the offline satellite pack.
