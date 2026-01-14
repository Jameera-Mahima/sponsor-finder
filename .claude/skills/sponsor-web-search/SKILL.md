Set-Content -Path ".claude\skills\sponsor-web-search\SKILL.md" -Value @"
---
name: sponsor-web-search
description: Searches for potential sponsors matching criteria. Use when user needs to find sponsors, donors, or funding sources for nonprofit/community projects. Handles keyword extraction, web searching, and result compilation.
---

# Sponsor Web Search Skill

## Overview
Find potential sponsors (corporations, foundations, NGOs) for nonprofit projects.

## Workflow

1. **Extract Keywords**
   - Parse user prompt for: budget, location, sector, cause
   - Extract keywords from mission/vision context
   - Combine into search terms

2. **Search Strategy**
   - Search for: "[cause] sponsors [location]"
   - Search for: "[cause] grants [location]"
   - Search for: "[industry] corporate giving [location]"
   - Search for: "foundations supporting [cause]"

3. **Categorize Results**
   - Corporations
   - Foundations
   - NGOs
   - Individual donors
   
4. **Validate & Format**
   - Check relevance to mission
   - Verify active giving programs
   - Format as structured list

## Output Format
``````json
{
  "corporations": [...],
  "foundations": [...],
  "ngos": [...],
  "individuals": [...]
}
``````
"@