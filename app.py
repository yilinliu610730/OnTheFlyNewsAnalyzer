import chainlit as cl
import openai
from datasets import load_dataset
from generate_schema import generate_initial_schema, generate_L0_keywords
from refine_schema_from_instances import refine_schema_with_instance_feedback
from retrieve_and_fill import get_schema_filled
from common.utils import process_schema, extract_enforced_fields, get_dataset
from final_answer import get_final_answer, get_final_answer_naive
from refine_schema import generate_L1_keywords, generate_follow_up_questions
from common.prompts import GENERATE_SCHEMA_INSTR, REFINE_SCHEMA_PROMPT_TEMPLATE
from common.utils import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


# Chainlit-based interaction to refine schema with user responses
async def refine_schema_with_levels_chainlit(initial_schema, instructions, L0_keywords, user_input):
    # Generate initial follow-up questions based on user input
    follow_up_questions = generate_follow_up_questions(user_input)
    # await cl.Message(content="Here are a few questions to help refine the schema:\n" + "\n".join(follow_up_questions)).send()

    all_L1_keywords = set()  # Use a set to handle duplicates

    # Iterate through follow-up questions
    for idx, follow_up_question in enumerate(follow_up_questions):
        # Ask user the follow-up question in Chainlit
        user_response_message = await cl.AskUserMessage(
            content=f"Let's dive a bit deeper! In order to better refine our response, could you please answer this question?\n{follow_up_question}\n(You can type 'exit' to stop anytime)",
            timeout=300
        ).send()

        if not user_response_message or user_response_message['output'].strip().lower() == "exit":
            await cl.Message(content="Thanks for your input! The refinement process has been exited.").send()
            break

        user_response = user_response_message['output'].strip()

        # Generate L1 keywords using the response
        L1_keywords = generate_L1_keywords(follow_up_question, user_response)
        all_L1_keywords.update(L1_keywords)  # Add keywords to the set to avoid duplicates

        # Refine schema based on the follow-up inputs
        refine_schema_prompt = REFINE_SCHEMA_PROMPT_TEMPLATE.format(
            initial_schema=initial_schema,
            instructions=instructions,
            follow_up_question=follow_up_question,
            user_response=user_response
        )

        # Use OpenAI API to refine the schema
        refine_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert schema generator."},
                {"role": "user", "content": refine_schema_prompt}
            ],
            max_tokens=5000,
            temperature=0.7
        )

        # Update the schema with the refined version
        initial_schema = refine_response["choices"][0]["message"]["content"].strip()
        await cl.Message(content=f"Great! The schema has been updated:\n{initial_schema}").send()

    # Remove any overlap between L0 and L1 keywords
    for l0 in L0_keywords + ['']:
        if l0 in all_L1_keywords:
            all_L1_keywords.remove(l0)

    return initial_schema, L0_keywords, sorted(all_L1_keywords)


