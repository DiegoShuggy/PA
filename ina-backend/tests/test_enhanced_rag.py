import unittest
from datetime import datetime, timedelta
import json
import os
from app.memory_manager import MemoryManager
from app.response_generator import ResponseGenerator
from app.rag import RAGEngine

class TestEnhancedRAGSystem(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.rag_engine = RAGEngine()
        self.memory_manager = self.rag_engine.memory_manager
        self.response_generator = ResponseGenerator(self.rag_engine)
        self.test_session_id = "test_session_001"

    def test_memory_storage_and_retrieval(self):
        """Prueba el almacenamiento y recuperación de memoria"""
        # Test query
        test_query = "¿Dónde está ubicado el gimnasio de la sede?"
        test_response = "El gimnasio está ubicado en el tercer piso del edificio principal."
        test_metadata = {
            "category": "deportes",
            "confidence": 0.95
        }

        # Almacenar en memoria
        self.memory_manager.add_to_memory(
            test_query,
            test_response,
            test_metadata
        )

        # Buscar consulta similar
        similar_queries = self.memory_manager.find_similar_queries(
            "¿En qué piso está el gimnasio?"
        )

        self.assertTrue(len(similar_queries) > 0)
        self.assertGreater(similar_queries[0]['similarity'], 0.7)
        self.assertEqual(similar_queries[0]['response'], test_response)

    def test_conversation_context(self):
        """Prueba el manejo del contexto de conversación"""
        # Simular una conversación
        conversations = [
            ("¿Cuál es el horario del gimnasio?", "El gimnasio está abierto de 8:00 a 20:00"),
            ("¿Y los fines de semana?", "Los fines de semana el horario es de 9:00 a 18:00"),
            ("¿Necesito reservar?", "Sí, debes reservar a través de la app con 24 horas de anticipación")
        ]

        for query, response in conversations:
            self.memory_manager.add_to_conversation_history(
                self.test_session_id,
                query,
                response
            )

        context = self.memory_manager.get_conversation_context(self.test_session_id)
        self.assertIn("gimnasio", context.lower())
        self.assertIn("horario", context.lower())

    def test_response_generation(self):
        """Prueba la generación de respuestas con diferentes estrategias"""
        # Prueba saludo
        greeting_query = "Hola, ¿cómo estás?"
        greeting_result = self.response_generator.generate_response(
            greeting_query,
            self.test_session_id,
            {"processing_strategy": "greeting"}
        )
        self.assertIn("InA", greeting_result['response'])
        self.assertEqual(greeting_result['cache_type'], 'greeting')

        # Prueba emergencia
        emergency_query = "Necesito ayuda urgente, estoy en crisis"
        emergency_result = self.response_generator.generate_response(
            emergency_query,
            self.test_session_id,
            {"processing_strategy": "emergency"}
        )
        self.assertIn("urgente", emergency_result['response'].lower())
        self.assertEqual(emergency_result['cache_type'], 'emergency')

    def test_memory_expiry(self):
        """Prueba la caducidad de la memoria a corto plazo"""
        # Agregar entrada con timestamp antiguo
        old_query = "¿Cuál es el correo de contacto?"
        old_response = "El correo es contacto@duoc.cl"
        old_metadata = {
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "category": "contacto"
        }

        self.memory_manager.add_to_memory(
            old_query,
            old_response,
            old_metadata
        )

        # Forzar limpieza
        self.memory_manager._cleanup_old_entries()

        # Verificar que la entrada antigua fue eliminada
        similar_queries = self.memory_manager.find_similar_queries(old_query)
        self.assertTrue(len(similar_queries) == 0)

    def test_enhanced_query_processing(self):
        """Prueba el procesamiento mejorado de consultas"""
        # Prueba con sinónimos
        queries = [
            "¿Dónde saco el pase escolar?",
            "¿Cómo obtengo la TNE?",
            "¿Dónde tramito la tarjeta nacional estudiantil?"
        ]

        responses = []
        for query in queries:
            result = self.rag_engine.process_user_query(query)
            responses.append(result)

        # Verificar que las respuestas son similares (mismo tema)
        self.assertTrue(all('tne' in str(r).lower() for r in responses))

    def test_feedback_system(self):
        """Prueba el sistema de retroalimentación"""
        test_query = "¿Cómo reservo una cancha deportiva?"
        test_response = "Puedes reservar a través de la app MaiClub"

        # Agregar respuesta inicial
        self.memory_manager.add_to_memory(
            test_query,
            test_response,
            {"feedback_score": 0}
        )

        # Actualizar con feedback
        self.memory_manager.update_feedback(test_query, 1)

        # Verificar actualización
        similar_queries = self.memory_manager.find_similar_queries(test_query)
        self.assertEqual(similar_queries[0]['metadata']['feedback_score'], 1)

def run_integration_tests():
    """Ejecutar pruebas de integración completas"""
    print("Iniciando pruebas de integración del sistema RAG mejorado...")
    
    # Configurar suite de pruebas
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedRAGSystem)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generar reporte
    print("\nResultados de las pruebas:")
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_integration_tests()