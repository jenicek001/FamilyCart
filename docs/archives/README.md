# FamilyCart Archives

**Purpose:** Historical documentation, configurations, and completed work  
**Date Created:** October 16, 2025

---

## 📁 Archive Structure

### `docker-compose/`
Legacy and duplicate Docker Compose configurations that have been superseded by more comprehensive setups.

**Contents:**
- `docker-compose.yml.legacy` - Basic PostgreSQL setup
- `docker-compose.ci.yml.legacy` - Duplicate CI infrastructure config

**Reason:** Superseded by active docker-compose files in root (uat, runners, ci-infrastructure, dev)

---

### `nginx/`
Extended and duplicate nginx configurations superseded by modular setup.

**Contents:**
- `nginx-uat-extended.conf` - Extended UAT nginx configuration

**Reason:** Active configs in `/nginx/` and `/deploy/nginx/` directories

---

### `tasks/`
Historical task tracking files that have been consolidated into current TASKS.md.

**Contents:**
- `TASKS_OLD.md` (1,706 lines) - Original comprehensive task tracking
- `TASKS_NEW.md` (235 lines) - Intermediate task format

**Reason:** Consolidated into current `TASKS.md` (897 lines) with better organization

---

### `sprints/` (To be populated)
Sprint summaries and completion reports from completed development cycles.

**Future Contents:**
- Sprint completion summaries
- Weekly workflow reports
- Feature implementation summaries

**Reason:** Completed work documented for historical reference

---

### `fixes/` (To be populated)
Documentation of completed bug fixes and improvements.

**Future Contents:**
- Authentication fixes
- UI/UX fixes
- Code quality improvements
- GitHub workflow fixes

**Reason:** Completed fixes documented for knowledge base

---

### `ci-cd/` (To be populated)
CI/CD infrastructure setup and completion documentation.

**Future Contents:**
- CI infrastructure completion reports
- Quality standards documentation
- Workflow test results
- UAT monitoring setup summaries

**Reason:** Completed CI/CD work documented for reference

---

### `test-reports/` (To be populated)
One-off test verification and debugging reports.

**Future Contents:**
- CI/CD test timestamps
- Runner stability tests
- Infrastructure verification reports

**Reason:** Temporary test files archived for debugging history

---

## 🎯 Philosophy

This archive preserves:
1. **Historical Context** - How decisions were made
2. **Evolution** - How the project structure evolved
3. **Lessons Learned** - What worked and what didn't
4. **Reference Material** - For troubleshooting similar issues

## ✅ What's NOT Archived

Active files remain in appropriate locations:
- **Root directory** - Essential active files only (README, TASKS, docker-compose files)
- **`/docs/deployment/`** - Active deployment documentation
- **`/docs/github/`** - GitHub setup guides
- **`/docs/development/`** - Development workflow documentation
- **`/docs/features/`** - Feature specifications
- **`/sprints/`** - Detailed sprint reports (Sprint 2-8)

---

## 🔄 Accessing Archived Files

All archived files are preserved in git history and can be:

```bash
# View archived files
ls -R docs/archives/

# Read archived content
cat docs/archives/tasks/TASKS_OLD.md

# Search archives
grep -r "keyword" docs/archives/

# Compare with current
diff docs/archives/tasks/TASKS_NEW.md TASKS.md

# Restore if needed (not recommended without review)
# git mv docs/archives/[path]/[file] [original-location]
```

---

## 📅 Archive Timeline

| Date | Action | Files |
|------|--------|-------|
| 2025-10-16 | Initial archive creation | docker-compose, nginx, tasks (6 files) |
| Future | Sprint summaries | To be added as they're completed |
| Future | Fix documentation | To be added as issues are resolved |
| Future | Test reports | To be added as needed |

---

## 🔍 Need Something?

If you're looking for information that might be archived:

1. **Check current docs first** - Most information is in active documentation
2. **Search archives** - Use grep or file search
3. **Check git history** - `git log --all --full-history -- [filepath]`
4. **Ask the team** - Context might be in conversation history

---

**Note:** Files are archived, not deleted. Everything is preserved for future reference!
