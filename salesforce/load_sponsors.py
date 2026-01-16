"""
Load validated sponsors into Salesforce

Usage:
    python salesforce/load_sponsors.py --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md
    python salesforce/load_sponsors.py --input sponsors.json --dry-run
"""

import argparse
import sys
from pathlib import Path
from salesforce_client import SalesforceClient
from sponsor_parser import parse_markdown_report, parse_json_file


def load_sponsors_from_file(file_path):
    """Load sponsor data from JSON or markdown file"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix == '.json':
        return parse_json_file(file_path)
    elif path.suffix == '.md':
        return parse_markdown_report(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .json or .md")


def main():
    parser = argparse.ArgumentParser(
        description='Upload validated sponsors to Salesforce CRM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload all sponsors from markdown report
  python salesforce/load_sponsors.py --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md

  # Preview sponsors without uploading
  python salesforce/load_sponsors.py --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md --dry-run

  # Upload from JSON file
  python salesforce/load_sponsors.py --input sponsors.json
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Path to sponsor data file (markdown or JSON)',
        metavar='FILE'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview sponsors without uploading to Salesforce'
    )
    parser.add_argument(
        '--campaign',
        help='Campaign name for tracking (optional)',
        metavar='NAME'
    )

    args = parser.parse_args()

    try:
        # Load sponsors from file
        print(f"Loading sponsors from: {args.input}")
        sponsors = load_sponsors_from_file(args.input)
        print(f"[OK] Found {len(sponsors)} sponsors\n")

        if not sponsors:
            print("No sponsors to upload. File may be empty.")
            return 1

        if args.dry_run:
            print("DRY RUN - Preview of sponsors to upload:")
            print(f"{'='*70}")
            for i, sponsor in enumerate(sponsors, 1):
                print(f"\n{i}. {sponsor.get('name', 'Unknown')}")
                if sponsor.get('type'):
                    print(f"   Type: {sponsor['type']}")
                if sponsor.get('tier'):
                    print(f"   Tier: {sponsor['tier']}")
                if sponsor.get('relevance_score'):
                    print(f"   Relevance Score: {sponsor['relevance_score']}/10")
                if sponsor.get('contact', {}).get('email'):
                    print(f"   Email: {sponsor['contact']['email']}")
                if sponsor.get('contact', {}).get('website'):
                    print(f"   Website: {sponsor['contact']['website']}")

            print(f"\n{'='*70}")
            print(f"\nTo upload these {len(sponsors)} sponsors, run:")
            print(f"  python salesforce/load_sponsors.py --input {args.input}")
            return 0

        # Connect to Salesforce
        print("Connecting to Salesforce...")
        try:
            client = SalesforceClient()
            print("[OK] Connected to Salesforce\n")
        except Exception as e:
            print(f"[ERROR] Failed to connect to Salesforce: {e}")
            print("\nPlease check:")
            print("  1. .env file exists with credentials")
            print("  2. SALESFORCE_USERNAME is set")
            print("  3. SALESFORCE_PASSWORD is set")
            print("  4. SALESFORCE_SECURITY_TOKEN is set")
            return 1

        # Upload sponsors
        print(f"Uploading {len(sponsors)} sponsors...")
        print(f"{'='*70}")

        results = client.upload_multiple_sponsors(sponsors)

        # Print summary
        print(f"\n{'='*70}")
        print("UPLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"Total sponsors processed: {results['total']}")
        print(f"[+] Created: {len(results['success'])}")
        print(f"[~] Updated: {len(results['updated'])}")
        print(f"[-] Failed: {len(results['failed'])}")

        # Print created leads
        if results['success']:
            print(f"\nSuccessfully created {len(results['success'])} new leads:")
            for item in results['success'][:10]:  # Show first 10
                print(f"  + {item['name']} (ID: {item['id']})")
            if len(results['success']) > 10:
                print(f"  ... and {len(results['success']) - 10} more")

        # Print updated leads
        if results['updated']:
            print(f"\nUpdated {len(results['updated'])} existing leads:")
            for item in results['updated'][:10]:  # Show first 10
                print(f"  ~ {item['name']} (ID: {item['id']})")
            if len(results['updated']) > 10:
                print(f"  ... and {len(results['updated']) - 10} more")

        # Print failed uploads
        if results['failed']:
            print(f"\nFailed to upload {len(results['failed'])} sponsors:")
            for item in results['failed'][:10]:  # Show first 10
                error = item.get('error', 'Unknown error')
                print(f"  - {item['name']}: {error}")
            if len(results['failed']) > 10:
                print(f"  ... and {len(results['failed']) - 10} more")

        print(f"\n{'='*70}")

        if results['failed']:
            print(f"\n[WARNING] {len(results['failed'])} sponsors failed to upload.")
            print("Review the errors above and try again.")
            return 1
        else:
            print(f"\n[SUCCESS] All {results['total']} sponsors uploaded successfully!")
            if args.campaign:
                print(f"Campaign: {args.campaign}")
            print("\nNext steps:")
            print("  1. Log in to Salesforce")
            print("  2. Navigate to the Leads tab")
            print("  3. Filter by Lead Source = 'AI Sponsor Search'")
            print("  4. Verify the data is correct")
            return 0

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
