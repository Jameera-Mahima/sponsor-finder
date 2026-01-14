Import historical donor data from Mailchimp to support donor relationship continuity and identify repeat sponsors.

## Purpose
Access Mailchimp contact lists to pull historical donor data, providing context for personalized outreach and identifying past supporters for current campaigns.

## Usage
`/mailchimp-import [api_key] [list_ids] [date_range]`

**Parameters**:
- `api_key` (required): Mailchimp API key for authentication
- `list_ids` (optional): Comma-separated list IDs to import (default: all accessible lists)
- `date_range` (optional): Filter contacts by date (e.g., "2020-01-01 to 2025-12-31", default: all time)

**Example**:
```
/mailchimp-import YOUR_API_KEY 123abc,456def "2023-01-01 to 2025-12-31"
```

## Processing Steps

1. **Authenticate with Mailchimp API**
   - Use provided API key in Authorization header: `Bearer <api_key>`
   - Validate credentials and retrieve account information
   - Endpoint: `GET https://usX.api.mailchimp.com/3.0/`

2. **Fetch Contact Lists**
   - If list_ids provided: Fetch specified lists only
   - If not provided: Fetch all accessible lists
   - Endpoint: `GET /3.0/lists/{list_id}/members`
   - Include query parameters: `count=1000`, `offset=0` for pagination

3. **Extract Donor Information**
   For each contact, extract:
   - Full name (merge_fields.FNAME + LNAME)
   - Email address (email_address)
   - Phone number (merge_fields.PHONE)
   - Status (subscribed, unsubscribed, cleaned)
   - Member rating (1-5 stars, based on engagement)
   - Tags and segments
   - Campaign history (stats.avg_open_rate, stats.avg_click_rate)
   - Last engagement date (last_changed)
   - Custom fields (donation amount, past campaigns if tracked)

4. **Deduplicate Contacts**
   - Group by email address (primary key)
   - For duplicates across lists:
     - Keep highest member rating
     - Merge tags from all lists
     - Use most recent engagement data
     - Flag as "Multi-list member" in notes

5. **Segment Donors**
   Classify into categories:
   - **Active**: Engaged (opened/clicked) in last 12 months
   - **Lapsed**: No engagement in 12+ months but still subscribed
   - **High-value**: Member rating 4-5 stars OR tagged as major donor OR donation history >$1000
   - **Unsubscribed**: Status = unsubscribed or cleaned

6. **Format for Salesforce Import**
   - Convert to CSV with Salesforce-compatible field names
   - Add computed fields: segment, engagement_score (0-100)
   - Validate all email addresses (RFC 5322 format)
   - Remove invalid/test emails (@example.com, @test.com)

## Output Files

All files saved to `docs/` directory:

1. **mailchimp_import.csv** - Salesforce-ready contact list
   Columns:
   - First_Name
   - Last_Name
   - Email
   - Phone
   - Status (Active/Lapsed/High-value/Unsubscribed)
   - Member_Rating (1-5)
   - Avg_Open_Rate (%)
   - Avg_Click_Rate (%)
   - Last_Engagement_Date
   - Tags (semicolon-separated)
   - Source_Lists (list names, semicolon-separated)
   - Notes

2. **historical_donor_analysis.md** - Comprehensive report
   - **Import Summary**:
     - Total contacts imported
     - Lists processed (names and IDs)
     - Date range covered
     - Import timestamp
   - **Segmentation Breakdown**:
     - Active: X contacts (XX%)
     - Lapsed: X contacts (XX%)
     - High-value: X contacts (XX%)
     - Unsubscribed: X contacts (XX%)
   - **Engagement Metrics**:
     - Average open rate across all contacts
     - Average click rate across all contacts
     - Most engaged contacts (top 10 by member rating)
   - **Top Engaged Donors** (Top 20):
     - Name, email, member rating, open/click rates
   - **Recommended Outreach Priorities**:
     - Re-engage lapsed donors (list specific names)
     - Thank and cultivate high-value donors
     - Welcome new active subscribers

3. **duplicate_contacts.json** - Flagged duplicates for review
   ```json
   {
     "total_duplicates": number,
     "duplicates": [
       {
         "email": "donor@example.com",
         "instances": [
           {
             "list_id": "123abc",
             "list_name": "2024 Campaign",
             "member_rating": 5,
             "last_engagement": "2024-12-01"
           },
           {
             "list_id": "456def",
             "list_name": "Annual Appeal",
             "member_rating": 4,
             "last_engagement": "2024-11-15"
           }
         ],
         "resolution": "Kept record from '2024 Campaign' (higher rating)"
       }
     ]
   }
   ```

## Success Criteria

- Import completes without API authentication errors
- All contacts have valid email addresses (RFC 5322 compliant)
- Duplicates identified and resolved automatically with manual review log
- Clear segmentation with at least 3 categories populated
- Output CSV parseable by Salesforce Data Import Wizard
- Analysis report provides actionable insights

