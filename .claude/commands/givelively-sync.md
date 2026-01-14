Track online donations in real-time from GiveLively campaigns and monitor progress toward fundraising goals.

## Purpose
Monitor donation activity from GiveLively campaigns, calculate fundraising progress, identify high-value donors, and generate prioritized thank-you lists for donor cultivation.

## Usage
`/givelively-sync [api_key] [campaign_id] [goal_amount]`

**Parameters**:
- `api_key` (required): GiveLively API key for authentication (or use `--csv` flag for manual upload)
- `campaign_id` (required): GiveLively campaign ID to track
- `goal_amount` (optional): Fundraising goal in dollars (default: pulls from GiveLively campaign settings)

**Alternative Usage (Manual CSV)**:
```
/givelively-sync --csv path/to/givelively_export.csv --goal 500000
```

**Examples**:
```
/givelively-sync YOUR_API_KEY abc123def 500000
/givelively-sync --csv donations_export.csv --goal 250000
```

## Processing Steps

### API Workflow

1. **Authenticate with GiveLively API**
   - Use provided API key for authentication
   - Validate credentials and retrieve organization info
   - Note: If GiveLively API is unavailable/restricted, fallback to CSV import

2. **Fetch Campaign Data**
   - Retrieve campaign details (name, description, goal, dates)
   - Endpoint: `GET /campaigns/{campaign_id}`
   - If goal_amount not provided, use campaign's configured goal

3. **Fetch Donation Records**
   - Retrieve all donations for specified campaign
   - Endpoint: `GET /campaigns/{campaign_id}/donations`
   - Include pagination for large datasets (100 donations per page)
   - Extract for each donation:
     - Donor name (first_name + last_name)
     - Email address
     - Donation amount
     - Donation date/timestamp
     - Donation frequency (one-time vs. recurring)
     - Donor message/comments
     - Payment status (completed, pending, failed)
     - Anonymous flag (if donor chose to remain anonymous)

4. **Calculate Campaign Metrics**
   - **Total Raised**: Sum of all completed donations
   - **Goal Progress**: (total_raised / goal_amount) × 100
   - **Amount Remaining**: goal_amount - total_raised
   - **Donation Velocity**:
     - Per day: total_raised / days_since_campaign_start
     - Per week: velocity_per_day × 7
   - **Average Gift Size**: total_raised / total_donations
   - **Donor Count**: Unique donors (deduplicated by email)
   - **Donor Retention**: Repeat donors / total unique donors
   - **Projected Completion Date**:
     - If velocity > 0: days_remaining = amount_remaining / velocity_per_day
     - Completion date = today + days_remaining

5. **Identify High-Value Donors**
   - Sort donors by donation amount (descending)
   - Tag top 10% as "Major Donors"
   - Tag donors who gave ≥$1,000 as "Large Donors"
   - Tag donors who gave ≥$5,000 as "Transformational Donors"

6. **Flag New vs. Repeat Donors**
   - Cross-reference with Mailchimp historical data (if available from prior `/mailchimp-import`)
   - Match by email address
   - Tag as:
     - **New Donor**: No prior giving history
     - **Repeat Donor**: Found in historical donor database
     - **Upgraded Donor**: Gave more than previous average gift
     - **Downgraded Donor**: Gave less than previous average gift

7. **Format for Salesforce Import**
   - Convert to CSV with donation records
   - Include donor details and computed fields
   - Link to contact records from Mailchimp import if available

### CSV Workflow (If No API)

If API is unavailable or user prefers manual export:

1. **User exports donations from GiveLively**:
   - Log into GiveLively dashboard
   - Go to Campaign → Reports → Export Donations
   - Download CSV with all donation records

2. **Upload CSV to system**:
   ```
   /givelively-sync --csv path/to/givelively_export.csv --goal 500000
   ```

3. **System parses CSV**:
   - Detect column headers (Donor Name, Email, Amount, Date, etc.)
   - Apply same processing logic as API workflow
   - Output identical files

## Output Files

All files saved to `docs/` directory:

1. **donations.csv** - Salesforce-ready donation records
   Columns:
   - Donation_ID (if available, else generated UUID)
   - Campaign_Name
   - Donor_First_Name
   - Donor_Last_Name
   - Donor_Email
   - Donation_Amount
   - Donation_Date
   - Frequency (One-time/Recurring)
   - Donor_Tier (Major/Large/Transformational/Regular)
   - New_or_Repeat (New/Repeat/Upgraded/Downgraded)
   - Donor_Message
   - Anonymous (Yes/No)
   - Payment_Status (Completed/Pending/Failed)

