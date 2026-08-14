from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import threading

class DuplicateChecker:
    def __init__(self, limit=0.85):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.limit = limit
        self.history = [] 
        self.lock = threading.Lock()
    
    def check_duplicate(self, sub_id: str, text: str) -> bool:
        emb = self.encoder.encode(text)
        
        flag = False
        with self.lock:
            if len(self.history) > 0:
                past_embs = np.array([e for _, e in self.history])
                sim = cosine_similarity([emb], past_embs)[0]
                
                if np.any(sim >= self.limit):
                    flag = True
            
            # save for next time
            self.history.append((sub_id, emb))
            
        return flag
