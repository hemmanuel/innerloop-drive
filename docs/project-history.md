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

## 9. Full study and frontage correction (Oct 26, PC conversation)

- The transferred study is available at `C:\Houston_Infill\study`: a 9-GB
  DuckDB database, 21,722 candidate sites, the co-living research and web exports.
  The database was opened read-only and the site export parsed in full.
- The buyer is still raising its fund and banking land faster than it builds.
  It uses SPVs/equity partners, visits sites before closing, and prefers shorter
  Medical Center and UH/TSU commutes while accepting the whole Loop.
- The user challenged the arbitrary 100-ft frontage shortcut after visiting Drew.
  Official Houston access rules distinguish 44-ft and 33-ft child lots. Tight
  building gaps are possible through rated-wall, opening and maintenance design.
- Added [site-layout-screen.md](site-layout-screen.md), a configuration router and
  supplied-envelope calculation. Narrow and unmeasured sites remain in inventory.
- Measured situs-street frontage for 20,110 of 21,722 sites. Drew is approximately
  104.5 ft along the street; its previous 97.7-ft field is the short bounding side.
  Corrected the web map's labels accordingly. Android data remains unchanged.
- Source co-living examples include smaller duplexes and ten-bedroom single-family
  buildings; they do not all represent the buyer's five-bedroom-per-unit duplex.
- Concentrated owner campaigns need both suitable-site density and owner
  residence. Keep individuals, estates, trusts and business ownership separate.
  Same-owner assembly identity and shared-edge contiguity still need a tighter
  audit than the transferred pipeline's one-foot proximity grouping.
- Added [campaign-pockets-2026-10-26.md](campaign-pockets-2026-10-26.md): ranked
  410 half-mile squares, resolved local owner mailing addresses using the full
  county account join, and intersected active city lot/building-line controls.
  Oak Acres, Houston Harbor/Liberty Heights and Forest Hill lead the field sequence.
- Downloaded METRO's October 8, 2026 GTFS release and resolved active bus/rail
  boarding stops for October 26-November 1. Of 21,722 sites, 21,627 pass the
  half-mile straight-line screen; transit contributes little geographic sorting.

## 10. Quality, buyer fit and block rejection risk (Oct 26)

- The user emphasized that blocks likely to repel the visiting buyer or tenants
  must be quantified directly, alongside stacked commute benefits and acquisition
  pricing/inventory conditions.
- Downloaded HPD 2025/2026 street-level files. The 2026 file ends in June; used a
  common July 2025-June 2026 window and deduplicated serious-violence incident IDs.
  Enriched all 21,722 sites with 660/1,320-ft exposure counts and repeat-review flags.
- Added physical-context measurements, scheduled GTFS commute comparisons for
  nine pockets, market updates and a transparent desktop score for the original
  five-pocket shortlist. Current 311 requests failed with a server error; no
  zero-complaint assumption was substituted.
- The quality sequence is Oak Acres (79), Forest Hill (71), Harbor central/south
  (67 each), Harbor north (60). Grand Park's comparison square has repeat-review
  flags on 43 of 50 sites, versus 7/119 in Oak Acres and 0/45 in Forest Hill.
- Added [quality-and-fit.md](quality-and-fit.md) and a 444-site private field queue.
  Field observation can veto a tour regardless of the numeric desktop score.
  The native app bundle and outreach systems remain unchanged.

## 11. Third Ward omission and selection-bias correction (Oct 26)

- The user challenged Third Ward proper's absence despite observed qualifying
  sites and the buyer's demonstrated UH/TSU project. The initial five-pocket
  shortlist optimized resident-owner campaign reach, then received quality
  scores without comparing the omitted Third Ward pockets.
- Recovered 312 candidate sites in eight UH/TSU-area squares: 188 singles and
  124 same-owner assemblies, with 648 distinct account IDs and no account overlap.
  There are 225 geometry-review sites across all ownership categories; 88 are
  individual-, estate- or trust-owned. All 312 remain in the private site queue.
- Rosedale/Wentworth/Arbor has 20 individual geometry-review sites, 14 resident
  owners and no repeat-violence flags. Its modeled UH/TSU/TMC access is 12/4/25
  minutes, compared with Oak Acres' 39/42/55 minutes.
