# Commit Conventions

This repository follows a standard based on **Conventional Commits**. Every commit message must be structured as follows:

```text
<type>(<scope>): <description>
```

---

## 1. Types

The type defines the purpose and nature of the introduced change.

| Type | Purpose | Example |
|---|---|---|
| **`feat`** | (Feature) Introducing a new feature to the codebase. | `feat(models): add database settings` |
| **`chore`** | Routine tasks, project structure, configuration, dependency updates (no production code changes). | `chore(all): created project structure` |
| **`fix`** | Patching a bug in the application. | `fix(auth): repair token validation` |
| **`refactor`**| A code change that neither adds a new feature nor fixes a bug. | `refactor(api): simplify user endpoints` |
| **`docs`** | Updating or adding documentation (e.g., README, CONVENTIONS). | `docs(readme): add setup instructions` |
| **`style`** | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.). | `style(ui): fix linting errors` |
| **`test`** | Adding missing tests or correcting existing tests. | `test(models): add user unit tests` |

---

## 2. Scope

The scope indicates the specific area, module, or package of the project affected by the change. It is written in parentheses.

**Examples of used scopes:**
*   `*(models)*` – changes related to schemas, data models, or database configurations.
*   `*(all)*` – global modifications affecting the entire project or its general structure.
*   *Others (depending on project needs, e.g., `api`, `auth`, `ui`, `config`, `utils`).*

---

## 3. Description

Rules for writing a short description of the changes:

*   **Language:** Always use **English**.
*   **Formatting:** Start the description with a **lowercase letter**.
*   **Conciseness:** A clear, brief message specifying exactly what the commit changes (e.g., `add database settings, config and some tables`). Do not end with a period.

---

## 4. Examples of valid commits

```bash
# Adding a new feature within the models scope
feat(models): add database settings, config and some tables

# Creating the project skeleton (configuration work)
chore(all): created project structure

# Fixing a bug in a specific module (example)
fix(api): resolve null pointer exception in user response
```