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


def upload_webhook(url: str, file_name: str):
    """
    Pass the url of the file to be downloaded, along with file_name to be saved as locally
    If upload is successful "True" is returned, else "False is returned"
    """
    try:
        #Authentication
        if(not authenticate()):
            print("Authentication Failed")
            return
        
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
    except Exception as e:
        print(f'Error appending to {file_path}: {e}')


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
#     print(query("Tell me about Aashish"))
    
#     txt = "Aashish's top 5 fruits would have to be: Strawberry, blueberry, apple, banana, and orange. This is a tough ranking that he spent hours mulling over. Strawberries are a no-brainer. They're delicious, have low calories, and can be eaten by themselves or as a topping. Aashish prefers adding them to oatmeal and pancakes. The same goes for blueberries, though they don't taste as well, which is why they rank second. Apples have this sweet and yet tart flavor that you can never get bored of. He tends to eat them alone though. There are recipes that attempt to make dishes with apples (e.g., apple french toast), but they always end up reducing the flavor of the apple. Bananas are a staple. They're healthy and cheap, so Aashish always includes them in my pantry. They're also the easiest to incorporate into cooking, given that they work with many other flavors. Furthermore, when bananas blacken, they can still be used in many baking recipes. That being said, the taste of a banana itself doesn't rival strawberries, blueberries, or apples. So, they rank fourth. Finally, oranges are incredibly rich in flavor, ranging from sweet to sour. Aashish never gets tired of them. However, they're difficult to incorporate into dishes. He's seen oranges added to salads, but that, to him, is just blasphemous. Ultimately, he rarely buys them, despite finding them delicious, which is why they rank fifth. "
#     upload_text(txt)
#     print(query("Tell me about Aashish"))
    
#     delete_all_upload_files()
#     print(query("Tell me about Aashish"))