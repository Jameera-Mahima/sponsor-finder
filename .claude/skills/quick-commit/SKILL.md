---
name: quick-commit
description: Intelligently commit changes with a context-aware, auto-generated message that the user can approve or edit before committing. Does not push.
---

# Quick Commit Skill

Intelligently commit changes with context-aware, auto-generated messages that the user can approve or edit before committing.

## Purpose
Create meaningful commits with descriptive messages based on what actually changed, while giving the user control to approve or customize the message before committing. Does not push to remote.

## Workflow

### 1. Analyze Changes
- Run `git status` to see all changed, staged, and untracked files
- Run `git diff` to understand the content of the changes
- Categorize changes by type and location

### 2. Generate Context-Aware Commit Message

Analyze the changes and create an appropriate message based on patterns:

**New Sponsor Reports** (files in `docs/`):
- Format: "Add [topic] sponsor research results"
- Example: "Add NYC mental health arts education sponsor research"
- Extract topic from filename or first heading in the file

**Agent Modifications** (`.claude/agents/*.md`):
- Format: "Update [agent-name] agent behavior"
- Example: "Update validator agent behavior"
- Note what aspect changed (prompts, tools, validation logic)

**Command/Skill Changes** (`.claude/commands/*.md` or `.claude/skills/*/SKILL.md`):
- Format: "Modify [command-name] skill"
- Example: "Modify sync skill"
- Note what functionality was added/changed

**Specification Updates** (`specs/*.md`):
- Format: "Update project specifications"
- Note which spec was modified

**Documentation Changes** (`CLAUDE.md`, `README.md`):
- Format: "Update project documentation"
- Note what section was changed

**Mixed Changes** (multiple areas):
- Format: "Update [primary areas]"
- Example: "Update agents and documentation"
- List the main areas affected

**Bug Fixes**:
- Format: "Fix [what was broken]"
- Example: "Fix validator agent keyword extraction"

**New Features**:
- Format: "Add [feature name]"
- Example: "Add CSV export functionality"

### 3. Present Message to User

Show the generated commit message and list of files to be committed:

```
Proposed commit message:
"Add NYC mental health sponsor research results"

Files to be committed:
- docs/NYC_Mental_Health_Sponsors.md (new file, 45KB)
- docs/QUICK_REFERENCE_CONTACT_TABLE.md (modified, 12KB)

Options:
1. Approve and commit
2. Edit the message
3. Cancel

What would you like to do?
```

### 4. Handle User Response

**If user approves**:
- Proceed to step 5 (stage and commit)

**If user wants to edit**:
- Ask: "Enter your commit message:"
- Use the user's custom message
- Proceed to step 5

**If user cancels**:
- Abort: "Commit cancelled. No changes were staged or committed."
- Exit command

### 5. Stage and Commit
- Stage all changes: `git add .`
- Commit with the approved/edited message
- Include co-authorship attribution:
  ```
  [commit message]

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### 6. Show Next Steps
Display commit confirmation:
- Commit hash and message
- Number of files committed
- Total changes (insertions/deletions)

Suggest next actions:
- "Run `git push` to push this commit"
- "Run `/sync` to commit and push in one step"
- "Continue working and commit again later"

## Special Handling for docs/ Changes

When changes include sponsor reports in `docs/`:
1. List each report file with its size
2. Extract and show the report topic/title from the file content
3. Add to the prompt: "These sponsor reports will be committed. Proceed?"
4. If user declines, offer to commit only non-docs files or cancel entirely

## Error Handling

- **No changes**: "No changes to commit. Working directory is clean."
- **Conflicts exist**: "Cannot commit - resolve merge conflicts first."
- **Empty message**: If user provides empty message, prompt again or use default
- **Commit fails**: Show git error and suggest resolution

## Example Output

```
Analyzing changes...

Proposed commit message:
"Add NYC arts education and mental health sponsor research"

Files to be committed:
- docs/NYC_Mental_Health_Sponsors.md (new file, 45KB)
  Topic: "Mental Health & Arts Education Sponsors in NYC"
- docs/Arts_Education_Funders.md (new file, 38KB)
  Topic: "Arts Education Foundations - New York"
- .claude/agents/validator.md (modified, 3KB)

These sponsor reports will be committed. Proceed?

Options:
1. Approve and commit
2. Edit the message
3. Cancel

[User selects: 1]

Staging changes...
Committing...

Commit successful!
- Hash: abc1234
- Message: "Add NYC arts education and mental health sponsor research"
- Files: 3 changed, 2 new files, 1 modified
- Changes: +2,156 insertions, -42 deletions

Next steps:
- Run `git push` to push this commit
- Run `/sync` to commit future changes and push
```

## When to Use

- **Meaningful commits**: When you want a descriptive commit message
- **Review before commit**: When you want to see exactly what's being committed
- **Custom messages**: When you might want to edit the auto-generated message
- **No immediate push**: When you want to commit locally first, push later

## When NOT to Use

- When you want to commit AND push immediately (use `/sync` instead)
- For work-in-progress snapshots (use `/checkpoint` instead)
- For committing only sponsor reports (use `/save-report` instead)

## Notes

- This command gives you the most control over commit messages
- It does NOT push - you decide when to push separately
- The auto-generated message is a starting point - feel free to customize it
- Co-authored attribution is automatically added to all commits
