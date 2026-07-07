import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

class MockChatOpenAI(ChatOpenAI):
    def __init__(self, model="gpt-4o-mini", temperature=0.7, **kwargs):
        # Pass a mock key to satisfy validation, and call super init
        super().__init__(
            model=model,
            temperature=temperature,
            openai_api_key="mock-key-for-local-testing",
            **kwargs
        )
        
    def invoke(self, input_data, *args, **kwargs):
        prompt_text = str(input_data)
        content = "Mock response content."
        prompt_lower = prompt_text.lower()
        
        # 1. CodeWriterAgent.ipynb logic
        if "safe_divide" in prompt_lower:
            content = json.dumps({
                "code": "def safe_divide(num, denom):\n    \"\"\"Divides num by denom. Raises ValueError if denom is zero.\"\"\"\n    if denom == 0:\n        raise ValueError('Cannot divide by zero')\n    return num / denom\n",
                "tests": "assert safe_divide(10, 2) == 5.0\nassert safe_divide(4, -1) == -4.0\ntry:\n    safe_divide(1, 0)\n    assert False, 'Expected ValueError'\nexcept ValueError as e:\n    assert str(e) == 'Cannot divide by zero'\n"
            })
            
        # 2. EmailAgent.ipynb categorization logic
        elif "subscription renewal failed" in prompt_lower or "renewal failed" in prompt_lower:
            content = json.dumps({
                "category": "billing",
                "tasks": ["Verify subscription payment", "Issue invoice copy"]
            })
            
        # 3. L3_Applied.ipynb Loop logic
        elif "what ai tools can do for writing copy" in prompt_lower or "writing copy" in prompt_lower:
            if "feedback" in prompt_lower or "revise" in prompt_lower:
                content = "The future of AI tools in copy writing is bright. AI drafts copy instantly, analyzing brand voices and generating ideas. Copywriters use AI to beat writer's block and shape the future of digital marketing."
            else:
                content = "AI tools can draft copy instantly, analyzing brand voices and generating ideas. Copywriters use AI to beat writer's block, write headers, and format outlines quickly. However, human editing is always needed to ensure true brand alignment."
                
        # 4. L1_Applied.ipynb logic
        elif "asynchronous programming" in prompt_lower:
            content = "Learning asynchronous programming allows developers to write highly concurrent applications. By managing tasks without blocking execution threads, programs run faster and handle massive user traffic efficiently. As a result, systems become responsive and modern web tools thrive."
            
        # 5. L2_Applied.ipynb logic
        elif "web3" in prompt_lower or "decentralization" in prompt_lower:
            content = "The future of Web3 lies in full decentralization. By moving authority away from singular tech platforms, web applications become trustless, secure, and user-owned. Through smart contracts, Web3 introduces transparent finance and community governance."
            
        # 6. L4_Applied.ipynb logic
        elif "cybersecurity for small businesses" in prompt_lower:
            content = "Cybersecurity is vital for small businesses to protect their client data. Cyberattacks, particularly phishing scams, frequently target smaller companies because of weak defenses. Implementing protocols safeguards trust and assets."
            
        # 7. L5_Applied.ipynb logic
        elif "reusable water bottles" in prompt_lower:
            content = "Sip sustainably. Save our oceans."
            
        # 8. SEO Audit Mock
        elif "seo" in prompt_lower:
            content = "SEO Audit: Excellent flow and keyword usage."
            
        # 9. Readability critique Mock
        elif "readability" in prompt_lower:
            content = "Readability Check: Sentences are clear and concise."
            
        # 10. General Email replies fallback
        elif "billing support" in prompt_lower or "billing team" in prompt_lower:
            content = "Dear Customer,\n\nThank you for contacting billing support. We have verified your request and our accounts team is looking into it.\n\nBest regards,\nBilling Team"
        elif "technical support" in prompt_lower:
            content = "Dear Customer,\n\nThank you for reaching out to Technical Support. We have logged your issue and our systems engineers are currently investigating.\n\nBest regards,\nTech Team"
        elif "feedback" in prompt_lower:
            content = "Dear Customer,\n\nThank you so much for your feedback! We truly value your inputs and have shared them directly with our product design team.\n\nBest regards,\nProduct Team"
        else:
            content = "This is a context-aware mock response generated locally to simulate LLM content writing."
            
        return AIMessage(content=content)

def get_llm(model="gpt-4o-mini", temperature=0.7):
    # Try using real ChatOpenAI first. If it fails due to billing/quota or lacks a key, return MockChatOpenAI.
    try:
        if not os.environ.get("OPENAI_API_KEY"):
            print("--- Using Mock LLM (No API Key found) ---")
            return MockChatOpenAI(model=model, temperature=temperature)
            
        llm = ChatOpenAI(model=model, openai_api_key=os.environ.get("OPENAI_API_KEY"), temperature=temperature)
        # Test connection with a fast prompt
        llm.invoke("Test")
        print("--- Using Real OpenAI LLM ---")
        return llm
    except Exception as e:
        print(f"--- OpenAI API connection failed ({str(e)[:60]}...). Falling back to Mock LLM ---")
        return MockChatOpenAI(model=model, temperature=temperature)
