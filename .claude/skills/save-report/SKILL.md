---
name: save-report
description: Commit newly generated sponsor reports from the docs/ directory with intelligent selection and preview. Includes optional push.
---

# Save Report Skill

Commit newly generated sponsor reports from the docs/ directory with intelligent selection and preview capabilities.

## Purpose
Specialized command for committing sponsor research reports. Scans for new or modified reports, shows previews, lets you select which to commit, and creates a descriptive commit message. Includes option to push.

## Workflow

### 1. Scan for Reports
- Check `docs/` directory for new or modified `.md` files
- Run `git status docs/` to identify:
  - New files (untracked)
  - Modified files (tracked but changed)
  - Deleted files (if any)
- Exclude non-report files like `00-READ-ME-FIRST.md` or index files if they shouldn't be committed separately

### 2. Analyze Each Report

For each report found, extract:
- **Filename**: Full path relative to repo root
- **File size**: In KB or MB
- **Report title**: First H1 heading from the file (`# Title`)
- **Report summary**: First paragraph or summary section
- **Status**: New file or modified existing file
- **Last modified**: Timestamp of last change

### 3. Preview Reports

Display a formatted list of reports:

```
Found 3 sponsor reports:

[1] docs/NYC_Mental_Health_Sponsors.md (NEW, 45KB)
    Title: "Mental Health & Arts Education Sponsors in NYC"
    Summary: Analysis of 23 foundations and corporations...
    Modified: 2 minutes ago

[2] docs/Arts_Education_Funders.md (NEW, 38KB)
    Title: "Arts Education Foundations - New York"
    Summary: Comprehensive research on 18 funders supporting...
    Modified: 5 minutes ago

[3] docs/VALIDATION_COMPLETE_INDEX.md (MODIFIED, 12KB)
    Title: "Validated Sponsor Database Index"
    Summary: Updated index with quality scores...
    Modified: 1 minute ago
```

### 4. Let User Select Reports

Prompt the user:
```
Which reports do you want to commit?
- Enter numbers (e.g., "1,2,3" for all, "1,2" for first two)
- Enter "all" to commit all reports
- Enter "cancel" to abort

Selection:
```

Wait for user input and validate:
- Verify numbers are valid (1-N where N is the number of reports)
- Handle "all" and "cancel" keywords
- Handle invalid input gracefully

### 5. Check File Sizes

For selected reports:
- If any report is >100KB, show a warning:
  ```
  Warning: Large files detected:
  - docs/NYC_Mental_Health_Sponsors.md (145KB)

  Large files can slow down the repository. Consider:
  - Breaking into smaller reports
  - Removing unnecessary content
  - Compressing data tables

  Proceed anyway? (yes/no)
  ```
- If user says no, return to selection step
- If user says yes, continue

### 6. Generate Commit Message

Create a commit message based on selected reports:

**Single report**:
- Format: "Add sponsor research: [report title]"
- Example: "Add sponsor research: Mental Health & Arts Education Sponsors in NYC"

**Multiple reports (same theme)**:
- Format: "Add sponsor research: [common theme]"
- Example: "Add sponsor research: NYC arts education and mental health sponsors"
- Try to identify common theme from titles

**Multiple reports (different themes)**:
- Format: "Add sponsor research reports: [topics]"
- Example: "Add sponsor research reports: NYC sponsors and validation index"
- List key topics covered

**Modified existing reports**:
- Format: "Update sponsor research: [report titles]"
- Example: "Update sponsor research: Validation index and contact tables"

### 7. Show Commit Preview

Display what will be committed:
```
Commit message:
"Add sponsor research: NYC arts education and mental health sponsors"

Files to commit:
- docs/NYC_Mental_Health_Sponsors.md
- docs/Arts_Education_Funders.md

Options:
1. Commit these reports
2. Edit commit message
3. Add custom notes to message
4. Cancel

Choice:
```

### 8. Handle User Choice

**Option 1 - Commit**:
- Proceed to step 9

**Option 2 - Edit message**:
- Ask: "Enter your commit message:"
- Use custom message
- Proceed to step 9

**Option 3 - Add notes**:
- Ask: "Enter additional notes for the commit message:"
- Append notes as bullet points or paragraph to the commit message
- Show updated message
- Proceed to step 9

**Option 4 - Cancel**:
- Abort: "Commit cancelled."
- Exit command

### 9. Stage and Commit

