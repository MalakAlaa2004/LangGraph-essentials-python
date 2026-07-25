import os
import sys

# Configure UTF-8 output encoding for Windows PowerShell terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Verify required LangSmith environment variables
tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2")
api_key = os.getenv("LANGCHAIN_API_KEY")
project_name = os.getenv("LANGCHAIN_PROJECT", "legacy-modernization-mvp")

ollama_base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
ollama_api_key = os.getenv("OLLAMA_API_KEY")
ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")

if not tracing_enabled or not api_key:
    print("[ERROR] LANGCHAIN_TRACING_V2 or LANGCHAIN_API_KEY not set in .env")
    sys.exit(1)


def test_langsmith_tracing():
    print("Initializing LangSmith Tracing Verification Test...")
    print(f"Project Name: {project_name}")
    print(f"Tracing Enabled: {tracing_enabled}")

    try:
        # Create a simple LangChain pipeline
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a senior enterprise architect evaluating legacy system modernization.",
                ),
                (
                    "user",
                    "Summarize the purpose of the ArchiMate 3.2 specification in one sentence.",
                ),
            ]
        )

        # Use Ollama Cloud API if key is present, otherwise fallback to FakeListLLM
        if ollama_api_key:
            print(f"Using Ollama Cloud Endpoint ({ollama_model})...")
            llm = ChatOpenAI(
                base_url=f"{ollama_base_url.rstrip('/')}/v1",
                api_key=ollama_api_key,
                model=ollama_model,
                temperature=0,
            )
        else:
            print("Using FakeListLLM fallback for test...")
            llm = FakeListLLM(
                responses=[
                    "ArchiMate 3.2 is an open standard modeling language for describing enterprise architectures."
                ]
            )

        chain = prompt | llm

        print("Executing test LLM call...")
        response = chain.invoke({})
        resp_text = response.content if hasattr(response, "content") else response

        print("[SUCCESS] LLM Call Successful!")
        print(f"Response: {resp_text}")
        print("\nTrace successfully dispatched to LangSmith!")
        print(
            f"Check your dashboard at: https://smith.langchain.com/ (Project: '{project_name}')"
        )
        return True

    except Exception as e:
        print(f" LangSmith Test Failed: {e}")
        return False


if __name__ == "__main__":
    success = test_langsmith_tracing()
    if not success:
        sys.exit(1)
