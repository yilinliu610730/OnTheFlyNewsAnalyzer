KEYWORD_PROMPT = f'''
You are a virtual assistance model and you need to read the given text and generate a list of keywords that best describe the text.
Notice you need to both summarize the text and generate a list of keywords, separated by commas for example: "investment, growth, innovation".
Don't include any other information in the output other than the keywords. Max output 20 keywords. Each keyword should be in natural language,
for instance, write "venture capital" instead of "VentureCapital" or "ventureCapital" as the later ones are not English terms.
Finally, don't include any keyword that is too general, such as "u.s.", "technology"; or too vague, such as "time", "people". Also, split the
keywords when you can. For instance, if the keyword is "u.s. supreme court", you should split them into 2 keywords, "u.s." and "supreme court".
Never include keywords more than 3 terms. Split them or remove them.
'''

# Define the initial prompt for schema generation
GENERATE_SCHEMA_INSTR = '''
Task: Based on user input, dynamically interpret and generate a structured schema with relevant entities, attributes, data types, and relationships.

Instructions:
- Define a single base class with the exact signature (ABC), which subsequent classes will extend.
- For each main entity, define a class with attributes reflecting its properties, all inheriting from the base class.
- Generate multiple subclass types where applicable, each representing specific event variations or details, all extending from the base class.
- The final output should include the base class and multiple subclasses as specified in the example.
- Use precise field names, data types (e.g., List, Optional, etc.), and descriptions to describe each attribute.
- Ensure that each field is defined with the exact signature format, using `Field(..., description="")` to indicate required fields and provide a description. Note that ... should not be replaced with None or any other value.
- Ensure that each field is in one line. For instance use `location: Location = Field(..., description="")`. Instead of:
    location: Location = Field(
        ...,
        description=""
    )
- In the base class comment, include descriptions of each subtype, as shown in the example.
- Keep the schema generic, focusing only on general structure and types.
- Use placeholders where specific details would go (e.g., sector, time period) rather than hardcoded values.
- Do not add pre-set values or defaults in the fields unless absolutely necessary; these should be determined by user inputs and follow-up responses.
- Ensure the schema is a txt file.
'''

