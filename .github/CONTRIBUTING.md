# Contributing to GVisit

## Git Workflow

We follow a feature-branch workflow to keep our codebase organized and ensure quality.

### Branch Structure

- **`main`** - Production-ready code. Deployed to production.
- **`dev`** - Integration branch for testing features together before release.
- **`feature/*`** - Individual feature branches for new development.

### Development Process

#### 1. Starting a New Feature

Always create a new branch from the latest `dev`:

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

**Naming Convention**: Use descriptive names like:
- `feature/user-profile-page`
- `feature/export-to-pdf`
- `fix/login-error-handling`

#### 2. While Working

- **Commit Often**: Make small, logical commits
- **Clear Messages**: Use conventional commit format:
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `test:` Test additions/changes
  - `refactor:` Code refactoring
  - `style:` Formatting changes

Example:
```bash
git add .
git commit -m "feat: Add export functionality to journal entries"
```

- **Push Regularly**: Backup your work
```bash
git push origin feature/your-feature-name
```

#### 3. Feature Complete

1. Ensure all tests pass:
```bash
python3 -m pytest
```

2. Push final changes:
```bash
git push origin feature/your-feature-name
```

3. Create Pull Request:
- Base: `dev`
- Compare: `feature/your-feature-name`
- Add description of changes
- Reference any issues

#### 4. After PR Approval

Once merged to `dev`:

```bash
git checkout dev
git pull origin dev
git branch -d feature/your-feature-name  # Delete local feature branch
```

#### 5. Release to Production

When `dev` is stable and tested:
- Create PR from `dev` → `main`
- Tag the release in `main`

### Important Rules

1. **One Feature Per Branch**: Keep branches focused on a single feature or fix
2. **Never Push Directly to Main**: Always go through PR process
3. **Keep PRs Small**: Easier to review and less likely to have conflicts
4. **Update from Dev**: If your feature branch gets old, update it:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout feature/your-branch
   git merge dev
   ```

### Testing Requirements

Before creating a PR:
- All tests must pass
- Add tests for new features
- Maintain or improve code coverage

### Code Review Process

1. Self-review your changes first
2. Ensure CI/CD pipeline passes
3. Address reviewer feedback promptly
4. Squash commits if requested

### End of Day Process

If you need to stop work but aren't ready to merge:

```bash
git add .
git commit -m "WIP: Description of progress"
git push origin feature/your-branch
```

This ensures your work is backed up and others can see progress if needed. 