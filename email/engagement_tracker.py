"""
Engagement Tracker for Email Campaigns

Queries Salesforce for email metrics and analyzes engagement.
Calculates scores, classifies leads, and generates reports.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class EngagementTracker:
    """Track and analyze email engagement from Salesforce"""

    def __init__(self, salesforce_client):
        """
        Initialize engagement tracker

        Args:
            salesforce_client: Instance of SalesforceClient or SalesforceEmailSender
        """
        self.sf = salesforce_client.sf
        self.client = salesforce_client

        # Load configuration from environment
        self.tracking_enabled = os.getenv('ENGAGEMENT_TRACKING_ENABLED', 'true').lower() == 'true'
        self.report_path = os.getenv('ENGAGEMENT_REPORT_PATH', 'docs/engagement_report.md')
        self.hot_leads_path = os.getenv('HOT_LEADS_EXPORT_PATH', 'docs/hot_leads.json')

        logger.info("Engagement tracker initialized")

    def get_email_activities(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Query email activities from Salesforce

        SOQL Query:
        SELECT Id, WhoId, Subject, Status, ActivityDate, Description
        FROM Task
        WHERE Type = 'Email'
        AND ActivityDate >= LAST_N_DAYS:30

        Args:
            days_back: Number of days to look back (default: 30)

        Returns:
            List of email activity records
        """
        try:
            query = f"""
                SELECT Id, WhoId, Subject, Status, ActivityDate, Description, TaskSubtype
                FROM Task
                WHERE TaskSubtype = 'Email'
                AND ActivityDate >= LAST_N_DAYS:{days_back}
                ORDER BY ActivityDate DESC
            """

            result = self.sf.query(query)
            activities = result['records']

            logger.info(f"Retrieved {len(activities)} email activities from last {days_back} days")
            return activities

        except Exception as e:
            logger.error(f"Failed to query email activities: {str(e)[:200]}")
            return []

    def get_lead_email_activities(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get email activities for a specific lead

        Args:
            lead_id: Salesforce Lead ID

        Returns:
            List of email activity records for the lead
        """
        try:
            query = f"""
                SELECT Id, WhoId, Subject, Status, ActivityDate, Description, TaskSubtype
                FROM Task
                WHERE TaskSubtype = 'Email'
                AND WhoId = '{lead_id}'
                ORDER BY ActivityDate DESC
            """

            result = self.sf.query(query)
            activities = result['records']

            logger.debug(f"Retrieved {len(activities)} email activities for Lead {lead_id}")
            return activities

        except Exception as e:
            logger.error(f"Failed to query activities for Lead {lead_id}: {str(e)[:100]}")
            return []

    def calculate_engagement_score(self, lead_id: str) -> int:
        """
        Calculate 0-100 engagement score for a lead

        Simplified Scoring (Phase 1):
        - Email sent: 0 points (baseline)
        - No response: 0 points
        - Got reply: 80 points
        - Same-day reply: +10 bonus (90 total)
        - Next-day reply: +5 bonus (85 total)

        Future Enhancement (Phase 2):
        - Email opened: 40 points
        - Link clicked: 40 points
        - Responded: 20 points

        Args:
            lead_id: Salesforce Lead ID

        Returns:
            int (0-100)
        """
        activities = self.get_lead_email_activities(lead_id)

        if not activities:
            return 0

        score = 0
        has_response = False
        send_date = None
        response_date = None

        # Analyze activities
        for activity in activities:
            status = activity.get('Status', '').lower()
            activity_date_str = activity.get('ActivityDate')

            # Parse activity date
            if activity_date_str:
                try:
                    activity_date = datetime.strptime(activity_date_str, '%Y-%m-%d')
                except:
                    activity_date = None

                # Track send date (first email)
                if not send_date:
                    send_date = activity_date

                # Check for response indicators
                if any(indicator in status for indicator in ['completed', 'responded', 'reply', 'answered']):
                    has_response = True
                    response_date = activity_date
                    break

        # Calculate score
        if has_response:
            score = 80  # Base score for response

            # Add bonus for quick response
            if send_date and response_date:
                days_to_respond = (response_date - send_date).days

                if days_to_respond == 0:
                    score += 10  # Same-day response bonus
                elif days_to_respond == 1:
                    score += 5  # Next-day response bonus

        return min(score, 100)  # Cap at 100

    def classify_leads(self, leads_with_scores: List[Dict[str, Any]]) -> Dict[str, List]:
        """
        Classify leads by engagement level

        Classification:
        - Hot: Score 70-100
        - Warm: Score 40-69
        - Cold: Score 0-39

        Args:
            leads_with_scores: List of dicts with 'lead_id', 'company_name', 'score'

        Returns:
            {
                'hot': [],    # Score 70-100
                'warm': [],   # Score 40-69
                'cold': []    # Score 0-39
            }
        """
        classified = {
            'hot': [],
            'warm': [],
            'cold': []
        }

        for lead in leads_with_scores:
            score = lead.get('score', 0)

            if score >= 70:
                classified['hot'].append(lead)
            elif score >= 40:
                classified['warm'].append(lead)
            else:
                classified['cold'].append(lead)

        # Sort each category by score (descending)
        for category in classified:
            classified[category].sort(key=lambda x: x.get('score', 0), reverse=True)

        logger.info(
            f"Classified leads: {len(classified['hot'])} hot, "
            f"{len(classified['warm'])} warm, {len(classified['cold'])} cold"
        )

        return classified

    def analyze_campaign_performance(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze overall campaign performance

        Args:
            days_back: Number of days to analyze

        Returns:
            Dict with campaign metrics
        """
        activities = self.get_email_activities(days_back)

        # Calculate metrics
        total_sent = len(activities)
        total_responded = sum(
            1 for act in activities
            if any(ind in act.get('Status', '').lower() for ind in ['completed', 'responded', 'reply', 'answered'])
        )

        response_rate = (total_responded / total_sent * 100) if total_sent > 0 else 0

        # Get unique leads contacted
        unique_leads = set(act.get('WhoId') for act in activities if act.get('WhoId'))

        # Calculate engagement scores for all leads
        leads_with_scores = []
        for lead_id in unique_leads:
            try:
                # Get lead company name
                lead = self.sf.Lead.get(lead_id)
                company_name = lead.get('Company', 'Unknown')
                email = lead.get('Email', 'No email')

                score = self.calculate_engagement_score(lead_id)

                leads_with_scores.append({
                    'lead_id': lead_id,
                    'company_name': company_name,
                    'email': email,
                    'score': score
                })
            except Exception as e:
                logger.warning(f"Failed to process lead {lead_id}: {str(e)[:100]}")
                continue

        # Classify leads
        classified = self.classify_leads(leads_with_scores)

        return {
            'campaign_metrics': {
                'total_emails_sent': total_sent,
                'total_responded': total_responded,
                'response_rate': round(response_rate, 2),
                'unique_leads_contacted': len(unique_leads),
                'days_analyzed': days_back
            },
            'lead_classification': {
                'hot_count': len(classified['hot']),
                'warm_count': len(classified['warm']),
                'cold_count': len(classified['cold'])
            },
            'hot_leads': classified['hot'],
            'warm_leads': classified['warm'],
            'cold_leads': classified['cold']
        }

    def generate_engagement_report(self, output_path: Optional[str] = None, days_back: int = 30) -> str:
        """
        Generate markdown report with engagement analysis

        Args:
            output_path: Path to save report (default: from env or docs/engagement_report.md)
            days_back: Number of days to analyze

        Returns:
            Path to generated report
        """
        if output_path is None:
            output_path = self.report_path

        logger.info(f"Generating engagement report for last {days_back} days...")

        # Analyze campaign performance
        analysis = self.analyze_campaign_performance(days_back)

        # Generate report
        report = self._format_engagement_report(analysis)

        # Write to file
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

            logger.info(f"[OK] Engagement report saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[ERROR] Failed to write report: {str(e)}")
            raise

    def _format_engagement_report(self, analysis: Dict[str, Any]) -> str:
        """Format engagement analysis as markdown report"""
        metrics = analysis['campaign_metrics']
        classification = analysis['lead_classification']
        hot_leads = analysis['hot_leads']
        warm_leads = analysis['warm_leads']
        cold_leads = analysis['cold_leads']

        report = f"""# Email Campaign Engagement Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Campaign Performance Summary

| Metric | Value |
|--------|-------|
| Total Emails Sent | {metrics['total_emails_sent']} |
| Total Responses | {metrics['total_responded']} |
| Response Rate | {metrics['response_rate']}% |
| Unique Leads Contacted | {metrics['unique_leads_contacted']} |
| Analysis Period | Last {metrics['days_analyzed']} days |

---

## Lead Classification

| Category | Count | Percentage |
|----------|-------|------------|
| HOT (70-100) | {classification['hot_count']} | {(classification['hot_count']/metrics['unique_leads_contacted']*100) if metrics['unique_leads_contacted'] > 0 else 0:.1f}% |
| WARM (40-69) | {classification['warm_count']} | {(classification['warm_count']/metrics['unique_leads_contacted']*100) if metrics['unique_leads_contacted'] > 0 else 0:.1f}% |
| COLD (0-39) | {classification['cold_count']} | {(classification['cold_count']/metrics['unique_leads_contacted']*100) if metrics['unique_leads_contacted'] > 0 else 0:.1f}% |

---

## HOT LEADS (Priority Follow-Up)

**Engagement Score: 70-100**
These leads have responded to outreach and show high engagement. Priority action required.

"""

        if hot_leads:
            for i, lead in enumerate(hot_leads, 1):
                report += f"{i}. **{lead['company_name']}**\n"
                report += f"   - Score: {lead['score']}/100\n"
                report += f"   - Email: {lead['email']}\n"
                report += f"   - Lead ID: {lead['lead_id']}\n"
                report += f"   - Action: Schedule follow-up meeting immediately\n\n"
        else:
            report += "*No hot leads at this time.*\n\n"

        report += "---\n\n## WARM LEADS\n\n"
        report += "**Engagement Score: 40-69**\n"
        report += "These leads show moderate engagement. Monitor and nurture.\n\n"

        if warm_leads:
            for i, lead in enumerate(warm_leads[:10], 1):  # Show top 10
                report += f"{i}. {lead['company_name']} (Score: {lead['score']}/100)\n"
            if len(warm_leads) > 10:
                report += f"\n*...and {len(warm_leads) - 10} more*\n"
        else:
            report += "*No warm leads at this time.*\n"

        report += "\n---\n\n## COLD LEADS (Re-Engagement Needed)\n\n"
        report += "**Engagement Score: 0-39**\n"
        report += "These leads have not responded. Consider follow-up campaign or alternate contact methods.\n\n"

        if cold_leads:
            report += f"Total cold leads: {len(cold_leads)}\n\n"
            report += "**Sample (first 10):**\n"
            for i, lead in enumerate(cold_leads[:10], 1):
                report += f"{i}. {lead['company_name']} (Score: {lead['score']}/100)\n"
            if len(cold_leads) > 10:
                report += f"\n*...and {len(cold_leads) - 10} more*\n"
        else:
            report += "*No cold leads at this time.*\n"

        report += "\n---\n\n## Recommended Actions\n\n"
        report += "1. **HOT LEADS**: Schedule immediate follow-up meetings\n"
        report += "2. **WARM LEADS**: Send personalized check-in emails\n"
        report += "3. **COLD LEADS**: Launch re-engagement campaign with different messaging\n"
        report += "4. **Data Quality**: Update contact information for leads with no email\n\n"

        report += "---\n\n"
        report += "*Report generated by CSOAF Sponsor Finder - Email Campaign System*\n"

        return report

    def export_hot_leads_json(self, output_path: Optional[str] = None, days_back: int = 30) -> str:
        """
        Export hot leads to JSON for easy import/processing

        Args:
            output_path: Path to save JSON (default: from env or docs/hot_leads.json)
            days_back: Number of days to analyze

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.hot_leads_path

        logger.info("Exporting hot leads to JSON...")

        # Analyze campaign performance
        analysis = self.analyze_campaign_performance(days_back)
        hot_leads = analysis['hot_leads']

        # Prepare export data
        export_data = {
            'export_date': datetime.now().isoformat(),
            'days_analyzed': days_back,
            'hot_leads_count': len(hot_leads),
            'leads': hot_leads
        }

        # Write to file
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"[OK] Hot leads exported: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[ERROR] Failed to export hot leads: {str(e)}")
            raise


# Export
__all__ = ['EngagementTracker']
