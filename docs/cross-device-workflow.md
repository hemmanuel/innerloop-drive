# Shared acquisitions workspace

Decision: on October 26, 2026 the user selected Supabase and authorized the first
cross-device workflow in this repository. The native Canvas map stays in place.
For the latest session boundary and next authorized action, read
[session-handoff.md](session-handoff.md). The user currently requests a read-only
connection check and a report before any further database work.

## First workflow

1. Sign into the desktop workspace under `web/workspace/`.
2. Filter the full Loop by campaign area, HCAD neighborhood, layout/transit fit,
   address/account or the current map view. Inspect polygons and working layouts.
3. Save a site to the driving shortlist or a named list.
4. Connect Joying using the same **app user**. Open Workspace → Saved lists.
5. Tap the site, record a block impression and visit note. The note is committed
   to local SQLite before a network request is attempted.
6. On reconnect or app resume, the native sync worker sends its durable outbox.
   The desktop retrieves the visit on Sync or its next foreground poll.

The desktop also works offline after its first load. Its app shell is cached by
a service worker; saved geometries, observations and pending operations live in
IndexedDB. Online research queries load 250 sites at a time. The native map uses
the full offline binary, while saved-list metadata arrives through sync.
The Android cache stores each site, visit and queued mutation in a separate
SQLite row; saved-list growth does not enlarge one row beyond CursorWindow limits.

## Implemented boundaries

- `supabase/migrations/`: catalog, snapshots, account identities, site membership,
  lists, visits, RLS, import functions and durable change-feed functions.
- `tools/build_loop_screening.py`: full-study screening and private snapshot.
- `tools/import_screening.py`: resumable server-side upload and atomic activation.
- `tools/build_native_data.py`: the same snapshot → stable-ID native binary.
- `web/workspace/`: authenticated desktop map, filters, lists, visits and outbox.
- Native `WorkspaceStore`, `SessionVault`, `WorkspaceSync`, `WorkspaceUi`:
  SQLite persistence, Keystore-encrypted session, background sync and parcel cards.

The first release uses the same app identity on desktop and Joying. Workspace
membership tables support later team access, but invitations/admin management
are not part of this UI. Supabase dashboard login and the app's Supabase Auth user
are separate accounts. CRM, photos, routing and automated seller outreach remain
outside this first workflow.

## Identity and import rules

HCAD accounts are 13-digit **strings**. A single-account site is `S` plus its
account. An assembly is `A` plus the first 24 hexadecimal characters of SHA-256
over its sorted, deduplicated accounts joined with `|`. No address or export row
number is an identity. An assembly whose membership changes gets a new identity.

Every account is retained as a single-account site, including small parcels and
state classes omitted by the older export. Primary land area comes from the HCAD
land-area field. Zero/missing land area is never replaced with the area of a GIS
polygon. Condominium/common-land interests and accounts sharing identical parcel
boundaries stay in explicit review categories. The draft v1 run was stopped when
1701 Hermann Dr 11G exposed this issue; v1 was never imported. Use v2 outputs.

Assemblies additionally require an
exact normalized full owner name and mailing address, at least 20 feet of shared
boundary within the source's one-foot tolerance, and no substantial overlap.
Confidential/current-owner labels cannot create an owner group. The new pass can
combine a small parcel with an already-large parcel.

Each import creates an immutable screening run with source provenance, model
configuration, generator hashes and a snapshot checksum. Results remain hidden
until their expected single-parcel and total-site counts are complete. Activation
switches one workspace pointer; it never rewrites lists, visit notes or statuses.
Completed runs cannot be edited by the import API. Repeating an import reuses its
run, and the previous run remains available in the database.

The screen applies 40×45-foot and 30×60-foot two-story duplex footprints, parking,
clearances and pedestrian access. Corners/through-street/major-road sites retain
an access-layout queue. Broad, complex sites exceeding a 500-foot placement
search span retain `large_layout`; they are not silently dropped. `fits` means a
complete working layout and a GTFS stop within 2,640 straight-line feet. The
layout result itself is kept separately from the transit result.

## Sync semantics

Every mutation has one client UUID. The server stores its exact request and
response in the same transaction as the operation. A retry after a lost response
returns the original receipt. Reusing a UUID with different contents fails.

A workspace row lock serializes revision allocation and commit order. Clients
pull events after a server revision; device clocks never determine ordering.
The cursor advances in the same local transaction as the downloaded events.

Visits are append-only. Saved-site edits carry an expected revision; concurrent
edits return a conflict instead of overwriting another device. The UI offers
“Use this device” or “Keep server.” Removal from a list is a tombstone and syncs
to other devices. Pending local edits remain visible during downloads.