- Stage only the selected reports: `git add [file1] [file2] ...`
- Do NOT stage other changed files
- Commit with the message:
  ```
  [commit message]

  Reports included:
  - [Report 1 title]
  - [Report 2 title]

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### 10. Ask About Push

```
Commit successful!
- Hash: def5678
- Message: "Add sponsor research: NYC arts education and mental health sponsors"
- Files: 2 reports committed

Do you want to push this commit now? (yes/no)
```

**If yes**:
- Run `git push`
- Show push result
- Display final summary

**If no**:
- Show: "Committed locally. Run `git push` when ready to push."
- Show final summary

### 11. Show Final Summary

```
Report save complete!

Committed:
- docs/NYC_Mental_Health_Sponsors.md (45KB)
- docs/Arts_Education_Funders.md (38KB)

Commit details:
- Hash: def5678
- Message: "Add sponsor research: NYC arts education and mental health sponsors"
- Status: Pushed to origin/main (or "Local only - not pushed")

View the commit: git show def5678
View git log: git log -1
```

## Error Handling

- **No reports found**: "No new or modified sponsor reports found in docs/."
- **All reports excluded**: "All reports were deselected. Nothing to commit."
- **Invalid selection**: "Invalid selection. Please enter numbers (e.g., '1,2') or 'all'."
- **Commit fails**: Show git error and suggest resolution
- **Push fails**: Show error, suggest `git pull` or `git push -u origin [branch]`

## Special Features

- **Smart theme detection**: Automatically identifies common themes across multiple reports
- **File size warnings**: Alerts for reports >100KB
- **Selective staging**: Only commits chosen reports, not other changes
- **Preview before commit**: Shows report titles and summaries
- **Custom notes**: Allows adding context to commit message
- **Optional push**: User decides whether to push immediately

## When to Use

- **After sponsor searches**: When you've generated new research reports
- **Batch commits**: Committing multiple reports at once
- **Selective commits**: When you want to commit reports but not other changes
- **Documentation**: When you want detailed commit messages for reports

## When NOT to Use

- When committing non-report files (use `/quick-commit` or `/sync`)
- For work-in-progress reports (use `/checkpoint`)
- When you want to commit everything at once (use `/sync`)

## Example Full Workflow

```
$ /save-report

Scanning docs/ directory...

Found 3 sponsor reports:

[1] docs/NYC_Mental_Health_Sponsors.md (NEW, 45KB)
    Title: "Mental Health & Arts Education Sponsors in NYC"
    Summary: Analysis of 23 foundations and corporations supporting mental health...
    Modified: 2 minutes ago

[2] docs/Arts_Education_Funders.md (NEW, 38KB)
    Title: "Arts Education Foundations - New York"
    Summary: Comprehensive research on 18 funders supporting arts programs...
    Modified: 5 minutes ago

[3] docs/VALIDATION_COMPLETE_INDEX.md (MODIFIED, 12KB)
    Title: "Validated Sponsor Database Index"
    Summary: Updated index with quality scores for all sponsors...
    Modified: 1 minute ago

Which reports do you want to commit?
Enter numbers (e.g., "1,2,3"), "all", or "cancel": 1,2

Selected reports:
- docs/NYC_Mental_Health_Sponsors.md
- docs/Arts_Education_Funders.md

Generating commit message...

Commit message:
"Add sponsor research: NYC arts education and mental health sponsors"

Options:
1. Commit these reports
2. Edit commit message
3. Add custom notes to message
4. Cancel

Choice: 1

Staging reports...
Committing...

Commit successful!
- Hash: abc1234
- Message: "Add sponsor research: NYC arts education and mental health sponsors"
- Files: 2 reports committed

Do you want to push this commit now? (yes/no): yes

Pushing to origin/main...
Push successful!

Report save complete!

Committed:
- docs/NYC_Mental_Health_Sponsors.md (45KB)
- docs/Arts_Education_Funders.md (38KB)

Commit details:
- Hash: abc1234
- Message: "Add sponsor research: NYC arts education and mental health sponsors"
- Status: Pushed to origin/main

View the commit: git show abc1234
```

## Notes

- This is the most specialized Git command for the sponsor research workflow
- Focuses exclusively on `docs/` directory reports
- Provides maximum visibility into what's being committed
- Allows fine-grained control over which reports to save
- Automatically extracts report metadata for better commit messages
- Optional push gives flexibility for local review before sharing
