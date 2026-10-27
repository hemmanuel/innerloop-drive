# Third Ward parcel maps and the secondary assemblage strategy

October 26, 2026. The primary acquisition strategy remains single-owner sites
and existing same-owner assemblies. The user requested a separate surface for
assembling a stale listed property with adjoining land owned by another seller.

**Current screen:** the user authorized reasonable duplex dimensions after
declining a city plans request. The maps now test 40-by-45-ft and 30-by-60-ft
two-story working footprints, each with two 1,800-gross-sq-ft dwellings. Buildings,
eight parking spaces and pedestrian paths must fit the actual child polygons.
See the [model, sources and reservations](site-layout-screen.md).

The current result is **13 front-access layouts**, **49 corner/through-street/major-road
access layouts to resolve**, and **13 other layout/geometry/owner cases** across
the same 75 source sites. All remain selectable. The old 51-site polygon-only
count is historical. 3531 Wentworth fails the footprint model because its
skewed sides constrain the buildings, not because every 74-ft frontage fails.

## Primary map

The map shows sourced HCAD parcel outlines, individual account boundaries inside
assemblies, Houston street centerlines and METRO stops. Select a site to inspect
area, street-facing span and depth, each equal-area half's frontage, ownership category, geometry route, serious-incident counts,
nearby residential/duplex permitting, assessed land value, transit access and
local owner mailing status. Map/satellite and Street View links open the location.

Map colors can show singles/assemblies, incident exposure, or working footprint.
The two pockets have a direct comparison table; no new blended score is invented.
The default view contains completed front-access layouts. Corners, through-street and major-road
sites have a dedicated group, followed by other layout and ownership cases. Gray background parcels provide block context. A bold line
marks the selected street face; a dashed line shows the equal-area cut. Passing
sites also show two buildings, eight parking stalls, side clearances and paths.

### Geographic correction from plotting the candidates

The original Drew/Tuam square contains 60 candidates but crosses I-45. Thirteen
records already carry other neighborhood labels; another two Gulf Freeway
properties are north/east of I-45 despite the study's Third Ward label. The primary
map therefore contains **45 Drew/Tuam source sites and 30 Rosedale/Arbor source sites**, or **75**
total, of which **13** appear in the default front-access view. The fifteen surrounding records remain in the source inventory. No buyer
geographic exclusion is implied by focusing this map on Third Ward proper.

The map builder uses the study's Third Ward classification and the south/west
side of the sourced I-45 highway centerlines for this two-pocket display. The
previous 312-site count describes eight operational grid cells, not a ward census.

| Comparison | Rosedale / Arbor | Drew / Tuam |
|---|---:|---:|
| Source sites, all layouts | 30 | 45 |
| Assembly candidates | 1 | 21 |
| Assemblies with matching current owner names | 1 | 20 |
| Completed front-access layouts | 5 | 8 |
| Same-owner assemblies with front-access layouts | 0 | 5 |
| Corner / through-street / major-road layouts to resolve | 14 | 35 |
| Other layout / geometry / owner cases | 11 | 2 |
| Individual / estate / trust front-access fits | 4 | 2 |
| Resident individual owners, front-access fits | 2 | 0 |
| Median serious incidents within 660 ft, individual front-access fits | 1.5 | 13.5 |
| Repeated-violence flags, same pool | 0 / 4 | 2 / 2 |
| UH / TSU / TMC modeled walk/transit minutes | 12 / 4 / 25 | 15 / 20 / 35 |
| Median HCAD land assessment per sq ft, individual front-access fits | $20.20 | $33.25 |

Rosedale leads the individual-owner search and the available block evidence.
The 2702/2706 Scott assembly has an owner-name mismatch in the current account
join and is separately colored for owner-match review; it is not counted among
the 21 assemblies with matching names across both pockets.
Drew/Tuam provides substantially more existing assemblies and the known buyer
benchmark. Crime review remains an inspection task, as established by Drew's
purchase history. Field observations have not been collected.

The road data uses both `HIGHWAY` and `FREEWAY`. The earlier freeway-distance
enrichment only selected `FREEWAY`, missing I-45 segments. Corrected distances
for 7,932 of 21,722 source sites and synchronized the private queues. The prior
five-pocket composite scores are explicitly historical. Frontage code now excludes
`HIGHWAY`, `HOV`, `FREEWAY` and `RAMP` centerlines as sources of direct lot access;
ordinary frontage roads remain distinct.

### Historical polygon screen before building placement

The original default map mixed 56 geometry-screened sites with 19 already flagged
for other layouts. Auditing the actual polygons removed five more from that pool:
2601 Callie, 3523 Hadley, the 3429 McGowen/2510 Canfield assembly, the 2303–2309
Scott assembly, and 3535 Wentworth. The first four are thin strips with a long
street edge; Wentworth's equal-area cut leaves one street-facing span below 33 ft.

The audit measures a continuous face rather than summing separate street edges,
follows the parcel depth axis when splitting skewed lots, and reports each half's
frontage. That earlier screen kept 3723 Rosedale at about 70 by 192 ft, with 35-ft
child frontages. It does not fit the new working building layouts. Drew's combined benchmark measures about 105 by 98 ft.
The 50-by-200-ft through-site assemblies at McIlhenny/Hadley and McIlhenny/Bremond
remain outside the primary view. The full source inventory remains available.

## Secondary map: listed anchor plus adjoining owners

