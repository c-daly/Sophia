from typing import List, Tuple, Dict
import numpy as np

class InMemoryVectorDatabase:
    def __init__(self):
        self.embeddings = []  # List[Tuple[embedding, metadata]]

    def add_embedding(self, embedding: np.array, metadata: Dict):
        self.embeddings.append((embedding, metadata))

    def retrieve_similar(self, embedding: np.array, top_n=5) -> List[Tuple[np.array, Dict]]:
        similarities = [self._compute_similarity(embedding, stored_embedding)
                        for stored_embedding, _ in self.embeddings]
        # Sort by similarity and get top_n embeddings
        sorted_indices = np.argsort(similarities)[-top_n:]
        return [self.embeddings[i] for i in sorted_indices]

    def update_embedding(self, embedding_id: int, new_embedding: np.array, new_metadata: Dict):
        self.embeddings[embedding_id] = (new_embedding, new_metadata)

    def _compute_similarity(self, embedding1: np.array, embedding2: np.array) -> float:
        # Using cosine similarity for this example
        dot_product = np.dot(embedding1, embedding2)
        norm_product = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        return dot_product / norm_product
