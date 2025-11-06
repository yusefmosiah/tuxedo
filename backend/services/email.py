"""
Email service for sending transactional emails via SendGrid
Implements email templates for passkey authentication flows
"""
import os
import logging
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

# Email configuration from environment
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "no-reply@choir.chat")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Choir")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class EmailService:
    """Service for sending transactional emails"""

    def __init__(self):
        self.sg = SendGridAPIClient(SENDGRID_API_KEY) if SENDGRID_API_KEY else None
        if not self.sg:
            logger.warning("SendGrid API key not configured - emails will be logged to console only")

    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email via SendGrid"""
        try:
            if self.sg:
                message = Mail(
                    from_email=SENDGRID_FROM_EMAIL,
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_content
                )

                response = self.sg.send(message)

                if response.status_code == 202:
                    logger.info(f"Email sent successfully to {to_email}: {subject}")
                    return True
                else:
                    logger.warning(f"SendGrid response status: {response.status_code}")
                    return False
            else:
                # Development mode - log to console
                logger.info(f"[EMAIL] To: {to_email}")
                logger.info(f"[EMAIL] Subject: {subject}")
                logger.info(f"[EMAIL] Content: {html_content[:200]}...")
                return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_welcome_email(self, email: str, recovery_codes: List[str]) -> bool:
        """Send welcome email with recovery codes after registration"""
        recovery_codes_html = "<br>".join([f"<code style='background-color: #f4f4f4; padding: 4px 8px; border-radius: 4px; font-family: monospace;'>{code}</code>" for code in recovery_codes])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Choir</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; margin-bottom: 20px;">Welcome to Choir! 🎉</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    Your account has been created successfully. You can now use your passkey to sign in securely.
                </p>

                <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <h2 style="color: #856404; margin-top: 0;">⚠️ Important: Save Your Recovery Codes</h2>
                    <p style="color: #856404; margin-bottom: 15px;">
                        These recovery codes allow you to access your account if you lose your passkey.
                        <strong>Save them in a secure location - they will not be shown again!</strong>
                    </p>
                    <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 15px 0;">
                        {recovery_codes_html}
                    </div>
                    <p style="color: #856404; font-size: 14px; margin-bottom: 0;">
                        Each code can only be used once. Store them securely (password manager, secure note, etc.)
                    </p>
                </div>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">What's Next?</h3>
                    <ul style="color: #555;">
                        <li>Use your passkey to sign in quickly and securely</li>
                        <li>You can add multiple passkeys from your account settings</li>
                        <li>If you lose access, use a recovery code to sign in</li>
                        <li>Keep your recovery codes safe and accessible</li>
                    </ul>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Choir - AI-Powered Conversational Platform<br>
                        If you didn't create this account, please contact support immediately.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(email, "Welcome to Choir - Your Recovery Codes", html_content)

    async def send_recovery_alert(self, email: str, remaining_codes: int) -> bool:
        """Send security alert after recovery code use"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Alert - Recovery Code Used</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #dc3545; margin-bottom: 20px;">🔐 Security Alert</h1>

                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        A recovery code was just used to access your Choir account.
                    </p>
                </div>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Account Status</h3>
                    <p><strong>Remaining recovery codes:</strong> {remaining_codes} of 8</p>
                    {"<p style='color: #dc3545;'><strong>⚠️ Warning:</strong> You're running low on recovery codes. Consider adding a new passkey from your account settings.</p>" if remaining_codes <= 2 else ""}
                </div>

                <div style="background-color: #d1ecf1; border-left: 4px solid #0c5460; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">Was this you?</h3>
                    <p style="color: #0c5460; margin-bottom: 10px;">
                        If you used a recovery code to sign in, you can safely ignore this email.
                    </p>
                    <p style="color: #0c5460; margin: 0;">
                        If you did not authorize this, please secure your account immediately by visiting
                        <a href="{FRONTEND_URL}/account/security" style="color: #0c5460;">your security settings</a>.
                    </p>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Choir Security Team<br>
                        This is an automated security notification.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(email, "Security Alert: Recovery Code Used", html_content)

    async def send_recovery_link(self, email: str, token: str) -> bool:
        """Send email recovery link for lost passkeys + codes"""
        recovery_url = f"{FRONTEND_URL}/auth/recover?token={token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Choir Account Recovery</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; margin-bottom: 20px;">🔑 Account Recovery Request</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    You requested to recover your Choir account. Click the button below to create a new passkey and regain access.
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{recovery_url}"
                       style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;">
                        Recover Your Account
                    </a>
                </div>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>⏰ This link expires in 1 hour</strong>
                    </p>
                </div>

                <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #721c24; margin-top: 0;">Security Notice</h3>
                    <p style="color: #721c24; margin-bottom: 10px;">
                        When you complete recovery:
                    </p>
                    <ul style="color: #721c24; margin: 0;">
                        <li>All your old passkeys will be invalidated</li>
                        <li>You'll receive new recovery codes</li>
                        <li>You'll create a new passkey</li>
                    </ul>
                </div>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="color: #555; margin: 0;">
                        If you didn't request this recovery link, you can safely ignore this email.
                        Your account remains secure.
                    </p>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Choir Security Team<br>
                        If you're having trouble, contact support for assistance.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(email, "Choir Account Recovery Request", html_content)

    async def send_recovery_confirmation(self, email: str, recovery_codes: List[str]) -> bool:
        """Send confirmation after account recovery with new recovery codes"""
        recovery_codes_html = "<br>".join([f"<code style='background-color: #f4f4f4; padding: 4px 8px; border-radius: 4px; font-family: monospace;'>{code}</code>" for code in recovery_codes])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Recovered Successfully</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #28a745; margin-bottom: 20px;">✅ Account Recovered Successfully</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    Your Choir account has been recovered. You now have a new passkey and new recovery codes.
                </p>

                <div style="background-color: #d1ecf1; border-left: 4px solid #0c5460; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">Security Changes</h3>
                    <ul style="color: #0c5460; margin: 0;">
                        <li>All previous passkeys have been revoked</li>
                        <li>Previous recovery codes are no longer valid</li>
                        <li>A new passkey has been created</li>
                        <li>New recovery codes have been generated</li>
                    </ul>
                </div>

                <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <h2 style="color: #856404; margin-top: 0;">⚠️ Your New Recovery Codes</h2>
                    <p style="color: #856404; margin-bottom: 15px;">
                        <strong>Save these new codes in a secure location!</strong>
                    </p>
                    <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 15px 0;">
                        {recovery_codes_html}
                    </div>
                    <p style="color: #856404; font-size: 14px; margin-bottom: 0;">
                        Each code can only be used once. Store them securely.
                    </p>
                </div>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">What's Next?</h3>
                    <p style="color: #555;">
                        Your account is now secure and ready to use. You can add additional passkeys from your account settings for backup access.
                    </p>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Choir Security Team<br>
                        If you didn't perform this recovery, contact support immediately.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(email, "Your Choir Account Has Been Recovered", html_content)

    async def send_passkey_added_alert(self, email: str, friendly_name: str = None) -> bool:
        """Send alert when new passkey is added to account"""
        device_info = friendly_name or "Unknown device"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Passkey Added</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50; margin-bottom: 20px;">🔑 New Passkey Added</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    A new passkey was just added to your Choir account.
                </p>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Passkey Details</h3>
                    <p><strong>Device:</strong> {device_info}</p>
                    <p><strong>Date:</strong> Just now</p>
                </div>

                <div style="background-color: #d1ecf1; border-left: 4px solid #0c5460; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">Was this you?</h3>
                    <p style="color: #0c5460; margin-bottom: 10px;">
                        If you added this passkey, you can safely ignore this email.
                    </p>
                    <p style="color: #0c5460; margin: 0;">
                        If you did not authorize this, remove it immediately from
                        <a href="{FRONTEND_URL}/account/security" style="color: #0c5460;">your security settings</a>.
                    </p>
                </div>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Choir Security Team<br>
                        This is an automated security notification.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(email, "New Passkey Added to Your Account", html_content)


# Global email service instance
email_service = EmailService()
