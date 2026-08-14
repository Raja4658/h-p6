from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import threading

class DuplicateChecker:
    def __init__(self, threshold=0.85):
        # Using a tiny and fast sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.threshold = threshold
        # In-memory storage for MVP. In production, this would be a Vector DB like Chroma/FAISS.
        self.past_embeddings = [] # List of tuples: (submission_id, embedding)
        self.lock = threading.Lock()
    
    def check_duplicate(self, submission_id: str, answer_text: str) -> bool:
        # Generate embedding for the new answer
        new_embedding = self.model.encode(answer_text)
        
        is_duplicate = False
        
        with self.lock:
            if self.past_embeddings:
                # Extract all past embeddings into a matrix
                past_embs = np.array([emb for _, emb in self.past_embeddings])
                
                # Calculate cosine similarity between new embedding and all past embeddings
                similarities = cosine_similarity([new_embedding], past_embs)[0]
                
                # Check if any similarity exceeds the threshold
                if np.any(similarities >= self.threshold):
                    is_duplicate = True
            
            # Store the current submission
            self.past_embeddings.append((submission_id, new_embedding))
            
        return is_duplicate
