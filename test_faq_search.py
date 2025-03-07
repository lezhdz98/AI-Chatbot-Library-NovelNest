from faq_search_rag import load_faq_data, generate_embeddings, upload_faq_to_pinecone, query_faq_pinecone

file_name = 'FAQ_library.txt'

# Example Usage:
if __name__ == '__main__':
    # Step 1: Load FAQ data
    faq_data = load_faq_data(file_name)  
    
    # Step 2: Generate embeddings for FAQ data
    faq_embeddings = generate_embeddings(faq_data)

    # Step 3: Upload FAQ data and embeddings to Pinecone
    upload_faq_to_pinecone(faq_data, faq_embeddings)

    # Step 4: Query Pinecone with a user query
    user_query = "What are your opening hours?"
    answer = query_faq_pinecone(user_query)
    
    # Step 5: Print the results from Pinecone
    print("FAQ Answer:", answer)
