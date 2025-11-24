// components/VoiceSearch.tsx (VERSIÓN SIMPLIFICADA)
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

interface VoiceSearchProps {
  onSearch?: (query: string) => void;
  onQuestionSelect?: (questionText: string) => void;
  onVoiceTranscript?: (transcript: string) => void;
}

const VoiceSearch: React.FC<VoiceSearchProps> = ({ 
  onSearch, 
  onQuestionSelect,
  onVoiceTranscript
}) => {
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

  const [lastTranscript, setLastTranscript] = useState<string>('');

  // Comandos de navegación
  const voiceCommands: Record<string, string> = {
    'inicio': '/',
    'lobby': '/',
    'chat': '/InA',
    'asistente': '/InA',
    'ina': '/InA',
    'el punto': '/Punto',
    'punto': '/Punto',
    'punto estudiantil': '/Punto',
    'preguntas frecuentes': '/Punto',
    'asuntos': '/asuntos',
    'asuntos estudiantiles': '/asuntos',
    'bienestar': '/bienestar',
    'bienestar estudiantil': '/bienestar',
    'deportes': '/deportes',
    'futbol': '/deportes',
    'baby futbol': '/deportes',
    'basketball': '/deportes',
    'basket': '/deportes',
    'gimnasio': '/deportes',
    'Titulados': '/desarrollo',
    'Desarrollo Profesional y Titulados': '/desarrollo',
    'desarrollo profesional': '/desarrollo',
    'desarrollo': '/desarrollo',
    'pastoral': '/pastoral',
    'iglesia': '/pastoral',
    'home': '/',
    'assistant': '/InA',
    'school board': '/Punto',
    'frequently asked questions': '/Punto',
  };

  const questionCommands: { [key: string]: string } = {
    'Cómo puedo inscribirme en un programa académico en Duoc UC': 'Lobby.Preguntas.FAQ2',
    'programa academico': 'Lobby.Preguntas.FAQ2',
    'inscribir programa academico': 'Lobby.Preguntas.FAQ2',
    'renovar tne': 'Lobby.Preguntas.FAQ3',
    'donde renovar tne': 'Lobby.Preguntas.FAQ3',
    'renovación tne': 'Lobby.Preguntas.FAQ3',
    'donde puedo renovar mi tne': 'Lobby.Preguntas.FAQ3',
  };

  useEffect(() => {
    if (transcript && transcript !== lastTranscript) {
      setLastTranscript(transcript);
      processVoiceCommand(transcript);
    }
  }, [transcript, lastTranscript]);

  const findBestMatch = (command: string, commandMap: { [key: string]: any }): string | null => {
    const normalizedCommand = command.toLowerCase().trim();
    
    // Coincidencia exacta
    if (commandMap[normalizedCommand]) {
      return normalizedCommand;
    }

    // Coincidencia por similitud
    let bestMatch: string | null = null;
    let bestScore = 0;

    for (const [key] of Object.entries(commandMap)) {
      const keyWords = key.toLowerCase().split(/\s+/);
      const commandWords = normalizedCommand.split(/\s+/);
      
      const matchingWords = commandWords.filter(word => 
        keyWords.some(keyWord => keyWord.includes(word) || word.includes(keyWord))
      ).length;

      const similarity = matchingWords / Math.max(commandWords.length, keyWords.length);
      
      if (similarity > bestScore && similarity >= 0.6) {
        bestScore = similarity;
        bestMatch = key;
      }
    }

    return bestMatch;
  };

  const processVoiceCommand = (command: string) => {
    const normalizedCommand = command.toLowerCase().trim();
    console.log('🎯 Procesando comando de voz:', normalizedCommand);

    // 1. Verificar comandos de navegación
    const navigationMatch = findBestMatch(normalizedCommand, voiceCommands);
    if (navigationMatch) {
      console.log('🧭 Navegando a:', voiceCommands[navigationMatch]);
      navigate(voiceCommands[navigationMatch]);
      return;
    }

    // 2. Verificar preguntas específicas
    const questionMatch = findBestMatch(normalizedCommand, questionCommands);
    if (questionMatch) {
      const questionText = t(questionCommands[questionMatch]);
      console.log('❓ Pregunta específica:', questionText);
      
      if (onQuestionSelect) {
        onQuestionSelect(questionText);
      } else {
        // Fallback directo
        navigate('/InA', { 
          state: { 
            predefinedQuestion: questionText,
            autoSend: true
          } 
        });
      }
      return;
    }

    // 3. Consulta general
    console.log('💬 Consulta general:', command);
    
    if (onQuestionSelect) {
      onQuestionSelect(command);
    } else {
      navigate('/InA', { 
        state: { 
          predefinedQuestion: command,
          autoSend: true
        } 
      });
    }

    // Callbacks adicionales
    if (onVoiceTranscript) onVoiceTranscript(command);
    if (onSearch) onSearch(command);
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
      setLastTranscript('');
    } else {
      startListening();
      setLastTranscript('');
    }
  };

  if (!hasRecognitionSupport) {
    return (
      <div className="voice-search-unsupported">
        <p>{t('VoiceSearch.notSupported')}</p>
      </div>
    );
  }

  return (
    <div className="voice-search-container">
      <button
        onClick={toggleListening}
        className={`voice-search-button ${isListening ? 'listening' : ''}`}
      >
        {isListening ? (
          <>
            <span className="pulse-animation"></span>
            🎤 {t('VoiceSearch.listening')}
            {transcript && (
              <span className="voice-transcript-preview">
                : "{transcript.length > 20 ? transcript.substring(0, 20) + '...' : transcript}"
              </span>
            )}
          </>
        ) : (
          <>🎤 {t('VoiceSearch.talk')}</>
        )}
      </button>
    </div>
  );
};

export default VoiceSearch;