# Sponsor Finder System Specification

## Problem Statement
Find 500 sponsors for Healing NY with $500,000 funding goal

## Mission & Vision Context
- Mental health support
- Arts education
- Community-based healing
- New York location

## Requirements

### Functional Requirements
1. Accept flexible prompts (short or detailed)
2. Extract keywords from:
   - User prompt
   - Mission/vision statement
3. Search multiple sources:
   - Web search
   - Foundation databases
4. Categorize results:
   - Corporations
   - Foundations
   - NGOs
   - Individuals
5. Filter by:
   - Location (optional)
   - Giving history (optional)
   - Sector/industry (optional)
   - Amount range (optional)

### Non-Functional Requirements
- Process 100+ sources per search
- Return results in <5 minutes
- Validate sponsor data quality
- Export as CSV/JSON

## User Stories

### Story 1: Simple Search
'I need sponsors for healing NY'
? System searches for mental health + healing + NY sponsors

### Story 2: Detailed Search
'I need sponsors for healing NY in Manhattan that have donated at least $10,000 to mental health causes in the past 2 years'
? System applies all filters

### Story 3: Sector-Specific
'I need art education sponsors for healing NY from the tech sector'
? System searches tech companies supporting arts

## Architecture

### Phase 1: Keyword Extraction
- Subagent: keyword-extractor
- Input: User prompt + mission context
- Output: JSON keywords

### Phase 2: Web Research
- Subagent: web-researcher
- Input: Keywords from Phase 1
- Output: 15-25 sponsor prospects

### Phase 3: Categorization
- Subagent: categorizer
- Input: Raw sponsor list
- Output: Categorized by type

### Phase 4: Validation
- Subagent: validator
- Input: Categorized sponsors
- Output: Validated list (score =5)

## Success Criteria
- Find at least 20 high-quality sponsors per search
- Relevance score average =7/10
- Complete workflow in <7 minutes
- Zero false positives (all sponsors are legitimate)
