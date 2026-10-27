# Inner Loop Drive

Native Android drive-mode parcel map for the Joying head unit.

Version 0.6 adds Supabase migrations, a desktop acquisitions workspace, stable
parcel/assembly IDs, native saved lists and offline visit sync. See
[cross-device setup and validation](docs/cross-device-workflow.md).
The completed full-Loop snapshot covers 181,840 accounts and 4,603 assemblies;
5,407 site records fit the layout and transit screen. The lossless index update
reduces the tested database from 470 MB to 442 MB. Hosted setup awaits an available
Supabase connection, and the Joying upgrade remains to be installed.

## Start here
- [`docs/session-handoff.md`](docs/session-handoff.md): current state, private artifact locations and the user's connection-check-only instruction for the next session.
- [`docs/buyer-mandate.md`](docs/buyer-mandate.md): current buyer criteria, exact duplex model and sourcing context (updated 2026-10-26).
- [`docs/cross-device-workflow.md`](docs/cross-device-workflow.md): database, desktop/Joying sync, full Loop build and deployment steps.
- [`docs/site-layout-screen.md`](docs/site-layout-screen.md): Houston frontage/access rules and the layout screen replacing the 100-ft shortcut.
- [`docs/campaign-pockets-2026-10-26.md`](docs/campaign-pockets-2026-10-26.md): full-study campaign ranking with resident owners, transit and subdivision controls.
- [`docs/quality-and-fit.md`](docs/quality-and-fit.md): scored shortlist, block rejection risk, commute comparisons and market conditions.
- [`docs/third-ward-opportunities-2026-10-26.md`](docs/third-ward-opportunities-2026-10-26.md): Third Ward inventory, UH/TSU access and the correction separating campaign density from acquisition opportunity.
- [`docs/third-ward-maps-and-listed-assemblages.md`](docs/third-ward-maps-and-listed-assemblages.md): parcel maps, corrected Third Ward display geography and the secondary listed-property assemblage search.
- [`docs/direction.md`](docs/direction.md): what we're building, the key dilemma, options, and the decisions still open.
- [`docs/project-history.md`](docs/project-history.md): how the project got here (PC data work, the failed browser map, the native rebuild).

## Acquisition context

The primary target is at least 10,000 contiguous sq ft with suitable dimensions
inside Loop 610 and within 0.5 mile of a bus or METRORail stop. The standard project
creates two 5,000-sq-ft parcels, each with a duplex whose two sides are each 5 bed /
5 bath: four dwelling units and 20 bedrooms / 20 bathrooms total for PadSplit use.
The buyers consider sites with improvements and may pay up to $20 per land sq ft
when the project checks out. A roughly 5,000-sq-ft site is an exceptional-deal lane.

All inside-Loop neighborhoods are in scope. Older ward priorities, the uniform
5,000-15,000 range, and the Zone-X-only assumption must be read with the current
mandate's supersession and confirmation notes. The code and generated datasets
are reconciled through the versioned full-Loop screening pipeline. Older static
exports and campaign rankings retain their original model versions.

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

The former research interface remains at `web/index.html`. The authenticated
desktop workspace is `web/workspace/`. Neither replaces the native map renderer.

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
tools/build_loop_screening.py            full Loop → private screening snapshot
tools/import_screening.py                snapshot → Supabase, atomic activation
supabase/migrations/                     schema, RLS, imports and sync functions
web/workspace/                          desktop map, lists, offline visits
AGENTS.md                               context and continuity for project work
docs/buyer-mandate.md                    current buyer mandate and sourcing context
docs/direction.md                        key dilemma, options, open decisions
docs/project-history.md                  project timeline and lessons
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

Use `SCREENING_SNAPSHOT=/private/sites.jsonl.gz ./build.sh` to build with the same
full-Loop snapshot imported into Supabase. Without that variable, the legacy
export is converted with stable IDs. The original APK was approximately 68 MiB,
mostly imagery; full-Loop bundle size differs.
Do not replace the signing key after distribution; Android requires subsequent
updates to use the same key.

## Field validation

The 0.5 native renderer has been installed and smoke-tested on the Joying unit. It
loads all 41,669 parcels with aligned satellite imagery. A road test is still
required to tune prediction/correction timing and POV look-ahead distance against
the unit's real GNSS behavior.

The 0.6 sync code has compiled to Android bytecode. Its desktop/offline round trip
passed with two browser clients and real PostgreSQL functions. Installation and
the actual Joying-to-hosted-Supabase round trip remain deployment checks.

## Data privacy

The generated source data includes public-record owner names. It and generated
map assets are intentionally excluded from this repository.
