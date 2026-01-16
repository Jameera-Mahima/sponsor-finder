# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered sponsor search system that helps the Community School of the Arts Foundation (CSOAF) discover and qualify potential sponsors.

## OpenAI Configuration

This project can use OpenAI models (GPT-4o, GPT-4o-mini) for all agent operations instead of Claude Code's default models.

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`:
     ```
     OPENAI_API_KEY=your-api-key-here
     USE_OPENAI=true
     ```

3. **Model configuration:**
   - `OPENAI_MODEL_FAST=gpt-4o-mini` - Used for quick tasks (keyword extraction, categorization)
   - `OPENAI_MODEL_QUALITY=gpt-4o` - Used for complex tasks (validation, orchestration)

### Agent-Model Mapping

The system automatically selects the appropriate model for each agent:

| Agent | Model | Rationale |
|-------|-------|-----------|
| keyword-extractor | gpt-4o-mini | Fast keyword extraction |
| web-researcher | gpt-4o-mini | Quick web searches |
| categorizer | gpt-4o-mini | Simple categorization |
| validator | gpt-4o | Quality validation needs deeper analysis |
| salesforce-integration | gpt-4o-mini | Data formatting |
| engagement-tracking | gpt-4o | Complex analytics |
| event-coordination | gpt-4o-mini | Event data processing |
| campaign-orchestrator | gpt-4o | Strategic coordination |

### Usage

The configuration is loaded automatically from `.env`. All agents will use OpenAI when `USE_OPENAI=true`.

**Example usage:**
```python
from config import get_openai_client, get_model_for_agent

# Get OpenAI client
client = get_openai_client()

# Get model for specific agent
model = get_model_for_agent('keyword-extractor')  # Returns 'gpt-4o-mini'
```

See `openai_agent_example.py` for complete examples.

### Security

- **Never commit `.env` files** - They're excluded in `.gitignore`
- API keys are loaded from environment variables only
- Use `.env.example` as a template for team members

## Model Fallback Strategy

The system uses **OpenAI as primary**, with **Claude as automatic fallback**:

### Automatic Fallback
- If OpenAI API fails (network error, rate limit, service outage), automatically switches to Claude
- Model mapping:
  - `gpt-4o-mini` → `claude-haiku-4-5-20251001`
  - `gpt-4o` → `claude-sonnet-4-5-20250929`
- Fallback is logged transparently in campaign logs
- No user intervention required

### Configuration
Both API keys recommended in `.env`:
```bash
# Required: OpenAI (primary)
OPENAI_API_KEY=sk-...
USE_OPENAI=true

# Optional but recommended: Claude (fallback)
ANTHROPIC_API_KEY=sk-ant-...
USE_CLAUDE_FALLBACK=true
```

### Cost Optimization
The system is **optimized for cost** by default:
- **Fast agents** use `gpt-4o-mini` ($0.15/$0.60 per 1M tokens)
  - keyword-extractor, web-researcher, categorizer, salesforce-integration, event-coordination
- **Quality agents** use `gpt-4o` ($2.50/$10.00 per 1M tokens)
  - validator, engagement-tracking, campaign-orchestrator
- Claude fallback costs slightly more but ensures reliability

### Cost Tracking
All campaign logs include accurate cost information:
- **Cost per agent** - breakdown by individual agent execution
- **Cost by provider** - OpenAI vs Claude split
- **Cost per validated sponsor** - efficiency metric
- **Total campaign cost** - overall budget tracking

Set cost alerts in `.env`:
```bash
COST_ALERT_THRESHOLD=5.00  # Alert if campaign exceeds $5.00
LOG_COSTS_PER_AGENT=true   # Enable detailed per-agent cost logging
```

### Using the Unified LLM Interface

For new Python code integrating with the system:
```python
from config import call_llm

# Call LLM with automatic fallback
messages = [
    {"role": "system", "content": "You are a sponsor researcher."},
    {"role": "user", "content": "Find sponsors for arts education..."}
]

result = call_llm('keyword-extractor', messages)

