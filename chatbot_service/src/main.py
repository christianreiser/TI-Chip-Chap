from google.cloud import bigquery
from vertexai.preview.language_models import TextGenerationModel
import os
from typing import Dict, List
import gradio as gr

from langchain.chat_models import ChatOpenAI



client = bigquery.Client()

generation_model = TextGenerationModel.from_pretrained("text-bison@001")
dataset_full_id = 'chatbot-420.info_bot'


def prompt2txt(prompt):
    llm_provider = 'google'
    return generation_model.predict(
            prompt,
            temperature=0.0,
            max_output_tokens=128,
            top_k=40,
            top_p=0.8,
        ).text


def map_question_to_table(question, client, dataset_full_id):
    # Get list of tables
    tables = list(client.list_tables(dataset_full_id))  # Convert iterator to list
    tables_list = []
    distinct_level_0_names = set()

    # Get distinct level_0 names
    for table in tables:
        if table.labels and 'level_0' in table.labels:
            distinct_level_0_names.add(table.labels['level_0'])
    print('distinct_level_0_names:', distinct_level_0_names)

    # Get correct level_0 name
    level_0_name = get_more_detailed_category(question, broad_category='Texas Instruments products',
                                              options=distinct_level_0_names)

    # fallback to 'other_level_0' if no match
    if level_0_name == 'other':
        return 'other_level_0', None, 'Not sure which kind of product you are asking about. I can help with: ' + (
            ", ".join(str(item) for item in distinct_level_0_names if item != "other"))

    # Get list of tables for level_0_name
    for table in tables:  # Now it's safe to iterate again
        if table.labels and 'level_0' in table.labels and table.labels['level_0'] == level_0_name:
            tables_list.append(table.table_id)
    tables_list.append('other')

    # Get correct table name
    table_short_id = get_more_detailed_category(question, broad_category=level_0_name,
                                                options=tables_list)

    # fallback to 'other_table' if no match
    if table_short_id == 'other':
        return 'other_table', None, f'It seems like your question is about {level_0_name} but I am not sure which category of {level_0_name} you are asking about. I can help with: ' + (
            ", ".join(str(item) for item in tables_list if item != "other"))

    # Get full table name
    table_full_id = dataset_full_id + '.' + table_short_id
    print('table_full_id:', table_full_id)
    return table_short_id, table_full_id, level_0_name


def get_table_list(client, dataset_full_id, level_0_name):
    tables = client.list_tables(dataset_full_id)
    tables_list = [table.table_id for table in tables]
    # print('tables_list:',tables_list)
    return tables_list


def get_more_detailed_category(question, broad_category, options):
    """
    Get more detailed category via LLM by letting it choose from a list of options.
    """
    prompt = f"""Please select one name of a table that most likely contains the answer to the question: {question}.
    Select from this list of possible tables about {broad_category}: {options}.
    Respond only with the name. e.g.: abc"""
    print('prompt:', prompt)
    detailed_category = llm.predict(prompt)
    print('detailed_category:', detailed_category)

    return detailed_category


def get_schema(table_full_id):
    table = client.get_table(table_full_id)
    schema = {field.name: field.field_type for field in table.schema}
    return schema


def count_distinct_values(table_full_id: str, schema: Dict[str, str], client) -> Dict[str, List[str]]:
    """
    Counts distinct STRING values in each field of a given BigQuery table.

    Args:
    table_full_id (str): Full ID of the table.
    schema (Dict[str, str]): Schema of the table.
    client: BigQuery client.

    Returns:
    Dict[str, List[str]]: Dictionary of distinct values for each STRING field.
    """
    # Getting all STRING fields
    string_fields = [field for field, type_ in schema.items() if type_ == 'STRING']

    if not string_fields:
        return {}

    # Constructing the query
    combined_query = " UNION ALL ".join(
        f"SELECT '{field}' as field_name, {field} as field_value FROM `{table_full_id}`"
        for field in string_fields
    )

    try:
        query_job = client.query(combined_query)
    except Exception as e:
        print(f"Error executing query: {e}")
        return {}

    distinct_values = {field: set() for field in string_fields}
    for row in query_job:
        distinct_values[row['field_name']].add(row['field_value'])

    # Filtering out fields with too many distinct values
    return {field: list(values) for field, values in distinct_values.items() if len(values) < 15}


