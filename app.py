import streamlit as st
from llama_index import StorageContext, load_index_from_storage, VectorStoreIndex, download_loader, SimpleDirectoryReader
from dotenv import load_dotenv 
import os
import pathlib
import requests

#Load API Keys
load_dotenv()

def main():

    st.header('Custom-Made Chatbots')
    st.write("Select the data that your chatbot should be trained with:")

    data = st.selectbox('Data', ('Use Existing Files', 'Upload New File directly', 'Upload file using webhook', 'Upload CSV'))
    
    #Rebuild storage context and load index
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    
    index = load_index_from_storage(storage_context)
    
    if data == 'Use Existing Files':
        index = load_index_from_storage(storage_context)
        query = st.text_input('Enter Your Query')
        button = st.button(f'Response')
        query_engine = index.as_query_engine()
            
        if button:
            st.write(query_engine.query(query).response)
                     
    elif data == 'Upload CSV':
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
    
    elif data == 'Upload New File directly':
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
        documents = SimpleDirectoryReader("data").load_data()

        #Construct the index with the Documents
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
        
    elif data == 'Upload file using webhook':
        url = st.text_input('Enter URL')  
        file_name = st.text_input('Enter File Name')  
        upload_state = False
        
        def url_download():
            r = requests.get(url, stream = True, allow_redirects=True)        
            
            full_file_name = "./data/" + file_name
            with open(full_file_name,"wb") as f:
                upload_state = True 
                for chunk in r.iter_content(chunk_size=1024): 
                
                    if chunk: 
                        f.write(chunk) 
        
        st.button("Upload File", on_click=url_download)
        if True:
            documents = SimpleDirectoryReader("data").load_data()

            #Construct the index with the Documents
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
        
if __name__ == '__main__':
    main()