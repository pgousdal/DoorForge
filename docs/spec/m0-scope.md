# M0 scope and acceptance criteria

## Goal

Create a reproducible evidence base and a repository from which the ABBS adapter
can be implemented without inventing undocumented behavior.

## Acceptance criteria

- [x] Source archive identified by cryptographic hash.
- [x] Complete header-level inventory generated.
- [x] Door-related files identified.
- [x] ABBS script and ARexx surfaces identified.
- [x] Multi-node implications recorded.
- [x] Proprietary files excluded from the repository.
- [x] Provisional session model written.
- [x] Host-side Hello Door executable provided.
- [x] Automated M0 checks provided.
- [ ] Original compressed door documentation extracted and reviewed.
- [ ] Live ABBS invocation traced.

The final two items are intentional M1 prerequisites and prevent M0 from
overclaiming protocol support.
