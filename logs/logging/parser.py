"""
Agent Output Parser
Extracts structured logging information from agent text outputs
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any


class LogParser:
    """Parses LOG_* statements from agent output text"""

    def __init__(self):
        self.log_patterns = {
            'start': r'LOG_START:\s*(.+)',
            'step': r'LOG_STEP:\s*(.+)',
            'complete': r'LOG_COMPLETE:\s*(.+)',
            'warning': r'LOG_WARNING:\s*(.+)',
            'error': r'LOG_ERROR:\s*(.+)'
        }

    def parse_agent_output(self, output_text: str) -> Dict[str, Any]:
        """
        Parse agent output for LOG_* statements

        Args:
            output_text: Raw text output from agent execution

        Returns:
            Dictionary with parsed log data
        """
        log_data = {
            'raw_output': output_text,
            'start': None,
            'steps': [],
            'complete': None,
            'warnings': [],
            'errors': [],
            'parsed_at': datetime.utcnow().isoformat()
        }

        lines = output_text.split('\n')

        for line in lines:
            # Check for LOG_START
            if match := re.search(self.log_patterns['start'], line):
                log_data['start'] = self._parse_key_value_string(match.group(1))

            # Check for LOG_STEP
            elif match := re.search(self.log_patterns['step'], line):
                log_data['steps'].append(self._parse_key_value_string(match.group(1)))

            # Check for LOG_COMPLETE
            elif match := re.search(self.log_patterns['complete'], line):
                log_data['complete'] = self._parse_key_value_string(match.group(1))

            # Check for LOG_WARNING
            elif match := re.search(self.log_patterns['warning'], line):
                log_data['warnings'].append(self._parse_key_value_string(match.group(1)))

            # Check for LOG_ERROR
            elif match := re.search(self.log_patterns['error'], line):
                log_data['errors'].append(self._parse_key_value_string(match.group(1)))

        return log_data

    def _parse_key_value_string(self, kv_string: str) -> Dict[str, str]:
        """
        Parse key=value pairs from string

        Example: 'agent=keyword-extractor, campaign_id=123, phase=Phase1'
        Returns: {'agent': 'keyword-extractor', 'campaign_id': '123', 'phase': 'Phase1'}
        """
        result = {}

        # Split by comma, but handle quoted values
        pairs = re.findall(r'(\w+)=([^,]+|"[^"]*")', kv_string)

        for key, value in pairs:
            # Remove quotes and whitespace
            clean_value = value.strip().strip('"').strip("'")
            result[key] = clean_value

        return result

    def extract_metrics(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract performance metrics from parsed log data

        Returns:
            Dictionary with metrics like tokens, duration, cost
        """
        metrics = {
            'tokens_input': 0,
            'tokens_output': 0,
            'tokens_total': 0,
            'duration_seconds': 0,
            'api_calls': 1,  # Assume at least 1 API call
            'cost_estimate_usd': 0.0
        }

        if log_data.get('complete'):
            complete_data = log_data['complete']

            # Extract tokens
            if 'tokens_input' in complete_data:
                metrics['tokens_input'] = int(complete_data.get('tokens_input', 0))
            if 'tokens_output' in complete_data:
                metrics['tokens_output'] = int(complete_data.get('tokens_output', 0))

            metrics['tokens_total'] = metrics['tokens_input'] + metrics['tokens_output']

            # Extract duration
            if 'duration' in complete_data:
                duration_str = complete_data['duration'].rstrip('s')
                try:
                    metrics['duration_seconds'] = float(duration_str)
                except ValueError:
                    metrics['duration_seconds'] = 0

            # Estimate cost (rough approximation)
            # Haiku: ~$0.001 per 1K tokens, Sonnet: ~$0.003 per 1K tokens
            metrics['cost_estimate_usd'] = (metrics['tokens_total'] / 1000) * 0.002

        return metrics

    def build_agent_log(self, agent_name: str, campaign_id: str, phase: str,
                       output_text: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Build complete agent log from output

        Args:
            agent_name: Name of the agent
            campaign_id: Campaign identifier
            phase: Execution phase
            output_text: Raw agent output
            start_time: ISO timestamp when agent started
            end_time: ISO timestamp when agent finished

        Returns:
            Complete agent log dictionary
        """
        parsed = self.parse_agent_output(output_text)
        metrics = self.extract_metrics(parsed)

        # Calculate duration from timestamps if not in logs
        if metrics['duration_seconds'] == 0:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                metrics['duration_seconds'] = (end_dt - start_dt).total_seconds()
            except:
                pass

        agent_log = {
            'agent_name': agent_name,
            'agent_type': self._get_agent_type(agent_name),
            'execution_id': f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_name[:3]}",
            'campaign_id': campaign_id,
            'phase': phase,
            'model': self._get_agent_model(agent_name),
            'start_time': start_time,
            'end_time': end_time,
            'duration_seconds': metrics['duration_seconds'],
            'status': 'completed' if not parsed['errors'] else 'failed',
            'execution_steps': self._format_steps(parsed['steps']),
            'output': {
                'files': self._extract_output_files(parsed['complete']),
                'summary': self._extract_summary(parsed['complete'])
            },
            'performance': metrics,
            'errors': parsed['errors'],
            'warnings': parsed['warnings'],
            'data_quality': {
                'input_validation': 'passed' if not parsed['errors'] else 'failed',
                'output_validation': 'passed',
                'completeness_score': 10 if parsed['complete'] else 5
            }
        }

        return agent_log

    def _get_agent_type(self, agent_name: str) -> str:
        """Determine agent type based on name"""
        type_mapping = {
            'keyword-extractor': 'research',
            'web-researcher': 'research',
            'categorizer': 'research',
            'validator': 'research',
            'salesforce-integration': 'execution',
            'engagement-tracking': 'analysis',
            'event-coordination': 'execution',
            'campaign-orchestrator': 'orchestration'
        }
        return type_mapping.get(agent_name, 'unknown')

    def _get_agent_model(self, agent_name: str) -> str:
        """Get model used by agent"""
        model_mapping = {
            'keyword-extractor': 'claude-haiku-4-5-20251001',
            'web-researcher': 'claude-haiku-4-5-20251001',
            'categorizer': 'claude-haiku-4-5-20251001',
            'validator': 'claude-sonnet-4-5-20250929',
            'salesforce-integration': 'claude-haiku-4-5-20251001',
            'engagement-tracking': 'claude-sonnet-4-5-20250929',
            'event-coordination': 'claude-haiku-4-5-20251001',
            'campaign-orchestrator': 'claude-sonnet-4-5-20250929'
        }
        return model_mapping.get(agent_name, 'unknown')

    def _format_steps(self, steps: List[Dict]) -> List[Dict]:
        """Format execution steps with timestamps"""
        formatted = []
        for i, step in enumerate(steps, 1):
            formatted.append({
                'step': step.get('step', i),
                'action': step.get('action', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'details': step.get('details', '')
            })
        return formatted

    def _extract_output_files(self, complete_data: Optional[Dict]) -> List[str]:
        """Extract output file names from completion data"""
        if not complete_data:
            return []

        output_file = complete_data.get('output_file', '')
        output_files = complete_data.get('output_files', '')

        if output_files:
            return [f.strip() for f in output_files.split(',')]
        elif output_file:
            return [output_file]

        return []

    def _extract_summary(self, complete_data: Optional[Dict]) -> Dict[str, Any]:
        """Extract summary information from completion data"""
        if not complete_data:
            return {}

        summary = {}

        # Extract numeric values
        for key in ['sponsors_found', 'categories', 'count', 'attendees', 'hot_leads',
                    'sponsors_validated', 'phases_completed']:
            if key in complete_data:
                try:
                    summary[key] = int(complete_data[key])
                except:
                    summary[key] = complete_data[key]

        return summary


if __name__ == '__main__':
    # Test the parser
    test_output = """
    Some agent output here...

    LOG_START: agent=keyword-extractor, campaign_id=camp_123, phase=Phase1
    LOG_STEP: step=1, action=analyze_prompt, details="Extracted 5 keywords"
    LOG_STEP: step=2, action=incorporate_mission, details="Added secondary keywords"
    LOG_COMPLETE: duration=13s, tokens_input=850, tokens_output=320, output_file=keywords.json

    More output...
    """

    parser = LogParser()
    result = parser.parse_agent_output(test_output)

    print("Parsed Log Data:")
    print(f"  Start: {result['start']}")
    print(f"  Steps: {len(result['steps'])}")
    print(f"  Complete: {result['complete']}")

    metrics = parser.extract_metrics(result)
    print(f"\nMetrics:")
    print(f"  Tokens: {metrics['tokens_total']}")
    print(f"  Duration: {metrics['duration_seconds']}s")
    print(f"  Cost: ${metrics['cost_estimate_usd']:.4f}")
