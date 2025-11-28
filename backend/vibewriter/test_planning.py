import sys
from dotenv import load_dotenv

# Load env before importing agent to ensure keys are available
load_dotenv()

from vibewriter.agent import VibewriterAgent

def test_planning():
    print("Initializing Vibewriter Agent...")
    agent = VibewriterAgent()

    task = "Create a plan to write a haiku about coding and save it to a file named 'haiku.txt'."
    print(f"Task: {task}")

    try:
        print("Invoking agent (this may take a minute)...")
        # Increase recursion limit for multi-step task
        result = agent.invoke(task, config={"recursion_limit": 50})

        print("Agent finished.")
        # print("Result state:", result) # Verbose

        print("Verifying file creation...")
        # Check if haiku.txt exists in backend
        # We can use the backend directly to check
        files = agent.backend.download_files(["haiku.txt"])

        if files and files[0].content:
            print("File 'haiku.txt' found!")
            print("Content:")
            print(files[0].content.decode('utf-8'))
        else:
            print("Error: File 'haiku.txt' not found or empty.")
            if files:
                print(f"Error details: {files[0].error}")
            sys.exit(1)

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("Cleaning up...")
        agent.cleanup()

if __name__ == "__main__":
    test_planning()
