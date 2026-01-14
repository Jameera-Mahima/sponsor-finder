"""
Log File Writer
Writes parsed log data to JSON and Markdown files
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class LogWriter:
    """Writes log data to files in JSON and Markdown formats"""

    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    def write_agent_log(self, agent_log: Dict[str, Any], campaign_id: str):
        """
        Write agent execution log in both JSON and Markdown

        Args:
            agent_log: Parsed agent log dictionary
            campaign_id: Campaign identifier
        """
        agent_name = agent_log['agent_name']

        # Write to campaign directory
        campaign_dir = self.logs_dir / "campaigns" / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        json_file = campaign_dir / f"agent_{agent_name}.json"
        md_file = campaign_dir / f"agent_{agent_name}.md"

        self._write_json(json_file, agent_log)
        self._write_agent_markdown(md_file, agent_log)

        # Write to agent history directory
        agent_dir = self.logs_dir / "agents" / agent_name / "runs"
        agent_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file_agent = agent_dir / f"{timestamp}.json"
        md_file_agent = agent_dir / f"{timestamp}.md"

        self._write_json(json_file_agent, agent_log)
        self._write_agent_markdown(md_file_agent, agent_log)

        print(f"✓ Wrote agent log: {agent_name}")

    def write_campaign_log(self, campaign_log: Dict[str, Any]):
        """
        Write campaign-level log

        Args:
            campaign_log: Campaign log dictionary
        """
        campaign_id = campaign_log['campaign_id']
        campaign_dir = self.logs_dir / "campaigns" / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        json_file = campaign_dir / "campaign_log.json"
        md_file = campaign_dir / "campaign_log.md"

        self._write_json(json_file, campaign_log)
        self._write_campaign_markdown(md_file, campaign_log)

        print(f"✓ Wrote campaign log: {campaign_id}")

    def write_performance_summary(self, summary: Dict[str, Any], campaign_id: str):
        """Write performance summary"""
        campaign_dir = self.logs_dir / "campaigns" / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        json_file = campaign_dir / "performance_summary.json"
        self._write_json(json_file, summary)

        print(f"✓ Wrote performance summary")

    def write_error_log(self, errors: List[Dict], campaign_id: str):
        """Write error log"""
        campaign_dir = self.logs_dir / "campaigns" / campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        error_log = {
            'campaign_id': campaign_id,
            'errors': errors,
            'summary': {
                'total_errors': len([e for e in errors if e.get('severity') == 'error']),
                'total_warnings': len([e for e in errors if e.get('severity') == 'warning']),
                'critical_errors': len([e for e in errors if e.get('severity') == 'critical'])
            }
        }

        json_file = campaign_dir / "error_log.json"
        self._write_json(json_file, error_log)

        print(f"✓ Wrote error log ({len(errors)} issues)")

    def write_current_execution(self, execution_data: Dict[str, Any]):
        """Write current execution status for dashboard"""
        json_file = self.logs_dir / "current_execution.json"
        self._write_json(json_file, execution_data)

    def _write_json(self, filepath: Path, data: Dict[str, Any]):
        """Write JSON file with pretty formatting"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _write_agent_markdown(self, filepath: Path, agent_log: Dict[str, Any]):
        """Write agent log in Markdown format"""
        content = f"""# Agent Execution Log: {agent_log['agent_name']}

**Execution ID:** {agent_log['execution_id']}
**Campaign:** {agent_log['campaign_id']}
**Phase:** {agent_log['phase']}
**Model:** {agent_log['model']}
**Status:** {self._status_emoji(agent_log['status'])} {agent_log['status'].title()}
**Duration:** {agent_log['duration_seconds']:.1f} seconds

---

## Timeline
- **Started:** {agent_log['start_time']}
- **Completed:** {agent_log['end_time']}

---

## Execution Steps

"""
        # Add steps
        for step in agent_log.get('execution_steps', []):
            content += f"### Step {step['step']}: {step['action'].replace('_', ' ').title()}\n"
            content += f"{step['details']}\n\n"

        # Add output
        content += f"""---

## Output

**Files Generated:**
"""
        for output_file in agent_log['output'].get('files', []):
            content += f"- {output_file}\n"

        if agent_log['output'].get('summary'):
            content += "\n**Summary:**\n"
            for key, value in agent_log['output']['summary'].items():
                content += f"- **{key.replace('_', ' ').title()}:** {value}\n"

        # Add performance metrics
        perf = agent_log['performance']
        content += f"""

---

## Performance Metrics

- **Tokens Input:** {perf['tokens_input']:,}
- **Tokens Output:** {perf['tokens_output']:,}
- **Total Tokens:** {perf['tokens_total']:,}
- **API Calls:** {perf['api_calls']}
- **Estimated Cost:** ${perf['cost_estimate_usd']:.4f}

---

## Data Quality

- **Input Validation:** {self._check_emoji(agent_log['data_quality']['input_validation'])} {agent_log['data_quality']['input_validation'].title()}
- **Output Validation:** {self._check_emoji(agent_log['data_quality']['output_validation'])} {agent_log['data_quality']['output_validation'].title()}
- **Completeness Score:** {agent_log['data_quality']['completeness_score']}/10

---

## Issues

"""
        # Add errors and warnings
        if agent_log.get('errors'):
            content += "### Errors\n"
            for error in agent_log['errors']:
                content += f"- ❌ **{error.get('severity', 'error').upper()}:** {error.get('message', 'Unknown error')}\n"
                if error.get('recovery'):
                    content += f"  - *Resolution:* {error['recovery']}\n"
            content += "\n"

        if agent_log.get('warnings'):
            content += "### Warnings\n"
            for warning in agent_log['warnings']:
                content += f"- ⚠️ **{warning.get('severity', 'warning').upper()}:** {warning.get('message', 'Unknown warning')}\n"
            content += "\n"

        if not agent_log.get('errors') and not agent_log.get('warnings'):
            content += "✅ No errors or warnings\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _write_campaign_markdown(self, filepath: Path, campaign_log: Dict[str, Any]):
        """Write campaign log in Markdown format"""
        content = f"""# Campaign Execution Log

**Campaign ID:** {campaign_log['campaign_id']}
**Campaign Name:** {campaign_log.get('campaign_name', 'Unknown')}
**Status:** {self._status_emoji(campaign_log['status'])} {campaign_log['status'].title()}
**Duration:** {self._format_duration(campaign_log.get('duration_seconds', 0))}

## Parameters

"""
        # Add parameters
        for key, value in campaign_log.get('parameters', {}).items():
            content += f"- **{key.replace('_', ' ').title()}:** {value}\n"

        content += f"""

## Timeline
- **Started:** {campaign_log.get('start_time', 'Unknown')}
- **Completed:** {campaign_log.get('end_time', 'Unknown')}

---

"""
        # Add phases
        for phase in campaign_log.get('phases', []):
            content += f"""## Phase {phase['phase_number']}: {phase['phase_name']}
⏱️ Duration: {self._format_duration(phase.get('duration_seconds', 0))} | {self._status_emoji(phase['status'])} Status: {phase['status'].title()}

**Agents Executed:**
"""
            for agent in phase.get('agents_executed', []):
                content += f"- {self._status_emoji('completed')} {agent}\n"

            content += f"\n**Outputs Produced:**\n"
            for output in phase.get('outputs_produced', []):
                content += f"- {output}\n"

            if phase.get('warnings'):
                content += f"\n**Warnings:**\n"
                for warning in phase['warnings']:
                    content += f"- ⚠️ {warning}\n"

            content += "\n---\n\n"

        # Add summary
        summary = campaign_log.get('summary', {})
        content += f"""## Summary

### Results
- **Total Agents Executed:** {summary.get('total_agents_executed', 0)}
- **Total API Calls:** {summary.get('total_api_calls', 0)}
- **Total Tokens Used:** {summary.get('total_tokens_used', 0):,}
- **Success Rate:** {summary.get('success_rate', 0):.1f}%

### Performance
- **Estimated Cost:** ${summary.get('estimated_cost_usd', 0):.2f}

### Issues
- **Errors:** {len(campaign_log.get('errors', []))}
- **Warnings:** {len(campaign_log.get('warnings', []))}

---

## Files Generated
- `logs/campaigns/{campaign_log['campaign_id']}/` - All execution logs
- `docs/{campaign_log['campaign_id']}/` - Campaign results and reports
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        emojis = {
            'completed': '✅',
            'in_progress': '🔄',
            'failed': '❌',
            'partial': '⚠️',
            'pending': '⏳'
        }
        return emojis.get(status, '❓')

    def _check_emoji(self, status: str) -> str:
        """Get check/cross emoji"""
        return '✅' if status == 'passed' else '❌'

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"


if __name__ == '__main__':
    # Test the writer
    test_agent_log = {
        'agent_name': 'keyword-extractor',
        'agent_type': 'research',
        'execution_id': 'exec_20240115_143022_key',
        'campaign_id': 'campaign_20240115_abc123',
        'phase': 'Phase 1: Research',
        'model': 'claude-haiku-4-5-20251001',
        'start_time': '2024-01-15T14:30:22Z',
        'end_time': '2024-01-15T14:30:35Z',
        'duration_seconds': 13,
        'status': 'completed',
        'execution_steps': [
            {'step': 1, 'action': 'analyze_prompt', 'timestamp': '2024-01-15T14:30:23Z', 'details': 'Extracted 5 keywords'},
            {'step': 2, 'action': 'incorporate_mission', 'timestamp': '2024-01-15T14:30:28Z', 'details': 'Added secondary keywords'}
        ],
        'output': {
            'files': ['keywords.json'],
            'summary': {'primary_keywords': 5, 'secondary_keywords': 10}
        },
        'performance': {
            'tokens_input': 850,
            'tokens_output': 320,
            'tokens_total': 1170,
            'api_calls': 1,
            'cost_estimate_usd': 0.002
        },
        'errors': [],
        'warnings': [],
        'data_quality': {
            'input_validation': 'passed',
            'output_validation': 'passed',
            'completeness_score': 10
        }
    }

    writer = LogWriter()
    writer.write_agent_log(test_agent_log, 'campaign_20240115_abc123')
    print("✓ Test log files written successfully")