# Example schema provided separately 
GENERATE_SCHEMA_EXAMPLE =  '''

class Battle(ABC): 
    """
    A "Battle" event is defined as a violent interaction between two organized armed groups at a particular time and location. "Battle" can occur between armed and organized state, non-state, and external groups,
    and in any combination therein. There is no fatality minimum necessary for inclusion. Civilians can be harmed in the course of larger "Battle" events if they are caught in the crossfire, for example, or affected by strikes on military targets, which is commonly referred to as "collateral damage" (for more,
    see Indirect Killing of Civilians). When civilians are harmed in a "Battle" event, they are not recorded as an "Actor", nor is a separate civilian-specific event recorded. If any civilian fatalities are reported as part of a battle, they are aggregated in the "Fatalities" field for the "Battle" event.
    The specific elements of the definition of a "Battle" event are as follows:
    Violent interaction: the exchange of armed force, or the use of armed force at close distance, between
    armed groups capable of inflicting harm upon the opposing side.
    Organized armed groups: collective actors assumed to be operating cohesively around an agenda, identity,
    or political purpose, using weapons to inflict harm. These groups frequently have a designated name and
    stated agenda.
    The "Battle" event type may include: ground clashes between different armed groups, ground clashes between
    armed groups supported by artillery fire or airstrikes, ambushes of on-duty soldiers or armed militants , exchanges of artillery fire, ground attacks against military or militant positions, air attacks where ground forces are able to effectively fire on the aircraft, and air-to-air combat.
    Cases where territory is regained or overtaken without resistance or armed interaction are not recorded as "Battle" events. Instead, they are recorded as "NonStateActorOvertakesTerritory" under the "
    StrategicDevelopment" event type
    "Battle" event type has the following subtypes:
    - GovernmentRegainsTerritory: Government forces or their affiliates regain control of a location from
    competing state forces or non-state groups through armed interaction.
    - NonStateActorOvertakesTerritory: A non-state actor or foreign state actor captures territory from an
    opposing government or non-state actor through armed interaction, establishing a monopoly of force within that territory.
    - ArmedClash: Armed, organized groups engage in a battle without significant changes in territorial control.
    """
    location: Location = Field(..., description="Location where the event takes place") 
    fatalities: Optional[int] = Field(..., description="Total number of fatalities, if known")

    
class GovernmentRegainsTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when government forces or their affiliates that are fighting against competing state forces or against a non-state group regain control of a location through armed interaction. This event type is only recorded for the re-establishment of government control and not for cases where competing non-state actors exchange control. Short-lived and/or small- scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash".
    """
    government_force: List[str] = Field(..., description="The government forces or their affiliates that regain control of the territory")
    adversary: List[str] = Field(..., description="The competing state forces or non-state group that lose control of the territory. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces")

class NonStateActorOvertakesTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when a non-state actor (excluding those operating directly on behalf of the government) or a foreign state actor, through armed interaction, captures territory from an opposing government or non-state actor; as a result, they are regarded as having a monopoly of force within that territory. Short-lived and/or small-scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash" events. In cases where non-state forces fight with opposing actors in a location many times before gaining control, only the final territorial acquisition is recorded as "Non-state actor overtakes territory". All other battles in that location are
    recorded as "ArmedClash". 
    """
    non_state_actor: List[str] = Field(..., description="The non-state actor overtaking territory. Can be Rebel Groups, Political Militias, Identity Militias or External Forces")
    adversary: List[str] = Field(..., description="The opposing government or non-state actor from whom the territory was taken. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces")

class ArmedClash(Battle): 
    """
    Is a type of "Battle" event. This event type is used when two organized groups like State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces engage in a battle, and no reports indicate a significant change in territorial control.
    'side_1' and 'side_2' denote the two sides of the armed clash.
    Excludes demonstrations that turn violent, riots, and other forms of violence that are not organized armed
    clashes. 
    """
    side_1: List[str] = Field(..., description="Groups involved in the clash. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces")
    side_2: List[str] = Field(..., description="Groups involved in the clash. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces")
    targets_local_administrators: bool = Field(..., description="Whether this violence is affecting local government officials and administrators - including governors, mayors, councilors, and other civil servants.")
    women_targeted: List[WomenTargetedCategory] = Field(..., description="The category of violence against women, if any. If this violence is not targeting women, this should be an empty list.")

class Protest(ABC):
    """
    A "Protest" event is defined as an in-person public demonstration of three or more participants in which the participants do not engage in violence, though violence may be used against them. Events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private institution. The following are not recorded as " Protest" events: symbolic public acts such as displays of flags or public prayers (unless they are accompanied by a demonstration); legislative protests, such as parliamentary walkouts or members of parliaments staying silent; strikes (unless they are accompanied by a demonstration); and individual acts such as self-harm actions like individual immolations or hunger strikes.
    Protestor are noted by generic actor name "Protestor". If they are representing a group, the name of that group is also recorded in the field.
    "Protest" event type has the following subtypes:
    - ExcessiveForceAgainstProtestors: Peaceful protestor are targeted with lethal violence or violence resulting in serious injuries by state or non-state actors.
    - ProtestWithIntervention: A peaceful protest is physically dispersed or suppressed without serious injuries, or protestor interact with armed groups or rioters without serious harm, or protestors are arrested.
    - PeacefulProtest: Demonstrators gather for a protest without engaging in violence or rioting and are not met with force or intervention.
    """
    location: Location = Field(..., description="Location where the event takes place") 
    protestors: List[str] = Field(..., description="List of protestor groups or individuals involved in the protest")

class ExcessiveForceAgainstProtestors(Protest): 
    """
    Is a type of "Protest" event (Protest events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private
    institution.) This event type is used when individuals are engaged in a peaceful protest and are targeted with lethal violence or violence resulting in serious injuries (e.g. requiring hospitalization) . This includes situations where remote explosives, such as improvised explosive devices, are used to target protestors, as well as situations where non-state actors, such as rebel groups, target protestors .
    """
    # Possible "Interaction" codes include: 16, 26, 36, 46, 56, and 68.
    perpetrators: List[str] = Field(..., description="Entities perpetrating the violence. Can be State Forces, Rebel Groups, Political Militias , Identity Militias, External Forces")
    targets_civilians: bool = Field(..., description="Indicates if the 'ExcessiveForceAgainstProtestors' event is mainly or only targeting civilians. E.g. state forces using lethal force to disperse peaceful protestors.")
    fatalities: Optional[int] = Field(..., description="Total number of fatalities, if known")

class ProtestWithIntervention(Protest): 
    """
    Is a type of "Protest" event. This event type is used when individuals are engaged in a peaceful protest during which there is a physically violent attempt to disperse or suppress the protest, which resulted in arrests, or minor injuries . If there is intervention, but not violent, the event is recorded as " PeacefulProtest" event type.
    """
    perpetrators: List[str] = Field(..., description="Group(s) or entities attempting to disperse or suppress the protest")
    fatalities: Optional[int] = Field(..., description="Total number of fatalities, if known")

class PeacefulProtest(Protest): 
    """
    Is a type of "Protest" event (Protest events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private
    institution.) This event type is used when demonstrators gather for a protest and do not engage in violence or other forms of rioting activity, such as property destruction, and are not met with any sort
    of violent intervention. 
    """
    # Possible "Interaction" codes include: 60, 66, and 67.
    counter_protestors: List[str] = Field(..., description="Groups or entities engaged in counter protest, if any")
---

Now, based on the user's input and strictly follow the instructions, interpret and generate a schema with structured classes, attributes, and descriptions using the above example as a model. Include fields such as location, relevant attributes, participant groups, and actions. Use List or Optional types where applicable. Ensure the schema is detailed and relevant to the user query.
Generate the initial schema based on the user input.
'''

