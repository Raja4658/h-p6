import threading

# Try to import sentence-transformers (not available on Vercel due to size)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class DuplicateChecker:
    def __init__(self, limit=0.85):
        self.limit = limit
        self.history = [] 
        self.lock = threading.Lock()
        
        if HAS_SENTENCE_TRANSFORMERS:
            print("✅ Using SentenceTransformers for duplicate detection")
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            print("⚠️  SentenceTransformers not available, using basic duplicate detection")
            self.encoder = None
    
    def check_duplicate(self, sub_id: str, text: str) -> bool:
        """Check if text is similar to previously submitted answers"""
        flag = False
        
        with self.lock:
            if HAS_SENTENCE_TRANSFORMERS and self.encoder:
                # Use embeddings-based detection
                try:
                    emb = self.encoder.encode(text)
                    
                    if len(self.history) > 0:
                        past_embs = np.array([e for _, e in self.history])
                        sim = cosine_similarity([emb], past_embs)[0]
                        
                        if np.any(sim >= self.limit):
                            flag = True
                    
                    self.history.append((sub_id, emb))
                except Exception as e:
                    print(f"Embedding error: {e}")
                    flag = False
            else:
                # Fallback: Simple string similarity check
                text_lower = text.lower()
                for _, past_text in [(s, t) for s, t in self.history if isinstance(t, str)]:
                    # Simple character overlap check
                    if text_lower == past_text.lower():
                        flag = True
                        break
                
                # Store text as string in fallback mode
                self.history.append((sub_id, text_lower))
        
        return flag

