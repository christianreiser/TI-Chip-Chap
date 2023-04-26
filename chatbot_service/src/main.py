import gradio as gr
import os
from gpt_index import GPTSimpleVectorIndex
from google.cloud import storage
import json

os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")


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

    if index_cache is None:
        bucket_name = os.getenv("index_bucket_name")
        file_path = 'index.json'
        json_data = read_json_from_bucket_with_cache(bucket_name, file_path)
        index_cache = GPTSimpleVectorIndex.load_from_dict(json_data)

    response = index_cache.query(input_text, response_mode="compact")
    return response.response


index_cache = None
json_data_cache = None
iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text about Chris"),
                     outputs="text",
                     title="Chris custom-trained AI chatbot",
                     flagging_options=["bad answer", "incorrect", "good answer", "not relevant"],
                     examples=['welche blutwerte  hatte Christian am 2019-09-05? schreibe eine zeile pro laborident. ', 'wie ist die Persönlichkeitsstrukturvon christian?', 'wo arbeitet christian derzeit?'],
                     interpretation="default",
                     theme=gr.themes.Default(primary_hue="green", secondary_hue="blue"),
                     )
url = iface.launch(share=True, server_port=8080, server_name="0.0.0.0", debug=True)
print('Visit {}'.format(url))