- Extended GTFS analysis to eight additional cells and allowed direct walking
  to nearby anchors. Saved the scope and method with the results.
- Independently counted Drew's serious incidents in the twelve months before
  the reported April 24, 2026 purchase: seven within 660 ft across six months,
  including three in public settings. The purchase demonstrates that our crime
  flag is not an automatic buyer-rejection rule.
- Added [third-ward-opportunities-2026-10-26.md](third-ward-opportunities-2026-10-26.md).
  Third Ward targeted sourcing joins the first acquisition wave. Keep campaign
  reach, buyer/location fit and seller economics separate. Original composite
  scores remain historical; they were not recalibrated into acceptance probabilities.
- Created private `third_ward_review.json` and `third_ward_site_queue.json`.
  No outreach, app rebuild or publication was performed.

## 12. Parcel maps and secondary listed-property assemblages (Oct 26)

- Built interactive parcel maps with actual outlines, internal assembly account
  boundaries, street labels, stops and property-level quality/fit evidence.
- Plotting exposed grid spillovers across I-45. The final primary map displays
  30 Rosedale/Arbor sites and 45 Drew/Tuam sites, including 22 assembly candidates.
  Twenty-one have matching current owner names; 2702/2706 Scott is separately
  flagged for owner-match review. Fifteen surrounding records stay in the source inventory.
- Corrected the road-class match for highway distances: include `HIGHWAY` and
  `FREEWAY`. Updated 7,932 site distances and synchronized the private queues.
  Historical composite scores are labeled accordingly.
- Recorded the user's secondary strategy: work the adjoining owner of a suitably
  priced stale listing, then secure the listed property and deliver the assembly.
  The main single-owner sourcing strategy remains primary.
- Built a second surface with six researched listings and 30 one/two-neighbor
  combinations. It deducts other known listing asks and an editable profit/cost
  reserve, distinguishes reset DOM from prior marketing, and marks pending anchors.
- Added [third-ward-maps-and-listed-assemblages.md](third-ward-maps-and-listed-assemblages.md).
  The browser checks cover parcel selection, correct pocket counts, budget
  changes, second-listed-property costs, unavailable anchors and narrow layouts.

## 13. Separate deep/narrow inventory from primary targets (Oct 26)

- The user identified 50-by-200-ft shapes in the map. Its default view had shown
  all 75 source sites, including 19 already outside the older geometry screen.
- Audited continuous street faces and actual equal-area polygon cuts. Four thin
  corner/through-street strips and one curved/tapered-frontage site also leave
  the primary pool. The new default is 24 Rosedale/Arbor plus 27 Drew/Tuam sites.
- Added frontage × depth, each child's street span, a bold street-face overlay
  and dashed equal-area cut. Other layouts are selectable separately; gray
  background parcels are explicitly identified as context.
- Preserved narrower side-by-side candidates, including approximately
  70-by-192-ft Rosedale sites. No 100-ft frontage requirement was reinstated.
- Applied the same audit to listed-property assemblages. Rear-neighbor pairs
  that only produce 50-by-200-ft sites no longer show a primary-project exit budget.
- Updated pocket comparisons to use the audited geometry pool. The complete
  source export and historical campaign rankings retain their earlier screen;
  the corrected counts are implemented in the two-pocket map payload.
- Geometry tests cover deep/narrow, square, compact-frontage, rotated, skewed,
  tapered, disconnected-frontage and shallow-strip cases. Browser checks cover
  filtered counts, retained inventory, dimensions, budgets and responsive layouts.

## 14. Parcel split was incorrectly promoted to product fit (Oct 26)

- The user challenged 3531 Wentworth (about 74 by 154 ft) and remaining frontages
  in the 60s. Code inspection confirmed the map admits a site at 66 ft combined
  and 33 ft per child without calling the existing building-envelope fit test.
- Those widths came from the access research. They do not supply the minimum
  footprint for a two-story duplex with two five-bed/five-bath units.
