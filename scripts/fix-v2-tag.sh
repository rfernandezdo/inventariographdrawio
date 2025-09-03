#!/bin/bash
# Script to fix the missing v2 tag issue
# This script creates the missing v2 tag that points to the same commit as v2.0.0

set -e

echo "🔧 Fixing missing v2 tag for GitHub Action compatibility..."

# Get the commit hash that v2.0.0 points to
V2_0_0_COMMIT=$(git rev-list -n 1 v2.0.0)
echo "📍 v2.0.0 tag points to commit: $V2_0_0_COMMIT"

# Check if v2 tag already exists
if git show-ref --tags --quiet refs/tags/v2; then
    echo "✅ v2 tag already exists"
    EXISTING_V2_COMMIT=$(git rev-list -n 1 v2)
    echo "📍 v2 tag points to commit: $EXISTING_V2_COMMIT"
    
    if [ "$V2_0_0_COMMIT" = "$EXISTING_V2_COMMIT" ]; then
        echo "✅ v2 tag already points to the correct commit"
    else
        echo "⚠️  v2 tag points to different commit, updating..."
        git tag -d v2
        git tag v2 $V2_0_0_COMMIT
        echo "✅ v2 tag updated to point to same commit as v2.0.0"
    fi
else
    echo "🏷️  Creating v2 tag..."
    git tag v2 $V2_0_0_COMMIT
    echo "✅ v2 tag created pointing to same commit as v2.0.0"
fi

# Push the tag to remote
echo "🚀 Pushing v2 tag to remote repository..."
git push origin v2

echo "🎉 Fix completed! The @v2 references should now work correctly."
echo "📋 Verification:"
echo "   - v2.0.0 tag: $V2_0_0_COMMIT"
echo "   - v2 tag:     $(git rev-list -n 1 v2)"