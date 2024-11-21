# The LLM need to provide answer to a user's query given a bunch of filled schema instances, each being a Python class object creation

from typing import Union, List, Any, Dict, Tuple
import openai
from common.utils import row_to_string, contain_at_least_n_keywords
from common.prompts import FINAL_ANSWER_PROMT, FINAL_ANSWER_PROMT_NAIVE
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL
openai.api_key = OPENAI_API_KEY

def get_final_answer(schema_definition: str, filled_schemas: Dict[str, Tuple[str, str]], user_query: str) -> str:
    filled_schemas_str = ''
    for article_index, (filled_schema, user_response) in filled_schemas.items():
        filled_schemas_str += filled_schema + "\n"
    
    final_answer_prompt = FINAL_ANSWER_PROMT.format(schema_definition, filled_schemas_str, user_query)
    final_answer_response = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert news scholar and need to summarizing events into natural language answer."},
            {"role": "user", "content": final_answer_prompt}
        ]
    )
    return final_answer_response.choices[0].message['content']

def get_final_answer_naive(
    dataset,
    max_articles: int,
    user_query: str,
    article_indices: List[int] = None
) -> str:
    
    if article_indices is not None:
        articles = "\n".join([row_to_string(dataset[i]) for i in article_indices])
    else:
        articles = ''
        count = 0
        keyword_prompt = f'''
        Extract relevant keywords based on the following input: {user_query}. 
        Keywords should be separated by commas and in the format keyword 1, keyword 2, ...
        Don't include any special characters or any other information.
        '''
        keywords_response = openai.ChatCompletion.create(
            model=OPENAI_API_MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant that generates relevant keywords for initial input."},
                {"role": "user", "content": keyword_prompt}
            ]
        )
        keywords = keywords_response.choices[0].message['content'].strip().split(', ')
        for i, row in enumerate(dataset):
            article_contents = row_to_string(row, to_lower=True)
            if contain_at_least_n_keywords(article_contents, keywords, 1):
                articles += article_contents + "\n"
                count += 1
            if count >= max_articles:
                break
    final_answer_prompt_naive = FINAL_ANSWER_PROMT_NAIVE.format(articles, user_query)
    final_answer_response_naive = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert news scholar and need to summarizing events into natural language answer."},
            {"role": "user", "content": final_answer_prompt_naive}
        ]
    )
    return final_answer_response_naive.choices[0].message['content']