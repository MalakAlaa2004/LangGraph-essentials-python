import os
import sys
from dotenv import load_dotenv

# Import mock_llm from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mock_llm import get_llm

load_dotenv()

article_1_path = r"C:\Users\LENOVO\.gemini\antigravity-ide\brain\ee2aa922-f01e-4776-a4e5-11fe2561b7c1\.system_generated\steps\377\content.md"
article_2_path = r"C:\Users\LENOVO\.gemini\antigravity-ide\brain\ee2aa922-f01e-4776-a4e5-11fe2561b7c1\.system_generated\steps\381\content.md"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_questions_for_article(article_title, content, output_file, assignment_num):
    llm = get_llm()
    print(f"Generating questions for: {article_title}...")
    
    # 50 MCQs
    prompt_mcqs = f"""You are a senior computer science professor. Read the technical document below:
Title: {article_title}
Content:
{content[:8000]}

Based on this content, generate exactly 50 high-quality Multiple-Choice Questions (MCQs).
Each question must:
1. Have a clear question text.
2. Have 4 options (A, B, C, D).
3. Specify the correct answer.
4. Cover technical details, architecture patterns, and recommendations mentioned in the text.
Format the output clearly in markdown."""

    res_mcqs = llm.invoke(prompt_mcqs)
    
    # 10 Essay questions
    prompt_long = f"""You are a senior computer science professor. Read the technical document below:
Title: {article_title}
Content:
{content[:8000]}

Based on this content, generate exactly 10 comprehensive, long-form essay/analytical questions that cover the core themes, architectural patterns, and trade-offs described.
Provide a brief expected answer outline for each question.
Format the output clearly in markdown."""

    res_long = llm.invoke(prompt_long)
    
    final_output = f"""# Assignment Study Guide: {article_title} ({assignment_num})

## PART 1: 50 Multiple-Choice Questions (MCQs)

{res_mcqs.content}

## PART 2: 10 Long-Form Study & Discussion Questions

{res_long.content}
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"Saved generated questions to: {output_file}")

if __name__ == "__main__":
    if os.path.exists(article_1_path):
        content_1 = read_file(article_1_path)
        generate_questions_for_article(
            "Building Effective Agents",
            content_1,
            os.path.join("week2", "assignment_14_building_effective_agents_questions.md"),
            "Assignment 14"
        )
    else:
        print(f"Error: Article 1 cache file not found at {article_1_path}")

    if os.path.exists(article_2_path):
        content_2 = read_file(article_2_path)
        generate_questions_for_article(
            "Harness Design for Long-Running Applications",
            content_2,
            os.path.join("week2", "assignment_15_harness_design_questions.md"),
            "Assignment 15"
        )
    else:
        print(f"Error: Article 2 cache file not found at {article_2_path}")
