import openai

# Set your OpenAI API key here
openai.api_key = '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'

# Define the initial prompt for schema generation
initial_prompt = '''
Task: Based on user input, dynamically interpret and generate a structured schema with relevant entities, attributes, data types, and relationships.

Instructions:
- Define a single base class with the exact signature (ACLEDEvent, ABC), which subsequent classes will extend.
- For each main entity, define a class with attributes reflecting its properties, all inheriting from the base class.
- Generate multiple subclass types where applicable, each representing specific event variations or details, all extending from the base class.
- The final output should include the base class and multiple subclasses as specified in the example below.
- Use precise field names, data types (e.g., List, Optional, etc.), and descriptions to describe each attribute.
- Do not include ACLEDEvent class in the final output; the final output should only contain the generated schema without example usage.
- In the base class comment, include descriptions of each subtype, as shown in the example below.


Example Workflow:
Generated Schema:

class Battle(ACLEDEvent, ABC): 
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
    location: Location = Field(..., description="Location where the event takes place") fatalities: Optional[int] = Field(
    ...,
    description="Total number of fatalities, if known", )

    
class GovernmentRegainsTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when government forces or their affiliates that are fighting against competing state forces or against a non-state group regain control of a location through armed interaction. This event type is only recorded for the re-establishment of government control and not for cases where competing non-state actors exchange control. Short-lived and/or small- scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash".
    """
    government_force: List[str] = Field( ...,
    description="The government forces or their affiliates that regain control of the territory", )
    adversary: List[str] = Field( ...,
    description="The competing state forces or non-state group that lose control of the territory. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces",
    )

class NonStateActorOvertakesTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when a non-state actor (excluding those operating directly on behalf of the government) or a foreign state actor, through armed interaction, captures territory from an opposing government or non-state actor; as a result, they are regarded as having a monopoly of force within that territory. Short-lived and/or small-scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash" events. In cases where non-state forces fight with opposing actors in a location many times before gaining control, only the final territorial acquisition is recorded as "Non-state actor overtakes territory". All other battles in that location are
    recorded as "ArmedClash". 
    """
    non_state_actor: List[str] = Field( ...,
    description="The non-state actor overtaking territory. Can be Rebel Groups, Political Militias, Identity Militias or External Forces",
    )
    adversary: List[str] = Field(
    ...,
    description="The opposing government or non-state actor from whom the territory was taken. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces",
    )

class ArmedClash(Battle): 
    """
    Is a type of "Battle" event. This event type is used when two organized groups like State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces engage in a battle, and no reports indicate a significant change in territorial control.
    ‘side_1‘ and ‘side_2‘ denote the two sides of the armed clash.
    Excludes demonstrations that turn violent, riots, and other forms of violence that are not organized armed
    clashes. 
    """
    side_1: List[str] = Field( ...,
    description="Groups involved in the clash. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces",
    )
    side_2: List[str] = Field(
    ...,
    description="Groups involved in the clash. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces",
    )
    targets_local_administrators: bool = Field(
    ...,
    description="Whether this violence is affecting local government officials and administrators - including governors, mayors, councilors, and other civil servants.",
    )
    women_targeted: List[WomenTargetedCategory] = Field(
    ...,
    description="The category of violence against women, if any. If this violence is not targeting women, this should be an empty list.",
    )

---

Now, based on the user’s input and strictly follow the instructions, interpret and generate a schema with structured classes, attributes, and descriptions using the above example as a model. Include fields such as location, relevant attributes, participant groups, and actions. Use List or Optional types where applicable. Ensure the schema is detailed and relevant to the user query.
Generate the intiaial schema based on the user input.
'''

# Follow-up prompt template for generating dynamic questions, now incorporating keywords
follow_up_prompt_template = """
Based on the user's initial input:

{user_input}

Generate specific follow-up questions to ask the user that clarify or refine details needed for the schema generation. These questions should focus on gathering additional context or specific requirements related to the user's goals, sector details, time frames, financial metrics, or other critical aspects they wish to include in the analysis. Avoid referencing the schema or using technical schema-related terminology. 
"""


# Function to generate schema based on user input
def generate_initial_schema(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": initial_prompt + f"\nUser: {user_input}"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    initial_schema = response['choices'][0]['message']['content'].strip()
    print("Initial schema generated:\n", initial_schema)
    
    # Save the initial schema to a text file
    with open("initial_schema.txt", "w") as file:
        file.write(initial_schema)
    print("Initial schema saved to initial_schema.txt")
    
    return initial_schema

# Function to generate keywords based on user input
def generate_keywords(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that generates relevant keywords."},
            {"role": "user", "content": f"Extract 10 relevant keywords based on the following input:\n\nUser Input: {user_input}"}
        ],
        max_tokens=50,
        temperature=0.5
    )
    keywords = response['choices'][0]['message']['content'].strip()
    print("Generated Keywords:\n", keywords)
    return keywords

# Function to refine schema based on user feedback
def refine_schema(initial_schema, keywords, user_input):
    refined_inputs = []
    while True:
        # Generate dynamic follow-up questions based on initial user input and keywords, without showing schema details
        follow_up_prompt = follow_up_prompt_template.format(user_input=user_input, keywords=keywords)
        follow_up_response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert schema generator."},
                {"role": "user", "content": follow_up_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        follow_up_question = follow_up_response['choices'][0]['message']['content'].strip()
        
        # Display the follow-up question and get the user's answer
        user_response = input(f"Follow-up Question: {follow_up_question}\nYour Answer: ")
        refined_inputs.append(f"{follow_up_question} {user_response}")
        
        # Refine the schema based on the user's responses
        refine_schema_prompt = (
            f"The initial schema is:\n{initial_schema}\n\n"
            "Refine the schema based on the following user inputs, ensuring it strictly follows the original instructions:\n"
            f"{initial_prompt}\n\nUser Inputs:\n" + "\n".join(refined_inputs)
        )
        refine_response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert schema generator."},
                {"role": "user", "content": refine_schema_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Update the schema with the refined version
        initial_schema = refine_response['choices'][0]['message']['content'].strip()
        print("Updated Schema:\n", initial_schema)
        
        # Ask if the user has further details to specify
        has_more_details = input("Do you have further details you'd like to specify? (no to save / yes for more details): ")
        if has_more_details.lower() == "no":
            break

    # Step 4: Save final schema and keywords to separate text files
    with open("final_schema.txt", "w") as schema_file:
        schema_file.write(initial_schema)
    print("Final schema saved to final_schema.txt")
    
    with open("keywords.txt", "w") as keywords_file:
        keywords_file.write(keywords)
    print("Keywords saved to keywords.txt")

# Main function to execute the schema generation process
def generate_schema(user_input):
    # Step 1: Generate Initial Schema
    initial_schema = generate_initial_schema(user_input)
    
    # Step 2: Generate Keywords based on User Input
    keywords = generate_keywords(user_input)
    
    # Step 3: Refine the Schema with multi-turn conversation, using keywords for context
    refine_schema(initial_schema, keywords, user_input)  

# Example: User prompt to generate a schema for financial trends in the technology sector
user_query = "What are the financial trends in the technology sector in the U.S.?"
generate_schema(user_query)