# Direction: the key dilemma and our options

Status: software decisions pending; buyer mandate clarified 2026-10-25 in
[`buyer-mandate.md`](buyer-mandate.md). History is in [`project-history.md`](project-history.md); the detailed plans are
[`sync-navigation-plan.md`](sync-navigation-plan.md) and [`ai-acquisitions-plan.md`](ai-acquisitions-plan.md).

## What we're building
One acquisitions system for the current buyer mandate: at least 10,000 contiguous
sq ft with suitable dimensions, anywhere inside 610 within 0.5 mile of a bus or
METRORail stop; existing improvements are acceptable if the project works. The
standard site becomes two 5,000-sq-ft parcels, each holding one duplex with two
5-bed/5-bath sides (four units, 20 bedrooms and 20 bathrooms total). Buyers may pay
up to $20 per land sq ft after diligence; roughly 5,000-sq-ft bargains are a separate
exception lane. There is no buyer preference for particular wards.

The earlier 15,000-sq-ft ceiling and Zone-X-only screen are not confirmed buyer
requirements. Preserve flood diligence and resolve the policy explicitly; see
the mandate for remaining measurement, layout, cost, and delivery questions.

- **Study** an area on the desktop and build named lists: completed co-living comps, teardown leads, listed lots to text, inbound leads.
- **Work** those lists through the CRM (GoHighLevel is the current candidate): D2A texting rounds, owner outreach, PPC inbound.
- **Drive** in the Joying app:
  - Free-driving mode: parcel sizes and color-coded attributes visible hands-free, for driving for dollars.
  - Tap a parcel for a basic info card and add it to a list.
  - Lists show as map layers.
  - Parcels in active conversations show their CRM status.
- **Navigate** to list stops, eventually inside the app.

Every piece hangs on stable parcel identity: retain each HCAD account and a
canonical site/assembly key with its constituent accounts. A site may contain
multiple tax accounts or legal lots; an account count is not a legal-lot count.

Reuse the existing inside-610 parcel and co-living research. The Third/Second Ward
context layer is current map coverage, not the boundary for new acquisitions work.
The pipeline needs an audit against the clarified mandate before its scores can
be treated as current buyer qualification.

## The key dilemma
**We want to start working the buy box aggressively now, but the field tool that makes that efficient sits on a foundation we may
have to replace, and every hour spent on infrastructure is an hour not spent on leads.**

It shows up in three places:

1. **Map engine.** The native Canvas renderer works and builds on the Joying itself (Termux: `javac`, `d8`, `aapt2`, no Gradle).
   But POV rotation, zooming out over 40K parcels, labels and prediction overshoot are the same problems that map engines solve
   with GPU geometry, vector tiles and built-in location tracking. Fixing them by hand means re-implementing a map engine.
   Moving to an engine (MapLibre Native) means a Gradle build, so CI builds instead of on-device builds.
2. **Build vs buy for lists, driving for dollars and the CRM link.** Commercial driving-for-dollars and list tools exist. A custom
   system wins on our HCAD data, buy-box scoring, co-living intelligence and the GHL link, but it costs time before it pays back.
3. **Data plumbing.** Today the app is rebuilt from the PC's web export, without parcel IDs, with picks baked in at build time and
   with owner names in the source files. Nothing can sync or link to the CRM until this changes.

## Options

### A. Patch the current native app and drive now
Fix the known flaws in the Canvas renderer:
- detail by zoom (hide the small context parcels below ~z17);
- animate the vehicle between fixes instead of predicting ahead;
- hold position when stationary;
- cap the frame rate when idle;
- reuse per-frame objects.

Then add local lists (tap → card → add to list, stored on the device) and hand-off navigation (open Google Maps or Waze).
- **For:** fastest to the field; keeps on-device builds.
- **Against:** POV and zoomed-out performance stay limited; lists stay on one device; no CRM link.

### B. Rebuild on MapLibre Native with vector tiles
- Parcels as vector tiles with IDs and buy-box attributes. Offline Protomaps street map and USGS satellite. MapLibre's location
  layer does the GPS following. Data-driven styling for list layers and CRM status.
- APKs built by GitHub Actions; the Joying installs releases.
- **For:** solves the rendering and motion problems at the root; ready for lists, sync, routes and navigation (MapLibre's
  navigation add-on).
- **Against:** a few days of rebuild; a build pipeline off the device; signing keys move to CI.

### C. Buy the field and list tooling
- Use a commercial driving-for-dollars and list app with its CRM integrations. Import our HCAD-derived lists and keep GHL for
  conversations.
- **For:** quickest path to tap-to-list in the field.
- **Against:** loses our parcel-level buy-box attributes and co-living layers in the car; vendor limits on data and export;
  recurring cost.

### D. Hybrid (recommended)
Do what every option needs first, then upgrade the renderer:
1. **Now (days):**
   - stable parcel IDs in the native data;
   - a PC-side export with buy-box fields and no owner names;
   - local lists with tap → card → add;
   - hand-off navigation;
   - the cheap renderer fixes from A.
   
   Start driving and working leads.
2. **Next (1–2 weeks):**
   - Supabase as the shared parcel, list and flag database, synced by the app (offline-first) and a desktop study tool;
   - a GHL connector: lists push to contacts and opportunities, and webhooks bring status back to parcels, so conversation status shows on the map.
3. **Then:** move the renderer to MapLibre Native with vector tiles. It reuses the same IDs, database and lists, so nothing built
   in steps 1–2 is thrown away.
4. **Later:** list routes (ordered stops drawn in the app, next-stop guidance), PPC inbound address-to-parcel matching, AI briefs, and
   turn-by-turn with voice if still wanted.

## In-app navigation: feasible, in stages
| Stage | What | Needs |
|---|---|---|
| 1 | "Navigate" on a card opens Google Maps or Waze | Android intent only |
| 2 | Optimized route over a list, drawn in the app, next-stop and arrival | Routing service (hosted Valhalla or OSRM, or self-hosted), called from the backend |
| 3 | Turn-by-turn, voice, rerouting | MapLibre navigation add-on; rerouting needs data unless a Houston road graph ships on the device |

## Working across devices
- **This repository** is the shared memory. Both agents read the docs before working and record outcomes in them.
- **PC agent:** data pipeline (parcels, IDs, buy-box fields, vector tiles, basemaps), backend and connector, desktop tool, CI.
- **Joying agent:** installs builds, runs field tests, records GPS traces of real drives, captures frame and memory statistics,
  makes on-device fixes, and writes field-test notes.
- **Planned files:**
  - `AGENTS.md`: roles and rules;
  - `TASKS.md`: owner, status and acceptance criteria per task;
  - `docs/decisions/`;
  - `field-tests/YYYY-MM-DD.md`, with GPS traces attached.
- **Private data** (owner names, contacts) stays out of Git. App data ships without owner names; contacts live in the CRM.

## Decisions needed
1. Option D (or another) and the engine: patch Canvas now and move to MapLibre later, or go straight to MapLibre?
2. CRM: confirm GoHighLevel. One location or several? Custom "Property" object available? Which pipeline stages map to map colors?
3. Outreach lanes at launch: D2A and PPC only, or owner outreach (D2S) too? That decides whether skip tracing and owner contacts come in.
4. Backend: Supabase hosted, or something else?
5. List vocabulary: starting lists and flags (co-living comps, teardown lead, vacant, FSBO sign, builder sign, pass + reason).
6. In-motion rules: what can be tapped above walking speed, and should there be voice alerts for list parcels?
7. Builds: are GitHub Actions and private releases acceptable for producing the APK?
