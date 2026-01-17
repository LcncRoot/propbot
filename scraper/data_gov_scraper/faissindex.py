import faiss

def create_faiss_index(embeddings_file, output_index):
    """Stores embeddings in a FAISS index"""
    embeddings = np.load(embeddings_file)
    dimension = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dimension)  # L2 similarity search
    index.add(embeddings)
    
    faiss.write_index(index, output_index)
    print(f"✅ FAISS index saved as {output_index}")

# Store grants and contracts separately
create_faiss_index("faiss_grants_embeddings.npy", "faiss_grants_index.bin")
create_faiss_index("faiss_contracts_embeddings.npy", "faiss_contracts_index.bin")
