import os
import sys
from together import Together
import together
import together.types.chat_completions
from datasets import load_dataset
from tqdm import tqdm
from typing import Union, List, Any, Dict

api_key = "cd7b5b267e7c7118ef2a4d6b9f59898a1d1fd9ae1551fb9b627b6d5c3d7e94ca"
os.environ["TOGETHER_API_KEY"] = api_key  # export TOGETHER_API_KEY=api_key
client = Together()

# complete list : https://api.together.ai/models.
model_choices = [
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "codellama/CodeLlama-70b-Instruct-hf",
    "deepseek-ai/deepseek-coder-33b-instruct",
    "Qwen/Qwen2-72B-Instruct",
]
MODEL_NAME = model_choices[2]

KEYWORD_PROMPT = f'''
    You are a virtual assistance model and you need to read the given text and generate a list of keywords that best describe the text.
    Notice you need to both summarize the text and generate a list of keywords. Your output should be easily transferable to a list
    of string in Python. Don't include any other information in the output other than the keywords.
    '''


FILL_SCHEMA_PROMPT = f'''
    You are a virtual assistance model given a list of articles and a schema, you need to fill the schema by information
    you find in the articles. The schema is in string but follows a Python Class definition format. You need to fill in the attributes
    of the class with any information you found from any of the articles. In the Python format, simply replace the '...' with actual
    information you found. Your output should also be a string, but easily transferable to a Python class definition.
    Fill as much fields as you can, but only fill the attributes that you can find in the articles, leave the rest as before (i.e. ...).
    Don't change the schema format or anything else from the Schema defintion such as class name, attribute names, attribute types, etc.
    Don't include any other information in the output other than the filled schema, no explanation needed.
'''


EXAMPLE_SCHEMA = '''
    class Riot(ACLEDEvent, ABC):
        """
        "Riot" are violent events where demonstrators or mobs of three or more engage in violent or destructive acts, including but not limited to physical fights, rock throwing, property destruction, etc. They may engage individuals, property, businesses, other rioting groups, or armed actors. Rioters are noted by generic actor name "Rioters". If rioters are affiliated with a specific group - which may or may not be armed - or identity group, that group is recorded in the respective "Actor" field. Riots may begin as peaceful protests, or a mob may have the intention to engage in violence from the outset.
        "Riot" event type has the following subtypes:
        - ViolentDemonstration: Demonstrators engage in violence or destructive activities, such as physical
        clashes, vandalism, or road-blocking, regardless of who initiated the violence.
        - MobViolence: Rioters violently interact with other rioters, civilians, property, or armed groups outside
        of demonstration contexts, often involving disorderly crowds with the intention to cause harm or disruption.
        """
        location: Location = Field(
            ...,
            description="Location where the event takes place"
        )
        fatalities: Optional[int] = Field(
            ...,
            description="Total number of fatalities, if known"
        )
        targets_civilians: bool = Field(
            ...,
            description="Indicates if the 'Riot' event is mainly or only targeting civilians. E.g. a village mob assaulting another villager over a land dispute."
        )
        group_1: List[str] = Field(
            ...,
            description="Group or individual involved in the violence"
        )
        group_2: List[str] = Field(
            ...,
            description="The other group or individual involved in the violence, if any"
        )
        targets_local_administrators: bool = Field(
            ...,
            description="Whether this violence is affecting local government officials and administrators - including governors, mayors, councilors, and other civil servants.",
        )
        women_targeted: List[WomenTargetedCategory] = Field(
            ...,
            description="The category of violence against women, if any. If this violence is not targeting women, this should be an empty list.",
        )
    
    class ViolentDemonstration(Riot):
        """
        Is a type of "Riot" event. This event type is used when demonstrators engage in violence and/or destructive activity. Examples include physical clashes with other demonstrators or government forces; vandalism; and road-blocking using barricades, burning tires, or other material. The coding of an event as a "Violent demonstration" does not necessarily indicate that demonstrators initiated the violence and /or destructive actions.
        Excludes events where a weapon is drawn but not used, or when the situation is de-escalated before violence occurs.
        """

    class MobViolence(Riot):
        """
        Is a type of "Riot" event. A mob is considered a crowd of people that is disorderly and has the intention to cause harm or disruption through violence or property destruction. Note that this type of violence can also include spontaneous vigilante mobs clashing with other armed groups or attacking civilians. While a "Mob violence" event often involves unarmed or crudely armed rioters, on rare occasions, it can involve violence by people associated with organized groups and/or using more sophisticated weapons, such as firearms.
        """
'''