# Define prompt template for generating all follow-up questions
FOLLOW_UP_PROMPT_TEMPLATE_ALL = """
Based on the user's initial input:

{user_input}

Generate 5 unique follow-up questions that clarify or refine details needed for schema generation. Each question should focus on a different aspect of the user's requirements, such as timeframe, specific segments, financial metrics, and geographic scope. Ensure each question is unique, and avoid repeating similar questions.
"""


REFINE_SCHEMA_PROMPT_TEMPLATE = """
You are a virtual assistant tasked with refining a schema based on user input. The schema is written in Python `class` definition format. Your goal is to update the schema by adding or revising fields based on each user response, while maintaining the structure and clarity of the schema.

### Initial Schema
The initial schema is:

{initial_schema}

### Instructions
1. Use the initial schema as a starting point. Add or revise fields only when explicitly indicated by user input. Avoid modifying the structure unnecessarily.
2. Follow these specific guidelines:
    - Define a single base class named `ABC` as the foundation, with other classes extending from it as needed.
    - Use precise field definitions. Replace placeholders (`...`) with concrete values or type definitions.
    - Each field must include a clear, concise description provided in the `Field` function's `description` parameter.
3. For specific inputs about segments or focus areas:
    - Add boolean fields based on the user’s response. For example:
      ```python
      is_software: bool = Field(True, description="Indicates focus on the software segment")
      ```
4. For inputs related to timeframes:
    - Add `start_date` and `end_date` fields using the `YYYY-MM-DD` format. For example:
      ```python
      start_date: datetime = Field(datetime(2024, 1, 1), description="Start date of the analysis period")
      end_date: datetime = Field(datetime(2024, 12, 31), description="End date of the analysis period")
      ```
5. For general responses such as "all", "any", "either", or anything relevant:
    - Define an `Enum` class to enumerate all possible options.
    - Add a field capturing the selected options. For example:
      ```python
      class FinancialMetric(Enum):
          REVENUE_GROWTH = "Revenue Growth"
          PROFIT_MARGINS = "Profit Margins"
          STOCK_PERFORMANCE = "Stock Performance"
          INVESTMENT_TRENDS = "Investment Trends"
      
      metrics: List[FinancialMetric] = Field(
          [FinancialMetric.REVENUE_GROWTH, FinancialMetric.PROFIT_MARGINS, FinancialMetric.STOCK_PERFORMANCE, FinancialMetric.INVESTMENT_TRENDS],
          description="List of all selected financial metrics"
      )
      ```

### Example Applications
1. **Specific Input**:
    - Follow-Up Question: "Are there particular segments within the technology sector, such as software, hardware, or telecom, that you would like to focus on?"
    - User Response: "Software"
    - Update the schema by adding the field:
      ```python
      is_software: bool = Field(True, description="Indicates focus on the software segment")
      ```

2. **Timeframe Input**:
    - Follow-Up Question: "What specific timeframe are you interested in analyzing for financial trends?"
    - User Response: "Past year"
    - Update the schema by adding the fields:
      ```python
      start_date: datetime = Field(datetime(2024, 1, 1), description="Start date of the analysis period")
      end_date: datetime = Field(datetime(2024, 12, 31), description="End date of the analysis period")
      ```

3. **General Input**:
    - Follow-Up Question: "Which financial metrics are most important to you in this analysis, such as revenue growth, profit margins, stock performance, or investment trends?"
    - User Response: "All metrics"
    - Update the schema by defining an `Enum` and adding the field:
      ```python
      class FinancialMetric(Enum):
          REVENUE_GROWTH = "Revenue Growth"
          PROFIT_MARGINS = "Profit Margins"
          STOCK_PERFORMANCE = "Stock Performance"
          INVESTMENT_TRENDS = "Investment Trends"
      
      metrics: List[FinancialMetric] = Field(
          [FinancialMetric.REVENUE_GROWTH, FinancialMetric.PROFIT_MARGINS, FinancialMetric.STOCK_PERFORMANCE, FinancialMetric.INVESTMENT_TRENDS],
          description="List of all selected financial metrics"
      )
      ```

### Follow-Up Context
- **Follow-Up Question**:
  {follow_up_question}
- **User Response**:
  {user_response}

Update the schema accordingly, ensuring all modifications adhere strictly to the instructions and provided examples.
"""


