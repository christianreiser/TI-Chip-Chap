import os

from gpt_index import SimpleDirectoryReader, GPTSimpleVectorIndex


def construct_index(directory_path):
    print('constructing index...')
    documents = SimpleDirectoryReader(directory_path).load_data()
    index = GPTSimpleVectorIndex.from_documents(documents)
    index.save_to_disk('index.json')
    print('index constructed and saved to disk at index.json')
    return index
os.environ["OPENAI_API_KEY"] = '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'

directory_path = "./../../../docs"
construct_index(directory_path)
