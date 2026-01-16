"""
Email Template Generator for Sponsor Outreach

Generates personalized email content for each sponsor type with token replacement.
Supports Foundation, Corporation, NGO, and Government templates.
"""

from typing import Dict, Any


# Template definitions by sponsor type
TEMPLATES = {
    'foundation': {
        'subject': 'Partnership Opportunity: Arts Education for Students with Disabilities',
        'body': '''Dear {{Contact_Name}},

I hope this message finds you well. I'm reaching out on behalf of the Community School of the Arts Foundation (CSOAF), a nonprofit organization dedicated to unlocking creative educational pathways for students with disabilities.

We've identified {{Organization_Name}} as an exceptional partner whose mission aligns closely with our work in arts education and community healing. Your support for {{Mission_Alignment}} resonates deeply with our programs.

**About CSOAF:**
Since 2003, we've provided accessible dance and creative arts instruction to K-12 students with moderate to severe disabilities in California and New York public schools. Our programs combine artistic enrichment with mental health support, creating pathways for self-expression and personal growth.

**Why This Partnership Matters:**
- We serve over 5 million supporters and have funded 68 projects to date
- Our programs specifically target students with disabilities in underserved communities
- 380 volunteers worldwide support our emerging artists
- Free educational opportunities for children and teens, with subscription-based services for broader reach

**Grant Request:**
We're seeking support in the {{Grant_Range}} range to expand our {{CSOAF_Program}} program. This investment would directly impact students who have limited access to creative arts education.

**Next Steps:**
{{Application_Strategy}}

I'd welcome the opportunity to discuss how {{Organization_Name}} and CSOAF can partner to create lasting impact for students with disabilities through the arts. Would you be available for a brief call in the coming weeks?

Thank you for considering this partnership opportunity.

Warm regards,

{{Email_Signature}}
'''
    },

    'corporation': {
        'subject': 'CSR Partnership: Community Impact Through Arts Education',
        'body': '''Dear {{Contact_Name}},

I'm reaching out to explore a corporate social responsibility partnership between {{Organization_Name}} and the Community School of the Arts Foundation (CSOAF).

**Aligned Corporate Values:**
Your company's commitment to {{Mission_Alignment}} mirrors our mission to provide accessible arts education for students with disabilities. We believe this creates a natural partnership opportunity.

**About Our Impact:**
CSOAF serves K-12 students with moderate to severe disabilities in California and New York public schools. Since 2003, we've built a community of 5 million supporters and 380 volunteers worldwide, delivering dance and creative arts programs that combine education with mental health support.

**Partnership Benefits for {{Organization_Name}}:**
- **Community Impact**: Direct support for underserved students with disabilities
- **Employee Engagement**: Volunteer opportunities for team building and giving back
- **Brand Alignment**: Association with arts education and inclusive programming
- **Measurable Outcomes**: Clear metrics on student participation and program growth

**Investment Opportunity:**
We're seeking corporate partners in the {{Grant_Range}} range to support our {{CSOAF_Program}} program. This funding would enable us to expand our reach and deepen our impact.

**Recommended Action:**
{{Application_Strategy}}

I'd be delighted to schedule a meeting to discuss how this partnership can advance {{Organization_Name}}'s CSR goals while transforming lives through the arts.

Thank you for your consideration.

Best regards,

{{Email_Signature}}
'''
    },

    'ngo': {
        'subject': 'Collaboration Opportunity: Expanding Arts Access Together',
        'body': '''Dear {{Contact_Name}},

I'm writing to explore a collaborative partnership between {{Organization_Name}} and the Community School of the Arts Foundation (CSOAF).

**Shared Mission:**
Both our organizations are committed to {{Mission_Alignment}}. We believe that by joining forces, we can amplify our impact and reach more students who need accessible arts education.

**About CSOAF:**
We've been unlocking creative educational pathways for students with disabilities since 2003. Our programs serve K-12 students with moderate to severe disabilities in California and New York, combining dance and creative arts instruction with mental health support.

**Collaboration Opportunities:**
- **Program Co-Development**: Design joint initiatives that leverage both organizations' strengths
- **Resource Sharing**: Combine expertise, volunteers, and networks
- **Joint Fundraising**: Pursue collaborative grants and funding opportunities
- **Knowledge Exchange**: Share best practices and program innovations

**Current Need:**
We're seeking partnership support in the {{Grant_Range}} range to expand our {{CSOAF_Program}} program. This would allow us to:
- Reach more students with disabilities
- Develop new curriculum materials
- Train additional teaching artists
- Expand to new school districts

**Next Steps:**
{{Application_Strategy}}

I believe our organizations can achieve more together than separately. Would you be interested in a conversation about potential collaboration?

Looking forward to connecting.

Sincerely,

{{Email_Signature}}
'''
    },

    'government': {
        'subject': 'Program Partnership: Mental Health Through Arts Education',
        'body': '''Dear {{Contact_Name}},

I'm writing to introduce the Community School of the Arts Foundation (CSOAF) and explore partnership opportunities with {{Organization_Name}}.

**Public Benefit Alignment:**
Our mission to provide accessible arts education for students with disabilities aligns with {{Mission_Alignment}}. We deliver measurable outcomes that address critical public priorities: educational equity, mental health support, and inclusive programming.

**Program Overview:**
Since 2003, CSOAF has served K-12 students with moderate to severe disabilities in California and New York public schools. Our evidence-based programs combine:
- Creative arts instruction (dance, visual arts, music)
- Mental health support through artistic expression
- Inclusive learning environments
- Professional teaching artist instruction

**Measurable Impact:**
- 5 million supporters engaged since founding
- 68 projects funded and completed
- 380 trained volunteers supporting program delivery
- Partnerships with public school systems in CA and NY

**Funding Request:**
We're seeking {{Grant_Range}} in support to expand our {{CSOAF_Program}} program. This investment would:
- Expand services to additional school districts
- Increase student capacity by [specific number]
- Develop assessment tools for program evaluation
- Create replicable models for other communities

**Application Process:**
{{Application_Strategy}}

**Compliance & Accountability:**
We maintain rigorous financial oversight, program evaluation, and reporting practices. We're prepared to meet all requirements for government partnership including:
- Detailed budget justification
- Outcome measurement and reporting
- Audit compliance
- Program evaluation data

I'd welcome the opportunity to discuss how CSOAF can support {{Organization_Name}}'s mission to serve students with disabilities through high-quality arts education.

Thank you for your consideration.

Respectfully,

{{Email_Signature}}
'''
    }
}