EXAMPLE_KEYWORDS = [
    # generated by LLM, selected by hand, testing only
    # use get_keywords(EXAMPLE_SCHEMA) to generate
    'Riot', 'violence', 'demonstrators', 'mobs', 'physical', 'fights', 'property', 'destruction',
    'rioters', 'armed', 'actors', 'protests', 'ViolentDemonstration', 'MobViolence', 
    'clashes', 'vandalism', 'roadblocking', 'civilians', 'disorderly', 'crowds', 'harm', 'disruption', 
    'vigilante', 'mobs', 'clashing', 'civilians', 'armed', 'groups', 'firearms', 'sophisticated', 
    'weapons', 'organized', 'groups', 'Location', 'fatalities', 'targetscivilians', 
    'targetslocaladministrators', 'womentargeted', 'WomenTargetedCategory'
]
EXAMPLE_KEYWORDS = [keyword.lower() for keyword in EXAMPLE_KEYWORDS]

# class MessageRole(str, Enum):
#     ASSISTANT = "assistant"
#     SYSTEM = "system"
#     USER = "user"
#     TOOL = "tool"

def row_to_string(row: dict) -> str:
    out_string = ''
    for k, v in row.items():
        out_string += f"{k}: {v}\n"
    return out_string


def get_keywords(row: Union[dict, str]) -> List[str]:
    row_string = row if isinstance(row, str) else row_to_string(row)
    stream = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": KEYWORD_PROMPT},
            {"role": "user", "content": f"Extract the keywords from the following text: \n{row_string}"},
        ],
        # stream=True,   # stream will print each token at once in generator
    )
    keywords_str = stream.choices[0].message.content
    keywords_lst = keywords_str.split(", ")
    keywords_lst = [''.join([char for char in _str if char.isalnum()]) for _str in keywords_lst]
    return keywords_lst


# first run will take time to download, next runs will only load
def get_dataset(year: Union[int, str], store_filter=False, from_local_path=None):
    if from_local_path is not None:
        return load_dataset(from_local_path)
    dataset = load_dataset("stanford-oval/ccnews", name=str(year))  # name: [2016 ... 2024]
    dataset = dataset.filter(lambda x: x["language"] == "en")
    dataset = dataset.select_columns(["plain_text", "title", "categories", "tags", "published_date"])
    if store_filter:
        dataset.save_to_disk(f"./retrieve_and_fill/dataset/filtered_data")
    return dataset


# Print information about the dataset
FIRST_RUN = False
if FIRST_RUN:
    dataset = get_dataset(year=2024, store_filter=True, from_local_path=None)
else:
    dataset = load_dataset("./retrieve_and_fill/dataset/filtered_data")


dataset.load_from_disk(f"./retrieve_and_fill/dataset/filtered_data")
dataset = dataset["train"]
print(dataset)  # 9,970,029    still 10M articles after filtering
print(type(dataset))


# for i, row in tqdm(enumerate(dataset)):
#     if i < 3:
#         get_keywords(row)
#     print(row)
#     print(i)
#     breakpoint()


# given a schema + keywords input, first retrieve 10 articles from database, then see if
# the schema can be filled by the articles.
def get_schema_filled(
    schema: str,
    keywords: List[str],
    min_occurrences: int = 5,
    max_articles: int = 20,
) -> Dict[str, Any]:
    # iterate through the articles, if there are > 3 keywords present in the content,
    # use the article stop until finding 10 articles
    articles: List[str] = []
    for i, row in tqdm(enumerate(dataset)):
        if len(articles) >= max_articles:
            break
        article_contents = row_to_string(row)
        occurrences = 0
        for keyword in keywords:
            if keyword in article_contents:
                occurrences += 1
        if occurrences >= min_occurrences:
            articles.append(article_contents)
    print(f"Found {len(articles)} relevant articles after scanning {i} articles.")
        
    # now we have 10 articles, we can use the model to fill the schema,
    # call TogetherAI for now, GPT later
    filled_schema = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": FILL_SCHEMA_PROMPT},
            {"role": "user", "content": f"Schema: {schema}\nArticles: {articles}"},
        ],
    )
    filled_schema = filled_schema.choices[0].message.content
    # now check any attibutes not filled, assume they are ... for now
    num_attributes_total = schema.count("...")
    num_attributes_unfilled = filled_schema.count("...")

    # can later easily add other information needed such as average fill length, etc.
    output = {
        "original_schema": schema,
        "keywords": keywords,
        "filled_schema": filled_schema,
        "num_attributes_total": num_attributes_total,
        "num_attributes_unfilled": num_attributes_unfilled,
        "num_attributes_filled": num_attributes_total - num_attributes_unfilled,
    }
    return output


filled_schema = get_schema_filled(EXAMPLE_SCHEMA, EXAMPLE_KEYWORDS)
print(filled_schema['filled_schema'])
breakpoint()