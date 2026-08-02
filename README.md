# DSA Practice Tracker

A clean, open-ended personal tracker for Data Structures & Algorithms practice in **Java**.
It is not tied to any syllabus — add unlimited problems from any platform or source
(LeetCode, HackerRank, Codeforces, textbooks, interviews, your own ideas, …).

The repository is structured so it can grow into analytics, dashboards, and
auto-generated summaries later — without restructuring what already exists.

---

## ✨ Design goals

- **Open-ended** — no fixed problem list or curriculum.
- **Source-agnostic** — track problems from any platform.
- **Scalable structure** — `problems/<topic>/<problem-name>/`.
- **Consistent metadata** — every problem carries a `metadata.json`.
- **Automatable** — scripts for scaffolding + validation, CI via GitHub Actions.
- **Extensible** — ready for analytics, dashboards, and generated reports.

---

## 📁 Repository structure

```
DSA/
├── .github/
│   └── workflows/
│       └── validate.yml          # CI: validate structure & metadata on push/PR
├── docs/
│   └── METADATA_SCHEMA.md       # Full metadata.json field reference
├── problems/                    # All tracked problems live here
│   └── <topic>/
│       └── <problem-name>/
│           ├── Solution.java    # Required: the solution
│           ├── metadata.json    # Required: structured metadata
│           ├── README.md        # Optional: problem statement / approach
│           └── notes.md         # Optional: learnings, edge cases, follow-ups
├── scripts/
│   ├── validate.py              # Validate repo structure & metadata
│   └── new_problem.py           # Scaffold a new problem folder
├── templates/                  # Starter templates for a problem folder
│   ├── Solution.java
│   ├── README.md
│   ├── notes.md
│   └── metadata.json
├── .gitignore
├── CONTRIBUTING.md              # How to add problems & conventions
├── LICENSE
├── README.md
└── ROADMAP.md                   # Future plans
```

---

## 🚀 Quick start

### Add a new problem (recommended)

Use the scaffolding script to create a correctly-structured folder:

```bash
python scripts/new_problem.py --topic arrays --name two-sum \
  --title "Two Sum" --difficulty easy --source leetcode \
  --url https://leetcode.com/problems/two-sum/ --source-id 1
```

This creates `problems/arrays/two-sum/` with `Solution.java`, `metadata.json`,
`README.md`, and `notes.md` pre-filled from `templates/`.

### Add a problem manually

1. Create `problems/<topic>/<problem-name>/`.
2. Copy files from `templates/` into it.
3. Fill in `metadata.json` (see [metadata schema](docs/METADATA_SCHEMA.md)).
4. Implement `Solution.java`.
5. (Optional) Write `README.md` and `notes.md`.

### Validate the repository

```bash
python scripts/validate.py
```

Exits with code `0` if everything is valid, non-zero otherwise.
This same check runs automatically in CI (`.github/workflows/validate.yml`).

---

## 📐 Naming conventions

| Element        | Convention   | Example                          |
|----------------|--------------|----------------------------------|
| Topic folder   | `kebab-case` | `dynamic-programming`           |
| Problem folder | `kebab-case` | `binary-tree-inorder-traversal`  |
| Java class     | `PascalCase` | `TwoSum`                         |
| File names     | Fixed        | `Solution.java`, `metadata.json` |

- Topic and problem folder names must be lowercase, use hyphens, and contain
  only letters, digits, and hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- The Java class inside `Solution.java` should be the PascalCase form of the
  problem folder name (e.g. `two-sum` → `TwoSum`).

---

## 🧾 Metadata at a glance

Every problem folder **must** contain a `metadata.json` with at least:

```json
{
  "title": "Two Sum",
  "topic": "arrays",
  "source": { "platform": "LeetCode", "url": "https://leetcode.com/problems/two-sum/", "problemId": "1" },
  "difficulty": "easy",
  "status": "solved",
  "language": "java",
  "createdAt": "2026-08-02",
  "updatedAt": "2026-08-02"
}
```

See [`docs/METADATA_SCHEMA.md`](docs/METADATA_SCHEMA.md) for the full field
reference, allowed values, and optional fields like `tags` and `attempts`.

---

## ✅ Validation rules

The validator (`scripts/validate.py`) enforces:

1. Every problem folder lives at `problems/<topic>/<problem-name>/`.
2. Every problem folder contains `metadata.json` and `Solution.java`.
3. `metadata.json` is valid JSON and has all **required** fields.
4. `difficulty` and `status` use only allowed values.
5. `topic` in metadata matches the topic folder name.
6. Folder names follow `kebab-case`.
7. Dates are valid ISO (`YYYY-MM-DD`) and `updatedAt >= createdAt`.

---

## 🗺️ Roadmap

See [`ROADMAP.md`](ROADMAP.md) for planned features (analytics, dashboards,
auto-generated summaries, multi-language support).

---

## 🤝 Contributing

This is a personal tracker, but conventions are documented in
[`CONTRIBUTING.md`](CONTRIBUTING.md) so the structure stays consistent over time.

---

## 📄 License

[MIT](LICENSE) © Surendher