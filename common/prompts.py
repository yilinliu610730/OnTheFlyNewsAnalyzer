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

If you can't find any information, leave the field empty. Fill as much fields as you can, but only fill the attributes that you can find in the articles.
Don't change the schema format or anything else from the Schema defintion such as class name, attribute names, attribute types, etc.
Don't include any other information in the output other than the filled schema, no explanation needed.
'''


FINAL_ANSWER_PROMT = '''
Given the following filled schema instances, please answer the following user query in natual language. Be clear and concise in your answer.
Your answer should align with the provided information in the filled schema instances.

The filled schema instances are:
{}

The user query is:
{}

Be sure to always include the key statistics in the events provided. For instance, given the instances of stock fluctuations like:
StockFluctuation(
    stock_name="Apple",
    fluctation_price=100,
    fluctation_rate=0.1
)
StockFluctuation(
    stock_name="Nvidia",
    fluctation_price=50,
    fluctation_rate=0.2
)
StockFluctuation(
    stock_name="Microsoft",
    fluctation_price=-20,
    fluctation_rate=...
)
You should always include key statistics such as max flucation price is 100, min fluctuation rate is -20, average fluctuation rate is 0.15 (skip the missing value).
And also summarize other information into natural languages.
'''

REFINE_SCHEMA_FROM_INSTANCES_PROMPT = '''
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
{}

Which was generated using an initial prompt:
{}

The tuples are:
{}

Make sure your output will follow the original schema format and will be a valid schema. Don't change anything in the base class schame
However, you are free to do any of the following:
1) Change the name or description of the or any of the child classes
2) Add new child classes with descriptions and fields properly defined
3) Remove child classes that are not relevant
4) Add new fields to any of the child classes
5) Remove fields that are not relevant
'''