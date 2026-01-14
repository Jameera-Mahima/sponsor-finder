---
name: checkpoint
description: Create timestamped work-in-progress commits to save current state locally without pushing. Use when experimenting or saving intermediate states.
---

# Checkpoint Skill

Create a timestamped work-in-progress commit to save current state without pushing to remote.

## Purpose
Save experimental work, intermediate states, or incomplete changes locally so you can safely try new approaches or step away without losing progress. These WIP commits can be squashed or edited later before pushing.

## Workflow

### 1. Check Current Changes
- Run `git status` to see what files have changed
- Run `git diff` to understand the nature of the changes
- Identify what work is in progress

### 2. Analyze Work in Progress
Determine what the user is currently working on:
- Experimenting with agent configurations
- Testing sponsor search queries
- Drafting new reports
- Modifying command skills
- Refactoring code
- Other exploratory work

Generate a brief description (5-10 words) of what's in progress.

### 3. Create Timestamp
Generate current timestamp in format: `YYYY-MM-DD HH:MM`

Example: `2026-01-13 14:30`

### 4. Stage All Changes
- Stage all current changes: `git add .`
- Include untracked files

### 5. Create WIP Commit
Commit with this format:
```
WIP: Checkpoint [timestamp] - [brief description]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Example:
```
WIP: Checkpoint 2026-01-13 14:30 - Testing validator agent improvements

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 6. Confirm Save (Do NOT Push)
- Create the commit locally only
- Do NOT run `git push`
- Show confirmation that work has been saved locally

### 7. Show Summary
Display what was saved:
- Number of files changed
- Full commit message
- Commit hash
- Note that changes are LOCAL ONLY (not pushed)
- Reminder: "Use `git reset HEAD~1` to undo this checkpoint if needed"

## Error Handling

- **No changes**: "No changes to checkpoint. Working directory is clean."
- **Existing staged changes**: Include them in the checkpoint
- **Commit fails**: Show the git error message

## Example Output

```
Analyzing work in progress...

Found changes in:
- .claude/agents/validator.md
- .claude/agents/web-researcher.md
- docs/test-search-results.md

Creating checkpoint for: Testing validator agent improvements

Staging changes...
Creating WIP commit...

Checkpoint saved!
- 3 files changed
- Commit: def5678 "WIP: Checkpoint 2026-01-13 14:30 - Testing validator agent improvements"
- Status: LOCAL ONLY (not pushed to remote)

To undo this checkpoint: git reset HEAD~1
To continue working: Make more changes and create another checkpoint
To finalize: Use /quick-commit or /sync when ready to push
```

## When to Use

- **Experimentation**: Trying different agent configurations or search strategies
- **Breaks**: Saving state before stepping away from work
- **Safety net**: Before attempting risky refactoring
- **Iterative work**: Saving multiple iterations of report generation
- **Collaboration prep**: Checkpointing before discussing changes with team

## When NOT to Use

- When you're ready to push changes (use `/sync` or `/quick-commit` instead)
- For final, polished work (use standard commit workflow)
- When creating pull requests (clean up WIP commits first)

## Notes

- WIP commits are local only - they won't clutter remote history
- You can create multiple checkpoints as you work
- Before pushing, consider squashing WIP commits into meaningful commits
- Use `git log` to see your checkpoint history
- These commits can be edited, squashed, or removed with `git rebase -i` before pushing