2. **campaign_progress_report.md** - Real-time dashboard

   **Campaign Overview**:
   - Campaign name and ID
   - Campaign start date and end date (if applicable)
   - Fundraising goal
   - Report generated date/time

   **Fundraising Progress**:
   - Total raised: $X,XXX (XX% of goal)
   - Amount remaining: $X,XXX
   - Progress bar visualization (text-based)
   - Status: On Track / Behind Schedule / Ahead of Schedule

   **Donation Velocity**:
   - Average per day: $XXX
   - Average per week: $X,XXX
   - Projected completion date: MM/DD/YYYY (or "Goal already met!")
   - Days remaining: X days

   **Donor Statistics**:
   - Total donors: XXX unique donors
   - New donors: XX (XX%)
   - Repeat donors: XX (XX%)
   - Average gift size: $XXX
   - Median gift size: $XXX
   - Largest single gift: $X,XXX

   **Donation Size Distribution**:
   - $1-$50: XX donations (XX%)
   - $51-$100: XX donations (XX%)
   - $101-$500: XX donations (XX%)
   - $501-$1,000: XX donations (XX%)
   - $1,001-$5,000: XX donations (XX%)
   - $5,001+: XX donations (XX%)

   **Top Donors Leaderboard** (Top 10):
   1. Jane Doe - $5,000 (Transformational Donor, New)
   2. John Smith - $2,500 (Large Donor, Repeat)
   ...

   **Donor Retention**:
   - Repeat donor rate: XX% (industry benchmark: 45%)
   - Upgraded donors: XX (giving more than before)
   - Downgraded donors: XX (giving less than before)

3. **donor_thank_you_list.json** - Prioritized outreach list
   ```json
   {
     "generated_date": "2026-01-13T15:30:00Z",
     "campaign_id": "abc123def",
     "total_donors": 142,
     "priority_groups": {
       "immediate_personal_outreach": [
         {
           "donor_name": "Jane Doe",
           "email": "jane.doe@example.com",
           "amount": 5000,
           "tier": "Transformational",
           "status": "New",
           "suggested_action": "Personal phone call from Executive Director within 24 hours",
           "talking_points": [
             "Thank for transformational $5,000 gift",
             "Share impact on arts education programs",
             "Invite to exclusive donor recognition event",
             "Ask about interest in board/advisory role"
           ]
         }
       ],
       "high_priority_email": [
         {
           "donor_name": "John Smith",
           "email": "john.smith@example.com",
           "amount": 2500,
           "tier": "Large",
           "status": "Repeat",
           "suggested_action": "Personalized email from Development Director within 48 hours",
           "talking_points": [
             "Thank for continued support (3rd year giving)",
             "Note increase from $1,500 last year to $2,500 this year",
             "Share specific program outcomes enabled by their gift",
             "Invite to behind-the-scenes studio visit"
           ]
         }
       ],
       "standard_thank_you": [
         {
           "donor_name": "Sarah Johnson",
           "email": "sarah.j@example.com",
           "amount": 250,
           "tier": "Regular",
           "status": "New",
           "suggested_action": "Automated thank-you email within 24 hours, followed by welcome packet",
           "talking_points": [
             "Welcome to CSOAF donor community",
             "Explain how $250 supports 5 students for one semester",
             "Invite to quarterly newsletter signup",
             "Share upcoming volunteer opportunities"
           ]
         }
       ]
     }
   }
   ```

## Success Criteria

- Donation data syncs accurately from GiveLively (API or CSV)
- Goal tracking calculations correct (total raised, % complete, velocity)
- Thank-you list prioritization aligns with donor value tiers
- Salesforce import CSV format validated and parseable
- Progress report provides actionable insights for development team
- Projected completion date realistic based on velocity trends

## Error Handling

**API Authentication Failure**:
- Error: "Invalid API key" or 401 Unauthorized
- Solution: Verify API key is active in GiveLively settings
- Alternative: Fall back to CSV import workflow

**Campaign ID Not Found**:
- Error: 404 Resource Not Found
- Solution: Verify campaign ID from GiveLively dashboard URL
- Provide instructions to find campaign ID

**Empty Campaign (No Donations)**:
- Error: Campaign exists but has 0 donations
- Solution: Generate report showing "$0 raised (0% of goal)"
- Output: Empty donations.csv with headers only
- Message: "No donations recorded yet. Check back after first donation."

**Invalid Goal Amount**:
- Error: Goal amount ≤ 0 or non-numeric
- Solution: Prompt user to provide valid goal
- Fallback: If goal not provided and can't fetch from API, use $100,000 default

**Network Timeout or API Downtime**:
- Error: Request timeout or 500 Internal Server Error
- Solution: Retry up to 3 times with exponential backoff
- Fallback: Suggest CSV export workflow
- Partial success: If some donations fetched, process available data and note incomplete sync

**CSV Parsing Errors**:
- Error: CSV missing required columns (Donor Name, Amount, Date)
- Solution: Provide template CSV format
- Attempt to auto-detect columns by content (numbers = amount, dates = date)
- Skip malformed rows, log warnings

**Data Quality Issues**:
- Missing donor emails: Flag as "Anonymous" or "No Email Provided"
- Negative donation amounts: Flag as refunds, exclude from total raised
- Future dates: Flag as scheduled donations, mark as pending
- Duplicate transactions: Deduplicate by transaction ID or timestamp+amount+email

