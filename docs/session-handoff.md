# Session handoff

Updated October 26, 2026. Read this before continuing the shared-workspace setup.

## Immediate instruction from the user

**Connection check only.** The user's latest instruction is: "Don't proceed with
the db work, let me know once it's connected." Verify authenticated Supabase
access with a read-only project/organization listing, report the result, and
stop. Wait for the user to resume database work before provisioning a project,
applying migrations, importing data or changing a plan. Updating these handoff
docs does not revoke that instruction.

The user signed in through their own Chrome browser and connected Supabase to
their ChatGPT account. The latest plugin check now confirms **installed and
enabled**. Its Supabase skills loaded, but no Supabase account-access tools were
exposed to the previous chat. Authenticated service access is therefore still
unverified. A fresh chat should discover the available Supabase tools first.
The CLI was not authenticated; CLI login is an alternative, not a prerequisite
for using the plugin. Do not request passwords or tokens in chat.

## Repository and saved work

- PC checkout: `C:\Users\emman\OneDrive\Documents\ChatGPT\Infill Wholesale\innerloop-drive`.
- Branch: `codex/cross-device-workflow`, pushed to origin.
- Draft PR: [#3](https://github.com/hemmanuel/innerloop-drive/pull/3), not merged.
- Implementation commit: `1c4894a`; lossless index optimization: `2f56eca`.
- Source, migrations and documentation are on GitHub. Private generated data
  remains on this PC in ignored directories. A clone on another computer does
  not include those assets; transfer them privately rather than assuming they
  were committed or rerunning the research unnecessarily.

## Working context

Read [buyer-mandate.md](buyer-mandate.md) and [direction.md](direction.md) for the
acquisition strategy. We are the local acquisition/wholesale partner, sourcing
sites for an out-of-state co-living developer. The primary site is 10,000+
contiguous sq ft inside 610, within half a mile of transit, supporting two
duplexes with two 5-bed/5-bath units apiece. Improvements are acceptable; buyers
may pay up to $20 per land sq ft. UH/TSU/TMC access is a preference, and all Loop
neighborhoods remain in scope.

The user authorized reasonable building dimensions instead of obtaining Drew's
plans. Current placement tests use whole-duplex footprints of 40×45 or 30×60 ft,
two stories, side clearances, eight parking spaces and pedestrian access. Neither
100 ft nor 66 ft is a product-fit gate. Drew's assembly passes the broad model;
3531 Wentworth fails the modeled layout. See
[site-layout-screen.md](site-layout-screen.md).

Communicate directly. Include unresolved facts only when they change the current
decision or next action; avoid boilerplate hedging and repeated diligence caveats.

## Completed implementation and data

- Four migrations under `supabase/migrations/`: workspace/RLS/sync schema,
  atomic snapshot imports, area filters and smaller catalog indexes.
- `web/workspace/`: desktop map, neighborhood/campaign-area filters, saved lists,
  visit notes and durable offline sync. Native Android keeps Canvas and adds
  stable site IDs, tap cards, saved lists, SQLite records and an encrypted session.
- Full Loop `loop-duplex-v2`: **181,840 accounts + 4,603 same-owner assemblies =
  186,443 site records**. **5,407** pass layout and transit, including 368 Third
  Ward site records. Earlier campaign scores have not been recomputed for this
  larger inventory; their matching enrichment is retained where available.
- All IDs/memberships and 162,810 placement objects passed validation. Twelve
  pipeline tests, three frontage tests, SQL RLS/import/sync checks and two-browser
  offline/reconnection/conflict tests passed. Android compiles to API-23-compatible
  DEX. The complete local database import took 93 seconds.
- Index optimization reduced the local database from **470,305,939** to
  **441,519,251 bytes**. All-record checksums and nine map-query comparisons are
  unchanged. Three compression experiments did not help and were discarded.

Private artifacts relative to this checkout:

| Artifact | Location |
|---|---|
| Valid complete snapshot | `.local/full-loop-v2/sites.jsonl.gz` (34,653,608 bytes) |
| Version, provenance and counts | `.local/full-loop-v2/manifest.json` |
| Geometry validation | `.local/full-loop-v2/validation.json` |
| Initial import report | `.local/full-loop-v2/local-import-validation.json` (before index optimization) |
| Final storage/content check | `.local/storage-content-after.json` |
| Full native bundle | `.local/parcels.bin` (186,199 mapped sites; 35,616,763 bytes) |
| Downloaded county polygons | `.local/loop-geometry/` |
| Original study, unchanged | `C:\Houston_Infill\study` |

Snapshot run ID: `6f68cd31-b3e6-585f-b559-1faccf957f4f`.
SHA-256: `9b324ece9f2149d1d4746c53f1c9e5e5c608870cbaafbbbef973ea1db5a6d728`.
The v1 draft is invalid: it assigned a condominium account the parent polygon's
land area. It was never imported. Use v2; it preserves recorded land area and
routes condo/shared-boundary interests out of primary fits.

## Deployment state and later work

No hosted Supabase project, application Auth user, public desktop deployment or
Joying upgrade has been created by this work. The local database and browser
test server are stopped. `.local/pgdata` retains the disposable PostgreSQL 17
cluster on port 55438, including `innerloop_cli_test`; its synthetic Auth stubs
must never be run against hosted Supabase.

No paid plan is authorized or activated. The measured 442-MB database leaves
about 58 MB against the currently documented 500-MB Free allowance before hosted
overhead. The user has not selected Free versus Pro. Archiving older runs as
compressed files is a future option, not an implemented retention process.

After the user explicitly resumes implementation: inspect accessible projects,
settle the plan/project, apply the four migrations, configure the private app
login, import the existing v2 snapshot, serve the desktop workspace over HTTPS,
and install/test the native upgrade using the existing signing identity. The
desktop and Joying app use the same application Auth user, separate from the
Supabase dashboard account. Do not regenerate signing keys.

Operational commands and source structure are in
[cross-device-workflow.md](cross-device-workflow.md). The chronological reasoning
and prior map corrections are in [project-history.md](project-history.md).
