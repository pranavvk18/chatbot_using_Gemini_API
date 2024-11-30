
# Chatbot using Gemini API

---

# **Project Documentation: Steps to run the Chatbot**

---

## **1. Document Selection and Interaction**
- Upon running the program, the user will be presented with a list of available PDF documents, each associated with a number for selection.
- **Steps**:
  1. Enter the number corresponding to the desired document.
  2. The chatbot processes the selected document by extracting its content and creating a searchable vector store.
  3. Once the document is loaded, the user can ask questions related to it.
- To **switch between documents**, type `back` to return to the main menu and select another document.

---

## **2. Embedding Creation and Storage**
- The text extracted from the document is chunked and converted into embeddings using **Google's Gemini embedding API** (`embedding-001`).
- These embeddings are stored in a **FAISS vector store** for efficient similarity searches.
- The vector store is saved locally with a filename based on the document, e.g., `faiss_index_doc1`, enabling reuse without reprocessing the document.

---

## **3. Answer Generation and Source Information**
- The chatbot uses **Google's Gemini conversational model** (`gemini-pro`) to generate detailed answers based on relevant text chunks retrieved from the vector store.
- **Source Transparency**:
  - The chatbot provides the exact paragraph(s) from the document that were used to generate the answer.
  - This ensures users can verify the information and understand its context.

---

## **4. Authentication Setup**
- **Gemini API Access**:
  - The engineer must create their own **Gemini API Key** by signing up for Google’s Generative AI service.
  - Add the API key to a `.env` file as `GOOGLE_API_KEY` in the root directory of the project.
- **Service Account JSON**:
  - For enhanced security, generate a **Service Account JSON** file from the Google Cloud Console.
  - Save the file locally and configure its path in your environment variables (e.g., `GOOGLE_APPLICATION_CREDENTIALS`).
  - This method avoids hardcoding sensitive credentials and ensures secure authentication.

---

## **5. Prerequisites and Execution**
### **Dependencies**:
Ensure the following are installed:

- I have created a separate environment named as `venv` which consist of Python 3.10 version.You can create a new environment as `create -p venv python==3.10`

- Then activate the environment

- Run the command to install all the dependencies using this command
`pip install -r requirements.txt`
- Required Python packages:
  - `langchain`
  - `PyPDF2`
  - `google.generativeai`
  - `faiss`
  - `dotenv`

### **Execution Steps**:
1. Place the PDF files in the appropriate directory and update the `PDF_PATHS` dictionary in the script.
2. Run the program.
3. Follow the prompts to:
   - Select documents.
   - Ask questions.
   - Receive answers along with cited sources.

---
# Architecture of the chatbot

## **1. Key Components of the Architecture**

### **a. PDF Text Extraction**
- **Module/Function**: `get_pdf_text`
  - **Purpose**: Reads and extracts text from a PDF file using `PyPDF2.PdfReader`.
  - **Output**: Raw text from all the pages of the specified PDF.

---

### **b. Text Chunking**
- **Module/Function**: `get_text_chunks`
  - **Purpose**: Splits the extracted text into smaller, manageable chunks using the `RecursiveCharacterTextSplitter` from LangChain.
  - **Why Needed**: Many LLMs, including Gemini, have token limits. Chunking ensures the text fits within those limits while retaining context.
  - **Output**: List of text chunks.

---

### **c. Embedding and Vector Store Creation**
- **Module/Function**: `get_vector_store`
  - **Purpose**: 
    - Converts text chunks into embeddings using Google's Gemini embedding model (`embedding-001`).
    - Stores these embeddings in a vector store powered by FAISS.
  - **Why Needed**: Embeddings enable semantic similarity searches to retrieve relevant text chunks for a user query.
  - **Google API Usage**: 
    - **`GoogleGenerativeAIEmbeddings`**: Generates embeddings for text chunks using the `embedding-001` model.
  - **Output**: Saved FAISS vector store, which can be loaded for querying.

---

