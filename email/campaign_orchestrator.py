"""
Email Campaign Orchestrator

Coordinates the complete email campaign workflow:
1. Generate personalized emails for sponsors
2. Look up Lead IDs in Salesforce
3. Send emails via Salesforce API
4. Track engagement and generate reports
"""

import sys
import os
import logging
from typing import Dict, List, Any, Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'salesforce'))
sys.path.insert(0, os.path.dirname(__file__))

from salesforce_email import SalesforceEmailSender
from engagement_tracker import EngagementTracker
from email_templates import generate_sponsor_email

logger = logging.getLogger(__name__)


class EmailCampaignOrchestrator:
    """Orchestrate complete email campaign workflow"""

    def __init__(self):
        """Initialize campaign orchestrator with Salesforce integration"""
        try:
            # Initialize email sender (extends SalesforceClient)
            self.email_sender = SalesforceEmailSender()

            # Initialize engagement tracker
            self.engagement_tracker = EngagementTracker(self.email_sender)

            logger.info("[OK] Campaign orchestrator initialized")

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize orchestrator: {str(e)}")
            raise

    def run_campaign(self, sponsor_list: List[Dict[str, Any]],
                     campaign_name: str = 'Sponsor Outreach') -> Dict[str, Any]:
        """
        Execute complete email campaign

        Workflow:
        1. Generate personalized email for each sponsor
        2. Look up Lead ID in Salesforce by company name
        3. Send email via Salesforce API
        4. Log send results
        5. Return summary

        Args:
            sponsor_list: List of sponsor dicts from parser
            campaign_name: Campaign identifier

        Returns:
            {
                'campaign_name': str,
                'sent': int,
                'failed': int,
                'not_found': int,  # Sponsors not found in Salesforce
                'results': list
            }
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"CAMPAIGN: {campaign_name}")
        logger.info(f"{'='*70}")
        logger.info(f"Preparing to send emails to {len(sponsor_list)} sponsors\n")

        results = {
            'campaign_name': campaign_name,
            'sent': 0,
            'failed': 0,
            'not_found': 0,
            'total': len(sponsor_list),
            'results': []
        }

        # Process each sponsor
        for i, sponsor in enumerate(sponsor_list, 1):
            sponsor_name = sponsor.get('name', 'Unknown')
            logger.info(f"\n[{i}/{len(sponsor_list)}] Processing: {sponsor_name}")

            try:
                # Step 1: Generate personalized email
                logger.info("  [1/3] Generating personalized email...")
                email_data = generate_sponsor_email(sponsor)
                subject = email_data['subject']
                body = email_data['body']
                logger.info(f"  [OK] Email generated (Template: {email_data['template_type']})")

                # Step 2: Look up Lead ID in Salesforce
                logger.info("  [2/3] Looking up Lead ID in Salesforce...")
                lead_id = self.email_sender.get_lead_id_by_company(sponsor_name)

                if not lead_id:
                    logger.warning(f"  [!] Lead not found in Salesforce for: {sponsor_name}")
                    results['not_found'] += 1
                    results['results'].append({
                        'sponsor_name': sponsor_name,
                        'success': False,
                        'error': 'Lead not found in Salesforce',
                        'lead_id': None,
                        'subject': subject
                    })
                    continue

                logger.info(f"  [OK] Lead ID: {lead_id}")

                # Step 3: Send email via Salesforce API
                logger.info("  [3/3] Sending email via Salesforce API...")
                send_result = self.email_sender.send_email_to_lead(
                    lead_id=lead_id,
                    subject=subject,
                    body=body
                )

                # Track result
                if send_result['success']:
                    results['sent'] += 1
                    logger.info(f"  [+] Email sent successfully")
                else:
                    results['failed'] += 1
                    error_msg = send_result['errors'][0] if send_result['errors'] else 'Unknown error'
                    logger.error(f"  [-] Email send failed: {error_msg}")

                results['results'].append({
                    'sponsor_name': sponsor_name,
                    'success': send_result['success'],
                    'lead_id': lead_id,
                    'subject': subject,
                    'message_id': send_result.get('message_id'),
                    'errors': send_result.get('errors', [])
                })

            except Exception as e:
                logger.error(f"  [ERROR] Failed to process {sponsor_name}: {str(e)[:100]}")
                results['failed'] += 1
                results['results'].append({
                    'sponsor_name': sponsor_name,
                    'success': False,
                    'error': str(e)[:200],
                    'lead_id': None,
                    'subject': None
                })

        # Print summary
        self._print_campaign_summary(results)

        return results

    def preview_campaign(self, sponsor_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preview emails without sending

        Args:
            sponsor_list: List of sponsor dicts from parser

        Returns:
            List of preview dicts with sponsor name, subject, body snippet
        """
        logger.info(f"\n{'='*70}")
        logger.info("CAMPAIGN PREVIEW")
        logger.info(f"{'='*70}")
        logger.info(f"Generating email previews for {len(sponsor_list)} sponsors\n")

        previews = []

        for i, sponsor in enumerate(sponsor_list, 1):
            sponsor_name = sponsor.get('name', 'Unknown')

            try:
                # Generate email
                email_data = generate_sponsor_email(sponsor)

                # Create preview
                preview = {
                    'number': i,
                    'sponsor_name': sponsor_name,
                    'template_type': email_data['template_type'],
                    'subject': email_data['subject'],
                    'body_snippet': email_data['body'][:300] + '...',
                    'tokens': email_data['tokens']
                }

                previews.append(preview)

                # Print preview
                logger.info(f"\n[{i}] {sponsor_name}")
                logger.info(f"    Template: {email_data['template_type'].upper()}")
                logger.info(f"    Subject: {email_data['subject']}")
                logger.info(f"    Body Preview: {preview['body_snippet']}\n")

            except Exception as e:
                logger.error(f"[{i}] Failed to preview {sponsor_name}: {str(e)[:100]}")
                previews.append({
                    'number': i,
                    'sponsor_name': sponsor_name,
                    'error': str(e)[:200]
                })

        logger.info(f"\n{'='*70}")
        logger.info(f"Preview complete: {len(previews)} emails generated")
        logger.info(f"{'='*70}\n")

        return previews

    def follow_up_campaign(self, days_since_first: int = 7) -> Dict[str, Any]:
        """
        Send follow-up to non-responders

        Workflow:
        1. Get engagement data
        2. Identify cold leads (score < 40)
        3. Generate follow-up emails
        4. Send follow-ups

        Args:
            days_since_first: Days since first email was sent

        Returns:
            Campaign results dict
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"FOLLOW-UP CAMPAIGN (Non-responders from last {days_since_first} days)")
        logger.info(f"{'='*70}\n")

        # Get engagement analysis
        logger.info("Analyzing engagement data...")
        analysis = self.engagement_tracker.analyze_campaign_performance(days_back=days_since_first)

        cold_leads = analysis['cold_leads']
        logger.info(f"[OK] Found {len(cold_leads)} cold leads (score < 40)\n")

        if not cold_leads:
            logger.info("No cold leads to follow up with. Campaign complete.")
            return {
                'campaign_name': 'Follow-Up Campaign',
                'sent': 0,
                'failed': 0,
                'total': 0,
                'results': []
            }

        # Generate follow-up emails
        # Note: This uses a simplified follow-up message
        # In production, you might want separate follow-up templates
        email_list = []

        for lead in cold_leads:
            lead_id = lead['lead_id']
            company_name = lead['company_name']

            # Generate follow-up email
            subject = f"Following up: Partnership Opportunity with CSOAF"
            body = f"""Dear Team at {company_name},

