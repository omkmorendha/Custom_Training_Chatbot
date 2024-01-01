import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader, TreeIndex
from dotenv import load_dotenv 

#Load API Keys
load_dotenv()

#Load Custom Data
documents = SimpleDirectoryReader("data").load_data()

#Construct the index with the Documents
index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist()