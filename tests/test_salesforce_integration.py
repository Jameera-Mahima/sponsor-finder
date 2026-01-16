"""
Test Salesforce API integration

Tests include:
- Connection testing
- Sample sponsor upload
- Data transformation
"""

import sys
import os

# Add salesforce module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'salesforce'))

from salesforce_client import SalesforceClient


def test_connection():
    """Test Salesforce connection with provided credentials"""
    print("\n" + "="*70)
    print("TEST 1: Salesforce Connection")
    print("="*70)
    print("Testing connection to Salesforce with provided credentials...")

    try:
        client = SalesforceClient()
        print("[OK] Successfully connected to Salesforce!")
        print(f"  Instance: {os.getenv('SALESFORCE_DOMAIN', 'login')}.salesforce.com")
        print(f"  User: {os.getenv('SALESFORCE_USERNAME')}")
        return True

    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print("\nPlease verify your .env file contains:")
        print("  - SALESFORCE_USERNAME")
        print("  - SALESFORCE_PASSWORD")
        print("  - SALESFORCE_SECURITY_TOKEN")
        print("  - SALESFORCE_DOMAIN (optional, defaults to 'login')")
        return False

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Connection failed: {error_msg[:200]}")

        if "invalid_grant" in error_msg:
            print("\n[WARNING] Invalid credentials. Please check:")
            print("  1. Username and password are correct")
            print("  2. Security token is correct (case-sensitive)")
            print("  3. Your Salesforce account is active")
        elif "host" in error_msg.lower() or "connection" in error_msg.lower():
            print("\n[WARNING] Network error. Please check:")
            print("  1. Internet connection is working")
            print("  2. Salesforce is accessible (login.salesforce.com)")
        else:
            print(f"\nFull error: {error_msg}")

        return False


def test_upload_sample():
    """Test uploading a single sample sponsor"""
    print("\n" + "="*70)
    print("TEST 2: Sample Sponsor Upload")
    print("="*70)
    print("Uploading test sponsor to Salesforce...")

    sample_sponsor = {
        'name': 'CSOAF Test Foundation - Integration Test',
        'type': 'Foundation',
        'tier': 'Tier 1A',
        'contact': {
            'name': 'Integration Test',
            'email': 'test@integration.local',
            'phone': '(555) 555-5555',
            'website': 'https://example.com/test',
            'address': '123 Test Street, New York, NY 10001'
        },
        'giving': {
            'range': '$100K-$500K',
            'geographic_scope': 'New York'
        },
        'relevance_score': 9.5,
        'quality_score': 9.0,
        'mission_alignment': 'This is an integration test record. Please delete after testing.',
        'application_strategy': 'Test integration between sponsor-finder and Salesforce',
        'last_verified': '2026-01-14'
    }

    try:
        client = SalesforceClient()

        # Upload the sample
        lead_id = client.upload_sponsor_as_lead(sample_sponsor)

        if lead_id:
            print(f"[OK] Test sponsor uploaded successfully!")
            print(f"  Name: {sample_sponsor['name']}")
            print(f"  Lead ID: {lead_id}")
            print(f"  Type: {sample_sponsor['type']}")
            print(f"  Tier: {sample_sponsor['tier']}")

            print("\n[WARNING] Delete this test record from Salesforce")
            print(f"  1. Log in to Salesforce")
            print(f"  2. Go to Leads tab")
            print(f"  3. Search for 'CSOAF Test Foundation'")
            print(f"  4. Delete the record with ID: {lead_id}")

            return True
        else:
            print(f"[ERROR] Failed to upload test sponsor")
            return False

    except Exception as e:
        print(f"[ERROR] Upload test failed: {str(e)[:200]}")
        return False


def test_data_transformation():
    """Test sponsor data transformation to Salesforce Lead format"""
    print("\n" + "="*70)
    print("TEST 3: Data Transformation")
    print("="*70)
    print("Testing sponsor data transformation...")

    sample_sponsor = {
        'name': 'Test Arts Foundation',
        'type': 'Foundation',
        'tier': 'Tier 1B',
        'contact': {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '(555) 123-4567',
            'website': 'https://example.com',
            'address': '456 Arts Ave, New York, NY 10002'
        },
        'giving': {
            'range': '$250K-$1M',
            'geographic_scope': 'Northeast'
        },
        'relevance_score': 8.7,
        'quality_score': 8.5,
        'mission_alignment': 'Strong focus on arts education and community programs',
        'application_strategy': 'Apply in Q2 2026',
        'last_verified': '2026-01-14'
    }

    try:
        client = SalesforceClient()
        lead_data = client._transform_to_lead(sample_sponsor)

        print("[OK] Data transformation successful!")
        print(f"\nTransformed Lead Data:")
        print(f"  Company: {lead_data.get('Company')}")
        print(f"  First Name: {lead_data.get('FirstName')}")
        print(f"  Last Name: {lead_data.get('LastName')}")
        print(f"  Email: {lead_data.get('Email')}")
        print(f"  Phone: {lead_data.get('Phone')}")
        print(f"  Website: {lead_data.get('Website')}")
        print(f"  Rating: {lead_data.get('Rating')}")
        print(f"  Lead Source: {lead_data.get('LeadSource')}")
        print(f"  Status: {lead_data.get('Status')}")

        # Check description field (where sponsor metadata is embedded)
        description = lead_data.get('Description', '')
        if description:
            print(f"\nDescription field (embedded metadata):")
            for line in description.split('\n')[:5]:
                print(f"    {line}")

        return True

    except Exception as e:
        print(f"[ERROR] Data transformation test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n")
    print("[" + "="*68 + "]")
    print("|" + " "*68 + "|")
    print("|" + "  Salesforce Integration Tests".center(68) + "|")
    print("|" + " "*68 + "|")
    print("[" + "="*68 + "]")

    # Check environment
    if not os.getenv('SALESFORCE_USERNAME'):
        print("\n[ERROR] Missing SALESFORCE_USERNAME in .env file")
        print("\nSetup instructions:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your Salesforce credentials:")
        print("     SALESFORCE_USERNAME=your-email@example.com")
        print("     SALESFORCE_PASSWORD=your-password")
        print("     SALESFORCE_SECURITY_TOKEN=your-token-here")
        print("     SALESFORCE_DOMAIN=login")
        return False

    if not os.getenv('SALESFORCE_PASSWORD'):
        print("\n[ERROR] Missing SALESFORCE_PASSWORD in .env file")
        return False

    if not os.getenv('SALESFORCE_SECURITY_TOKEN'):
        print("\n[ERROR] Missing SALESFORCE_SECURITY_TOKEN in .env file")
        return False

    # Run tests
    tests = [
        ("Connection", test_connection),
        ("Data Transformation", test_data_transformation),
        ("Sample Upload", test_upload_sample),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test error: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[+] PASS" if result else "[-] FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("  1. Run the full upload with:")
        print("     python salesforce/load_sponsors.py --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        print("  2. Monitor the upload process")
        print("  3. Verify in Salesforce UI (Leads tab)")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
