from flask import Flask, request, jsonify
from llama_index import (
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex,
    SimpleDirectoryReader,
)
from dotenv import load_dotenv
import os
import requests
import hashlib

app = Flask(__name__)

# Load API Keys
load_dotenv()


def authenticate(api_key):
    """
    Simple authentication function that checks for authentication via an API key
    which is defined in the .env file, if the key exists in the api_keys.txt file
    True is returned otherwise False is returned
    """
    # currently keys "abcd", "efgh", "ijkl"

    try:
        hash_api_key = hashlib.sha256(api_key.encode()).hexdigest()

        with open("api_keys.txt", "r") as file:
            # Read the entire file content
            file_content = file.read()

            # Check if the target string exists in the file
            if hash_api_key in file_content:
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


@app.route("/save-index", methods=["GET"])
def save_index():
    """
    Saves the index to the storage folder
    """

    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

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
    return jsonify({"message": "Index saved successfully"})


def load_index():
    """
    Loads the saved index from the storage folder
    """

    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    # If index was not previously created, create new
    if not os.path.exists("storage"):
        return save_index()

    # Load previously saved index from the storage directory
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    return index


@app.route("/query", methods=["POST"])
def query_route():
    """
    Pass a Query to the chatbot using this function
    By sending the input via a parameter, this function returns the chatbot's response
    Returns an output based on the custom dataset
    """

    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    query_input = request.json.get("query_input")
    if not query_input:
        return jsonify({"message": "Missing 'query_input' in the request body"}), 400

    index = load_index()
    query_engine = index.as_query_engine()

    response = query_engine.query(query_input).response
    return jsonify({"message": response})


@app.route("/upload-webhook", methods=["POST"])
def upload_webhook_route():
    """
    Pass the url of the file to be downloaded, along with file_name to be saved as locally
    If upload is successful "True" is returned, else "False is returned"
    """

    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        url = request.json.get("url")
        if not url:
            return jsonify({"message": "Missing 'url' in the request body"}), 400

        file_name = request.json.get("file_name")

        # Add automated extension
        if not file_name:
            words = url.split("/")
            file_name = words[-1].strip()

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
        return jsonify({"message": "Upload successful"}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Upload failed: {e}"}), 500


@app.route("/upload-text", methods=["POST"])
def upload_text_route():
    """
    Uploads text to a new file or appends it to a default file (text.txt)
    Returns True if text is successfully added and False if unsuccessful
    """
    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        text_to_append = request.json.get("text")
        file_name = request.json.get("file_name", "uploaded_text.txt")
        
        target_folder = "data/"
        file_path = os.path.join(target_folder, file_name)

        with open(file_path, "a+") as file:
            # Check if the file already exists
            if os.path.exists(file_path):
                # Append text with a newline if the file already exists
                file.write("\n" + text_to_append)
            else:
                file.write(text_to_append)


        save_index()
        return jsonify({"message": "Text uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error uploading text: {e}"}), 500


@app.route("/delete-upload-file", methods=["POST"])
def delete_upload_file_route():
    """
    Deletes an uploaded file using the saved file's name in the data folder
    Returns False if the file couldn't be deleted and True if otherwise
    """
    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        file_name = request.json.get("file_name")
        
        target_folder = "./data/"
        file_path = os.path.join(target_folder, file_name)
        os.remove(file_path)

        save_index()
        return jsonify({"message": "File deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error deleting file: {e}"}), 500


@app.route("/delete-all-upload-files", methods=["POST"])
def delete_all_upload_files_route():
    """
    Deletes all the uploaded files
    Keeps a temporary text file to avoid indexing errors
    Returns False if files couldn't be deleted and True if otherwise
    """
    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        folder_path = "./data/"
        all_files = os.listdir(folder_path)

        for file_name in all_files:
            if file_name != "tmp.txt":
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)

        save_index()
        return jsonify({"message": "All files deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error deleting files: {e}"}), 500


@app.route("/delete-webhook", methods=["POST"])
def delete_webhook_route():
    """
    Deletes a webhook uploaded file using the saved file's name in the data_webhooks folder
    Returns False if file couldn't be deleted and True if otherwise
    """
    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        file_name = request.json.get("file_name")
        
        target_folder = "./data_webhooks/"
        file_path = os.path.join(target_folder, file_name)
        os.remove(file_path)

        save_index()
        return jsonify({"message": "Webhook file deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error deleting file: {e}"}), 500


@app.route("/delete-all-webhooks", methods=["POST"])
def delete_all_webhooks_route():
    """
    Deletes all the webhooks
    Keeps a temporary text file to avoid indexing errors
    Returns False if files couldn't be deleted and True if otherwise
    """
    # Authentication
    api_key = request.headers.get("Authorization")
    if not authenticate(api_key):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        folder_path = "./data_webhooks/"
        all_files = os.listdir(folder_path)

        for file_name in all_files:
            if file_name != "tmp.txt":
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)

        save_index()
        return jsonify({"message": "All webhook files deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error deleting files: {e}"}), 500


def upload_direct():
    # USE A FILE UPLOADER TOOL
    # AND THEN CALL THE save_index() function
    save_index()


# Testing Code
if __name__ == "__main__":
    app.run(debug=True)
