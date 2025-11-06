"""
Email service for sending transactional emails via SendGrid
Handles passkey authentication-related emails
"""
import os
import logging
from typing import List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

# Email configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "no-reply@choir.chat")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Choir")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


async def send_welcome_email(email: str, recovery_codes: List[str]) -> bool:
    """Send welcome email with recovery codes after registration"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, skipping welcome email")
            logger.info(f"Welcome email would be sent to: {email}")
            logger.info(f"Recovery codes: {recovery_codes}")
            return True

        sg = SendGridAPIClient(SENDGRID_API_KEY)

        # Format recovery codes for email
        codes_html = "<ul style='list-style: none; padding: 0;'>"
        for i, code in enumerate(recovery_codes, 1):
            codes_html += f"<li style='font-family: monospace; font-size: 14px; padding: 5px; background: #f5f5f5; margin: 5px 0;'>{i}. {code}</li>"
        codes_html += "</ul>"

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
                <h1 style="color: #2c3e50; margin-bottom: 20px;">Welcome to Choir!</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    Your account has been created successfully. You've registered using a passkey for secure, passwordless authentication.
                </p>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h2 style="color: #856404; margin-top: 0;">🔑 Your Recovery Codes</h2>
                    <p style="margin: 10px 0; color: #856404;">
                        Save these codes in a safe place. You can use them to access your account if you lose your passkey.
                    </p>
                    {codes_html}
                    <p style="margin: 10px 0; color: #856404; font-weight: bold;">
                        Each code can only be used once. You have 8 codes total.
                    </p>
                </div>

                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h3 style="color: #0c5460; margin-top: 0;">What are passkeys?</h3>
                    <p style="margin: 0; color: #0c5460;">
                        Passkeys use your device's biometric authentication (Face ID, Touch ID, Windows Hello)
                        or security key for fast, secure sign-in. No passwords to remember!
                    </p>
                </div>

                <p style="margin-top: 30px; color: #7f8c8d; font-size: 14px;">
                    Questions? Visit <a href="{FRONTEND_URL}" style="color: #3498db;">choir.chat</a>
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        {FROM_NAME}<br>
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=email,
            subject=f"Welcome to {FROM_NAME} - Save Your Recovery Codes",
            html_content=html_content
        )

        response = sg.send(message)

        if response.status_code == 202:
            logger.info(f"Welcome email sent successfully to {email}")
            return True
        else:
            logger.warning(f"SendGrid response status: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return False


async def send_recovery_alert(email: str, remaining_codes: int) -> bool:
    """Send security alert after recovery code use"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, skipping recovery alert")
            logger.info(f"Recovery alert would be sent to: {email}")
            return True

        sg = SendGridAPIClient(SENDGRID_API_KEY)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Alert: Recovery Code Used</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #e74c3c;">🔒 Security Alert</h1>

                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #721c24;">
                        <strong>A recovery code was just used to access your account.</strong>
                    </p>
                </div>

                <p style="font-size: 16px;">
                    If this was you, no action is needed.
                </p>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>Remaining recovery codes: {remaining_codes}/8</strong>
                    </p>
                </div>

                <p style="font-size: 16px;">
                    If you didn't use a recovery code, your account may be compromised.
                    Please <a href="{FRONTEND_URL}/auth/recovery" style="color: #3498db;">secure your account immediately</a>.
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        {FROM_NAME} Security Team<br>
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=email,
            subject="Security Alert: Recovery Code Used",
            html_content=html_content
        )

        response = sg.send(message)

        if response.status_code == 202:
            logger.info(f"Recovery alert sent successfully to {email}")
            return True
        else:
            logger.warning(f"SendGrid response status: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send recovery alert: {e}")
        return False


