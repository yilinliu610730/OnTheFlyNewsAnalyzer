from common.prompts import FOLLOW_UP_PROMPT_TEMPLATE_ALL, REFINE_SCHEMA_PROMPT_TEMPLATE
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL
import openai
openai.api_key = OPENAI_API_KEY


# Function to generate follow-up L1 keywords based on both question and user answer (limit to 1-3 keywords)
def generate_L1_keywords(follow_up_question, follow_up_answer):
    response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an assistant that generates relevant keywords for follow-up answers based on the full context of the question and answer."},
            {"role": "user", "content": f"Extract 0-3 most relevant keywords based on the following follow-up question and answer.\n\nFollow-up Question: {follow_up_question}\nUser Answer: {follow_up_answer}. Keywords should be in format keyword 1, keyword 2, ..."}
        ],
        max_tokens=50,
        temperature=0.5
    )
    keywords = response['choices'][0]['message']['content'].strip().split(', ')[:3]
    print("Generated L1 Keywords:\n", keywords)
    return keywords

# Function to generate 10 follow-up questions upfront
def generate_follow_up_questions(user_input):
    follow_up_prompt = FOLLOW_UP_PROMPT_TEMPLATE_ALL.format(user_input=user_input)
    response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": follow_up_prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    # Split and filter out empty lines
    questions = [q.strip() for q in response['choices'][0]['message']['content'].split("\n") if q.strip()]
    print("Generated Follow-Up Questions:\n", questions)
    return questions

def refine_schema_with_levels(initial_schema, instructions, L0_keywords, user_input):
    # Generate initial follow-up questions based on user input
    follow_up_questions = generate_follow_up_questions(user_input)
    all_L1_keywords = set()  # Use a set to automatically handle duplicates

    for idx, follow_up_question in enumerate(follow_up_questions):
        # Capture user response for each follow-up question
        user_response = input(f"Follow-up Question {idx + 1}: {follow_up_question}\nYour Answer (type 'exit' to finish): ")
        
        if user_response.lower() == "exit":
            break

        # Generate L1 keywords using both question and answer
        L1_keywords = generate_L1_keywords(follow_up_question, user_response)
        all_L1_keywords.update(L1_keywords)  # Add keywords to the set to avoid duplicates

        # Refine schema based on follow-up inputs using the updated prompt template
        refine_schema_prompt = REFINE_SCHEMA_PROMPT_TEMPLATE.format(
            initial_schema=initial_schema,
            instructions=instructions,
            follow_up_question=follow_up_question,
            user_response=user_response  # Pass only the response, not the full Q&A pair
        )
        
        # Send the prompt to OpenAI to refine the schema
        refine_response = openai.ChatCompletion.create(
            model=OPENAI_API_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert schema generator."},
                {"role": "user", "content": refine_schema_prompt}
            ],
            max_tokens=5000,
            temperature=0.7
        )
        
        # Update the schema with the refined version
        initial_schema = refine_response['choices'][0]['message']['content'].strip()
        print("Updated Schema:\n", initial_schema)
    
    # Save the final schema and keywords to separate text files after refinement
    with open("final_schema.txt", "w") as schema_file:
        schema_file.write(initial_schema)
    print("Final schema saved to final_schema.txt")
    
    # Save L0 and consolidated L1 keywords in the specified format
    with open("keywords.txt", "w") as keywords_file:
        keywords_file.write(f"L0: {L0_keywords}\n")
        keywords_file.write(f"L1: {sorted(all_L1_keywords)}\n")  # Sort for consistency
    print("Keywords saved to keywords.txt in the specified format.")

    return initial_schema, L0_keywords, sorted(all_L1_keywords)