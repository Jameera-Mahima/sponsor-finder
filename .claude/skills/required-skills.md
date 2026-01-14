# Required Skills for Sponsor-Finder Project

This document outlines the skills needed to develop, maintain, and operate the AI-powered sponsor search system for the Community School of the Arts Foundation (CSOAF).

## Technical Skills

### AI/LLM Development

#### Claude API & Agent Orchestration
- Building multi-agent workflows using Claude Code's agent system
- Coordinating sequential execution across 4-phase workflow (keyword extraction → research → categorization → validation)
- Managing agent communication and data passing between phases
- Selecting appropriate models (Haiku 4.5 for speed, Sonnet 4.5 for quality)

#### Prompt Engineering
- Designing effective prompts for specialized tasks:
  - Keyword extraction from campaign descriptions and mission statements
  - Web research with relevance scoring
  - Sponsor categorization into types (Foundations/Corporations/NGOs/Government)
  - Data quality validation and verification
- Iterating on prompts to improve accuracy and reduce hallucinations
- Balancing specificity with flexibility in agent instructions

#### Agent Design
- Creating specialized agent definitions in `.claude/agents/`:
  - `keyword-extractor` - Extracting search terms from user prompts
  - `web-researcher` - Finding sponsors through web search
  - `categorizer` - Organizing sponsors by type
  - `validator` - Quality scoring and verification
- Defining agent roles, allowed tools, and model selection
- Testing agents with diverse inputs and edge cases

### Data Processing & Analysis

#### Web Scraping & Research
- Automated sponsor discovery using web search
- Extracting structured data from unstructured web content
- Validating organization legitimacy through online presence verification
- Finding contact information (websites, emails, phone numbers)

#### Data Validation
- Implementing quality scoring systems (1-10 scale)
- Verifying active giving programs (grants in last 2 years)
- Cross-referencing multiple sources for accuracy
- Detecting false positives and filtering out non-sponsors

#### Structured Data Formats
- **JSON**: Structured output for programmatic access
- **CSV**: Spreadsheet-compatible format for CRM import
- **Markdown**: Human-readable reports with rankings and analysis
- Converting between formats based on user needs

### Integration Skills

#### Salesforce
- **Contact Management**: Importing sponsor lists to central CRM database
- **Email Campaign Execution**: Sending personalized outreach emails
- **Analytics**: Tracking opens, clicks, and responses
- **Report Generation**: Creating dashboards for marketing team
- **Meeting Coordination**: Scheduling follow-ups with interested prospects

#### Mailchimp
- Accessing historical donor data from past campaigns
- Syncing contact lists with Salesforce
- Analyzing donor behavior patterns across campaigns
- Migrating data to primary CRM system

#### Luma/Eventbrite
- **Event Registration**: Tracking participant sign-ups
- **Attendance Monitoring**: Recording who actually attends events
- **Follow-up Workflows**: Post-event communication automation
- **Data Sync**: Sending participant data to Salesforce

#### GiveLively
- Campaign page management and customization
- Online donation processing and tracking
- Fundraising goal monitoring and progress updates
- Donor information collection and CRM integration

#### API Integration
- Building webhooks and API connections between platforms
- Ensuring unified data flow: Historical Data (Mailchimp) → Event Data (Luma) → Donations (GiveLively) → Central Hub (Salesforce)
- Handling authentication, rate limits, and error handling
- Maintaining data consistency across systems

## Domain Knowledge

### Fundraising & Nonprofit Operations

#### Grant Research
- Understanding foundation giving priorities and application processes
- Identifying corporate philanthropy programs and CSR initiatives
- Researching government grants (NEA, state arts councils, NYC/NY/CA programs)
- Tracking funding cycles and deadlines

#### Donor Prospecting
- Ranking prospects by:
  - **Past giving history**: Donation amounts and frequency
  - **Mission alignment**: Match with CSOAF's focus areas
  - **Geographic relevance**: NYC/NY/CA presence and funding patterns
- Segmenting donors by capacity and likelihood to give
- Building cultivation strategies for different donor types

#### Campaign Management
- Planning seasonal campaigns (e.g., Christmas education campaign)
- Setting realistic fundraising goals ($500K target, 500 sponsors)
- Coordinating multi-channel outreach (email, events, online donations)
- Measuring campaign ROI and effectiveness

#### CRM Best Practices
- Database hygiene and contact deduplication
- Segmentation strategies for personalized outreach
- Lead scoring and prioritization
- Donor journey mapping from prospect to contributor

### Arts Education & Disability Services

#### Mission Alignment
Understanding CSOAF's core focus areas:
- **Arts Education**: Dance classes, creative arts instruction, K-12 programs
- **Disability Services**: Programs for students with moderate to severe disabilities
- **Accessibility**: Inclusive learning environments for all types of learners
- **Community Healing**: Mental health support through arts
- **Adult Education**: Lifelong learning and professional development

#### Sector Knowledge
Knowing which organizations fund:
- Arts education and cultural enrichment initiatives
- Special education and disability services
- Accessibility improvements and inclusive programming
- Community-based youth development programs
- Mental health and wellness through creative arts

#### Geographic Targeting
- **New York**: NYC public schools, state foundations, local corporate sponsors
- **California**: Public school systems, Bay Area tech companies, CA-based foundations
- Understanding regional giving patterns and philanthropic ecosystems
- Identifying local community foundations and United Ways

## Analytical Skills

### Research & Qualification

