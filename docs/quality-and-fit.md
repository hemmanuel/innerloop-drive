# Quality, buyer fit and block rejection risk

October 26, 2026. Applies to the five pockets in the initial campaign shortlist.

**Later correction:** these five scores compare an audience-density shortlist;
Third Ward was never scored alongside them. They must not decide the full
acquisition geography. The [Third Ward analysis](third-ward-opportunities-2026-10-26.md)
adds eight UH/TSU pockets and demonstrates that Drew itself triggers the numeric
crime-review rule using incidents before the reported purchase. Preserve crime
flags as inspection tasks, not automatic exclusions. The counts and v1 scores
below remain available for campaign planning; targeted Third Ward sourcing is
now part of the first acquisition wave.

The [parcel-map pass](third-ward-maps-and-listed-assemblages.md) also corrected
highway proximity: the street source labels I-45 segments `HIGHWAY`, not only
`FREEWAY`. The site evidence is updated; the original composite scores below
remain historical and have not been recalibrated.

**For concentrated geographic campaigns, lead with Oak Acres and Forest Hill. Move Houston Harbor north below its central
and southern pockets.** Treat repeated serious violence and visible street
conditions as property-level decisions that can stop a buyer tour regardless of
price or commute. The original resident-owner ranking is retained separately.

## Updated shortlist

Scores are desktop prioritization indices. Actual street disorder, building
condition, lighting and the transit walk remain field inputs with veto power.

