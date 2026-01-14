"""
Campaign Logger
Main logging interface for sponsor-finder campaigns
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from parser import LogParser
from writer import LogWriter


class CampaignLogger:
    """Main logger for campaign execution"""

    def __init__(self, campaign_name: str, parameters: Dict[str, Any]):
        """
        Initialize campaign logger

        Args:
            campaign_name: Human-readable campaign name
            parameters: Campaign parameters (goal, location, etc.)
        """
        self.campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        self.campaign_name = campaign_name
        self.parameters = parameters
        self.start_time = datetime.utcnow().isoformat()
        self.end_time = None

        self.parser = LogParser()
        self.writer = LogWriter()

        self.phases = []
        self.all_errors = []
        self.all_warnings = []
        self.agent_logs = []

        print(f"\n{'='*60}")
        print(f"Campaign Started: {campaign_name}")
        print(f"Campaign ID: {self.campaign_id}")
        print(f"{'='*60}\n")

    def log_agent_execution(self, agent_name: str, phase: str,
                           output_text: str, start_time: str, end_time: str):
        """
        Log an agent execution

        Args:
            agent_name: Name of the agent executed
            phase: Execution phase
            output_text: Raw text output from agent
            start_time: ISO timestamp when started
            end_time: ISO timestamp when finished
        """
        print(f"  Logging {agent_name}...")

        # Parse agent output
        agent_log = self.parser.build_agent_log(
            agent_name=agent_name,
            campaign_id=self.campaign_id,
            phase=phase,
            output_text=output_text,
            start_time=start_time,
            end_time=end_time
        )

        # Store agent log
        self.agent_logs.append(agent_log)

        # Collect errors/warnings
        self.all_errors.extend(agent_log.get('errors', []))
        self.all_warnings.extend(agent_log.get('warnings', []))

        # Write agent log files
        self.writer.write_agent_log(agent_log, self.campaign_id)

        # Update current execution for dashboard
        self._update_current_execution(agent_name, phase)

        return agent_log

    def start_phase(self, phase_number: int, phase_name: str):
        """Start tracking a new phase"""
        phase = {
            'phase_number': phase_number,
            'phase_name': phase_name,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'status': 'in_progress',
            'agents_executed': [],
            'outputs_produced': [],
            'errors': [],
            'warnings': []
        }
        self.phases.append(phase)

        print(f"\n{'─'*60}")
        print(f"Phase {phase_number}: {phase_name}")
        print(f"{'─'*60}")

        return phase

    def end_phase(self, phase_number: int, outputs: List[str] = None):
        """End the current phase"""
        if phase_number <= len(self.phases):
            phase = self.phases[phase_number - 1]
            phase['end_time'] = datetime.utcnow().isoformat()

            # Calculate duration
            start_dt = datetime.fromisoformat(phase['start_time'].replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(phase['end_time'].replace('Z', '+00:00'))
            phase['duration_seconds'] = (end_dt - start_dt).total_seconds()

            phase['status'] = 'completed'
            phase['outputs_produced'] = outputs or []

            # Collect agents from this phase
            for agent_log in self.agent_logs:
                if agent_log['phase'].startswith(f"Phase {phase_number}"):
                    phase['agents_executed'].append(agent_log['agent_name'])

            print(f"✓ Phase {phase_number} completed in {phase['duration_seconds']:.1f}s\n")

    def finalize(self):
        """Finalize campaign and write all logs"""
        self.end_time = datetime.utcnow().isoformat()

        print(f"\n{'='*60}")
        print(f"Finalizing Campaign Logs")
        print(f"{'='*60}\n")

        # Calculate total duration
        start_dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        duration_seconds = (end_dt - start_dt).total_seconds()

        # Build campaign log
        campaign_log = {
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_seconds': duration_seconds,
            'status': 'completed' if not self.all_errors else 'partial',
            'initiated_by': 'user',
            'parameters': self.parameters,
            'phases': self.phases,
            'summary': self._build_summary(),
            'errors': self.all_errors,
            'warnings': self.all_warnings
        }

        # Write campaign log
        self.writer.write_campaign_log(campaign_log)

        # Write performance summary
        performance_summary = self._build_performance_summary()
        self.writer.write_performance_summary(performance_summary, self.campaign_id)

        # Write error log
        if self.all_errors or self.all_warnings:
            all_issues = self.all_errors + self.all_warnings
            self.writer.write_error_log(all_issues, self.campaign_id)

        # Clear current execution
        self._clear_current_execution()

        print(f"\n{'='*60}")
        print(f"Campaign Complete: {self.campaign_name}")
        print(f"Duration: {duration_seconds:.1f}s")
        print(f"Logs: logs/campaigns/{self.campaign_id}/")
        print(f"{'='*60}\n")

    def _build_summary(self) -> Dict[str, Any]:
        """Build campaign summary"""
        total_tokens = sum(log['performance']['tokens_total'] for log in self.agent_logs)
        total_api_calls = sum(log['performance']['api_calls'] for log in self.agent_logs)
        total_cost = sum(log['performance']['cost_estimate_usd'] for log in self.agent_logs)

        # Count sponsors found
        sponsors_found = 0
        sponsors_validated = 0
        for log in self.agent_logs:
            if 'sponsors_found' in log['output'].get('summary', {}):
                sponsors_found = log['output']['summary']['sponsors_found']
            if 'sponsors_validated' in log['output'].get('summary', {}):
                sponsors_validated = log['output']['summary']['sponsors_validated']

        return {
            'total_agents_executed': len(self.agent_logs),
            'total_api_calls': total_api_calls,
            'total_tokens_used': total_tokens,
            'sponsors_found': sponsors_found,
            'sponsors_validated': sponsors_validated,
            'success_rate': 100.0 if not self.all_errors else 75.0,
            'estimated_cost_usd': total_cost
        }

    def _build_performance_summary(self) -> Dict[str, Any]:
        """Build performance summary with bottleneck analysis"""
        # Calculate total duration
        start_dt = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        total_duration = (end_dt - start_dt).total_seconds()

        # Aggregate by phase
        by_phase = {}
        for phase in self.phases:
            phase_key = f"phase_{phase['phase_number']}"
            phase_tokens = sum(
                log['performance']['tokens_total']
                for log in self.agent_logs
                if log['phase'].startswith(f"Phase {phase['phase_number']}")
            )
            phase_cost = sum(
                log['performance']['cost_estimate_usd']
                for log in self.agent_logs
                if log['phase'].startswith(f"Phase {phase['phase_number']}")
            )

            by_phase[phase_key] = {
                'duration_seconds': phase['duration_seconds'],
                'agents': len(phase['agents_executed']),
                'tokens': phase_tokens,
                'cost_usd': phase_cost
            }

        # Aggregate by agent
        by_agent = {}
        for log in self.agent_logs:
            agent = log['agent_name']
            by_agent[agent] = {
                'executions': 1,
                'avg_duration_seconds': log['duration_seconds'],
                'tokens_used': log['performance']['tokens_total'],
                'success_rate': 100.0 if not log['errors'] else 0.0
            }

        # Identify bottlenecks
        bottlenecks = []
        for log in self.agent_logs:
            if log['duration_seconds'] > 30:  # Agents taking >30s
                percentage = (log['duration_seconds'] / total_duration) * 100
                bottlenecks.append({
                    'agent': log['agent_name'],
                    'duration_seconds': log['duration_seconds'],
                    'percentage_of_total': round(percentage, 1)
                })

        bottlenecks.sort(key=lambda x: x['duration_seconds'], reverse=True)

        # Generate optimization suggestions
        suggestions = []
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            suggestions.append(
                f"{top_bottleneck['agent']} takes {top_bottleneck['percentage_of_total']}% of total time - consider optimization"
            )

        total_tokens = sum(log['performance']['tokens_total'] for log in self.agent_logs)
        total_cost = sum(log['performance']['cost_estimate_usd'] for log in self.agent_logs)

        return {
            'campaign_id': self.campaign_id,
            'generated_at': datetime.utcnow().isoformat(),
            'overview': {
                'total_duration_seconds': total_duration,
                'total_agents': len(self.agent_logs),
                'total_api_calls': sum(log['performance']['api_calls'] for log in self.agent_logs),
                'total_tokens': total_tokens,
                'estimated_cost_usd': total_cost
            },
            'by_phase': by_phase,
            'by_agent': by_agent,
            'bottlenecks': bottlenecks,
            'optimization_suggestions': suggestions
        }

    def _update_current_execution(self, current_agent: str, current_phase: str):
        """Update current_execution.json for live dashboard"""
        # Find current phase number
        phase_number = 0
        for phase in self.phases:
            if phase['status'] == 'in_progress':
                phase_number = phase['phase_number']
                break

        execution_data = {
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'status': 'in_progress',
            'start_time': self.start_time,
            'current_phase': current_phase,
            'current_agent': current_agent,
            'phases': self.phases,
            'summary': {
                'total_tokens_used': sum(log['performance']['tokens_total'] for log in self.agent_logs),
                'total_api_calls': sum(log['performance']['api_calls'] for log in self.agent_logs),
                'estimated_cost_usd': sum(log['performance']['cost_estimate_usd'] for log in self.agent_logs),
                'sponsors_found': 0  # Will be updated as we go
            },
            'recent_logs': [
                {
                    'timestamp': log['end_time'],
                    'agent': log['agent_name'],
                    'message': f"Completed in {log['duration_seconds']:.1f}s",
                    'severity': 'info'
                }
                for log in self.agent_logs[-5:]  # Last 5 logs
            ],
            'errors': self.all_errors,
            'warnings': self.all_warnings
        }

        self.writer.write_current_execution(execution_data)

    def _clear_current_execution(self):
        """Clear current execution status"""
        execution_data = {
            'campaign_id': None,
            'status': 'idle',
            'message': 'No active campaign'
        }
        self.writer.write_current_execution(execution_data)


if __name__ == '__main__':
    # Test the logger
    logger = CampaignLogger(
        campaign_name="Test Campaign",
        parameters={
            'description': 'Find sponsors for test',
            'goal_amount': 100000,
            'location': 'NYC'
        }
    )

    # Simulate Phase 1
    phase1 = logger.start_phase(1, "Research & Discovery")

    # Simulate agent execution
    test_output = """
    LOG_START: agent=keyword-extractor, campaign_id=test, phase=Phase1
    LOG_STEP: step=1, action=analyze_prompt, details="Extracted 5 keywords"
    LOG_COMPLETE: duration=13s, tokens_input=850, tokens_output=320, output_file=keywords.json
    """

    logger.log_agent_execution(
        agent_name='keyword-extractor',
        phase='Phase 1: Research',
        output_text=test_output,
        start_time=datetime.utcnow().isoformat(),
        end_time=datetime.utcnow().isoformat()
    )

    logger.end_phase(1, outputs=['keywords.json'])

    # Finalize
    logger.finalize()

    print("✓ Test campaign logged successfully")
