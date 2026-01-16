"""
Bulk add researched emails to Salesforce Leads from JSON

Usage:
    python salesforce/bulk_add_emails_from_json.py --input data/emails_research_results.json
"""

import sys
import os
import json
import argparse
import logging

sys.path.insert(0, os.path.dirname(__file__))

from salesforce_client import SalesforceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def bulk_add_emails_from_json(json_path='data/emails_research_results.json'):
    """Read researched emails from JSON and bulk update Salesforce Leads"""

    logger.info(f"Opening {json_path}...\n")

    if not os.path.exists(json_path):
        logger.error(f"[ERROR] File not found: {json_path}")
        return False

    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    emails_to_add = data.get('emails', [])
    logger.info(f"Loaded {len(emails_to_add)} email addresses\n")

    logger.info("Connecting to Salesforce...\n")
    client = SalesforceClient()

    logger.info("Updating Leads with researched emails...\n")

    updates_made = 0
    errors = 0
    not_found = 0

    for i, entry in enumerate(emails_to_add, 1):
        company_name = entry['company']
        email = entry['email'].strip()

        logger.info(f"[{i}/{len(emails_to_add)}] {company_name}")

        # Find Lead by company name
        try:
            safe_name = company_name.replace("'", "\\'")
            query = f"SELECT Id FROM Lead WHERE Company = '{safe_name}' LIMIT 1"
            result = client.sf.query(query)

            if result['totalSize'] == 0:
                logger.warning(f"  [!] Lead not found in Salesforce")
                not_found += 1
                continue

            lead_id = result['records'][0]['Id']

            # Update Lead with email
            client.sf.Lead.update(lead_id, {'Email': email})
            logger.info(f"  [OK] Updated with: {email}")
            updates_made += 1

        except Exception as e:
            logger.error(f"  [ERROR] {str(e)[:80]}")
            errors += 1

    logger.info(f"\n{'='*70}")
    logger.info("BULK EMAIL UPDATE SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total emails researched: {len(emails_to_add)}")
    logger.info(f"Successfully updated: {updates_made}")
    logger.info(f"Leads not found: {not_found}")
    logger.info(f"Errors: {errors}")
    logger.info(f"{'='*70}\n")

    if updates_made == len(emails_to_add):
        logger.info("[SUCCESS] All emails have been added to Salesforce!")
        logger.info("\nNext steps:")
        logger.info("1. Verify: python salesforce/verify_lead_emails.py")
        logger.info("2. Send campaign: python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        return True
    else:
        logger.warning(f"\n[WARNING] {len(emails_to_add) - updates_made} updates failed or were skipped")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Bulk add researched emails to Salesforce Leads from JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python salesforce/bulk_add_emails_from_json.py --input data/emails_research_results.json
        """
    )

    parser.add_argument(
        '--input',
        default='data/emails_research_results.json',
        help='JSON file path with researched emails',
        metavar='FILE'
    )

    args = parser.parse_args()

    success = bulk_add_emails_from_json(args.input)
    sys.exit(0 if success else 1)
