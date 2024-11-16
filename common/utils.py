from typing import Dict, Tuple, Union
from datasets import load_dataset
import os

OPENAI_API_KEY = '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'
OPENAI_API_MODEL = "gpt-4o"

def process_schema(raw_schema: str, add_base_class: bool = True) -> Tuple[Dict[str, str], str]:
    schema_by_class = raw_schema.split("class ")[1:]
    schema_by_class = [f"class {schema}" for schema in schema_by_class]
    base_class = schema_by_class[0]
    schema_by_class = schema_by_class[1:]
    if add_base_class:
        schema_by_class = [base_class + schema for schema in schema_by_class]
        split_idx = 2
    else:
        split_idx = 1
    # class name to entire class SCHEMA string
    return {schema.split("class ")[split_idx].split("(")[0]: schema for schema in schema_by_class}, base_class

def row_to_string(row: dict) -> str:
    out_string = ''
    for k, v in row.items():
        out_string += f"{k}: {v}\n"
    return out_string

# first run will take time to download, next runs will only load
def get_dataset(year: Union[int, str], store_and_filter=False, data_path=None):
    dataset = load_dataset("stanford-oval/ccnews", name=str(year))  # name: [2016 ... 2024]
    dataset = dataset.filter(lambda x: x["language"] == "en")
    dataset = dataset.select_columns(["plain_text", "title", "categories", "tags", "published_date"])
    if store_and_filter and data_path is not None:
        dataset.save_to_disk(data_path)
    return dataset