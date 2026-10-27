# Project context

Read [docs/session-handoff.md](docs/session-handoff.md) first for the current
session boundary, connection state, saved artifacts and next authorized action.

Read [docs/buyer-mandate.md](docs/buyer-mandate.md) and
[docs/direction.md](docs/direction.md) before changing acquisition filters, scoring,
data exports, or field/desktop workflows. Use [README.md](README.md) for the current
runtime and build entry points.

- The buyer mandate records the user's 2026-10-25 clarification. Later explicit
  user instructions take precedence; older "locked buy box" passages are historical.
- Distinguish confirmed buyer requirements, working assumptions, recommended
  workflows, and implemented features. Unknown feasibility is not a pass.
- Preserve individual HCAD account IDs and assembly membership. Addresses are
  display values, and an appraisal account is not proof of a legal lot.
- Reuse and audit the existing PC research before rebuilding its inventory.
  Generated data is excluded from this repository; documentation counts do not
  prove that the data is present, fresh, or complete under the latest mandate.
- Keep owner/contact data, generated private assets, and signing credentials out
  of Git. Preserve the existing Android signing identity for upgrades.
- Update the relevant planning/history documents when decisions or implementation
  status change so desktop and Joying work retain the same context.
