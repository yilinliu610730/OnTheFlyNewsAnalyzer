import os
import sys
from together import Together
import together
import together.types.chat_completions
from datasets import load_dataset
from tqdm import tqdm
from typing import Union, List, Any, Dict
from collections import defaultdict
from tqdm import tqdm
import openai
openai.api_key = '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'

together_api_key = "cd7b5b267e7c7118ef2a4d6b9f59898a1d1fd9ae1551fb9b627b6d5c3d7e94ca"
os.environ["TOGETHER_API_KEY"] = together_api_key  # export TOGETHER_API_KEY=together_api_key
client = Together()
FIRST_RUN = False

# complete list : https://api.together.ai/models.
model_choices = [
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "codellama/CodeLlama-70b-Instruct-hf",
    "deepseek-ai/deepseek-coder-33b-instruct",
    "Qwen/Qwen2-72B-Instruct",
]
MODEL_NAME = model_choices[1]

KEYWORD_PROMPT = f'''
You are a virtual assistance model and you need to read the given text and generate a list of keywords that best describe the text.
Notice you need to both summarize the text and generate a list of keywords. Your output should be easily transferable to a list
of string in Python. Don't include any other information in the output other than the keywords.
'''


FILL_SCHEMA_PROMPT = f'''
You are a virtual assistance model given a list of articles and a schema, you need to fill the schema by information
you find in the articles. The schema is in string but follows a Python Class definition format. You need to fill in the attributes
of the class with any information you found from any of the articles. In the Python format, create an class object with actual
information you found. For example:

Given the schema in format of Python class definition:
    class ViolenceAgainstCivilians(ACLEDEvent, ABC):
        location: Location = Field(...)
        targets_local_administrators: bool = Field(...)
        women_targeted: List[WomenTargetedCategory] = Field(...)
    
    class SexualViolence(ViolenceAgainstCivilians):
        fatalities: Optional[int] = Field(...)
        perpetrators: List[str] = Field(...)
        victims: List[str] = Field(...)
        

A filled schema should follow the format of Python class initialization (not definition) you should initialize the class using only the child class name,
but with fields from both parent and child classes. Filled with actual information you found in the articles. For example:
    SexualViolence(
        location="Paris",
        targets_local_administrators=True,
        women_targeted=[],
        fatalities=10,
        perpetrators=["John Doe"],
        victims=["Alice", "Bob"]
    )

If you can't find any information, leave the ... as is. Fill as much fields as you can, but only fill the attributes that you can find in the articles.
Don't change the schema format or anything else from the Schema defintion such as class name, attribute names, attribute types, etc.
Don't include any other information in the output other than the filled schema, no explanation needed.
'''

EXAMPLE_SCHEMA = '''
class FinancialTrend(ACLEDEvent, ABC):
    """
    A "Financial Trend" event describes the patterns and tendencies in financial metrics observed over time within a specific sector. For the technology sector, these trends can represent changes in stock prices, market capitalization, revenue growth, investment rates, or other economic indicators relevant to tech companies in the U.S. This event type captures both positive and negative financial developments and can highlight periods of growth, decline, or stability.
    - InvestmentIncrease: Represents a significant rise in investments within the technology sector, including venture capital, private equity, and public market investments.
    - MarketCapGrowth: Reflects an increase in the overall market capitalization of tech companies, indicating a general market valuation increase.
    - RevenueGrowth: Tracks the revenue increases across tech companies, which may result from new products, expansion into new markets, or overall industry growth.
    - StockPriceFluctuation: Captures the variations in stock prices of tech companies, which could be influenced by market trends, company performance, or external economic factors.
    """
    sector: str = Field(..., description="The specific sector under analysis, here being 'technology'.")
    country: str = Field(..., description="The country of interest, here the 'U.S.'.") 
    period: str = Field(..., description="The time frame over which the financial trends are observed.")

class InvestmentIncrease(FinancialTrend):
    """
    This subtype of "Financial Trend" is used when there is a significant rise in the level of investments within the technology sector. This can include increases in venture capital funding, growth in private equity stakes, or enhancements in other forms of financial injections into tech companies.
    """
    investment_type: List[str] = Field(..., description="Types of investments observed to increase such as venture capital, private equity, etc.")
    amount: float = Field(..., description="The monetary value of the investment increase.")
    companies_involved: Optional[List[str]] = Field(None, description="List of key companies that benefited from these investments.")

class MarketCapGrowth(FinancialTrend):
    """
    This subtype of "Financial Trend" reflects an increase in the overall market capitalization of companies within the technology sector, suggesting a rise in market valuation.
    """
    average_increase_percentage: float = Field(..., description="The average percentage increase in market capitalization.")
    leading_companies: List[str] = Field(..., description="Companies leading in market cap growth.")

class RevenueGrowth(FinancialTrend):
    """
    Represents growth in revenue across technology sector companies, which could be due to factors like market expansion, product launches, or increased consumer demand.
    """
    average_growth_rate: float = Field(..., description="The average revenue growth rate observed.")
    key_contributors: List[str] = Field(..., description="Major companies contributing to this revenue growth.")

class StockPriceFluctuation(FinancialTrend):
    """
    Captures the fluctuations in stock prices of technology sector companies, which can be influenced by various internal and external economic factors.
    """
    volatility_index: float = Field(..., description="A measure of the price volatility observed among tech stocks.")
    impacted_companies: List[str] = Field(..., description="Companies whose stock prices have shown significant fluctuations.")
'''

