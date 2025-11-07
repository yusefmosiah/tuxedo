"""
Passkey Authentication Service Layer
Handles business logic for passkey registration, authentication, and management
"""
import os
import json
import base64
import logging
import traceback
from typing import Dict, Any, List, Tuple
from datetime import datetime

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers import parse_registration_credential_json
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    AuthenticatorAttachment,
    AttestationConveyancePreference,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

logger = logging.getLogger(__name__)

# Configuration
RP_NAME = os.getenv("RP_NAME", "Tuxedo AI")


class PasskeyService:
    """Service for handling passkey authentication operations"""

    def __init__(self, database):
        """
        Initialize passkey service.

        Args:
            database: Database manager instance (PasskeyDatabaseManager)
        """
        self.db = database

    def generate_registration_challenge(
        self,
        email: str,
        rp_id: str,
        origin: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate registration challenge and options.

        Args:
            email: User's email address
            rp_id: Relying Party ID
            origin: Request origin

        Returns:
            Tuple of (challenge_id, options_dict)

        Raises:
            ValueError: If user already exists
        """
        logger.info(f"🔐 Generating registration challenge for {email}")
        logger.debug(f"   RP_ID: {rp_id}, Origin: {origin}")

        # Check if user already exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            passkeys = self.db.get_user_passkeys(existing_user['id'])
            passkey_count = len(passkeys)
            logger.warning(f"⚠️ User {email} already exists with {passkey_count} passkey(s)")
            raise ValueError(
                f"An account with this email already exists with {passkey_count} passkey(s). "
                "Please sign in instead of creating a new account."
            )

        # Create challenge
        challenge_id, challenge = self.db.create_challenge()
        logger.info(f"✅ Challenge created: {challenge_id}")

        # Build excludeCredentials list to prevent duplicate passkey creation
        exclude_credentials = []
        if existing_user:
            passkeys = self.db.get_user_passkeys(existing_user['id'])
            exclude_credentials = [
                PublicKeyCredentialDescriptor(
                    id=base64.urlsafe_b64decode(pk['credential_id'])
                )
                for pk in passkeys
            ]
            logger.debug(f"   Added {len(exclude_credentials)} credentials to exclude list")

        # Generate registration options
        registration_options = generate_registration_options(
            rp_id=rp_id,
            rp_name=RP_NAME,
            user_id=challenge_id.encode(),
            user_name=email,
            user_display_name=email,
            challenge=challenge.encode(),
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                require_resident_key=False,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            attestation=AttestationConveyancePreference.NONE,
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            timeout=60000,
        )

        # Convert to JSON-serializable format
        options_json = json.loads(options_to_json(registration_options))

        logger.info(f"✅ Registration options generated for {email}")
        return challenge_id, options_json

    def verify_and_complete_registration(
        self,
        email: str,
        challenge_id: str,
        credential: Dict[str, Any],
        rp_id: str,
        origin: str
    ) -> Tuple[Dict[str, Any], str, List[str]]:
        """
        Verify registration credential and create user.

        Args:
            email: User's email address
            challenge_id: Challenge ID from registration start
            credential: WebAuthn credential from client
            rp_id: Relying Party ID
            origin: Request origin

        Returns:
            Tuple of (user_dict, session_token, recovery_codes)

        Raises:
            ValueError: If verification fails or user already exists
        """
        logger.info(f"🔍 Verifying registration for {email}")
        logger.debug(f"   RP_ID: {rp_id}, Origin: {origin}")
        logger.debug(f"   Challenge ID: {challenge_id}")
        logger.debug(f"   Credential ID: {credential.get('id', 'N/A')[:20]}...")

        # Get challenge
        challenge_data = self.db.get_challenge(challenge_id)
        if not challenge_data:
            logger.error(f"❌ Challenge not found or expired: {challenge_id}")
            raise ValueError("Challenge expired or invalid")

        # Verify the registration response
        try:
            # Try to parse using webauthn helper
            try:
                credential_json = json.dumps(credential)
                parsed_credential = parse_registration_credential_json(credential_json)
                logger.debug("✅ Parsed credential using webauthn helper")
            except Exception as parse_error:
                logger.warning(f"⚠️ Fallback to raw credential dict: {parse_error}")
                parsed_credential = credential

            verification = verify_registration_response(
                credential=parsed_credential,
                expected_challenge=challenge_data['challenge'].encode(),
                expected_origin=origin,
                expected_rp_id=rp_id,
                require_user_verification=True,
            )
            logger.info("✅ Registration verification successful")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            error_trace = traceback.format_exc()

            logger.error(f"❌ Registration verification failed:")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_msg}")
            logger.error(f"   RP_ID: {rp_id}, Origin: {origin}")
            logger.error(f"   Traceback:\n{error_trace}")

            raise ValueError(f"Failed to verify passkey credential: {error_type} - {error_msg}")

        # Mark challenge as used
        self.db.mark_challenge_used(challenge_id)

        # Re-check if user exists (prevent race condition)
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            logger.error(f"❌ Race condition: User {email} created during registration")
            raise ValueError("An account with this email was created while registration was in progress")

        # Create user
        try:
            user = self.db.create_user(email)
            logger.info(f"✅ User created: {user['id']}")
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['unique', 'constraint', 'integrity']):
                logger.error(f"❌ IntegrityError creating user: {e}")
                raise ValueError("An account with this email already exists")
            raise

        # Store passkey credential
        credential_id = base64.urlsafe_b64encode(verification.credential_id).decode('utf-8')
        public_key = base64.urlsafe_b64encode(verification.credential_public_key).decode('utf-8')

        self.db.store_passkey_credential(
            user_id=user['id'],
            credential_id=credential_id,
            public_key=public_key,
            sign_count=verification.sign_count,
            backup_eligible=verification.credential_backed_up,
            transports=credential.get('response', {}).get('transports', []),
            friendly_name="Primary passkey"
        )
        logger.info(f"✅ Passkey credential stored")

        # Generate recovery codes
        recovery_codes = self.db.generate_recovery_codes(user['id'])
        logger.info(f"✅ Generated {len(recovery_codes)} recovery codes")

        # Create session
        session_token = self.db.create_session(user['id'])
        logger.info(f"✅ Session created")

        # Update last login
        self.db.update_last_login(user['id'])

        logger.info(f"🎉 Registration completed successfully for {email}")
        return user, session_token, recovery_codes

    def generate_login_challenge(
        self,
        email: str,
        rp_id: str,
        origin: str
    ) -> Tuple[str, Dict[str, Any], str]:
        """
        Generate login challenge and options.

        Args:
            email: User's email address
            rp_id: Relying Party ID
            origin: Request origin

        Returns:
            Tuple of (challenge_id, options_dict, user_id)

        Raises:
            ValueError: If user not found or has no passkeys
        """
        logger.info(f"🔐 Generating login challenge for {email}")
        logger.debug(f"   RP_ID: {rp_id}, Origin: {origin}")

        # Get user by email
        user = self.db.get_user_by_email(email)
        if not user:
            logger.warning(f"⚠️ User not found: {email}")
            raise ValueError("No account found with this email")

        # Get user's passkeys
        passkeys = self.db.get_user_passkeys(user['id'])
        if not passkeys:
            logger.warning(f"⚠️ No passkeys found for user: {email}")
            raise ValueError("No passkeys found for this account")

        logger.debug(f"   Found {len(passkeys)} passkey(s)")

        # Create challenge
        challenge_id, challenge = self.db.create_challenge(user['id'])
        logger.info(f"✅ Challenge created: {challenge_id}")

        # Create allowed credentials list
        allowed_credentials = [
            PublicKeyCredentialDescriptor(
                id=base64.urlsafe_b64decode(pk['credential_id'])
            )
            for pk in passkeys
        ]

        # Generate authentication options
        authentication_options = generate_authentication_options(
            rp_id=rp_id,
            challenge=challenge.encode(),
            allow_credentials=allowed_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
            timeout=60000,
        )

        # Convert to JSON-serializable format
        options_json = json.loads(options_to_json(authentication_options))

        logger.info(f"✅ Login options generated for {email}")
        return challenge_id, options_json, user['id']

    def verify_and_complete_login(
        self,
        challenge_id: str,
        credential: Dict[str, Any],
        rp_id: str,
        origin: str
    ) -> Tuple[Dict[str, Any], str]:
        """
        Verify login credential and create session.

        Args:
            challenge_id: Challenge ID from login start
            credential: WebAuthn credential from client
            rp_id: Relying Party ID
            origin: Request origin

        Returns:
            Tuple of (user_dict, session_token)

        Raises:
            ValueError: If verification fails
        """
        logger.info(f"🔍 Verifying login")
        logger.debug(f"   RP_ID: {rp_id}, Origin: {origin}")
        logger.debug(f"   Challenge ID: {challenge_id}")

        # Get challenge
        challenge_data = self.db.get_challenge(challenge_id)
        if not challenge_data:
            logger.error(f"❌ Challenge not found or expired: {challenge_id}")
            raise ValueError("Challenge expired or invalid")

        if not challenge_data.get('user_id'):
            logger.error(f"❌ Challenge not associated with a user: {challenge_id}")
            raise ValueError("Challenge not associated with a user")

        # Get credential ID from request (already base64url-encoded by WebAuthn client)
        credential_id = credential.get('id', '')
        logger.debug(f"   Looking up credential: {credential_id[:20]}...")

        # Get stored credential
        stored_credential = self.db.get_passkey_credential(credential_id)
        if not stored_credential:
            logger.error(f"❌ Credential not found: {credential_id[:20]}...")
            raise ValueError("Credential not found")

        # Verify the authentication response
        try:
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge_data['challenge'].encode(),
                expected_origin=origin,
                expected_rp_id=rp_id,
                credential_public_key=base64.urlsafe_b64decode(stored_credential['public_key'] + '=='),
                credential_current_sign_count=stored_credential['sign_count'],
                require_user_verification=True,
            )
            logger.info("✅ Login verification successful")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            error_trace = traceback.format_exc()

            logger.error(f"❌ Login verification failed:")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_msg}")
            logger.error(f"   RP_ID: {rp_id}, Origin: {origin}")
            logger.error(f"   Traceback:\n{error_trace}")

            raise ValueError(f"Failed to verify passkey: {error_type} - {error_msg}")

        # Update sign count
        self.db.update_passkey_sign_count(credential_id, verification.new_sign_count)

        # Mark challenge as used
        self.db.mark_challenge_used(challenge_id)

        # Get user
        user = self.db.get_user_by_id(stored_credential['user_id'])
        if not user:
            logger.error(f"❌ User not found: {stored_credential['user_id']}")
            raise ValueError("User not found")

        # Create session
        session_token = self.db.create_session(user['id'])
        logger.info(f"✅ Session created for {user['email']}")

        # Update last login
        self.db.update_last_login(user['id'])

        logger.info(f"🎉 Login completed successfully for {user['email']}")
        return user, session_token
