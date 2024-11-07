import openai

# Set your OpenAI API key here
openai.api_key = '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'

# Define the initial prompt for schema generation
instructions = '''
Task: Based on user input, dynamically interpret and generate a structured schema with relevant entities, attributes, data types, and relationships.

Instructions:
- Define a single base class with the exact signature (ACLEDEvent, ABC), which subsequent classes will extend. ACLEDEvent should not be defined.
- For each main entity, define a class with attributes reflecting its properties, all inheriting from the base class.
- Generate multiple subclass types where applicable, each representing specific event variations or details, all extending from the base class.
- The final output should include the base class and multiple subclasses as specified in the example.
- Use precise field names, data types (e.g., List, Optional, etc.), and descriptions to describe each attribute.
- Ensure that each field is defined with the exact signature format, using `Field(..., description="")` to indicate required fields and provide a description. Note that ... should not be replaced with None or any other value.
- Do not include ACLEDEvent class in the final output; the final output should only contain the generated schema without example usage.
- In the base class comment, include descriptions of each subtype, as shown in the example.
- Keep the schema generic, focusing only on general structure and types.
- Use placeholders where specific details would go (e.g., sector, time period) rather than hardcoded values.
- Do not add pre-set values or defaults in the fields unless absolutely necessary; these should be determined by user inputs and follow-up responses.
- Ensure the schema is a txt file.
'''

# Example schema provided separately 
example_schema = '''

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
    location: Location = Field(..., description="Location where the event takes place") 
    fatalities: Optional[int] = Field(
        ...,
        description="Total number of fatalities, if known", 
    )

    
class GovernmentRegainsTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when government forces or their affiliates that are fighting against competing state forces or against a non-state group regain control of a location through armed interaction. This event type is only recorded for the re-establishment of government control and not for cases where competing non-state actors exchange control. Short-lived and/or small- scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash".
    """
    government_force: List[str] = Field( 
        ...,
        description="The government forces or their affiliates that regain control of the territory", 
    )
    adversary: List[str] = Field( 
        ...,
        description="The competing state forces or non-state group that lose control of the territory. Can be State Forces, Rebel Groups, Political Militias, Identity Militias or External Forces",
    )

class NonStateActorOvertakesTerritory(Battle): 
    """
    Is a type of "Battle" event. This event type is used when a non-state actor (excluding those operating directly on behalf of the government) or a foreign state actor, through armed interaction, captures territory from an opposing government or non-state actor; as a result, they are regarded as having a monopoly of force within that territory. Short-lived and/or small-scale territorial exchanges that do not last for more than one day are recorded as "ArmedClash" events. In cases where non-state forces fight with opposing actors in a location many times before gaining control, only the final territorial acquisition is recorded as "Non-state actor overtakes territory". All other battles in that location are
    recorded as "ArmedClash". 
    """
    non_state_actor: List[str] = Field( 
        ...,
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
    side_1: List[str] = Field( 
        ...,
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

class Protest(ACLEDEvent, ABC):
    """
    A "Protest" event is defined as an in-person public demonstration of three or more participants in which the participants do not engage in violence, though violence may be used against them. Events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private institution. The following are not recorded as " Protest" events: symbolic public acts such as displays of flags or public prayers (unless they are accompanied by a demonstration); legislative protests, such as parliamentary walkouts or members of parliaments staying silent; strikes (unless they are accompanied by a demonstration); and individual acts such as self-harm actions like individual immolations or hunger strikes.
    Protestor are noted by generic actor name "Protestor". If they are representing a group, the name of that group is also recorded in the field.
    "Protest" event type has the following subtypes:
    - ExcessiveForceAgainstProtestors: Peaceful protestor are targeted with lethal violence or violence resulting in serious injuries by state or non-state actors.
    - ProtestWithIntervention: A peaceful protest is physically dispersed or suppressed without serious injuries, or protestor interact with armed groups or rioters without serious harm, or protestors are arrested.
    - PeacefulProtest: Demonstrators gather for a protest without engaging in violence or rioting and are not met with force or intervention.
    """
    location: Location = Field(..., description="Location where the event takes place") 
    protestors: List[str] = Field(
        ...,
        description="List of protestor groups or individuals involved in the protest", 
    )

class ExcessiveForceAgainstProtestors(Protest): 
    """
    Is a type of "Protest" event (Protest events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private
    institution.) This event type is used when individuals are engaged in a peaceful protest and are targeted with lethal violence or violence resulting in serious injuries (e.g. requiring hospitalization) . This includes situations where remote explosives, such as improvised explosive devices, are used to target protestors, as well as situations where non-state actors, such as rebel groups, target protestors .
    """
    # Possible "Interaction" codes include: 16, 26, 36, 46, 56, and 68.
    perpetrators: List[str] = Field( 
        ...,
        description="Entities perpetrating the violence. Can be State Forces, Rebel Groups, Political Militias , Identity Militias, External Forces",
    )
    targets_civilians: bool = Field(
        ...,
        description="Indicates if the ’ExcessiveForceAgainstProtestors’ event is mainly or only targeting civilians. E.g. state forces using lethal force to disperse peaceful protestors.",
    )
    fatalities: Optional[int] = Field( 
        ...,
        description="Total number of fatalities, if known", 
    )

class ProtestWithIntervention(Protest): 
    """
    Is a type of "Protest" event. This event type is used when individuals are engaged in a peaceful protest during which there is a physically violent attempt to disperse or suppress the protest, which resulted in arrests, or minor injuries . If there is intervention, but not violent, the event is recorded as " PeacefulProtest" event type.
    """
    perpetrators: List[str] = Field( 
        ...,
        description="Group(s) or entities attempting to disperse or suppress the protest", 
    )
    fatalities: Optional[int] = Field( 
        ...,
        description="Total number of fatalities, if known", 
    )

class PeacefulProtest(Protest): 
    """
    Is a type of "Protest" event (Protest events include individuals and groups who peacefully demonstrate against a political entity, government institution, policy, group, tradition, business, or other private
    institution.) This event type is used when demonstrators gather for a protest and do not engage in violence or other forms of rioting activity, such as property destruction, and are not met with any sort
    of violent intervention. 
    """
    # Possible "Interaction" codes include: 60, 66, and 67.
    counter_protestors: List[str] = Field(
        ..., description="Groups or entities engaged in counter protest, if any"    
    )
---

Now, based on the user’s input and strictly follow the instructions, interpret and generate a schema with structured classes, attributes, and descriptions using the above example as a model. Include fields such as location, relevant attributes, participant groups, and actions. Use List or Optional types where applicable. Ensure the schema is detailed and relevant to the user query.
Generate the initial schema based on the user input.
'''

