# CSV Export Feature - Planning Document
## Healing NY Sponsor Finder System

---

## 1. EXECUTIVE SUMMARY

The CSV export feature will enable users to download validated sponsor lists in a standardized CSV format for use in external tools (spreadsheets, CRM systems, databases). This feature addresses the need for portable data that can be manipulated offline and integrated with grant management workflows.

**Key Points:**
- **Scope:** Add CSV export capability to the existing 4-phase validation workflow
- **Integration Point:** Post-validation, pre-report generation
- **Output Columns:** Name, Type, Contact, Website, Giving History, Relevance Score, Plus metadata
- **User Base:** Nonprofit grant writers, development directors, fundraising teams
- **Priority:** Medium (valuable but not blocking current functionality)

---

## 2. REQUIREMENTS

### 2.1 FUNCTIONAL REQUIREMENTS

#### Must-Have Features:
1. **Export Core Data**
   - [ ] Export validated sponsor list as CSV file
   - [ ] Include columns: Name, Type, Contact, Website, Giving History, Relevance Score
   - [ ] Preserve all validation metadata
   - [ ] Generate downloadable file with timestamp

2. **Data Completeness**
   - [ ] Include all sponsors with validation score ≥5
   - [ ] Capture all contact information fields (email, phone, address, website)
   - [ ] Include tier classification (Tier 1, 2, 3, etc.)
   - [ ] Include mission alignment notes

3. **CSV Format Standards**
   - [ ] UTF-8 encoding
   - [ ] Proper escaping of special characters (commas, quotes, newlines)
   - [ ] RFC 4180 compliance
   - [ ] Readable header row with clear column names

4. **File Management**
   - [ ] Generate file with descriptive name (e.g., `Healing_NY_Sponsors_2025-01-13.csv`)
   - [ ] Save to accessible location
   - [ ] Optional: Generate alongside report generation

#### Nice-to-Have Features:
1. **Additional Export Options**
   - [ ] Filter by sponsor type (Corporations, Foundations, NGOs)
   - [ ] Filter by minimum relevance score threshold
   - [ ] Filter by tier classification
   - [ ] Export subset of columns (user customizable)

2. **Enhanced Features**
   - [ ] Add "Last Verified" date
   - [ ] Include "Quality Score" alongside Relevance Score
   - [ ] Add "Application Strategy" notes column
   - [ ] Include "Funding Range" column
   - [ ] Add "Geographic Focus" column

3. **Automation**
   - [ ] Batch export multiple searches
   - [ ] Schedule recurring exports
   - [ ] Email export results

### 2.2 NON-FUNCTIONAL REQUIREMENTS

1. **Performance**
   - [ ] Export time: <2 seconds for typical 30-sponsor list
   - [ ] File size: <500 KB for single export
   - [ ] No performance impact on validation workflow

2. **Reliability**
   - [ ] Error handling for file I/O failures
   - [ ] Graceful fallback if export fails
   - [ ] Data integrity validation (all rows exported)
   - [ ] UTF-8 encoding verification

3. **Usability**
   - [ ] Clear success message with file path/download location
   - [ ] Intuitive column ordering (most important first)
   - [ ] Readable column names (no internal field names)
   - [ ] Consistent data formatting

4. **Security & Compliance**
   - [ ] No sensitive information exposure (PII handling)
   - [ ] Secure file permissions (world-readable OK, not writable)
   - [ ] GDPR compliance for contact information (if applicable)
   - [ ] Audit trail of exports (optional)

5. **Compatibility**
   - [ ] Open in Excel, Google Sheets, LibreOffice Calc
   - [ ] Import to common CRM systems (Salesforce, Pipedrive)
   - [ ] Compatible with data analysis tools (Python, R)
   - [ ] Works on Windows, Mac, Linux

---

## 3. USER STORIES

### User Story 1: Basic CSV Export
**As a** grant writer
**I want to** export the validated sponsor list to CSV
**So that** I can open it in Excel and organize prospects by priority

**Acceptance Criteria:**
- [ ] CSV file contains all validated sponsors
- [ ] File opens correctly in Excel/Google Sheets
- [ ] All required columns are present and populated
- [ ] File has a clear, timestamped filename
- [ ] Export completes without errors

**Priority:** HIGH

---

### User Story 2: Filtered Export by Type
**As a** development director
**I want to** export only foundation sponsors
**So that** I can focus my outreach efforts on the best matching sponsor category

**Acceptance Criteria:**
- [ ] User can select sponsor type filter (e.g., "Foundations only")
- [ ] CSV contains only selected type
- [ ] Filter results are documented in export
- [ ] File reflects filtered status in filename (e.g., `..._Foundations_Only.csv`)

