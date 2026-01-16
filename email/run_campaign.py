"""
Email Campaign CLI Tool

Command-line interface for running email campaigns to sponsors.

Usage:
    python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md
    python email/run_campaign.py --action preview --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md
    python email/run_campaign.py --action report --output docs/engagement_report.md
    python email/run_campaign.py --action followup --days 7
"""

import sys
import os
import argparse
import logging

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'salesforce'))
sys.path.insert(0, os.path.dirname(__file__))

from campaign_orchestrator import EmailCampaignOrchestrator
from sponsor_parser import parse_markdown_report, parse_json_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def load_sponsors_from_file(file_path):
    """Load sponsor data from JSON or markdown file"""
    from pathlib import Path

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix == '.json':
        return parse_json_file(file_path)
    elif path.suffix == '.md':
        return parse_markdown_report(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .md")


def action_send(args):
    """Send email campaign to sponsors"""
    logger.info("ACTION: Send Email Campaign\n")

    # Load sponsors
    logger.info(f"Loading sponsors from: {args.input}")
    sponsors = load_sponsors_from_file(args.input)
    logger.info(f"[OK] Loaded {len(sponsors)} sponsors\n")

    if not sponsors:
        logger.error("[ERROR] No sponsors found in file")
        return 1

    # Initialize orchestrator
    logger.info("Initializing campaign orchestrator...")
    orchestrator = EmailCampaignOrchestrator()

    # Run campaign
    campaign_name = args.campaign or 'Sponsor Outreach Campaign'
    results = orchestrator.run_campaign(sponsors, campaign_name=campaign_name)

    # Return status
    if results['failed'] > 0:
        logger.warning(f"\n[WARNING] {results['failed']} emails failed to send")
        return 1
    else:
        logger.info(f"\n[SUCCESS] All {results['sent']} emails sent successfully!")
        return 0


def action_preview(args):
    """Preview emails without sending"""
    logger.info("ACTION: Preview Email Campaign\n")

    # Load sponsors
    logger.info(f"Loading sponsors from: {args.input}")
    sponsors = load_sponsors_from_file(args.input)
    logger.info(f"[OK] Loaded {len(sponsors)} sponsors\n")

    if not sponsors:
        logger.error("[ERROR] No sponsors found in file")
        return 1

    # Initialize orchestrator
    orchestrator = EmailCampaignOrchestrator()

    # Preview campaign
    previews = orchestrator.preview_campaign(sponsors)

    logger.info(f"\n[OK] Preview complete: {len(previews)} emails would be sent")
    return 0


def action_report(args):
    """Generate engagement report"""
    logger.info("ACTION: Generate Engagement Report\n")

    # Initialize orchestrator
    logger.info("Initializing campaign orchestrator...")
    orchestrator = EmailCampaignOrchestrator()

    # Generate report
    days = args.days or 30
    output_path = args.output or 'docs/engagement_report.md'

    report_path = orchestrator.generate_campaign_report(
        days_back=days,
        output_path=output_path
    )

    logger.info(f"\n[SUCCESS] Report generated: {report_path}")
    return 0


def action_followup(args):
    """Send follow-up campaign to non-responders"""
    logger.info("ACTION: Follow-Up Campaign\n")

    # Initialize orchestrator
    logger.info("Initializing campaign orchestrator...")
    orchestrator = EmailCampaignOrchestrator()

    # Run follow-up campaign
    days = args.days or 7
    results = orchestrator.follow_up_campaign(days_since_first=days)

    # Return status
    if results['failed'] > 0:
        logger.warning(f"\n[WARNING] {results['failed']} follow-up emails failed")
        return 1
    elif results['sent'] == 0:
        logger.info("\n[INFO] No follow-ups needed")
        return 0
    else:
        logger.info(f"\n[SUCCESS] {results['sent']} follow-up emails sent!")
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Run email campaigns to sponsors via Salesforce API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview emails before sending
  python email/run_campaign.py --action preview --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md

  # Send campaign to all sponsors
  python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md

  # Send campaign with custom name
  python email/run_campaign.py --action send --input sponsors.json --campaign "Spring 2026 Outreach"

  # Generate engagement report (last 30 days)
  python email/run_campaign.py --action report

  # Generate report for specific time period
  python email/run_campaign.py --action report --days 60 --output docs/q1_engagement.md

  # Send follow-up to non-responders (last 7 days)
  python email/run_campaign.py --action followup --days 7
        """
    )

    parser.add_argument(
        '--action',
        required=True,
        choices=['send', 'preview', 'report', 'followup'],
        help='Action to perform'
    )

    parser.add_argument(
        '--input',
        help='Path to sponsor data file (markdown or JSON)',
        metavar='FILE'
    )

    parser.add_argument(
        '--output',
        help='Path to output file (for report action)',
        metavar='FILE'
    )

    parser.add_argument(
        '--days',
        type=int,
        help='Number of days (for report or followup action)',
        metavar='N'
    )

    parser.add_argument(
        '--campaign',
        help='Campaign name (for send action)',
        metavar='NAME'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.action in ['send', 'preview'] and not args.input:
        parser.error(f"--input is required for action '{args.action}'")

    # Execute action
    try:
        if args.action == 'send':
            return action_send(args)
        elif args.action == 'preview':
            return action_preview(args)
        elif args.action == 'report':
            return action_report(args)
        elif args.action == 'followup':
            return action_followup(args)
        else:
            parser.error(f"Unknown action: {args.action}")

    except FileNotFoundError as e:
        logger.error(f"\n[ERROR] {e}")
        return 1
    except ValueError as e:
        logger.error(f"\n[ERROR] {e}")
        return 1
    except Exception as e:
        logger.error(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
