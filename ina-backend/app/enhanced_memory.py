from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

class HierarchicalMemory:
    def __init__(self):
        self.short_term_memory = {}  # Caché en memoria
        self.medium_term_memory = {}  # ChromaDB
        self.long_term_memory = "long_term_storage.json"
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        
    def store_information(self, content: str, metadata: Dict, memory_type: str = "short"):
        embedding = self.model.encode([content])[0]
        timestamp = datetime.now().isoformat()
        
        data = {
            "content": content,
            "embedding": embedding.tolist(),
            "metadata": metadata,
            "timestamp": timestamp
        }
        
        if memory_type == "short":
            self.short_term_memory[content] = data
        elif memory_type == "medium":
            # Aquí iría la lógica de ChromaDB
            pass
        elif memory_type == "long":
            self._store_long_term(data)
    
    def _store_long_term(self, data: Dict):
        if os.path.exists(self.long_term_memory):
            with open(self.long_term_memory, 'r', encoding='utf-8') as f:
                memory = json.load(f)
        else:
            memory = []
            
        memory.append(data)
        
        with open(self.long_term_memory, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    
    def query_memory(self, query: str, threshold: float = 0.75) -> List[Dict]:
        query_embedding = self.model.encode([query])[0]
        results = []
        
        # Buscar en memoria a corto plazo
        for content, data in self.short_term_memory.items():
            similarity = cosine_similarity([query_embedding], [np.array(data['embedding'])])[0][0]
            if similarity > threshold:
                results.append({"source": "short_term", "data": data, "similarity": similarity})
        
        # Buscar en memoria a largo plazo
        if os.path.exists(self.long_term_memory):
            with open(self.long_term_memory, 'r', encoding='utf-8') as f:
                long_term_data = json.load(f)
                
            for data in long_term_data:
                similarity = cosine_similarity([query_embedding], [np.array(data['embedding'])])[0][0]
                if similarity > threshold:
                    results.append({"source": "long_term", "data": data, "similarity": similarity})
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)

class IntelligentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, text: str) -> List[Dict]:
        # Dividir en párrafos
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para.split())
            
            if current_size + para_size <= self.chunk_size:
                current_chunk += para + "\n\n"
                current_size += para_size
            else:
                # Guardar chunk actual
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "size": current_size,
                        "metadata": {
                            "chunk_id": len(chunks),
                            "timestamp": datetime.now().isoformat()
                        }
                    })
                
                # Comenzar nuevo chunk con overlap
                last_words = " ".join(current_chunk.split()[-self.overlap:])
                current_chunk = last_words + "\n" + para + "\n\n"
                current_size = len(last_words.split()) + para_size
        
        # Guardar último chunk
        if current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "size": current_size,
                "metadata": {
                    "chunk_id": len(chunks),
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        return chunks