# Fix for v2 Tag Issue

## Problem Statement
Unable to resolve action `rfernandezdo/inventariographdrawio@v2`, unable to find version `v2`.

## Root Cause Analysis
The repository has a `v2.0.0` tag but is missing the corresponding major version tag `v2`. GitHub Actions convention requires major version tags (like `v2`) to exist and point to the latest stable version within that major version.

Current tag situation:
- ✅ `v2.0.0` tag exists (points to commit `545dfb92667d3309e21197f227896a135dce03b2`)
- ❌ `v2` tag missing (required for `@v2` references to work)

## Files with @v2 references
All workflow files and documentation reference `rfernandezdo/inventariographdrawio@v2`:
- `.github/workflows/infrastructure-change-detection.yml`
- `.github/workflows/manual-diagram-generation.yml`
- `.github/workflows/weekly-infrastructure-report.yml`
- Various documentation files (README.md, ACTION_README.md, etc.)

## Solution
Create a `v2` tag that points to the same commit as `v2.0.0`:

```bash
git tag v2 545dfb92667d3309e21197f227896a135dce03b2
git push origin v2
```

## Verification
After applying the fix:
1. Both `v2` and `v2.0.0` tags will point to the same commit
2. All `@v2` references in GitHub Actions will resolve correctly
3. The action will be usable from external repositories

## Follow GitHub Actions Best Practices
This aligns with GitHub Actions versioning best practices:
- Semantic versioning tags (v2.0.0, v2.1.0, etc.)
- Major version tags (v2) pointing to latest stable within that major version
- Users can reference either specific version (@v2.0.0) or major version (@v2)