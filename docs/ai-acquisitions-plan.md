# AI-assisted acquisitions ecosystem plan

Status: planning only; not yet implemented.

Related plan: [`sync-navigation-plan.md`](sync-navigation-plan.md).

## Objective

Use the parcel platform, Joying driving application, future desktop viewer, and
a true CRM as one coordinated acquisitions system. The initial wholesale buy box
is:

- 5,000–15,000 sq ft parcels;
- unimproved land or an acceptable teardown;
- FEMA Zone X;
- inside Loop 610;
- near a bus stop;
- initially concentrated in Third Ward and Second Ward;
- both direct-to-seller (D2S) and direct-to-agent (D2A) acquisition lanes;
- off-market, FSBO, expired, and stale on-market opportunities.

If those areas do not produce enough viable leads, the system should support a
measured pivot toward inside-610 areas with less expensive land.

## Product boundaries

The parcel platform should be the source of truth for:

- parcel identity, geometry, and geospatial facts;
- buy-box eligibility and scoring evidence;
- saved parcels, scouting routes, and field observations;
- listing/property research associated with a parcel;
- AI recommendations and their supporting evidence.

The CRM should be the source of truth for:

- people, agents, owners, and organizations;
- phone, email, mail, and conversation history;
- campaigns, tasks, appointments, and reminders;
- opportunity/deal stage, offers, contracts, and dispositions.

Both systems should share stable parcel and opportunity IDs and communicate
through APIs and webhooks. Avoid maintaining competing copies of CRM activities.

## Configurable buy boxes

Do not hard-code Third Ward or Second Ward rules into either user interface.
Store versioned strategy profiles with:

```text
name and version
active geography/boundary
minimum and maximum parcel size
allowed improvements/teardown rules
allowed flood zones
maximum distance to transit
land-price or offer constraints
D2S/D2A source rules
ranking weights
```

For every parcel, keep separate outputs:

- **Eligibility:** whether all hard requirements pass;
- **Fit:** how closely it matches preferences inside the hard box;
- **Motivation:** evidence suggesting a seller may transact;
- **Economics:** expected acquisition and assignment potential;
- **Confidence:** freshness and reliability of the evidence;
- **Explanation:** exact facts and sources behind each result.

AI must not silently override hard eligibility rules. Unknown data should remain
unknown rather than being treated as a pass.

## Unified property opportunity

A parcel is the stable physical entity. It can have multiple acquisition
opportunities over time and in different lanes:

```text
Parcel
  ├─ facts, geometry, zoning, flood, transit
  ├─ ownership history
  ├─ listings and listing events
  ├─ scouting observations and photos
  └─ Opportunities
       ├─ D2S owner outreach
       ├─ D2A active/stale listing
       └─ later renewed opportunity
```

D2S and D2A remain distinct workflows but refer to the same parcel. A listing
should not erase prior owner outreach, and an expired listing can transition
into a D2S opportunity with its history intact.

## Valuable AI capabilities

### Research and prioritization

Use deterministic filters first, then AI to summarize and rank evidence such as:

- probable vacancy or teardown condition;
- stale, expired, withdrawn, or repeatedly relisted property;
- FSBO evidence;
- absentee/entity ownership and length of ownership;
- permit, demolition, and construction history;
- nearby development activity;
- asking price and land-price comparisons;
- field observations and previous outreach results.

Every generated claim should cite an underlying source record. Example:

> High-priority D2S candidate: 9,800 sq ft, Zone X, 0.12 miles from a bus stop,
> absentee owner, held 17 years, and no recent permits. Field verification is
> still required.

### Scouting and driving for dollars

The Joying application can eventually act as a field assistant:

- load a prioritized route from the desktop;
- save, reject, defer, or flag the current parcel;
- capture structured observations with large driving-safe controls;
- record a voice note and extract structured facts later;
- associate phone-companion photos with the parcel;
- classify visible vacancy, damage, deferred maintenance, overgrowth, boarded
  openings, demolition potential, or active construction;
- OCR addresses and FSBO signs;
- ask only for important missing observations;
- retain explicit rejection reasons.

Photo and language processing should occur asynchronously and must never block
GPS/navigation rendering.

### D2S assistance

AI may:

