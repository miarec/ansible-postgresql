# Phase 3 — Documentation, Metadata & Final Verification

## Goal
Update user-facing documentation and project metadata to reflect PostgreSQL 16/17 support, record the default version change, and run the full verification suite to confirm end-to-end stability.

## Scope
- README compatibility matrix, usage notes, and any changelog or role metadata (`meta/main.yml`) impacted by the new version support.
- Final Molecule regression spot checks and linting.
- No additional feature work; focused on communication and final validation.

## Tasks
- [x] Update `README.md` compatibility matrix to add columns for PostgreSQL 16 and 17, adjust default version references, and refresh instructions for Molecule env vars.
- [x] Review `meta/main.yml` or other metadata files for supported version declarations; update as needed. *(No changes required.)*
- [x] If a changelog or release notes document exists, add an entry summarizing the new version support and default change. *(No changelog maintained in repo.)*
- [x] Run comprehensive Molecule suites (default and TLS) with key distro/version combinations to ensure documentation reflects tested configurations.
- [x] Capture final verification evidence (command outputs, notes) for inclusion in Outcomes.

## Acceptance Criteria
- Documentation clearly states PostgreSQL 16/17 support and highlights the default version change to 17.
- Metadata files align with README claims (e.g., Galaxy support ranges).
- Final Molecule runs succeed for a representative subset (e.g., Ubuntu 24.04 + PG17 default scenario, Rocky Linux 9 + PG16 default scenario, TLS scenario with PG17).

## Edge Cases to Address
- README compatibility matrix must stay readable despite additional columns; ensure layout remains within standard width.
- If Galaxy metadata cannot express per-version support beyond major OS releases, document limitations explicitly.
- Should full Molecule matrix runs prove too time-consuming, capture rationale for sampling and instructions for on-demand full sweeps.

## Tests (Must be implemented in this phase)
- ✅ `uv run --python 3.12 molecule test`
- ✅ `uv run --python 3.12 molecule test -s tls`

## Verification Steps
- Execute documentation updates; lint markdown if tooling exists.
- Run the Molecule commands above; confirm all steps pass.
- Summarize results in plan `Progress` and `Outcomes` sections.
