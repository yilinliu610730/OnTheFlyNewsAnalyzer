import openai

# Set your OpenAI API key here
openai.api_key = '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'

# Define prompt template for generating all follow-up questions
follow_up_prompt_template_all = """
Based on the user's initial input:

{user_input}

Generate 10 unique follow-up questions that clarify or refine details needed for schema generation. Each question should focus on a different aspect of the user's requirements, such as timeframe, specific segments, financial metrics, and geographic scope. Ensure each question is unique, and avoid repeating similar questions.
"""

refine_schema_prompt_template = """
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

def refine_schema_with_levels(initial_schema, instructions, L0_keywords, user_input):
    # Generate initial follow-up questions based on user input
    follow_up_questions = generate_follow_up_questions(user_input)
    all_L1_keywords = set()  # Use a set to automatically handle duplicates

    for idx, follow_up_question in enumerate(follow_up_questions):
        # Capture user response for each follow-up question
        user_response = input(f"Follow-up Question {idx + 1}: {follow_up_question}\nYour Answer (type 'exit' to finish): ")
        
        if user_response.lower() == "exit":
            break

        # Generate L1 keywords using both question and answer
        L1_keywords = generate_L1_keywords(follow_up_question, user_response)
        all_L1_keywords.update(L1_keywords)  # Add keywords to the set to avoid duplicates

        # Refine schema based on follow-up inputs using the updated prompt template
        refine_schema_prompt = refine_schema_prompt_template.format(
            initial_schema=initial_schema,
            instructions=instructions,
            follow_up_question=follow_up_question,
            user_response=user_response  # Pass only the response, not the full Q&A pair
        )
        
        # Send the prompt to OpenAI to refine the schema
        refine_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert schema generator."},
                {"role": "user", "content": refine_schema_prompt}
            ],
            max_tokens=5000,
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

    return initial_schema, L0_keywords, sorted(all_L1_keywords)