# Result contains:
# - result['content']: Response text
# - result['model_used']: Which model was used (gpt-4o-mini, etc.)
# - result['tokens_input']: Input tokens
# - result['tokens_output']: Output tokens
# - result['provider']: 'openai' or 'claude'
```

## Organization Profile: Community School of the Arts Foundation (CSOAF)

### Mission Statement
The Community School of the Arts Foundation strives to **unlock creative educational pathways for any type of learner**. We are committed to providing accessible and engaging art education programs that inspire young minds, encourage self-expression, and foster a lifelong appreciation for the arts. Through our unwavering dedication to artistic enrichment, we aim to cultivate the next generation of imaginative, empathetic, and culturally aware individuals who will contribute positively to society through their artistic talents and creative insights.

### Vision
Nurturing the next generation of imaginative and empathetic people who contribute to society through artistic talent and creative thinking.

### Core Values
- **Accessibility and Inclusion**: Art education for all learners, regardless of ability
- **Artistic Enrichment**: Quality creative arts instruction and self-expression
- **Community Partnership**: Collaboration with local schools and artists
- **Empowerment**: Creative exploration for personal growth

### Target Population
Students with **moderate to severe disabilities** attending public schools in California and New York.

### Programs & Services
- **Dance classes** for K-12 students
- **Creative arts instruction** across multiple disciplines
- **Adult learning classes** (in-person and online)
- **Free local educational opportunities** for children and teens
- **Paid counseling classes** for adult learners with subscription-based online services

### Geographic Scope
- **Primary**: California and New York public school systems
- **Focus for this project**: New York City/State
- **Global reach**: 380 volunteers worldwide supporting emerging artists

### Organizational Impact (Since 2003)
- **Founded**: 2003 by passionate art educators
- **Supporters**: 5 million
- **Volunteers**: 380 worldwide
- **Projects Funded**: 68
- **Website**: https://www.csoaf.org

### Funding Strategy
- Free community programs for underserved populations
- Subscription-based online services for broader reach
- Reliance on institutional and individual patron donations
- **Current Goal**: 500 sponsors with $500,000+ funding target

### Key Search Keywords for Sponsor Finding
When searching for sponsors, always consider CSOAF's core focus areas:
- **Arts education** (dance, creative arts, cultural enrichment)
- **Disability services** (special education, inclusive learning, moderate to severe disabilities)
- **Community healing** and mental health support through arts
- **K-12 education** and youth development
- **Adult education** and lifelong learning
- **Accessibility** and inclusive programming
- **New York** and **California** geographic priorities

## Architecture

### 8-Phase Agent Workflow

The system uses a sequential workflow orchestrated through Claude Code's agent system:

```
Phase 1: Keyword Extraction (keyword-extractor agent)
  Input: User prompt + CSOAF mission context
  Output: JSON with primary/secondary/location/sector keywords
  Model: Claude Haiku 4.5

Phase 2: Web Research (web-researcher agent)
  Input: Keywords from Phase 1
  Output: 15-25 sponsor prospects with relevance scores
  Model: Claude Haiku 4.5

Phase 3: Categorization (categorizer agent)
  Input: Raw sponsor list from Phase 2
  Output: Sponsors organized by type (Corporations/Foundations/NGOs/Government)
  Model: Claude Haiku 4.5

Phase 4: Validation (validator agent)
  Input: Categorized sponsors from Phase 3
  Output: Validated list (quality score ≥5) with quality report
  Model: Claude Sonnet 4.5

Phase 5: Salesforce Integration (salesforce-integration agent)
  Input: Validated sponsor list from Phase 4
  Output: Salesforce CSV, personalized email templates, historical matches
  Model: Claude Haiku 4.5

Phase 6: Engagement Tracking (engagement-tracking agent)
  Input: Salesforce campaign analytics CSV
  Output: Engagement report, hot leads list, follow-up tasks
  Model: Claude Sonnet 4.5

Phase 7: Event Coordination (event-coordination agent)
  Input: Luma event data (registrations, attendance)
  Output: Event summary, attendee follow-ups, no-show re-engagement
  Model: Claude Haiku 4.5

Phase 8: Campaign Orchestration (campaign-orchestrator agent)
  Input: Campaign parameters (goal, location, keywords, type)
  Output: Campaign report, workflow status, consolidated metrics
  Model: Claude Sonnet 4.5
