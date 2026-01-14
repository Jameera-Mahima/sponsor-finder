Execute the entire 5-step fundraising workflow end-to-end with a single command, orchestrating all agents and generating consolidated campaign reports.

## Purpose
Run a complete sponsor discovery and campaign management workflow for CSOAF fundraising initiatives. This command coordinates all agents (keyword extraction, web research, categorization, validation, Salesforce integration, engagement tracking, and event coordination) to deliver a comprehensive campaign strategy.

## Usage
`/run-campaign "<campaign_description>" <goal_amount> [options]`

**Required Parameters**:
- `campaign_description` (string, in quotes): What are you fundraising for?
  - Example: "Arts education programs for students with disabilities in NYC"
- `goal_amount` (number): Target fundraising amount in dollars
  - Example: 500000 (for $500,000)

**Optional Parameters**:
- `--location <location>` : Geographic focus (default: "New York")
- `--mailchimp-key <api_key>` : Import historical donors from Mailchimp
- `--givelively-id <campaign_id>` : Track donations from GiveLively
- `--luma-id <event_id>` : Include event data from Luma
- `--output-dir <path>` : Custom output directory (default: `docs/campaign_YYYYMMDD/`)

**Examples**:
```
/run-campaign "Arts education for disabled students in NYC" 500000

/run-campaign "Mental health healing through creative arts" 250000 --location "California"

/run-campaign "Holiday fundraiser for K-12 dance programs" 100000 --mailchimp-key YOUR_KEY --givelively-id abc123

/run-campaign "Community art exhibition supporting disabled children" 75000 --luma-id xyz789 --location "New York City"
```

## Execution Logging

**IMPORTANT**: This command automatically logs all agent executions for analysis and debugging.

**Logging System**:
- **Campaign logs**: `logs/campaigns/<campaign_id>/` - Full execution details (JSON + Markdown)
- **Agent logs**: `logs/agents/<agent_name>/runs/` - Individual agent execution history
- **Live dashboard**: `logs/dashboard/index.html` - Real-time monitoring (open in browser)
- **Performance metrics**: Tokens, API calls, duration, cost estimates
- **Error tracking**: All errors and warnings with context

**Integration**:
```python
# Import logging system
from logs.logging.logger import CampaignLogger

# Initialize logger
logger = CampaignLogger(
    campaign_name="Christmas Education Campaign",
    parameters={
        'description': campaign_description,
        'goal_amount': goal_amount,
        'location': location
    }
)

# For each agent execution:
start_time = datetime.utcnow().isoformat()
agent_output = execute_agent(...)  # Run agent via Task tool
end_time = datetime.utcnow().isoformat()

logger.log_agent_execution(
    agent_name='keyword-extractor',
    phase='Phase 1: Research',
    output_text=agent_output,
    start_time=start_time,
    end_time=end_time
)

# Finalize logging
logger.finalize()
```

**View Logs**:
- Open `logs/dashboard/index.html` in browser for live monitoring
- Check `logs/campaigns/<campaign_id>/campaign_log.md` for human-readable summary
- Query `logs/campaigns/<campaign_id>/*.json` files for programmatic analysis

**See**: `logs/logging/example_usage.py` for complete integration example

---

## Processing Steps

The command orchestrates 5 sequential phases, automatically handling data flow between agents:

---

### **Phase 1: Research & Discovery**

**Objective**: Find and qualify potential sponsors matching campaign goals

**Step 1.1: Extract Keywords**
- Input: Campaign description + CSOAF mission statement
- Agent: `keyword-extractor` (Haiku 4.5)
- Output: JSON with primary/secondary/location/sector keywords
- Example keywords: "arts education", "disability services", "accessibility", "NYC", "$50k+ grants"

**Step 1.2: Web Research**
- Input: Keywords from Step 1.1
- Agent: `web-researcher` (Haiku 4.5)
- Tools: web_search, web_fetch
- Output: 15-25 sponsor prospects with relevance scores (1-10)
- Success Criteria: Minimum 15 prospects identified

