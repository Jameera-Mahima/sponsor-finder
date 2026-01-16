"""
Verify Salesforce Leads have email addresses

Usage:
    python salesforce/verify_lead_emails.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from salesforce_client import SalesforceClient


def verify_lead_emails():
    """Check how many Leads have email addresses"""

    print("Connecting to Salesforce...\n")
    client = SalesforceClient()

    # Count Leads with emails
    print("Querying Leads with emails...")
    query_with_email = "SELECT COUNT() FROM Lead WHERE Email != null"
    result_with = client.sf.query(query_with_email)
    count_with_email = result_with['totalSize']

    # Count Leads without emails
    print("Querying Leads without emails...")
    query_without_email = "SELECT COUNT() FROM Lead WHERE Email = null"
    result_without = client.sf.query(query_without_email)
    count_without_email = result_without['totalSize']

    # Total Leads
    total = count_with_email + count_without_email

    print(f"\n{'='*60}")
    print("LEAD EMAIL VERIFICATION")
    print(f"{'='*60}")
    print(f"Total Leads: {total}")
    print(f"Leads WITH email: {count_with_email} ({count_with_email/total*100:.1f}%)")
    print(f"Leads WITHOUT email: {count_without_email} ({count_without_email/total*100:.1f}%)")
    print(f"{'='*60}\n")

    if count_without_email > 0:
        # Show which Leads are missing emails
        print(f"Leads missing emails:\n")
        query_missing = "SELECT Id, Company FROM Lead WHERE Email = null ORDER BY Company"
        missing = client.sf.query(query_missing)
        for lead in missing['records']:
            print(f"  - {lead['Company']} (ID: {lead['Id']})")

    if count_with_email == total:
        print("\n[SUCCESS] All Leads have email addresses!")
        print("\nYou can now run the email campaign:")
        print("  python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        return True
    else:
        print(f"\n[WARNING] {count_without_email} Leads still need emails")
        return False


if __name__ == '__main__':
    success = verify_lead_emails()
    sys.exit(0 if success else 1)