def format_output(distinct_values: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Formats the output of distinct values.

    Args:
    distinct_values (Dict[str, List[str]]): Dictionary of distinct values for each STRING field.

    Returns:
    Dict[str, str]: Formatted output dictionary.
    """
    return {field: ', '.join([f"%{value}%" for value in values]) for field, values in distinct_values.items()}


def query_distinct_string_values(table_full_id: str, schema: Dict[str, str], client) -> Dict[str, str]:
    """
    Queries distinct STRING values from a BigQuery table and formats the output.

    Args:
    table_full_id (str): Full ID of the table.
    schema (Dict[str, str]): Schema of the table.
    client: BigQuery client.

    Returns:
    Dict[str, str]: Dictionary of formatted distinct values for each STRING field.
    """
    distinct_values = count_distinct_values(table_full_id, schema, client)
    return format_output(distinct_values)


def answer_question(question):
    """
    Main function that answers a question.
    """
    table_short_id, table_full_id, level_0_name = map_question_to_table(question, client, dataset_full_id)

    # Fallback: if no level_0 match, return list of distinct level_0_names
    if table_short_id == 'other_level_0':
        fallback_message = level_0_name
        print('fallback_message:', fallback_message)
        return fallback_message, None
    # Fallback: if no table match, return list of distinct tables
    elif table_short_id == 'other_table':
        fallback_message = level_0_name
        print('fallback_message:', fallback_message)
        return fallback_message, None
    else:
        schema = get_schema(table_full_id)
        example = f"""SELECT Product_or_Part_number, Slew_rate_in_V_per___s FROM `chatbot-420.info_bot.op-amps`  where Rating like '%Automotive%' and Type like '%Power op amps%' order by Slew_rate_in_V_per___s asc limit 10;
        or
        SELECT GBW_in_MHz FROM `chatbot-420.info_bot.op-amps` where Product_or_Part_number ='OPA2863-Q1';"""

        question_to_sql_prompt = f"""
        Please write BigQuery SQL that answers question: {question}. 
        For context: 
        table_ID: {table_full_id};
        table schema: {schema}; 
        Distinct string values: {query_distinct_string_values(table_full_id, schema, client)};
        This table is about only about {table_short_id}, {level_0_name}, of Texas Instruments (TI) {level_0_name}. 
        Try to avoid "SELECT *" or more than 6 selections.
        Give only the sql without any additional text. 
        A good example is: 
        {example}
        """
        print('question_to_sql_prompt:', question_to_sql_prompt)
        # Get SQL from LLM
        sql = llm.predict(question_to_sql_prompt)

        print(f'sql: {sql}')

        # Execute SQL
        query_job = client.query(sql)
        sql_result_df = query_job.result().to_dataframe()
        print(f'sql_result_df: {sql_result_df}')

        # Convert SQL result to a readable format for LLM
        sql_result_str = str(sql_result_df)
        # print(f'sql_result_str: {sql_result_str}')
        # Get natural language answer from LLM
        response = llm.predict(f"""Translate the following SQL result to a 
        natural language answer: '{sql_result_str}' 
        in the context of the question: '{question}'. 
        For example an answer can be: The GBW of the OPA2863-Q1 is 50 MHz.
        """)
        print(f'response: {response}')

        # Return both the response and the plot/image
        return response, sql_result_df



with gr.Blocks() as iface:
    gr.Markdown(
        """
        #       TI ChipChap </span> 
        """)

    with gr.Row():
        input_question = gr.Textbox(label="Ask me about any TI product", lines=6)
        examples = gr.Examples(examples=["""Which are the top 10 amplifiers with the slowest slew rate? """,
                                         """compare the TLV333 with the OPA333""",
                                         """what types of amps does TI offer?""",
                                         "what are features of the OPA186?",
                                         "what is the Iq per channel (mA) of OPA333?",
                                         "Can you recommend me a 4-channel, SOIC package, with less than 0.03mA Iq, more than 350kHz GBW  amplifier?",
                                         "Which military rated Precision op amps with 4 channels does TI offer",
                                         "what are the 10 Precision amps with the highest slew rate that are Space rated and have at least 2 pins?",
                                         "which PGAs can operate at 150 deg C?",
                                         "which Comparators have a RSPECL output?",
                                         "can you recommend me a catalog rating current sense amplifier with 80V common mode range?"],
                               inputs=[input_question])

    with gr.Row():
        input_button = gr.Button()

    with gr.Row():
        output_text = gr.Text(label="Answer")
        output_table = gr.DataFrame(label="Table")

    input_button.click(answer_question, inputs=input_question, outputs=[output_text, output_table])

url = iface.launch(share=True, server_port=8080, server_name="0.0.0.0", debug=True)
print('Visit {}'.format(url))
