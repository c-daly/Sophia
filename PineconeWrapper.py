import numpy as np
import pinecone
import hashlib
import json
class PineconeWrapper:
    def __init__(self, index_name):
        # Initialize Pinecone
        pinecone.init(api_key="d6f058b1-c3b0-4795-ae82-5b469cc543d3", environment="asia-southeast1-gcp-free")

        self.index_name = "embeddings"
        self.index = pinecone.Index(self.index_name)

    def add_embedding(self, embedding, original_text, metadata=None):
        """
        Store an embedding to Pinecone with optional metadata.
        """
        id = str(hashlib.sha256(original_text.encode()).hexdigest())
        #vectors = (str(hashlib.sha256(original_text.encode()).hexdigest()), [embedding], metadata)
        vectors = {'id': id, 'values': embedding, 'metadata': metadata}
        print(json.dumps([vectors]))
        self.index.upsert(vectors=[vectors])

    def query_embedding(self, embedding, k=5):
        """
        Retrieve the top-k most similar embeddings from Pinecone.
        """
        # Convert embedding to a list (if it's a numpy array) for Pinecone compatibility
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()

        # Query the embedding
        results = self.index.query(queries=[embedding], top_k=k, include_metadata=True, include_values=True)
        return results

    def update_embedding(self, embedding_id, new_embedding):
        """
        Update an existing embedding in Pinecone.
        """
        self.add_embedding(embedding_id, new_embedding)  # Upsert serves as update

    def remove_embedding(self, embedding_id):
        """
        Remove an embedding from Pinecone.
        """
        pinecone.index.deindex(index_name=self.index_name, ids=[embedding_id])
