import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from ollama import Client as OllamaClient

# Custom LangChain wrapper for Ollama Cloud (https://ollama.com)
class OllamaCloudChat(BaseChatModel):
    model: str = "gpt-oss:120b"
    temperature: float = 0.7

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # 1. Format LangChain message history into Ollama Client format
        ollama_messages = []
        for m in messages:
            if m.type == "human" or m.type == "user":
                role = "user"
            elif m.type == "ai" or m.type == "assistant":
                role = "assistant"
            elif m.type == "system":
                role = "system"
            else:
                role = "user"
            ollama_messages.append({
                "role": role,
                "content": m.content
            })
            
        # 2. Initialize the official Ollama Cloud Client
        api_key = os.environ.get("OLLAMA_API_KEY")
        client = OllamaClient(
            host="https://ollama.com",
            headers={'Authorization': f'Bearer {api_key}'}
        )
        
        # 3. Request model inference
        response = client.chat(
            model=self.model,
            messages=ollama_messages
        )
        
        # 4. Extract generated text and wrap in LangChain types
        content = response['message']['content']
        message = AIMessage(content=content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "ollama-cloud-chat"


class MockChatOpenAI(ChatOpenAI):
    def __init__(self, model="gpt-4o-mini", temperature=0.7, **kwargs):
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
        
        # --- Deep Research Project Mock Logic ---
        
        # 1. Scoping (Module 2) - Clarifying Questions
        if "clarifying" in prompt_lower and "question" in prompt_lower:
            content = json.dumps({
                "questions": [
                    "What is the primary target audience for this quantum cryptography research?",
                    "Should we focus more on symmetric (AES) or asymmetric (RSA/ECC) algorithms?",
                    "What is the expected depth of the final technical migration timeline?"
                ]
            })
            
        # 2. Scoping (Module 2) - Research Brief
        elif "brief" in prompt_lower or "research brief" in prompt_lower:
            content = """# Research Brief: Impact of Quantum Computing on Modern Cryptography
- **Topic**: The threats posed by Shor's and Grover's algorithms to RSA/ECC.
- **Focus Areas**: Post-Quantum Cryptography (PQC), NIST lattice-based standards.
- **Audience**: Enterprise security architects.
- **Depth**: High-level executive summary + technical migration timeline."""
            
        # 3. Research Supervisor (Module 5) - Supervisor routing
        elif "supervisor" in prompt_lower or "select the next analyst" in prompt_lower or "next_agent" in prompt_lower:
            # Simple simulation: route to market analyst, then tech analyst, then finish
            if "market analyst" not in prompt_lower and "market_researcher" not in prompt_lower:
                content = json.dumps({"next_agent": "market_researcher"})
            elif "technical analyst" not in prompt_lower and "technical_researcher" not in prompt_lower:
                content = json.dumps({"next_agent": "technical_researcher"})
            else:
                content = json.dumps({"next_agent": "compile_report"})
                
        # 4. Research Agent (Module 3 & 4) - Search and facts extraction
        elif "search" in prompt_lower or "query" in prompt_lower or "mcp" in prompt_lower:
            content = "[Search Results]: Lattice-based cryptography standardizations were finalized by NIST in late 2024. Shor's algorithm renders RSA-2048 insecure once quantum computers reach ~20 million physical qubits (estimated 2030-2035)."

        # 5. Full Agent (Module 6) - Report generation
        elif "report" in prompt_lower or "compile report" in prompt_lower:
            content = """# Deep Research Report: Quantum Computing vs Modern Cryptography

## 1. Executive Summary
Quantum computers pose a critical threat to modern asymmetric cryptography. Shor's algorithm will render current RSA and ECC schemas obsolete.

## 2. Technical Findings
- Lattice-based algorithms are the current standard for Post-Quantum Cryptography (PQC).
- Grover's algorithm halves symmetric key strength (AES-256 remains safe).

## 3. Market Analysis
Enterprises are beginning migration planning, with NIST standardizations finalized in late 2024.
"""
            
        # --- CodeWriterAgent.ipynb logic ---
        elif "safe_divide" in prompt_lower:
            content = json.dumps({
                "code": "def safe_divide(num, denom):\n    \"\"\"Divides num by denom. Raises ValueError if denom is zero.\"\"\"\n    if denom == 0:\n        raise ValueError('Cannot divide by zero')\n    return num / denom\n",
                "tests": "assert safe_divide(10, 2) == 5.0\nassert safe_divide(4, -1) == -4.0\ntry:\n    safe_divide(1, 0)\n    assert False, 'Expected ValueError'\nexcept ValueError as e:\n    assert str(e) == 'Cannot divide by zero'\n"
            })
            
        # --- EmailAgent.ipynb categorization logic ---
        elif "subscription renewal failed" in prompt_lower or "renewal failed" in prompt_lower:
            content = json.dumps({
                "category": "billing",
                "tasks": ["Verify subscription payment", "Issue invoice copy"]
            })
            
        # --- L3_Applied.ipynb Loop logic ---
        elif "what ai tools can do for writing copy" in prompt_lower or "writing copy" in prompt_lower:
            if "feedback" in prompt_lower or "revise" in prompt_lower:
                content = "The future of AI tools in copy writing is bright. AI drafts copy instantly, analyzing brand voices and generating ideas. Copywriters use AI to beat writer's block and shape the future of digital marketing."
            else:
                content = "AI tools can draft copy instantly, analyzing brand voices and generating ideas. Copywriters use AI to beat writer's block, write headers, and format outlines quickly. However, human editing is always needed to ensure true brand alignment."
                
        # --- L1_Applied.ipynb logic ---
        elif "asynchronous programming" in prompt_lower:
            content = "Learning asynchronous programming allows developers to write highly concurrent applications. By managing tasks without blocking execution threads, programs run faster and handle massive user traffic efficiently. As a result, systems become responsive and modern web tools thrive."
            
        # --- L2_Applied.ipynb logic ---
        elif "web3" in prompt_lower or "decentralization" in prompt_lower:
            content = "The future of Web3 lies in full decentralization. By moving authority away from singular tech platforms, web applications become trustless, secure, and user-owned. Through smart contracts, Web3 introduces transparent finance and community governance."
            
        # --- L4_Applied.ipynb logic ---
        elif "cybersecurity for small businesses" in prompt_lower:
            content = "Cybersecurity is vital for small businesses to protect their client data. Cyberattacks, particularly phishing scams, frequently target smaller companies because of weak defenses. Implementing protocols safeguards trust and assets."
            
        # --- L5_Applied.ipynb logic ---
        elif "reusable water bottles" in prompt_lower:
            content = "Sip sustainably. Save our oceans."
            
        # --- SEO Audit Mock ---
        elif "seo" in prompt_lower:
            content = "SEO Audit: Excellent flow and keyword usage."
            
        # --- Readability critique Mock ---
        elif "readability" in prompt_lower:
            content = "Readability Check: Sentences are clear and concise."
            
        # --- General Email replies fallback ---
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
    # 1. Try Hosted Ollama Cloud if API key is present and points to ollama.com
    ollama_key = os.environ.get("OLLAMA_API_KEY")
    ollama_host = os.environ.get("OLLAMA_BASE_URL", "")
    ollama_model = os.environ.get("OLLAMA_MODEL", "gpt-oss:120b")
    
    if ollama_key and "ollama.com" in ollama_host:
        try:
            llm = OllamaCloudChat(
                model=ollama_model,
                temperature=temperature
            )
            # Test connection
            llm.invoke("Hi")
            print(f"--- Using Live Ollama Cloud ({ollama_model}) ---")
            return llm
        except Exception as e:
            print(f"--- Ollama Cloud connection failed ({str(e)[:50]}...). Trying local Ollama ---")

    # 2. Check for Local Ollama support (no API key required)
    local_url = "http://localhost:11434/v1"
    try:
        llm = ChatOpenAI(
            model="llama3",
            openai_api_key="ollama-local", # Required but ignored
            openai_api_base=local_url,
            temperature=temperature,
            timeout=3 # Short timeout
        )
        llm.invoke("Hi")
        print("--- Using Local Ollama Model (llama3) ---")
        return llm
    except:
        pass

    # 3. Try OpenAI key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            llm = ChatOpenAI(
                model=model,
                openai_api_key=openai_key,
                temperature=temperature
            )
            llm.invoke("Hi")
            print(f"--- Using Live OpenAI LLM ({model}) ---")
            return llm
        except Exception as e:
            pass

    # 4. Fallback to Local Mock
    print("--- Using Local Mock LLM ---")
    return MockChatOpenAI(model=model, temperature=temperature)