**Step 1.3: Validate Data Quality**
- Input: Raw sponsor list from Step 1.2
- Agent: `validator` (Sonnet 4.5)
- Output: Filtered list with quality scores ≥5
- Validation checks: Existence, contact info, giving programs, mission alignment

**Phase 1 Output Files**:
- `sponsor_research_report.md` - Detailed findings with all prospects
- `keywords_used.json` - Extracted keywords for reference
- `validation_log.md` - Quality assessment details

---

### **Phase 2: Prospect Identification**

**Objective**: Organize and rank sponsors for strategic outreach

**Step 2.1: Categorize by Type**
- Input: Validated sponsors from Phase 1
- Agent: `categorizer` (Haiku 4.5)
- Output: Sponsors grouped by type (Corporations/Foundations/NGOs/Government/Individuals)

**Step 2.2: Rank by Relevance**
- Input: Categorized sponsors
- Agent: `validator` (Sonnet 4.5)
- Scoring: 1-10 scale based on mission alignment, geographic fit, giving capacity, accessibility
- Output: Ranked list with top 20 highlighted

**Step 2.3: Format for Export**
- Input: Ranked sponsors
- Skill: `sponsor-format`
- Output Formats:
  - Markdown report (human-readable)
  - CSV (Salesforce import-ready)
  - JSON (programmatic access)

**Phase 2 Output Files**:
- `salesforce_import.csv` - CRM-ready contact list
- `ranked_sponsors.md` - Detailed sponsor profiles with rankings
- `sponsors_by_category.json` - Structured data by type

---

### **Phase 3: Outreach Preparation**

**Objective**: Enrich sponsor data with historical context and prepare personalized outreach

**Step 3.1: Import Historical Donors** (Optional)
- Condition: If `--mailchimp-key` provided
- Skill: `/mailchimp-import`
- Output: Historical donor database with engagement metrics

**Step 3.2: Cross-Reference New Prospects with Historical Data**
- Input: New sponsor list + Historical donor database
- Processing: Match by organization name and email domain
- Output: Flag prospects who are past donors (warm leads)

**Step 3.3: Generate Personalized Email Templates**
- Input: Categorized sponsors + Historical matches
- Agent: `salesforce-integration` (Haiku 4.5)
- Output: Email templates customized by:
  - Sponsor type (Foundation vs. Corporation vs. NGO)
  - Giving history (new prospect vs. repeat donor)
  - Geographic location
  - Mission alignment specifics

**Phase 3 Output Files**:
- `email_templates.md` - Personalized outreach templates by sponsor type
- `historical_matches.json` - Prospects identified as past donors
- `outreach_priority_list.md` - Ranked by warmth (past donors first)

---

### **Phase 4: Tracking & Analysis Setup**

**Objective**: Establish monitoring systems for campaign performance

**Step 4.1: Sync Donation Data** (Optional)
- Condition: If `--givelively-id` provided
- Skill: `/givelively-sync`
- Output: Current donation status, velocity, top donors
- Metrics: Goal progress, donation velocity, projected completion date

**Step 4.2: Create Engagement Tracking Template**
- Input: Salesforce import CSV from Phase 2
- Agent: `engagement-tracking` (Sonnet 4.5)
- Output: Template for tracking email opens/clicks/responses
- Instructions: How to export Salesforce analytics for analysis

**Step 4.3: Establish Baseline Metrics**
- Document starting point:
  - Current funds raised: $X (if GiveLively connected)
  - Prospects identified: XX sponsors
  - Outreach target: XX emails to send
  - Expected response rate: ~5% (nonprofit benchmark)

**Phase 4 Output Files**:
- `campaign_progress_report.md` - Current fundraising status (if GiveLively connected)
- `tracking_instructions.md` - How to monitor engagement via Salesforce
- `engagement_template.csv` - Template for logging email responses

