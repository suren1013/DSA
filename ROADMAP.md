# Roadmap

This repository starts as a minimal, well-structured DSA practice tracker.
The structure is intentionally designed to grow into richer tooling without
breaking existing problem folders.

Progress is tracked by milestone. Items are exploratory and may change.

---

## ✅ Milestone 0 — Foundation (this release)

- [x] Scalable folder structure `problems/<topic>/<problem-name>/`
- [x] Standard `metadata.json` schema
- [x] Starter templates (`Solution.java`, `README.md`, `notes.md`, `metadata.json`)
- [x] Validation script (`scripts/validate.py`)
- [x] Scaffolding script (`scripts/new_problem.py`)
- [x] GitHub Actions CI (`.github/workflows/validate.yml`)
- [x] Root docs: `README.md`, `CONTRIBUTING.md`, `ROADMAP.md`, `LICENSE`, `.gitignore`

---

## 🚧 Milestone 1 — Metadata & searchability

- [x] Metadata scanner (`scripts/scanner.py`) — parses `metadata.json` + Solution.java fallback
- [x] Auto-generated README sections (stats, topics, solved table, activity, languages)
- [x] Topic-wise summary sections in root README
- [x] Detect duplicate problems (same source + problemId) in `validate.py`
- [x] Detect duplicate problem slugs across topics in `validate.py`
- [x] Track revision history via `attempts[]` (recent activity section)
- [ ] Tag-based filtering helper script

---

## 📊 Milestone 2 — Analytics & dashboards

- [x] Stats: problems by difficulty, by topic, by status, by source (in README)
- [x] Activity timeline from `attempts[]` dates (recent activity section)
- [x] Language breakdown section
- [x] Progress bars in README (`scripts/formatters.py`)
- [x] Streak & activity from git commit history (`scripts/stats.py`)
- [x] Dashboard JSON output (`dashboard/stats.json` via `scripts/generate_dashboard.py`)
- [x] Export stats to JSON for external tooling (`dashboard/stats.json`)
- [x] Dedicated static dashboard page (`site/` — GitHub Pages-ready, no build deps)
- [x] Search/filter support in the static dashboard (title, topic, tag, source, difficulty, status)
- [ ] Weak-topic detection (low solve rate per topic)
- [ ] Export stats to CSV for external tooling

---

## 🤖 Milestone 3 — Automation

- [x] GitHub Action to regenerate README, dashboard & site data on push (`.github/workflows/generate.yml`)
- [x] GitHub Pages deployment workflow (`.github/workflows/pages.yml`)
- [x] Scanner smoke test in CI (`.github/workflows/validate.yml`)
- [ ] Auto-bump `updatedAt` when a problem folder changes
- [ ] Optional: compile + run `Solution.java` against sample tests
- [ ] Pre-commit hook to run `validate.py` locally

---

## 🌐 Milestone 4 — Extensibility

- [ ] Multi-language support (Python/C++ solutions alongside Java)
- [ ] Per-problem test cases (`tests/` subfolder convention)
- [ ] Editorial / solution write-up linking
- [ ] Import problems from platform APIs (LeetCode, Codeforces)
- [ ] Spaced-repetition review scheduler based on `status` + `attempts`

---

## Principles guiding growth

1. **Never break existing problem folders** — new features are additive.
2. **Metadata-first** — anything automatable reads from `metadata.json`.
3. **Keep it minimal** — only add tooling that reduces manual work.
4. **Stay source-agnostic** — no platform lock-in.