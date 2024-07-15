import streamlit as st
import pandas as pd
from io import StringIO
import os
import openai
import numpy as np
import faiss
import json
from bert_score import score

# Import the process_xml_to_txt function from the correct file
from input_process.xml_to_cleaned_json_txt import process_xml_to_json_txt
from input_process.xml_to_cleaned_xml_txt import process_and_clean_xml_to_txt
from input_process.convert_xml_to_txt import process_xml_to_txt

openai_api_key = os.environ["OPENAI_API_KEY"]

def save_uploaded_file(uploaded_file, save_dir):
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def create_vectordb(extracts, openai_api_key):
    openai.api_key = openai_api_key

    # Generate embeddings for each extract
    embeddings = []
    for extract in extracts:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=extract
        )
        embedding = response['data'][0]['embedding']
        embeddings.append(embedding)

    # Convert embeddings to numpy array
    embeddings_array = np.array(embeddings).astype('float32')

    # Create the FAISS index
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    return index, embeddings

def query_vectordb(vector_db, question_embedding, k=5):
    question_embedding = np.array(question_embedding).astype('float32').reshape(1, -1)
    _, indices = vector_db.search(question_embedding, k)  # Get top k relevant extracts
    return indices[0]

def generate_initial_responses(vector_db, embeddings, extracts, question, openai_api_key):
    openai.api_key = openai_api_key

    # Generate embedding for the question
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=question
    )
    question_embedding = response['data'][0]['embedding']

    # Query the vector database for relevant extracts
    indices = query_vectordb(vector_db, question_embedding)

    combined_responses = []
    for idx in indices:
        extract = extracts[idx]
        
        # Generate response using the extract
        individual_prompt = f"Based on the following context, answer the question:\n\nContext: {extract}\n\nQuestion: {question}"
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": individual_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.2
            )
            response = completion.choices[0].message.content
            combined_responses.append(response.strip())
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    return combined_responses

def run_frontend():
    st.title("Data Evaluation App")

    uploaded_file1 = st.file_uploader("Upload an XML, PDF, or Office file", type=["xml", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"])
    uploaded_file2 = st.file_uploader("Upload a CSV file containing questions", type="csv")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        # Read the second file (CSV)
        file2_content = uploaded_file2.read().decode('utf-8')
        df = pd.read_csv(StringIO(file2_content))
        questions = df.iloc[:, 0].tolist()  # Assuming the questions are in the first column

        # Radio buttons for different operations
        operation = st.radio(
            "Choose an operation",
            ("Only XML", "XML to JSON", "XML to ENRICHED XML", "OFFICE File")
        )

        # Initialize variables
        processed_file_path = None
        extracts = []

        if operation == "XML to JSON":
            temp_xml_path = os.path.join(os.path.dirname(__file__), "temp_uploaded.xml")
            with open(temp_xml_path, "wb") as f:
                f.write(uploaded_file1.getvalue())

            try:
                processed_file_path = process_xml_to_json_txt(temp_xml_path)
                with open(processed_file_path, 'r') as file:
                    extracts = file.readlines()
                st.success(f"Processed XML file saved as: {processed_file_path}")
            except Exception as e:
                st.error(f"Error processing XML file: {str(e)}")
            finally:
                if os.path.exists(temp_xml_path):
                    os.remove(temp_xml_path)

        elif operation == "XML to ENRICHED XML":
            temp_xml_path = os.path.join(os.path.dirname(__file__), "temp_uploaded.xml")
            with open(temp_xml_path, "wb") as f:
                f.write(uploaded_file1.getvalue())

            try:
                processed_file_path = process_and_clean_xml_to_txt(temp_xml_path)
                with open(processed_file_path, 'r') as file:
                    extracts = file.readlines()
                st.success(f"Processed XML file saved as: {processed_file_path}")
            except Exception as e:
                st.error(f"Error processing XML file: {str(e)}")
            finally:
                if os.path.exists(temp_xml_path):
                    os.remove(temp_xml_path)

        elif operation == "Only XML":
            temp_xml_path = os.path.join(os.path.dirname(__file__), "temp_uploaded.xml")
            with open(temp_xml_path, "wb") as f:
                f.write(uploaded_file1.getvalue())

            try:
                processed_file_path = process_xml_to_txt(temp_xml_path)
                with open(processed_file_path, 'r') as file:
                    extracts = file.readlines()
                st.success(f"Processed XML file saved as: {processed_file_path}")
            except Exception as e:
                st.error(f"Error processing XML file: {str(e)}")
            finally:
                if os.path.exists(temp_xml_path):
                    os.remove(temp_xml_path)

        elif operation == "OFFICE File":
            if uploaded_file1.type != "application/xml":
                data_dir = os.path.join(os.path.dirname(__file__), "data")
                os.makedirs(data_dir, exist_ok=True)

                processed_file_path = save_uploaded_file(uploaded_file1, data_dir)
                with open(processed_file_path, 'r') as file:
                    extracts = file.readlines()
                st.success(f"Office file saved as: {processed_file_path}")
            else:
                st.error("Please upload a PDF or Office file (Word, Excel, PowerPoint) for direct saving.")

        if processed_file_path:
            vector_db, embeddings = create_vectordb(extracts, openai_api_key)
            responses = []

            for question in questions:
                response = generate_initial_responses(vector_db, embeddings, extracts, question, openai_api_key)
                responses.append(response)

            # Add BERT score evaluation
            st.write("### BERT Score Evaluation")
            for i, (response, question) in enumerate(zip(responses, questions)):
                P, R, F1 = score(response, [question], lang='en', verbose=True)
                st.write(f"Question {i + 1}: {question}")
                st.write(f"Response: {response}")
                st.write(f"Precision: {P.mean():.4f}")
                st.write(f"Recall: {R.mean():.4f}")
                st.write(f"F1 Score: {F1.mean():.4f}")

    else:
        st.error("Please upload both files to proceed.")