---

### **Phase 5: Follow-Up Planning**

**Objective**: Create actionable follow-up strategy for donor cultivation

**Step 5.1: Fetch Event Data** (Optional)
- Condition: If `--luma-id` provided
- Agent: `event-coordination` (Haiku 4.5)
- Input: Luma event ID
- Output: Registration, attendance, and donation data
- Metrics: Attendance rate, conversion rate, revenue per attendee

**Step 5.2: Generate Prioritized Follow-Up Tasks**
- Input:
  - Email engagement data (opens/clicks)
  - Donation data (if GiveLively connected)
  - Event attendance (if Luma connected)
- Agent: `engagement-tracking` (Sonnet 4.5)
- Output: Hot/Warm/Cold lead classification with next steps

**Step 5.3: Create Thank-You and Re-Engagement Lists**
- Input: Donor data from all sources
- Output:
  - Thank-you list for donors (prioritized by gift size)
  - Re-engagement list for lapsed donors
  - Follow-up list for interested prospects (opened emails, attended events)

**Phase 5 Output Files**:
- `follow_up_plan.md` - Prioritized action items for marketing team
- `hot_leads.json` - Top 20% engaged prospects with talking points
- `event_summary.md` - Event metrics and attendee analysis (if Luma connected)
- `donor_thank_you_list.json` - Prioritized outreach list (if donations tracked)

---

### **Master Orchestration & Reporting**

**Objective**: Consolidate all outputs into executive-level strategic report

**Agent**: `campaign-orchestrator` (Sonnet 4.5)

**Step M.1: Data Consolidation**
- Aggregate outputs from all 5 phases
- Calculate consolidated metrics:
  - Total prospects identified vs. target (500 sponsors)
  - Current funds raised vs. goal (if tracking enabled)
  - Engagement rates (if tracking enabled)
  - Event conversion (if event connected)

**Step M.2: ROI Projection**
- Estimate potential revenue:
  - Top 10 sponsors × $50k average = $500k potential
  - Top 20 sponsors × $25k average = $500k potential
  - Assume 5-10% conversion rate (nonprofit standard)
  - Projected raise: $25k-$100k from this research

**Step M.3: Lessons Learned & Optimization**
- Identify strongest sponsor categories (most prospects with high scores)
- Recommend focus areas for follow-up
- Suggest keywords for future searches
- Benchmark performance vs. CSOAF goals

**Step M.4: Next Steps Action Plan**
- Create timeline for outreach (weeks 1-4)
- Assign responsibilities (Development Director, Marketing Team, Executive Director)
- Set milestones (email send dates, follow-up deadlines, donor meeting goals)

**Master Output Files**:
- `CAMPAIGN_EXECUTIVE_SUMMARY.md` - Comprehensive overview for leadership
- `workflow_status.json` - Phase-by-phase completion tracker
- `consolidated_metrics.md` - Dashboard with all KPIs
- `next_steps_action_plan.md` - Timeline and responsibilities

---

## Output Directory Structure

All files organized in timestamped campaign folder:

```
docs/
└── campaign_20260113/
    ├── CAMPAIGN_EXECUTIVE_SUMMARY.md        ⭐ START HERE
    ├── phase1_research/
    │   ├── sponsor_research_report.md
    │   ├── keywords_used.json
    │   └── validation_log.md
    ├── phase2_identification/
    │   ├── salesforce_import.csv            🔄 IMPORT TO SALESFORCE
    │   ├── ranked_sponsors.md
    │   └── sponsors_by_category.json
    ├── phase3_outreach/
    │   ├── email_templates.md               📧 USE FOR OUTREACH
    │   ├── historical_matches.json
    │   └── outreach_priority_list.md
    ├── phase4_tracking/
    │   ├── campaign_progress_report.md      (if GiveLively)
    │   ├── tracking_instructions.md
    │   └── engagement_template.csv
    ├── phase5_followup/
    │   ├── follow_up_plan.md                📋 ACTION ITEMS
    │   ├── hot_leads.json
    │   ├── event_summary.md                 (if Luma)
    │   └── donor_thank_you_list.json        (if GiveLively)
    └── master_reports/
        ├── workflow_status.json
        ├── consolidated_metrics.md
        └── next_steps_action_plan.md
```

