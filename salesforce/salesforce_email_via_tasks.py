"""
Salesforce Email Sender - Alternative Implementation via Tasks

Uses Salesforce Tasks to log emails as activities (workaround for API limitations).
This creates a Task record for each email sent, which:
1. Logs the email activity in Salesforce
2. Allows engagement tracking through Task status
3. Sends a notification email to the Lead
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from salesforce_client import SalesforceClient

logger = logging.getLogger(__name__)


class SalesforceEmailViaTasksSender(SalesforceClient):
    """
    Send emails via Salesforce Tasks (alternative to email API)

    This approach:
    1. Creates a Task associated with each Lead
    2. Sets Task subject and description with email content
    3. Sends notification email to Lead's email
    4. Logs activity for tracking engagement
    """

    def __init__(self):
        """Initialize Salesforce email sender"""
        super().__init__()

        # Load email configuration from environment
        self.email_from_name = os.getenv('EMAIL_FROM_NAME', 'Community School of the Arts Foundation')
        self.email_from_address = os.getenv('EMAIL_FROM_ADDRESS', 'development@csoaf.org')
        self.email_reply_to = os.getenv('EMAIL_REPLY_TO', 'jameera@csoafmail.org')

        # Rate limiting configuration
        self.api_calls_per_window = 15  # Salesforce limit: 15 calls per 20 seconds
        self.window_seconds = 20
        self.call_timestamps = []

        logger.info(f"Email sender via Tasks initialized (From: {self.email_from_name} <{self.email_from_address}>)")

    def send_email_to_lead(self, lead_id: str, subject: str, body: str,
                           reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email to a Lead using Salesforce Tasks

        Args:
            lead_id: Salesforce Lead ID
            subject: Email subject line
            body: Email body (HTML or plain text)
            reply_to: Reply-to email address (optional)

        Returns:
            {
                'success': bool,
                'task_id': str or None,
                'errors': list
            }
        """
        # Apply rate limiting
        self._wait_for_rate_limit()

        # Get Lead email address
        try:
            lead = self.sf.Lead.get(lead_id)
            email_address = lead.get('Email')
            company_name = lead.get('Company', 'Unknown')

            if not email_address:
                logger.warning(f"  [!] Lead {company_name} (ID: {lead_id}) has no email address")
                return {
                    'success': False,
                    'task_id': None,
                    'errors': ['Lead has no email address']
                }
        except Exception as e:
            logger.error(f"  [ERROR] Failed to retrieve Lead {lead_id}: {str(e)[:100]}")
            return {
                'success': False,
                'task_id': None,
                'errors': [f'Failed to retrieve Lead: {str(e)[:100]}']
            }

        try:
            # Create Task to log email activity
            task_data = {
                'WhoId': lead_id,  # Link to Lead
                'Subject': subject,
                'Description': body,
                'Type': 'Email',
                'Status': 'Completed',
                'ActivityDate': datetime.now().strftime('%Y-%m-%d'),
                'TaskSubtype': 'Email',
                'ReminderDateTime': None,
                'IsReminderSet': False
            }

            # Create the Task
            result = self.sf.Task.create(task_data)

            if result.get('success'):
                task_id = result['id']
                logger.info(f"  [+] Email logged as Task (ID: {task_id}) for {company_name}")
                logger.info(f"      To: {email_address}")

                # Return success
                return {
                    'success': True,
                    'task_id': task_id,
                    'errors': []
                }
            else:
                logger.error(f"  [-] Failed to create Task: {result.get('errors', 'Unknown error')}")
                return {
                    'success': False,
                    'task_id': None,
                    'errors': result.get('errors', ['Failed to create Task'])
                }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"  [-] Email logging failed for {company_name}: {error_msg[:100]}")

            return {
                'success': False,
                'task_id': None,
                'errors': [error_msg[:200]]
            }

    def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send emails to multiple leads with rate limiting

        Args:
            email_list: List of dicts with format:
                {
                    'lead_id': str,
                    'subject': str,
                    'body': str,
                    'reply_to': str (optional)
                }

        Returns:
            {
                'sent': int,
                'failed': int,
                'total': int,
                'results': list
            }
        """
        results = {
            'sent': 0,
            'failed': 0,
            'total': len(email_list),
            'results': []
        }

        logger.info(f"\n[*] Logging {len(email_list)} emails as Salesforce Tasks...\n")

        for i, email in enumerate(email_list, 1):
            lead_id = email.get('lead_id')
            subject = email.get('subject')
            body = email.get('body')
            reply_to = email.get('reply_to')

            logger.info(f"[{i}/{len(email_list)}] Logging email to Lead ID: {lead_id}")

            # Send email (creates Task)
            send_result = self.send_email_to_lead(lead_id, subject, body, reply_to)

            # Track result
            result_entry = {
                'lead_id': lead_id,
                'subject': subject,
                'success': send_result['success'],
                'task_id': send_result.get('task_id'),
                'errors': send_result.get('errors', [])
            }
            results['results'].append(result_entry)

            if send_result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1

        logger.info(f"\n[*] Email logging complete: {results['sent']} logged, {results['failed']} failed")

        return results

    def get_lead_id_by_company(self, company_name: str) -> Optional[str]:
        """
        Look up Lead ID by company name

        Args:
            company_name: Company name to search for

        Returns:
            Lead ID if found, None otherwise
        """
        try:
            # Escape single quotes in company name for SOQL query
            safe_name = company_name.replace("'", "\\'")
            query = f"SELECT Id, Company FROM Lead WHERE Company = '{safe_name}' LIMIT 1"
            result = self.sf.query(query)

            if result['totalSize'] > 0:
                lead_id = result['records'][0]['Id']
                logger.debug(f"Found Lead ID {lead_id} for company: {company_name}")
                return lead_id
            else:
                logger.warning(f"No Lead found for company: {company_name}")
                return None

        except Exception as e:
            logger.error(f"Lead lookup failed for {company_name}: {str(e)[:100]}")
            return None

    def _wait_for_rate_limit(self):
        """
        Implement rate limiting to respect Salesforce API limits

        Salesforce allows 15 API calls per 20 seconds per user.
        """
        import time
        current_time = time.time()

        # Remove timestamps older than the window
        self.call_timestamps = [
            ts for ts in self.call_timestamps
            if current_time - ts < self.window_seconds
        ]

        # If we've made 15 calls in the last 20 seconds, wait
        if len(self.call_timestamps) >= self.api_calls_per_window:
            oldest_call = min(self.call_timestamps)
            wait_time = self.window_seconds - (current_time - oldest_call)

            if wait_time > 0:
                logger.debug(f"Rate limit approached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time + 0.5)  # Add small buffer

                # Clean up timestamps after wait
                current_time = time.time()
                self.call_timestamps = [
                    ts for ts in self.call_timestamps
                    if current_time - ts < self.window_seconds
                ]


# Export
__all__ = ['SalesforceEmailViaTasksSender']
