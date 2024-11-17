from datasets import load_dataset
from tqdm import tqdm
from typing import Union, List, Any, Dict, Tuple
import openai
from common.prompts import FILL_SCHEMA_PROMPT, KEYWORD_PROMPT
from common.utils import OPENAI_API_KEY, OPENAI_API_MODEL, process_schema, row_to_string
openai.api_key = OPENAI_API_KEY


def process_keywords(keywords: str) -> List[str]:
    return [word.lower() for word in keywords]


def get_keywords(row: Union[dict, str]) -> List[str]:
    row_string = row if isinstance(row, str) else row_to_string(row)
    keywords_str = openai.ChatCompletion.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": KEYWORD_PROMPT},
            {"role": "user", "content": f"Extract the keywords from the following text: {row_string}"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    keywords_str = keywords_str['choices'][0]['message']['content'].strip()
    keywords_lst = keywords_str.split(", ")
    keywords_lst = [keyword.lower() for keyword in keywords_lst]
    return keywords_lst


def count_keyword_occurences(text: str, keywords: List[str]) -> int:
    occurrences = 0
    for keyword in keywords:
        if keyword in text:
            occurrences += 1
    return occurrences


def satisfy_l0_keywords(text: str, keywords: List[str]) -> bool:
    for keyword in keywords:
        if keyword not in text:
            return False
    return True


# in-place edit
def ask_user_response(filled_schemas_by_class: Dict[str, Dict[int, Tuple[str, str]]], dataset) -> None:
    for schema_class, filled_schemas in filled_schemas_by_class.items():
        print(f"\n\n*** Starting response collection for schema class: {schema_class} ***")
        for article_index, (filled_schema, _) in filled_schemas.items():
            article_content = row_to_string(dataset[article_index])
            user_response = input(
                f'''Please provide feedback for the filled schema for article:\n{article_content}\nfilled schma: {filled_schema}\n
                Please put [N/NO/NONE] if you don't have any feedback.
                '''
            )
            if user_response.lower() not in ["no", "n", "none"]:
                filled_schemas[article_index] = (filled_schema, user_response)

# given a schema + keywords input, first retrieve 10 articles from database, then see if
# the schema can be filled by the articles.
def get_schema_filled(
    schema: str,
    dataset,
    L0_keywords: List[str],
    L1_keywords: List[str],
    min_occurrences: int = 3,
    max_articles: int = 3,
    collect_user_feedback: bool = True
) -> Dict[str, Dict[int, Tuple[str, str]]]:
    
    schema_by_class, _ = process_schema(schema, add_base_class=True)
    L0_keywords = process_keywords(L0_keywords)
    L1_keywords = process_keywords(L1_keywords)


    # output is a dictionary key being schema class name, value being a dictionary with key being article index
    # and value being a tuple of (filled schema, user response)

    # iterate through the articles, if there are > 3 keywords present in the content,
    # use the article stop until finding 10 articles

    # article index to article content
    articles: Dict[int, str] = {}
    for i, row in tqdm(enumerate(dataset), desc = f"num retrieved so far: {len(articles)}"):
        article_contents = row_to_string(row, to_lower=True)
        if len(articles) >= max_articles:
            break
        if not satisfy_l0_keywords(article_contents, L0_keywords):
            continue
        if count_keyword_occurences(article_contents, L1_keywords) > min_occurrences:
            articles[i] = article_contents

    print(f"Found {len(articles)} relevant articles after scanning {i} articles.")
        
    # class to article index to filled schema
    filled_schemas_by_class = {}
    default_user_response = "No feedback provided."
    for schema_class, schema in schema_by_class.items():
        # L2_keywords = get_keywords(schema)
        article_to_filled_schema = {}
        for article_index, article in tqdm(articles.items()):

            # # L2 retrieval, need to satisfy narrowed down keywords
            # if count_keyword_occurences(article, L2_keywords) < 1:
            #     print("not satisfying schema specific (L2) keywords")
            #     continue

            filled_schema = openai.ChatCompletion.create(
                model=OPENAI_API_MODEL,
                messages=[
                    {"role": "system", "content": FILL_SCHEMA_PROMPT},
                    {"role": "user", "content": f"Schema: {schema}\nArticles: {article}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            filled_schema = filled_schema['choices'][0]['message']['content'].strip()
            article_to_filled_schema[article_index] = (filled_schema, default_user_response)
        filled_schemas_by_class[schema_class] = article_to_filled_schema
    
    if collect_user_feedback:
        ask_user_response(filled_schemas_by_class, dataset=dataset)

    return filled_schemas_by_class


if __name__ == "__main__":

    # Print information about the dataset
    # try:
    DATA_PATH = "../dataset/filtered_data"
    dataset = load_dataset(DATA_PATH)
    # except:
    #     dataset = get_dataset(year=2024, store_and_filter=True)  # download, process, store
    dataset = dataset["train"]


    print(dataset)        # 9,970,029    still 10M articles after filtering
    print(f"{type(dataset) = }")
    from common.example_tech import EXAMPLE_SCHEMA, EXAMPLE_L0_KEYWORDS, EXAMPLE_L1_KEYWORDS
    filled_schemas_by_class = get_schema_filled(
        EXAMPLE_SCHEMA,
        dataset,
        EXAMPLE_L0_KEYWORDS,
        EXAMPLE_L1_KEYWORDS,
        min_occurrences=3,
        max_articles=5,
        ask_user=True
    )



    output_str_to_write = ""
    for schema_class, filled_schemas in filled_schemas_by_class.items():
        output_str_to_write += f"Schema class: {schema_class}"
        for article_index, (filled_schema, user_response) in filled_schemas.items():
            output_str_to_write += "\n" + row_to_string(dataset[article_index])
            output_str_to_write += filled_schema
            output_str_to_write += "\n" + f"{user_response = }"
        output_str_to_write += "\n\n"

    with open("filled_schemas.txt", "w") as f:
        f.write(output_str_to_write)