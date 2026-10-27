# Parcel sync and navigation plan

Status: the first list/visit workflow is implemented in source as of October 26,
2026. See [cross-device-workflow.md](cross-device-workflow.md) for the actual
schema, local tests and hosted/device deployment status. Routing remains planned.

Acquisition criteria and the two-duplex development model are maintained in
[`buyer-mandate.md`](buyer-mandate.md). Sync must support both individual parcels
and contiguous multi-parcel sites across the entire inside-610 area.

## Goals

1. Tap a parcel in Inner Loop Drive and save it.
2. Make saved parcels visible in a separate desktop viewer.
3. Allow the desktop viewer to save or edit parcels and have those changes appear on the Joying unit.
4. Later, load saved-parcel lists, create an efficient route, and navigate that route inside Inner Loop Drive.
5. Preserve offline driving behavior whenever connectivity is unavailable.

## Recommended architecture

```text
Desktop viewer  <---->  Supabase/Postgres  <---->  Joying app
                                                    |
                                              local SQLite
```

GitHub remains the source-code and release repository. It should not be used as
the runtime synchronization database.

Supabase is the selected backend because it provides Postgres,
authentication, row-level security, REST/realtime APIs, and a practical path to
the separate desktop viewer. The APK must never contain a Supabase service-role
key. It should authenticate as a normal user or dedicated device identity and be
restricted by row-level security.

## Parcel identity and data

Saved records must use a stable parcel identifier, preferably the HCAD account
ID or the canonical combined account key already present in the generated data.
Addresses are display fields, not identifiers.

For an assembly, retain every constituent HCAD account alongside the canonical
combined key; do not replace parcel records with an address or aggregate area.
Keep tax accounts, verified legal lots, and the proposed two-parcel layout
separate. Existing adjoining lots may support the project without the same
replat work as a single legal lot, subject to survey and title verification.

The native `parcels.bin` format is now ILP3, carrying account IDs, canonical site
IDs, assembly membership, neighborhood and screening status. Both candidate and
context parcels support selection and saving.

The original single-record sketch below is superseded by separate saved lists,
list items, append-only observations and screening snapshots in the migrations:

```text
parcel_id       stable HCAD/combined account key; unique
saved           boolean
status          optional workflow state (visit, interested, pass, etc.)
notes           optional text
created_at      server timestamp
updated_at      server timestamp
deleted_at      nullable tombstone timestamp
updated_by      desktop/Joying identity
```

Possible later fields include tags, rating, visit outcome, photos, and custom
geometry. If users need to introduce a parcel that is not in the bundled data,
store its GeoJSON geometry and centroid as a separate synchronized record.

## Joying parcel interaction

1. Convert a map tap from screen coordinates through the current pan/rotation/
   zoom transform into map coordinates.
2. Hit-test visible parcel polygons, preferring candidate parcels when layers
   overlap.
3. Show a compact, driving-safe card with address, area, status, and Save/Unsave.
4. Commit the action to local SQLite immediately.
5. Visually mark saved parcels in gold without waiting for the network.
6. Queue an idempotent background mutation for Supabase.
7. Pull remote changes on app launch/resume, after local writes, and periodically
   while connected.
8. Display sync state without blocking map or GPS rendering.

The existing generated `picks.js` entries can be imported into the synchronized
saved list during migration.

## Offline and conflict behavior

The Joying app must remain offline-first:

- Local SQLite is the app's immediate source of saved-state truth.
- Failed uploads remain in a durable mutation queue.
- Pulling the complete saved list is acceptable initially because it will be
  small relative to the bundled parcel dataset.
- Deletes use tombstones so an offline device does not resurrect removed rows.
- Initial conflict handling can use server-ordered last-write-wins semantics.
- Each mutation should have a client-generated ID so retries are idempotent.

Device clocks should not be trusted as the sole conflict authority. Prefer a
server timestamp or monotonically increasing server revision.

## Desktop viewer

The desktop viewer will be developed separately but should share:

- the same Supabase project and authenticated account/organization;
- the same stable parcel IDs;
- the same saved/status/tag vocabulary;
- the ability to create and edit route lists;
- an export/import path for backup and diagnostics.

The full private parcel data does not need to be placed in GitHub. It can be
loaded from the existing generated package or imported into appropriately
secured backend tables.

## Navigation progression

### Phase 1: ordered route display

The desktop or backend supplies:

- a route ID and revision;
- an ordered list of saved parcel stops;
- a road-following route polyline;
- optional distance and duration.

The Joying downloads and stores the route, draws the polyline in the existing
native renderer, displays the next stop, and advances stops manually or through
an arrival radius. This is a relatively small extension to the current app.

### Phase 2: route generation and optimization

Submit selected parcel centroids to a backend routing endpoint. The backend
calls a routing/optimization engine and returns ordered stops, a polyline, and
maneuvers. Keeping this server-side avoids embedding provider credentials in the
APK.

Potential engines:

- Google Routes / Route Optimization;
- Mapbox Directions / Optimization;
- GraphHopper or Valhalla;
- self-hosted OSRM for lower-cost Houston-area routing.

Choice depends on stop limits, optimization quality, traffic requirements,
pricing, and whether self-hosting is desirable.

### Phase 3: guided navigation

Add, in order:

1. distance and bearing to the next stop;
2. maneuver list and upcoming-turn display;
3. arrival detection and automatic stop advancement;
4. skip/reorder controls;
5. off-route detection and backend rerouting;
6. Android text-to-speech instructions;
7. optional road map-matching for the displayed vehicle position.

The current renderer and GNSS motion model can support route and maneuver
display. It does not contain a routable road graph, so route calculation and
rerouting should initially remain a backend responsibility. Previously fetched
routes should remain navigable offline, but automatic rerouting will require
connectivity unless an on-device routing graph is added later.

## Suggested implementation order

1. Create Supabase project, schema, authentication, and row-level policies.
2. Add stable parcel IDs to the native binary format.
3. Add parcel hit-testing and the Save/Unsave card.
4. Add local SQLite saved records and durable mutation queue.
5. Add push/pull synchronization and migrate existing picks.
6. Build the desktop viewer against the same schema.
7. Add route and route-stop tables.
8. Synchronize an ordered route and polyline to the Joying.
9. Add basic next-stop navigation.
10. Add maneuvers, arrival handling, rerouting, and voice guidance.

## Decisions still needed

- Does “add a parcel” only mean save an existing bundled parcel, or must users
  draw/import entirely new geometry?
- The first statuses are saved, visited, pursue and pass; visits contain notes
  and an optional 1–5 block impression. Expand tags/fields when acquisition work
  establishes a need.
- The first deployment uses the same app account on desktop and Joying.
  Separate device/team identities are a later access-management feature.
- Supabase hosted was selected October 26; provisioning remains an account setup
  step. Source implementation is documented in `cross-device-workflow.md`.
- Which routing provider, maximum route size, and optimization objective?
- Should routes optimize pure drive time, preserve a partial order, or support
  user-defined priority and time windows?
