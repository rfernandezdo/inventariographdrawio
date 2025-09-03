# GitHub Action v2 Tag Fix - Implementation Guide

## Issue Summary
GitHub Actions using `rfernandezdo/inventariographdrawio@v2` fail with "unable to find version `v2`" because the repository only has a `v2.0.0` tag but lacks the required major version `v2` tag.

## Current State (Before Fix)
```bash
$ git tag --list
v2.0.0
```

## Required State (After Fix)
```bash
$ git tag --list
v2        # <-- Missing tag that needs to be created
v2.0.0
```

## Implementation Steps

### 1. Identify the Target Commit
```bash
# Find the commit that v2.0.0 points to
$ git rev-list -n 1 v2.0.0
545dfb92667d3309e21197f227896a135dce03b2
```

### 2. Create the v2 Tag
```bash
# Create v2 tag pointing to the same commit as v2.0.0
$ git tag v2 545dfb92667d3309e21197f227896a135dce03b2
```

### 3. Push the Tag to Remote
```bash
# Push the new tag to make it available for GitHub Actions
$ git push origin v2
```

### 4. Verify the Fix
```bash
# Both tags should now point to the same commit
$ git show-ref --tags
545dfb92667d3309e21197f227896a135dce03b2 refs/tags/v2
545dfb92667d3309e21197f227896a135dce03b2 refs/tags/v2.0.0
```

## Automated Fix Script
Run `scripts/fix-v2-tag.sh` to automatically apply this fix.

## Impact
Once implemented, this will fix all failing GitHub Actions that reference:
- `rfernandezdo/inventariographdrawio@v2`

This follows GitHub Actions best practices where major version tags point to the latest stable release within that major version.

## Files That Will Benefit
- `.github/workflows/infrastructure-change-detection.yml`
- `.github/workflows/manual-diagram-generation.yml` 
- `.github/workflows/weekly-infrastructure-report.yml`
- Any external repositories using this action with `@v2` reference