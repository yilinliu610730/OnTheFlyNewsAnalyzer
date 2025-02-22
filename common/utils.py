from typing import Dict, Tuple, Union, List
from datasets import load_dataset
import os

OPENAI_API_KEY = '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'
OPENAI_API_MODEL = "gpt-4o"

def process_schema(raw_schema: str, add_base_class: bool = True) -> Tuple[Dict[str, str], str]:
    schema_by_class = raw_schema.split("class ")[1:]
    enum_classes = '\n'.join([_class for _class in schema_by_class if "Enum" in _class])
    schema_by_class = [f"class {schema}" for schema in schema_by_class if "Enum" not in schema]
    base_class = enum_classes + schema_by_class[0]
    schema_by_class = schema_by_class[1:]
    if add_base_class:
        schema_by_class = [base_class + schema for schema in schema_by_class]
        split_idx = 2
    else:
        split_idx = 1
    # class name to entire class SCHEMA string
    out = {schema.split("class ")[split_idx].split("(")[0]: schema for schema in schema_by_class}, base_class
    return out

def row_to_string(row: dict, to_lower: bool = True) -> str:
    out_string = ''
    for k, v in row.items():
        out_string += f"{k}: {v}\n"
    if to_lower:
        return out_string.lower()
    return out_string

# first run will take time to download, next runs will only load
def get_dataset(year: Union[int, str], store_and_filter=False, data_path=None):
    dataset = load_dataset("stanford-oval/ccnews", name=str(year))  # name: [2016 ... 2024]
    dataset = dataset.filter(lambda x: x["language"] == "en")
    dataset = dataset.select_columns(["plain_text", "title", "categories", "tags", "published_date"])
    if store_and_filter and data_path is not None:
        dataset.save_to_disk(data_path)
    return dataset


def contain_at_least_n_keywords(text: str, keywords: List[str], n: int) -> bool:
    count = 0
    for keyword in keywords:
        if keyword not in text:
            continue
        count += 1
        if count >= n:
            return True
    return False


def extract_enforced_fields(schema_definition: str) -> Dict[str, str]:
    enforced_fields = {}
    return enforced_fields
    for line in schema_definition.split("\n"):
        # detect anything like `Field(True, description="")`, instead of unfilled Field(..., description="")
        if "Field(" in line and "..." not in line and "None" not in line:
            field_name, line = line.split(":")[0], line.split(":")[1]
            field_name = "".join(field_name.split())
            line = line.split("Field(")[1]
            field_val = line.split(",")[0]
            enforced_fields[field_name] = field_val
    return enforced_fields


def schema_satisfy_all_enforced_fields(schema_instance: str, enforced_fields: Dict[str, str]) -> bool:
    for field_name, field_val in enforced_fields.items():
        if field_name not in schema_instance:
            return False
        if field_val not in schema_instance.split(field_name)[1].split(",")[0]:
            return False
    return True


# index to keywords system building
def build_index(dataset):
    import os, pickle, tqdm
    from together import Together
    from common.prompts import KEYWORD_PROMPT

    api_key = "cd7b5b267e7c7118ef2a4d6b9f59898a1d1fd9ae1551fb9b627b6d5c3d7e94ca"
    os.environ["TOGETHER_API_KEY"] = api_key  # export TOGETHER_API_KEY=api_key
    client = Together()
    model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

    idx_to_keywords = {2024: {}}  # year to article index to keywords
    for i, row in tqdm(enumerate(dataset), total=len(dataset)):
        if i > 20:
            break
        article_contents = row_to_string(row, to_lower=True)
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": KEYWORD_PROMPT},
                {"role": "user", "content": f"Extract the keywords from the following text: \n{article_contents}"},
            ],
        )
        keywords_str = stream.choices[0].message.content
        keywords_lst = keywords_str.split(", ")
        keywords_lst = set([keyword.lower() for keyword in keywords_lst])
        print(f"Article {i} keywords: {keywords_lst}")
        idx_to_keywords[2024][i] = keywords_lst

    with open("idx_to_keywords.pkl", "wb") as f:
        pickle.dump(idx_to_keywords, f)