# Buyer mandate and sourcing context

Updated 2026-10-26 from the user's direct clarifications in the project conversation.
This is the current source of truth for acquisition criteria. It supersedes older
buy-box language in the project history and planning documents. Later explicit
user instructions take precedence. It records buyer requirements and separates
them from proposed workflows and matters still needing confirmation.

## Buyer and development model

The buyers are an out-of-state team, active in Houston for less than a year, with
an early-stage fund still raising capital. The earlier mid-nine-figure figure is
their fundraising ambition. They are banking land faster than they can build and
have completed several Houston projects. They use equity partners and separate
project SPVs, so one LLC will not identify their entire portfolio. They fly in to
inspect sites, blocks and transit before closing.

Our role is a local acquisition partner seeking quick assignments or double
closes. We are sourcing land for their underwriting, rather than investing in the
fund's operating thesis.

Their standard project is:

1. Acquire at least 10,000 contiguous sq ft with appropriate dimensions.
2. For the standard 10,000-sq-ft site, establish two equal 5,000-sq-ft parcels.
3. Build one duplex on each parcel.
4. Each side of each duplex has five bedrooms and five bathrooms.

The result is **two duplexes, four dwelling units, 20 bedrooms, and 20 bathrooms**,
intended for PadSplit rentals. The buyers may sell one duplex and retain the other.
The prior shorthand "two 10/10 structures" refers to two duplex buildings; it does
not mean 20 separate dwelling units.

## Confirmed criteria

| Criterion | Current mandate |
|---|---|
| Geography | Anywhere inside Loop 610, provided the project checks out. |
| Transit | Within 0.5 mile of a public bus stop or METRORail stop/station. |
| Primary site | At least 10,000 contiguous sq ft with dimensions supporting the two-parcel duplex project. |
| Smaller-site exception | A roughly 5,000-sq-ft site may be considered if it is a great deal; it is not automatically equivalent to the primary project. |
| Improvements | Cleared land or land with an existing house/improvements can qualify. |
| Price | Up to $20 per land sq ft when site-specific diligence and project economics check out. |
| Feasibility | Deed restrictions, local approval friction, utilities, layout, and other development constraints must work for the actual project. |
| Sourcing | Off-market, FSBO, expired/withdrawn, and stale on-market opportunities; D2S and D2A lanes. |

The buyers' underwriting treats projected cash flow equally across locations
meeting their Loop/transit criteria. This is their stated underwriting policy,
not an independently established claim that operating results are identical.
Third, Second, Fifth Ward, and other inside-Loop neighborhoods are all eligible.
Their soft preference is shorter commutes to the Medical Center and UH/TSU.
Third, Second and Fifth Ward, Northside and Near Northside are practical sourcing
areas; the west side is likely harder to acquire at the required basis. These
preferences guide campaign sequencing while the entire Loop remains eligible.

## Earlier assumptions and unresolved details

- **Third/Second Ward first:** superseded as a buyer preference or geographic gate.
  Existing context-map coverage in those wards is a data-coverage fact, not the mandate.
- **5,000-15,000 sq ft as one uniform range:** superseded. Keep the primary project
  and smaller-site exception distinct. No 15,000-sq-ft hard ceiling was confirmed.
  Larger sites need a buyer-approved layout and price; do not assume unlimited
  linear value at $20/sq ft.
- **Zone X only:** an earlier project screening assumption, not reconfirmed as a
  buyer hard requirement. Preserve flood evidence and flag the policy for buyer
  confirmation. This clarification neither clears non-X sites nor silently
  authorizes a change to an existing flood filter.
- **Transit measurement:** the 0.5-mile threshold and bus/rail eligibility are
  confirmed; straight-line versus walking-route distance is not. Record the
  measurement method, stop ID, service date, and source. A radius can support
  discovery but cannot settle final acceptance until the convention is agreed.
- **Dimensions:** no 100-ft frontage requirement. Use the configuration and
  building-envelope approach in [site-layout-screen.md](site-layout-screen.md).
  The user observed ample spacing at Drew and tighter spacing at other projects.
  The original calibration target was the Drew duplex structures. On October 26,
  the user declined a city records request and explicitly authorized reasonable
  duplex dimensions instead. Use two-story 40-by-45-ft and 30-by-60-ft working
  footprints, each providing 1,800 gross sq ft per dwelling, and fit buildings,
  clearance, eight parking spaces and pedestrian access within the two child
  polygons. Do not require Drew-sized lots or reproduce its generous spacing.
  A 50-ft-frontage by 200-ft-deep site is outside the primary side-by-side search.
  Narrow sites stay in a separate adjoining-frontage/alternative-layout inventory;
  area alone must never put them in the primary target map or campaign count.
  Drew's actual structure dimensions remain unknown; the approximately
  104.5-by-98-ft measurement describes its land. The working footprints are
  supported by published co-living plans and are now implemented in the two-pocket
  maps. Corners, through-street sites and major-road frontages retain a separate
  access-layout queue.
  The former 66-ft access threshold no longer grants a product-fit pass.
- **Fee and cost treatment:** confirm whether the buyer's ceiling includes the
  assignment fee, closing costs, demolition, replatting, and infrastructure work.
  Until clarified, budget our assignment inside the buyer's acquisition price;
  label this as a working assumption rather than a confirmed fee agreement.

