# The LLM need to provide answer to a user's query given a bunch of filled schema instances, each being a Python class object creation

from typing import Union, List, Any, Dict, Tuple
import openai
from common.prompts import FINAL_ANSWER_PROMT
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL
openai.api_key = OPENAI_API_KEY

def get_final_answer(filled_schemas: Dict[str, Tuple[str, str]], user_query: str) -> str:
    filled_schemas_str = ''
    for article_index, (filled_schema, user_response) in filled_schemas.items():
        filled_schemas_str += filled_schema + "\n"
    
    final_answer_prompt = FINAL_ANSWER_PROMT.format(filled_schemas_str, user_query)
    final_answer_response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert news scholar and need to summarizing events into natural language answer."},
            {"role": "user", "content": final_answer_prompt}
        ]
    )
    return final_answer_response.choices[0].message['content']