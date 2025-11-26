import pytest
import os

# Set environment variables for tests BEFORE importing the app
os.environ["OPENAI_API_KEY"] = "dummy_key_for_testing"
os.environ["ENCRYPTION_MASTER_KEY"] = "dummy_encryption_key_for_testing"

from fastapi.testclient import TestClient
from app import create_app
from database_passkeys import db

@pytest.fixture(scope="function")
def test_client():
    """
    Provides a FastAPI TestClient with an authenticated user session.
    - Creates a temporary user.
    - Creates a session for the user.
    - Injects an 'Authorization' header into the client.
    - Cleans up the user after the test.
    """
    app = create_app()
    with TestClient(app) as client:
        # Create a test user
        test_email = "testuser@example.com"

        # Clean up user if it exists from a previous failed run
        existing_user = db.get_user_by_email(test_email)
        if existing_user:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (existing_user["id"],))
                conn.commit()

        user = db.create_user(email=test_email)
        session_token = db.create_session(user_id=user["id"])

        # Set headers
        client.headers = {
            "Authorization": f"Bearer {session_token}"
        }

        yield client

        # Teardown: clean up the test user
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user["id"],))
            conn.commit()