async def send_recovery_link(email: str, token: str) -> bool:
    """Send email recovery link for lost passkeys + codes"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, skipping recovery link email")
            logger.info(f"Recovery link would be sent to: {email}")
            logger.info(f"Recovery link: {FRONTEND_URL}/auth/recover?token={token}")
            return True

        sg = SendGridAPIClient(SENDGRID_API_KEY)

        recovery_link = f"{FRONTEND_URL}/auth/recover?token={token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Recovery Request</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #2c3e50;">Account Recovery Request</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    We received a request to recover your {FROM_NAME} account.
                </p>

                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #0c5460;">
                        Click the button below to create a new passkey and regain access to your account.
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{recovery_link}"
                       style="background-color: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block;">
                        Recover My Account
                    </a>
                </div>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;">
                        <strong>⏰ This link expires in 1 hour</strong>
                    </p>
                </div>

                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #721c24;">
                        <strong>Security Notice:</strong> When you recover your account, all existing passkeys will be invalidated and new recovery codes will be generated.
                    </p>
                </div>

                <p style="color: #7f8c8d; font-size: 14px; margin-top: 30px;">
                    If you didn't request this recovery link, you can safely ignore this email. Your account remains secure.
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        {FROM_NAME} Security Team<br>
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=email,
            subject=f"{FROM_NAME} Account Recovery Request",
            html_content=html_content
        )

        response = sg.send(message)

        if response.status_code == 202:
            logger.info(f"Recovery link email sent successfully to {email}")
            return True
        else:
            logger.warning(f"SendGrid response status: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send recovery link email: {e}")
        return False


async def send_recovery_confirmation(email: str, recovery_codes: List[str]) -> bool:
    """Send confirmation after account recovery with new recovery codes"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, skipping recovery confirmation")
            logger.info(f"Recovery confirmation would be sent to: {email}")
            logger.info(f"New recovery codes: {recovery_codes}")
            return True

        sg = SendGridAPIClient(SENDGRID_API_KEY)

        # Format recovery codes for email
        codes_html = "<ul style='list-style: none; padding: 0;'>"
        for i, code in enumerate(recovery_codes, 1):
            codes_html += f"<li style='font-family: monospace; font-size: 14px; padding: 5px; background: #f5f5f5; margin: 5px 0;'>{i}. {code}</li>"
        codes_html += "</ul>"

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
                <h1 style="color: #27ae60;">✅ Account Recovered Successfully</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    Your {FROM_NAME} account has been recovered and a new passkey has been created.
                </p>

                <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #155724;">
                        <strong>Security Update:</strong> All previous passkeys have been invalidated for your security.
                    </p>
                </div>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h2 style="color: #856404; margin-top: 0;">🔑 Your New Recovery Codes</h2>
                    <p style="margin: 10px 0; color: #856404;">
                        Save these codes in a safe place. These are different from your previous codes.
                    </p>
                    {codes_html}
                    <p style="margin: 10px 0; color: #856404; font-weight: bold;">
                        Each code can only be used once. You have 8 new codes.
                    </p>
                </div>

                <p style="font-size: 16px;">
                    We recommend reviewing your recent account activity to ensure everything looks correct.
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        {FROM_NAME} Security Team<br>
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=email,
            subject=f"Your {FROM_NAME} Account Has Been Recovered",
            html_content=html_content
        )

        response = sg.send(message)

        if response.status_code == 202:
            logger.info(f"Recovery confirmation sent successfully to {email}")
            return True
        else:
            logger.warning(f"SendGrid response status: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send recovery confirmation: {e}")
        return False


async def send_passkey_added_alert(email: str, device_info: Optional[str] = None) -> bool:
    """Send alert when new passkey is added"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, skipping passkey added alert")
            logger.info(f"Passkey added alert would be sent to: {email}")
            return True

        sg = SendGridAPIClient(SENDGRID_API_KEY)

        device_text = f"Device: {device_info}" if device_info else "Device: Unknown"

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
                <h1 style="color: #2c3e50;">🔐 New Passkey Added</h1>

                <p style="font-size: 16px; margin-bottom: 20px;">
                    A new passkey was just added to your {FROM_NAME} account.
                </p>

                <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 5px 0; color: #0c5460;"><strong>{device_text}</strong></p>
                </div>

                <p style="font-size: 16px;">
                    If this was you, no action is needed. You can now use this passkey to sign in.
                </p>

                <p style="font-size: 16px;">
                    If you didn't add this passkey, please <a href="{FRONTEND_URL}/account/security" style="color: #3498db;">review your account security</a> immediately.
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        {FROM_NAME} Security Team<br>
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=email,
            subject="New Passkey Added to Your Account",
            html_content=html_content
        )

        response = sg.send(message)

        if response.status_code == 202:
            logger.info(f"Passkey added alert sent successfully to {email}")
            return True
        else:
            logger.warning(f"SendGrid response status: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send passkey added alert: {e}")
        return False
