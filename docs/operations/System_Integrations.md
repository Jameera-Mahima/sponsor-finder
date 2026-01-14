# System Integrations

This document outlines how different platforms connect and integrate to support the fundraising workflow.

## Salesforce Integration (Core Hub)

**Role:** Central contact and campaign management system

**Capabilities:**
- Stores all sponsor and donor contact details
- Manages email campaign execution
- Tracks engagement metrics (opens, clicks, responses)
- Generates reports for stakeholders
- Coordinates meeting scheduling and follow-ups

**Integration Points:**
- Connects with Mailchimp for historical data access
- Integrates with Luma for event participant tracking
- Links with GiveLively for donation data

## Mailchimp Integration

**Role:** Historical data repository

**Purpose:**
- Provides access to past sponsor information
- Maintains database of previous campaign contacts
- Preserves donor history and engagement patterns
- Supports data migration to Salesforce

**Technical Integration:**
- **Command:** `/mailchimp-import` - Automated import via Mailchimp API v3.0
- **Authentication:** API key (Bearer token)
- **Endpoint:** `GET /3.0/lists/{list_id}/members`
- **Rate Limits:** 10 requests/second
- **Alternative:** Manual CSV upload if API unavailable

**Data Extracted:**
- Contact information (name, email, phone)
- Engagement metrics (open rates, click rates, member rating)
- Campaign participation history
- Subscription status and tags
- Last engagement date

**Output Files:**
- `mailchimp_import.csv` - Salesforce-ready contact list
- `historical_donor_analysis.md` - Engagement report with segmentation
- `duplicate_contacts.json` - Flagged duplicates for review

**Segmentation:**
- **Active:** Engaged in last 12 months
- **Lapsed:** No engagement in 12+ months
- **High-value:** Member rating 4-5 stars or major donor tags
- **Unsubscribed:** Cleaned or unsubscribed status

**Integration Points:**
- Syncs contact lists with Salesforce via CSV import
- Shares historical campaign performance data
- Enables comparison of donor behavior across campaigns
- Cross-references with new prospects to identify warm leads

## Luma Integration

**Role:** Event participant management

**Purpose:**
- Tracks participant registration for events
- Records attendance information during events
- Identifies registered vs. actual attendees
- Enables post-event communication workflows

**Integration Points:**
- Provides attendance data to Salesforce
- Supports automated follow-up email campaigns
- Shares participant contact information for CRM updates

## GiveLively Integration

**Role:** Online donation processing

**Purpose:**
- Manages campaign pages and descriptions
- Processes online donations
- Tracks fundraising progress toward goals
- Collects donor information and preferences

**Technical Integration:**
- **Command:** `/givelively-sync` - Track donations and campaign progress
- **Authentication:** API key or manual CSV export
- **Primary Method:** CSV export (most reliable, no API restrictions)
- **Alternative:** API integration if available for enterprise accounts
- **Update Frequency:** Weekly during active campaigns

**Data Extracted:**
- Donor information (name, email, donation amount, date)
- Campaign attribution and donation frequency
- Payment status (completed, pending, failed)
- Donor messages and preferences
- Anonymous donor flags

**Output Files:**
- `donations.csv` - Salesforce-ready donation records
- `campaign_progress_report.md` - Real-time fundraising dashboard
- `donor_thank_you_list.json` - Prioritized outreach list

**Metrics Tracked:**
- **Goal Progress:** Total raised vs. target (% complete)
- **Donation Velocity:** Per day/week, projected completion date
- **Donor Statistics:** Average gift size, retention rate, new vs. repeat
- **Donation Distribution:** By size category ($1-$50, $51-$100, etc.)

**Donor Tiers:**
- **Transformational:** $5,000+
- **Large:** $1,000-$4,999
- **Regular:** Under $1,000

**Thank-You Prioritization:**
- **Immediate Personal Outreach:** Transformational donors (phone call within 24 hours)
- **High Priority Email:** Large donors (personalized email within 48 hours)
- **Standard Thank-You:** Regular donors (automated email within 24 hours)

**Integration Points:**
- Sends donation data to Salesforce via CSV import
- Updates donor records with contribution amounts
- Provides real-time campaign performance metrics
- Enables donors to contribute without event attendance
- Cross-references with Mailchimp data to identify new vs. repeat donors

## Integration Workflow

**Data Flow:**
1. **Historical Data:** Mailchimp → Salesforce (contact lists, past campaigns)
2. **Event Management:** Luma → Salesforce (registrations, attendance)
3. **Donation Processing:** GiveLively → Salesforce (donor info, amounts)
4. **Campaign Execution:** Salesforce → All platforms (coordinated outreach)
5. **Reporting:** All platforms → Salesforce (consolidated analytics)

**Benefits:**
- Unified contact database across all platforms
- Seamless data flow between systems
- Comprehensive tracking of donor journey
- Single source of truth for reporting and analysis

---

## Full Workflow Orchestration

### `/run-campaign` Command

**Purpose:** Execute complete 5-step fundraising workflow with single command

**Integration Flow:**
```
Campaign Description + Goal
    ↓
Phase 1: Research & Discovery
    → keyword-extractor agent
    → web-researcher agent
    → validator agent
    ↓
Phase 2: Prospect Identification
    → categorizer agent
    → validator agent
    → sponsor-format skill
    ↓
Phase 3: Outreach Preparation
    → /mailchimp-import (optional)
    → salesforce-integration agent
    → Cross-reference prospects with historical donors
    ↓
Phase 4: Tracking & Analysis
    → /givelively-sync (optional)
    → engagement-tracking agent
    → Baseline metrics established
    ↓
Phase 5: Follow-Up Planning
    → event-coordination agent (if Luma connected)
    → engagement-tracking agent
    → Follow-up tasks prioritized
    ↓
Master Orchestration
    → campaign-orchestrator agent
    → Consolidated executive summary
    → ROI projection and action plan
```

**Optional Integrations:**
- `--mailchimp-key` : Import historical donors for warm lead identification
- `--givelively-id` : Track current campaign donations and velocity
- `--luma-id` : Include event registration and attendance data

**Output:**
- Complete campaign folder (`docs/campaign_YYYYMMDD/`)
- Executive summary with top prospects and action items
- Salesforce import CSV with 20-50 qualified sponsors
- Personalized email templates by sponsor type
- Follow-up task list prioritized by urgency
- Campaign metrics dashboard (if tracking enabled)

**Typical Workflow Timeline:**
1. **Day 1:** Run `/run-campaign` command (7-10 minutes)
2. **Day 2:** Review executive summary, import to Salesforce
3. **Week 1:** Send personalized emails to all prospects
4. **Week 2:** Follow up with engaged prospects (opened emails)
5. **Week 3:** Schedule meetings with hot leads
6. **Week 4:** Submit grant proposals and continue cultivation
7. **Ongoing:** Weekly `/givelively-sync` to monitor progress

**Success Metrics:**
- 20+ qualified sponsors identified per search
- 5-10% email response rate (nonprofit benchmark)
- 2-3 meetings scheduled with high-priority prospects
- 1-2 grant proposals submitted within first month
- ROI: 3,750x-5,625x return on staff time invested
