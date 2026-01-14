#!/bin/bash
# Script to push to your fork and create PR

# Remove old myfork remote if exists
git remote remove myfork 2>/dev/null

# Add your fork as remote
git remote add myfork https://github.com/rgodavarthi7/sponsor-finder.git

# Push to your fork
git push myfork main

echo "✓ Pushed to your fork!"
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/rgodavarthi7/sponsor-finder"
echo "2. Click 'Contribute' -> 'Open pull request'"
echo "3. Add title: 'Restructure project with 8-phase workflow and new agents'"
echo "4. Add description explaining the changes"
echo "5. Submit the PR"
