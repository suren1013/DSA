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

- [ ] Auto-generated `INDEX.md` of all problems (title, topic, difficulty, status)
- [ ] Topic-level `README.md` auto-summary
- [ ] Tag-based filtering helper script
- [ ] Detect duplicate problems (same source + problemId)
- [ ] Track revision history via `attempts[]` analytics

---

## 📊 Milestone 2 — Analytics & dashboards

- [ ] Static dashboard generated from `metadata.json` across all problems
- [ ] Stats: problems by difficulty, by topic, by status, by source
- [ ] Streak / activity timeline from `attempts[]` dates
- [ ] Weak-topic detection (low solve rate per topic)
- [ ] Export stats to JSON/CSV for external tooling

---

## 🤖 Milestone 3 — Automation

- [ ] GitHub Action to regenerate `INDEX.md` and dashboard on push
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