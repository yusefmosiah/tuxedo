import os
import sys
from dotenv import load_dotenv
from runloop_api_client import Runloop

load_dotenv()

def test_connection():
    api_key = os.environ.get("RUNLOOP_API_KEY")
    if not api_key:
        print("Error: RUNLOOP_API_KEY not found in environment")
        sys.exit(1)

    print(f"Connecting with API key: {api_key[:4]}...")

    client = Runloop(bearer_token=api_key)

    try:
        print("Creating devbox and waiting for it to be ready...")
        devbox = client.devboxes.create_and_await_running(name="vibewriter-test")
        print(f"Devbox created and running: {devbox.id}")
        print("Devbox methods:", [m for m in dir(devbox) if not m.startswith('_')])

        print("Executing command...")
        cmd_res = client.devboxes.execute_sync(devbox.id, command="echo hello")
        print("Command result:", cmd_res)
        print("Result dir:", dir(cmd_res))

        print("Shutting down devbox...")
        # client.devboxes.shutdown(devbox.id)

    except Exception as e:
        print(f"Error: {e}")
        # Print available methods on client for debugging
        print("Client dir:", dir(client))
        if 'devbox' in locals():
            print("Devbox dir:", dir(devbox))
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
