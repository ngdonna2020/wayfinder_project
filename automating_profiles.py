import os
from itertools import product
import json
from openai import OpenAI
import logging
from pprint import pprint
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# llm call 1, generate the 36 profiles, profile id = combinarion (AAAA)
# llm call 2, generate structured output for each profile
# boto3 to create dynamodb to interact with aws
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


#### Precisionists Questions
questions = [
    {
        "id": 1,
        "text": "How do you prefer to structure your workday?",
        "task-id": "work-style",
        "is_free_response": False,
        "options": [
            ("A", "I thrive with a structured schedule"),
            ("B", "I prefer flexibility in my work hours")
        ]
    },
    {
        "id": 2,
        "text": "What type of workspace do you find most comfortable?",
        "task-id": "environment",
        "is_free_response": False,
        "options": [
            ("A", "Quiet and private spaces"),
            ("B", "Collaborative and open spaces"),
            #("C", "A mix of both")
        ]
    },
    {
        "id": 3,
        "text": "How comfortable are you with frequent interactions with colleagues?",
        "task-id": "interaction-level",
        "is_free_response": False,
        "options": [
            ("A", "Prefer minimal interactions"),
            ("B", "Comfortable with regular teamwork"),
            ("C", "Enjoy leading or coordinating teams")
        ]
    },
    {
        "id": 4,
        "text": "Do you prefer tasks that are:",
        "task-id": "task-preference",
        "is_free_response": False,
        "options": [
            ("A", "Highly detailed and focused"),
            ("B", "Creative and innovative"),
            #("C", "A balance of both")
        ]
    }
]


def generate_all_combinations():
    """Generate all possible combinations of answers"""
    options_per_question = [
        [option[0] for option in q["options"]] for q in questions
    ]
    return list(product(*options_per_question))
def format_combination_for_analysis(combination):
    """Format a combination of answers into a readable format for analysis"""
    formatted_answers = []
    for q_idx, answer in enumerate(combination):
        question = questions[q_idx]
        answer_text = next(opt[1] for opt in question["options"] if opt[0] == answer)
        formatted_answers.append(f"Q: {question['text']}\nA: {answer_text}")
    return formatted_answers
def analyze_combination(answers):
    """Analyze a specific combination of answers using OpenAI API"""
    prompt = "\n".join([
        "Based on these assessment responses, provide a detailed analysis of the ideal",
        "work environment for this candidate. For each aspect, explain how it specifically",
        "relates to their assessment answers. Your response MUST be valid JSON with these fields:",
        "- work_style: {",
        "    description: brief description of preferred work style,",
        "    explanation: how this connects to their assessment answers",
        "  }",
        "- environment: {",
        "    description: ideal work environment,",
        "    explanation: how this matches their preferences",
        "  }",
        "- interaction_level: {",
        "    description: preferred level of social interaction,",
        "    explanation: why this level suits them based on their responses",
        "  }",
        "- task_preference: {",
        "    description: type of tasks they excel at,",
        "    explanation: how this aligns with their answers",
        "  }",
        "- accommodations: {",
        "    description: any specific needs,",
        "    explanation: reasoning behind these accommodations",
        "  }",
        "",
        "Here are the responses:",
        *answers
    ])
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {e}")
        return None
def main():
    """Main function to generate and analyze all combinations"""
    # Generate all possible combinations
    combinations = generate_all_combinations()
    logger.info(f"Generated {len(combinations)} possible combinations")
    # Create a dictionary to store all analyses
    all_analyses = {}
    # Analyze each combination
    for combo in combinations:
        combo_key = "-".join(combo)
        logger.info(f"Analyzing combination: {combo_key}")
        formatted_answers = format_combination_for_analysis(combo)
        analysis = analyze_combination(formatted_answers)
        if analysis:
            all_analyses[combo_key] = {
                "combination": combo,
                "formatted_answers": formatted_answers,
                "analysis": analysis
            }
    # Save results to a JSON file
    output_file = "personality_analyses.json"
    with open(output_file, "w") as f:
        json.dump(all_analyses, f, indent=2)
    logger.info(f"Analysis complete. Results saved to {output_file}")
    # Print a sample analysis
    sample_key = list(all_analyses.keys())[0]
    logger.info("\nSample Analysis:")
    pprint(all_analyses[sample_key])
if __name__ == "__main__":
    main()