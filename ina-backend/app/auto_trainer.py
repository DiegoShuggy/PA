from sqlmodel import Session, select
from app.models import UnansweredQuestion, engine
import logging
import json
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class AutoTrainer:
    def __init__(self):
        self.training_data_path = "training_data/"
        os.makedirs(self.training_data_path, exist_ok=True)
    
    def generate_training_data(self, days: int = 30):
        """
        Genera datos de entrenamiento from preguntas no respondidas
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            with Session(engine) as session:
                # Obtener preguntas no respondidas
                unanswered_questions = session.exec(
                    select(UnansweredQuestion)
                    .where(UnansweredQuestion.timestamp >= start_date)
                    .where(UnansweredQuestion.needs_human_review == True)
                ).all()
                
                training_data = []
                
                for question in unanswered_questions:
                    # Formato para fine-tuning con Ollama
                    training_example = {
                        "input": question.original_question,
                        "output": f"RESPUESTA_IDEAL_PARA: {question.original_question}",
                        "category": question.category,
                        "metadata": {
                            "source": "unanswered_question",
                            "timestamp": question.timestamp.isoformat()
                        }
                    }
                    training_data.append(training_example)
                
                # Guardar en archivo JSON
                filename = f"{self.training_data_path}training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(training_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Generated training data with {len(training_data)} examples: {filename}")
                return {"generated_examples": len(training_data), "file": filename}
                
        except Exception as e:
            logger.error(f"Error generating training data: {e}")
            return {"error": str(e)}
    
    def prepare_fine_tuning_data(self):
        """
        Prepara datos en formato específico para Ollama fine-tuning
        """
        try:
            # Buscar el archivo de training más reciente
            import glob
            files = glob.glob(f"{self.training_data_path}training_data_*.json")
            if not files:
                return {"error": "No training data found"}
            
            latest_file = max(files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # Convertir a formato Ollama
            ollama_format = []
            for example in training_data:
                ollama_format.append({
                    "input": example["input"],
                    "output": example["output"]
                })
            
            return {
                "total_examples": len(ollama_format),
                "format": "ollama",
                "data": ollama_format[:10]  # Muestra solo 10 ejemplos
            }
            
        except Exception as e:
            logger.error(f"Error preparing fine-tuning data: {e}")
            return {"error": str(e)}

# Instancia global
auto_trainer = AutoTrainer()