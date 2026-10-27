# Concentrated owner campaigns: first pocket ranking

Updated October 26, 2026 from the transferred full study, Houston street and
planning layers, and METRO's October 8 GTFS release.

**Updated sequence: Oak Acres, Forest Hill, Harbor central/south, then Harbor
north.** The [quality-and-fit layer](quality-and-fit.md) adds block-level serious
violence, physical context, stacked commute access and pricing/inventory conditions.
The original owner-concentration ranking below remains available for campaign
planning; the quality layer changes which blocks we put in front of the buyer.

**Scope correction:** this is a concentrated-campaign shortlist, not the entire
acquisition search. [Third Ward near UH/TSU](third-ward-opportunities-2026-10-26.md)
adds 312 candidate sites across eight pockets, including 124 assemblies and 88
individual/estate/trust sites passing the geometry screen. Run targeted sourcing
there alongside geographic campaigns in the pockets below.

**Geometry update:** the later [Third Ward polygon audit](third-ward-maps-and-listed-assemblages.md)
corrects the two-pocket map to 51 side-by-side geometry sites and 24 other source
sites. Counts below use the earlier frontage/fill screen. Future campaign reranks
must apply the polygon audit before counting target owners; 50-by-200-ft sites
belong in the adjoining-frontage or separate-layout lane.

## Original owner-concentration sequence

Each row is a half-mile-by-half-mile square, not an entire neighborhood. Sites
below are individual-owned, at least 10,000 sq ft, with at least 66 ft of measured
situs-street frontage, a substantially rectangular shape and one connected
polygon. Assemblies also require matching owner names. These are the sites to
test against the buyer's building layout. Corner, narrow and other access
configurations remain in the wider inventory.