- Wentworth's equal-area split has street spans of about 36.6/37.5 ft, leaving
  30.6/31.5 ft at the street after the earlier 3-ft-per-side assumption. The
  actual product was not tested against those widths or the child polygons.
- Withdrew the statement that approximately 70-ft-frontage sites were viable.
  The 51-site count describes parcel geometry candidates only. Documentation
  now distinguishes that from product fit. No replacement minimum was invented.
- The next product-fit implementation needs an explicit building envelope,
  unit arrangement and parking/access layout. The current map remains the
  geometry candidate view until that separate test is implemented.

- The user clarified that Drew's **structures**, not its lot sizes or generous
  gaps, are the calibration target. Measure and fit those footprints on the
  candidate parcels. The 66/33 threshold came from a narrow-lot access provision,
  not Drew measurements. The recorded approximately 104.5-by-98-ft dimensions
  describe Drew's land; no structure-based fit model had been completed.

## 15. Reasonable duplex footprints and map rescreen (Oct 26)

- Public permits identify Drew's two-story no-garage duplexes but omit dimensions.
  The user declined submitting a records request and authorized reasonable
  duplex dimensions. The draft was cancelled without submission.
- Reviewed SIH's dimensioned two-story co-living plans: a 30-ft-wide seven-bedroom
  duplex unit at 1,866 heated sq ft, and 20-ft-wide five-bedroom units at 1,160
  heated sq ft. Selected 40-by-45 and adapted 30-by-60 working duplex footprints,
  each giving 1,800 gross sq ft per dwelling over two floors.
- Implemented rigid building rectangles in equal-area child polygons, 3/5-ft side
  options, eight 9-by-19 parking spaces in dwelling-assigned tandem pairs, 3-ft
  pedestrian paths, entry/rear reservations and 12/18-ft driveway scenarios.
  Buildings are never sheared to make a skewed parcel pass.
- Removed road-facing false positives that crossed intervening property. Corners
  and through-street sites have a separate access-layout group. Major-road
  frontages also move there for shared/flag/turnaround access; a front-only fit
  cannot bypass their street-side building-line and side-access work.
- Rescreened the 75 mapped sites: 5 Rosedale/Arbor and 8 Drew/Tuam front-access
  fits, 49 street-access layout cases and 13 other layout/geometry/owner cases.
  Drew fits the broad working model. Wentworth fails due to its actual skew,
  while a rectangular 74-ft-frontage site fits the narrow model.
- Applied the model to 30 secondary assemblies: six front-access fits, including
  three around active 3212 McIlhenny; three others have an unavailable anchor.
  Updated both maps with actual-scale buildings, parking and access overlays.
- Geometry tests cover widths, skew, rotation, boundary pinches, front jogs,
  parking/path separation and retained area gates. Browser checks cover map
  groups, drawn objects, budget gating, selected-site zoom and mobile/dark layouts.
- Updated the mandate, direction and research docs. The full 21,722-site export
  and Android bundle were not rerun or rebuilt by this two-pocket update.

## 16. Full-Loop screening and the first shared workflow (Oct 26)

- The user selected Supabase, asked for schema/migrations/code in innerloop-drive,
  and required the full Loop screening to feed the same system. The first workflow
  is desktop shortlist → Joying visit/status/note → desktop, with offline writes.
- Added workspace-scoped tables and RLS, immutable screening runs, canonical
  account/assembly IDs, append-only observations, list tombstones, durable change
  events, idempotent mutation receipts and explicit conflicting-edit resolution.
  Imports activate only after complete counts and preserve all acquisition work.
- Built the authenticated desktop map with neighborhood/campaign-area filters,
  actual parcel and layout shapes, named lists, visit notes and an IndexedDB
  outbox. The app shell and saved sites survive an offline reload.
- Added native tap cards, list highlighting, saved lists, block impressions and
  background sync while preserving Canvas/GPS behavior. SQLite stores records
  separately; Android Keystore encrypts the session. The original signing key
  is required for upgrades. No replacement signing identity was created.
- Downloaded and cached 211,139 county parcel polygons. The inside-Loop study
  contains 181,840 accounts, of which 181,596 match county polygons. Added 4,603
  strict same-owner contiguous groups, including small-plus-large combinations.
