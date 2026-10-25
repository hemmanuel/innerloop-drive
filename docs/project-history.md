# Project history

How Inner Loop Drive came to exist, in order. Two machines and two agents have worked on it:

- **PC (WSL, `~/kb`)**: Claude Code. Library study, the Houston public-data pipeline, lot scoring, and the first (browser) map.
- **Joying head unit (Termux, `~/innerloop-android`)**: the on-device agent. The native Android app in this repository.

Dates are 2026.

This is a chronological record. The current acquisition requirements are in
[`buyer-mandate.md`](buyer-mandate.md); the earlier screening choices below do not
override the user's later clarification.

## 1. Program study and playbook (Oct 8–9, PC)
- Built a private knowledge base from the wholesaling program's video library (637 hours), served to Claude only through an
  anonymizing gateway (`kb-private`).
- Turned it into a cited playbook for the program's current system: **direct-to-agent (D2A) wholesaling run in GoHighLevel**
  (texting rounds, AI reply bot, vetting calls, offers, contracts, dispositions, VA team).

## 2. Houston market data (Oct 11, PC)
- Downloaded Houston public data:
  - HCAD 2010–2026 rolls, parcels and permits;
  - FEMA flood maps;
  - Redfin zip data;
  - City of Houston permits;
  - the TREC agent roster.
- **Zip study:** scored every Harris County zip for D2A wholesaling (flips, investor buying, price band, flood, institutional
  landlords) and picked starting clusters.
- **Agent list:** listings → TREC licence match → HCAD join → fit score → tiered agents for texting, with a weekly
  refresh workflow.

## 3. Inside-610 land and the co-living buyer (Oct 24, PC)
- Explored an inside-610 land buy box (10K+ sq ft, MAO from land value).
- An out-of-state co-living developer group (two side-by-side 10-bed/10-bath structures per 10K sq ft site) became the target buyer.
- **Co-living scan:** found completed and in-progress co-living builds inside 610 from HCAD bedrooms/baths, building counts and
  permits, and grouped their owners into operators (backup buyer list).
- **Target lot list:** every inside-610 site of 10K+ sq ft (single lots and same-owner pairs), with condition, owner type, years
  held, flood, campus distance and duplex context. Ranked by priority (A/B/C) and lot form (existing ~5K lots first, no replat).
- **Calibration sheet:** a 20-lot sample with block-level locations for the developers.

## 4. What the market actually builds (Oct 25, PC)
- **Profile of 60 confirmed co-living builds:**
  - usually one structure on a 5,000 sq ft (50 × 100 ft) lot;
  - land around $18/sq ft (HCAD), about 2 miles from campus;
  - outside the 100-year floodplain;
  - about 40% built to sell.
- **Side-by-side builds:** 20 of the 60 sit next to another co-living build. Most of those pairs were two *existing* platted lots
  bought together, not one lot replatted.
- **Hidden co-living detector:** HCAD room counts under-record co-living duplexes. Scoring "DUPLEX – NO GARAGE" permits, heated
  area, baths and investor ownership caught all five marketed Third Ward examples, and added 48 likely and 92 possible
  co-living duplexes plus 37 permits not yet built.
- **Area comparison:**
  - Third Ward: proven.
  - OST / South Union: most active.
  - Fifth Ward / Denver Harbor: rising.
  - Near Northside: warming but thin.
  - Second Ward: townhome-priced.
  - The Brock St corridor (Riverview / Edmundson, south of UH): an active 20-unit no-garage duplex project on about $8/sq ft land.

## 5. The browser map (Oct 25, PC) — failed in the car
- Built a local Leaflet web app over the lot list:
  - filters, list and detail panel;
  - a drive mode with GPS follow and picks;
  - all Third Ward and Second Ward parcels;
  - recent co-living layers;
  - an offline Protomaps vector basemap and an offline USGS satellite pack.