| Pocket | Quality & fit / 100 | Repeated-violence review sites | Initial individual-site pool | First field-pass sites after violence, mapped minimum-lot and flood checks |
|---|---:|---:|---:|---:|
| [Oak Acres / Extension](https://www.google.com/maps/search/?api=1&query=29.703192,-95.308233) | **79** | 7 | 119 | **112** |
| [Forest Hill](https://www.google.com/maps/search/?api=1&query=29.724732,-95.299132) | **71** | 0 | 45 | **44** |
| [Houston Harbor / Liberty Heights central](https://www.google.com/maps/search/?api=1&query=29.775527,-95.297288) | **67** | 11 | 80 | **69** |
| [Houston Harbor / Liberty Heights south](https://www.google.com/maps/search/?api=1&query=29.768271,-95.297552) | **67** | 8 | 58 | **50** |
| [Houston Harbor / Liberty Heights north](https://www.google.com/maps/search/?api=1&query=29.782783,-95.297025) | **60** | 31 | 92 | **61** |

Central and south are effectively tied. Central has more inventory; south has
more residential surroundings and somewhat better geographic access. This is a
field sequence, not a reason to reject the other 61 Harbor-north sites.

## Quantifying the block problem

The first pass uses HPD's July 1, 2025–June 30, 2026 data, the latest complete
twelve-month window in the downloaded files. Count **distinct incident IDs** for
homicide, robbery and aggravated assault, rather than summing offense or victim
rows. Evaluate 660-ft and 1,320-ft circles around every candidate site. Keep
incidents at street, parking, store, restaurant, park and terminal premises
separate from residence and other premises.

The initial repeat-violence field-review trigger is:

- At least **3 incidents in 2 different months**, including at least **2 in public
  settings**, within 660 ft; **or**
- At least **6 incidents across 3 months** within 660 ft.

These are explicit acquisition-screening thresholds we selected. They identify
where to investigate recurrence before bringing the buyer. They do not assign
an acceptance probability. The counts describe the surroundings of a candidate,
not crimes attributed to its owner or occurring at that parcel.

| Pocket | Median incidents within 660 ft | Sites with zero | Sites triggering repeat review |
|---|---:|---:|---:|
| Oak Acres | 0 | 67 / 119 | 7 / 119 |
| Forest Hill | 1 | 12 / 45 | 0 / 45 |
| Harbor north | 2 | 4 / 92 | 31 / 92 |
| Harbor central | 2 | 13 / 80 | 11 / 80 |
| Harbor south | 2 | 4 / 58 | 8 / 58 |
| Grand Park / OST comparison square | **10** | **0 / 50** | **43 / 50** |

This materially separates blocks inside the broad areas the buyer accepts.
Grand Park's comparison square has substantial development activity—31 of its
50 sites have a duplex permit within 500 ft—yet the repeat-violence screen still
flags 43 sites. Nearby construction cannot erase that signal.

Specific field-review locations from the site results:

- **2900–3000 Golfcrest:** several Oak Acres candidates have 6–7 serious incidents
  within 660 ft, spanning 4–5 months. Review this edge independently from the
  pocket's low-exposure interior.
- **6900 Brownsville / Laredo / Hillsboro and 500 Port:** several Harbor-north
  candidates have 6 incidents within 660 ft across 5–6 months.
- **6900–7000 Tuck / Boyce:** several Harbor-south candidates have 5 incidents
  within 660 ft across 3 months.
- **6700 Cullen / Eastwood and 6500 Madrid:** Grand Park candidates have 19–23
  incidents within 660 ft. The Cullen example has 23 incidents across 11 months,
  including 17 in public settings. This is a much stronger reason to deprioritize a block than
  the neighborhood's name.

Source: [HPD monthly street-level data](https://www.houstontx.gov/police/cs/Monthly_Crime_Data_by_Street_and_Police_Beat.htm),
[2025 file](https://www.houstontx.gov/police/cs/xls/NIBRSPublicView2025.csv),
[2026 file](https://www.houstontx.gov/police/cs/xls/NIBRSPublicView2026.csv).
The 2026 download ends in June. The public 311 service returned a server error
on October 26; current dangerous-building and dumping counts are unpopulated.

## Field veto and a repeatable observation score

Visit the actual site, its block, the transit walk and the final arrival approach.
Record daytime and after-dark conditions. Score each item 0, 1 or 2 with a dated
observation and the affected segment:

| Item | 0 | 1 | 2 |
|---|---|---|---|
| Threatening activity | None observed | Repeated disorder that does not obstruct passage | Threats, harassment, obstruction or clearly observed active dealing |
| Surrounding structures | Maintained / occupied appearance | Isolated boarded or badly deteriorated structure | Multiple burned, open or abandoned structures dominating the visible block |
| Dumping / unmanaged lots | Clear | Isolated accumulation | Repeated bulk dumping or extensive unmanaged frontage |
| Transit approach | Usable walking surface, crossings and lighting | A specific gap or poor segment | Forced exposure to fast traffic, major unprotected crossing or threatening stop environment |
| Trucks / noise / incompatible uses | Residential-scale activity | Intermittent intrusion | Continuous heavy-truck movement, severe noise or an active yard dominating the frontage |

Sum the five observations to a 0–10 **field discomfort score**: 0–2 prioritizes
the site, 3–5 calls for a block/route-specific decision, and 6–10 removes it from
the first buyer-tour batch. A score of 2 for threatening activity is an immediate
tour veto. Record what was observed rather than inferring activity from people's
appearance. An isolated defect on the parcel being acquired is different from
conditions on neighboring properties the buyer cannot change.

The next calibration data are the buyer's actual accept/reject decisions, with
reasons. Keep these outcomes attached to sites so weights can be adjusted from
observed behavior. No acceptance percentage is estimated yet.

## Commute benefits must stack

The model includes UH, TSU, TMC, UHD/downtown, HCC Central and Rice. Geographic
distance and scheduled transit receive equal shares of the commute component.
The anchor weights are UH 25%, TSU 15%, TMC 30%, UHD 15%, HCC Central 10%, Rice 5%.

| Pocket center | UH miles | TSU miles | TMC miles | Modeled morning transit: UH / TSU / TMC / UHD |
|---|---:|---:|---:|---|
| Oak Acres | 2.3 | 3.3 | 5.5 | 39 / 42 / 55 / 49 min |
| Forest Hill | 2.6 | 3.6 | 6.1 | 50 / 52 / 65 / 51 min |
| Harbor central | 4.7 | 5.3 | 7.7 | 59 / 62 / 62 / 39 min |
| Harbor south | 4.3 | 4.9 | 7.4 | 59 / 62 / 62 / 39 min |
| Harbor north | 5.1 | 5.6 | 8.1 | 75 / 80 / 80 / 53 min |

Miles are straight-line distances. Transit results use METRO's current GTFS,
departing the square center at 6:30, 7:00 and 7:30 a.m. on October 26; the table
shows median modeled arrival times. The model allows up to two transfers, a
two-minute transfer boarding allowance, and walking at 3 mph on straight-line
links, with half-mile initial/final walks and 660-ft transfer walks. Actual road
crossings and walking paths are field inputs. These are not driving times.

Forest Hill has a stronger block profile than Harbor north, but it is not the
best transit commute story in the shortlist: its modeled trips to UH/TSU/TMC
often need two transfers. Oak Acres' representative trips to UH and TSU usually
need one. Harbor central/south favor UHD/downtown relative to the southern anchors.
Harbor north's half-mile-stop eligibility conceals a much weaker commute package.

Timber Crest/Riverside and Riverside south have substantially shorter access to
the southern anchors. Their mapped lot controls still block many proposed equal
splits. Keep a targeted exception list there rather than buying broad campaign
coverage based on location appeal alone.

Source: [METRO developer portal and GTFS](https://api-portal.ridemetro.org/).
Route and arrival data provided by permission of METRO.

## Price and inventory conditions

| Market context | Latest observed period | Median DOM | Listings with price reductions | Sale/list ratio | Study inventory months, June–August |
|---|---|---:|---:|---:|---:|
| Oak Acres: ZIP 77087 | September 2026 | 52 | 33.4% | 95.2% | 3.8 |
| Forest Hill: ZIP 77023 | August 2026 | 42 | 35.2% | 95.6% | 6.7 |
| Harbor: ZIP 77020 | September 2026 | 78 | 31.6% | 97.2% | 6.5 |

These are ZIP-wide residential indicators. The inventory and commute labels
remain separate from actual qualifying-land listings. Harbor offers more stale
listing opportunities; Oak Acres' low land basis is attractive but its inventory
was tighter in the study window.

Price examples make the difference concrete:

- **4011 Grimes, Oak Acres:** 15,000 sq ft, listed at $180,000 in May and sold that
  month. HAR shows a $215,000–$250,000 sold range, approximately **$14.33–$16.67 per
  land sq ft** including the house. It is a closed example, not available stock.
- **1921 Forest Hill Boulevard:** the HAR snapshot shows $197,500 for 10,027 sq ft,
  about **$19.70 per land sq ft**, marketed for lot value with a deteriorated house.
  That ask leaves only about $3,040 below a $20/sq-ft resale ceiling before any
  costs. The location may work; the asking price does not create our spread.
- **7005 Bonham, Liberty Heights:** the broker snapshot shows $93,500 for roughly
  5,000 sq ft, about **$18.70 per land sq ft**. This is smaller-site pricing context,
  not a 10,000-sq-ft assembly.

Sources: [77087 market](https://www.redfin.com/zipcode/77087/housing-market),
[77023 market](https://www.redfin.com/zipcode/77023/housing-market),
[77020 market](https://www.redfin.com/zipcode/77020/housing-market),
[Oak Acres sold ranges](https://www.har.com/pricetrends/oak-acres-realestate/3411),
[4011 Grimes history](https://www.redfin.com/TX/Houston/4011-Grimes-St-77087/home/29855630),
[1921 Forest Hill listing](https://www.har.com/homedetail/1921-forest-hill-blvd-houston-tx-77023/2960907?cid=tdelaney),
[7005 Bonham broker listing](https://www.coldwellbankerhomes.com/tx/houston/7005-bonham-st/pid_70980068/).

## Score construction and data files

`tools/quality_fit_policy.py` contains the editable scoring policy. Every component
is on a 0–100 scale before these weights:

- **30% block exposure:** 100 minus ten times median serious incidents, twice the
  90th-percentile count, and fifty times the share triggering repeat review;
  clamp the result to 0–100.
- **10% physical context:** 80 points times the residential share of nearby
  real-property accounts; up to 20 points for nearby new-residential permitting,
  reaching the maximum when half the candidate sites have such permits within
  500 ft. Deduct 25 points times each share within 330 ft of an industrial account
  centroid or freeway centerline. This captures land-use context, not observed
  exterior condition.
- **30% commute:** the anchor weights above, half geographic access and half
  scheduled transit. Geographic points decline linearly from 100 at one mile
  to zero at ten miles; transit points from 100 at twenty minutes to zero at
  ninety minutes.
- **20% acquisition conditions:** half assessed land-price context, declining
  from 100 points at $8/sq ft to zero at $30; half market negotiability, averaging
  DOM scaled to ninety days and price-cut share scaled to 50%. Actual seller
  terms replace these discovery inputs in a property underwriting.
- **10% usable inventory:** sites remaining after the first mapped lot-size,
  flood and repeated-violence checks, reaching 100 points at sixty sites.

The v1 inventory component discounts crime-flagged sites, so it understates
the full opportunity pool. Do not use it as buyer-eligible inventory; the newer
Third Ward queue preserves every site regardless of that flag. Separate campaign
reach from location fit in the next scoring revision rather than extending this
composite as an inside-Loop ranking.

The numeric score cannot override a field rejection. A repeat-violence flag puts
that property in the inspect-before-buyer-tour lane; a recorded field rejection
puts it in the reject-for-buyer-tour lane. No source sites are deleted.

The parent workspace retains private derived files:

- `outputs/frontage-2026-10-26/campaign_pockets.json`: five complete quality/fit
  historical scores, seventeen commute comparisons, and block-exposure summaries across the
  inventory's campaign cells.
- `outputs/frontage-2026-10-26/sites_with_frontage.json`: all 21,722 sites with
  local serious-incident counts, physical-context fields and review lanes.
- `outputs/frontage-2026-10-26/block_review_queue.json`: **444 sites** in the five
  shortlisted squares plus the Grand Park comparison square. There are 343 for
  first field reconnaissance, 100 requiring repeated-violence review, and one
  routed to flood-fit review. The queue retains stable site and account IDs.

Reproduce after the original frontage pipeline with `research/fetch_quality_sources.py`,
`quality_crime.py`, `quality_commutes.py`, `quality_context.py`, then
`score_quality_fit.py`. Run these sequentially because they enrich the same files.
The app's native data bundle has not been rebuilt.
