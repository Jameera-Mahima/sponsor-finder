# Fundraising Workflow

This document outlines the step-by-step process for executing a fundraising campaign from research to follow-up.

## Step 1: Research & Discovery

**Extract Keywords**
- Analyze campaign description to identify key themes
- Incorporate community foundation mission statement
- Generate search terms for sponsor research

**Web Research**
- Search for foundations aligned with campaign goals
- Identify companies and corporations matching keywords
- Research organizations with relevant philanthropic programs

## Step 2: Prospect Identification

**Create Ranked List**
- Compile potential sponsors from research phase
- Rank prospects based on:
  - **Past donation history:** Previous giving amounts and frequency
  - **Mission alignment:** Match between organization's goals and campaign cause
  - **Geographic relevance:** Focus on organizations active in target location

**Categorization**
- Group by sponsor type (foundations, corporations, NGOs)
- Note specific offerings or focus areas of each company

## Step 3: Outreach

**Data Preparation (Automated)**
- **Agent**: `salesforce-integration`
- Converts validated sponsor data to Salesforce CSV format
- Generates personalized email templates by sponsor type
- Identifies historical matches from Mailchimp data
- **Output**: Salesforce-ready CSV + customized email templates

**Email Campaign Execution (Manual)**
- Import CSV to Salesforce
- Send personalized emails via Salesforce using generated templates
- Customize messaging based on:
  - Organization type and size
  - Past giving history (flagged by agent)
  - Specific alignment with campaign goals
- Include categorization details and company-specific talking points
- Target all relevant contacts in the database

## Step 4: Tracking & Analysis

**Monitor Engagement (Manual)**
- Track email opens using Salesforce analytics
- Monitor click-through rates on campaign links
- Record responses and inquiries
- Measure overall engagement levels
- Export campaign analytics from Salesforce

**Generate Reports (Automated)**
- **Agent**: `engagement-tracking`
- Analyzes Salesforce campaign export data
- Calculates engagement scores (Hot/Warm/Cold classification)
- Identifies top 20% high-value prospects
- Benchmarks performance against nonprofit standards
- Flags engagement anomalies and patterns
- **Output**: Engagement report + hot leads list + prioritized follow-up tasks

## Step 5: Follow-up

**Marketing Team Coordination**
- Share engagement reports and hot leads list with marketing team
- Schedule meetings with interested prospects
- Coordinate personalized follow-up communications based on priority tiers
- Execute action items from follow-up task list

**Event Management (Automated)** - for event-based campaigns
- **Agent**: `event-coordination`
- Processes Luma event data (registrations and attendance)
- Calculates attendance rates and donor conversion metrics
- Segments attendees, no-shows, and donors
- **Output**: Event summary + attendee follow-ups + no-show re-engagement lists

**Post-Event Follow-up**
- Send personalized thank-you emails to attendees using generated templates
- Execute re-engagement campaigns for no-shows
- Request feedback and future engagement opportunities
- Track conversion from event attendance to donations
- Nurture relationships for future campaigns

**Campaign Orchestration (Optional)**
- **Agent**: `campaign-orchestrator`
- Coordinates complete end-to-end workflow (Phases 1-7)
- Generates consolidated campaign report and ROI analysis
- Tracks progress across all phases with workflow status
- Provides unified follow-up plan merging email and event data
- **Output**: Campaign dashboard + consolidated metrics + lessons learned
