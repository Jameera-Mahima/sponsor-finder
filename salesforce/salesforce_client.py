"""
Salesforce API Client
Handles authentication and data upload to Salesforce CRM
"""

import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Salesforce Configuration
SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN')
SALESFORCE_DOMAIN = os.getenv('SALESFORCE_DOMAIN', 'login')
SALESFORCE_OBJECT_TYPE = os.getenv('SALESFORCE_OBJECT_TYPE', 'Lead')
SALESFORCE_LEAD_SOURCE = os.getenv('SALESFORCE_LEAD_SOURCE', 'AI Sponsor Search')


class SalesforceClient:
    """Salesforce API client for sponsor data upload"""

    def __init__(self):
        """Initialize Salesforce connection"""
        if not all([SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_SECURITY_TOKEN]):
            raise ValueError(
                "Missing Salesforce credentials. Set SALESFORCE_USERNAME, "
                "SALESFORCE_PASSWORD, and SALESFORCE_SECURITY_TOKEN in .env"
            )

        try:
            self.sf = Salesforce(
                username=SALESFORCE_USERNAME,
                password=SALESFORCE_PASSWORD,
                security_token=SALESFORCE_SECURITY_TOKEN,
                domain=SALESFORCE_DOMAIN
            )
            logger.info(f"✓ Connected to Salesforce ({SALESFORCE_DOMAIN}.salesforce.com)")
        except Exception as e:
            logger.error(f"✗ Salesforce connection failed: {e}")
            raise

    def upload_sponsor_as_lead(self, sponsor_data):
        """
        Upload sponsor to Salesforce as Lead

        Args:
            sponsor_data: Dict with sponsor information

        Returns:
            Lead ID if successful, None if failed
        """
        try:
            # Transform sponsor data to Salesforce Lead format (standard fields only)
            lead_data = self._transform_to_lead(sponsor_data)

            # Try to check for duplicates (may timeout, so catch exceptions)
            try:
                existing = self._find_duplicate_lead(sponsor_data['name'])
                if existing:
                    logger.warning(f"  Duplicate found: {sponsor_data['name']} (ID: {existing})")
                    return self._update_lead(existing, lead_data)
            except Exception as dup_check_error:
                logger.debug(f"  Duplicate check error (will proceed with create): {str(dup_check_error)[:100]}")

            # Create new lead
            result = self.sf.Lead.create(lead_data)
            lead_id = result['id']
            logger.info(f"  ✓ Created: {sponsor_data['name']} (ID: {lead_id})")
            return lead_id

        except Exception as e:
            error_msg = str(e).lower()
            # Handle expired session errors by attempting to reconnect
            if "expired session" in error_msg or "invalid_grant" in error_msg or "session" in error_msg:
                logger.warning(f"  Session timeout detected, will retry with fresh connection")
                # Don't retry here - let caller handle with fresh client
                logger.error(f"  Failed to upload {sponsor_data['name']}: Session timeout")
                return None
            else:
                logger.error(f"  ✗ Failed to upload {sponsor_data['name']}: {str(e)[:100]}")
                return None

    def _transform_to_lead(self, sponsor):
        """Transform sponsor dict to Salesforce Lead fields (standard fields only)"""
        # Parse contact name if available
        contact_name = sponsor.get('contact', {}).get('name', '')
        first_name, last_name = self._parse_name(contact_name)

        # Map tier to rating (Hot/Warm/Cold)
        rating = self._tier_to_rating(sponsor.get('tier', ''))

        # Build lead data with ONLY STANDARD Salesforce fields
        lead_data = {
            'Company': sponsor['name'],
            'FirstName': first_name or 'Development',
            'LastName': last_name or 'Contact',
            'Email': sponsor.get('contact', {}).get('email'),
            'Phone': sponsor.get('contact', {}).get('phone'),
            'Website': sponsor.get('contact', {}).get('website'),
            'Street': self._extract_street(sponsor.get('contact', {}).get('address', '')),
            'City': self._extract_city(sponsor.get('contact', {}).get('address', '')),
            'State': self._extract_state(sponsor.get('contact', {}).get('address', '')),
            'PostalCode': self._extract_zip(sponsor.get('contact', {}).get('address', '')),
            'LeadSource': SALESFORCE_LEAD_SOURCE,
            'Status': 'New',
            'Rating': rating,
            'Description': sponsor.get('mission_alignment', ''),
        }

        # Build description with additional info since we don't have custom fields
        description_parts = [
            f"Type: {sponsor.get('type') or 'Unknown'}",
            f"Tier: {sponsor.get('tier') or 'Unknown'}",
            f"Relevance Score: {sponsor.get('relevance_score') or 'N/A'}/10",
            f"Quality Score: {sponsor.get('quality_score') or 'N/A'}/10",
            f"Grant Range: {sponsor.get('giving', {}).get('range') or 'Not specified'}",
            f"Application Strategy: {sponsor.get('application_strategy') or 'To be determined'}",
            "",
            "Mission Alignment:",
            sponsor.get('mission_alignment') or 'No details provided'
        ]

        # Ensure all parts are strings and join
        lead_data['Description'] = '\n'.join(str(part) for part in description_parts)

        # Remove None values (Salesforce doesn't like them)
        return {k: v for k, v in lead_data.items() if v is not None}

    def _parse_name(self, full_name):
        """Parse full name into first and last name"""
        if not full_name or full_name == '':
            return None, None

        parts = full_name.strip().split(' ', 1)
        if len(parts) == 1:
            return parts[0], parts[0]
        return parts[0], parts[1]

    def _tier_to_rating(self, tier):
        """Map tier to Salesforce Rating (Hot/Warm/Cold)"""
        if not tier:
            return 'Warm'

        tier_upper = tier.upper()
        if 'TIER 1A' in tier_upper or 'TIER 1B' in tier_upper:
            return 'Hot'
        elif 'TIER 2' in tier_upper:
            return 'Warm'
        else:
            return 'Cold'

    def _extract_street(self, address):
        """Extract street from full address"""
        if not address:
            return None
        parts = address.split(',')
        return parts[0].strip() if parts else None

    def _extract_city(self, address):
        """Extract city from full address"""
        if not address:
            return None
        parts = address.split(',')
        return parts[1].strip() if len(parts) > 1 else None

    def _extract_state(self, address):
        """Extract state from full address"""
        if not address:
            return None
        parts = address.split(',')
        if len(parts) > 2:
            last_part = parts[-1].strip()
            words = last_part.split()
            for word in words:
                if len(word) == 2 and word.isupper():
                    return word
        return None

    def _extract_zip(self, address):
        """Extract ZIP code from full address"""
        if not address:
            return None
        import re
        zip_match = re.search(r'\b\d{5}\b', address)
        return zip_match.group(0) if zip_match else None

    def _find_duplicate_lead(self, company_name):
        """Check if lead with same company name exists"""
        try:
            # Escape single quotes in company name for SOQL query
            safe_name = company_name.replace("'", "\\'")
            query = f"SELECT Id FROM Lead WHERE Company = '{safe_name}' LIMIT 1"
            result = self.sf.query(query)
            if result['totalSize'] > 0:
                return result['records'][0]['Id']
            return None
        except Exception as e:
            logger.debug(f"Duplicate check failed: {e}")
            return None

    def _update_lead(self, lead_id, lead_data):
        """Update existing lead"""
        try:
            self.sf.Lead.update(lead_id, lead_data)
            logger.info(f"  ↻ Updated: {lead_data.get('Company')} (ID: {lead_id})")
            return lead_id
        except Exception as e:
            logger.error(f"Lead update failed: {e}")
            return None

    def upload_multiple_sponsors(self, sponsors_list):
        """
        Upload multiple sponsors in batch

        Args:
            sponsors_list: List of sponsor dicts

        Returns:
            Dict with success/failure counts and IDs
        """
        results = {
            'success': [],
            'failed': [],
            'updated': [],
            'total': len(sponsors_list)
        }

        logger.info(f"\nUploading {len(sponsors_list)} sponsors...")

        for i, sponsor in enumerate(sponsors_list, 1):
            logger.info(f"\n[{i}/{len(sponsors_list)}] {sponsor['name']}")
            lead_id = self.upload_sponsor_as_lead(sponsor)

            if lead_id:
                # Check if it was an update
                if self._find_duplicate_lead(sponsor['name']):
                    results['updated'].append({'name': sponsor['name'], 'id': lead_id})
                else:
                    results['success'].append({'name': sponsor['name'], 'id': lead_id})
            else:
                results['failed'].append({'name': sponsor['name'], 'error': 'Upload failed'})

        logger.info(
            f"\n✓ Batch upload complete: {len(results['success'])} created, "
            f"{len(results['updated'])} updated, {len(results['failed'])} failed"
        )

        return results


# Export
__all__ = ['SalesforceClient']