- Stopped the first draft when a condominium account at 1701 Hermann inherited
  its entire building parcel's area. The corrected model uses recorded land area,
  flags common-land interests and identical shared polygons, and reevaluates
  those conditions before reusing any verified placement cache. V1 was never
  imported.
- Completed `loop-duplex-v2`: 186,443 site records; 5,407 layout-and-transit fits
  (4,513 singles, 894 assemblies). Twenty additional layouts exceed the transit
  radius. Third Ward contributes 368 fitting site records. Campaign scores are
  still the earlier research snapshot.
- Validated every ID/member relationship and 162,810 layout objects with no
  errors. Drew passes `wide_5`; Wentworth remains `no_fit`. Generated the matching
  35,616,763-byte native bundle containing 186,199 mapped sites.
- The official Supabase CLI applied all migrations to fresh PostgreSQL 17 and
  reported no changes on a repeat push. RLS/import/sync SQL assertions, 12 Python
  tests and a two-browser offline/reconnection/conflict test passed. Android Java
  compiles and desugars for API 23 using stable R8 9.5.28.
- Imported and activated the complete snapshot locally through the production
  SQL functions in 93 seconds. The database uses about 470 MB, close to the
  500-MB Free allowance. Requested the user's choice of Free initial setup or
  Pro at up to $25/month; no paid plan has been activated.
- The user prefers authenticating through their own browser. Installed the
  official CLI locally and provided its `login` command for their PowerShell
  window. Supabase provisioning awaits that login. No hosted project, app Auth
  user, public deployment or Joying upgrade has been created by this work yet.
- Implementation and operational steps are in
  [cross-device-workflow.md](cross-device-workflow.md). Generated inventory,
  databases, credentials and native assets remain outside Git.

## 17. Storage reduction and plugin sign-in clarification (Oct 26)

- The user asked for simple storage savings without losing data resolution.
  Measured tables/columns/indexes rather than simplifying the parcel geometry.
- Tested three lossless compression settings against full temporary copies.
  Each preserved every row but slightly increased storage, so none was retained.
- Replaced the 30.8-MB neighborhood index with a 1.5-MB neighborhood lookup and
  0.4-MB partial index for fitting sites. Actual database size fell from 470.3 MB
  to 441.5 MB, a 6.1% reduction. Added migration 20261026000400.
- Complete-content checksums of all 186,443 records match. Nine API query
  comparisons returned identical JSON; RLS/import/sync assertions still pass.
  Every coordinate, field, record and identity is preserved.
- The complete source snapshot is already losslessly compressed to 34.7 MB.
  Archiving older screening runs outside the live database is a future retention
  option; no old run was deleted and no cloud archive lifecycle was implemented.
- The user clarified that authentication happened through Chrome and the
  ChatGPT Supabase connection, not CLI login. This session's plugin check still
  reports uninstalled and exposes no Supabase tools. Provided the official
  Plugins/Installed and new-chat guidance; no credentials were requested in chat.

## 18. Connection-only boundary and session handoff (Oct 26)

- A later plugin check confirms Supabase is now installed and enabled; its
  skills loaded in this chat. Supabase account-access tools still did not appear,
  so authenticated service access has not yet been verified.
- The user instructed: "Don't proceed with the db work, let me know once it's
  connected." No database work followed that instruction. The next session must
  run a read-only connection check, report it and await further instruction.
- Added [session-handoff.md](session-handoff.md) and linked it from AGENTS.md and
  README. It records the branch/PR, buyer context, model, completed validation,
  artifact paths, stopped local services, uncompleted deployment and plan choice.
- Code and docs are pushed on `codex/cross-device-workflow`; private datasets
  remain on the PC. A new session must distinguish a repo clone from possession
  of the generated full-Loop snapshot and native bundle.

## Lessons
1. Test in-vehicle software against real motion: road tests or recorded GPS traces, not desktop simulation.
2. Browser/WebView runtimes are the wrong tool for a moving map on a head unit.
3. A desktop browser is still fine for studying an area. The vehicle needs a native runtime.
4. Keep stable parcel IDs everywhere. Every later feature (lists, CRM links, sync, routes) depends on them.
