# Fake Namespace Allocation (test fixture)

Synthetic prefix table for scanner tests. Maps the fake fleet's repositories to
test prefixes. `fake-orphan` is deliberately **absent** so the scanner's
"ADR-bearing repository with no allocated prefix" hard-fail can be exercised.

| Prefix | Repository | Rationale |
|---|---|---|
| `FA-` | `fake-app` | test app repo |
| `FC-` | `fake-collide` | test repo with a planted ID collision |
| `FB-` | `fake-broken` | test repo with an unparseable ADR |
| `FCON-` | `fake-consolidated` | test repo with a consolidated registry |
