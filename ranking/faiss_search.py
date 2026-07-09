import faiss
import numpy as np

class FaissIndex:
    def __init__(self, dimension=384): # 384 is the dim for all-MiniLM-L6-v2
        self.dimension = dimension
        # Using L2 distance or Inner Product. For cosine similarity, normalize vectors and use Inner Product.
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {} # Maps faiss index to database candidate ID
        self.current_count = 0

    def add_vectors(self, vectors, db_ids):
        """
        Add normalized vectors to the FAISS index.
        """
        if len(vectors) == 0:
            return
            
        vectors = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        
        for i, db_id in enumerate(db_ids):
            self.id_map[self.current_count + i] = db_id
        self.current_count += len(vectors)

    def search(self, query_vector, k=5):
        """
        Search for top k similar vectors.
        """
        if self.current_count == 0:
            return [], []
            
        q = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(q)
        
        # k can't be larger than total elements
        k = min(k, self.current_count)
        
        similarities, indices = self.index.search(q, k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            if idx in self.id_map:
                db_id = self.id_map[idx]
                score = similarities[0][i]
                results.append((db_id, score))
                
        return results
