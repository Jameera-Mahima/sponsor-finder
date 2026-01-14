"""
Example Usage: Campaign Logging Integration
Shows how to use the logging system with agent executions
"""

from datetime import datetime
from logger import CampaignLogger


def run_logged_campaign():
    """
    Example of running a campaign with full logging

    This demonstrates the pattern to use when integrating
    with the actual run-campaign skill
    """

    # 1. Initialize campaign logger
    logger = CampaignLogger(
        campaign_name="Christmas Education Campaign 2024",
        parameters={
            'description': 'Find sponsors for $500k education campaign in NYC',
            'goal_amount': 500000,
            'target_sponsors': 500,
            'location': 'New York City',
            'campaign_type': 'direct_fundraising'
        }
    )

    # 2. Execute Phase 1: Research & Discovery
    logger.start_phase(1, "Research & Discovery")

    # Execute keyword-extractor agent
    print("  → Running keyword-extractor agent...")
    start_time = datetime.utcnow().isoformat()

    # ACTUAL AGENT EXECUTION WOULD HAPPEN HERE
    # In real usage: result = Task(subagent_type="keyword-extractor", ...)
    # For now, simulate output:
    agent_output = """
    Analyzing user prompt and CSOAF mission statement...

    LOG_START: agent=keyword-extractor, campaign_id={campaign_id}, phase=Phase 1
    LOG_STEP: step=1, action=analyze_prompt, details="Extracted primary keywords: education, disabilities, arts, NYC, $50k+"
    LOG_STEP: step=2, action=incorporate_mission, details="Added secondary keywords from CSOAF focus areas: arts education, special education, accessibility, community healing"
    LOG_STEP: step=3, action=generate_output, details="Created keywords JSON with 15 terms (5 primary, 10 secondary)"
    LOG_COMPLETE: duration=13s, tokens_input=850, tokens_output=320, output_file=keywords_used.json

    Keywords extracted successfully.
    """

    end_time = datetime.utcnow().isoformat()

    # Log the agent execution
    logger.log_agent_execution(
        agent_name='keyword-extractor',
        phase='Phase 1: Research & Discovery',
        output_text=agent_output,
        start_time=start_time,
        end_time=end_time
    )

    # Execute web-researcher agent
    print("  → Running web-researcher agent...")
    start_time = datetime.utcnow().isoformat()

    agent_output = """
    Searching for sponsors matching keywords...

    LOG_START: agent=web-researcher, campaign_id={campaign_id}, phase=Phase 1
    LOG_STEP: step=1, action=search_web, details="Executed 8 searches with keywords: education, disabilities, arts, NYC"
    LOG_STEP: step=2, action=fetch_details, details="Retrieved details for 25 prospects"
    LOG_STEP: step=3, action=validate_contacts, details="Verified contact info for 23 sponsors"
    LOG_COMPLETE: duration=85s, tokens_input=5200, tokens_output=8500, output_file=sponsor_research_report.md, sponsors_found=23

    Found 23 potential sponsors.
    """

    end_time = datetime.utcnow().isoformat()

    logger.log_agent_execution(
        agent_name='web-researcher',
        phase='Phase 1: Research & Discovery',
        output_text=agent_output,
        start_time=start_time,
        end_time=end_time
    )

    # Execute validator agent
    print("  → Running validator agent...")
    start_time = datetime.utcnow().isoformat()

    agent_output = """
    Validating sponsor quality...

    LOG_START: agent=validator, campaign_id={campaign_id}, phase=Phase 1
    LOG_STEP: step=1, action=verify_existence, details="Verified 23 sponsors exist online"
    LOG_STEP: step=2, action=validate_giving, details="Confirmed 20 sponsors have active programs"
    LOG_STEP: step=3, action=quality_scoring, details="Assigned quality scores (avg: 7.8/10), removed 5 low-quality"
    LOG_WARNING: severity=low, message="Missing phone number for Foundation XYZ"
    LOG_COMPLETE: duration=45s, tokens_input=8500, tokens_output=3200, output_file=validation_log.md, sponsors_validated=18

    Validated 18 high-quality sponsors.
    """

    end_time = datetime.utcnow().isoformat()

    logger.log_agent_execution(
        agent_name='validator',
        phase='Phase 1: Research & Discovery',
        output_text=agent_output,
        start_time=start_time,
        end_time=end_time
    )

    # End Phase 1
    logger.end_phase(1, outputs=[
        'keywords_used.json',
        'sponsor_research_report.md',
        'validation_log.md'
    ])

    # 3. Execute Phase 2: Categorization & Ranking
    logger.start_phase(2, "Categorization & Ranking")

    # Execute categorizer agent
    print("  → Running categorizer agent...")
    start_time = datetime.utcnow().isoformat()

    agent_output = """
    Categorizing sponsors...

    LOG_START: agent=categorizer, campaign_id={campaign_id}, phase=Phase 2
    LOG_STEP: step=1, action=analyze_types, details="Categorized 18 sponsors into 4 types"
    LOG_STEP: step=2, action=assign_scores, details="Assigned relevance scores (avg: 8.2/10)"
    LOG_STEP: step=3, action=resolve_duplicates, details="Resolved 2 duplicate entries"
    LOG_COMPLETE: duration=25s, tokens_input=3500, tokens_output=2100, output_file=sponsors_by_category.json, categories=4

    Organized into: 8 Foundations, 6 Corporations, 3 NGOs, 1 Government.
    """

    end_time = datetime.utcnow().isoformat()

    logger.log_agent_execution(
        agent_name='categorizer',
        phase='Phase 2: Categorization & Ranking',
        output_text=agent_output,
        start_time=start_time,
        end_time=end_time
    )

    # End Phase 2
    logger.end_phase(2, outputs=[
        'sponsors_by_category.json',
        'salesforce_import.csv'
    ])

    # 4. Finalize campaign logging
    logger.finalize()

    print(f"\n✅ Campaign logged successfully!")
    print(f"   View logs: logs/campaigns/{logger.campaign_id}/")
    print(f"   Dashboard: logs/dashboard/index.html")