SCHEMA_BY_CLASS = EXAMPLE_SCHEMA.split("class ")[1:]
SCHEMA_BY_CLASS = [f"class {schema}" for schema in SCHEMA_BY_CLASS]
# get the parent class combine with each child classes
SCHEMA_BY_CLASS = [SCHEMA_BY_CLASS[0] + schema for schema in SCHEMA_BY_CLASS[1:]]
# class name to entire class SCHEMA string
SCHEMA_BY_CLASS = {schema.split("class ")[2].split("(")[0]: schema for schema in SCHEMA_BY_CLASS}

EXAMPLE_KEYWORDS = [
    'Financial trends', 'Technology sector', 'U.S. market', 'Investment', 'Innovation',
    'Growth rates', 'Market analysis', 'Tech startups', 'Venture capital', 'Economic impact'
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
        dataset.save_to_disk(f"./dataset/filtered_data")
    return dataset


# Print information about the dataset
dataset = get_dataset(year=2024, store_filter=True, from_local_path=None) if FIRST_RUN \
    else load_dataset("./dataset/filtered_data")


dataset.load_from_disk(f"./dataset/filtered_data")
dataset = dataset["train"]
print(dataset)  # 9,970,029    still 10M articles after filtering
print(type(dataset))



# given a schema + keywords input, first retrieve 10 articles from database, then see if
# the schema can be filled by the articles.
def get_schema_filled(
    schema_by_class: Dict[str, str],
    keywords: List[str],
    min_occurrences: int = 3,
    max_articles: int = 5,
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
        
    filled_schemas_by_class = defaultdict(list) # class name to filledd schema (string in format of class obj)
    for schema_class, schema in schema_by_class.items():
        for article in tqdm(articles):
            # filled_schema = client.chat.completions.create(
            #     model=MODEL_NAME,
            #     messages=[
            #         {"role": "system", "content": FILL_SCHEMA_PROMPT},
            #         {"role": "user", "content": f"Schema: {schema}\nArticles: {article}"},
            #     ],
            # )
            # filled_schema = filled_schema.choices[0].message.content

            refine_response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": FILL_SCHEMA_PROMPT},
                    {"role": "user", "content": f"Schema: {schema}\nArticles: {article}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            filled_schema = refine_response['choices'][0]['message']['content'].strip()
            filled_schemas_by_class[schema_class].append(filled_schema)

    return filled_schemas_by_class


filled_schema = get_schema_filled(SCHEMA_BY_CLASS, EXAMPLE_KEYWORDS)
for schema_class, filled_schemas in filled_schema.items():
    print(f"Schema class: {schema_class}")
    for filled_schema in filled_schemas:
        print(filled_schema)
        print("\n\n")