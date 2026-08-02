# Contributing

This is a personal DSA practice tracker, but these conventions keep the
repository consistent, searchable, and ready for future automation
(analytics, dashboards, auto-generated summaries).

---

## 1. Folder structure

Every problem lives at:

```
problems/<topic>/<problem-name>/
```

Inside each problem folder:

| File           | Required | Purpose                                  |
|----------------|----------|------------------------------------------|
| `Solution.java` | ✅ Yes   | The Java solution                        |
| `metadata.json` | ✅ Yes   | Structured metadata (see schema)         |
| `README.md`     | ⬜ No    | Problem statement, approach, examples    |
| `notes.md`      | ⬜ No    | Learnings, edge cases, follow-ups        |

No other files are required. Avoid committing compiled `.class` files
(they are gitignored).

---

## 2. Naming conventions

- **Topic folder**: `kebab-case`, lowercase.
  - ✅ `dynamic-programming`, `binary-search`, `arrays`
  - ❌ `Dynamic Programming`, `dynamic_programming`, `DP`
- **Problem folder**: `kebab-case`, lowercase.
  - ✅ `two-sum`, `binary-tree-inorder-traversal`
  - ❌ `TwoSum`, `two_sum`, `two.sum`
- **Java class**: `PascalCase`, derived from the problem folder name.
  - `two-sum` → `TwoSum`
  - `binary-tree-inorder-traversal` → `BinaryTreeInorderTraversal`
- **Fixed file names**: `Solution.java`, `metadata.json`, `README.md`, `notes.md`.

Regex for folder names: `^[a-z0-9]+(-[a-z0-9]+)*$`

---

## 3. Adding a problem

### Option A — Use the scaffolding script (recommended)

```bash
python scripts/new_problem.py \
  --topic arrays \
  --name two-sum \
  --title "Two Sum" \
  --difficulty easy \
  --source leetcode \
  --url https://leetcode.com/problems/two-sum/ \
  --source-id 1
```

The script:
- Creates `problems/arrays/two-sum/`.
- Copies templates from `templates/`.
- Fills `metadata.json` with the provided values and today's date.
- Generates the `PascalCase` class name in `Solution.java`.

### Option B — Add manually

1. `mkdir -p problems/<topic>/<problem-name>`
2. Copy `templates/*` into the new folder.
3. Edit `metadata.json` (set `title`, `topic`, `source`, `difficulty`, `status`, dates).
4. Rename the class in `Solution.java` to the PascalCase problem name.
5. Implement the solution.
6. (Optional) Fill `README.md` and `notes.md`.

---

## 4. Metadata rules

Every `metadata.json` **must** include these required fields:

| Field         | Type   | Allowed values                                  |
|---------------|--------|--------------------------------------------------|
| `title`       | string | Human-readable title                             |
| `topic`       | string | Must match the topic folder name                 |
| `source`      | object | `{ "platform", "url"?, "problemId"? }`          |
| `difficulty`  | string | `easy` \| `medium` \| `hard`                     |
| `status`      | string | `todo` \| `in-progress` \| `solved` \| `reviewed`|
| `language`    | string | Default `java`                                   |
| `createdAt`   | string | ISO date `YYYY-MM-DD`                            |
| `updatedAt`   | string | ISO date `YYYY-MM-DD`, `>= createdAt`            |

Optional fields: `tags` (string[]), `timeComplexity` (string),
`spaceComplexity` (string), `attempts` (object[]), `notes` (string).

Full reference: [`docs/METADATA_SCHEMA.md`](docs/METADATA_SCHEMA.md).

---

## 5. Validation

Before committing, run:

```bash
python scripts/validate.py
```

The validator checks structure, metadata completeness, allowed values,
naming conventions, and date sanity. CI runs the same check on every push
and pull request.

**A failing validation blocks the CI pipeline** — fix all reported errors
before merging.

---

## 6. Workflow

1. Create/scaffold the problem folder.
2. Implement `Solution.java`.
3. Fill `metadata.json` (set `status` appropriately).
4. Run `python scripts/validate.py`.
5. Commit with a clear message, e.g.:
   `add: arrays/two-sum (easy, solved)`
6. Push. CI validates automatically.

---

## 7. Tips for maintainability

- One problem per folder — never combine multiple problems.
- Keep `metadata.json` up to date (`updatedAt`, `status`, `attempts`).
- Prefer many small topics over one giant topic.
- Use `notes.md` to record *why* an approach works, not just *what* it does.