This is an opportunistic sourcing lane. Start with a stale listing whose price
could support a combined deal. Work the adjoining owner first; once their terms
work, secure the listed property and deliver the assemblage to the developer.
Track the listed seller's actual willingness and current availability rather
than treating a public ask as a commitment to accept later.

The initial surface contains **six researched listing anchors and 30 combinations**
of one or two adjoining parcels. Four anchors have active public listing evidence;
two are pending/under contract and are visibly retained as reference cases.
This is a researched seed set, not a complete MLS inventory.

Adjacency requires at least 20 ft of overlapping boundary with no more than a
one-foot GIS gap. Corner-only contact, opposite sides of a road and substantial
polygon overlaps are excluded. Each combination retains constituent account IDs,
additional owner-group count, combined area, street frontage, geometry/access
route, known additional listing asks and unpriced land area. Source outlines are
shown individually; combined calculations snap GIS gaps up to one foot.

The editable calculation is:

```text
maximum price for unpriced adjoining land
  = combined land area × entered buyer price per sq ft
  − entered listed-anchor price
  − asks of any other selected listed parcels
  − our profit and costs reserve
```

The initial $30,000 reserve is an editable scenario, not an agreed fee. The
calculator retains larger and alternative-layout combinations and labels the
geometry route. It suppresses buyer-exit budgets for combinations outside the
completed front-access pool, including corner/through-street cases and rear neighbors that create 50-by-200-ft sites.
For side-by-side combinations it shows the effect of the entered linear buyer-price scenario
rather than assigning a buyer approval to larger tracts.

Six of the 30 combinations fit the front-access model: three alternatives around
3212 McIlhenny and three around the unavailable 3514 McIlhenny anchor. Twelve
need corner/through-street access layouts, ten are below 10,000 sq ft, and two
fail the tested building/parking arrangement.

### Listing economics and findings

- **3212 McIlhenny:** active public listing at $159,000. Either 3214 or 3206
  McIlhenny adds 5,000 sq ft and creates about 100 ft of combined street frontage.
  At a $200,000 buyer price, $41,000 remains before our reserve; the $30,000
  scenario leaves only **$11,000 ($2.20/sq ft)** for that neighbor. The geometry
  works much more easily than the economics. Adding both neighbors gives a
  15,000-sq-ft scenario with two additional owners.
- **3221 Drew:** $205,000 ask already exceeds the entire $200,000 ceiling for
  pairing it with 3225 Drew into 10,000 sq ft. Larger combinations are shown
  separately. The rear 3232 Dennis property creates an alternate-layout shape.
- **2604 Canfield + 3430 McGowen + 3426 McGowen:** reaches 10,000 sq ft, but the
  two listed asks alone total $241,900. Both asks remain recorded. This corner assembly is in the access-layout queue,
  so the current map withholds its acquisition-budget output.
- **3461 Drew:** pending; the older $175,000 active results are stale.
- **3514 McIlhenny:** the latest HAR agent page shows $150,000 under contract;
  older property pages still show $200,000 active.

Relisting history is retained separately from current-listing age. For example,
3212 McIlhenny was marketed in February 2025 before its August 2026 relisting;
3430 McGowen's October 2026 relisting follows marketing in March 2025. A reset DOM
must not hide that history.

Sources checked October 26:
[3212 McIlhenny](https://www.har.com/homedetail/3212-mcilhenny-st-houston-tx-77004/3008982),
[its listing history](https://www.redfin.com/TX/Houston/3212-McIlhenny-St-77004/home/29764314),
[3221 Drew](https://www.har.com/homedetail/3221-drew-st-houston-tx-77004/3010100),
[2604 Canfield](https://www.har.com/homedetail/2604-canfield-st-houston-tx-77004/11012683),
[3430 McGowen](https://www.har.com/homedetail/3430-mcgowen-st-houston-tx-77004/17441923),
[3461 Drew](https://www.redfin.com/TX/Houston/3461-Drew-St-77004/home/29687667),
[3514 McIlhenny agent page](https://www.har.com/isaigha-mcneil/agent_isaigham).

## Implementation and next coverage

Private inputs/outputs are in the parent workspace:

- `research/third_ward_listing_seeds.json`: dated listing evidence and source links.
- `research/build_third_ward_maps.py`: parcel matching, map scope, adjacency,
  one/two-neighbor combinations and geometry calculations.
- `research/site_shape_audit.py` and `test_site_shape_audit.py`: continuous
  frontage, skew-aware equal-area splits, dimensions and geometry routing.
- `research/duplex_footprint_screen.py` and `test_duplex_footprint_screen.py`:
  rigid building placement, parking, walks, clearance and frontage-access scenarios.
- `research/map-core.js` and `third-ward-*.template.html`: interactive maps.
- `research/render_third_ward_maps.py`: creates the two inline map fragments.
- `outputs/third-ward-map-2026-10-26/map_data.json`: data underlying both maps.
- `research/check_third_ward_maps.cjs`: browser interaction and layout checks.

Future listing coverage should retain MLS ID, account mapping, source/update date,
status, latest listing date, prior marketing episodes, reductions and asking price.
Join that feed to boundary adjacency and owner groups; prioritize combinations
with useful frontage, enough unpriced-neighbor budget, few additional sellers,
and a workable block. Include houses and duplexes as well as vacant-land listings.
No new subscription, automated listing feed, outreach or purchase was initiated.
