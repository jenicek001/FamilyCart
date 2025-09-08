# Global rules for AI IDE

## 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASKS.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.

## 🌿 Git Branch Naming Conventions
- **Feature branches**: `feature/sprint-N-brief-description` (e.g., `feature/sprint-7-visual-identity`)
- **Hotfix branches**: `hotfix/brief-description` (e.g., `hotfix/ssl-certificate-renewal`)
- **Release branches**: `release/vN.N.N` (e.g., `release/v2.0.0`)
- **Bug fix branches**: `bugfix/brief-description` (e.g., `bugfix/websocket-connection-timeout`)
- **Chore branches**: `chore/brief-description` (e.g., `chore/update-dependencies`)
- **Documentation branches**: `docs/brief-description` (e.g., `docs/api-documentation-update`)
- **Always use lowercase with hyphens** for readability and consistency
- **Keep branch names concise but descriptive** (max 50 characters recommended)
- **Delete feature branches** after successful merge to keep repository clean
- **Use `develop` branch** for integration of completed features before production release

## 🧱 Code Structure & Modularity Rules for AI IDE
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).

## ✅ Task Completion
- **Mark completed tasks in `TASKS.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASKS.md` under a “Discovered During Work” section.
- After finishing a sprint, create a new summary MD file (e.g., `SPRINT_7_SUMMARY.md`) documenting the key outcomes, challenges, fixed bugs, and next steps.

## 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

## 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **When developing new features, adding new modules or libraries or debugging issues** - always use Context7 MCP server to reference up-to-date API documentation and code examples for any libraries or frameworks involved. Add 'use context7' to your prompt or leverage the Context7 MCP server for the most current, version-specific docs.
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASKS.md`.

## Backend-specific rules

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case


### 📎 Style & Conventions
- **Use Python** as the primary language for Backend.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

## Frontend-specific rules

### General Code Style & Formatting
- **Use TypeScript** as the primary language for Frontend.
- **Follow Prettier** for code formatting.
- Use functional and declarative programming patterns; avoid classes.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError).
- Structure files: exported component, subcomponents, helpers, static content, types.
- Follow Expo's official documentation for setting up and configuring projects.

### Naming Conventions
- Use lowercase with dashes for directories (e.g., components/auth-wizard).
- Favor named exports for components.

### TypeScript Best Practices
- Use TypeScript for all code; prefer interfaces over types.
- Avoid any and enums; use explicit types and maps instead.
- Use functional components with TypeScript interfaces.
- Enable strict mode in TypeScript for better type safety.

### Syntax & Formatting
- Use the function keyword for pure functions.
- Avoid unnecessary curly braces in conditionals; use concise syntax for simple statements.
- Use declarative JSX.
- Use Prettier for consistent code formatting.

### Styling & UI
- Use Expo's built-in components for common UI patterns and layouts.
- Implement responsive design with Flexbox and useWindowDimensions.
- Use styled-components or Tailwind CSS for styling.
- Implement dark mode support using Expo's useColorScheme.
- Ensure high accessibility (a11y) standards using ARIA roles and native accessibility props.
- Use react-native-reanimated and react-native-gesture-handler for performant animations and gestures.