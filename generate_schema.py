import openai

# Set your OpenAI API key here
openai.api_key = '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'

# Define the initial prompt for schema generation
initial_prompt = """
Task: Based on user input, dynamically interpret and generate a structured schema with relevant entities, attributes, data types, and relationships.

Instructions:
- For each main entity, define a class with attributes reflecting its properties.
- The base class for a schema should have the exact signature (ACLEDEvent, ABC).
- Use precise field names, data types (e.g., List, Optional, etc.), and descriptions to describe each attribute.
- Define subclass types where applicable to represent specific event variations or details.
- After providing the schema, confirm if the user would like additional elements or refinements.

Example Workflow:

User Input: "What are the current details of the battle between Iraq and Balenstaine?"

Step 1: Extract keywords - "battle," "current details," "Iraq," "Balenstaine."
Step 2: Generate Schema

Generated Schema:

class Battle(ACLEDEvent, ABC):
    # A "Battle" event is defined as a violent interaction between two organized armed groups at a particular time and location. "Battle" can occur between armed and organized state, non-state, and external groups, and in any combination therein. Civilians can be harmed during "Battle" events if caught in crossfire or impacted by strikes on military targets (referred to as "collateral damage"). When civilians are harmed, they are not recorded as an "Actor"; any fatalities are aggregated in the "Fatalities" field.
    location: Location = Field(..., description="Location where the event takes place")
    fatalities: Optional[int] = Field(..., description="Total number of fatalities, if known")
    involved_groups: List[str] = Field(..., description="Groups involved in the battle, e.g., Iraq, Balenstaine")

class GovernmentRegainsTerritory(Battle):
    # Type of "Battle" event where government forces regain control of a location through armed interaction. Only re-establishments of government control are recorded.
    government_force: List[str] = Field(..., description="Government forces or affiliates regaining control")
    adversary: List[str] = Field(..., description="Competing state forces or non-state group losing control")

class NonStateActorOvertakesTerritory(Battle):
    # Type of "Battle" event where a non-state actor or foreign actor captures territory from an opposing government or non-state actor.
    non_state_actor: List[str] = Field(..., description="Non-state actor overtaking territory")
    adversary: List[str] = Field(..., description="Opposing entity from whom territory was taken")

class ArmedClash(Battle):
    # Type of "Battle" event where two organized groups engage in battle without territorial change.
    side_1: List[str] = Field(..., description="Group on one side of the clash")
    side_2: List[str] = Field(..., description="Group on the other side of the clash")
    targets_local_administrators: bool = Field(..., description="Whether local officials are targeted")
    women_targeted: List[WomenTargetedCategory] = Field(..., description="Category of violence against women, if any")

---

Now, based on the user’s input, interpret and generate a schema with structured classes, attributes, and descriptions using the above example as a model. Include fields such as location, relevant attributes, participant groups, and actions. Use List or Optional types where applicable. Ensure the schema is detailed and relevant to the user query.
Generate the intiaial schema based on the user input.
"""

# Follow-up prompt template for generating dynamic questions
follow_up_prompt_template = """
Given the current schema:

{schema}

Generate specific follow-up questions to ask the user in order to refine the schema further. These questions should help clarify details, add missing information, or refine attribute definitions.
"""

# Function to generate schema and handle multi-turn refinement
def generate_schema(user_input):
    # Step 1: Generate Initial Schema
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert schema generator."},
            {"role": "user", "content": initial_prompt + "\nUser: " + user_input}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    initial_schema = response['choices'][0]['message']['content'].strip()
    print("Initial schema generated. Let's refine it with additional details.\n")

    # Step 2: Multi-turn conversation for schema refinement
    refined_inputs = []
    while True:
        # Generate dynamic follow-up questions based on the current schema
        follow_up_prompt = follow_up_prompt_template.format(schema=initial_schema)
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
        
        # Refine the schema based on the user's response
        refine_schema_prompt = f"The initial schema is:\n{initial_schema}\n\nRefine the schema based on the following user inputs:\n" + "\n".join(refined_inputs)
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

    # Step 3: Save final schema to file
    with open("final_schema.py", "w") as file:
        file.write(initial_schema)
    print("Final schema saved to final_schema.py")

# Example: User prompt to generate a schema for financial trends in the technology sector
user_query = "What are the financial trends in the technology sector in the U.S.?"
generate_schema(user_query)