- consolidate and summarize ownership/entity history;
- identify missing research and inconsistent source records;
- create a human-reviewable owner/property brief;
- recommend a next channel or CRM task;
- draft letters, email, call preparation, and follow-up language;
- convert call notes/transcripts into motivation, timing, disposition, and tasks.

Contact data and outbound activity remain in the CRM. AI-generated messages and
offers require human approval.

### D2A assistance

AI may:

- monitor days on market, price reductions, relists, withdrawals, and expiry;
- summarize listing history and agent interactions;
- compare ask price to parcel and teardown economics;
- prepare an agent call brief and questions;
- draft inquiry/offer language for review;
- recommend follow-up when listing events occur.

Use authorized MLS/listing feeds and respect provider terms rather than relying
on brittle or prohibited scraping.

### Desktop work queue

A desktop session should support requests such as:

> Show today's 25 best unworked opportunities inside 610, split into D2S and
> D2A, excluding parcels visited in the previous 60 days.

The system should explain each result, identify missing facts, group nearby
properties, generate a scouting route, synchronize it to the Joying, and create
appropriate CRM tasks.

After a drive, an AI-generated review can summarize parcels visited, saves and
rejections, observations, photos, CRM updates, recommended outreach, and open
research tasks.

## Geographic expansion

Evaluate potential expansion areas with transparent metrics:

- count and density of eligible parcels;
- median land price per square foot;
- estimated wholesale spread;
- listing and buyer competition;
- development and permit activity;
- transit coverage;
- D2S/D2A response and conversion rates;
- scouting yield and common rejection reasons.

Example question:

> Which inside-610 areas have at least 100 eligible parcels and materially lower
> land prices than Third Ward?

Do not use protected-class attributes or demographic proxies to target housing
outreach or rank opportunities.

## Feedback and learning

Capture the complete outcome funnel:

```text
identified → reviewed → routed → scouted → saved/rejected → contacted
→ response → appointment → offer → contract → assigned/closed/lost
```

Use controlled reason codes as well as notes, including:

- lot too small or wrong configuration;
- flood or transit failure;
- structure too valuable / poor teardown;
- asking price or seller expectation too high;
- no owner contact;
- seller not motivated;
- title/legal issue;
- insufficient buyer demand;
- already under contract.

Begin with transparent rules and weighted scoring. After enough labeled outcomes
exist, train a conventional ranking/propensity model and validate it against
held-out outcomes. LLMs should explain and structure evidence, not serve as an
unverifiable numerical scoring engine.

## Technical AI architecture

```text
Joying app / desktop viewer / CRM
                 |
          shared backend API
             ├─ Postgres + PostGIS
             ├─ sync and authentication
             ├─ routing service
             ├─ background job queue
             ├─ model-provider adapter
             ├─ evidence/citation service
             └─ audit and evaluation logs
```

AI and routing credentials belong only on the backend. Store the model, prompt
version, source references, output, reviewer action, and eventual outcome for
each material recommendation. Keep verified facts distinct from inferred facts.
Minimize owner/contact data sent to external model providers.

## Suggested delivery sequence

1. Shared parcel saving and PC/Joying synchronization.
2. Stable parcel, owner, listing, opportunity, and activity identifiers.
3. CRM integration contract and field ownership rules.
4. Mobile observations, rejection reasons, and route workflow.
5. Configurable buy-box engine with evidence-backed explanations.
6. Voice-note extraction and post-drive desktop summaries.
7. Research briefs and next-best-action suggestions.
8. Human-reviewed outreach drafting.
9. Ordered route synchronization and basic next-stop navigation.
10. Outcome-trained ranking and geographic expansion analysis.
11. Guided maneuvers, rerouting, and voice navigation.

The highest-value early AI features are expected to be voice-note structuring,
research summaries, daily prioritization, and post-drive CRM updates. Autonomous
outreach and learned scoring should wait until the underlying workflow produces
clean, consistent outcome data.

## Decisions for desktop planning

- Which CRM will be authoritative?
- Which MLS/listing and contact-data sources are licensed and available?
- What exactly qualifies as “near” a bus stop?
- How should teardown acceptability and land economics be calculated?
- Which statuses, rejection reasons, and campaign channels are required first?
- Will field photos come from the Joying, a paired phone, or both?
- Which outreach steps always require approval?
- What volume and route-size limits should navigation support?
