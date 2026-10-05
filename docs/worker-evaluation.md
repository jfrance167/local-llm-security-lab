# Supervised Ruflo pilot

Ruflo and @claude-flow/cli 3.51.1 were pinned. VM-only npm installation used
`--ignore-scripts --omit=optional`; no host installation, automatic init,
instruction replacement or permanent integration occurred. Worker UID 2000,
empty credential environment, tested IPv4/IPv6 denial rules and exact-model
relay enforced local qwen3.5:2b routing. The MCP server advertised version 3.0.0,
despite installed package versions 3.51.1; package versions are authoritative
for the recorded installation, not the server's reported metadata.

| Actual Ruflo task | Duration reported | Input/output tokens | Review outcome |
|---|---:|---:|---|
| Supplied-evidence extraction | 5,689 ms | 186 / 58 | Correct completion flag and counts; `evaluated` was a boolean rather than the intended numeric count (brief was ambiguous about its type) |
| parse_eval initial draft | 6,557 ms | 333 / 857 | Useful structure; unwanted fences, accepts empty labels, lacks explicit nones range validation and exact-dict validation |
| Focused correction | 5,844 ms | 319 / 772 | Fixes labels/range; introduces default-zero missing counts and still ignores exact-dict requirement |

Raw code was inspected before testing. Eight initial independent tests had two
empty-label failures. Expanded review cases were added after defects were found;
the correction had six failures across eleven tests (five omitted-zero-count
cases and a dict-subclass case). Those additional cases are regression checks,
not untouched held-out evidence. The final Codex-reviewed parser/report wrapper
passes all 22 tests. Codex provided orchestration, security judgment, report
streaming/limits, final fixes, real probe execution, tests and documentation;
Ruflo did not independently complete the project.

Local-first drafting was honored. A refreshed startup audit verified the existing
free-only OmniRoute guardrails and fixed zero-price OpenRouter profiles. After
local code inadequacy, one explicit public North parser request through the
OmniRoute helper returned no text. No retries, fallback, paid API or remote Ruflo
request occurred. North supplied no shipped code. This is separate evidence
from Ruflo, and neither worker changes the main Codex model/allowance.

Dependency audit: full lockfile reports 24 moderate, 14 high and 1 critical entry;
omitting absent optional dependencies leaves 3 high entries, all related to
`toml` (<4.2.0 recursion and <4.1.2 prototype-pollution advisories) and its Ruflo/CLI
dependents. Counts are affected packages, not unique independently exploitable
vulnerabilities. Audit's proposed CLI downgrade was not automatically applied.
See [recursion advisory](https://github.com/advisories/GHSA-82x6-q7mm-w9cf) and
[prototype-pollution advisory](https://github.com/advisories/GHSA-v5mp-jgw5-2x6j).
Reachability/exploitability in this narrow route remains unverified.

Recommendation: retain Ruflo only as a restricted experimental worker. Real local
execution worked, but draft correctness required active intervention, dependency
advisories remain, and previously reviewed verification weaknesses are unresolved.
This small test does not establish broad agent/swarm effectiveness, independence,
security, or measured cost savings. Raw private pilot evidence is preserved outside
the public checkout; this document exposes only non-sensitive measured findings.
