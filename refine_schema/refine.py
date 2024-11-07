import os
import sys
from datasets import load_dataset
from tqdm import tqdm
from typing import Union, List, Any, Dict
from collections import defaultdict
from tqdm import tqdm
from retrieve_and_fill.retrieve_and_fill import row_to_string
import openai
openai.api_key = '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'


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

    refine_schema_prompt = f'''
    Your are an expert schema refiner, and your task is to refine the schema based on user's response and the previous schema
    demonstrated to the user. Refine the schema based on the following user inputs, ensuring it strictly follows the original instructions.
    You will be given tuples of (filled schema, user response, article information source) to help you refine the schema. Each tuple will be
    presented in the following format:
    """
    (filled schema 1: ..., user response 1: ..., article 1: ...)
    (filled schema 2: ..., user response 2: ..., article 2: ...)
    """
    They will all share the same initial schema below and the same initial prompt used to generate the schema, in which
    the instructions you will also follow. Carefully read user responses in each tuple and refine the "initial_schema" based on them.

    The initial schema is:
    {initial_schema}

    Which was generated using an initial prompt:
    {initial_prompt}

    The tuples are:
    {schema_and_response}

    Make sure your output will follow the original schema format and will be a valid schema. Don't change anything in the base class schame
    However, you are free to do any of the following:
    1) Change the name or description of the or any of the child classes
    2) Add new child classes with descriptions and fields properly defined
    3) Remove child classes that are not relevant
    4) Add new fields to any of the child classes
    5) Remove fields that are not relevant
    '''
    refine_response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert schema refiner."},
            {"role": "user", "content": refine_schema_prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    new_schema = refine_response['choices'][0]['message']['content'].strip()
    return new_schema