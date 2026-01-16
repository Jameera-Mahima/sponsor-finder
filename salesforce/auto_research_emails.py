"""
Automatically research contact emails from sponsor websites

Uses BeautifulSoup to scrape sponsor websites for contact emails.

Usage:
    pip install beautifulsoup4 requests
    python salesforce/auto_research_emails.py
"""

import sys
import os
import re
import logging
import time

sys.path.insert(0, os.path.dirname(__file__))

from salesforce_client import SalesforceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Try to import web scraping libraries
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING_LIBS = True
except ImportError:
    HAS_SCRAPING_LIBS = False
    logger.warning("beautifulsoup4 and requests not installed. Run: pip install beautifulsoup4 requests")


def extract_email_from_website(website_url, org_name):
    """
    Extract contact email from organization website

    Strategy:
    1. Check common paths: /contact, /grants, /apply, /about
    2. Look for mailto: links
    3. Extract email patterns from text
    4. Prefer emails with keywords: grant, info, contact, apply
    """
    if not website_url or not HAS_SCRAPING_LIBS:
        return None

    # Common paths to check
    paths_to_check = ['', '/contact', '/grants', '/apply', '/about', '/contact-us', '/donations']

    for path in paths_to_check:
        try:
            url = website_url.rstrip('/') + path
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for mailto: links
                mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
                if mailto_links:
                    email = mailto_links[0]['href'].replace('mailto:', '').split('?')[0]
                    if '@' in email:
                        return email.strip()

                # Look for email patterns in text
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)

                if emails:
                    # Filter for relevant emails (grants, info, contact, apply, development)
                    for email in emails:
                        email_lower = email.lower()
                        if any(keyword in email_lower for keyword in ['grant', 'info', 'contact', 'apply', 'develop']):
                            return email.strip()

                    # Return first email if no preferred ones found
                    if emails:
                        return emails[0].strip()

        except requests.RequestException:
            continue
        except Exception as e:
            logger.debug(f"Error parsing {url}: {str(e)[:50]}")
            continue

        # Small delay between requests to be respectful
        time.sleep(0.5)

    return None


def research_and_update_emails():
    """Research emails for all Leads and update Salesforce"""

    if not HAS_SCRAPING_LIBS:
        logger.error("beautifulsoup4 and requests are required for automated research")
        logger.info("Install with: pip install beautifulsoup4 requests")
        return False

    logger.info("Connecting to Salesforce...\n")
    client = SalesforceClient()

    # Get Leads without emails
    logger.info("Querying Leads without emails...")
    query = "SELECT Id, Company, Website FROM Lead WHERE Email = null ORDER BY Company"
    leads = client.sf.query(query)['records']

    logger.info(f"Found {len(leads)} Leads without emails\n")

    if not leads:
        logger.info("[OK] All Leads already have emails!")
        return True

    updates_made = 0
    found_emails = 0
    no_emails_found = 0

    for i, lead in enumerate(leads, 1):
        lead_id = lead['Id']
        company = lead['Company']
        website = lead.get('Website')

        logger.info(f"[{i}/{len(leads)}] {company}")

        if not website:
            logger.info(f"  [SKIP] No website provided")
            continue

        # Research email
        logger.info(f"  Researching from: {website}")
        email = extract_email_from_website(website, company)

        if email:
            try:
                client.sf.Lead.update(lead_id, {'Email': email})
                logger.info(f"  [OK] Updated with: {email}")
                updates_made += 1
                found_emails += 1
            except Exception as e:
                logger.error(f"  [ERROR] Failed to update: {str(e)[:80]}")
        else:
            logger.info(f"  [!] No email found")
            no_emails_found += 1

    logger.info(f"\n{'='*70}")
    logger.info("AUTOMATED EMAIL RESEARCH SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Processed: {len(leads)}")
    logger.info(f"Emails found: {found_emails}")
    logger.info(f"No emails found: {no_emails_found}")
    logger.info(f"Updated in Salesforce: {updates_made}")
    logger.info(f"{'='*70}\n")

    if no_emails_found > 0:
        logger.warning(f"\n[WARNING] {no_emails_found} Leads still need emails")
        logger.info("You'll need to manually research these and add them to Salesforce")
        logger.info("Run: python salesforce/export_leads.py")
        logger.info("Then manually add emails and run: python salesforce/update_lead_emails.py")
        return False
    else:
        logger.info("[SUCCESS] All emails have been researched and updated!")
        logger.info("Verify with: python salesforce/verify_lead_emails.py")
        return True


if __name__ == '__main__':
    success = research_and_update_emails()
    sys.exit(0 if success else 1)