**Priority:** MEDIUM

---

### User Story 3: CRM Integration
**As a** development manager
**I want to** import the CSV into our Salesforce CRM
**So that** I can track grant applications and communications in one system

**Acceptance Criteria:**
- [ ] CSV format compatible with Salesforce import
- [ ] Column mapping is clear (Salesforce field names)
- [ ] Contact information is properly separated (name vs. email)
- [ ] No data loss during import

**Priority:** MEDIUM

---

### User Story 4: Offline Analysis
**As a** nonprofit board member
**I want to** download the sponsor list as CSV
**So that** I can analyze it offline without internet access

**Acceptance Criteria:**
- [ ] CSV exports all necessary data for offline analysis
- [ ] Giving history information is complete
- [ ] Relevance scores guide priority decisions
- [ ] No external references needed for offline use

**Priority:** LOW

---

### User Story 5: Historical Tracking
**As a** grant writer
**I want to** have timestamped CSV exports
**So that** I can track which sponsors were viable at different times

**Acceptance Criteria:**
- [ ] Each export includes export date/time
- [ ] Multiple exports can be compared chronologically
- [ ] Historical exports are preserved
- [ ] Version tracking is possible

**Priority:** LOW

---

## 4. ARCHITECTURE & DESIGN

### 4.1 COMPONENT DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sponsor Finder Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase 1: Keyword Extraction  →  Phase 2: Web Research         │
│         (Claude Haiku 4.5)              (Claude Haiku 4.5)      │
│                                                                   │
│              ↓                              ↓                     │
│                                                                   │
│  Phase 3: Categorization  →  Phase 4: Validation                │
│  (Claude Haiku 4.5)          (Claude Sonnet 4.5)                │
│                                                                   │
│              ↓                              ↓                     │
│                                                                   │
│             ┌─────────────────────────────────┐                 │
│             │  Validated Sponsor List (JSON)  │                 │
│             └──────────────┬──────────────────┘                 │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                 │
│         ↓                  ↓                  ↓                  │
│   ┌──────────┐      ┌──────────────┐   ┌───────────┐            │
│   │ Markdown │      │ CSV EXPORTER │   │JSON Export│            │
│   │ Reports  │      │  (NEW FEATURE)   │ Formatter │            │
│   └──────────┘      └──────────────┘   └───────────┘            │
│         ↓                  ↓                  ↓                  │
│   ┌──────────┐      ┌──────────────┐   ┌───────────┐            │
│   │ .md Files│      │.csv File     │   │ JSON File │            │
│   └──────────┘      └──────────────┘   └───────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 CSV EXPORTER COMPONENT

**Location:** `csv_exporter.py` (new module)

**Core Responsibilities:**
1. Accept validated sponsor list (JSON format)
2. Transform sponsor objects to CSV rows
3. Handle special characters and formatting
4. Write to file with proper encoding
5. Return file path and status

**Interface:**
```python
class SponsorCSVExporter:
    def __init__(self, sponsors_list: List[Dict], output_dir: str = None)
    def export(self, filename: str = None, filters: Dict = None) -> Dict[str, Any]
    def _format_contact_info(self, sponsor: Dict) -> str
    def _validate_csv_output(self, filepath: str) -> bool
```

### 4.3 Integration Points

**Input:**
- Validated sponsor list from Phase 4 (Validation)
- User preferences (filters, columns, output path)

**Output:**
- CSV file saved to disk
- Return status: success/failure with filepath
- Integration with existing report generation

**Modification to Workflow:**
```
Phase 4: Validation
    ↓
CSV Export Module (NEW)
    ├─ Extract validated sponsors
    ├─ Apply filters (optional)
    ├─ Transform to CSV format
    └─ Write to file
    ↓
Report Generation (Existing)
```

---

## 5. DATA MODELS

### 5.1 SPONSOR DATA STRUCTURE (Input to CSV Exporter)

```python
Sponsor = {
    "name": str,                      # "Laurie M. Tisch Illumination Fund"
    "type": str,                      # "Foundation" | "Corporation" | "NGO" | "Individual" | "Government"
    "tier": str,                      # "Tier 1A", "Tier 1B", "Tier 2", etc.
    "contact": {
        "website": str,               # "https://example.org"
        "email": str,                 # "grants@example.org"
        "phone": str,                 # "212-555-0100"
        "address": str,               # "123 Main St, NYC, NY 10001"
    },
    "giving": {
        "history": str,               # "Funded [Project] with $250k in 2023"
        "range": str,                 # "$100K-$500K" or "$50K+"
        "focus_areas": [str],         # ["mental health", "arts education"]
        "geographic_scope": str,      # "New York City" | "New York State"
    },
    "relevance_score": float,         # 1-10 scale
    "quality_score": float,           # 1-10 scale
    "mission_alignment": str,         # Narrative description
    "last_verified": str,             # ISO date format "2025-01-13"
    "application_strategy": str,      # "Contact first" | "Cold apply" | "Refer through NAMI"
}
```