def generate_sponsor_email(sponsor_data: Dict[str, Any], template_type: str = None) -> Dict[str, Any]:
    """
    Generate personalized email for a sponsor

    Args:
        sponsor_data: Dict with sponsor info from parser
            Expected fields: name, type, tier, contact, giving, relevance_score,
            quality_score, mission_alignment, application_strategy
        template_type: Override template type (default: auto-detect from sponsor_data['type'])

    Returns:
        {
            'subject': str,
            'body': str,
            'tokens': dict,  # Variables used for personalization
            'template_type': str
        }
    """
    # Determine template type
    if template_type is None:
        sponsor_type = sponsor_data.get('type', 'Foundation').lower()
        template_type = get_template_type_from_sponsor_type(sponsor_type)

    # Get template
    template = TEMPLATES.get(template_type.lower())
    if not template:
        # Default to foundation template
        template = TEMPLATES['foundation']
        template_type = 'foundation'

    # Build token dictionary
    tokens = build_token_dict(sponsor_data)

    # Replace tokens in subject and body
    subject = replace_tokens(template['subject'], tokens)
    body = replace_tokens(template['body'], tokens)

    return {
        'subject': subject,
        'body': body,
        'tokens': tokens,
        'template_type': template_type
    }


def get_template_type_from_sponsor_type(sponsor_type: str) -> str:
    """
    Map sponsor type to template type

    Args:
        sponsor_type: Sponsor type from categorization (Foundation, Corporation, NGO, Government)

    Returns:
        Template type key (foundation, corporation, ngo, government)
    """
    sponsor_type_lower = sponsor_type.lower()

    if 'corporation' in sponsor_type_lower or 'company' in sponsor_type_lower:
        return 'corporation'
    elif 'ngo' in sponsor_type_lower or 'nonprofit' in sponsor_type_lower:
        return 'ngo'
    elif 'government' in sponsor_type_lower or 'agency' in sponsor_type_lower or 'municipal' in sponsor_type_lower:
        return 'government'
    else:
        # Default to foundation
        return 'foundation'


