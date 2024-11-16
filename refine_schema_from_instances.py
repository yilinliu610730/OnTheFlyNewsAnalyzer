from datasets import load_dataset
from typing import Union, List, Any, Dict
from common.prompts import REFINE_SCHEMA_FROM_INSTANCES_PROMPT
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL, row_to_string
import openai
openai.api_key = OPENAI_API_KEY


def refine_schema_with_instance_feedback(
    initial_prompt: str,
    initial_schema: str,
    filled_schemas: Dict[str, List[str]],
    dataset,
) -> str:
    
    schema_and_response = ''
    for article_index, (filled_schema, user_response) in filled_schemas.items():
        article_content = row_to_string(dataset[article_index])
        schema_and_response += f"(filled schema: {filled_schema}, user response: {user_response}, article: {article_content})\n"

    refine_schema_prompt = REFINE_SCHEMA_FROM_INSTANCES_PROMPT.format(
        initial_schema,
        initial_prompt,
        schema_and_response
    )
    refine_response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert schema refiner."},
            {"role": "user", "content": refine_schema_prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    new_schema = refine_response['choices'][0]['message']['content'].strip()
    return new_schema