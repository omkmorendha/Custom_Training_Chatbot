from distutils.command import upload
import streamlit as st
from llama_index import StorageContext, load_index_from_storage, VectorStoreIndex, download_loader, SimpleDirectoryReader
from dotenv import load_dotenv 
import os
import pathlib
import requests

#Load API Keys
load_dotenv()
#Rebuild storage context and load index
storage_context = StorageContext.from_defaults(persist_dir='./storage')
index = load_index_from_storage(storage_context)

def save_index():
    #Load Custom Data
    documents = SimpleDirectoryReader("data").load_data()

    #Construct the index with the Documents
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

def exisiting_files():
    index = load_index_from_storage(storage_context)
    query = st.text_input('Enter Your Query')
    button = st.button(f'Response')
    query_engine = index.as_query_engine()
            
    if button:
        st.write(query_engine.query(query).response)

def upload_csv():
    uploaded_file = st.file_uploader("Choose a CSV file")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = uploaded_file.getvalue().decode('utf-8').splitlines()         
        st.session_state["preview"] = ''
        for i in range(0, min(5, len(data))):
            st.session_state["preview"] += data[i]
                
        preview = st.text_area("CSV Preview", "", height=150, key="preview")
        
    upload_state = st.text_area("Upload State", "", key="upload_state")
        
    if uploaded_file is not None:
        data = uploaded_file.getvalue().decode('utf-8')
        parent_path = pathlib.Path(__file__).parent.resolve()           
        save_path = os.path.join(parent_path, "data")
        complete_name = os.path.join(save_path, uploaded_file.name)       
        
    def upload():
        if uploaded_file is None:
            st.session_state["upload_state"] = "Upload a file first!"
        else:
            destination_file = open(complete_name, "w+")
            destination_file.write(data)
            destination_file.close()
            st.session_state["upload_state"] = "Saved successfully!"

    st.button("Upload File", on_click=upload)
        
    if st.session_state["upload_state"][:4] == "Save":
        SimpleCSVReader = download_loader("SimpleCSVReader")
        loader = SimpleCSVReader(encoding="utf-8")
        documents = loader.load_data(file=pathlib.Path(complete_name))
        
        index = VectorStoreIndex.from_documents(documents)
            
        query = st.text_input('Enter Your Query')
        button = st.button(f'Response')
        query_engine = index.as_query_engine()
            
        if button:
            st.write(query_engine.query(query).response)
            
        save_button = st.button('Save Data Permanently')
        if save_button:
            index.storage_context.persist()
            index = load_index_from_storage(storage_context)    

def upload_direct():
    uploaded_files = st.file_uploader("Upload a file", accept_multiple_files=True)
    upload_state = st.text_area("Upload State", "", key="upload_state")
    complete_names = []
        
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            data = uploaded_file.getvalue()
            parent_path = pathlib.Path(__file__).parent.resolve()           
            save_path = os.path.join(parent_path, "data")
            complete_name = os.path.join(save_path, uploaded_file.name)
            complete_names.append(complete_name)    
        
    def upload():
        if uploaded_files is None:
            st.session_state["upload_state"] = "Upload a file first!"
        else:
            for complete_name in complete_names:
                destination_file = open(complete_name, "wb+")
                destination_file.write(data)
                destination_file.close()
                st.session_state["upload_state"] = "Saved successfully!"

    st.button("Upload File", on_click=upload)
    if st.session_state["upload_state"] == "Saved successfully!":
        save_index()
        index = load_index_from_storage(storage_context)

        query = st.text_input('Enter Your Query')
        button = st.button(f'Response')
        query_engine = index.as_query_engine()
                
        if button:
            st.write(query_engine.query(query).response)                                                        


def upload_webhook():
    url = st.text_input('Enter URL')
    file_name = st.text_input('Enter File Name')  

    
    def url_download(file_name):
        try:
            r = requests.get(url, stream=True, allow_redirects=True)

            # Check if the request was successful (status code 200)
            r.raise_for_status()

            full_file_name = "./data/" + file_name
            with open(full_file_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            st.session_state["upload_state"] = "Saved " + file_name + " successfully!"
        except requests.exceptions.RequestException as e:
            st.session_state["upload_state"] = "Failed to download: " + str(e)
    
    if st.button("Upload File"):
        url_download(file_name)

    upload_state = st.text_area("Upload State", "", key="upload_state")  

    save_index()
    index = load_index_from_storage(storage_context)

    query = st.text_input('Enter Your Query')
    button = st.button(f'Response')
    query_engine = index.as_query_engine()
                
    if button:
        st.write(query_engine.query(query).response)    


def manage_files():
    filelist=[]
    for root, dirs, files in os.walk("data"):
        for file in files:
            if(file == '.txt'):
                continue
            
            filename=os.path.join(root, file)
            filelist.append(file)
                    
            if(st.button('Delete ' + file)):
                os.remove('./data/' + file)
                save_index()
                st.rerun()

def main():

    st.header('Custom-Training Chatbot')
    st.write("Upload, Delete or Query the data using Chatbot:")

    #data = st.selectbox('Option', ('Use Existing Files', 'Upload New File directly', 'Upload file using webhook', 'Upload CSV', 'Manage Files'))
    data = st.selectbox('Option', ('Use Existing Files', 'Upload New File directly', 'Upload file using webhook', 'Manage Files'))
    
    if data == 'Use Existing Files':
        exisiting_files()
                     
    elif data == 'Upload CSV':
        upload_csv()
    
    elif data == 'Upload New File directly':
        upload_direct()
        
    elif data == 'Upload file using webhook':
        upload_webhook()
        
    elif data == 'Manage Files':
        manage_files()
    
if __name__ == '__main__':
    main()