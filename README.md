# Royal-Inland-InfoBot
A Retrieval-Augmented Generation (RAG) powered chatbot that answers questions using hospital/organization-specific documents.
This demo project uses LangChain, FAISS/Chroma, and Streamlit to make hospital information accessible through natural conversation.

📂 Project Structure
<pre lang="text"><code> 📁 royal-inland-infobot/ 
  ├── data/ 
  │ └── hospital_docs/ 
    └── chunks.pkl 
  ├── app/ 
  │ ├── chatbot_app.py 
  │ └── data_loader.py 
    └──embeddings.py 
    └──rag_pipeline.py 
  ├── requirements.txt 
  └── README.md </code></pre>


The MVP includes:

✔️ Fully open source stack with no API keys needed

✔️ Local embeddings + FAISS retrieval

✔️ A small system prompt to reduce hallucinations

✔️ Source snippets shown for transparency

✔️ Easy to extend PDFs/HTML and many more pages


<img width="1006" height="531" alt="Screenshot 2025-08-25 at 5 05 40 PM" src="https://github.com/user-attachments/assets/33f09927-7f27-466a-82e1-0ba111a74e1e" />

1️⃣ Clone the Repository
`git clone https://github.com/ktannee/royal-inland-infobot.git
cd royal-inland-infobot`

2️⃣ ⚙️ Environment Setup
`pip install -r requirements.txt`

3️⃣ 🗂️ **Data Preparation**
This project does not include the data/ folder (for privacy reasons).
However, you can collect your own documents and use them to reproduce the pipeline.

**1. Collect Your Data**
Download hospital or organization documents (e.g., service descriptions, FAQs, annual reports, policies, PDFs, or web pages).
Place them inside:


```data/
|   └── hospital_docs/
|      ├── file1.pdf
|      ├── file2.html
|      └── ...

You can use:
- PDFs (brochures, reports, guidelines)
- HTML pages (download with wget or BeautifulSoup)
- Plain text files

**2. Process and Chunk Data**
The script app/data_loader.py automatically:
Reads all files in data/hospital_docs/
Cleans and chunks the text into manageable sections
Saves the chunks to data/chunks.pkl

**3. Build Vector Store**
The embeddings are created from your chunks and stored in a vector database (FAISS/Chroma).
This makes the RAG pipeline able to retrieve context when answering user queries.

**4. Run the Chatbot**
Once your data is prepared, launch the Streamlit app:
`streamlit run app/chatbot_app.py`

This will start an interactive chatbot where you can query your own hospital/organization data.