### **d. Conversational Chain**
- **Module/Function**: `get_conversational_chain`
  - **Purpose**: 
    - Sets up a LangChain-based question-answering (QA) chain.
    - Uses a custom prompt template to guide the model's response format.
  - **Why Needed**: The QA chain orchestrates the interaction between the retrieved chunks and Google's Gemini API to generate context-aware answers.
  - **Google API Usage**: 
    - **`ChatGoogleGenerativeAI`**: Generates conversational responses using the `gemini-pro` model.

---

### **e. Document Processing**
- **Module/Function**: `process_document`
  - **Purpose**:
    - Handles end-to-end processing of a document:
      1. Extracts text from the PDF.
      2. Splits it into chunks.
      3. Creates a vector store and saves it locally.
      4. Loads the vector store for querying.
  - **Why Needed**: Prepares the document for efficient querying by creating and indexing its embeddings.
  - **Google API Usage**: 
    - **`GoogleGenerativeAIEmbeddings`**: Generates embeddings during vector store creation.

---

### **f. Main Interaction Loop**
- **Module/Function**: `main`
  - **Purpose**:
    - Manages the chatbot interface, allowing users to:
      1. Select a document.
      2. Ask questions based on the selected document.
      3. Receive answers with cited sources.
    - Handles user input and error cases.

---

## **2. Workflow of the Chatbot**

1. **Startup**: 
   - The application loads Google API credentials using `dotenv`.

2. **Document Selection**:
   - The user is presented with a list of available PDFs.
   - The user selects a document, which is processed by `process_document`.

3. **Document Processing**:
   - The selected document is converted into text chunks and stored in a FAISS vector store.

4. **Question and Answer Interaction**:
   - The user enters a question.
   - The chatbot retrieves similar text chunks from the vector store using semantic search (`similarity_search`).
   - The QA chain generates a response based on the retrieved chunks.

5. **Response and Source Display**:
   - The chatbot provides an answer and cites the source text chunks.

6. **Looping**:
   - The user can continue asking questions or switch to another document.

7. **Exit**:
   - The user can exit the application at any time.

---

## **3. Where Google's Gemini API is Used**
Google's Gemini API is used in the following places:

### **a. Embedding Creation**
- **API**: `GoogleGenerativeAIEmbeddings` with `embedding-001`.
- **Purpose**: Converts text chunks into vector embeddings for semantic search.

### **b. Conversational Response**
- **API**: `ChatGoogleGenerativeAI` with `gemini-pro`.
- **Purpose**: 
  - Generates detailed answers to user questions.
  - Produces responses based on the retrieved context, adhering to the custom prompt template.

---

## **4. Advantages of the Architecture**
- **Scalability**: Can process and handle multiple documents efficiently by storing their vector stores locally.
- **Accuracy**: Uses Google's Gemini for precise embeddings and conversational answers.
- **Transparency**: Cites exact sources from the context for each answer.
- **Flexibility**: Allows users to switch between documents and refine their queries interactively.

---

## **5. Limitations**
- **Dependency on Google API**: Requires internet connectivity and valid API credentials for embeddings and conversational responses.
- **Document Size**: Large PDFs may take longer to process due to chunking and embedding creation.
- **Local Storage**: FAISS indices for large documents may consume significant disk space.

This architecture effectively combines the power of Google's Gemini API with LangChain's tooling to create a robust PDF-based Q&A chatbot.

# **Safeguards for Developing a Commercial Product**

## **1. Data Privacy and Security**
- Encrypt sensitive data in transit and at rest.
- Implement strict access controls and regularly audit data usage.

## **2. User Authentication and Authorization**
- Use strong authentication methods (e.g., multi-factor authentication).
- Ensure role-based access control to limit actions based on user roles.

## **3. Robust Error Handling**
- Gracefully handle errors and display meaningful messages to users without exposing sensitive information.

## **4. Regular Updates and Patching**
- Provide timely updates to fix security vulnerabilities and improve performance.