#### Web Research
- Efficiently searching for foundation websites and giving programs
- Verifying organization legitimacy (IRS 990s, Guidestar, Foundation Directory)
- Finding decision-maker contact information
- Identifying recent grant announcements and recipients

#### Relevance Scoring
Evaluating sponsors on multiple criteria:
- **Mission alignment** (0-10): How well does their focus match CSOAF's programs?
- **Geographic fit** (0-10): Do they fund in NYC/NY or California?
- **Giving capacity** (0-10): Grant size matches $50K+ target?
- **Accessibility** (0-10): How easy to apply? Do they accept unsolicited proposals?

#### Data Quality Assessment
Ensuring high-quality results:
- All sponsors have verified websites and contact information
- Active giving programs with grants awarded in last 2 years
- No false positives (consultants posing as foundations, defunct organizations)
- Validation score ≥5 for inclusion in final results

### Campaign Analytics

#### Email Metrics
- **Open rates**: Measuring initial interest in outreach
- **Click-through rates**: Tracking engagement with campaign links
- **Response rates**: Monitoring replies and inquiries
- **Conversion rates**: Measuring donation/sponsorship commitments

#### Donor Behavior
- Analyzing giving patterns (seasonal trends, average gift size)
- Identifying loyal donors vs. one-time contributors
- Tracking donor retention and churn rates
- Predicting likelihood to give based on past behavior

#### ROI Analysis
- Calculating cost per donor acquired
- Measuring revenue per email sent or event hosted
- Comparing campaign performance across channels
- Identifying highest-value outreach strategies

## Communication Skills

### Stakeholder Management

#### Marketing Coordination
- Sharing engagement reports with marketing team
- Identifying high-priority prospects for personal outreach
- Coordinating meeting scheduling with interested sponsors
- Aligning messaging across email, events, and online channels

#### Report Generation
Creating actionable insights:
- Executive summaries highlighting top prospects
- Detailed sponsor profiles with contact info and giving history
- Campaign performance dashboards with key metrics
- Recommendations for follow-up actions

#### Personalized Outreach
Crafting targeted messages based on:
- **Organization type**: Foundations vs. corporations vs. government
- **Past giving**: Referencing similar grants they've made
- **Mission alignment**: Emphasizing shared values and impact
- **Geographic connection**: Highlighting local community impact

### Documentation

#### Technical Documentation
- System architecture diagrams showing 4-phase workflow
- Agent definition specifications with roles and tools
- Integration documentation for Salesforce, Mailchimp, Luma, GiveLively
- Troubleshooting guides for common issues

#### User Guides
- Step-by-step instructions for running sponsor searches
- How to interpret relevance scores and rankings
- Exporting results to CSV for CRM import
- Best practices for search prompts and keywords

## Priority Ranking

### Most Critical (Must Have)
1. **Claude API/Agent Development**: Core system functionality depends on this
2. **Salesforce CRM Expertise**: Central hub for all campaign operations
3. **Nonprofit Fundraising Knowledge**: Understanding donor behavior and grant processes
4. **Web Research & Data Validation**: Ensuring high-quality, accurate sponsor lists

### Important (Should Have)
5. **Integration Development**: Connecting platforms for unified workflows
6. **Campaign Analytics**: Measuring effectiveness and optimizing strategies
7. **Arts Education/Disability Sector Knowledge**: Mission-specific alignment

### Nice to Have
8. **Advanced Prompt Engineering**: Optimizing agent performance
9. **Event Management**: Supporting fundraising events with Luma/Eventbrite
10. **Data Science**: Predictive modeling for donor likelihood

## Skill Development Roadmap

### Phase 1: Foundation (Weeks 1-4)
- Learn Claude Code agent system and Task tool
- Master Salesforce basics (contact management, email campaigns)
- Study nonprofit fundraising fundamentals
- Practice web research and data validation techniques

### Phase 2: Integration (Weeks 5-8)
- Build API connections between platforms
- Implement data flow from research → CRM
- Test email campaign execution workflows
- Develop reporting dashboards

### Phase 3: Optimization (Weeks 9-12)
- Refine agent prompts based on results
- Improve relevance scoring algorithms
- Enhance data quality validation
- Optimize campaign analytics and insights

### Phase 4: Scale (Months 4-6)
- Automate repetitive tasks
- Build templates for common campaign types
- Create self-service tools for non-technical users
- Establish best practices and standard operating procedures

## Resources

### Learning Platforms
- **Claude API Documentation**: https://docs.anthropic.com
- **Salesforce Trailhead**: Free CRM training modules
- **Nonprofit Leadership Alliance**: Fundraising courses
- **Foundation Directory Online**: Grant research training

### Communities
- **Anthropic Discord**: Claude developers and prompt engineers
- **Salesforce Success Community**: CRM best practices
- **Association of Fundraising Professionals (AFP)**: Nonprofit networking
- **Arts Education Partnership**: Sector-specific knowledge

### Tools
- **Claude Code CLI**: Agent orchestration platform
- **Salesforce**: CRM and email campaign management
- **Mailchimp**: Email marketing and historical data
- **Luma/Eventbrite**: Event management
- **GiveLively**: Donation processing

## Next Steps

1. **Self-Assessment**: Evaluate your current skill level in each area
2. **Gap Analysis**: Identify skills needing development
3. **Learning Plan**: Create personalized roadmap based on priorities
4. **Hands-On Practice**: Start with small sponsor searches and iterate
5. **Feedback Loop**: Measure results and refine approach continuously