@cl.on_chat_start
async def main():
    try:
        # Welcome message
        await cl.Message(content="Hello! 👋 Welcome to the On The Fly News Seeker Chatbot! I'm here to help you understand global events and news based on your query. Ask me anything! 😊").send()

        # Step 1: Ask the user for a topic
        user_query = await cl.AskUserMessage(content="What topic or question would you like to explore today?", timeout=300).send()
        if not user_query or not user_query.get('output'):
            await cl.Message(content="Oops, I didn't catch that! Could you please share a topic or a question you have?").send()
            return

        # Extract user input
        topic = user_query['output'].strip()

        # Step 2: Generate initial schema
        initial_schema = generate_initial_schema(topic)
        await cl.Message(content=f"Awesome! I’ve generated an initial schema for your topic:\n{initial_schema}").send()

        # Step 3: Generate L0 keywords
        L0_keywords = generate_L0_keywords(topic)
        # await cl.Message(content=f"Here are the key keywords related to your topic:\n{', '.join(L0_keywords)}").send()

        # Step 4: Confirm to proceed
        feedback = await cl.AskUserMessage(
            content="Does this look good to you? Would you like to refine the schema further? (yes/no)", timeout=300
        ).send()
        if not feedback or feedback['output'].lower() not in ["yes", "y"]:
            await cl.Message(content="No worries, feel free to reach out whenever you want to refine the schema! 😊").send()
            return

        # Step 5: Refine schema with follow-up questions in Chainlit
        refined_schema, L0_keywords, L1_keywords = await refine_schema_with_levels_chainlit(
            initial_schema, GENERATE_SCHEMA_INSTR, L0_keywords, topic
        )
        await cl.Message(content=f"Great! Here is the final refined schema:\n{refined_schema}").send()

        # Step 5: Initialize variables for schema retrieval and refinement
        enforced_fields = extract_enforced_fields(initial_schema)
        schema_by_class, _ = process_schema(refined_schema, add_base_class=True)
        schema_by_class_nobase, base_class = process_schema(refined_schema, add_base_class=False)
        max_articles = 50
        DATA_PATH = "./dataset/filtered_data"
        try:
            dataset = load_dataset(DATA_PATH)['train']
        except:
            dataset = get_dataset(year=2024, store_and_filter=True, data_path=DATA_PATH)['train']  # download, process, store
        refined_schema = initial_schema

        # Step 6: Retrieve and refine schema instances in a loop
        try:
            # Retrieve schema instances
            filled_schemas_by_class, article_indices = get_schema_filled(
                refined_schema,
                dataset=dataset,
                L0_keywords=L0_keywords,
                L1_keywords=L1_keywords,
                min_occurrences=3,
                max_articles=max_articles,
                enforced_fields=enforced_fields,
                collect_user_feedback=False
            )

            await cl.Message(content=f"Here's what I found for your query:\n{filled_schemas_by_class}").send()

        except Exception as e:
            await cl.Message(content=f"Oops! Something went wrong during the retrieval process. Here's the error: {str(e)}").send()
            return

        # Step 7: VERY naive answer generation
        try:
            naive_answer = f'Here is the VERY naive answer to your query "{topic}":\n'
            naive_answer += get_final_answer_naive(
                dataset,
                max_articles=max_articles,
                user_query=topic,
                article_indices=None  # No specific articles, very naive
            )
            # also save to txt
            with open("answer_very_naive.txt", "w") as f:
                f.write(naive_answer)
            await cl.Message(content=naive_answer).send()
        except Exception as e:
            await cl.Message(content=f"Error generating VERY naive answer: {str(e)}").send()
            return
    
        # Step 8: Naive Answer Generation
        try:
            naive_answer = f'Here is the naive answer to your query "{topic}":\n'
            naive_answer += get_final_answer_naive(
                dataset,
                max_articles=max_articles,
                user_query=topic,
                article_indices=article_indices
            )
            # also save to txt
            with open("answer_naive.txt", "w") as f:
                f.write(naive_answer)
            await cl.Message(content=naive_answer).send()
        except Exception as e:
            await cl.Message(content=f"Error generating naive answer: {str(e)}").send()
            return
        
        # Step 9: Generate the final answer
        try:
            answer = f'Here is the final answer to your query "{topic}":\n'
            for schema_class, filled_schemas in filled_schemas_by_class.items():
                perspective_answer = get_final_answer(
                    schema_by_class[schema_class],
                    filled_schemas,
                    topic
                )
                answer += f"Perspective {schema_class}:\n{perspective_answer}\n"
            # also save to txt
            with open("answer_schema.txt", "w") as f:
                f.write(answer)
            await cl.Message(content=answer).send()
        except Exception as e:
            await cl.Message(content=f"Error generating final answer: {str(e)}").send()
            return
        
        # End the session
        await cl.Message(content="Thank you for using the Schema Generator Chatbot! 😊 Have a wonderful day!").send()

    except Exception as e:
        await cl.Message(content=f"Oops! An unexpected error occurred. Here's the message: {str(e)}").send()