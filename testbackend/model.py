from flask import Flask, request, jsonify
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import torch
from torch.cuda.amp import autocast

app = Flask(__name__)

# Load and process the document
loader = TextLoader("./movies_rag.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
docs = text_splitter.split_documents(documents=documents)

# Initialize embeddings and vector store
embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cuda"}
with autocast():
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs)
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index_")
persisted_vectorstore = FAISS.load_local("faiss_index_", embeddings, allow_dangerous_deserialization=True)

# Create components for the chain
retriever = persisted_vectorstore.as_retriever()
llm = Ollama(model="llama3.1:8b")

# Define a custom prompt that includes memory support
custom_prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template="""
Core Instructions:
1. Analyze queries through three lenses:
   - Semantic context from movie synopses
   - Entity relationships (actors, directors, themes)
   - Comparative genre dynamics
   - Respond only to the user's questions. If there is no question, engage in polite small talk with the user

2. Response protocol:
   - Respond in 1-3 sentences maximum
   - Always mention 2-3 specific connection points from context
   - Use natural, enthusiastic language (no markdown)

3. Safety/Accuracy:
   - Never invent facts outside provided context
   - Acknowledge limitations: "Based on my movie database..."
   - Handle sensitive topics with: "That theme appears in [X], which involves..."

4. Entity Disambiguation Protocol:
   - Treat similar names as distinct until proven related. For example, Adam Sandler and Jackie Sandler are different actors.

Chat History:
{chat_history}

Context:
{context}

Question:
{question}

Answer:
"""
)

# Set up memory and create the conversational retrieval chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": custom_prompt}
)

# Define the /query endpoint to accept POST and OPTIONS requests
@app.route('/query', methods=['POST', 'OPTIONS'])
def query_endpoint():
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response

    # For POST requests, process the incoming JSON data.
    data = request.json
    # Assuming the key is "question"; adjust if your front end sends a different key.
    question = data.get('message', '')
    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    # Invoke the chain with the provided question.
    result = qa.invoke({"question": question})
    answer = result.get('answer', '')

    # Create response and include CORS header.
    response = jsonify({'answer': answer})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    # Run the Flask app on the specified host and port
    app.run(host='192.168.0.249', port=5500)
