# Git Quick Reference

## Daily Workflow Commands

### Start New Feature
```bash
git checkout dev
git pull origin dev
git checkout -b feature/feature-name
```

### Save Work in Progress
```bash
git add .
git commit -m "WIP: What I'm working on"
git push origin feature/current-branch
```

### Finish Feature
```bash
git add .
git commit -m "feat: Completed feature description"
git push origin feature/current-branch
# Then create PR on GitHub: feature → dev
```

### After PR Merged
```bash
git checkout dev
git pull origin dev
git branch -d feature/old-branch
```

### Check Status
```bash
git status           # What's changed
git branch -a        # See all branches
git log --oneline -5 # Recent commits
```

## Current Workflow

```
feature/branch → dev → main
     ↓            ↓      ↓
   (WIP)      (Test)  (Prod)
```

## Commit Message Format

- `feat:` New feature
- `fix:` Bug fix  
- `test:` Adding tests
- `docs:` Documentation
- `refactor:` Code cleanup
- `style:` Formatting

## Remember

✅ One feature per branch
✅ Test before PR
✅ Small, focused commits
✅ Clear commit messages
❌ Never push to main directly 