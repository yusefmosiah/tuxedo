import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def test_model():
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    model_name = "anthropic/claude-3.5-sonnet"

    print(f"Testing model: {model_name}")
    print(f"Base URL: {base_url}")

    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url
    )

    msg = HumanMessage(content="Hello, who are you?")
    try:
        response = model.invoke([msg])
        print("Response:")
        print(response.content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