- Tested only on a desktop with a **simulated, stationary** GPS position.
- **In the car it was unusable:**
  - laggy and jumpy following;
  - freezes;
  - Firefox's location provider timing out on the Joying;
  - the `file://` path pointed one directory too high.
- Root causes:
  - about 1 Hz GPS with no smoothing between fixes;
  - independent Leaflet pan and rotate animations;
  - JavaScript running on the UI thread;
  - parcel layers rebuilt on the main thread.

## 6. Native rebuild (Oct 25, Joying) — this repository
- **0.1–0.3:** WebView wrapper with native GPS injection, POV rotation fix and compass. Still too jittery.
- **0.4:** WebView removed. Native hardware-accelerated Canvas renderer:
  - GPS on a dedicated thread;
  - bounded prediction (2 s) with eased correction;
  - all 41,669 parcels in a 4 MB binary, culled to the viewport;
  - offline satellite.
- **0.5:** Satellite/Map toggle (Esri street tiles cached after first use), drag-to-pan, pinch zoom, Follow.
- Plans written:
  - `sync-navigation-plan.md`: Supabase sync, a desktop viewer, routing.
  - `ai-acquisitions-plan.md`: buy-box engine, CRM boundaries, AI roles.
- **Earlier buy box (subsequently clarified; see section 8):**
  - 5,000–15,000 sq ft;
  - vacant or acceptable teardown;
  - FEMA Zone X;
  - inside 610, near a bus stop;
  - Third Ward and Second Ward first;
  - D2S and D2A lanes.

## 7. Where things stand (Oct 25)
- **Smoke-tested on the Joying:** the native app loads all parcels with aligned imagery. A moving road test is still needed.
- **Data source:** the app is built from the PC's generated web data (`data.js`, `parcels.js`, `picks.js`, `sat/`). That data
  carries no stable parcel IDs in the native format, and picks are baked in at build time.
- **No connection to the CRM, outreach or lists yet.**
- **GitHub:** connected on the PC (Oct 25), so both agents can work through this repository.

## 8. Buyer mandate clarified (Oct 25, PC conversation)

- The user specified the actual prototype: a standard 10,000-sq-ft contiguous
  site becomes two 5,000-sq-ft parcels, each with a duplex; each duplex side is
  5 bed / 5 bath. Total: four units, 20 bedrooms, and 20 bathrooms for PadSplit use.
- Buyers consider qualifying sites anywhere inside 610 within 0.5 mile of a bus
  or METRORail stop. Third, Second, Fifth Ward and other neighborhoods are in scope
  without a buyer neighborhood preference. The buyers may sell one duplex and
  retain the other.
- The conditional ceiling is $20 per land sq ft, or $200,000 on a qualifying
  10,000-sq-ft site. Existing improvements are acceptable if the project works;
  roughly 5,000-sq-ft sites are an exceptional-deal lane.
- The earlier uniform 5,000-15,000 range and ward priorities are superseded.
  Zone X remains an earlier screening assumption requiring buyer confirmation,
  not a newly verified requirement or clearance for other flood zones.
- The 6019 England St investigation highlighted an apparent per-lot price versus
  total-project-area mismatch. The user stopped that property's research after
  the initial explanation; no full restriction, title, or feasibility review was
  completed. Preserve the price-basis check as a sourcing lesson.
- Reviewing this repository established that the existing inside-610 pipeline
  and co-living research should be reused and audited. The older six-neighborhood
  distressed-property inventory in the PC workspace is supplemental.
- Added the current mandate and linked it from the project entry points. The
  native binary still omits account IDs, picks remain baked in, and sync/CRM/list
  workflows remain planned. Renderer, CRM, backend, and CI choices remain open.

## Lessons
1. Test in-vehicle software against real motion: road tests or recorded GPS traces, not desktop simulation.
2. Browser/WebView runtimes are the wrong tool for a moving map on a head unit.
3. A desktop browser is still fine for studying an area. The vehicle needs a native runtime.
4. Keep stable parcel IDs everywhere. Every later feature (lists, CRM links, sync, routes) depends on them.
