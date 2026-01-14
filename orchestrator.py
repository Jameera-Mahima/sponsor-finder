"""
Healing NY Sponsor Finder - Orchestrator
Coordinates subagents for complete sponsor search workflow

Usage in Claude Code:
    'Execute orchestrator workflow for: [your prompt]'
"""

class SponsorOrchestrator:
    '''
    Main orchestration engine for sponsor search
    '''
    
    def __init__(self):
        self.workflow_phases = {
            1: 'keyword-extractor',
            2: 'web-researcher',
            3: 'categorizer',
            4: 'validator'
        }
        
        self.mission_context = '''
        Healing NY Mission:
        - Mental health support
        - Arts education  
        - Community healing
        - New York focus
        '''
    
    def execute_workflow(self, user_prompt):
        '''
        Execute complete 4-phase workflow
        
        Args:
            user_prompt (str): User's sponsor search request
            
        Returns:
            dict: Complete workflow results
        '''
        
        print('?? Healing NY Sponsor Finder - Orchestration Started')
        print(f'?? Request: {user_prompt}')
        print(f'?? Mission: {self.mission_context}')
        print('=' * 60)
        
        # Phase 1: Keyword Extraction
        print('\n?? PHASE 1: Keyword Extraction')
        print(f'   Agent: @keyword-extractor')
        print(f'   Input: User prompt + mission context')
        print(f'   Expected: JSON with primary/secondary/location/sector keywords')
        
        # Phase 2: Web Research
        print('\n?? PHASE 2: Web Research')
        print(f'   Agent: @web-researcher')
        print(f'   Input: Keywords from Phase 1')
        print(f'   Expected: 15-25 sponsor prospects with relevance scores')
        
        # Phase 3: Categorization
        print('\n?? PHASE 3: Categorization')
        print(f'   Agent: @categorizer')
        print(f'   Input: Raw sponsor list from Phase 2')
        print(f'   Expected: Sponsors organized by type (corps/foundations/ngos)')
        
        # Phase 4: Validation
        print('\n? PHASE 4: Validation')
        print(f'   Agent: @validator')
        print(f'   Input: Categorized sponsors from Phase 3')
        print(f'   Expected: Validated list (score =5) with quality report')
        
        print('\n' + '=' * 60)
        print('?? Orchestration Blueprint Complete')
        print('\nTo execute in Claude Code:')
        print('  "Execute this orchestration for: {user_prompt}"')
        
        return {
            'status': 'blueprint_ready',
            'phases': 4,
            'workflow': self.workflow_phases
        }

# Demo
if __name__ == '__main__':
    orchestrator = SponsorOrchestrator()
    result = orchestrator.execute_workflow(
        'Find mental health sponsors in NYC with $50k+ grants'
    )
    print(f'\nResult: {result}')
