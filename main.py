# 1) ask user to provide a topic, called user_query
# 2) run generate_schema(user_query) 
#     - will also ask for user feedback on the schema
#     - confirm with user to start retrieval and filling
# 3) run retrieval_and_fill(user_query, schema)
#     - ask for user's feedback in each pair (article, schema instance)
# 4) run refine_schema_with_instance_feedback(initial_prompt, initial_schema, sample_article, sample_instance, user_response)

from generate_schema.generate_schema import generate_schema, initial_prompt
from refine_schema.refine import refine_schema_with_instance_feedback
from retrieve_and_fill.retrieve_and_fill import get_schema_filled, get_dataset, row_to_string
from retrieve_and_fill.retrieve_and_fill import EXAMPLE_SCHEMA, EXAMPLE_L0_KEYWORDS, EXAMPLE_L1_KEYWORDS
from datasets import load_dataset

class SchemaGenerator():
    
    def __init__(self):
        DATA_PATH = "./dataset/filtered_data"
        self.dataset = load_dataset(DATA_PATH)['train']

    def run_single(self):
        # while True:
        #     user_query_input = input("What's the topic you want to generate a schema for? ")
        #     schema = generate_schema(user_query_input)
        #     print("Generated schema:", schema)
        #     user_feedback = input("Confirm if you want to start retrieval with this schema? (yes/no)")
        #     if user_feedback.lower() in ["yes", "y"]:
        #         break
        filled_schemas_by_class = get_schema_filled(
            EXAMPLE_SCHEMA,  # later change to real schema
            self.dataset,
            EXAMPLE_L0_KEYWORDS,  # later change to auto-generated L0 keywords
            EXAMPLE_L1_KEYWORDS,  # later change to auto-generated L1 keywords
            min_occurrences=3,
            max_articles=5,
            ask_user=True
        )
        refined_schemas = []
        for schema_class, filled_schemas in filled_schemas_by_class.items():
            refined_schema = refine_schema_with_instance_feedback(
                initial_prompt,
                initial_schema=EXAMPLE_SCHEMA,  # later change to real schema
                filled_schemas=filled_schemas,
                dataset=self.dataset
            )
            refined_schemas.append(refined_schema)
        for refined_schema in refined_schemas:
            print("Refined schema:", refined_schema)

    def run(self):
        while True:
            self.run_single()
            user_feedback = input("Do you want to generate another schema? (yes/no)")
            if user_feedback.lower() not in ["yes", "y"]:
                break


schema_generator = SchemaGenerator()
schema_generator.run_single()