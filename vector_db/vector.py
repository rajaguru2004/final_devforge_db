import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
books_dir = os.path.join(project_root, "books")
persistent_directory = os.path.join(current_dir, "db", "chroma_db_optimized")

# OPTIMIZATION 1: Fast and efficient embedding model with normalized embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},  # Change to 'cuda' if you have GPU for faster processing
    encode_kwargs={'normalize_embeddings': True}  # Enables faster similarity search
)

def create_vector_store(docs, store_name):
    """Create vector store with optimization for fast retrieval"""
    persistent_directory = os.path.join(current_dir, "db", store_name)
    
    if not os.path.exists(persistent_directory):
        print(f"\n--- Creating vector store {store_name} ---")
        print(f"Total documents to embed: {len(docs)}")
        
        # Create vector store with optimized settings
        db = Chroma.from_documents(
            docs, 
            embeddings, 
            persist_directory=persistent_directory,
            collection_metadata={"hnsw:space": "cosine"}  # Faster similarity search using cosine distance
        )
        
        print(f"--- Finished creating vector store {store_name} ---")
        print(f"Vector store location: {persistent_directory}")
        return db
    else:
        print(f"Vector store {store_name} already exists. Loading existing vector store...")
        db = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embeddings
        )
        print(f"Loaded {db._collection.count()} documents from vector store")
        return db

def query_vector_store_mmr(store_name, query, embedding_function, k=3, fetch_k=20, lambda_mult=0.5):
    """
    Query vector store using MMR (Max Marginal Relevance) for diverse results
    
    Parameters:
    - k: Number of documents to return
    - fetch_k: Number of documents to initially fetch based on similarity
    - lambda_mult: Balance between relevance and diversity (0=max diversity, 1=max relevance)
    """
    persistent_directory = os.path.join(current_dir, "db", store_name)
    
    if os.path.exists(persistent_directory):
        print(f"\n--- Querying vector store {store_name} with MMR ---")
        print(f"Query: '{query}'")
        
        db = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embedding_function
        )
        
        # METHOD 2: MMR - Balances relevance and diversity
        retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,                    # Number of documents to return
                "fetch_k": fetch_k,        # Number of documents to initially fetch
                "lambda_mult": lambda_mult # Diversity control (0.5 = balanced)
            }
        )
        
        relevant_docs = retriever.invoke(query)
        
        # Display results
        print(f"\n--- Found {len(relevant_docs)} Relevant Documents (Using MMR) ---")
        if relevant_docs:
            for i, doc in enumerate(relevant_docs, 1):
                print(f"\n{'='*70}")
                print(f"Document {i}:")
                print(f"{'='*70}")
                print(f"{doc.page_content}\n")
                if doc.metadata:
                    print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"File: {os.path.basename(doc.metadata.get('source', 'Unknown'))}")
        else:
            print("No relevant documents found.")
        
        return relevant_docs
    else:
        print(f"Vector store {store_name} does not exist.")
        return []

def load_documents(books_dir):
    """Load all text documents from the books directory"""
    if not os.path.exists(books_dir):
        raise FileNotFoundError(f"Directory {books_dir} does not exist.")
    
    book_files = [f for f in os.listdir(books_dir) if f.endswith(".txt")]
    
    if not book_files:
        raise ValueError("No .txt files found in the books directory.")
    
    print(f"\nFound {len(book_files)} text files")
    documents = []
    
    for idx, book_file in enumerate(book_files, 1):
        file_path = os.path.join(books_dir, book_file)
        print(f"[{idx}/{len(book_files)}] Loading {book_file}...")
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            docs = loader.load()
            documents.extend(docs)
            print(f"  ✓ Loaded successfully")
        except Exception as e:
            print(f"  ✗ Error loading {book_file}: {e}")
    
    print(f"\nTotal documents loaded: {len(documents)}")
    return documents

# Main execution
if __name__ == "__main__":
    # Load all documents from books directory
    documents = load_documents(books_dir)
    
    # Recursive Character-based Splitting
    # Splits text at natural boundaries while maintaining context
    print("\n--- Using Recursive Character-based Splitting ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,       # Size of each chunk
        chunk_overlap=100,     # Overlap between chunks to preserve context
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Split at these boundaries in order
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"Created {len(split_docs)} chunks from {len(documents)} documents")
    
    # Create or load vector store
    db = create_vector_store(split_docs, "chroma_db_optimized")
    
    # Define your query
    query = "who is juliet?"
    
    # Query using MMR (Max Marginal Relevance)
    # This returns diverse yet relevant results
    print("\n" + "="*70)
    print("QUERYING WITH MAX MARGINAL RELEVANCE (MMR)")
    print("="*70)
    
    results = query_vector_store_mmr(
        store_name="chroma_db_optimized",
        query=query,
        embedding_function=embeddings,
        k=3,              # Return top 3 documents
        fetch_k=10,       # Initially fetch 10 similar documents
        lambda_mult=0.5   # Balance: 0.5 = equal relevance and diversity
    )
    
    print("\n" + "="*70)
    print("RETRIEVAL COMPLETE")
    print("="*70)
    print(f"Total results returned: {len(results)}")