### 5.2 CSV OUTPUT FORMAT

**File:** `Healing_NY_Sponsors_{date}.csv`

**Columns (in order):**

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| Name | Organization name | "Laurie M. Tisch Illumination Fund" | Yes |
| Type | Sponsor category | "Foundation" | Yes |
| Tier | Classification tier | "Tier 1A" | Yes |
| Website | Web URL | "https://www.tischeducation.org" | Yes |
| Email | Contact email | "grants@example.org" | Yes |
| Phone | Phone number | "212-555-0100" | No |
| Address | Mailing address | "123 Main St, NYC, NY 10001" | No |
| Giving Range | Typical grant size | "$250K-$500K" | Yes |
| Giving History | Recent grants | "Mental Health Initiative ($250k, 2023)" | Yes |
| Focus Areas | Priority sectors | "Mental Health, Arts Education" | Yes |
| Geographic Focus | Geographic scope | "New York City" | Yes |
| Relevance Score | 1-10 alignment | "9.8" | Yes |
| Quality Score | 1-10 data quality | "9.5" | Yes |
| Mission Alignment | Narrative fit | "Perfect fit: funds mental health + arts" | Yes |
| Application Strategy | Outreach approach | "Contact program officer first" | Yes |
| Last Verified | Data verification date | "2025-01-13" | Yes |

**Sample Row:**
```
"Laurie M. Tisch Illumination Fund","Foundation","Tier 1A","https://www.tischeducation.org","grants@example.org","212-555-0100","123 Main St, NYC, NY","$250K-$500K","Mental Health Initiative ($250k, 2023); Arts in Schools ($300k, 2022)","Mental Health, Arts, Education","New York City","9.8","9.5","Perfect alignment: funded similar mental health+arts projects","Contact program officer first","2025-01-13"
```

### 5.3 FILTER OPTIONS

```python
ExportFilters = {
    "sponsor_types": [str],          # ["Foundation", "Corporation"]
    "min_relevance_score": float,     # 7.5
    "min_quality_score": float,       # 8.0
    "tiers": [str],                  # ["Tier 1A", "Tier 1B"]
    "min_grant_amount": str,          # "$100K"
    "geographic_focus": [str],        # ["New York City"]
    "columns": [str],                 # Subset of available columns
}
```

---

## 6. IMPLEMENTATION PLAN

### Phase 1: Core CSV Export (Week 1)
- [ ] Create `csv_exporter.py` module
- [ ] Implement basic export functionality
- [ ] Handle UTF-8 encoding and special characters
- [ ] Write to file with timestamp
- [ ] Basic error handling

**Deliverable:** Basic CSV export working end-to-end

---

### Phase 2: Integration (Week 2)
- [ ] Integrate with orchestrator.py workflow
- [ ] Add CSV export option to CLI/interface
- [ ] Test with actual validated sponsor data
- [ ] Verify format in Excel/Google Sheets

**Deliverable:** CSV export integrated and tested

---

### Phase 3: Enhanced Features (Week 3)
- [ ] Implement filter options
- [ ] Add customizable column selection
- [ ] Include additional metadata columns
- [ ] Add data validation

**Deliverable:** Filters and customization working

---

### Phase 4: Optimization (Week 4)
- [ ] Performance testing
- [ ] CRM format compatibility testing
- [ ] Documentation and user guide
- [ ] Final testing and QA

**Deliverable:** Production-ready feature

---

## 7. RISK ASSESSMENT

### Risk 1: Special Character Handling
**Risk:** CSV format broken by commas, quotes, or newlines in data
**Probability:** MEDIUM
**Impact:** HIGH (data corruption)
**Mitigation:**
- [ ] Use proper CSV library (Python `csv` module)
- [ ] Test with data containing special characters
- [ ] Implement validation to verify output integrity

---

### Risk 2: Encoding Issues
**Risk:** Non-ASCII characters (accents, symbols) corrupted
**Probability:** LOW
**Impact:** MEDIUM
**Mitigation:**
- [ ] Always use UTF-8 encoding
- [ ] Test with international names/addresses
- [ ] Validate file encoding on write

---

### Risk 3: File Permissions
**Risk:** CSV file not accessible to user or overwritten unexpectedly
**Probability:** LOW
**Impact:** MEDIUM
**Mitigation:**
- [ ] Set appropriate file permissions
- [ ] Create versioned filenames with timestamps
- [ ] Return full filepath to user for verification

