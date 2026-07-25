import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Verify required LangSmith environment variables
tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2")
api_key = os.getenv("LANGCHAIN_API_KEY")
project_name = os.getenv("LANGCHAIN_PROJECT", "legacy-modernization-mvp")

if not tracing_enabled or not api_key:
    print(" ERROR: LANGCHAIN_TRACING_V2 or LANGCHAIN_API_KEY not set in .env")
    sys.exit(1)

def test_langsmith_tracing():
    print("Initializing LangSmith Tracing Verification Test...")
    print(f"Project Name: {project_name}")
    print(f"Tracing Enabled: {tracing_enabled}")
    
    try:
        # Create a simple LangChain pipeline
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior enterprise architect evaluating legacy system modernization."),
            ("user", "Summarize the purpose of the ArchiMate 3.2 specification in one sentence.")
        ])
        
        # Initialize LLM model (uses OPENAI_API_KEY from .env)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        chain = prompt | llm
        
        print("Executing test LLM call...")
        response = chain.invoke({})
        
        print(" LLM Call Successful!")
        print(f"Response: {response.content}")
        print("\n Trace successfully dispatched to LangSmith!")
        print(f"Check your dashboard at: https://smith.langchain.com/ (Project: '{project_name}')")
        return True

    except Exception as e:
        print(f" LangSmith Test Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_langsmith_tracing()
    if not success:
        sys.exit(1)
