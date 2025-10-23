# My Git Version Control Workflow

## Core Principles

### 1. **Atomic Commits**
- Every logical change gets its own commit
- Never mix unrelated changes in one commit
- Commit immediately after changes are made

### 2. **Descriptive Messages**
```bash
# Format: type(scope): description
git commit -m "feat(backend): Add real-time data validation"
git commit -m "fix(frontend): Resolve localhost connection issue"
git commit -m "docs(readme): Update installation instructions"
```

### 3. **File Organization Before Commits**
```bash
# Check what's changed
git status

# Review changes
git diff

# Stage specific files or all
git add specific_file.py  # Specific files
git add .                 # All changes
```

### 4. **Branch Management**
```bash
# Create feature branch
git checkout -b feature/prompt-capture

# Work and commit
git add .
git commit -m "feat: Add feature"

# Merge back
git checkout main
git merge feature/prompt-capture
```

### 5. **Remote Synchronization**
```bash
# Before starting work
git pull origin main

# After commits
git push origin branch-name

# For pull requests
git push -u origin feature-branch
```

## My Typical Session Workflow

### Starting a Task:
```bash
# 1. Check current state
git status
git branch

# 2. Pull latest changes
git pull origin main

# 3. Create branch if needed
git checkout -b task-branch
```

### During Development:
```bash
# After each logical change
git add affected_files
git commit -m "type: description"

# Example sequence:
git add backend.py
git commit -m "feat(backend): Add endpoint"

git add frontend.html
git commit -m "feat(frontend): Add UI component"

git add README.md
git commit -m "docs: Update API documentation"
```

### Completing a Task:
```bash
# 1. Final commit
git add .
git commit -m "chore: Final cleanup"

# 2. Push to remote
git push origin branch-name

# 3. Create pull request (if branch)
# Via GitHub UI or CLI
```

## Special Workflows

### Major Reorganization (like we just did):
```bash
# Use git mv to preserve history
git mv old_path new_path

# Commit with detailed message
git commit -m "refactor: Reorganize repository structure

- Moved files to organized folders
- Created documentation
- Updated references"
```

### Fixing Mistakes:
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Amend last commit
git commit --amend -m "Updated message"

# Revert a commit
git revert commit_hash
```

### Working with Sensitive Data:
```bash
# Never commit tokens/passwords
# Use .gitignore for sensitive files
echo "secrets.txt" >> .gitignore
git add .gitignore
git commit -m "chore: Update gitignore"
```

## Backup Strategy

### Before Major Changes:
```bash
# Create backup branch
git checkout -b backup-$(date +%Y%m%d-%H%M%S)
git push origin backup-$(date +%Y%m%d-%H%M%S)
```

### File System Backup:
```bash
# Backup critical files
cp important_file.py important_file_backup_$(date +%Y%m%d).py
```

## GitHub Integration

### Setting up credentials:
```bash
git config --global user.name "username"
git config --global user.email "email"
git config --global credential.helper store
```

### Push with token:
```bash
# Set remote with token
git remote set-url origin https://TOKEN@github.com/user/repo.git

# Push changes
git push origin main
```

## Best Practices I Follow

1. **Commit Early and Often**
   - Don't wait until "everything is perfect"
   - Commit working increments

2. **Write Clear Messages**
   - Future me needs to understand
   - Include the "why" not just "what"

3. **Review Before Committing**
   - `git diff` to check changes
   - `git status` to see affected files

4. **Keep Main Branch Clean**
   - Always work in branches for features
   - Merge only tested code

5. **Document in Commits**
   - Large commits get detailed descriptions
   - Reference issue numbers if applicable

## My Commit Statistics Pattern

Typically in a session, I make:
- 5-10 small commits for incremental changes
- 1-2 large commits for major features
- 1 final commit for cleanup/documentation

## Tools I Use

- `git status` - Check current state
- `git diff` - Review changes
- `git log --oneline` - View history
- `git branch -a` - List all branches
- `git blame` - Track change origins
- `git stash` - Temporarily store changes

## Error Prevention

- Always check branch before commits
- Use `--dry-run` for dangerous operations
- Create backups before major changes
- Test merges in separate branches first
- Never force push to main without backup