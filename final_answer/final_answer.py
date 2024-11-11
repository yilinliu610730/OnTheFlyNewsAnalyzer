# The LLM need to provide answer to a user's query given a bunch of filled schema instances, each being a Python class object creation

import os
import sys
from datasets import load_dataset
from typing import Union, List, Any, Dict, Tuple
import openai
openai.api_key = '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'

FINAL_ANSWER_PROMT = '''
Given the following filled schema instances, please answer the following user query in natual language. Be clear and concise in your answer.
Your answer should align with the provided information in the filled schema instances.

The filled schema instances are:
{}

The user query is:
{}
'''

def get_final_answer(filled_schemas: Dict[str, Tuple[str, str]], user_query: str) -> str:
    filled_schemas_str = ''
    for article_index, (filled_schema, user_response) in filled_schemas.items():
        filled_schemas_str += f"(filled schema: {filled_schema}, user response: {user_response})\n"
    
    final_answer_prompt = FINAL_ANSWER_PROMT.format(filled_schemas_str, user_query)
    final_answer_response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert schema refiner."},
            {"role": "user", "content": final_answer_prompt}
        ]
    )
    return final_answer_response.choices[0].message['content']