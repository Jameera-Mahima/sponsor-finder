# Logging Infrastructure

This directory contains the Python-based logging infrastructure that captures all agent execution details.

## Components

### 1. parser.py
Parses LOG_* statements from agent text outputs and extracts structured data.

**Features:**
- Parses LOG_START, LOG_STEP, LOG_COMPLETE, LOG_WARNING, LOG_ERROR
- Extracts key=value pairs from log statements
- Calculates performance metrics (tokens, duration, cost)
- Builds complete agent log objects

**Usage:**
```python
from parser import LogParser

parser = LogParser()
log_data = parser.parse_agent_output(agent_text_output)
metrics = parser.extract_metrics(log_data)
```

### 2. writer.py
Writes log data to files in both JSON and Markdown formats.

**Features:**
- Writes agent logs (JSON + MD)
- Writes campaign logs (JSON + MD)
- Writes performance summaries
- Writes error logs
- Updates current_execution.json for dashboard

**Usage:**
```python
from writer import LogWriter

writer = LogWriter()
writer.write_agent_log(agent_log, campaign_id)
writer.write_campaign_log(campaign_log)
```

### 3. logger.py
Main logging interface - coordinates parser and writer.

**Features:**
- Campaign-level logging
- Phase tracking
- Agent execution logging
- Automatic metric aggregation
- Performance analysis
- Bottleneck identification

**Usage:**
```python
from logger import CampaignLogger

# Initialize
logger = CampaignLogger(
    campaign_name="My Campaign",
    parameters={'goal': 100000}
)

# Track phases
logger.start_phase(1, "Research")

# Log agents
logger.log_agent_execution(
    agent_name='keyword-extractor',
    phase='Phase 1',
    output_text=agent_output,
    start_time=start_time,
    end_time=end_time
)

# Finalize
logger.end_phase(1, outputs=['file.json'])
logger.finalize()
```

### 4. example_usage.py
Complete examples showing how to integrate logging.

**Run examples:**
```bash
# Run full example
python logs/logging/example_usage.py

# Show usage guide
python logs/logging/example_usage.py --guide

# Run error handling example
python logs/logging/example_usage.py --error
```

## Integration Pattern

### Step-by-Step Integration

**1. Import the logger:**
```python
from logs.logging.logger import CampaignLogger
from datetime import datetime
```

**2. Initialize at campaign start:**
```python
logger = CampaignLogger(
    campaign_name="Christmas Education Campaign 2024",
    parameters={
        'description': 'Find sponsors for $500k education campaign in NYC',
        'goal_amount': 500000,
        'location': 'New York City'
    }
)
```

**3. For each phase:**
```python
logger.start_phase(1, "Research & Discovery")

# ... execute agents ...

logger.end_phase(1, outputs=['keywords.json', 'report.md'])
```

**4. For each agent:**
```python
# Capture start time
start_time = datetime.utcnow().isoformat()

# Execute agent (via Task tool or other method)
agent_output = execute_agent('keyword-extractor', ...)

# Capture end time
end_time = datetime.utcnow().isoformat()

# Log execution
logger.log_agent_execution(
    agent_name='keyword-extractor',
    phase='Phase 1: Research & Discovery',
    output_text=agent_output,
    start_time=start_time,
    end_time=end_time
)
```

**5. Finalize campaign:**
```python
logger.finalize()
```

## Agent Output Requirements

Agents MUST include LOG_* statements in their output for proper logging:

```
LOG_START: agent=<agent_name>, campaign_id=<id>, phase=<phase>
LOG_STEP: step=<number>, action=<action_name>, details="<description>"
LOG_COMPLETE: duration=<seconds>s, tokens_input=<count>, tokens_output=<count>, output_file=<filename>
LOG_WARNING: severity=<low/medium/high>, message="<warning_text>"
LOG_ERROR: severity=<error/critical>, message="<error_text>", recovery="<what_was_done>"
```

**Example agent output:**
```
Some agent processing...

LOG_START: agent=keyword-extractor, campaign_id=camp_123, phase=Phase1
LOG_STEP: step=1, action=analyze_prompt, details="Extracted 5 keywords"
LOG_STEP: step=2, action=incorporate_mission, details="Added 10 secondary keywords"
LOG_COMPLETE: duration=13s, tokens_input=850, tokens_output=320, output_file=keywords.json

Keywords generated successfully.
```

## Output Structure

When you run a campaign with logging, it creates:

```
logs/
├── campaigns/<campaign_id>/
│   ├── campaign_log.json          # Master log (JSON)
│   ├── campaign_log.md            # Master log (Markdown)
│   ├── agent_<name>.json          # Per-agent logs (JSON)
│   ├── agent_<name>.md            # Per-agent logs (Markdown)
│   ├── performance_summary.json   # Metrics and bottlenecks
│   ├── error_log.json             # Errors and warnings
│   └── data_quality_audit.json    # Quality decisions
│
├── agents/<agent_name>/runs/
│   ├── YYYYMMDD_HHMMSS.json      # Historical agent runs
│   └── YYYYMMDD_HHMMSS.md
│
└── current_execution.json         # Real-time status for dashboard
```

## Testing

### Test the parser:
```bash
cd logs/logging
python parser.py
```

### Test the writer:
```bash
cd logs/logging
python writer.py
```

### Test the logger:
```bash
cd logs/logging
python logger.py
```

### Run full example:
```bash
cd logs/logging
python example_usage.py
```

## Dependencies

**Required:**
- Python 3.7+
- No external dependencies (uses only standard library)

**Files:**
- `parser.py` - Log parsing
- `writer.py` - File writing
- `logger.py` - Main interface
- `example_usage.py` - Usage examples

## Troubleshooting

**No logs being created?**
- Ensure agents are outputting LOG_* statements
- Check that logger.finalize() is called
- Verify write permissions on logs/ directory

**Dashboard shows "Idle"?**
- Check if `current_execution.json` exists
- Ensure logger._update_current_execution() is being called
- Try refreshing the browser

**Parsing errors?**
- Verify LOG_* statement format matches pattern
- Check for proper key=value syntax
- Ensure quotes are escaped in values

**Missing metrics?**
- Agents must output LOG_COMPLETE with tokens_input/tokens_output
- Provide start_time and end_time to log_agent_execution()
- Check that duration is included in LOG_COMPLETE

## Performance

**Overhead:**
- Minimal (<1% of execution time)
- Parsing is fast (regex-based)
- File I/O is buffered and async-friendly

**Storage:**
- ~10-50KB per agent execution
- ~100-500KB per complete campaign
- Archive old logs regularly

## Next Steps

1. **Test locally**: Run example_usage.py to see it in action
2. **Integrate**: Add logging to your run-campaign orchestration
3. **Monitor**: Open dashboard while campaign runs
4. **Analyze**: Query JSON logs for performance insights

For integration examples, see `example_usage.py`.
For dashboard usage, see `../README.md` (parent directory).
