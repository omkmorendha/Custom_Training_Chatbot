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

def authenticate():
    """
    Simple authentication function that checks for authentication via an API key
    which is defined in the .env file, if the key exists in the api_keys.txt file
    True is returned otherwise False is returned
    """
    
    try:
        api_key = os.getenv("API_KEY")
        with open("api_keys.txt", 'r') as file:
            # Read the entire file content
            file_content = file.read()

            # Check if the target string exists in the file
            if api_key in file_content:
                return True
            else:
                return False
    except Exception as e:
        print(f"Could not authenticate: {e}")
        return False

def create_tmp_folder_files(folder):
    os.makedirs(folder)
    file_path = os.path.join(folder, "tmp.txt")
    with open(file_path, "w") as file:
        file.write("")
    

def save_index():
    """
    Saves the index to the storage folder
    """

    #Authentication
    if(not authenticate()):
        print("Authentication Failed")
        return

    # Create the folder if it doesn't exist
    if not os.path.exists("data"):
        create_tmp_folder_files("data")
     
    if not os.path.exists("data_webhooks"):
        create_tmp_folder_files("data_webhooks")        
    
    # Load Custom Data and construct the index with the Documents
    documents_direct = SimpleDirectoryReader("data").load_data()
    documents_webhooks = SimpleDirectoryReader("data_webhooks").load_data() 
    doc_list = documents_direct + documents_webhooks
    index = VectorStoreIndex.from_documents(doc_list)
        
    index.storage_context.persist()
    return index


def load_index():
    """
    Loads the saved index from the storage folder
    """

    #Authentication
    if(not authenticate()):
        print("Authentication Failed")
        return

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
    
    #Authentication
    if(not authenticate()):
        print("Authentication Failed")
        return
    
    index = load_index()
    query_engine = index.as_query_engine()

    return query_engine.query(query_input).response


def upload_webhook(url: str, file_name: str = "uploaded_file"):
    """
    Pass the url of the file to be downloaded, along with file_name to be saved as locally
    If upload is successful "True" is returned, else "False is returned"
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
        #Add automated extension
        if(file_name == "uploaded_file"):
            words = url.split('.')
            ext = words[-1].strip()
            file_name += "." + ext

        r = requests.get(url, stream=True, allow_redirects=True)

        # Check if the request was successful (status code 200)
        r.raise_for_status()

        # Create the folder if it doesn't exist
        if not os.path.exists("data_webhooks"):
            os.makedirs("data_webhooks")

        full_file_name = "./data_webhooks/" + file_name
        with open(full_file_name, "wb+") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # Save new index
        save_index()
        return True

    except requests.exceptions.RequestException as e:
        return False

def upload_text(text_to_append: str, file_name : str = "text.txt"):
    """
    Uploads text to a new file or appends it to a default file (text.txt)
    returns True if text is successfully added and False if unsuccessfull
    """
    
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
        target_folder = "data/"
        file_path = os.path.join(target_folder, file_name)
        
        with open(file_path, 'a+') as file:
            file.write(text_to_append)
            
        save_index()
        return True
    except Exception as e:
        print(f'Error appending to {file_path}: {e}')
        return False


def delete_upload_file(file_name):
    """
    Deletes an uploaded file using the saved file's name in the data folder
    Returns False if file couldn't be deleted and True if otherwise
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
        target_folder = "./data/"
        file_path = os.path.join(target_folder, file_name)
        os.remove(file_path)

        save_index()
        return True

    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def delete_all_upload_files():
    """
    Deletes all the uploaded files
    Keeps a temporary text file to avoid indexing errors
    Returns False if files couldn't be deleted and True if otherwise
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
            
        folder_path = "./data/"
        all_files = os.listdir(folder_path)
        
        for file_name in all_files:
            if file_name != "tmp.txt":
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
        
        save_index()
        return True 
    except Exception as e:
        print(f"Error deleting files: {e}")
        return False       

def delete_webhook(file_name):
    """
    Deletes a webhook uploaded file using the saved file's name in the data_webhooks folder
    Returns False if file couldn't be deleted and True if otherwise
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
        target_folder = "./data_webhooks/"
        file_path = os.path.join(target_folder, file_name)
        os.remove(file_path)

        save_index()
        return True

    except Exception as e:
        print(f"Error deleting file: {e}")
        return False
     

def delete_all_webhooks():
    """
    Deletes all the webhooks
    Keeps a temporary text file to avoid indexing errors
    Returns False if files couldn't be deleted and True if otherwise
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
        folder_path = "./data_webhooks/"
        all_files = os.listdir(folder_path)
        
        for file_name in all_files:
            if file_name != "tmp.txt":
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
        
        save_index()
    except Exception as e:
        print(f"Error deleting files: {e}")
        return False      
        
    
def upload_direct():
    # USE A FILE UPLOADER TOOL
    # AND THEN CALL THE save_index() function
    save_index()


#Testing Code
# if __name__ == "__main__":
#     print(query("Tell me about the black cat"))
    
#     url = "https://americanenglish.state.gov/files/ae/resource_files/the_black_cat.pdf"
#     upload_webhook(url)
#     print(query("Tell me about the black cat"))
    
#     delete_all_webhooks()
#     print(query("Tell me about the black cat"))