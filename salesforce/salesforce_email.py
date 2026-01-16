"""
Salesforce Email Sender

Extends SalesforceClient with email sending capability via Salesforce API.
Uses SingleEmailMessage approach for individual email sending.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional
from salesforce_client import SalesforceClient

logger = logging.getLogger(__name__)


class SalesforceEmailSender(SalesforceClient):
    """
    Extends SalesforceClient with email sending capability

    Uses Salesforce REST API endpoint:
    POST /services/data/v59.0/actions/standard/emailSimple
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

        logger.info(f"Email sender initialized (From: {self.email_from_name} <{self.email_from_address}>)")

    def send_email_to_lead(self, lead_id: str, subject: str, body: str,
                           reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email to a Lead using Salesforce Email API

        Args:
            lead_id: Salesforce Lead ID
            subject: Email subject line
            body: Email body (HTML or plain text)
            reply_to: Reply-to email address (optional, uses default if not provided)

        Returns:
            {
                'success': bool,
                'message_id': str or None,
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
                    'message_id': None,
                    'errors': ['Lead has no email address']
                }
        except Exception as e:
            logger.error(f"  [ERROR] Failed to retrieve Lead {lead_id}: {str(e)[:100]}")
            return {
                'success': False,
                'message_id': None,
                'errors': [f'Failed to retrieve Lead: {str(e)[:100]}']
            }

        # Use provided reply_to or default
        reply_to_address = reply_to or self.email_reply_to

        # Prepare email payload
        # Note: Salesforce emailSimple action sends plain text emails
        # For HTML emails, would need to use different API endpoint
        payload = {
            "inputs": [{
                "emailAddresses": email_address,
                "emailSubject": subject,
                "emailBody": body,
                "senderType": "CurrentUser",
                "saveAsActivity": True
            }]
        }

        try:
            # Send via Salesforce REST API
            # Using the base_url from simple_salesforce session
            endpoint = f"{self.sf.base_url}actions/standard/emailSimple"
            response = self.sf.restful(endpoint, method='POST', json=payload)

            # Track API call for rate limiting
            self.call_timestamps.append(time.time())

            # Parse response
            if response and len(response) > 0:
                result = response[0]
                if result.get('isSuccess', False):
                    logger.info(f"  [+] Email sent to {company_name} ({email_address})")
                    return {
                        'success': True,
                        'message_id': result.get('outputValues', {}).get('id'),
                        'errors': []
                    }
                else:
                    errors = result.get('errors', [])
                    error_msgs = [err.get('message', str(err)) for err in errors]
                    logger.error(f"  [-] Failed to send email to {company_name}: {error_msgs[0] if error_msgs else 'Unknown error'}")
                    return {
                        'success': False,
                        'message_id': None,
                        'errors': error_msgs
                    }
            else:
                logger.error(f"  [-] No response from Salesforce for {company_name}")
                return {
                    'success': False,
                    'message_id': None,
                    'errors': ['No response from Salesforce API']
                }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"  [-] Email send failed for {company_name}: {error_msg[:100]}")

            # Check for session timeout
            if "expired session" in error_msg.lower() or "invalid_grant" in error_msg.lower():
                logger.warning("  [WARNING] Session timeout detected - reconnection required")

            return {
                'success': False,
                'message_id': None,
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
                'results': list  # Individual send results
            }
        """
        results = {
            'sent': 0,
            'failed': 0,
            'total': len(email_list),
            'results': []
        }

        logger.info(f"\n[*] Sending {len(email_list)} emails...")

        for i, email in enumerate(email_list, 1):
            lead_id = email.get('lead_id')
            subject = email.get('subject')
            body = email.get('body')
            reply_to = email.get('reply_to')

            logger.info(f"\n[{i}/{len(email_list)}] Sending to Lead ID: {lead_id}")

            # Send email
            send_result = self.send_email_to_lead(lead_id, subject, body, reply_to)

            # Track result
            result_entry = {
                'lead_id': lead_id,
                'subject': subject,
                'success': send_result['success'],
                'message_id': send_result.get('message_id'),
                'errors': send_result.get('errors', [])
            }
            results['results'].append(result_entry)

            if send_result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1

        logger.info(f"\n[*] Bulk send complete: {results['sent']} sent, {results['failed']} failed")

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

    def get_lead_email_by_company(self, company_name: str) -> Optional[str]:
        """
        Look up Lead email address by company name

        Args:
            company_name: Company name to search for

        Returns:
            Email address if found, None otherwise
        """
        try:
            safe_name = company_name.replace("'", "\\'")
            query = f"SELECT Id, Email, Company FROM Lead WHERE Company = '{safe_name}' LIMIT 1"
            result = self.sf.query(query)

            if result['totalSize'] > 0:
                email = result['records'][0].get('Email')
                if email:
                    logger.debug(f"Found email {email} for company: {company_name}")
                    return email
                else:
                    logger.warning(f"Lead found but no email for company: {company_name}")
                    return None
            else:
                logger.warning(f"No Lead found for company: {company_name}")
                return None

        except Exception as e:
            logger.error(f"Email lookup failed for {company_name}: {str(e)[:100]}")
            return None

    def _wait_for_rate_limit(self):
        """
        Implement rate limiting to respect Salesforce API limits

        Salesforce allows 15 API calls per 20 seconds per user.
        This method waits if we're approaching the limit.
        """
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
__all__ = ['SalesforceEmailSender']
