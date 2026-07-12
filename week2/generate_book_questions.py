import os
import sys
from pypdf import PdfReader
from dotenv import load_dotenv

# Import mock_llm from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

pdf_path = r"C:\Users\LENOVO\Downloads\Building Effective AI Agents- Architecture Patterns and Implementation Frameworks.pdf"
output_path = os.path.join("week2", "assignment_06_building_effective_ai_agents_book_questions.md")

def extract_text_from_pdf(path):
    print(f"Extracting text from PDF: {path}...")
    reader = PdfReader(path)
    text_content = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_content.append(text)
    return "\n".join(text_content)

def generate_questions(pdf_text, output_file):
    llm = get_llm()
    print("Querying Ollama Cloud to generate MCQs...")
    
    # 50 MCQs
    prompt_mcqs = f"""You are an expert AI engineering professor. Read the technical document below:
{pdf_text[:9000]}

Based on this content, generate exactly 50 high-quality Multiple-Choice Questions (MCQs).
Each question must:
1. Have a clear question text.
2. Have 4 options (A, B, C, D).
3. Specify the correct answer.
4. Cover the case studies (Coinbase, Tines, Gradient Labs, Augment, Grafana, Intercom, Assembled, CoCounsel, Legora, Advolve, Inscribe), design principles, agent workflows, and routing topologies.
Format the output clearly in markdown."""

    res_mcqs = llm.invoke(prompt_mcqs)
    
    # 10 Essay questions
    print("Querying Ollama Cloud to generate analytical essay questions...")
    prompt_long = f"""You are an expert AI engineering professor. Read the technical document below:
{pdf_text[:9000]}

Based on this content, generate exactly 10 comprehensive, long-form essay/analytical questions that cover the core themes, architectural patterns, and trade-offs described.
Provide a brief expected answer outline for each question.
Format the output clearly in markdown."""

    res_long = llm.invoke(prompt_long)
    
    final_output = f"""# Assignment Study Guide: Building Effective AI Agents (Assignment 06)

## PART 1: 50 Multiple-Choice Questions (MCQs)

{res_mcqs.content}

## PART 2: 10 Long-Form Study & Discussion Questions

{res_long.content}
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"Saved generated questions to: {output_file}")

if __name__ == "__main__":
    if os.path.exists(pdf_path):
        text = extract_text_from_pdf(pdf_path)
        generate_questions(text, output_path)
    else:
        print(f"Error: PDF book file not found at: {pdf_path}")
