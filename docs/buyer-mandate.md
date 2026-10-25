# Buyer mandate and sourcing context

Updated 2026-10-25 from the user's direct clarification in the project conversation.
This is the current source of truth for acquisition criteria. It supersedes older
buy-box language in the project history and planning documents. Later explicit
user instructions take precedence. It records buyer requirements and separates
them from proposed workflows and matters still needing confirmation.

## Buyer and development model

The user reports that the buyers are an out-of-state team deploying a mid-nine-figure
fund, have recently completed successful Houston projects, and are actively
acquiring qualifying sites through wholesalers. These are user-provided business
facts, not independently verified fund information or a commitment on any one site.

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
Neighborhood names and campus proximity are descriptive research fields, not
additional buyer eligibility gates or preference scores.

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
- **Dimensions and delivery:** obtain accepted site plans and the buyer's frontage,
  depth, access, parking, utility, demolition, occupancy, and delivery requirements.
  Area alone does not establish that the prototype fits or can be permitted.
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
documented in [project-history.md](project-history.md). Retrieve and audit the
generated PC data before deciding what must be rebuilt. The older six-neighborhood
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

## Implementation state and next context to retain

The native app exists; the synchronized acquisitions workflow is planned. The native
binary currently omits stable account IDs, picks are baked in during builds, and
native parcel cards/saved lists, desktop sync, and CRM integration are not implemented.
Private generated data, imagery, contacts, and signing keys stay out of Git.

The recommended software direction remains the hybrid option in
[direction.md](direction.md): establish stable IDs and useful field/list workflows
while working leads, then improve sync and rendering. The user has not selected
the renderer migration, CRM, backend, or CI approach. This documentation update
does not change application filters, regenerate data, approve outreach, or implement
those proposed systems.