## Error Handling

**API Authentication Failure**:
- Error: "Invalid API key" or 401 Unauthorized
- Solution: Verify API key format (ends with `-usX` where X is datacenter number)
- Alternative: Generate new API key from Mailchimp account settings

**Rate Limit Exceeded**:
- Error: 429 Too Many Requests
- Solution: Implement exponential backoff (wait 60s, then retry)
- Mailchimp limit: 10 requests/second per API key
- For large lists, paginate with 500 contacts per request

**List ID Not Found**:
- Error: 404 Resource Not Found
- Solution: Validate list_ids exist in account
- Fallback: Skip invalid list, continue with valid ones

**Empty or Invalid Data**:
- If no contacts found: Generate report noting "No contacts match criteria"
- If all contacts invalid emails: Log warnings, output empty CSV with headers
- If missing name fields: Use email prefix as name placeholder

**Network Timeout**:
- Error: Request timeout after 30 seconds
- Solution: Retry up to 3 times with exponential backoff
- For persistent failures: Suggest manual CSV export from Mailchimp

## API Integration Details

**Mailchimp API v3.0**:
- Base URL: `https://<dc>.api.mailchimp.com/3.0/` (dc = datacenter, e.g., us1, us19)
- Authentication: `Authorization: Bearer <api_key>`
- Rate Limits: 10 requests/second
- Documentation: https://mailchimp.com/developer/marketing/api/

**Key Endpoints**:
1. `GET /3.0/` - Ping to validate API key
2. `GET /3.0/lists` - Get all lists
3. `GET /3.0/lists/{list_id}/members` - Get list members (pagination required)
4. Query params: `count` (max 1000), `offset`, `since_last_changed` (date filter)

**Response Pagination**:
- Request with `count=1000&offset=0` for first batch
- Response includes `total_items` field
- Repeat with `offset=1000`, `offset=2000` until all fetched

## Alternative: Manual CSV Upload

If API access is unavailable or fails:

1. User exports CSV from Mailchimp manually:
   - Go to Audience → View Contacts → Export
   - Select "Export as CSV"
   - Include all available fields

2. Upload CSV to system:
   ```
   /mailchimp-import --csv path/to/mailchimp_export.csv
   ```

3. System processes CSV with same logic:
   - Parse columns (email, name, member rating, etc.)
   - Apply segmentation rules
   - Output same 3 files (import CSV, analysis report, duplicates log)

## Example Output Snippet

**mailchimp_import.csv** (first 3 rows):
```csv
First_Name,Last_Name,Email,Phone,Status,Member_Rating,Avg_Open_Rate,Avg_Click_Rate,Last_Engagement_Date,Tags,Source_Lists,Notes
Jane,Doe,jane.doe@example.com,555-0123,High-value,5,85.2,42.1,2024-12-15,"major donor;arts patron","2024 Campaign;Annual Appeal","Multi-list member"
John,Smith,john.smith@example.com,555-0456,Active,4,62.5,28.3,2024-11-30,"regular donor","2024 Campaign",""
Sarah,Johnson,sarah.j@example.com,,Lapsed,3,45.0,12.0,2023-06-15,"past donor","Annual Appeal 2023","No engagement in 18 months"
```

**historical_donor_analysis.md** (excerpt):
```markdown
# Historical Donor Analysis - Mailchimp Import

**Import Date**: January 13, 2026
**Lists Processed**: 2024 Campaign (123abc), Annual Appeal (456def)
**Total Contacts**: 1,247

## Segmentation Breakdown
- **Active**: 523 contacts (41.9%)
- **Lapsed**: 312 contacts (25.0%)
- **High-value**: 89 contacts (7.1%)
- **Unsubscribed**: 323 contacts (25.9%)

## Top Engaged Donors
1. Jane Doe (jane.doe@example.com) - Rating: 5⭐, Open: 85.2%, Click: 42.1%
2. Michael Chen (m.chen@example.com) - Rating: 5⭐, Open: 81.7%, Click: 38.9%
...

## Recommended Actions
1. **Re-engage 312 lapsed donors** - Send "We miss you" campaign
2. **Thank 89 high-value donors** - Personal outreach from Executive Director
3. **Cultivate 523 active donors** - Invite to upcoming events
```

## Integration with Existing Workflow

This command integrates with:
- **Step 3 (Outreach)**: Enriches `salesforce-integration` agent with historical donor context
- **Cross-reference**: Use with `/run-campaign` to identify prospects who are also past donors
- **Follow-up**: Combine with `engagement-tracking` agent to measure re-engagement success

**Typical Workflow**:
1. Run `/mailchimp-import` to pull historical donors
2. Run sponsor search (`/run-campaign` or manual research)
3. Cross-reference new prospects against historical donor list
4. Prioritize prospects who are past supporters (warm leads)
5. Personalize outreach: "Thank you for your past support in [year]..."
