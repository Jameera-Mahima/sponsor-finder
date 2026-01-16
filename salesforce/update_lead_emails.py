"""
Bulk update Salesforce Lead emails from CSV

Usage:
    python salesforce/update_lead_emails.py --input data/leads_for_email_research.csv
"""

import sys
import os
import csv
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from salesforce_client import SalesforceClient


def update_leads_from_csv(csv_path='data/leads_for_email_research.csv'):
    """Update Salesforce Leads with emails from CSV file"""

    print(f"Opening {csv_path}...\n")

    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        return False

    print("Connecting to Salesforce...")
    client = SalesforceClient()

    print(f"Reading CSV and updating Leads...\n")

    updates_made = 0
    skipped = 0
    errors = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            lead_id = row['Lead ID'].strip()
            email = row['Email'].strip()
            company = row['Company'].strip()

            # Skip if no email provided
            if not email or email == '':
                print(f"[{i}] [SKIP] {company}: No email provided")
                skipped += 1
                continue

            # Update Lead in Salesforce
            try:
                client.sf.Lead.update(lead_id, {'Email': email})
                print(f"[{i}] [OK] {company}: Updated with {email}")
                updates_made += 1
            except Exception as e:
                print(f"[{i}] [ERROR] {company}: {str(e)[:80]}")
                errors += 1

    print(f"\n{'='*70}")
    print("UPDATE SUMMARY")
    print(f"{'='*70}")
    print(f"Updated: {updates_made}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"{'='*70}\n")

    if errors == 0:
        print("[OK] All updates completed successfully!")
        print("\nNext steps:")
        print("1. Run: python salesforce/verify_lead_emails.py")
        print("2. Then run: python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        return True
    else:
        print(f"[WARNING] {errors} updates failed. Please review the errors above.")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update Salesforce Leads with emails from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python salesforce/update_lead_emails.py --input data/leads_for_email_research.csv
        """
    )

    parser.add_argument(
        '--input',
        default='data/leads_for_email_research.csv',
        help='CSV file path (default: data/leads_for_email_research.csv)',
        metavar='FILE'
    )

    args = parser.parse_args()

    success = update_leads_from_csv(args.input)
    sys.exit(0 if success else 1)