def build_token_dict(sponsor_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Build dictionary of token values from sponsor data

    Args:
        sponsor_data: Sponsor information dict

    Returns:
        Dict of token names to values
    """
    # Extract contact info
    contact = sponsor_data.get('contact', {})
    contact_name = contact.get('name', 'Development Team')

    # Parse first name from contact name for personalization
    first_name = contact_name.split()[0] if contact_name and contact_name != 'Development Team' else 'Development Team'

    # Build grant range display
    giving = sponsor_data.get('giving', {})
    grant_range = giving.get('range', '$50K-$250K')

    # Mission alignment (sanitize to avoid None)
    mission_alignment = sponsor_data.get('mission_alignment') or 'arts education and community programs'

    # Application strategy
    application_strategy = sponsor_data.get('application_strategy') or 'We recommend submitting a Letter of Inquiry (LOI) to initiate the conversation.'

    # CSOAF program to highlight (based on tier and focus)
    csoaf_program = get_recommended_program(sponsor_data)

    # Email signature
    email_signature = get_email_signature()

    return {
        'Organization_Name': sponsor_data.get('name', 'Your Organization'),
        'Contact_Name': first_name,
        'Tier': sponsor_data.get('tier', 'Tier 2'),
        'Grant_Range': grant_range,
        'Mission_Alignment': mission_alignment,
        'Application_Strategy': application_strategy,
        'CSOAF_Program': csoaf_program,
        'Email_Signature': email_signature
    }


def get_recommended_program(sponsor_data: Dict[str, Any]) -> str:
    """
    Recommend specific CSOAF program to highlight based on sponsor data

    Args:
        sponsor_data: Sponsor information

    Returns:
        Program name/description to highlight
    """
    tier = sponsor_data.get('tier', '').upper()
    mission = (sponsor_data.get('mission_alignment') or '').lower()

    # Tier 1A/1B sponsors: flagship programs
    if 'TIER 1A' in tier or 'TIER 1B' in tier:
        if 'mental health' in mission or 'healing' in mission:
            return 'Arts for Healing and Mental Wellness'
        elif 'dance' in mission:
            return 'Inclusive Dance Education'
        else:
            return 'Comprehensive Creative Arts for Students with Disabilities'

    # Tier 2 sponsors: specific programs
    if 'dance' in mission:
        return 'Dance Education Program'
    elif 'mental health' in mission:
        return 'Arts-Based Mental Health Support'
    elif 'adult' in mission:
        return 'Adult Learning Classes (Online and In-Person)'
    else:
        return 'K-12 Creative Arts Instruction'


def get_email_signature() -> str:
    """
    Get email signature for outreach emails

    Returns:
        Formatted email signature
    """
    return '''Jamee Ra
Development Director
Community School of the Arts Foundation
Phone: (555) 555-5555
Email: jameera@csoafmail.org
Website: www.csoaf.org'''


def replace_tokens(template: str, tokens: Dict[str, str]) -> str:
    """
    Replace {{Variable}} tokens with actual values

    Args:
        template: Template string with {{Token}} placeholders
        tokens: Dict mapping token names to values

    Returns:
        Template with tokens replaced
    """
    result = template
    for token_name, token_value in tokens.items():
        placeholder = f'{{{{{token_name}}}}}'
        result = result.replace(placeholder, str(token_value))

    return result


def get_all_template_types() -> list:
    """Get list of all available template types"""
    return list(TEMPLATES.keys())


def preview_template(template_type: str, sample_sponsor: Dict[str, Any] = None) -> str:
    """
    Preview a template with sample data

    Args:
        template_type: Type of template to preview
        sample_sponsor: Optional sample sponsor data (uses default if not provided)

    Returns:
        Formatted preview string
    """
    if sample_sponsor is None:
        sample_sponsor = {
            'name': 'Sample Foundation',
            'type': template_type.capitalize(),
            'tier': 'Tier 1A',
            'contact': {
                'name': 'John Smith',
                'email': 'john@example.org'
            },
            'giving': {
                'range': '$100K-$500K'
            },
            'mission_alignment': 'arts education and community development',
            'application_strategy': 'Submit LOI through online portal by March 15, 2026'
        }

    email = generate_sponsor_email(sample_sponsor, template_type=template_type)

    preview = f"""
Template Type: {template_type.upper()}
{'='*70}

Subject: {email['subject']}

{'='*70}

{email['body']}

{'='*70}
Tokens Used:
"""
    for token, value in email['tokens'].items():
        preview += f"  {token}: {value[:50]}{'...' if len(str(value)) > 50 else ''}\n"

    return preview


# Export public API
__all__ = [
    'generate_sponsor_email',
    'get_template_type_from_sponsor_type',
    'get_all_template_types',
    'preview_template',
    'replace_tokens',
    'TEMPLATES'
]
