import os

from langchain.chat_models import ChatOpenAI
from llama_index import (
    LLMPredictor,
    ServiceContext,
    SimpleDirectoryReader, GPTSimpleVectorIndex
)

def construct_index(directory_path):
    print('constructing index...')
    documents = SimpleDirectoryReader(directory_path).load_data()
    # llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-4"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
    index.save_to_disk('index.json')
    print('index constructed and saved to disk at index.json')
    return index
os.environ["OPENAI_API_KEY"] = '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'

directory_path = "./../../../docs"
construct_index(directory_path)