def simulate_agent_with_error():
    """Example showing error handling"""

    logger = CampaignLogger(
        campaign_name="Test Campaign with Errors",
        parameters={'test': True}
    )

    logger.start_phase(1, "Test Phase")

    # Simulate agent with error
    agent_output = """
    LOG_START: agent=web-researcher, campaign_id=test, phase=Phase 1
    LOG_STEP: step=1, action=search_web, details="Started web search"
    LOG_ERROR: severity=critical, message="Web search API timeout after 30s", recovery="Retry succeeded on attempt 2"
    LOG_STEP: step=2, action=search_web, details="Retry succeeded, found 10 results"
    LOG_WARNING: severity=low, message="API timeout for search query X, retry succeeded"
    LOG_COMPLETE: duration=65s, tokens_input=2000, tokens_output=5000, output_file=results.md, sponsors_found=10
    """

    logger.log_agent_execution(
        agent_name='web-researcher',
        phase='Phase 1',
        output_text=agent_output,
        start_time=datetime.utcnow().isoformat(),
        end_time=datetime.utcnow().isoformat()
    )

    logger.end_phase(1, outputs=['results.md'])
    logger.finalize()

    print(f"\n✅ Error handling example complete")
    print(f"   Check error_log.json in campaign directory")


def quick_usage_guide():
    """Print quick usage guide"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  CAMPAIGN LOGGING - QUICK USAGE GUIDE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

1. INITIALIZE LOGGER
   ─────────────────
   from logger import CampaignLogger

   logger = CampaignLogger(
       campaign_name="My Campaign",
       parameters={'goal': 100000, 'location': 'NYC'}
   )

2. START PHASE
   ─────────────
   logger.start_phase(1, "Research & Discovery")

3. LOG AGENT EXECUTION
   ───────────────────────
   start_time = datetime.utcnow().isoformat()

   # Execute agent (Task tool or other method)
   agent_output = execute_agent(...)

   end_time = datetime.utcnow().isoformat()

   logger.log_agent_execution(
       agent_name='keyword-extractor',
       phase='Phase 1: Research',
       output_text=agent_output,
       start_time=start_time,
       end_time=end_time
   )

4. END PHASE
   ──────────
   logger.end_phase(1, outputs=['keywords.json', 'report.md'])

5. FINALIZE CAMPAIGN
   ──────────────────
   logger.finalize()

REQUIREMENTS:
- Agents must include LOG_* statements in their output
- All timestamps should be ISO format (datetime.utcnow().isoformat())
- Provide output file lists when ending phases

VIEW LOGS:
- Campaign logs: logs/campaigns/<campaign_id>/
- Dashboard: logs/dashboard/index.html (open in browser)
- Agent history: logs/agents/<agent_name>/runs/

════════════════════════════════════════════════════════════════════════════
    """)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--guide':
        quick_usage_guide()
    elif len(sys.argv) > 1 and sys.argv[1] == '--error':
        simulate_agent_with_error()
    else:
        print("Running example logged campaign...\n")
        run_logged_campaign()
