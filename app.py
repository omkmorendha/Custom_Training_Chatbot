import streamlit as st
from llama_index import StorageContext, load_index_from_storage, VectorStoreIndex, download_loader
from dotenv import load_dotenv 
import os
import pathlib

#Load API Keys
load_dotenv()

def main():

    st.header('Custom-Made Chatbots')
    st.write("Select the data that your chatbot should be trained with:")

    data = st.selectbox('Data', ('Use Existing Files', 'Upload New File directly', 'Upload file using webhook'))
    
    # if data == 'Use Existing Files':
        #Rebuild storage context and load index
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    index = load_index_from_storage(storage_context)
        
    if data == 'Upload New File directly':
        uploaded_file = st.file_uploader("Choose a CSV file")
        complete_name = ""
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            data = uploaded_file.getvalue().decode('utf-8').splitlines()         
            st.session_state["preview"] = ''
            for i in range(0, min(5, len(data))):
                st.session_state["preview"] += data[i]
                
            preview = st.text_area("CSV Preview", "", height=150, key="preview")
        
        upload_state = st.text_area("Upload State", "", key="upload_state")

        
        def upload():
            if uploaded_file is None:
                st.session_state["upload_state"] = "Upload a file first!"
            else:
                data = uploaded_file.getvalue().decode('utf-8')
                parent_path = pathlib.Path(__file__).parent.resolve()           
                save_path = os.path.join(parent_path, "data")
                nonlocal complete_name 
                complete_name = os.path.join(save_path, uploaded_file.name)
                destination_file = open(complete_name, "w+")
                destination_file.write(data)
                destination_file.close()
                st.session_state["upload_state"] = "Saved " + complete_name + " successfully!"

        st.button("Upload File", on_click=upload)
        
        if(st.session_state["upload_state"]):
            SimpleCSVReader = download_loader("SimpleCSVReader")
            loader = SimpleCSVReader(encoding="utf-8")
            print(complete_name)
            documents = loader.load_data(file=pathlib.Path(complete_name))
        
            index = VectorStoreIndex.from_documents(documents)
        
    elif data == 'Upload file using webhook':
        pass
    
    query = st.text_input('Enter Your Query')
    button = st.button(f'Response')

    query_engine = index.as_query_engine()

    if button:
        st.write(query_engine.query(query).response)

if __name__ == '__main__':
    main()