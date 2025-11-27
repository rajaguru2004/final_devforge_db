"""
DevForge Graph Database
Main entry point for running examples and demonstrations
"""

from examples import main as run_examples

if __name__ == "__main__":
    print(" DevForge Graph Database - NetworkX Implementation")
    print("=" * 70)
    print()
    
    # Run all examples
    run_examples()
    
    print("\n Execution completed!")
    print("\n To extend this into a full Graph RAG system:")
    print("  1. Add embedding models (OpenAI, HuggingFace, etc.)")
    print("  2. Store embeddings as node properties")
    print("  3. Implement vector similarity search")
    print("  4. Add LLM integration for query understanding")
    print("  5. Create retrieval chains with LangChain")
    print("  6. Add caching and indexing for performance")
