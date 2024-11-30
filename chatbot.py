from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Pre-defined PDF file paths
PDF_PATHS = {
    1: "test_sample_1.pdf",  # First document path
    2: "test_sample_2.pdf"   # Second document path
}

def get_pdf_text(pdf_path):
    """Extract text from PDF"""
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    """Split text into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, doc_number):
    """Create vector store from text chunks"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    
    # Save the index locally with document-specific filename
    vector_store.save_local(f"faiss_index_doc{doc_number}")
    return vector_store

def get_conversational_chain():
    """Set up the conversational chain"""
    prompt_template = """
    Answer the question as detailed as possible from the provided context. 
    If the answer is not in the provided context, just say "answer is not available in the context".

    Context:\n {context}\n
    Question: \n{question}\n
    Answer in the following format:
    Answer: [Your detailed answer]
    Source: [The exact paragraph from the context that contains the answer]
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def process_document(doc_number):
    """Process a specific document and create its vector store"""
    # Validate document number
    if doc_number not in PDF_PATHS:
        print(f"Invalid document number: {doc_number}")
        return None

    # Extract text from PDF
    print(f"Processing PDF document {doc_number}...")
    raw_text = get_pdf_text(PDF_PATHS[doc_number])
    
    # Create text chunks
    text_chunks = get_text_chunks(raw_text)
    
    # Create vector store
    get_vector_store(text_chunks, doc_number)
    print(f"PDF document {doc_number} processed and indexed successfully!")
    
    # Prepare embeddings and vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load the vector store 
    try:
        new_db = FAISS.load_local(f"faiss_index_doc{doc_number}", embeddings, allow_dangerous_deserialization=True)
        return new_db
    except Exception as e:
        print(f"Error loading vector store for document {doc_number}: {e}")
        return None

def main():
    # Conversational chain
    chain = get_conversational_chain()
    
    # Interactive document selection and Q&A loop
    while True:
        try:
            # Document selection
            print("\nAvailable Documents:")
            for key, path in PDF_PATHS.items():
                print(f"{key}: {os.path.basename(path)}")
            print("0: Exit")
            
            # Get document selection
            try:
                doc_selection = int(input("\nSelect a document number to query: ").strip())
                
                # Exit condition
                if doc_selection == 0:
                    print("Exiting the application.")
                    break
                
                # Process and load selected document
                vector_db = process_document(doc_selection)
                
                if vector_db is None:
                    continue
                
                # Q&A loop for selected document
                while True:
                    user_question = input("\nEnter your question (or type 'back' to select another document): ").strip()
                    
                    if user_question.lower() == 'back':
                        break
                    
                    if not user_question:
                        print("Please enter a valid question.")
                        continue
                    
                    # Find similar documents
                    docs = vector_db.similarity_search(user_question)
                    
                    # Get response
                    response = chain(
                        {"input_documents": docs, "question": user_question}, 
                        return_only_outputs=True
                    )
                    
                    # Print response
                    print("\nResponse:")
                    print(response["output_text"])
                    
                    # Print source documents for transparency
                    print("\nSource Documents:")
                    for i, doc in enumerate(docs, 1):
                        print(f"Source {i}:\n{doc.page_content}\n")
            
            except ValueError:
                print("Please enter a valid document number.")
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()