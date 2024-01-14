# Custom Training Chatbot
This repository provides a framework for building a custom-trained chatbot using Llama and Streamlit. You can train the chatbot on your own data and use it for various tasks like question answering, information retrieval, or conversational interactions.

- Train on custom data: Train the chatbot on your own text documents or CSV files.
- Interactive interface: Streamlit interface allows you to upload files, query the chatbot, and manage data easily.
- Multiple data upload options: Upload data directly, via CSV, or through webhooks.
- Manage files: Delete unwanted data files directly from the interface.
- Configurable: Easy to modify the configuration file to adjust your chatbot's behavior.

## Getting Started

### Setting up the API

1. Download the API files:
```
git clone https://github.com/omkmorendha/Custom_Training_Chatbot/tree/api
```
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Make an .env file and add OPENAI_API_KEY
4. Run the file by using
```
python main.py
```

##### Base URL:
http://127.0.0.1:5000

##### Authorisation Headers:

Authorisation : API_KEY
Authorisation is done via checking if the SHA-256 hash of the API_KEY exists in the
api_keys.txt file, currently we can use “abcd”, “efgh”, “ijkl” as the API key.

To use the API properly follow the documentation pdf in this repository

### Setting up the Streamlit Web Application

1. Download the API files:
```
git clone https://github.com/omkmorendha/Custom_Training_Chatbot
```
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Make an .env file and add OPENAI_API_KEY
4. Run the file by using
```
streamlit run app.py
```

![image](https://github.com/omkmorendha/Custom_Training_Chatbot/assets/17925053/9337bfff-eeae-4b61-8f58-ddcbe9b218c6)
