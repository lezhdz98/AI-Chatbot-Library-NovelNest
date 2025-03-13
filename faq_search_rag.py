import os
from dotenv import load_dotenv  # Load environment variables
from langchain_openai import OpenAIEmbeddings  # OpenAI embeddings
from langchain_community.vectorstores import Pinecone  # Pinecone integration
from langchain_community.document_loaders import TextLoader  # Load documents
from langchain.chains.question_answering import load_qa_chain  # Q&A chain
from langchain.schema import Document  # Define document structure
from pinecone import Pinecone, ServerlessSpec  # Pinecone initialization
import re  # Regular expressions for text processing

load_dotenv()  # Load environment variables from .env file

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define the Pinecone index name and environment
PINECONE_INDEX_NAME = "faq-index-new"

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

def load_faq_data(file_path):
    """
    Loads FAQ data from a text file and formats it into a list of Document objects.
    
    Args:
        file_path (str): The path to the FAQ text file.
    
    Returns:
        list: A list of Document objects containing questions and answers.
    """
    # Read the file as a single text
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Use regex to split based on numbered questions (e.g., "1. What is...?", "2. How do I...?")  
    faq_entries = re.split(r"\n\d+\.\s", text)[1:]  # Ignore first empty split

    documents = []
    for i, entry in enumerate(faq_entries):
        # Extract the question (first line) and answer (rest of the text)
        lines = entry.strip().split("\n")
        question = lines[0]  # First line is the question
        answer = " ".join(lines[1:]).strip()  # Remaining lines are the answer

        # Store each FAQ as a separate document
        documents.append(Document(page_content=f"{question}\n{answer}"))

    return documents  # Returns a list of Documents, each representing one FAQ

def generate_embeddings(faq_data):
    """
    Generates embeddings for FAQ data using OpenAI embeddings.
    
    Args:
        faq_data (list): A list of Document objects containing FAQ entries.
    
    Returns:
        list: A list of embeddings corresponding to the FAQ entries.
    """
    return embeddings.embed_documents([doc.page_content for doc in faq_data])  

def create_index():
    """
    Creates a Pinecone index if it does not already exist.
    """
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

def upload_faq_to_pinecone(faq_data, faq_embeddings):
    """
    Uploads FAQ data and embeddings to Pinecone for efficient retrieval.
    
    Args:
        faq_data (list): A list of Document objects containing FAQ entries.
        faq_embeddings (list): A list of embeddings corresponding to the FAQ entries.
    """

    # Create index if it doesn't exist
    create_index()

    # Upload FAQ data and embeddings to Pinecone
    index = pc.Index(PINECONE_INDEX_NAME)

    # Delete old data if necessary
    #index.delete(delete_all=True, namespace="faq")

    # Prepare Pinecone upsert requests
    upsert_data = []
    for i in range(len(faq_data)):
        vector = faq_embeddings[i]  # Embedding for current FAQ
        metadata = {'text': faq_data[i].page_content}  # The FAQ question text
        upsert_data.append((str(i), vector, metadata))

    #Upsert the data to Pinecone (now each FAQ entry is a separate vector)
    index.upsert(
        vectors=upsert_data,
        namespace="faq"  # Use a namespace to separate this data from others
    )

    print("FAQ data uploaded successfully.")
    print("Uploaded", len(upsert_data), "FAQ entries to Pinecone")



def query_faq_pinecone(query):
    """
    Queries the Pinecone index with a user question and retrieves the most relevant FAQ answer.
    
    Args:
        query (str): The user question.

    Returns:
        str: The best matching answer from the FAQ database.
    """
    
    #Generate the embedding (vector representation) for the query
    query_embedding = embeddings.embed_query(query)

    #Debugging: Print query embedding information
    #print(f"Query embedding length: {len(query_embedding)}")
    #print(f"First 10 values of embedding: {query_embedding[:10]}")  # Check the first 10 values

    #Ensure the embedding is valid before querying Pinecone
    if query_embedding is None:
        raise ValueError("Query embedding is None!")

    if any(x is None or isinstance(x, str) for x in query_embedding):
        raise ValueError("Query embedding contains invalid values!")

    #Ensure embedding has the correct dimension (1536 for OpenAI models)
    if len(query_embedding) != 1536:
        raise ValueError(f"Query embedding has incorrect dimension: {len(query_embedding)} (expected 1536)")

    #Initialize the Pinecone index
    index = pc.Index(PINECONE_INDEX_NAME)

    #Get index statistics (useful for debugging)
    #print(index.describe_index_stats())

    #Query Pinecone using the correct format (Pinecone 2.x)
    results = index.query(
        vector=query_embedding,  
        top_k=3,  # Retrieve the top 3 most relevant FAQ entries
        include_metadata=True,  # Include stored metadata (the actual text answer)
        namespace="faq"  # Ensure we're searching within the "faq" namespace
    )

    #Return the best-matching result if there are any matches
    if results.get("matches"):
        return results["matches"][0]["metadata"]["text"]
    else:
        print(f"No match found for query: {query}")
        return "Sorry, I couldn't find a relevant answer."