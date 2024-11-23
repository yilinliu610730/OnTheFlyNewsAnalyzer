import openai
from refine_schema import refine_schema_with_levels
from common.prompts import GENERATE_SCHEMA_INSTR, GENERATE_SCHEMA_EXAMPLE, KEYWORD_PROMPT_FROM_QUERY_L0
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL
openai.api_key = OPENAI_API_KEY
from typing import List, Tuple

# Function to generate schema based on user input
def generate_initial_schema(user_input: str) -> str:
    response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": GENERATE_SCHEMA_INSTR + GENERATE_SCHEMA_EXAMPLE + f"\nUser: {user_input}"}
        ],
        max_tokens=5000,
        temperature=0.7
    )
    initial_schema = response['choices'][0]['message']['content'].strip()
    print("Initial schema generated:\n", initial_schema)
    
    # Save the initial schema to a text file
    with open("initial_schema.txt", "w") as file:
        file.write(initial_schema)
    print("Initial schema saved to initial_schema.txt")
    
    return initial_schema


# Function to generate initial L0 keywords based on user input (limit to 5 keywords)
def generate_L0_keywords(user_input: str) -> List[str]:
    num_keywords = 3
    response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": KEYWORD_PROMPT_FROM_QUERY_L0.format(num_keywords=num_keywords)},
            {"role": "user", "content": f"User input query: {user_input}. Keywords should be comma-separated."}
        ],
        max_tokens=30,
        temperature=0.1
    )
    keywords = response['choices'][0]['message']['content'].strip().replace(' ', '').split(',')[:num_keywords]
    print("Generated L0 Keywords:\n", keywords)
    return keywords


# Main function to execute the schema generation process with levels
def generate_schema_with_levels(user_input: str) -> Tuple[str, List[str], List[str]]:
    # Step 1: Generate Initial Schema
    initial_schema = generate_initial_schema(user_input)
    
    # Step 2: Generate L0 Keywords based on User Input
    L0_keywords = generate_L0_keywords(user_input)
    
    # Step 3: Refine Schema with L1 Keywords from Follow-Up Answers
    schema, L0_keywords, L1_keywords = refine_schema_with_levels(initial_schema, GENERATE_SCHEMA_INSTR, L0_keywords, user_input)  

    return schema, L0_keywords, L1_keywords

if __name__ == "__main__":
    # Example: User prompt to generate a schema for financial trends in the technology sector
    user_query = "What are the financial trends in the technology sector in the U.S.?"
    generate_schema_with_levels(user_query)