FILL_SCHEMA_PROMPT = f'''
You are a virtual assistance model given a news articles and a schema, you need to fill the schema by information
you find in the article. The schema is in string but follows a Python Class definition format. You need to fill in the attributes
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
Don't include any other information in the output other than the filled schema, no explanation needed.  Carefully read and analyze the news article,
notice that the news article is usually published on a specific date representing what happened on that day or a few days before.

Here is a examples, assume the article is:
The Dow soared 575 points on the day, its most winning day of 2024. The technology sector led declines among the S&P 500 sectors. The U.S. personal consumption expenditures (PCE) price index increased 0.3% last month. Traders of futures tied to the Fed policy rate added to bets of roughly even odds that the central bank will begin to cut rates in September and boosted the chances of a second rate cut in December. S&P 500 gained 44.53 points, or 0.85%, to end at 5,280.01 points, while the Nasdaq Composite lost 2.06 points, or 0.01%, to 16,735.02. The Dow Jones Industrial Average rose 574.84 points, or 1.51%, to 38,686.32. Tech and chip stocks, which have led Wall Street\'s recent rally, retreated this week as a spike in Treasury yields pressured riskier assets. Among gainers, Zscaler jumped after the security solutions provider forecast fourth-quarter results above estimates. Gap surged after the apparel maker raised its annual sales forecast and its first-quarter results beat market expectations. Nvidia’s stock has skyrocketed by over 500% since early 2023, fueled by earnings growth.

If the schema is about Merge or Acquisition, you should leave the entire schema empty, as there is no information about it in the article. For instance:
MergerAndAcquisition(
    purchaser=...,
    target=...,
    deal_value=...
)

If the schema is about Stock Fluctuation in 2024 on technology. You should clearly output multiple filled schemas, 
as there are multiple information about stock fluctuation in the article. An example filled schemas could be:
StockFluctuation(
    affected_party="S&P 500",
    price_change=44.53,
    percentage_change=0.0085,  # 0.85% also acceptable
    reason="bet on Fed policy rate"
)
StockFluctuation(
    affected_party="Nasdaq Composite",
    price_change=-2.06,
    percentage_change=-0.0001,  # -0.01% also acceptable
    reason="bet on Fed policy rate"
)
StockFluctuation(
    affected_party="Dow Jones Industrial Average",
    price_change=574.84,
    percentage_change=0.0151,  # 1.51% also acceptable
    reason="bet on Fed policy rate"
)
StockFluctuation(
    affected_party="Zscaler",
    price_change=...,
    percentage_change=...,
    reason="forecast above estimates"
)

However, do not include NVIDIA or GAP's stock fluctuation, as even though they were mentioned in the article, NVIDIA's event happened in 2023 not 2024.
And GAP is not a technology company, so it is not relevant to the schema. You will be given detailed instructions but it is your job to carefully 
analyze whether each event matches the criteria. If they fail any of the criteria (such as year or sector), ignore the schema.

If the schema is about financial index trend, an example filled schema could be:
FinancialIndexTrend(
    index_name="Personal Consumption Expenditures (PCE) Price Index",
    trend="gain",
    rate=0.03%
)
'''


FINAL_ANSWER_PROMT = '''
Given the following filled schema instances, please answer the following user query in natual language. Be clear and very concise in your sentences, but remember to
mention the specific numbers you see in the schema instances. Your final summarized answer should align with the provided information in the filled schema instances.

The schema definition and description is:
{}

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
Always include key statistics in your final report such as max flucation price is 100, min fluctuation rate is -20, average fluctuation rate is 0.15 (skip the missing value).
Make sure your final summary aligns with the datestamp in the schema instances if any. For instance, If the U.S. government responds at a specific date, 
make sure your answer point out the date instead of making it sound like a long-term decision over a long-term time frame.
'''

FINAL_ANSWER_PROMT_NAIVE = '''
Given the following articles, please answer the following user query in natual language. Be clear and concise in your answer.
Your answer should align with the provided information in the articles, if the article is irrelevant to the query, ignore it.

User query:
{}

Articles:
{}
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