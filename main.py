from llama_index import (
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex,
    SimpleDirectoryReader,
)
from dotenv import load_dotenv
import os
import requests

# Load API Keys
load_dotenv()


def save_index():
    """
    Saves the index to the storage folder
    """

    # Create the folder if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        file_path = os.path.join("data", "tmp.txt")
        with open(file_path, "w") as file:
            file.write("")

    # Load Custom Data
    documents = SimpleDirectoryReader("data").load_data()

    # Construct the index with the Documents
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()
    return index


def load_index():
    """
    Loads the saved index from the storage folder
    """

    # If index was not previously created, create new
    if not os.path.exists("storage"):
        return save_index()

    # Load previously saved index from the storage directory
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    return index


def query(query_input: str) -> str:
    """
    Pass a Query to the chatbot using this function
    By sending the input via a paramter, this function returns the chatbot's response
    Returns an output based on the custom dataset
    """
    index = load_index()
    query_engine = index.as_query_engine()

    return query_engine.query(query_input).response


def upload_webhook(url: str, file_name: str):
    """
    Pass the url of the file to be downloaded, along with file_name to be saved as locally
    If upload is successful "True" is returned, else "False is returned"
    """
    try:
        r = requests.get(url, stream=True, allow_redirects=True)

        # Check if the request was successful (status code 200)
        r.raise_for_status()

        # Create the folder if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

        full_file_name = "./data/" + file_name
        with open(full_file_name, "wb+") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # Save new index
        save_index()
        return True

    except requests.exceptions.RequestException as e:
        return False


def delete_file(file_name):
    """
    Deletes a file using the saved file's name in the data folder
    Returns False if file couldn't be deleted and True if otherwise
    """
    try:
        target_folder = "./data/"
        file_path = os.path.join(target_folder, file_name)
        os.remove(file_path)

        save_index()
        return True

    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def upload_direct():
    # USE A FILE UPLOADER TOOL
    # AND THEN CALL THE save_index() function
    save_index()


# Testing Code
# if __name__ == "__main__":
#     resp = query("Tell me about the black cat")
#     print(resp)

#     upload_webhook("https://americanenglish.state.gov/files/ae/resource_files/the_black_cat.pdf", "the_black_cat.pdf")
#     resp = query("Tell me about the black cat")
#     print(resp)

#     delete_file("the_black_cat.pdf")
#     resp = query("Tell me about the black cat")
#     print(resp)