## CAMPAIGN_EXECUTIVE_SUMMARY.md Format

The executive summary provides a high-level overview for leadership:

```markdown
# Campaign Executive Summary
## [Campaign Name]

**Generated**: January 13, 2026
**Goal**: $500,000
**Geographic Focus**: New York City

---

## Quick Stats

- **Prospects Identified**: 47 sponsors (Goal: 20+) ✅
- **High-Priority Targets**: 12 sponsors (score ≥8)
- **Current Funds Raised**: $127,250 (25.5% of goal) (if GiveLively)
- **Projected Completion**: June 18, 2026 (if GiveLively)
- **Event Attendance**: 89% (126/142 registrants) (if Luma)

---

## Top 10 Recommended Sponsors

1. **Robin Hood Foundation** (Foundation, Score: 9.5)
   - Contact: grants@robinhood.org | (212) 555-0100
   - Giving Range: $50k-$250k
   - Why: NYC-based, funds education for underserved youth, disability focus
   - Action: Submit LOI by Feb 1 (rolling deadline)

2. **The Pinkerton Foundation** (Foundation, Score: 9.2)
   - Contact: info@thepinkertonfoundation.org | (212) 555-0200
   - Giving Range: $25k-$100k
   - Why: NYC priority, arts education, special needs programming
   - Action: Full proposal due March 15

[... continues for top 10]

---

## Historical Donor Insights (if Mailchimp connected)

- **Total Historical Donors**: 1,247
- **Active (last 12 months)**: 523 (41.9%)
- **Lapsed (12+ months)**: 312 (25.0%)
- **High-Value Donors**: 89 (7.1%)

**Key Finding**: 15 of our identified prospects are past donors (warm leads!)
- Jane Doe (jane.doe@robinhood.org) - Gave $5,000 in 2023
- Michael Chen (m.chen@pinkerton.org) - Gave $2,500 annually 2021-2024

**Recommendation**: Prioritize these 15 warm leads with personalized "thank you for past support" messaging.

---

## Fundraising Progress (if GiveLively connected)

**Status**: ⚠️ Behind Schedule

- **Goal**: $500,000
- **Raised**: $127,250 (25.5%)
- **Remaining**: $372,750
- **Velocity**: $2,850/day
- **Needed Velocity**: $4,841/day to meet deadline

**Top Donors**:
1. Jane Doe - $5,000 (New donor, needs thank-you call)
2. John Smith - $2,500 (Repeat donor, up from $1,500 last year)

**Action Required**: Accelerate outreach to meet goal. Launch urgency email campaign to lapsed donors.

---

## Event Metrics (if Luma connected)

**Event**: Arts Exhibition Fundraiser
**Date**: December 15, 2024

- **Registrations**: 142
- **Attendance**: 126 (89% attendance rate)
- **Donations Collected**: $18,500
- **Average Donation**: $147 per attendee

**Key Insight**: Event attendees gave 2.5x more than online-only donors.

**Recommendation**: Plan quarterly events to maintain momentum.

---

## Next Steps (Immediate Actions)

### Week 1: Outreach Preparation
- [ ] Import `salesforce_import.csv` to Salesforce (47 contacts)
- [ ] Review and customize `email_templates.md` for each sponsor type
- [ ] Schedule personal calls to 15 warm leads (past donors)

### Week 2: Email Campaign Launch
- [ ] Send personalized emails to all 47 prospects
- [ ] Track opens/clicks in Salesforce
- [ ] Follow up within 48 hours with engaged prospects (opened email)

### Week 3: Follow-Up & Meetings
- [ ] Call top 12 high-priority sponsors (score ≥8)
- [ ] Schedule meetings with interested prospects
- [ ] Send proposals to foundations with open deadlines

### Week 4: Donor Cultivation
- [ ] Thank-you calls to all major donors ($1,000+)
- [ ] Send impact reports to repeat donors
- [ ] Re-engagement campaign for lapsed donors

### Ongoing: Monitoring
- [ ] Update GiveLively progress weekly
- [ ] Review Salesforce engagement metrics bi-weekly
- [ ] Adjust outreach strategy based on response rates

---

## Lessons Learned

**What Worked Well**:
- Keyword extraction identified highly relevant prospects
- 15 warm leads discovered (past donors) - huge advantage
- Event attendees showed strong giving patterns

**What Could Improve**:
- Need faster donation velocity to meet goal
- Lapsed donor re-engagement should start earlier
- Consider diversifying beyond foundations (more corporate sponsors)

**Keywords for Future Searches**:
- "arts education equity" (identified 8 strong prospects)
- "disability services NYC" (high mission alignment)
- "K-12 creative learning" (emerging focus area)

---

## ROI Projection

**Investment**: ~40 hours staff time for research and outreach
**Potential Return**:
- Top 10 sponsors (assuming 30% conversion): 3 grants × $50k avg = **$150k**
- Top 20 sponsors (assuming 15% conversion): 3 grants × $25k avg = **$75k**
- **Total Projected**: $150k-$225k from this research cycle

**ROI**: 3,750x-5,625x return on time invested

---

## Team Responsibilities

**Development Director**:
- Lead outreach to top 10 sponsors
- Schedule and conduct foundation meetings
- Manage grant proposal submissions

**Marketing Team**:
- Execute email campaigns via Salesforce
- Monitor engagement metrics
- Design donor thank-you materials

**Executive Director**:
- Personal calls to transformational donors ($5,000+)
- Attend meetings with high-priority prospects
- Sign-off on all grant proposals

---

## Campaign Dashboard

(Update weekly)

| Metric | Current | Goal | % Complete |
|--------|---------|------|----------|
| Prospects Identified | 47 | 20+ | 235% ✅ |
| Funds Raised | $127,250 | $500,000 | 25.5% |
| Emails Sent | 0 | 47 | 0% |
| Meetings Scheduled | 0 | 12 | 0% |
| Proposals Submitted | 0 | 10 | 0% |
| Grants Awarded | 0 | 5 | 0% |

**Next Update**: January 20, 2026
```

---

## Success Criteria

Each phase must meet these standards:

**Phase 1: Research & Discovery**
- ✅ Minimum 15 validated sponsors identified
- ✅ All sponsors have quality scores ≥5
- ✅ Contact information verified (website, email, phone)

**Phase 2: Prospect Identification**
- ✅ Sponsors categorized by type
- ✅ Relevance scores calculated (1-10 scale)
- ✅ Salesforce import CSV generated and validated

**Phase 3: Outreach Preparation**
- ✅ Email templates customized by sponsor type
- ✅ Historical donor matches identified (if Mailchimp connected)
- ✅ Outreach priority list ranked

**Phase 4: Tracking Setup**
- ✅ Current campaign status documented
- ✅ Tracking instructions provided
- ✅ Engagement template created

**Phase 5: Follow-Up Planning**
- ✅ Follow-up tasks prioritized by urgency
- ✅ Hot leads identified with talking points
- ✅ Thank-you lists generated (if donations tracked)

**Master Orchestration**
- ✅ Executive summary provides clear action items
- ✅ All phases completed successfully (no critical errors)
- ✅ Output files organized in logical directory structure
- ✅ Workflow completed in <10 minutes

---

## Error Handling

**Phase Failure Handling**:
- If Phase 1 fails (no sponsors found): Expand keywords and retry
- If Phase 3 fails (Mailchimp API error): Continue without historical data, log warning
- If Phase 4 fails (GiveLively error): Continue without donation tracking, note in report
- If Phase 5 fails (Luma error): Skip event data, continue with other follow-up tasks

