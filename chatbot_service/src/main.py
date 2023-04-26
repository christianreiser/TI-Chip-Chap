import gradio as gr
import os
from google.cloud import storage
import json
from datetime import datetime
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from llama_index import (
    LLMPredictor,
    ServiceContext,
    GPTSimpleVectorIndex
)
# os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")
os.environ["OPENAI_API_KEY"] = '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'


def read_json_from_bucket_with_cache(bucket_name, file_name):
    global json_data_cache
    if json_data_cache is None:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = storage.Blob(file_name, bucket)
        content = blob.download_as_text()
        json_data_cache = json.loads(content)

    return json_data_cache


def chatbot(input_text):
    global index_cache
    global service_context

    if index_cache is None:
        bucket_name = os.getenv("index_bucket_name")
        file_path = 'index.json'
        json_data = read_json_from_bucket_with_cache(bucket_name, file_path)
        index_cache = GPTSimpleVectorIndex.load_from_dict(json_data)
    # index_cache = GPTSimpleVectorIndex.load_from_disk('indexing/index.json')
    # llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, max_tokens=900, model_name="gpt-3.5-turbo"))
    if service_context is None:
        llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, max_tokens=900, model_name="text-davinci-003"))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=900)
    response = index_cache.query(response_mode="compact", query_str=input_text,service_context=service_context)
    return response.response


index_cache, service_context, json_data_cache = None, None, None

iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text about Chris"),
                     outputs="text",
                     title="Chris chatbot",
                     description="Last updated:" + str(datetime.utcnow()) + " (UTC)",
                     flagging_options=["bad answer", "incorrect", "good answer", "not relevant"],
                     examples=['welche blutwerte hatte Christian am 2019-09-05? z.b.HDL,LDL,NF,QCH,GT,AP,BILI,OT,...  schreibe eine zeile pro laborident. ',
                               'was steht im Persönlichkeitsstrukturtest PST-R von Klient Reiser, Christian?',
                               'wo arbeitet christian derzeit?'],
                     interpretation="default",
                     theme=gr.themes.Default(primary_hue="green", secondary_hue="blue"),
                     )
url = iface.launch(share=True, server_port=8080, server_name="0.0.0.0", debug=True)
print('Visit {}'.format(url))
