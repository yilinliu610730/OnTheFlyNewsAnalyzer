# 1) ask user to provide a topic, called user_query
# 2) run generate_schema(user_query) 
#     - will also ask for user feedback on the schema
#     - confirm with user to start retrieval and filling
# 3) run retrieval_and_fill(user_query, schema)
#     - ask for user's feedback in each pair (article, schema instance)
# 4) run refine_schema_with_instance_feedback(initial_prompt, initial_schema, sample_article, sample_instance, user_response)

from generate_schema.generate_schema import instructions, example_schema, generate_schema_with_levels # generate_schema, initial_prompt
from refine_schema.refine import refine_schema_with_instance_feedback
from retrieve_and_fill.retrieve_and_fill import get_schema_filled, get_dataset, row_to_string
from retrieve_and_fill.retrieve_and_fill import EXAMPLE_SCHEMA, EXAMPLE_L0_KEYWORDS, EXAMPLE_L1_KEYWORDS
from final_answer.final_answer import get_final_answer
from datasets import load_dataset
from typing import List, Tuple, Dict

# raw schema to schema by class name, with parent class combined with child classes
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

class SchemaGenerator():
    
    def __init__(self):
        DATA_PATH = "./dataset/filtered_data"
        self.dataset = load_dataset(DATA_PATH)['train']

        self.user_query: str = ""
        self.schema: str = EXAMPLE_SCHEMA  # this is a string contains both base class and child classes
        self.L0_keywords: List[str] = EXAMPLE_L0_KEYWORDS
        self.L1_keywords: List[str] = EXAMPLE_L1_KEYWORDS
        self.schema_by_class: Dict[str, str] = {}  # class name to entire class SCHEMA string, value contains both base class and child classes
        self.schema_by_class_nobase: Dict[str, str] = {}  # same above, no base class in value
        self.filled_schemas_by_class: Dict[str, str] = {}
        self.answer: str = ""
    
    def reset(self):
        self.user_query = ""
        self.schema = EXAMPLE_SCHEMA
        self.L0_keywords = EXAMPLE_L0_KEYWORDS
        self.L1_keywords = EXAMPLE_L1_KEYWORDS
        self.schema_by_class = {}
        self.schema_by_class_nobase = {}
        self.filled_schemas_by_class = {}
        self.answer = ""

    # STEP 1: find the schema and keywords for the user query, back-and-forth with user
    def run_generator(self) -> Tuple[str, List[str], List[str]]:
        while True:
            self.user_query = input("What's the topic you want to generate a schema for? ")
            self.schema, self.L0_keywords, self.L1_keywords = generate_schema_with_levels(self.user_query)
            print("Generated schema:", self.schema)
            user_feedback = input("Confirm if you want to start retrieval with this schema? (yes/no)")
            if user_feedback.lower() in ["yes", "y"]:
                break
        return self.schema, self.L0_keywords, self.L1_keywords

    # STEP 2: retrieve and fill the schema with instances
    # STEP 3: back-and-forth with user to refine the schema based on filled instances
    def run_retrieval_and_fill(self):
        while True:
            collect_user_feedback = input("Reply [Y/YES] if you want to provide feedback, otherwise there will be no feedback or refinement loop: ")
            collect_user_feedback = collect_user_feedback.lower() in ["yes", "y"]
            # STEP 2: retrieve and fill the schema with instances
            self.schema_by_class, _ = process_schema(self.schema, add_base_class=True)
            self.schema_by_class_nobase, self.base_class = process_schema(self.schema, add_base_class=False)
            self.filled_schemas_by_class = get_schema_filled(
                self.schema_by_class,  # later change to real schema, generated in step1
                self.dataset,
                self.L0_keywords,  # later change to auto-generated L0 keywords, generated in step1
                self.L1_keywords,  # later change to auto-generated L1 keywords, generated in step1
                min_occurrences=3,
                max_articles=5,
                collect_user_feedback=collect_user_feedback
            )
            if not collect_user_feedback:
                break
            # STEP 3: back-and-forth with user to refine the schema based on filled instances
            new_schema: str = self.base_class
            for schema_class, filled_schemas in self.filled_schemas_by_class.items():
                refined_schema = refine_schema_with_instance_feedback(
                    initial_instructions=instructions,
                    initial_schema=self.schema_by_class_nobase[schema_class],  # later change to real schema
                    filled_schemas=filled_schemas,  # class instances
                    dataset=self.dataset
                )
                new_schema += refined_schema
                if refined_schema[:3] == '```':
                    refined_schema = refined_schema[3:]
                if refined_schema[:6] == 'python':
                    refined_schema = refined_schema[6:]
                if refined_schema[-3:] == '```':
                    refined_schema = refined_schema[:-3]

            print("Refined schema:", refined_schema)
            self.schema = new_schema

            retrieve_again = input("Put [Y/YES] to retrieve again in new schema, otherwise use current filled schema instances: ")
            if retrieve_again.lower() not in ["yes", "y"]:
                break
            collect_feedback_again = input("In next round of retrieval, put [Y/YES] to collect user feedback again, otherwise stop collecting user feedback: ")
            collect_user_feedback = collect_feedback_again.lower() in ["yes", "y"]
            breakpoint()


    # basically need to provide a final NLP answer to user's input query, with information from filled schemas
    def final_answer(self) -> str:
        answer = f'Here are the final answer to your query "{self.user_query}" analyzed from different perspestives:\n\n'
        for schema_class, filled_schemas in self.filled_schemas_by_class.items():
            answer += f"From the perspective of {schema_class}:\n"
            summarized_answer = get_final_answer(filled_schemas, self.user_query)
            answer += summarized_answer + "\n\n"
        with open(f"final_answer_{self.user_query}.txt", "w") as f:
            f.write(answer)
        return answer


    def run_single(self):
        self.reset()
        # schema, L0_keywords, L1_keywords = self.run_generator()
        # self.run_retrieval_and_fill(schema, L0_keywords, L1_keywords)
        self.run_retrieval_and_fill()
        self.final_answer()

    
    def run(self):
        while True:
            self.run_single()
            user_feedback = input("Do you want to generate another schema? (yes/no)")
            if user_feedback.lower() not in ["yes", "y"]:
                break

if __name__ == "__main__":
    schema_generator = SchemaGenerator()
    schema_generator.run_single()