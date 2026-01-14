# Sponsor Finder Logging System

This directory contains execution logs for all sponsor research campaigns and agent executions.

## Directory Structure

```
logs/
├── campaigns/              # Campaign-level logs (organized by campaign ID)
│   └── campaign_YYYYMMDD_xxxxxx/
│       ├── campaign_log.json        # Master campaign log (JSON format)
│       ├── campaign_log.md          # Master campaign log (Markdown format)
│       ├── phase1_research.json     # Phase-specific logs
│       ├── phase1_research.md
│       ├── agent_*.json             # Agent execution logs
│       ├── agent_*.md
│       ├── performance_summary.json # Performance metrics and bottlenecks
│       ├── error_log.json           # All errors and warnings
│       └── data_quality_audit.json  # Quality decisions and filters
│
├── agents/                 # Agent-level logs (organized by agent type)
│   ├── keyword-extractor/
│   │   ├── execution_history.json   # Historical runs
│   │   ├── performance_metrics.json # Aggregate statistics
│   │   └── runs/
│   │       ├── YYYYMMDD_HHMMSS.json
│   │       └── YYYYMMDD_HHMMSS.md
│   └── [other agents]/
│
├── dashboard/              # Live monitoring dashboard
│   ├── index.html          # Dashboard viewer (open in browser)
│   ├── dashboard.css       # Styling
│   ├── dashboard.js        # Live updates (2-second refresh)
│   └── current_execution.json  # Real-time execution status
│
└── archive/                # Archived logs (>30 days old)
```

## Log Formats

### JSON Logs
- **Purpose**: Machine-parseable for analysis and automation
- **Use cases**: Performance analysis, cost tracking, error aggregation
- **Tools**: Query with `jq`, import into analytics platforms

### Markdown Logs
- **Purpose**: Human-readable for quick review and debugging
- **Use cases**: Manual inspection, troubleshooting, stakeholder reports

## Viewing Logs

### Live Dashboard (Recommended)
1. Open `dashboard/index.html` in your web browser
2. Dashboard auto-refreshes every 2 seconds during execution
3. Shows real-time campaign progress, metrics, and errors

### Command Line
```bash
# View latest campaign log (Markdown)
cat logs/campaigns/campaign_*/campaign_log.md | tail -n 100

# View specific agent logs (JSON)
cat logs/agents/keyword-extractor/runs/*.json | jq .

# Search for errors across all campaigns
grep -r "severity.*error" logs/campaigns/*/error_log.json
```

### File Browser
Navigate to `logs/campaigns/<campaign_id>/` and open `.md` files in any text editor.

## Log Contents

### Campaign Log
- Campaign ID, name, and parameters
- Timeline (start, end, duration)
- Phase-by-phase execution summary
- Agents executed per phase
- Outputs produced
- Performance metrics (tokens, API calls, cost)
- Errors and warnings
- Success criteria evaluation

### Agent Log
- Agent name, model, and execution ID
- Campaign and phase context
- Input content and parameters
- Step-by-step execution trace
- Output files and summaries
- Performance metrics
- Data quality scores
- Errors and warnings

### Performance Summary
- Total duration and cost
- Breakdown by phase and agent
- Bottleneck identification
- Optimization suggestions

### Error Log
- All errors and warnings with timestamps
- Severity levels (critical/error/warning)
- Error context and affected data
- Resolution steps taken
- Error counts by agent

### Data Quality Audit
- Filters applied (sponsors removed)
- Duplicate resolution decisions
- Quality score assignments
- Audit trail for transparency

## Log Retention

- **Active campaigns**: Keep indefinitely
- **Completed campaigns**: Keep 30 days in `campaigns/`
- **Archived**: Moved to `archive/` after 30 days, kept 1 year
- **Historical summaries**: Kept forever (small size)

## Analysis Examples

### Find All Errors in a Campaign
```bash
campaign_id="campaign_20240115_abc123"
cat logs/campaigns/$campaign_id/error_log.json | jq '.errors[]'
```

### Calculate Average Execution Time for an Agent
```bash
cat logs/agents/web-researcher/execution_history.json | \
  jq '.executions[].duration_seconds' | \
  awk '{sum+=$1; count++} END {print sum/count}'
```

### Compare Performance Across Campaigns
```bash
for dir in logs/campaigns/*/; do
  echo "$dir:"
  cat "$dir/performance_summary.json" | jq '.overview.total_duration_seconds'
done
```

### Generate Cost Report by Phase
```bash
cat logs/campaigns/*/performance_summary.json | \
  jq '.by_phase | to_entries[] | {phase: .key, cost: .value.cost_usd}'
```

## Troubleshooting

### Dashboard Not Loading
- Ensure `current_execution.json` exists in `logs/` directory
- Check browser console for JavaScript errors
- Verify web server has read access to `logs/` directory

### Missing Logs
- Confirm agents have logging instructions enabled
- Check agent execution completed successfully
- Verify file permissions on `logs/` directory

### Large Log Files
- Archive old campaigns: Move to `archive/` directory
- Compress archived logs: `tar -czf archive_YYYYMM.tar.gz logs/archive/campaign_*`
- Clean up: Delete archived logs older than 1 year

## Best Practices

1. **Review logs after each campaign** to identify performance issues
2. **Monitor error_log.json** for recurring problems
3. **Use dashboard for live monitoring** during critical campaigns
4. **Archive old logs regularly** to manage disk space
5. **Analyze performance trends** across multiple campaigns
6. **Document unusual patterns** for future reference

## Support

For questions about the logging system:
- Review `specs/sponsor-finder-spec.md` for system architecture
- Check `CLAUDE.md` for agent definitions and workflow
- Inspect log schemas in this README for structure reference

---

Last Updated: 2024-01-15
Version: 1.0.0
