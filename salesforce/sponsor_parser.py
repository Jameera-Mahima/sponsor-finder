"""
Parse sponsor data from various formats into standardized structure

Supports:
- Markdown reports (VALIDATED_SPONSOR_DATABASE_REPORT.md format)
- JSON files
"""

import json
import re
from pathlib import Path


def parse_markdown_report(file_path):
    """
    Parse sponsor data from markdown report

    Args:
        file_path: Path to markdown file

    Returns:
        List of sponsor dicts
    """
    sponsors = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all tier sections by looking for ### TIER patterns
    # Split content into tier sections
    tier_sections = re.split(r'(?=### TIER)', content)

    for tier_section in tier_sections:
        if not tier_section.strip():
            continue

        # Extract tier name
        tier_match = re.match(r'### (TIER [12][AB]?)[:\s-]*', tier_section)
        if not tier_match:
            continue

        tier_name = tier_match.group(1)

        # Find all sponsors in this tier section (#### N. Name format)
        sponsor_pattern = r'#### (\d+)\.\s*([^\n]+)\n(.*?)(?=#### |\Z)'
        sponsor_matches = re.finditer(sponsor_pattern, tier_section, re.DOTALL)

        for sponsor_match in sponsor_matches:
            sponsor_name = sponsor_match.group(2).strip()
            sponsor_block = sponsor_match.group(3)

            sponsor = _parse_sponsor_section(sponsor_name, sponsor_block, tier_name)
            if sponsor:
                sponsors.append(sponsor)

    return sponsors


def _parse_sponsor_section(sponsor_name, section, tier_name):
    """Parse individual sponsor section from markdown"""
    sponsor = {
        'name': sponsor_name.strip(),
        'type': 'Foundation',  # Default type
        'tier': tier_name,
        'contact': {},
        'giving': {},
        'relevance_score': None,
        'quality_score': None,
        'mission_alignment': None,
        'application_strategy': None,
        'last_verified': None,
    }

    # Extract Quality Score (e.g., "**Quality Score:** 9.5/10")
    quality_match = re.search(r'\*\*Quality Score:\*\*\s*([\d.]+)', section)
    if quality_match:
        try:
            sponsor['quality_score'] = float(quality_match.group(1))
            sponsor['relevance_score'] = float(quality_match.group(1))
        except ValueError:
            pass

    # Extract Website URL
    website_match = re.search(r'Website:\s*(https?://[^\s\-\*]+)', section)
    if website_match:
        sponsor['contact']['website'] = website_match.group(1).strip()

    # Extract Giving History (e.g., "**Giving History:** $250K-$500K+")
    giving_match = re.search(r'\*\*Giving History:\*\*\s*(.+?)(?=\n\*\*|---)', section, re.DOTALL)
    if giving_match:
        sponsor['giving']['range'] = giving_match.group(1).strip()

    # Extract Recommendation as application strategy
    recommendation_match = re.search(r'\*\*Recommendation:\*\*\s*(.+?)(?=\n\*\*|---|\n$)', section, re.DOTALL)
    if recommendation_match:
        sponsor['application_strategy'] = recommendation_match.group(1).strip()

    # Extract mission alignment from various possible field names
    mission_match = re.search(
        r'(?:Mental Health Focus|Focus Areas|Geographic Focus|Giving Capacity):\s*(.+?)(?=\n[-\*]|\n$)',
        section,
        re.IGNORECASE | re.DOTALL
    )
    if mission_match:
        sponsor['mission_alignment'] = mission_match.group(1).strip()

    # Infer organization type from content
    if any(word in section.lower() for word in ['foundation', 'trust', 'fund']):
        sponsor['type'] = 'Foundation'
    elif 'corporation' in section.lower() or 'company' in section.lower():
        sponsor['type'] = 'Corporation'
    elif 'nonprofit' in section.lower() or 'ngo' in section.lower():
        sponsor['type'] = 'NGO'

    return sponsor if sponsor.get('name') else None


def parse_json_file(file_path):
    """Parse sponsor data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'sponsors' in data:
        return data['sponsors']
    elif isinstance(data, dict) and 'results' in data:
        return data['results']
    else:
        return []


# Export
__all__ = ['parse_markdown_report', 'parse_json_file']
