// components/VoiceSearch.tsx (versión actualizada)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

interface VoiceSearchProps {
  onSearch?: (query: string) => void;
  onQuestionSelect?: (questionText: string) => void;
}

const VoiceSearch: React.FC<VoiceSearchProps> = ({ onSearch, onQuestionSelect }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const {
    transcript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    hasRecognitionSupport,
  } = useSpeechRecognition();

  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [autoNavigate, setAutoNavigate] = useState<string | null>(null);

  // Mapeo de comandos de voz a rutas
    const voiceCommands: Record<string, string> = {
      // Comandos en español
    'inicio': '/',
    'lobby': '/',
    'chat': '/InA',
    'asistente': '/InA',
    'punto estudiantil': '/ConsultasR',
    'preguntas frecuentes': '/ConsultasR',
    'asuntos': '/asuntos',
    'asuntos estudiantiles': '/asuntos',
    'bienestar': '/bienestar',
    'deportes': '/deportes',
    'desarrollo': '/desarrollo',
    'reportes': '/reportes',
    'pastoral': '/pastoral',
    'iglesia': '/pastoral',
    
    // Comandos en inglés
    'home': '/',
    'assistant': '/InA',
    'school board': '/ConsultasR',
    'frequently asked questions': '/ConsultasR',
  };

  // Mapeo de preguntas específicas a sus textos traducidos
  const questionCommands: { [key: string]: string } = {
    // Preguntas en español - variaciones comunes
    
    
    'Cómo puedo inscribirme en un programa académico en Duoc UC': 'Lobby.Preguntas.FAQ2',
    'programa academico': 'Lobby.Preguntas.FAQ2',
    'inscribir programa academico': 'Lobby.Preguntas.FAQ2',
    
    'renovar tne': 'Lobby.Preguntas.FAQ3',
    'donde renovar tne': 'Lobby.Preguntas.FAQ3',
    'renovación tne': 'Lobby.Preguntas.FAQ3',
    'donde puedo renovar mi tne': 'Lobby.Preguntas.FAQ3',
    // Agrega más variaciones según necesites
  };

  // Procesar el transcript cuando cambie
  useEffect(() => {
    if (transcript) {
      processVoiceCommand(transcript);
    }
  }, [transcript]);

// components/VoiceSearch.tsx (función corregida)
const findBestMatch = (command: string, commandMap: { [key: string]: any }): string | null => {
  const normalizedCommand = command.toLowerCase().trim();
  
  // 1. Primero buscar coincidencia EXACTA (máxima prioridad)
  if (commandMap[normalizedCommand]) {
    console.log('✅ Coincidencia exacta encontrada:', normalizedCommand);
    return normalizedCommand;
  }

  // 2. Buscar coincidencias de frases completas
  const commandWords = normalizedCommand.split(/\s+/);
  
  // Para cada comando en el mapa, calcular similitud
  let bestMatch: string | null = null;
  let bestScore = 0;
  const MIN_SIMILARITY_THRESHOLD = 0.6; // 60% de similitud mínimo

  for (const [key] of Object.entries(commandMap)) {
    const keyWords = key.toLowerCase().split(/\s+/);
    
    // Calcular similitud basada en palabras coincidentes
    const matchingWords = commandWords.filter(word => 
      keyWords.some(keyWord => {
        // Coincidencia exacta de palabra
        if (keyWord === word) return true;
        // Coincidencia de palabra incluida
        if (keyWord.includes(word) || word.includes(keyWord)) return true;
        return false;
      })
    ).length;

    const similarity = matchingWords / Math.max(commandWords.length, keyWords.length);
    
    if (similarity > bestScore && similarity >= MIN_SIMILARITY_THRESHOLD) {
      bestScore = similarity;
      bestMatch = key;
    }
  }

  if (bestMatch) {
    console.log(`✅ Coincidencia por similitud: "${bestMatch}" (score: ${bestScore.toFixed(2)})`);
    return bestMatch;
  }

  // 3. Solo como último recurso, buscar palabras sueltas (pero con restricciones)
  for (const [key] of Object.entries(commandMap)) {
    const keyWords = key.toLowerCase().split(/\s+/);
    
    // Solo considerar coincidencia si la palabra es significativa
    const significantWords = keyWords.filter(word => word.length > 3); // Ignorar palabras cortas
    
    const hasSignificantMatch = significantWords.some(significantWord =>
      normalizedCommand.includes(significantWord)
    );

    if (hasSignificantMatch) {
      console.log(`⚠️ Coincidencia débil encontrada: "${key}"`);
      return key;
    }
  }

  console.log('❌ No se encontraron coincidencias para:', normalizedCommand);
  return null;
};

  const processVoiceCommand = (command: string) => {
    const normalizedCommand = command.toLowerCase().trim();
    console.log('Procesando comando:', normalizedCommand);

    // Primero buscar si es una pregunta específica
    const questionMatch = findBestMatch(normalizedCommand, questionCommands);
    
    if (questionMatch && questionCommands[questionMatch]) {
      const translationKey = questionCommands[questionMatch];
      const questionText = t(translationKey);
      
      console.log('Pregunta detectada:', questionMatch, 'Texto:', questionText);
      
      // Navegar al chat automáticamente con la pregunta
      if (onQuestionSelect) {
        onQuestionSelect(questionText);
      } else {
        // Navegación por defecto si no hay callback
        navigate('/InA', { 
          state: { 
            predefinedQuestion: questionText,
            autoSend: true
          } 
        });
      }
      
      setAutoNavigate(questionText);
      setShowResults(false);
      return;
    }

    // Si no es una pregunta, buscar comandos de navegación
    const navigationMatch = findBestMatch(normalizedCommand, voiceCommands);
    
    if (navigationMatch && voiceCommands[navigationMatch]) {
      const route = voiceCommands[navigationMatch];
      console.log('Navegación detectada:', navigationMatch, 'Ruta:', route);
      executeNavigation(route, navigationMatch);
      return;
    }

    // Si no hay coincidencias, mostrar mensaje
    setSearchResults([t('VoiceSearch.noResults') || 'No se encontraron resultados']);
    setShowResults(true);
    
    // Llamar al callback si existe
    if (onSearch) {
      onSearch(command);
    }
  };

  const executeNavigation = (route: string, command: string) => {
    console.log(`Navegando a: ${route} por comando: ${command}`);
    navigate(route);
    setShowResults(false);
    setSearchResults([]);
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
      setShowResults(false);
      setSearchResults([]);
      setAutoNavigate(null);
    }
  };

  if (!hasRecognitionSupport) {
    return (
      <div className="voice-search-unsupported">
        <p>{t('VoiceSearch.notSupported') || 'El reconocimiento de voz no es compatible con tu navegador'}</p>
      </div>
    );
  }

  return (
    <div className="voice-search-container">
      <button
        onClick={toggleListening}
        className={`voice-search-button ${isListening ? 'listening' : ''}`}
        aria-label={isListening ? 
          (t('VoiceSearch.stopListening') || 'Detener escucha') : 
          (t('VoiceSearch.startListening') || 'Iniciar escucha por voz')
        }
      >
        {isListening ? (
          <>
            <span className="pulse-animation"></span>
            🎤 {t('VoiceSearch.listening') || 'Escuchando...'}
          </>
        ) : (
          <>
            🎤 {t('VoiceSearch.talk') || 'Habla ahora'}
          </>
        )}
      </button>

      {transcript && (
        <div className="voice-transcript">
          <strong>{t('VoiceSearch.recognized') || 'Reconocido'}:</strong> {transcript}
        </div>
      )}

      {autoNavigate && (
        <div className="voice-auto-navigate">
          <div className="navigating-message">
            ✅ {t('VoiceSearch.navigatingTo') || 'Navegando a'}: "{autoNavigate}"
          </div>
        </div>
      )}

      {showResults && searchResults.length > 0 && (
        <div className="voice-results">
          <h4>{t('VoiceSearch.results') || 'Resultados'}:</h4>
          <ul>
            {searchResults.map((result, index) => (
              <li key={index} className="voice-result-item">
                {result}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default VoiceSearch;