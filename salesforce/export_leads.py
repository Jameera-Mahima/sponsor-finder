"""
Export Salesforce Leads to CSV for email research

Usage:
    python salesforce/export_leads.py
"""

import sys
import os
import csv

sys.path.insert(0, os.path.dirname(__file__))

from salesforce_client import SalesforceClient


def export_leads_to_csv(output_path='data/leads_for_email_research.csv'):
    """Export all Salesforce Leads to CSV for manual email research"""

    print("Connecting to Salesforce...")
    client = SalesforceClient()

    print("Querying Leads...")
    # Query all Leads
    query = """
        SELECT Id, Company, Website, Email, Status
        FROM Lead
        ORDER BY Company
    """
    result = client.sf.query(query)
    leads = result['records']

    print(f"Retrieved {len(leads)} Leads\n")

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # Write to CSV
    print(f"Writing to {output_path}...\n")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Lead ID', 'Company', 'Website', 'Email', 'Status'])
        writer.writeheader()

        for lead in leads:
            writer.writerow({
                'Lead ID': lead['Id'],
                'Company': lead['Company'],
                'Website': lead.get('Website', ''),
                'Email': lead.get('Email', ''),
                'Status': lead.get('Status', '')
            })

    print(f"[OK] Exported {len(leads)} leads to {output_path}")
    print(f"\nNext steps:")
    print(f"1. Open {output_path}")
    print(f"2. For each Lead, visit the Website and find the contact email")
    print(f"3. Add email to the 'Email' column")
    print(f"4. Save the CSV")
    print(f"5. Run: python salesforce/update_lead_emails.py --input {output_path}")


if __name__ == '__main__':
    export_leads_to_csv()