# Define prompt template for generating all follow-up questions
follow_up_prompt_template_all = """
Based on the user's initial input:

{user_input}

Generate 10 unique follow-up questions that clarify or refine details needed for schema generation. Each question should focus on a different aspect of the user's requirements, such as timeframe, specific segments, financial metrics, and geographic scope. Ensure each question is unique, and avoid repeating similar questions.
"""


# Function to generate schema based on user input
def generate_initial_schema(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": instructions + example_schema + f"\nUser: {user_input}"}
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

# Function to generate 10 follow-up questions upfront
def generate_follow_up_questions(user_input):
    follow_up_prompt = follow_up_prompt_template_all.format(user_input=user_input)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": follow_up_prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    # Split and filter out empty lines
    questions = [q.strip() for q in response['choices'][0]['message']['content'].split("\n") if q.strip()]
    print("Generated Follow-Up Questions:\n", questions)
    return questions

# Function to generate initial L0 keywords based on user input (limit to 5 keywords)
def generate_L0_keywords(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that generates relevant keywords for initial input."},
            {"role": "user", "content": f"Extract 5 relevant keywords based on the following input:\n\nUser Input: {user_input}.  Keywords should be in format keyword 1, keyword 2, ..."}
        ],
        max_tokens=50,
        temperature=0.5
    )
    keywords = response['choices'][0]['message']['content'].strip().split(', ')[:5]
    print("Generated L0 Keywords:\n", keywords)
    return keywords

# Function to generate follow-up L1 keywords based on both question and user answer (limit to 1-3 keywords)
def generate_L1_keywords(follow_up_question, follow_up_answer):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that generates relevant keywords for follow-up answers based on the full context of the question and answer."},
            {"role": "user", "content": f"Extract 0-3 most relevant keywords based on the following follow-up question and answer.\n\nFollow-up Question: {follow_up_question}\nUser Answer: {follow_up_answer}. Keywords should be in format keyword 1, keyword 2, ..."}
        ],
        max_tokens=50,
        temperature=0.5
    )
    keywords = response['choices'][0]['message']['content'].strip().split(', ')[:3]
    print("Generated L1 Keywords:\n", keywords)
    return keywords

def refine_schema_with_levels(initial_schema, instructions, L0_keywords, user_input):
    follow_up_questions = generate_follow_up_questions(user_input)
    refined_inputs = []
    all_L1_keywords = set()  # Use a set to automatically handle duplicates

    for idx, follow_up_question in enumerate(follow_up_questions):
        user_response = input(f"Follow-up Question {idx + 1}: {follow_up_question}\nYour Answer (type 'exit' to finish): ")
        
        if user_response.lower() == "exit":
            break

        refined_inputs.append(f"{follow_up_question} {user_response}")
        
        # Generate L1 keywords using both question and answer
        L1_keywords = generate_L1_keywords(follow_up_question, user_response)
        all_L1_keywords.update(L1_keywords)  # Add keywords to the set to avoid duplicates

        # Refine schema based on follow-up inputs
        refine_schema_prompt = (
            f"The initial schema is:\n{initial_schema}\n\n"
            "Refine the schema based on the following user inputs, ensuring it strictly follows the original instructions:\n"
            f"{instructions}\n\n"
            "Important: Only add or revise fields as needed based on the user input. "
            "Do not modify other parts of the schema, such as existing classes, comments, or initial variables, unless explicitly instructed by the user.\n\n"
            "User Inputs:\n" + "\n".join(refined_inputs)
        )
        
        refine_response = openai.ChatCompletion.create(
            model="gpt-4o",
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
    
    # Save the final schema and keywords to separate text files after refinement
    with open("final_schema.txt", "w") as schema_file:
        schema_file.write(initial_schema)
    print("Final schema saved to final_schema.txt")
    
    # Save L0 and consolidated L1 keywords in the specified format
    with open("keywords.txt", "w") as keywords_file:
        keywords_file.write(f"L0: {L0_keywords}\n")
        keywords_file.write(f"L1: {sorted(all_L1_keywords)}\n")  # Sort for consistency
    print("Keywords saved to keywords.txt in the specified format.")

# Main function to execute the schema generation process with levels
def generate_schema_with_levels(user_input):
    # Step 1: Generate Initial Schema
    initial_schema = generate_initial_schema(user_input)
    
    # Step 2: Generate L0 Keywords based on User Input
    L0_keywords = generate_L0_keywords(user_input)
    
    # Step 3: Refine Schema with L1 Keywords from Follow-Up Answers
    refine_schema_with_levels(initial_schema, instructions, L0_keywords, user_input)  

# Example: User prompt to generate a schema for financial trends in the technology sector
user_query = "What are the financial trends in the technology sector in the U.S.?"
generate_schema_with_levels(user_query)