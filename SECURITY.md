# Security model

Scope: owned local model and public/synthetic prompts only. No client/employer material, external-target testing, API credentials, remote judges, purchases or paid inference. Report parsing treats every input byte as untrusted and executes no content.

Threats include third-party package behavior, generated code, adversarial prompts, provider fallback, VM escape, credential inheritance, excessive requests, and malformed or forged report evidence. Use a fresh VM and non-root worker, no host mounts, no credentials, constrained resources, and independently tested firewall rules. The host relay accepts only one exact installed model, two POST API paths, <=32 KiB requests, <=12 text messages, <=1,600 output tokens, one active request and a 120-second upstream timeout. Driver runs cap prompts to four per experiment and output tokens to 128; Garak can retry empty/error responses, so the external 180-second deadline is also required. The relay binds loopback; it does not authenticate other local users or protect against a guest privilege escalation combined with broader host reachability.

The analyzer caps records at 10,000, lines at 1 MiB, reports at 16 MiB, and detector counts at 10 million. It rejects duplicate JSON keys, non-finite JSON constants, inconsistent counts and duplicate probe/detector evaluations. It keeps each detector separate and emits escaped JSON. It does not authenticate reports, validate the truth of producer counts, detect every corrupt attempt snapshot, or accept all historical Garak schemas. Feed only ordinary local files; do not use it as a service for attacker-controlled filesystem paths.

Garak 0.17.0 is an alpha project with a broad dependency surface. This lab uses only its inspected core path; it is not a claim that the complete framework is safe. The dependency snapshot is not a vulnerability-free or fully hashed lock. Runtime egress restrictions are required even if configuration says local-only.

Ruflo's selected installed dependency graph had three high advisory entries (`toml` and its two dependent packages). The full lockfile, including omitted optional packages, had 39 entries including a critical `protobufjs` entry. No exploit reachability was proven. Existing Ruflo witness-verification weaknesses and unsafe README execution examples were recorded separately; they were not relied on as trust controls. Keep Ruflo out of the regular stack pending further review/remediation.

Before publication or reuse, manually review the parser, relay, VM network rules, generated drafts and evidence. Do not commit private keys, VM images, credentials or raw diagnostic archives. Report vulnerabilities privately to the repository owner through an existing trusted channel; this project does not authorize disclosure to third parties.

## Dependency review — October 5, 2026

GitHub compared the PR dependency graph with the placeholder main branch: 39
added entries and one advisory, [GHSA-8mgp-746c-j5xp](https://github.com/advisories/GHSA-8mgp-746c-j5xp),
a high-severity NLTK model-artifact filesystem sandbox bypass affecting the
recorded `nltk==3.10.3`. The advisory lists no patched version. Preconditions
include relying on NLTK pathsec enforcement while untrusted workflows control
model import/export paths.

The driver does not directly call the listed model persistence/parser APIs.
Full transitive reachability was not proven. Guest OS isolation and worker
filesystem permissions, rather than NLTK pathsec, are the containment controls.
The standard-library analyzer and CI tests do not install this runtime snapshot.
Preserve its versions as historical experiment evidence; do not treat it as a
recommended secure environment. Repeating the scan requires owner risk review
or a separately verified fixed environment. No alert was dismissed or suppressed.
The PR remains draft pending that review; these findings do not justify stack
adoption.
