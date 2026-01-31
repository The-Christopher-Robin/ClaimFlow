"""Notification service for Slack and Email."""
import httpx
from typing import Optional
from app.models import ClaimResponse
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via Slack and Email."""
    
    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        smtp_config: Optional[dict] = None
    ):
        self.slack_webhook_url = slack_webhook_url
        self.smtp_config = smtp_config or {}
    
    async def send_slack_notification(self, claim: ClaimResponse) -> bool:
        """Send Slack notification about the claim."""
        if not self.slack_webhook_url:
            logger.info("Slack webhook URL not configured, skipping Slack notification")
            return False
        
        message = {
            "text": f"New Claim Processed: {claim.claim_id}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚗 Claim {claim.claim_id} Processed"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Policy ID:*\n{claim.policy_info.policy_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{claim.payout_calculation.status.replace('_', ' ').title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Damage Type:*\n{claim.damage_analysis.damage_type.title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Payout:*\n${claim.payout_calculation.payout_amount:,.2f}"
                        }
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url,
                    json=message,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"Slack notification sent for claim {claim.claim_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def send_email_notification(self, claim: ClaimResponse, email: str) -> bool:
        """
        Send email notification (stub implementation).
        
        In production, this would use SMTP to send actual emails.
        """
        logger.info(f"[EMAIL STUB] Sending email to {email}")
        logger.info(f"[EMAIL STUB] Subject: Your Claim {claim.claim_id} Has Been Processed")
        logger.info(f"[EMAIL STUB] Payout Amount: ${claim.payout_calculation.payout_amount:,.2f}")
        logger.info(f"[EMAIL STUB] Status: {claim.payout_calculation.status}")
        
        # In production, would actually send email via SMTP
        # For now, just log it as a stub
        return True
    
    async def notify_all(self, claim: ClaimResponse, email: Optional[str] = None) -> dict:
        """Send all configured notifications."""
        results = {
            "slack": await self.send_slack_notification(claim),
            "email": await self.send_email_notification(claim, email or "customer@example.com")
        }
        return results