I wanted to follow up on my previous email regarding a partnership opportunity between your organization and the Community School of the Arts Foundation (CSOAF).

We understand you receive many partnership requests. However, we believe there's a strong alignment between our missions, and we'd welcome the opportunity to discuss how we might work together.

If now isn't the right time, I'd be grateful for guidance on:
- The best time to reconnect
- The appropriate contact person for partnership discussions
- Any upcoming grant cycles or application deadlines

Thank you for considering this opportunity.

Warm regards,

Jamee Ra
Development Director
Community School of the Arts Foundation
Phone: (555) 555-5555
Email: jameera@csoafmail.org
Website: www.csoaf.org
"""

            email_list.append({
                'lead_id': lead_id,
                'subject': subject,
                'body': body
            })

        # Send follow-up emails
        logger.info(f"Sending {len(email_list)} follow-up emails...\n")
        results = self.email_sender.send_bulk_emails(email_list)

        # Update results with campaign name
        results['campaign_name'] = 'Follow-Up Campaign'

        # Print summary
        self._print_campaign_summary(results)

        return results

    def generate_campaign_report(self, days_back: int = 30,
                                 output_path: Optional[str] = None) -> str:
        """
        Pull engagement data and generate report

        Workflow:
        1. Query Salesforce for email activities
        2. Calculate engagement scores
        3. Classify leads (hot/warm/cold)
        4. Generate markdown report
        5. Export hot leads JSON

        Args:
            days_back: Number of days to analyze
            output_path: Path to save report (default: from env)

        Returns:
            Path to generated report
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"GENERATING ENGAGEMENT REPORT")
        logger.info(f"{'='*70}\n")

        # Generate engagement report
        report_path = self.engagement_tracker.generate_engagement_report(
            output_path=output_path,
            days_back=days_back
        )

        # Export hot leads
        hot_leads_path = self.engagement_tracker.export_hot_leads_json(days_back=days_back)

        logger.info(f"\n[OK] Report generated: {report_path}")
        logger.info(f"[OK] Hot leads exported: {hot_leads_path}\n")

        return report_path

    def _print_campaign_summary(self, results: Dict[str, Any]):
        """Print formatted campaign summary"""
        logger.info(f"\n{'='*70}")
        logger.info("CAMPAIGN SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Campaign: {results['campaign_name']}")
        logger.info(f"Total Sponsors: {results['total']}")
        logger.info(f"[+] Emails Sent: {results['sent']}")
        logger.info(f"[-] Failed: {results['failed']}")
        if 'not_found' in results and results['not_found'] > 0:
            logger.info(f"[!] Not Found in Salesforce: {results['not_found']}")

        success_rate = (results['sent'] / results['total'] * 100) if results['total'] > 0 else 0
        logger.info(f"\nSuccess Rate: {success_rate:.1f}%")
        logger.info(f"{'='*70}\n")


# Export
__all__ = ['EmailCampaignOrchestrator']
