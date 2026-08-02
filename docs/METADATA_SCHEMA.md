# Metadata Schema

Every problem folder **must** contain a `metadata.json` file conforming to this
schema. The validator (`scripts/validate.py`) enforces the required fields and
allowed values described here.

---

## Required fields

| Field        | Type    | Description                                              |
|--------------|---------|----------------------------------------------------------|
| `title`      | string  | Human-readable problem title (e.g. `"Two Sum"`).         |
| `topic`      | string  | Topic slug; **must match** the topic folder name.       |
| `source`     | object  | Where the problem came from (see below).                 |
| `difficulty` | string  | One of `easy`, `medium`, `hard`.                         |
| `status`     | string  | One of `todo`, `in-progress`, `solved`, `reviewed`.       |
| `language`   | string  | Solution language; default `java`.                       |
| `createdAt`  | string  | ISO date `YYYY-MM-DD` when the folder was created.       |
| `updatedAt`  | string  | ISO date `YYYY-MM-DD` of last update; `>= createdAt`.     |

---

## Optional fields

| Field              | Type     | Description                                              |
|--------------------|----------|----------------------------------------------------------|
| `tags`             | string[] | Free-form tags for filtering (e.g. `["array","hash-table"]`). |
| `timeComplexity`   | string   | Big-O time complexity (e.g. `"O(n)"`).                   |
| `spaceComplexity`  | string   | Big-O space complexity (e.g. `"O(n)"`).                  |
| `attempts`         | object[] | Revision/solve history (see below).                      |
| `notes`            | string   | Short free-text note (longer notes go in `notes.md`).    |

---

## `source` object

| Field      | Required | Type   | Description                                  |
|------------|----------|--------|----------------------------------------------|
| `platform` | ✅ Yes   | string | Platform/source name (e.g. `LeetCode`).     |
| `url`      | ⬜ No     | string | Direct link to the problem.                 |
| `problemId`| ⬜ No     | string | Platform-specific problem id (e.g. `"1"`).  |

> `platform` is required so problems can be grouped by source even without a URL.
> For self-made or textbook problems, use a descriptive platform like
> `"Textbook"` or `"Self"`.

---

## `attempts[]` entries

Each attempt records one solve/revision event:

| Field             | Required | Type   | Description                                        |
|-------------------|----------|--------|----------------------------------------------------|
| `date`            | ✅ Yes    | string | ISO date `YYYY-MM-DD` of the attempt.              |
| `outcome`         | ✅ Yes    | string | One of `accepted`, `wrong-answer`, `timeout`, `gave-up`, `reviewed`. |
| `timeComplexity`  | ⬜ No     | string | Complexity achieved on this attempt.              |
| `spaceComplexity` | ⬜ No     | string | Space complexity achieved on this attempt.        |
| `notes`           | ⬜ No     | string | What happened, what was learned.                  |

---

## Allowed values

### `difficulty`
`easy` · `medium` · `hard`

### `status`
`todo` · `in-progress` · `solved` · `reviewed`

### `attempts[].outcome`
`accepted` · `wrong-answer` · `timeout` · `gave-up` · `reviewed`

---

## Full example

```json
{
  "title": "Two Sum",
  "topic": "arrays",
  "source": {
    "platform": "LeetCode",
    "url": "https://leetcode.com/problems/two-sum/",
    "problemId": "1"
  },
  "difficulty": "easy",
  "status": "solved",
  "language": "java",
  "tags": ["array", "hash-table"],
  "timeComplexity": "O(n)",
  "spaceComplexity": "O(n)",
  "attempts": [
    {
      "date": "2026-08-02",
      "outcome": "accepted",
      "timeComplexity": "O(n)",
      "spaceComplexity": "O(n)",
      "notes": "Hash map for O(1) complement lookup."
    }
  ],
  "createdAt": "2026-08-02",
  "updatedAt": "2026-08-02"
}
```

---

## Validation summary

The validator enforces:

1. `metadata.json` exists and is valid JSON.
2. All **required** fields are present and non-empty.
3. `source.platform` is present.
4. `difficulty`, `status`, and `attempts[].outcome` use only allowed values.
5. `topic` matches the topic folder name.
6. `createdAt` and `updatedAt` are valid ISO dates and `updatedAt >= createdAt`.
7. Folder names follow `kebab-case` (`^[a-z0-9]+(-[a-z0-9]+)*$`).
8. `Solution.java` exists alongside `metadata.json`.