---

### Risk 4: Data Loss During Filtering
**Risk:** Filters accidentally exclude important sponsors
**Probability:** LOW
**Impact:** HIGH
**Mitigation:**
- [ ] Provide summary of filters applied
- [ ] Show count of filtered-out sponsors
- [ ] Option to export with/without filters clearly separated

---

### Risk 5: Compatibility Issues
**Risk:** CSV opens incorrectly in some spreadsheet applications
**Probability:** LOW
**Impact:** MEDIUM
**Mitigation:**
- [ ] Test in Excel, Google Sheets, LibreOffice
- [ ] Use RFC 4180 compliant format
- [ ] Provide CSV format troubleshooting guide

---

### Risk 6: Performance Degradation
**Risk:** Large exports slow down validation workflow
**Probability:** LOW
**Impact:** LOW
**Mitigation:**
- [ ] Process CSV export asynchronously
- [ ] Performance testing with 100+ sponsors
- [ ] Optimize for batch exports

---

## 8. SUCCESS METRICS

### Functionality Metrics
- [ ] 100% of validated sponsors exported correctly
- [ ] Zero data loss during export
- [ ] CSV opens in all major spreadsheet applications
- [ ] All required columns present and populated

### Quality Metrics
- [ ] CSV validates against RFC 4180
- [ ] UTF-8 encoding verified
- [ ] Special characters handled correctly
- [ ] No truncation of data

### Performance Metrics
- [ ] Export time: <2 seconds (30 sponsors)
- [ ] File size: <500 KB
- [ ] Memory usage: <50 MB

### User Experience Metrics
- [ ] Clear feedback on export success/failure
- [ ] Intuitive column ordering
- [ ] Easy import to external tools
- [ ] Self-explanatory column names

### Adoption Metrics
- [ ] Feature used by 80%+ of users
- [ ] Positive feedback on utility
- [ ] Reduced manual data entry
- [ ] Integration with user workflows

---

## 9. TESTING STRATEGY

### Unit Tests
- [ ] CSV formatting with special characters
- [ ] UTF-8 encoding validation
- [ ] Filter logic accuracy
- [ ] File I/O error handling

### Integration Tests
- [ ] CSV export in full workflow
- [ ] Data integrity from validation to export
- [ ] Filter application accuracy
- [ ] Orchestrator integration

### System Tests
- [ ] Excel/Google Sheets compatibility
- [ ] CRM import compatibility
- [ ] Large dataset performance
- [ ] Cross-platform compatibility

### User Acceptance Tests
- [ ] Real user workflows
- [ ] Grant writer feedback
- [ ] CRM import testing
- [ ] Data accuracy verification

---

## 10. DOCUMENTATION

### User Documentation
- [ ] CSV Export User Guide
- [ ] Filter Options Guide
- [ ] CRM Import Instructions (Salesforce, Pipedrive)
- [ ] Troubleshooting Guide

### Technical Documentation
- [ ] CSV Exporter API Documentation
- [ ] Integration Points Guide
- [ ] Data Model Documentation
- [ ] Error Handling Guide

---

## 11. DEPENDENCIES & PREREQUISITES

### Required Python Libraries
- `csv` (standard library) - CSV generation
- `json` (standard library) - JSON parsing
- `datetime` (standard library) - Timestamps
- Optional: `pandas` - Enhanced data manipulation

### System Dependencies
- File system write access
- UTF-8 encoding support
- Standard Python 3.7+

### Data Dependencies
- Validated sponsor list from Phase 4
- Contact information must be populated
- Relevance scores must be calculated

---

## 12. ROLLOUT PLAN

### MVP (Minimum Viable Product)
- [ ] Basic CSV export of validated sponsors
- [ ] All required columns
- [ ] UTF-8 encoding
- [ ] Timestamp in filename

### Phase 2: Enhanced
- [ ] Filter by sponsor type
- [ ] Filter by relevance score
- [ ] Customizable columns

### Phase 3: Premium
- [ ] CRM format options
- [ ] Batch exports
- [ ] Email delivery
- [ ] Historical exports

---

## 13. APPROVAL & SIGN-OFF

**Feature Owner:** [TBD]
**Technical Lead:** [TBD]
**Stakeholder Approval:** [TBD]

---

## 14. NEXT STEPS

1. **Stakeholder Review** - Get feedback on requirements
2. **Technology Decision** - Confirm CSV library approach
3. **Data Model Validation** - Verify sponsor data structure
4. **Architecture Approval** - Confirm integration points
5. **Development Kickoff** - Begin Phase 1 implementation

---

**Document Date:** 2025-01-13
**Status:** DRAFT - Pending Approval
**Version:** 1.0
