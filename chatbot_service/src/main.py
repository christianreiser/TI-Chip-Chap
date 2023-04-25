import gradio as gr
import os
from gpt_index import GPTSimpleVectorIndex
from google.cloud import storage
import json

os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")


def read_json_from_bucket(bucket_name, file_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = storage.Blob(file_name, bucket)
    content = blob.download_as_text()
    data = json.loads(content)

    return data


def chatbot(input_text):
    bucket_name = os.getenv("index_bucket_name")
    file_path = 'index.json'  # os.environ["JSON_FILE_PATH"]
    json_data = read_json_from_bucket(bucket_name, file_path)
    index = GPTSimpleVectorIndex.load_from_dict(json_data)
    response = index.query(input_text, response_mode="compact")
    return response.response


iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text about Chris"),
                     outputs="text",
                     title="Chris custom-trained AI chatbot",
                     flagging_options=["bad answer", "incorrect", "good answer", "not relevant"],
                     examples=['Who is Chris?', 'Wer ist Chris?'],
                     interpretation="default",
                     theme=gr.themes.Default(primary_hue="green", secondary_hue="blue"),
                     )
url = iface.launch(share=True, server_port=8080, server_name="0.0.0.0", debug=True)
print('Visit {}'.format(url))
