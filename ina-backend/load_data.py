# load_data.py
from app.rag import rag_engine

def load_sample_data():
    with open("data/placeholder_faqs.txt", "r", encoding="utf-8") as f:
        faqs = f.readlines()
    
    for faq in faqs:
        if faq.strip():
            rag_engine.add_document(faq.strip())
    
    print(f"✅ {len(faqs)} FAQs cargadas en ChromaDB")

if __name__ == "__main__":
    load_sample_data()