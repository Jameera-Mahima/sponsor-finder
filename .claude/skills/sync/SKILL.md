---
name: sync
description: Stage all changes, commit with auto-generated message, and push to remote in one command. Use when you want to quickly save and share changes.
---

# Sync Skill

Stage all changes, commit with auto-generated message, and push to remote in one command.

## Workflow

### 1. Check Repository Status
- Run `git status` to see what files have changed
- Run `git diff` to understand the nature of the changes
- Identify if any changes are in the `docs/` directory (sponsor reports)

### 2. Generate Commit Message
Analyze the changed files and diff output and create a descriptive commit message based on what changed:
- Changes to `docs/`: "Update sponsor reports: [topics/filenames]"
- Changes to `.claude/agents/`: "Update [agent-name] agent configuration"
- Changes to `.claude/commands/`: "Modify [command-name] skill"
- Changes to `CLAUDE.md`: "Update project documentation"
- Changes to `specs/`: "Update specifications"
- Mixed changes: "Update [primary areas changed]"

Keep the commit message under 50 characters for the summary line. Use imperative mood ("Update", "Add", "Fix", not "Updated", "Adding").

### 3. Confirm with User (if docs/ changed)
If changes include files in `docs/`:
- List the specific report files that changed
- Show the proposed commit message
- Ask: "These sponsor reports will be committed. Proceed? (yes/no)"
- If user says no, abort the sync operation
- If user says yes, continue to step 4

### 4. Stage and Commit
- Stage all changes: `git add .`
- Commit with the generated message
- Include co-authorship attribution:
  ```
  [commit message]

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### 5. Push to Remote
- Push to the current branch: `git push`
- If the push fails (e.g., branch not set up), show the error and suggest: `git push -u origin [branch-name]`

### 6. Show Summary
Display what was synced:
- Number of files changed
- Commit message used
- Branch pushed to
- Short git log showing the new commit

## Error Handling

- **No changes**: "No changes to sync. Working directory is clean."
- **Merge conflicts**: Show the git error and suggest resolution steps
- **Push rejected**: "Remote has updates. Run `git pull` first, then try /sync again."

## Example Output

```
Analyzing changes...

Found changes in:
- CLAUDE.md
- docs/NYC_Mental_Health_Sponsors.md
- docs/Arts_Education_Funders.md

Proposed commit message: "Update documentation and sponsor reports"

These sponsor reports will be committed:
- docs/NYC_Mental_Health_Sponsors.md (45KB)
- docs/Arts_Education_Funders.md (38KB)

Proceed? (yes/no)

[User confirms]

Staging changes...
Committing...
Pushing to origin/main...

Synced successfully!
- 3 files changed
- Commit: abc1234 "Update documentation and sponsor reports"
- Pushed to: origin/main
```

## When to Use

- Quick, routine saves when you want to immediately push changes
- All changes are ready to be shared with the team
- You don't need fine-grained control over what gets committed

## When NOT to Use

- For more control over the commit message, use `/quick-commit` instead
- For work-in-progress that shouldn't be pushed yet, use `/checkpoint`
- For committing only sponsor reports, use `/save-report`