```

### Workflow Stages

**Stage 1: Research & Discovery (Phases 1-4)**
- Automated sponsor discovery and qualification
- Output: Validated sponsor database ready for CRM import

**Stage 2: Campaign Execution (Phase 5 + Manual)**
- Salesforce data preparation and email template generation
- Manual: User imports to Salesforce and executes email campaigns

**Stage 3: Performance Analysis (Phases 6-7)**
- Email engagement tracking and event management
- Output: Prioritized follow-up lists and performance insights

**Stage 4: Coordination & Reporting (Phase 8)**
- End-to-end campaign orchestration and consolidated reporting
- Output: Complete campaign dashboard and ROI analysis

### Agent Definitions

All agents are defined in `.claude/agents/`:

**Research Agents (Phases 1-4):**
- `keyword-extractor.md` - Extracts search keywords from prompts and mission
- `web-researcher.md` - Searches web for sponsor information
- `categorizer.md` - Categorizes sponsors into types
- `validator.md` - Validates data quality and giving programs

**Execution Agents (Phases 5-7):**
- `salesforce-integration.md` - Formats data for Salesforce CRM and generates email templates
- `engagement-tracking.md` - Analyzes campaign metrics and prioritizes follow-ups
- `event-coordination.md` - Manages event registrations, attendance, and follow-ups

**Orchestration Agent (Phase 8):**
- `campaign-orchestrator.md` - Coordinates end-to-end workflow from research to follow-up

**IMPORTANT**: All agents should always incorporate CSOAF's mission, values, and focus areas (listed above) when extracting keywords, researching sponsors, and validating alignment. The organization profile section is the authoritative source for mission context.

### Custom Skills

Located in `.claude/commands/`:

**Sponsor Research Skills:**
- `search-keywords.md` - Keyword extraction from user prompts
- `sponsor-format.md` - Format results as reports/CSV/JSON
- `validate-results.md` - Quality validation workflow

**Platform Integration Skills:**
- `mailchimp-import.md` - Import historical donor data from Mailchimp for donor relationship continuity
- `givelively-sync.md` - Track online donations and campaign progress from GiveLively
- `run-campaign.md` - Execute complete 5-step fundraising workflow end-to-end

**Git Workflow Skills:**
- `sync.md` - Quick commit and push with auto-generated messages
- `checkpoint.md` - Create timestamped WIP commits (local only)
- `quick-commit.md` - Smart commits with user-approved messages
- `save-report.md` - Specialized command for committing sponsor reports

## Project Structure

```
sponsor-finder/
├── .claude/
│   ├── agents/              # Agent definitions (keyword-extractor, web-researcher, etc.)
│   ├── commands/            # Custom skills for sponsor workflows
│   └── PLAN_*.md           # Planning documents for features
├── docs/                   # Generated sponsor reports and documentation
│   ├── 00-READ-ME-FIRST.md # Start here for navigation
│   ├── Healing_NY_Sponsor_Database.md
│   ├── CATEGORIZATION_*.md  # Categorization analysis documents
│   └── orchestrator.py      # Blueprint for orchestration (conceptual)
├── specs/
│   └── sponsor-finder-spec.md  # System requirements and architecture
└── CLAUDE.md               # This file
```

## How to Execute the Workflow

### Basic Search
To run a complete sponsor search:

1. **Invoke the workflow** with a prompt:
   ```
   "Find sponsors for CSOAF's arts education programs for students with disabilities in NYC with $50k+ grants"
   ```

2. **The system will**:
   - Extract keywords (arts education, disability services, accessibility, NYC, $50k+)
   - Search for matching sponsors online
   - Categorize by type (Foundation/Corporation/NGO/Government)
   - Validate data quality and giving programs
   - Generate formatted reports in `docs/`

### Understanding the Orchestration

The `docs/orchestrator.py` file is a **blueprint** showing the intended workflow. It's conceptual Python code demonstrating how the agents should be coordinated. In practice, you execute this workflow by:
- Calling each agent sequentially through Claude Code's Task tool
- Passing output from one phase as input to the next
- Using the agent definitions in `.claude/agents/`

### Output Formats

The system generates multiple output formats:
- **Markdown Reports**: Detailed analysis with rankings and contact info
- **CSV Export**: Spreadsheet-compatible format for CRM systems
- **JSON Format**: Structured data for programmatic access

## Key Files to Know

### For Understanding Requirements
- `specs/sponsor-finder-spec.md` - Full system specification
- `docs/00-READ-ME-FIRST.md` - Navigation guide for generated reports

### For Agent Development
- `.claude/agents/*.md` - Agent role definitions and behavior
- `.claude/commands/*.md` - Custom workflow skills

### For Planning
- `.claude/PLAN_CSV_EXPORT_FEATURE.md` - CSV export feature planning doc

## Success Criteria

- Find 20+ high-quality sponsors per search
- Average relevance score ≥7/10
- Complete workflow in <7 minutes
- Zero false positives (all sponsors are legitimate)
- Validation score ≥5 for all included sponsors

## Data Quality Standards

### Validation Requirements
- Organization exists with legitimate online presence
- Active giving program (grants awarded in last 2 years)
- Contact information verified (website, email, phone)
- Mission alignment with arts education/disability services/accessibility/community healing
- Geographic match (NYC/NY or California preferred)

### Scoring System
- **9-10**: Perfect match, all criteria met, verified info
- **7-8**: Good match, most criteria met, minor gaps
- **5-6**: Possible match, some gaps in verification
- **Below 5**: Excluded from results

## Sponsor Categories

1. **Foundations**: Private/family/corporate foundations (grantmaking)
   - Look for: Arts education, disability services, special education, accessibility funders
2. **Corporations**: Companies with CSR/philanthropic programs
   - Look for: Tech companies, arts/media companies, healthcare companies supporting disability initiatives
3. **NGOs/Nonprofits**: Collaborative funding partners
   - Look for: Arts organizations, disability advocacy groups, education reform organizations
4. **Government**: Municipal/state grant programs
   - Look for: NEA, state arts councils, special education funding, NYC/NY/CA grants
5. **Individual Donors**: High-net-worth individuals (rare)
   - Look for: Arts patrons, disability advocates, education philanthropists

## Working with This Codebase

### When Adding New Features
1. Review existing agent definitions in `.claude/agents/`
2. Check if workflow needs new phase or enhancement to existing
3. Create planning document in `.claude/` if implementing major feature
4. Update this CLAUDE.md if architecture changes

### When Debugging Searches
1. Check keyword extraction output (Phase 1)
2. Verify web search results (Phase 2)
3. Review categorization accuracy (Phase 3)
4. Examine validation scores (Phase 4)

### When Modifying Agents
- Agent behavior is defined in their `.md` files
- Model selection: Haiku 4.5 for speed, Sonnet 4.5 for quality
- Allowed tools specified in agent frontmatter
- Test changes with diverse prompts (short/detailed, different sectors)

## Common Tasks

### Run a Complete Search
Execute all 4 phases sequentially, passing outputs between phases.

### Format Existing Results
Use `sponsor-format` skill to convert raw data to reports/CSV.

### Validate Data Quality
Run validator agent on categorized sponsor list to score and filter.

### Extract Keywords Only
Run keyword-extractor agent standalone to test keyword extraction logic.

### Git Commands

The project includes custom Git commands optimized for the sponsor research workflow:

**`/sync` - Quick Commit and Push**
- Stages all changes, generates commit message, and pushes in one command
- Prompts for confirmation if `docs/` reports are included
- Use when: You want to save and share changes immediately

**`/checkpoint` - Save Work in Progress**
- Creates timestamped WIP commits locally (does not push)
- Use when: Experimenting with agents, saving intermediate states

**`/quick-commit` - Smart Commit with User Approval**
- Generates context-aware commit message based on what changed
- Lets you approve or edit the message before committing
- Does not push (you decide when to push separately)
- Use when: You want control over the commit message

**`/save-report` - Commit Sponsor Reports**
- Scans `docs/` for new/modified reports
- Shows previews with titles and summaries
- Lets you select which reports to commit
- Generates descriptive commit messages
- Optional push after committing
- Use when: Committing sponsor research results

**Git Command Workflow Examples:**

```
# After generating sponsor reports
/save-report           # Select and commit specific reports

# Quick save and push all changes
/sync                  # Auto-commit and push everything

# Experimental work (local only)
/checkpoint            # Save WIP without pushing

# Controlled commit with review
/quick-commit          # Review and approve commit message
git push              # Push when ready
```

## Notes

- No package.json, requirements.txt, or Makefile - this is a Claude Code agent-based system
- All execution happens through Claude Code's agent orchestration
- Python file (`docs/orchestrator.py`) is illustrative, not executable code
- Focus is on AI workflow design, not traditional software development
- Reports and data are generated in `docs/` directory