## Acquisition economics

At the stated ceiling, 10,000 sq ft implies **$200,000** for a qualifying site.
That is a conditional ceiling, not an appraisal, standing offer, or guaranteed exit.
Use the buyer's approved price for the specific site to calculate:

```text
maximum seller contract price
  = site-specific buyer acquisition price
  - assignment fee
  - costs and contingency borne by us
```

For illustration only: $200,000 buyer price minus a $25,000 assignment and $5,000
of our costs/reserve leaves $170,000 for the seller contract. These fee/reserve
amounts are not agreed targets. Apply buyer-required site-cost adjustments once;
do not deduct the same demolition or utility expense twice. HCAD assessed land
values and historical operator estimates are not verified sale prices.

## Recommended sourcing workflow

Build on the existing inside-610 parcel, adjoining-owner, and co-living research
documented in [project-history.md](project-history.md). The full study is now
available at `C:\Houston_Infill\study`, including the 9-GB DuckDB database and
21,722-site export. Audit its older filters before reusing its priorities. The older six-neighborhood
distress inventory in the PC workspace is supplemental, not the master geography.

1. **Build the eligible-site inventory:** combine individual parcels and genuinely
   contiguous assemblies, then screen location, transit, size, and prototype fit.
   Preserve constituent HCAD IDs and distinguish tax accounts from legal lots.
2. **Prioritize acquisition opportunities:** stale listings, houses on double lots,
   same-owner adjoining parcels, FSBOs, and stalled developments. Search homes and
   duplexes as well as land. Seller motivation is separate from project feasibility.
3. **Verify what is offered:** price basis, exact legal lots/accounts, included area,
   current status, and whether a displayed price covers one lot or the entire site.
   The 6019 England St investigation exposed per-lot pricing alongside project-level
   area; it is a data-quality lesson, not a completed title or feasibility review.
4. **Check project constraints:** survey/layout, restrictions and plat notes, split
   approval, municipality, local friction, intended PadSplit use, access, flood and
   drainage, utility capacity/connections, improvements, title, and delivery costs.
   A duplex approval alone does not establish approval for the intended operation.
5. **Submit a consistent buyer packet:** geometry and proposed split, transit proof,
   photos, evidence with dates, open issues, seller price, assignment, and proposed
   buyer price. Record acceptance/rejection and reasons to improve future screening.

Research across the whole Loop from the outset. Choose outreach and driving batches
using actual qualifying supply, price/spread, evidence quality, and travel efficiency.
Operational batching must not become an undocumented neighborhood exclusion.

Outreach should emphasize individual owners and families holding suitable sites.
Prioritize qualifying expired/withdrawn listings for the agent channel. Evaluate
affordable geographic campaigns where suitable sites and resident owners are
concentrated. Do not lead seller/agent conversations with the redevelopment upside
or the buyer's ceiling. Cold SMS, generic mail and a tiny 30-owner test are not the
user's chosen owner-acquisition strategy.

The October 26 quality refinement gives block-level rejection risk independent
weight. Repeated serious violence, observed threatening activity, surrounding
abandonment, dumping, a hostile transit walk and severe industrial/traffic
intrusion can stop a buyer tour despite a low price and good dimensions. Score
stacked access to UH, TSU, TMC and other anchors, and current acquisition-market
conditions separately from resident-owner concentration. Use
[quality-and-fit.md](quality-and-fit.md) for the implemented desktop screen and
the field-observation rubric. A neighborhood name alone does not decide a site.

The subsequent [Third Ward correction](third-ward-opportunities-2026-10-26.md)
restores targeted acquisition near UH/TSU alongside concentrated campaigns
elsewhere. Resident-owner density and ownership category select outreach methods;
they cannot exclude locations or business-owned sites from buyer consideration.
Drew triggers the proposed crime-review rule on pre-purchase incidents, so that
rule routes inspection rather than predicting a failed visit or deleting a site.

The user added a secondary listed-property assemblage strategy: identify stale
on-market properties with workable asking-price economics, pursue adjoining
owners, and secure the listed property once the neighbor terms work. Preserve
this as a separate opportunistic lane; single-owner sites and existing same-owner
assemblies remain primary. The [map and strategy notes](third-ward-maps-and-listed-assemblages.md)
record the initial researched listings, adjacency rules and residual-neighbor
budget calculation. Asking price, seller willingness and contract control are
separate fields.

## Implementation state and next context to retain

The user selected Supabase and authorized the first cross-device workflow on
October 26. The repository now contains migrations, stable account/assembly IDs,
the full-Loop screening/import pipeline, a desktop workspace, native parcel cards,
saved lists and durable offline visit sync. Local integration tests and hosted/
Joying deployment are recorded separately in
[cross-device-workflow.md](cross-device-workflow.md).

The Canvas renderer remains in place. CRM, renderer migration and CI decisions
remain open. The earlier [campaign ranking](campaign-pockets-2026-10-26.md) is a
research snapshot; current site layouts come from versioned screening runs.
Private generated data, imagery, contacts and signing keys stay out of Git.