A rejected operation stays in the local review queue without blocking later
valid visits. The user can retry it or discard that local change. Authentication
and temporary network failures keep the outbox for the next sync attempt.

## Hosted setup

1. Create a Supabase project for this application. Use an existing suitable
   organization and choose the project plan explicitly before adding any paid
   capacity. Set the database password in the Supabase account setup flow.
2. Apply the committed migrations in timestamp order. With the official CLI:

   ```sh
   supabase login
   supabase link --project-ref PROJECT_REF
   supabase db push
   ```

3. In Authentication → Users, create the first confirmed app user and choose its
   password. This is not the Supabase dashboard account. Keep public signups off
   for the private workspace. `supabase/config.toml` disables local signups;
   confirm the equivalent hosted Auth setting when provisioning.
4. Serve `web/workspace/` over HTTPS (localhost works for desktop development).
   Sign in with project URL, publishable/anon key and the app user. First sign-in
   creates the workspace and Driving shortlist. Copy its ID from `workspaces`.
5. In the trusted import environment, set `SUPABASE_URL`,
   `SUPABASE_SECRET_KEY` and `INNERLOOP_WORKSPACE_ID`. Import the snapshot:

   ```sh
   python tools/import_screening.py /private/full-loop-v2
   ```

   The importer sends modern secret keys only in `apikey`. It also accepts a
   legacy service-role JWT through `SUPABASE_SERVICE_ROLE_KEY`.
   [Supabase API-key documentation](https://supabase.com/docs/guides/getting-started/api-keys).

6. Build the native app with the existing signing identity and the same snapshot:

   ```sh
   SCREENING_SNAPSHOT=/private/full-loop-v2/sites.jsonl.gz ./build.sh
   ```

7. Install the APK as an upgrade, connect the app, and perform the field round
   trip above. The Supabase URL/publishable key are entered on each device;
   neither needs a service-role key. The server key never belongs in the APK,
   browser, source repository or chat.

Development desktop server:

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory web/workspace
```

## Full Loop build

The October 26 `loop-duplex-v2` run contains **181,840 individual accounts and
4,603 same-owner assemblies**, or **186,443 site records**. Of those, **5,407**
pass the layout and transit screen: 4,513 individual-account sites and 894
assemblies. Twenty additional layouts fall outside the transit radius. Assemblies
retain their member accounts, so these are site-record counts rather than a count
of mutually exclusive acquisition opportunities.

The private snapshot is `.local/full-loop-v2/sites.jsonl.gz` (34,653,608 bytes),
run `6f68cd31-b3e6-585f-b559-1faccf957f4f`. Its native counterpart,
`.local/parcels.bin`, contains **186,199 mapped sites** in 35,616,763 bytes. The
244 accounts without matched county polygons remain in the database inventory.

Full validation checked all IDs and memberships plus **162,810 layout objects**
across 5,427 placed layouts, with zero errors. The Drew assembly passes `wide_5`;
3531 Wentworth remains `no_fit`. The 1701 Hermann condominium account retains
zero recorded land area and is excluded from land fits. The earlier campaign
scores remain historical until recomputed against this inventory.

Install `tools/requirements.txt`, then run from the repository root:

```sh
python tools/fetch_loop_geometry.py --study /private/study --cache .local/loop-geometry
python tools/build_loop_screening.py \
  --study /private/study --geometry .local/loop-geometry \
  --roads /private/loop_roads.json --gtfs /private/metro_gtfs.zip \
  --enrichment /private/sites_with_frontage.json --output .local/full-loop-v2
python tools/build_native_data.py .local/full-loop-v2/sites.jsonl.gz .local/parcels.bin
python tools/validate_screening.py .local/full-loop-v2
```

The county downloader saves resumable pages and checks every object count. The
builder uses the study's Loop polygon and all inside-Loop account centroids.
Unmatched accounts remain in the database with an explicit result; they cannot
appear as mapped polygons. Resuming requires the same model and source signature.
An optional placement cache requires matching source polygons, streets and
placement-engine hashes, then exact site members, address, area and geometry.
Land-interest eligibility is reevaluated even when a placement is reused. The
cache checksum and its provenance are saved in the new manifest.

The enrichment input carries earlier block-quality/control research where its
account membership matches; the new layout result replaces the old frontage pass.

Owner names and mailing addresses are used locally for assembly matching, then
omitted from the shared snapshot. Existing owner-category/locality flags are
retained where available. All generated assets, snapshots, downloads, databases
and credentials stay under ignored paths.

## Validation and deployment status

The official Supabase CLI (2.122.0) applied the initial three migrations to a fresh
PostgreSQL 17 database; a second push reported no changes. The subsequent index
migration was also applied through the CLI. Supabase role/Auth
stubs supply the local test identity layer.
They exercise actual RLS, import activation, mutation receipts, conflicts and
rescreening isolation. Two independent browser contexts run against those real
database functions with simulated login. Tests cover an offline shell reload,
a visit surviving reload, a lost acknowledgment and explicit status-conflict
resolution and recovery after a rejected operation. The native source compiles
against Android API 33 and desugars to API-23-compatible DEX using stable R8 9.5.28.

The complete 186,443-site snapshot imported and activated through the same SQL
RPCs in a disposable local database in 93 seconds. The database occupied
470,305,939 bytes, including 461,733,888 bytes of application tables/indexes.
Catalog summary and first-page queries, including starting `psql`, took
1.094/0.781 seconds; the Third Ward query took 0.703 seconds. The catalog exposes
1,248 HCAD neighborhood groups and 14 broader campaign-area groups.

The storage pass below reduces the measured database to **441,519,251 bytes**.
Supabase Free currently allows a 500-MB database, leaving approximately 58 MB
before hosted-service overhead. Retaining another full run would exceed that
allowance. Pro starts at $25/month with an 8-GB project disk. No paid plan has
been activated. [Pricing checked October 26](https://supabase.com/pricing).

### Lossless storage reduction

Migration `20261026000400_lean_catalog_indexes.sql` replaces a 30,777,344-byte
neighborhood index with a 1,531,904-byte neighborhood lookup index and a
401,408-byte partial index for fitting-site pagination. Neighborhood keys can
now share PostgreSQL's deduplicated index entries; the separate fit index
supports the default map view. Primary keys, uniqueness constraints, spatial
index, geometries and all data fields remain intact.

The whole-database measurement fell from 470,305,939 to 441,519,251 bytes (6.1%).
All 186,443 records produced the same complete-content digest before and after.
Nine API query comparisons covered fitting/all sites, Third Ward, viewport,
HCAD neighborhood, account and address searches; all returned identical JSON.
RLS/import/sync SQL assertions passed after the migration.

Three alternative PostgreSQL compression configurations were tested in temporary
full-data copies and discarded: they increased total storage slightly. No
coordinate rounding, polygon simplification or record removal was applied.

The next larger retention improvement is to keep older screening runs as exact
compressed snapshots outside the live database. The existing complete snapshot
is 34,653,608 bytes and the import tool can restore it. Cloud archive/restore and
removal of old database runs are not implemented; do not delete old runs on the
strength of this recommendation alone.

The user subsequently authenticated in Chrome and connected Supabase to their
ChatGPT account. The latest check confirms the plugin is **installed and enabled**;
its skills are loaded, but this chat still exposes no Supabase account-access
tools. Authenticated connectivity is not yet verified. The CLI has no login token.
Use the plugin connection when available, following the
[official plugin instructions](https://learn.chatgpt.com/docs/plugins).
The next session should perform a read-only connection check, report the result
and stop. The user explicitly said not to proceed with database work. The CLI
flow below remains an alternative, not a requirement for plugin access.

Hosted provisioning requires available Supabase access. Native device validation requires
installing the upgrade on Joying. Do not describe the local integration tests as
a deployed Supabase project or a completed head-unit field test.

The user can authenticate from their own PowerShell window and default browser:

```powershell
# From this repository, using the locally installed official CLI:
& ".local\supabase\supabase.exe" login
```

Complete the browser flow and enter its verification code in that terminal.
Passwords and access tokens do not need to be pasted into the conversation.
[CLI login](https://supabase.com/docs/reference/cli/supabase-login).

Run the tests using a disposable database:

```sh
psql ... -v ON_ERROR_STOP=1 -f supabase/tests/workflow.sql
PYTHONPATH=tools python -m unittest discover -s tests -p 'test_*.py'
python tests/serve_test_workspace.py --psql /path/to/psql --pg-port 55438 --database TEST_DB
node tests/browser_workflow.cjs
python tests/import_local_snapshot.py .local/full-loop-v2 --psql /path/to/psql --pg-port 55438 --database innerloop_cli_test
```

`serve_test_workspace.py` binds localhost and simulates authentication solely for
integration tests. It must never be deployed as the application backend.

For a fresh ordinary PostgreSQL test database, run
`supabase/tests/bootstrap_local.sql` before applying migrations. Skip that stub
file when testing against a real local/hosted Supabase project.
