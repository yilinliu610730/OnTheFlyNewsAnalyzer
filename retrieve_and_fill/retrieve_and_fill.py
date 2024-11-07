import os
import sys
from datasets import load_dataset
from tqdm import tqdm
from typing import Union, List, Any, Dict, Tuple
from collections import defaultdict
from tqdm import tqdm
import openai
openai.api_key = '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'


FIRST_RUN = False
DATA_PATH = "./dataset/filtered_data"
MODEL_CHOICES = [
    "gpt-4",
    "gpt-4-turbo",
]
MODEL_NAME = MODEL_CHOICES[1]

KEYWORD_PROMPT = f'''
You are a virtual assistance model and you need to read the given text and generate a list of keywords that best describe the text.
Notice you need to both summarize the text and generate a list of keywords, separated by commas for example: "investment, growth, innovation".
Don't include any other information in the output other than the keywords. Max output 20 keywords. Each keyword should be in natural language,
for instance, write "venture capital" instead of "VentureCapital" or "ventureCapital" as the later ones are not English terms.
Finally, don't include any keyword that is too general, such as "US", "technology"; or too vague, such as "time", "people".
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

class InvestmentReceived(FinancialTrend):
    """
    This subtype of "Financial Trend" is used when there is a significant rise in the level of investments within the technology sector. This can include increases in venture capital funding, growth in private equity stakes, or enhancements in other forms of financial injections into tech companies.
    """
    investment_type: List[str] = Field(..., description="Types of investments observed to increase such as venture capital, private equity, etc.")
    amount: float = Field(..., description="The monetary value of the investment increase.")
    unit: str = Field(..., description="The currency and unit in which the investment increase is measured. Such as Million USD, Billion USD, etc.")
    companies_involved: Optional[List[str]] = Field(None, description="List of key companies that received these investments. Such as technology startups, established tech firms, etc.")

class InvestmentMade(FinancialTrend):
    """
    This subtype of "Financial Trend" is used when there is a significant rise in the level of investments within the technology sector. This can include increases in venture capital funding, growth in private equity stakes, or enhancements in other forms of financial injections into tech companies.
    """
    investment_type: List[str] = Field(..., description="Types of investments observed to increase such as venture capital, private equity, etc.")
    amount: float = Field(..., description="The monetary value of the investment increase.")
    unit: str = Field(..., description="The currency and unit in which the investment increase is measured. Such as Million USD, Billion USD, etc.")
    companies_involved: Optional[List[str]] = Field(None, description="List of key companies that made these investments. Such as venture capital firms, private equity funds, etc.")

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

# raw schema to schema by class name, with parent class combined with child classes
def process_schema(raw_schema: str) -> Dict[str, str]:
    schema_by_class = raw_schema.split("class ")[1:]
    schema_by_class = [f"class {schema}" for schema in schema_by_class]
    # get the parent class combine with each child classes
    schema_by_class = [schema_by_class[0] + schema for schema in schema_by_class[1:]]
    # class name to entire class SCHEMA string
    return {schema.split("class ")[2].split("(")[0]: schema for schema in schema_by_class}

def process_keywords(keywords: str) -> List[str]:
    return [word.lower() for word in keywords]

EXAMPLE_L0_KEYWORDS = [
    'u.s.', 'tech'
]
# print(process_keywords(EXAMPLE_L0_KEYWORDS))
# breakpoint()
EXAMPLE_L1_KEYWORDS = [
    'Financial', 'trends', 'Technology sector', 'market', 'Investment', 'Innovation',
    'Growth', 'Market analysis', 'startups', 'Venture capital', 'Economic', 'stock',
    'revenue'
]

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
    keywords_str = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": KEYWORD_PROMPT},
            {"role": "user", "content": f"Extract the keywords from the following text: {row_string}"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    keywords_str = keywords_str['choices'][0]['message']['content'].strip()
    keywords_lst = keywords_str.split(", ")
    # keywords_lst = [''.join([char for char in _str if char.isalnum()]) for _str in keywords_lst]
    keywords_lst = [keyword.lower() for keyword in keywords_lst]
    return keywords_lst


# first run will take time to download, next runs will only load
def get_dataset(year: Union[int, str], store_and_filter=False):
    dataset = load_dataset("stanford-oval/ccnews", name=str(year))  # name: [2016 ... 2024]
    dataset = dataset.filter(lambda x: x["language"] == "en")
    dataset = dataset.select_columns(["plain_text", "title", "categories", "tags", "published_date"])
    if store_and_filter:
        dataset.save_to_disk(DATA_PATH)
    return dataset


# Print information about the dataset
try:
    dataset = load_dataset(DATA_PATH)
except:
    dataset = get_dataset(year=2024, store_and_filter=True)  # download, process, store

dataset = dataset["train"]
print(dataset)        # 9,970,029    still 10M articles after filtering
print(f"{type(dataset) = }")


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
def ask_user_response(filled_schemas_by_class: Dict[str, Dict[int, Tuple[str, str]]]) -> None:
    for schema_class, filled_schemas in filled_schemas_by_class.items():
        print(f"\n\n*** Starting response collection for schema class: {schema_class} ***")
        for article_index, (filled_schema, _) in filled_schemas.items():
            article_content = row_to_string(dataset[article_index])
            user_response = input(
                f'''Please provide feedback for the filled schema for article:\n{article_content}\nfilled schma: {filled_schema}\n
                Please put "no" or "n" or "none" if you don't have any feedback.
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
    ask_user: bool = True
) -> Dict[str, Dict[int, Tuple[str, str]]]:
    
    schema_by_class = process_schema(schema)    
    L0_keywords = process_keywords(L0_keywords)
    L1_keywords = process_keywords(L1_keywords)


    # output is a dictionary key being schema class name, value being a dictionary with key being article index
    # and value being a tuple of (filled schema, user response)

    # iterate through the articles, if there are > 3 keywords present in the content,
    # use the article stop until finding 10 articles

    # article index to article content
    articles: Dict[int, str] = {}
    for i, row in tqdm(enumerate(dataset)):
        article_contents = row_to_string(row)
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
        L2_keywords = get_keywords(schema)
        article_to_filled_schema = {}
        for article_index, article in tqdm(articles.items()):

            # L2 retrieval, need to satisfy narrowed down keywords
            if count_keyword_occurences(article, L2_keywords) < 1:
                print("not satisfying schema specific (L2) keywords")
                continue

            filled_schema = openai.ChatCompletion.create(
                model="gpt-4-turbo",
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
    
    if ask_user:
        ask_user_response(filled_schemas_by_class)

    return filled_schemas_by_class

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