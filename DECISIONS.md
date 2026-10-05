# Decisions

- Adopt pinned Garak core instead of reimplementing its scanner. Build only a
  standard-library evidence analyzer and finite driver. NVIDIA source/license,
  actual Ollama adapter and recent maintenance were inspected; popularity alone
  was not the selection criterion. Alternatives: WrongSecrets adds vulnerable
  service/license scope; Kubernetes Goat adds a cluster prerequisite.
- Use a fresh VirtualBox VM because Docker/WSL failed and the existing Windows
  hypervisor was intentionally off. Preserve existing labs and host boot settings.
  Enforce network restrictions independently of Ruflo's provider/fallback config.
- Bound one PromptInject class to four prompts. Validate its constant trigger and
  disable upstream per-attempt generation mutation due prompt/settings shuffle
  misalignment. Do not claim a full upstream CLI installation or broad benchmark.
- Keep per-detector denominators separate. Require exact integer counts and
  matching completion; zero and missing evidence must never become success.
- Preserve worker drafts before corrections; acknowledge Codex's final contribution.
  Restrict Ruflo to experimentation because observed draft defects, advisories and
  prior verification flaws do not support regular-stack adoption.
- Use Apache-2.0 and retain upstream attribution for derived prompt evidence.
  Publish only reviewed synthetic/model evidence, not VM credentials or archives.
