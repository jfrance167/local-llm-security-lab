# Project state — October 5, 2026

Authorization: Jake approved the researched Garak lab plan and said begin on
October 3. Implementation, finite owned-model tests, guided Ruflo work, review
and documentation authorized. October 4: explicitly approved pilot shutdown.
Jake requested GitHub checks/publication preparation October 5 and delegated the
destination choice after being shown private/public staging options. A public
portfolio repository with an unmerged draft PR was selected for free CodeQL and
Actions checks. No merge or permanent stack integration authorized/performed.

Phase: local implementation and supervised experiment complete; owner publication
and adoption review pending. Separate local git branch: codex/garak-local-pilot.

Completed: pinned Garak source/core path review; fresh Debian VirtualBox VM;
restricted worker firewall and boundary tests; pinned script-disabled Ruflo
installation; genuine MCP discovery/execution; three local worker drafts with
preserved failures/corrections; independent tests and final reviewed analyzer;
two finite real Garak runs; manual output interpretation; security/attribution
and learning documentation; pinned Actions security workflows; public repository
and draft PR #1 at https://github.com/jfrance167/local-llm-security-lab/pull/1.

Verification: 22 Python 3.13 unittest cases pass locally; Bandit 1.9.4 has zero
findings on Python application/tools. Both Garak runs exited 0 with four scored
matches each, zero unscored. VM state poweroff verified and exact temporary relay
process stopped. No other VM, service, host boot option or instruction changed.

Limitations: final analyzer suite ran locally after VM-copy approval timed out
twice; it was not rerun in Linux. Initial/corrected worker tests ran in Debian.
GitHub Ubuntu tests/Bandit and Python/JavaScript CodeQL passed for publication
commit 9f35c0f. No open code-scanning or secret-scanning alerts were returned.
Dependency comparison found an unpatched high NLTK advisory (see SECURITY.md).
Model digest was not captured at scan time. No standalone JS SAST run locally;
relay had source review, syntax and route/model-denial checks, with CodeQL JS
completed remotely. Ruflo dependency advisories and earlier verification issues remain.

Worker choice: local Ollama first, actual Ruflo requests to local model only;
one public North request after local draft inadequacy returned no text and stopped.
No paid fallback or retries. Updated Laya instructions were read; request-category
and refund/urgency schemas are unsuitable for this already scoped code/security
verification, so no Laya inference was made.

Publication preparation: relay handler now has 9 offline tests covering denied
routes/models, bounds, forced upstream controls, redaction and concurrency;
malformed non-object JSON now correctly receives HTTP 400. This update was not
used for the earlier real model experiment; raw results remain unchanged.
Read-only worker readiness refreshed. This verification/security stage requires
no drafting worker or classifier inference; no new provider research needed.

GitHub baseline: main protected with strict required checks, administrator
enforcement, conversation resolution, and force-push/deletion denial. Workflow
token permissions read-only by default; secret scanning, push protection,
Dependabot alerts and security updates enabled. Single-owner review count is zero;
Jake's manual review and merge decision remain required by this workflow.

Next: verify final documentation commit checks; keep PR draft for Jake's NLTK
risk review and merge decision. No release, deployment or PR merge performed.
Recommendation: keep Ruflo experimental, do not add to the regular stack yet.
Private raw pilot evidence is outside this checkout; see docs/worker-evaluation.md.