## API Integration Details

**GiveLively API** (Note: API availability varies by plan tier):

**If API Available**:
- Base URL: TBD (check GiveLively documentation - they may use a partner API or direct integration)
- Authentication: API key or OAuth token
- Documentation: https://www.givelively.org/ (check for developer portal)

**If API Not Available** (Most common scenario):
- GiveLively provides CSV export functionality in dashboard
- Use CSV import workflow as primary method
- CSV format typically includes:
  - Donor Name, Email, Amount, Date, Payment Method, Message, Campaign Name

**Recommended Approach**:
1. First attempt: Check if organization has API access (enterprise plans)
2. Primary method: CSV export workflow (most reliable, no API limits)
3. Future enhancement: Web scraping GiveLively dashboard (if permission granted)

## Alternative: Manual CSV Format

**Expected CSV Columns**:
```csv
Donor First Name,Donor Last Name,Email,Amount,Date,Frequency,Message,Campaign,Status
Jane,Doe,jane.doe@example.com,5000,2024-12-15,One-time,"Keep up the great work!",Arts Education Fund,Completed
John,Smith,john.smith@example.com,2500,2024-12-10,Monthly,"Happy to support!",Arts Education Fund,Completed
```

**Minimum Required Columns**:
- Donor Name (or First Name + Last Name)
- Amount
- Date

**Optional but Recommended**:
- Email (for thank-you outreach and CRM import)
- Frequency (one-time vs. recurring)
- Message (donor comments for personalization)
- Status (completed vs. pending)

## Example Output Snippet

**donations.csv** (first 3 rows):
```csv
Donation_ID,Campaign_Name,Donor_First_Name,Donor_Last_Name,Donor_Email,Donation_Amount,Donation_Date,Frequency,Donor_Tier,New_or_Repeat,Donor_Message,Anonymous,Payment_Status
d001,Arts Education Fund,Jane,Doe,jane.doe@example.com,5000,2024-12-15,One-time,Transformational,New,"Keep up the great work!",No,Completed
d002,Arts Education Fund,John,Smith,john.smith@example.com,2500,2024-12-10,Monthly,Large,Repeat,"Happy to support!",No,Completed
d003,Arts Education Fund,Sarah,Johnson,sarah.j@example.com,250,2024-12-08,One-time,Regular,New,"",No,Completed
```

**campaign_progress_report.md** (excerpt):
```markdown
# Campaign Progress Report - Arts Education Fund

**Campaign ID**: abc123def
**Report Generated**: January 13, 2026 at 3:30 PM EST
**Campaign Period**: December 1, 2024 - March 31, 2025

## Fundraising Progress

**Goal**: $500,000
**Total Raised**: $127,250 (25.5% of goal)
**Amount Remaining**: $372,750

Progress: [████████░░░░░░░░░░░░░░░░░░░░░░] 25.5%

**Status**: ⚠️ Behind Schedule (at current pace, goal will not be met by deadline)

## Donation Velocity

- **Per Day**: $2,850
- **Per Week**: $19,950
- **Projected Completion**: June 18, 2026 (78 days past deadline)
- **Days Remaining to Deadline**: 77 days

**Recommendation**: Increase outreach efforts. Need $4,841/day to meet goal on time.

## Donor Statistics

- **Total Donors**: 142 unique donors
- **New Donors**: 89 (62.7%)
- **Repeat Donors**: 53 (37.3%)
- **Average Gift**: $896
- **Median Gift**: $250
- **Largest Gift**: $5,000 (Jane Doe)

## Top 10 Donors

1. **Jane Doe** - $5,000 (Transformational Donor, New)
2. **John Smith** - $2,500 (Large Donor, Repeat - Up from $1,500 last year)
3. **Michael Chen** - $2,000 (Large Donor, Repeat)
...
```

## Integration with Existing Workflow

This command integrates with:
- **Step 4 (Tracking & Analysis)**: Feeds data to `engagement-tracking` agent for donor attribution
- **Step 3 (Outreach)**: Inform `salesforce-integration` with current donor status
- **Mailchimp Cross-reference**: Identifies repeat vs. new donors using `/mailchimp-import` data
- **Campaign Orchestration**: Used by `/run-campaign` to provide real-time funding progress

**Typical Workflow**:
1. Run `/givelively-sync` weekly during active campaign
2. Review progress report to assess velocity vs. goal
3. Export donations.csv to Salesforce for CRM record updates
4. Use thank-you list (donor_thank_you_list.json) to prioritize outreach
5. Send personalized thank-you emails within 24-48 hours of donation
6. Schedule personal calls for major/transformational donors
7. Track donor retention for future campaigns

**Re-engagement Strategy**:
- If behind schedule: Launch urgency email campaign to lapsed donors
- If ahead of schedule: Announce momentum to inspire additional giving
- Highlight top donors publicly (with permission) to encourage peer giving