**Partial Success Protocol**:
- Generate report even if some phases fail
- Mark failed phases clearly in workflow_status.json
- Provide manual workarounds in executive summary
- Log all errors to `error_log.txt` in campaign directory

**Quality Assurance**:
- If <15 sponsors found: Warning message + suggestion to broaden search
- If all relevance scores <7: Warning about weak prospects + refine keywords
- If Salesforce CSV validation fails: Provide corrected format instructions
- If goal velocity impossible: Flag unrealistic goal + adjust timeline recommendation

---

## Integration with Existing System

This command is the **master orchestrator** that ties together:

**Agents Used**:
1. `keyword-extractor` - Phase 1
2. `web-researcher` - Phase 1
3. `categorizer` - Phase 2
4. `validator` - Phases 1 & 2
5. `salesforce-integration` - Phase 3
6. `engagement-tracking` - Phases 4 & 5
7. `event-coordination` - Phase 5
8. `campaign-orchestrator` - Master coordination

**Skills Used**:
1. `search-keywords` - Phase 1
2. `sponsor-format` - Phase 2
3. `validate-results` - Phases 1 & 2
4. `/mailchimp-import` - Phase 3 (if --mailchimp-key provided)
5. `/givelively-sync` - Phase 4 (if --givelively-id provided)

**Data Flow**:
```
Campaign Description
    ↓
Phase 1: Keywords → Web Research → Validation
    ↓
Phase 2: Categorization → Ranking → CSV Export
    ↓
Phase 3: Historical Match → Email Templates → Priority List
    ↓
Phase 4: Donation Sync → Tracking Setup → Baseline Metrics
    ↓
Phase 5: Event Data → Follow-Up Tasks → Thank-You Lists
    ↓
Master: Consolidation → Executive Summary → Action Plan
```

---

## Example Complete Invocation

```
/run-campaign "Mental health healing through creative arts for students with disabilities in NYC" 500000 --mailchimp-key sk_abc123def --givelively-id campaign_xyz789 --luma-id event_123abc
```

**What This Does**:
1. Searches for sponsors matching "mental health + creative arts + disability services + NYC"
2. Identifies 20-50 prospects (foundations, corporations, government grants)
3. Imports historical donors from Mailchimp to find warm leads
4. Syncs current donations from GiveLively campaign xyz789
5. Fetches event attendance from Luma event 123abc
6. Generates complete campaign strategy with:
   - Salesforce import of 20-50 prospects
   - Personalized email templates
   - Current fundraising progress ($X raised / $500k goal)
   - Event conversion metrics
   - Follow-up action plan prioritized by urgency
7. Creates executive summary with ROI projection and next steps

**Time to Complete**: 7-10 minutes

**Output**: Complete campaign folder with 15-20 files across 6 subdirectories

---

## Post-Execution Workflow

**After running `/run-campaign`**:

1. **Read** `CAMPAIGN_EXECUTIVE_SUMMARY.md` first
2. **Import** `phase2_identification/salesforce_import.csv` to Salesforce
3. **Customize** `phase3_outreach/email_templates.md` with campaign-specific details
4. **Send** personalized emails to all prospects via Salesforce
5. **Track** engagement using `phase4_tracking/tracking_instructions.md`
6. **Follow up** using `phase5_followup/follow_up_plan.md` action items
7. **Monitor** progress weekly by re-running `/givelively-sync` (if connected)
8. **Cultivate** donors using `donor_thank_you_list.json` priorities
9. **Refine** strategy based on `lessons_learned` in executive summary
10. **Report** results to leadership using `consolidated_metrics.md`

---

This command provides a complete, end-to-end campaign management solution for CSOAF fundraising initiatives.