| Order / pocket | Individual sites | Unique owners | Owners mailing within this square | Same-owner assemblies | Frontage under 95 ft | Median HCAD land value/sq ft |
|---|---:|---:|---:|---:|---:|---:|
| 1. [Oak Acres / Oak Acres Extension](https://www.google.com/maps/search/?api=1&query=29.703192,-95.308233) | 119 | 116 | 96 | 2 | 21 | $8.50 |
| 2. [Houston Harbor / Liberty Heights north](https://www.google.com/maps/search/?api=1&query=29.782783,-95.297025) | 92 | 89 | 63 | 15 | 4 | $12.80 |
| 3. [Houston Harbor / Liberty Heights central](https://www.google.com/maps/search/?api=1&query=29.775527,-95.297288) | 80 | 78 | 44 | 12 | 6 | $12.80 |
| 4. [Forest Hill](https://www.google.com/maps/search/?api=1&query=29.724732,-95.299132) | 45 | 44 | 36 | 3 | 24 | $14.00 |
| 5. [Houston Harbor / Liberty Heights south](https://www.google.com/maps/search/?api=1&query=29.768271,-95.297552) | 58 | 58 | 31 | 11 | 0 | $11.20 |

The 95-ft sensitivity column avoids counting 99-point-something GIS measurements
as meaningfully narrower than a nominal 100-ft lot. All sites in these five rows
pass the half-mile straight-line transit screen. Forest Hill has one site in the
mapped special flood hazard area; the other four rows have none. The measured
minimum-lot overlays exceed half of the site area on none of these rows.

### Oak Acres: strongest concentrated audience

Focus on Grimes, Duval, Huey, Askew, Golfcrest and Pecan. Most candidate land is
in Oak Acres and its extension. Of 288 residential/vacant appraisal accounts in
the square, 96 distinct candidate owners mail within the square: 33.3 reachable
owner records per 100 accounts. This is the clearest match to a geographically
concentrated campaign aimed at local individual owners.

There are 107 distinct candidate owners with Houston mailing addresses, but only
96 located within this square. Use the latter figure when sizing a neighborhood
campaign. One estate site adds a separate family channel. No active city special
minimum-lot or special building-line overlay intersects this review pool.

### Houston Harbor / Liberty Heights: larger adjoining campaign territory

The three vertically adjoining squares provide repeated concentrations of
roughly 10,000-sq-ft holdings and same-owner assemblies. North streets include
Harbor, Eagle Pass, Force, Hillsboro, Victoria and Laredo; central streets include
Brownwood, Hershe, Abilene, Amarillo, Market and Greenville; south streets include
Tuck, Gonzales, San Angelo, Boyce and Corsicana.

The north and central squares have 8.3 and 8.5 resident candidate owners per 100
residential/vacant accounts, versus Oak Acres' 33.3. They offer more surrounding
territory to expand into, but broader coverage spends more impressions on
non-target households. These squares contain 11, 11 and 10 sites respectively
in city minimum-lot overlays; their numeric minimums do not exceed an equal half
of the site. Preserve the ordinance references and their SFR fields for the
property review.

### Forest Hill: the width correction matters

Focus on Alta Vista, Forest Hill Boulevard, Pasadena and Esperanza. Twenty-four
of 45 review sites have frontage below 95 ft. The old 100-ft shortcut would have
hidden much of this pocket's useful supply. Thirty-six of 44 distinct owners mail
within the square, and all 44 have Houston mailing addresses. One estate and one
trust site are counted separately from the individual-owner totals. No active
city special minimum-lot or special building-line overlay intersects this pool.

## Pockets that move down after looking beyond lot area

| Pocket | Initial individual sites / resident owners | Mapped issue | Sites / resident owners after transit, larger-minimum-lot and SFHA checks |
|---|---:|---|---:|
| Riverside Terrace south, Charleston / Rio Vista / Parkwood | 83 / 67 | 57 sites have a minimum lot size larger than an equal half | 26 / 19 |
| Timber Crest / Riverside, Binz / Prospect / MacGregor | 76 / 63 | 50 have that minimum-lot conflict; 9 intersect SFHA | 24 / 18 |
| Lindale Park, Irvington / Sue / Milwaukee | 76 / 59 | 40 minimum-lot conflicts; median assessed land value $45.30/sq ft | 36 / 27 |

These checks change campaign sequencing; existing legal parcels and alternate
configurations remain available for individual review. The low assessed prices
in the Valencia Park/Kashmere Gardens comparison squares come with pervasive
mapped flood exposure: all 54 and 56 individual review sites respectively are
in SFHA. Keep that supply visible, but it is a weaker opening campaign for a
quick, repeatable buyer submission.

## What the full pass establishes

- Read all **21,722 exported candidate sites**, preserving every HCAD ID and
  assembly membership. Street-facing edges were measured for 20,110; 1,612 remain
  in the measurement queue.
- Used the countywide HCAD account/centroid join to resolve owner mailing
  locations and count **181,840 accounts inside the exported Loop boundary**.
  The ranking spans **410 squares**. Western pockets remain in the full result;
  for example, the resident-owner count alone ranks a River Oaks square first.
- Individual, estate and trust holdings have separate counts. Owners are
  deduplicated by normalized name plus mailing address. Matching the subject
  address, or resolving a mailing address within the square, establishes local
  mailing location. An ambiguous address remains unresolved. Mailing location
  is the residence indicator used here.
- Rectangularity is polygon area divided by minimum bounding-rectangle area,
  at least 0.85. This is separate from frontage. No building-footprint minimum is
  assumed: the next input is the buyer's dimensioned two-story duplex plan.
- There is no upper site-area cutoff. Sites above 20,000 sq ft have separate
  counts: 10 in Oak Acres, 0/3/2 in Harbor north/central/south, and 7 in Forest Hill.
- Active city minimum-lot and building-line overlays were intersected with the
  actual candidate geometry. The dataset contains 1,618 sites touched by active
  minimum-lot polygons and 227 touched by active special building-line polygons.
  Private deed restrictions are outside these city layers.
- **21,627 sites (99.6%)** are within 2,640 ft of an active boarding stop using
  straight-line distance from the site centroid. The GTFS feed is
  `August2026IVOMS_20261008`, valid August 30, 2026–January 23, 2027. Services active
  during October 26–November 1 were resolved from calendars and exceptions;
  8,796 boarding stops serve the selected bus/rail trips. Walking routes have not
  been calculated. Transit therefore adds little geographic discrimination to
  this inventory.

The transferred assembly generator still needs two improvements: shared-edge
validation instead of one-foot proximity alone, and combinations that join a
small parcel to an already-10,000-sq-ft parcel. This pass improves and ranks the
entire existing export; those additional assemblies will expand the inventory.

## How to use this ranking

Drive the three leading areas and record block condition, visible redevelopment,
the walk to transit and the buyer's likely arrival route. Select campaign
boundaries from that field evidence and resident-owner concentration. Keep the
seller message about buying their property; the redevelopment strategy and
$20/sq-ft exit ceiling stay in our acquisition analysis.

For the agent channel, intersect qualifying accounts with expired, withdrawn and
stale listings. For geographic owner campaigns, track inbound leads back to
these exact accounts and cells so spend can be compared by reachable owner and
usable site, rather than total neighborhood population.

## Files and reproduction

Private results in the parent workspace:

- `outputs/frontage-2026-10-26/sites_with_frontage.json`: all original sites plus
  frontage/access, owner location, city overlays and transit fields.
- `outputs/frontage-2026-10-26/campaign_pockets.json`: all 410 cells, counts,
  streets, map centers, transit metadata and estate/trust counts.
- `outputs/frontage-2026-10-26/summary.json`: frontage totals and benchmark Drew.

Run the parent workspace scripts in this order after caching the public sources:
`frontage_full_study.py`, `rank_campaign_pockets.py`, `apply_layout_overlays.py`,
`apply_transit.py`, all under `research/`. They write derived outputs in the
workspace and open the original DuckDB read-only. Owner records stay out of Git.

Sources: [Houston minimum-lot/building-line program](https://www.houstontx.gov/planning/Min-Lot_Size-Min_Bldg_Line.html),
[city planning map service](https://mycity2.houstontx.gov/gisweb01/rest/services/HoustonMap/Planning_and_Development/MapServer),
[METRO developer portal](https://api-portal.ridemetro.org/),
[official GTFS download](https://metro.resourcespace.com/pages/download.php?ref=4835&ext=zip).

Route and arrival data provided by permission of METRO.
