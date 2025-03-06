import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # Updated import
from langchain_community.vectorstores import Pinecone  # Updated import
from langchain_community.document_loaders import TextLoader  # Updated import
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec

load_dotenv()  # Load environment variables from .env file


# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define the Pinecone index name and environment
PINECONE_INDEX_NAME = "faq-index-new"

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Function to load FAQ data from the .txt file
def load_faq_data(file_path):
    loader = TextLoader(file_path)
    return loader.load()

# Function to generate embeddings for FAQ data
def generate_embeddings(faq_data):
    return embeddings.embed_documents([doc.page_content for doc in faq_data])  

#Function to create an index if it does not exist
def create_index():
    # Create index if it doesn't exist
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # The dimension should match the embedding size
            metric='cosine',
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ) 
        )

# Function to upload FAQ data and embeddings to Pinecone
def upload_faq_to_pinecone(faq_data, faq_embeddings):
    # Create index if it doesn't exist
    create_index()

    # Upload FAQ data and embeddings to Pinecone
    index = pc.Index(PINECONE_INDEX_NAME)

    # Delete old data if necessary
    #index.delete(delete_all=True, namespace="faq")

    # Ensure all FAQ data is uploaded
    upsert_data = [
        (str(i), faq_embeddings[i], {"text": faq_data[i].page_content})
        for i in range(len(faq_data))
    ]
    index.upsert(vectors=upsert_data, namespace="faq")

    print("Uploaded", len(upsert_data), "FAQ entries to Pinecone")



# Function to query Pinecone and get the most relevant FAQ answers
def query_faq_pinecone(query):
    # Generate query embedding
    query_embedding = embeddings.embed_query(query)
    #print(query_embedding)
    
    # Query Pinecone index
    index = pc.Index(PINECONE_INDEX_NAME)
    print(index.describe_index_stats()) 
    results = index.query(queries=[query_embedding], top_k=3, include_metadata=True)

    # Return the top answer

    if results.get("matches"):
        return results["matches"][0]["metadata"]["text"]
    else:
        print(f"No match found for query: {query}")
        return "Sorry, I couldn't find a relevant answer."
