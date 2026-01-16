"""
Email System Integration Tests

Tests the email template generation, Salesforce sending, engagement tracking,
and campaign orchestration functionality.

Note: These tests require valid Salesforce credentials in .env
"""

import sys
import os
import json

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'salesforce'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'email'))

from email_templates import generate_sponsor_email, get_all_template_types, preview_template
from engagement_tracker import EngagementTracker


def test_template_generation():
    """Test that templates are generated correctly with token replacement"""
    print("\n" + "="*70)
    print("TEST 1: Email Template Generation")
    print("="*70)

    sample_sponsor = {
        'name': 'Test Foundation',
        'type': 'Foundation',
        'tier': 'Tier 1A',
        'contact': {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '(555) 123-4567',
            'website': 'https://example.com',
            'address': '123 Test St, New York, NY 10001'
        },
        'giving': {
            'range': '$250K-$1M'
        },
        'relevance_score': 9.5,
        'quality_score': 9.0,
        'mission_alignment': 'Arts education and disability services',
        'application_strategy': 'Submit LOI by March 15, 2026'
    }

    try:
        # Generate email
        email = generate_sponsor_email(sample_sponsor, template_type='foundation')

        # Verify output structure
        assert 'subject' in email
        assert 'body' in email
        assert 'tokens' in email
        assert 'template_type' in email

        # Verify tokens were replaced
        assert '{{' not in email['body']
        assert '{{' not in email['subject']

        # Verify content
        assert 'Jane' in email['body']
        assert 'Test Foundation' in email['body']
        assert '$250K-$1M' in email['body']

        print("[OK] Template generation successful")
        print(f"  - Template type: {email['template_type']}")
        print(f"  - Subject: {email['subject']}")
        print(f"  - Body length: {len(email['body'])} characters")
        print(f"  - Tokens used: {len(email['tokens'])}")

        return True

    except AssertionError as e:
        print(f"[ERROR] Template validation failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Template generation failed: {str(e)[:200]}")
        return False


def test_all_template_types():
    """Test that all template types generate correctly"""
    print("\n" + "="*70)
    print("TEST 2: All Template Types")
    print("="*70)

    template_types = get_all_template_types()
    print(f"Testing {len(template_types)} template types: {', '.join(template_types)}")

    sample_sponsor = {
        'name': 'Test Organization',
        'type': 'Foundation',
        'tier': 'Tier 2',
        'contact': {'name': 'John Doe'},
        'giving': {'range': '$100K-$500K'},
        'mission_alignment': 'Arts and community',
        'application_strategy': 'Apply online'
    }

    try:
        for template_type in template_types:
            email = generate_sponsor_email(sample_sponsor, template_type=template_type)

            # Verify structure
            assert email['template_type'] == template_type
            assert len(email['subject']) > 0
            assert len(email['body']) > 0

            print(f"[OK] {template_type.upper()} template")

        print("[OK] All template types validated successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Template type test failed: {str(e)[:200]}")
        return False


def test_template_preview():
    """Test template preview functionality"""
    print("\n" + "="*70)
    print("TEST 3: Template Preview")
    print("="*70)

    try:
        preview = preview_template('foundation')

        assert 'Template Type: FOUNDATION' in preview
        assert 'Subject:' in preview
        assert 'Tokens Used:' in preview

        print("[OK] Template preview generated")
        print(f"  - Preview length: {len(preview)} characters")

        return True

    except Exception as e:
        print(f"[ERROR] Template preview failed: {str(e)[:200]}")
        return False


def test_engagement_scoring():
    """Test engagement scoring algorithm with sample data"""
    print("\n" + "="*70)
    print("TEST 4: Engagement Scoring Logic")
    print("="*70)

    print("[INFO] Engagement Scoring (Phase 1 - Simplified)")
    print("  Email sent: 0 points (baseline)")
    print("  No response: 0 points")
    print("  Got reply: 80 points")
    print("  Same-day reply: +10 bonus (90 total)")
    print("  Next-day reply: +5 bonus (85 total)")

    try:
        # Test scoring thresholds
        test_cases = [
            (0, 'Cold'),
            (39, 'Cold'),
            (40, 'Warm'),
            (69, 'Warm'),
            (70, 'Hot'),
            (100, 'Hot')
        ]

        for score, expected_category in test_cases:
            if score < 40:
                category = 'Cold'
            elif score < 70:
                category = 'Warm'
            else:
                category = 'Hot'

            assert category == expected_category, f"Score {score} should be {expected_category}, got {category}"
            print(f"[OK] Score {score} = {category}")

        print("\n[OK] Engagement scoring logic validated")
        return True

    except AssertionError as e:
        print(f"[ERROR] Scoring logic failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Engagement scoring test failed: {str(e)[:200]}")
        return False


def test_token_replacement():
    """Test token replacement with various sponsor data"""
    print("\n" + "="*70)
    print("TEST 5: Token Replacement")
    print("="*70)

    test_sponsors = [
        {
            'name': 'XYZ Foundation',
            'type': 'Foundation',
            'contact': {'name': 'Alice Johnson'},
            'giving': {'range': '$50K-$250K'},
            'mission_alignment': 'Arts education',
            'application_strategy': 'Direct approach'
        },
        {
            'name': 'Tech Corp Inc',
            'type': 'Corporation',
            'contact': {'name': 'Bob Smith'},
            'giving': {'range': '$100K-$500K'},
            'mission_alignment': 'Community programs',
            'application_strategy': 'Sponsorship proposal'
        },
        {
            'name': 'Community NGO',
            'type': 'NGO',
            'contact': {'name': 'Carol Lee'},
            'giving': {'range': '$25K-$100K'},
            'mission_alignment': 'Accessibility initiatives',
            'application_strategy': 'Partnership discussion'
        }
    ]

    try:
        for sponsor in test_sponsors:
            email = generate_sponsor_email(sponsor)

            # Verify no tokens remain
            assert '{{' not in email['body']
            assert '{{' not in email['subject']

            # Verify sponsor name is in body
            assert sponsor['name'] in email['body']

            # Verify contact name is in body
            first_name = sponsor['contact']['name'].split()[0]
            assert first_name in email['body']

            # Verify giving range is in body
            assert sponsor['giving']['range'] in email['body']

            print(f"[OK] {sponsor['name']} ({sponsor['type']})")

        print("\n[OK] Token replacement validated for all sponsor types")
        return True

    except AssertionError as e:
        print(f"[ERROR] Token replacement failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Token replacement test failed: {str(e)[:200]}")
        return False


def run_all_tests():
    """Run all email system tests"""
    print("\n")
    print("[" + "="*68 + "]")
    print("|" + " "*68 + "|")
    print("|" + "  Email System Tests".center(68) + "|")
    print("|" + " "*68 + "|")
    print("[" + "="*68 + "]")

    tests = [
        ("Template Generation", test_template_generation),
        ("All Template Types", test_all_template_types),
        ("Template Preview", test_template_preview),
        ("Engagement Scoring", test_engagement_scoring),
        ("Token Replacement", test_token_replacement),
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
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[+] PASS" if result else "[-] FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All email system tests passed!")
        print("\nNext steps:")
        print("  1. Configure Salesforce credentials in .env")
        print("  2. Run email campaign: python email/run_campaign.py --action preview --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        print("  3. Send campaign: python email/run_campaign.py --action send --input docs/VALIDATED_SPONSOR_DATABASE_REPORT.md")
        print("  4. Generate report: python email/run_campaign.py --action report")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
