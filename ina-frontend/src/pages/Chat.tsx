import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import '../css/Chat.css';
import microIcon from '../img/Micro.png';
import { useNavigate, useLocation } from 'react-router-dom';
import '../css/Chat.css';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  qr_codes?: { [url: string]: string };
  has_qr?: boolean;
  feedback_session_id?: string;
  chatlog_id?: number;
}

interface LocationState {
  predefinedQuestion?: string;
  autoSend?: boolean;
}

// Interfaz extendida para el reconocimiento de voz
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  onnomatch: (() => void) | null;
  // Propiedades específicas para aumentar el tiempo de escucha
  timeout: number; // Tiempo máximo de escucha
  noSpeechTimeout: number; // Tiempo sin hablar para detenerse
}

declare global {
  interface Window {
    SpeechRecognition: {
      new(): SpeechRecognition;
    };
    webkitSpeechRecognition: {
      new(): SpeechRecognition;
    };
  }
}

const Chat: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);

  
  // Estados para el lector de texto (TTS)
  const [isReading, setIsReading] = useState(false);
  const [currentReadingIndex, setCurrentReadingIndex] = useState<number | null>(null);
  const [isTtsSupported, setIsTtsSupported] = useState(true);

  const [inactivityTime, setInactivityTime] = useState(0);
  const inactivityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inactivityCounterRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Configuración del temporizador de inactividad (en milisegundos)
  const INACTIVITY_TIMEOUT = 300000;
  const FEEDBACK_AUTO_PRESS_TIMEOUT = 299999; // 4.59 minutos para feedback automático

  // Agrega este estado adicional
  const feedbackAutoPressTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Estados para feedback
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentFeedbackSession, setCurrentFeedbackSession] = useState<string | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [showFollowup, setShowFollowup] = useState(false);
  const [currentRating, setCurrentRating] = useState<number>(0);
  const [userComments, setUserComments] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalTranscriptRef = useRef('');
  const menuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const feedbackRef = useRef<HTMLDivElement>(null);
  const isStartingRef = useRef(false);
  const silenceTimerRef = useRef<number | null>(null);
  const restartTimerRef = useRef<number | null>(null);

  // Referencias para el lector de texto
  const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Obtener la pregunta predefinida del estado de navegación
  const abortControllerRef = useRef<AbortController | null>(null);
  // Función para volver a la página anterior
  const handleGoBack = () => {
    navigate(-1);
  };

 // INICIO - FUNCIONALIDAD DEL LECTOR DE TEXTO (TEXT-TO-SPEECH)
// Agregar un ref para controlar si la detención fue manual
const isManualStopRef = useRef(false);
// Ref para controlar si ya se leyó un mensaje
const hasBeenReadRef = useRef<Set<number>>(new Set());

// Función para detener la lectura actual
const stopReading = useCallback((isManual = false) => {
  if (isManual) {
    isManualStopRef.current = true;
  }
  
  if (speechSynthesisRef.current) {
    // Cancelar inmediatamente
    speechSynthesisRef.current.cancel();

    // Limpiar referencia
    currentUtteranceRef.current = null;

    // Resetear estados inmediatamente
    setIsReading(false);
    setCurrentReadingIndex(null);
  }
}, []);

// Verificar soporte del lector de texto al cargar el componente
useEffect(() => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    speechSynthesisRef.current = window.speechSynthesis;
    setIsTtsSupported(true);

    // Función para cargar voces en Chrome
    const loadVoices = () => {
      if (speechSynthesisRef.current) {
        try {
          // Esperar a que Chrome cargue las voces
          const waitForVoices = (attempt = 1) => {
            const voices = speechSynthesisRef.current?.getVoices() || [];

            if (voices.length > 0) {
              console.log(`✅ ${voices.length} voces cargadas en intento ${attempt}:`);
              voices.forEach(voice => {
                console.log(`   - ${voice.name} (${voice.lang})`);
              });
            } else if (attempt < 10) {
              console.log(`⏳ Esperando voces... intento ${attempt}`);
              setTimeout(() => waitForVoices(attempt + 1), 500);
            } else {
              console.warn('⚠️ No se pudieron cargar voces después de 10 intentos');
            }
          };

          waitForVoices(1);
        } catch (error) {
          console.error('Error cargando voces:', error);
        }
      }
    };

    // Configurar event listener para cuando las voces cambien
    speechSynthesisRef.current.onvoiceschanged = loadVoices;

    // Cargar voces inicialmente
    loadVoices();

  } else {
    setIsTtsSupported(false);
    console.warn('El lector de texto no es compatible con este navegador');
  }

  // Cleanup: detener lectura cuando el componente se desmonta
  return () => {
    stopReading();
    // Limpiar el set de mensajes leídos
    hasBeenReadRef.current.clear();
  };
}, [stopReading]);

// Función para leer un mensaje en voz alta
const readMessage = useCallback((text: string, messageIndex: number, isAutoRead = false) => {
  // Si es lectura automática y hubo una detención manual, no leer
  if (isAutoRead && isManualStopRef.current) {
    console.log('🚫 Lectura automática bloqueada por detención manual');
    return;
  }

  // Si el mensaje ya fue leído y es lectura automática, no repetir
  if (isAutoRead && hasBeenReadRef.current.has(messageIndex)) {
    console.log('🚫 Mensaje ya fue leído anteriormente, no repetir');
    return;
  }

  if (!speechSynthesisRef.current || !isTtsSupported) {
    alert(t('chat.ttsNotSupported') || 'El lector de texto no es compatible con este navegador.');
    return;
  }

  // Resetear el flag de detención manual si es una lectura manual
  if (!isAutoRead) {
    isManualStopRef.current = false;
  }

  // Detener cualquier lectura en curso ANTES de crear el nuevo utterance
  stopReading();

  // Pequeña pausa para asegurar que se detuvo completamente
  setTimeout(() => {
    try {
      // Configurar el idioma para la síntesis de voz
      const ttsLang = i18n.language === 'es' ? 'es-ES' :
        i18n.language === 'fr' ? 'fr-FR' : 'en-US';

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = ttsLang;
      utterance.rate = 0.8;
      utterance.pitch = 1.4;
      utterance.volume = 1;

      // BUSCAR Y SELECCIONAR UNA VOZ FEMENINA ESPECÍFICA
      const voices = speechSynthesisRef.current?.getVoices() || [];
      console.log('Todas las voces disponibles:', voices.map(v => ({ name: v.name, lang: v.lang })));

      let femaleVoice = null;

      // BUSCAR VOCES FEMENINAS ESPECÍFICAS POR NOMBRE
      const femaleVoiceNames = [
        // Voces femeninas en español
        'google español', 'español', 'spanish', 'mujer', 'female', 'femenina',
        'mexico', 'colombia', 'argentina', 'latina', 'latino', 'españa',
        'sabina', 'helena', 'juana', 'catalina', 'sofia', 'valeria',
        'google español de estados unidos', 'microsoft sabina', 'microsoft helena'
      ];

      const maleVoiceNames = [
        // Voces masculinas a EVITAR
        'raul', 'pablo', 'carlos', 'diego', 'jorge', 'miguel', 'male', 'masculino',
        'microsoft raul', 'microsoft pablo', 'google español masculino'
      ];

      // Primero buscar voces femeninas explícitas
      for (let voice of voices) {
        const voiceName = voice.name.toLowerCase();
        const voiceLang = voice.lang.toLowerCase();

        // Verificar que sea del idioma correcto
        if (!voiceLang.startsWith(ttsLang.substring(0, 2))) continue;

        // Buscar características femeninas en el nombre
        const isFemale = femaleVoiceNames.some(femaleName =>
          voiceName.includes(femaleName.toLowerCase())
        );

        // Evitar voces masculinas explícitas
        const isMale = maleVoiceNames.some(maleName =>
          voiceName.includes(maleName.toLowerCase())
        );

        if (isFemale && !isMale) {
          femaleVoice = voice;
          console.log('✅ Voz femenina encontrada:', voice.name);
          break;
        }
      }

      // Si no encontramos voz femenina explícita, buscar cualquier voz que no sea masculina
      if (!femaleVoice) {
        for (let voice of voices) {
          const voiceName = voice.name.toLowerCase();
          const voiceLang = voice.lang.toLowerCase();

          if (!voiceLang.startsWith(ttsLang.substring(0, 2))) continue;

          // Evitar voces masculinas conocidas
          const isMale = maleVoiceNames.some(maleName =>
            voiceName.includes(maleName.toLowerCase())
          );

          if (!isMale) {
            femaleVoice = voice;
            console.log('⚠️ Usando voz no-masculina:', voice.name);
            break;
          }
        }
      }

      // Si todavía no hay voz, usar la primera voz disponible del idioma
      if (!femaleVoice) {
        femaleVoice = voices.find(voice =>
          voice.lang.startsWith(ttsLang.substring(0, 2))
        );
        console.warn('🚨 Usando primera voz disponible:', femaleVoice?.name);
      }

      if (femaleVoice) {
        utterance.voice = femaleVoice;
        console.log('🎯 Voz seleccionada finalmente:', femaleVoice.name);
      } else {
        console.error('❌ No se pudo encontrar ninguna voz adecuada');
      }

      utterance.onstart = () => {
        setIsReading(true);
        setCurrentReadingIndex(messageIndex);
        console.log(`🔊 ${isAutoRead ? 'Auto-' : ''}Lectura iniciada con voz:`, utterance.voice?.name);
      };

      utterance.onend = () => {
        console.log(`✅ ${isAutoRead ? 'Auto-' : ''}Lectura finalizada`);
        setIsReading(false);
        setCurrentReadingIndex(null);
        currentUtteranceRef.current = null;
        
        // Marcar el mensaje como leído
        if (isAutoRead) {
          hasBeenReadRef.current.add(messageIndex);
        }
        
        // Resetear el flag de detención manual cuando termina naturalmente
        if (!isAutoRead) {
          isManualStopRef.current = false;
        }
      };

      utterance.onerror = (event) => {
        console.error(`❌ Error en la ${isAutoRead ? 'auto-' : ''}lectura:`, event.error);
        setIsReading(false);
        setCurrentReadingIndex(null);
        currentUtteranceRef.current = null;

        if (event.error !== 'interrupted') {
          console.warn('Error de TTS:', event.error);
        }
        
        // Resetear el flag de detención manual en caso de error
        if (!isAutoRead) {
          isManualStopRef.current = false;
        }
      };

      // Prevenir que se agregue múltiples veces el mismo utterance
      if (currentUtteranceRef.current === utterance) {
        console.log('🚫 Utterance duplicado detectado, cancelando');
        return;
      }

      currentUtteranceRef.current = utterance;

      // Pequeño delay antes de empezar a hablar
      setTimeout(() => {
        if (speechSynthesisRef.current && currentUtteranceRef.current === utterance) {
          speechSynthesisRef.current.speak(utterance);
        }
      }, 100);

    } catch (error) {
      console.error('💥 Error al configurar la lectura:', error);
      setIsReading(false);
      setCurrentReadingIndex(null);
    }
  }, 50);
}, [i18n.language, t, isTtsSupported, stopReading]);

// Función para alternar lectura de un mensaje
const toggleReading = useCallback((message: Message, index: number) => {
  if (isReading && currentReadingIndex === index) {
    // Si ya está leyendo este mensaje, detener (marcar como manual)
    stopReading(true);
  } else {
    // Si está leyendo otro mensaje, detener y empezar este
    if (isReading) {
      stopReading(true);
    }
    // Leer el mensaje seleccionado (no es automático)
    readMessage(message.text, index, false);
  }
}, [isReading, currentReadingIndex, readMessage, stopReading]);

// Efecto para limpiar la lectura cuando el componente se desmonta o cambia el idioma
useEffect(() => {
  return () => {
    stopReading();
  };
}, [stopReading]);

// Efecto para resetear el estado de mensajes leídos cuando cambian los mensajes
useEffect(() => {
  // Limpiar el set de mensajes leídos cuando los mensajes cambian significativamente
  hasBeenReadRef.current.clear();
}, [messages.length]); // Se resetea cuando cambia la cantidad de mensajes

// FIN - FUNCIONALIDAD DEL LECTOR DE TEXTO

  // Función para resetear el feedback - MOVER ARRIBA DE submitFeedback
  const resetFeedback = useCallback(() => {
    setCurrentFeedbackSession(null);
    setFeedbackSubmitted(false);
    setShowFollowup(false);
    setCurrentRating(0);
    setUserComments('');
    // Limpiar timer de feedback automático
    if (feedbackAutoPressTimerRef.current) {
      clearTimeout(feedbackAutoPressTimerRef.current);
      feedbackAutoPressTimerRef.current = null;
    }
  }, []); // No tiene dependencias

  // Función para enviar feedback básico (Sí/No) - CON useCallback
  const submitFeedback = useCallback(async (isSatisfied: boolean) => {
    if (!currentFeedbackSession) {
      console.error(t('chat.feedbackError'));
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/feedback/response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currentFeedbackSession: currentFeedbackSession,
          isSatisfied: isSatisfied
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (response.ok) {
        console.log(`Feedback ${isSatisfied ? 'positivo' : 'negativo'} enviado exitosamente`);

        if (isSatisfied) {
          setFeedbackSubmitted(true);
          setTimeout(() => {
            setShowFeedback(false);
            resetFeedback();
          }, 2000);
        } else {
          setShowFollowup(true);
        }

        if (feedbackAutoPressTimerRef.current) {
          clearTimeout(feedbackAutoPressTimerRef.current);
          feedbackAutoPressTimerRef.current = null;
        }
      }
    } catch (error) {
      console.error(t('chat.feedbackServerError'), error);
    }
  }, [currentFeedbackSession, t, resetFeedback]); // AGREGAR resetFeedback COMO DEPENDENCIA


  // LUEGO la función autoPressFeedbackButton
  const autoPressFeedbackButton = useCallback(() => {
    console.log('Presionando automáticamente botón de feedback por inactividad');

    // Verificar que el feedback esté visible y no se haya enviado
    if (showFeedback && !feedbackSubmitted && currentFeedbackSession) {
      console.log('Condiciones cumplidas - enviando feedback positivo automáticamente');

      // Presionar el botón "Sí" (feedback positivo) automáticamente
      submitFeedback(true);

      // Limpiar el timer después de ejecutar
      if (feedbackAutoPressTimerRef.current) {
        clearTimeout(feedbackAutoPressTimerRef.current);
        feedbackAutoPressTimerRef.current = null;
      }
    } else {
      console.log('Feedback automático no ejecutado - condiciones:', {
        showFeedback,
        feedbackSubmitted,
        hasSession: !!currentFeedbackSession
      });
    }
  }, [showFeedback, feedbackSubmitted, currentFeedbackSession, submitFeedback])

  // Función para reiniciar el temporizador de inactividad
  const resetInactivityTimer = useCallback(() => {
    setInactivityTime(0);

    // Limpiar temporizadores existentes
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }
    if (inactivityCounterRef.current) {
      clearInterval(inactivityCounterRef.current);
    }
    if (feedbackAutoPressTimerRef.current) {
      clearTimeout(feedbackAutoPressTimerRef.current);
      feedbackAutoPressTimerRef.current = null;
    }

    // Crear nuevo temporizador de redirección
    inactivityTimerRef.current = setTimeout(() => {
      console.log('Tiempo de inactividad agotado - redirigiendo...');
      navigate('/');
    }, INACTIVITY_TIMEOUT);

    // SOLO crear temporizador para feedback automático si el feedback está visible
    if (showFeedback && !feedbackSubmitted && currentFeedbackSession) {
      feedbackAutoPressTimerRef.current = setTimeout(() => {
        console.log('20 segundos de inactividad - activando feedback automático');
        autoPressFeedbackButton();
      }, FEEDBACK_AUTO_PRESS_TIMEOUT);
    }

    // Opcional: Contador para debug
    inactivityCounterRef.current = setInterval(() => {
      setInactivityTime(prev => prev + 1000);
    }, 1000);
  }, [navigate, showFeedback, feedbackSubmitted, currentFeedbackSession, autoPressFeedbackButton]); // AGREGAR DEPENDENCIAS FALTANTES
  // Función para manejar eventos de actividad
  const handleActivity = useCallback(() => {
    resetInactivityTimer();
  }, [resetInactivityTimer]);

  // Efecto para inicializar los detectores de actividad
  useEffect(() => {
    // Lista de eventos que indican actividad del usuario
    const events = [
      'mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart',
      'click', 'input', 'focus', 'submit'
    ];

    // Agregar event listeners
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    // Iniciar el temporizador por primera vez
    resetInactivityTimer();

    // Cleanup: remover event listeners y limpiar temporizadores
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });

      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
      if (inactivityCounterRef.current) {
        clearInterval(inactivityCounterRef.current);
      }
      if (feedbackAutoPressTimerRef.current) {
        clearTimeout(feedbackAutoPressTimerRef.current);
      }
    };
  }, [handleActivity, resetInactivityTimer]);
  useEffect(() => {
    return () => {
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
      if (inactivityCounterRef.current) {
        clearInterval(inactivityCounterRef.current);
      }
      if (feedbackAutoPressTimerRef.current) {
        clearTimeout(feedbackAutoPressTimerRef.current);
      }
    };
  }, []);

  // Efecto opcional para mostrar el tiempo de inactividad en consola (debug)
  useEffect(() => {
    if (inactivityTime > 0 && inactivityTime % 5000 === 0) {
      console.log(`Tiempo de inactividad: ${inactivityTime / 1000} segundos`);
    }
  }, [inactivityTime]);


  // Función para detener la generación
  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);

    const cancelMessage: Message = {
      text: t('chat.generationCancelled') || 'Generación cancelada',
      isUser: false,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, cancelMessage]);
  };

  // Inicializar el reconocimiento de voz - VERSIÓN MEJORADA CON DURACIÓN EXTENDIDA
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('El reconocimiento de voz no es compatible con este navegador');
      setIsSpeechSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();

      // CONFIGURACIÓN MEJORADA PARA DURACIÓN EXTENDIDA
      recognition.continuous = true; // Cambiado a true para escucha continua
      recognition.interimResults = true;
      recognition.maxAlternatives = 3; // Más alternativas para mejor precisión

      // Configurar idioma según el idioma actual
      const recognitionLang = i18n.language === 'es' ? 'es-ES' :
        i18n.language === 'fr' ? 'fr-FR' : 'en-US';
      recognition.lang = recognitionLang;

      // Configuraciones específicas para navegadores Webkit (Chrome, Safari)
      if ('webkitSpeechRecognition' in window) {
        // Estas propiedades pueden ayudar a extender el tiempo de escucha
        (recognition as any).continuous = true;
        (recognition as any).interimResults = true;

        // Intentar configurar tiempo máximo de escucha (no estándar pero funciona en algunos navegadores)
        try {
          (recognition as any).maxDuration = 60000; // 60 segundos máximo
        } catch (e) {
          console.log('maxDuration no soportado');
        }
      }

      recognition.onstart = () => {
        console.log('Reconocimiento de voz iniciado - Modo escucha extendida');
        isStartingRef.current = false;

        // Reiniciar el temporizador de silencio
        resetSilenceTimer();
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        // Reiniciar el temporizador de silencio cada vez que se detecte voz
        resetSilenceTimer();

        let interimTranscript = '';
        let finalTranscript = finalTranscriptRef.current;

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        finalTranscriptRef.current = finalTranscript;
        setInputMessage(finalTranscript + interimTranscript);

        console.log('Voz detectada - Reiniciando temporizador');
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Error en reconocimiento de voz:', event.error);
        isStartingRef.current = false;
        clearSilenceTimer();

        switch (event.error) {
          case 'not-allowed':
          case 'permission-denied':
            alert(t('chat.microphonePermission') || 'Permiso de micrófono denegado. Por favor, permite el acceso al micrófono en la configuración de tu navegador.');
            setIsSpeechSupported(false);
            break;
          case 'audio-capture':
            alert(t('chat.microphoneNotFound') || 'No se encontró ningún micrófono. Por favor, conecta un micrófono e intenta de nuevo.');
            setIsSpeechSupported(false);
            break;
          case 'network':
            alert(t('chat.speechRecognitionError') || 'Error de red en el reconocimiento de voz.');
            break;
          case 'no-speech':
            console.log('No se detectó voz - continuando escucha');
            // No detenemos en caso de no detectar voz, continuamos escuchando
            return;
          default:
            console.warn('Error de reconocimiento de voz:', event.error);
        }

        setIsListening(false);
      };

      recognition.onend = () => {
        console.log('Reconocimiento de voz finalizado');
        isStartingRef.current = false;
        clearSilenceTimer();

        // Solo reiniciar si todavía estamos en modo escucha
        if (isListening && !silenceTimerRef.current) {
          console.log('Reiniciando reconocimiento de voz automáticamente...');
          setTimeout(() => {
            if (isListening && recognitionRef.current) {
              try {
                recognitionRef.current.start();
              } catch (error) {
                console.error('Error al reiniciar reconocimiento:', error);
                setIsListening(false);
              }
            }
          }, 500);
        }
      };

      recognition.onnomatch = () => {
        console.log('No se reconoció el discurso - continuando escucha');
        // Continuar escuchando incluso si no hay coincidencia
        resetSilenceTimer();
      };

      recognitionRef.current = recognition;
      setIsSpeechSupported(true);
    } catch (error) {
      console.error('Error al inicializar reconocimiento de voz:', error);
      setIsSpeechSupported(false);
    }

    return () => {
      clearSilenceTimer();
      if (restartTimerRef.current) {
        clearTimeout(restartTimerRef.current);
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.error('Error al detener reconocimiento en cleanup:', error);
        }
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [i18n.language, t]);

  // Temporizador de silencio - se detiene después de 30 segundos sin voz
  const resetSilenceTimer = () => {
    clearSilenceTimer();
    silenceTimerRef.current = setTimeout(() => {
      console.log('Temporizador de silencio agotado - deteniendo escucha');
      if (isListening) {
        setIsListening(false);
      }
    }, 30000); // 30 segundos de silencio antes de detenerse
  };
  // Efecto para manejar el timer automático cuando cambia el estado del feedback
  useEffect(() => {
    // Cuando el feedback se muestra, iniciar el timer automático si no existe
    if (showFeedback && !feedbackSubmitted && currentFeedbackSession) {
      if (!feedbackAutoPressTimerRef.current) {
        console.log('Feedback visible - iniciando timer de 4,59 minutos para feedback automático');
        feedbackAutoPressTimerRef.current = setTimeout(() => {
          console.log('Timer de feedback automático ejecutado');
          autoPressFeedbackButton();
        }, FEEDBACK_AUTO_PRESS_TIMEOUT);
      }
    } else {
      // Cuando el feedback se oculta o se envía, limpiar el timer
      if (feedbackAutoPressTimerRef.current) {
        console.log('Feedback no visible o enviado - limpiando timer automático');
        clearTimeout(feedbackAutoPressTimerRef.current);
        feedbackAutoPressTimerRef.current = null;
      }
    }

    // Cleanup
    return () => {
      if (feedbackAutoPressTimerRef.current) {
        clearTimeout(feedbackAutoPressTimerRef.current);
        feedbackAutoPressTimerRef.current = null;
      }
    };
  }, [showFeedback, feedbackSubmitted, currentFeedbackSession, autoPressFeedbackButton]);

  const clearSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  // Efecto para sincronizar el estado de escucha
  useEffect(() => {
    if (!recognitionRef.current) return;

    if (isListening && !isStartingRef.current) {
      startRecognition();
    }

    if (!isListening) {
      stopRecognition();
    }
  }, [isListening]);

  // Función mejorada para iniciar reconocimiento
  const startRecognition = async () => {
    if (!recognitionRef.current || isStartingRef.current) return;

    try {
      // Solicitar permiso de micrófono primero
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (error) {
        console.error('Error al acceder al micrófono:', error);
        alert(t('chat.microphonePermission') || 'Permiso de micrófono denegado.');
        setIsSpeechSupported(false);
        setIsListening(false);
        return;
      }

      isStartingRef.current = true;
      finalTranscriptRef.current = inputMessage;

      // Configuración adicional para escucha extendida
      const recognition = recognitionRef.current;
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.start();
      console.log('Iniciando reconocimiento de voz - Escucha extendida activada');

    } catch (error) {
      console.error('Error al iniciar reconocimiento:', error);
      isStartingRef.current = false;
      setIsListening(false);
      setIsSpeechSupported(false);
    }
  };

  // Función mejorada para detener reconocimiento
  const stopRecognition = () => {
    if (!recognitionRef.current) return;

    try {
      clearSilenceTimer();
      recognitionRef.current.stop();
      isStartingRef.current = false;
      console.log('Reconocimiento de voz detenido manualmente');
    } catch (error) {
      console.error('Error al detener reconocimiento:', error);
    }
  };

  // Función para cambiar idioma
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setIsLanguageMenuOpen(false);

    // Reiniciar reconocimiento de voz si está activo
    if (isListening && recognitionRef.current) {
      try {
        stopRecognition();
        setTimeout(() => {
          const recognitionLang = lng === 'es' ? 'es-ES' :
            lng === 'fr' ? 'fr-FR' : 'en-US';
          if (recognitionRef.current) {
            recognitionRef.current.lang = recognitionLang;
          }
          if (isListening) {
            startRecognition();
          }
        }, 500);
      } catch (e) {
        console.error('Error al reiniciar reconocimiento:', e);
      }
    }
  };






  // Función para enviar feedback detallado
  const submitDetailedFeedback = async () => {
    if (!currentFeedbackSession) {
      console.error(t('chat.feedbackError'));
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/feedback/response/detailed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currentFeedbackSession: currentFeedbackSession,
          userComments: userComments,
          rating: currentRating || null
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (response.ok) {
        setFeedbackSubmitted(true);
        setTimeout(() => {
          setShowFeedback(false);
          resetFeedback();
        }, 2000);
      }
    } catch (error) {
      console.error(t('chat.feedbackServerError'), error);
    }
  };

  // Efecto para manejar la pregunta predefinida y auto-enviar
  useEffect(() => {
    const locationState = location.state as LocationState;

    if (locationState?.predefinedQuestion) {
      setInputMessage(locationState.predefinedQuestion);

      // Si autoSend es true, enviar automáticamente después de un breve delay
      if (locationState.autoSend) {
        const timer = setTimeout(() => {
          handleAutoSend(locationState.predefinedQuestion!);
        }, 500);

        return () => clearTimeout(timer); // Cleanup
      } else {
        // Solo enfocar el input si no es auto-envío
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
      }
    }
  }, [location.state]);

  // Función para manejar el envío automático
  const handleAutoSend = async (question: string) => {
    if (!question.trim() || isLoading) return;

    // Detener reconocimiento de voz si está activo
    if (isListening) {
      setIsListening(false);
    }

    const userMessage: Message = {
      text: question,
      isUser: true,
      timestamp: new Date()
    };

    // Limpiar input
    setInputMessage('');
    finalTranscriptRef.current = '';

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Crear nuevo abort controller para esta petición
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: question }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(t('chat.serverError'));
      }

      const data = await response.json();

      // Normalizar qr_codes
      let qrCodesObj: { [url: string]: string } = {};
      if (Array.isArray(data.qr_codes)) {
        data.qr_codes.forEach((qr: any) => {
          if (qr.url && qr.qr_data) {
            qrCodesObj[qr.url] = qr.qr_data;
          }
        });
      } else if (typeof data.qr_codes === 'object' && data.qr_codes !== null) {
        qrCodesObj = data.qr_codes;
      }

      const aiMessage: Message = {
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        qr_codes: qrCodesObj,
        has_qr: data.has_qr || false,
        feedback_session_id: data.feedback_session_id,
        chatlog_id: data.chatlog_id
      };

      setMessages(prev => [...prev, aiMessage]);

      // Mostrar feedback después de la respuesta de Ina
      if (data.feedback_session_id) {
        setCurrentFeedbackSession(data.feedback_session_id);
        setShowFeedback(true);
        setFeedbackSubmitted(false);
        setShowFollowup(false);
      }

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Error:', error);
        const errorMessage: Message = {
          text: t('chat.serverError'),
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  // Función mejorada para toggle del micrófono
  const toggleListening = async () => {
    if (!recognitionRef.current || !isSpeechSupported) {
      alert(t('chat.browserNotSupported') || 'El reconocimiento de voz no es compatible con este navegador.');
      return;
    }

    if (isListening) {
      setIsListening(false);
      finalTranscriptRef.current = ''; // Limpiar transcripción al detener
    } else {
      // Verificar permisos antes de iniciar
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        setIsListening(true);
      } catch (error) {
        console.error('Error de permisos de micrófono:', error);
        alert(t('chat.microphonePermission') || 'Permiso de micrófono denegado. Por favor, permite el acceso al micrófono.');
        setIsSpeechSupported(false);
      }
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleLanguageMenu = () => {
    setIsLanguageMenuOpen(!isLanguageMenuOpen);
  };

  const handleMenuAction = (action: string) => {
    setIsMenuOpen(false);

    switch (action) {
      case 'clear':
        setMessages([]);
        stopReading(); // Detener lectura al limpiar chat
        break;
      case 'help':
        alert(t('chat.helpMessage'));
        break;
      case 'greeting':
        insertText(t('chat.quickActions.greeting'));
        break;
      case 'thanks':
        insertText(t('chat.quickActions.thanks'));
        break;
      case 'Laboral':
        insertText(t('chat.quickActions.internships'));
        break;
      case 'Consultas':
        insertText(t('chat.quickActions.faq'));
        break;
      case 'TNE':
        insertText(t('chat.quickActions.tne'));
        break;
      default:
        break;
    }
  };

  const insertText = (text: string) => {
    const newText = inputMessage ? `${inputMessage} ${text}` : text;
    setInputMessage(newText);

    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    if (!inputMessage.trim() || isLoading) return;

    // Detener reconocimiento de voz si está activo
    if (isListening) {
      setIsListening(false);
    }

    const userMessage: Message = {
      text: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    // Limpiar input inmediatamente
    const messageToSend = inputMessage;
    setInputMessage('');
    finalTranscriptRef.current = '';

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Crear nuevo abort controller para esta petición
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: messageToSend
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(t('chat.serverError'));
      }

      const data = await response.json();

      // Normalizar qr_codes
      let qrCodesObj: { [url: string]: string } = {};
      if (Array.isArray(data.qr_codes)) {
        data.qr_codes.forEach((qr: any) => {
          if (qr.url && qr.qr_data) {
            qrCodesObj[qr.url] = qr.qr_data;
          }
        });
      } else if (typeof data.qr_codes === 'object' && data.qr_codes !== null) {
        qrCodesObj = data.qr_codes;
      }

      const aiMessage: Message = {
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        qr_codes: qrCodesObj,
        has_qr: data.has_qr || false,
        feedback_session_id: data.feedback_session_id,
        chatlog_id: data.chatlog_id
      };

      setMessages(prev => [...prev, aiMessage]);

      // Mostrar feedback después de la respuesta de Ina
      if (data.feedback_session_id) {
        setCurrentFeedbackSession(data.feedback_session_id);
        setShowFeedback(true);
        setFeedbackSubmitted(false);
        setShowFollowup(false);
      }

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Error:', error);
        const errorMessage: Message = {
          text: t('chat.serverError'),
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Función para renderizar códigos QR
  const renderQRCodes = (qr_codes: { [url: string]: string }) => {
    return Object.entries(qr_codes).map(([url, qrData], index) => (
      <div key={index} className="qr-code-container">
        <div className="qr-code-header">
          <span className="qr-icon">📱</span>
          <span className="qr-url">{url}</span>
        </div>
        <img
          src={qrData}
          alt={t('chat.qrAlt', { url })}
          className="qr-code-image"
        />
        <div className="qr-instruction">{t('chat.qrInstruction')}</div>
      </div>
    ));
  };
  // Agrega este useEffect para lectura automática
useEffect(() => {
  // Si hubo una detención manual, no activar lectura automática
  if (isManualStopRef.current) {
    return;
  }

  // Buscar el último mensaje de la AI que no se haya leído
  const lastAIMessageIndex = messages.findIndex((msg, index) => 
    !msg.isUser && 
    index > (currentReadingIndex ?? -1)
  );

  // Si hay un nuevo mensaje de AI y no estamos leyendo actualmente
  if (lastAIMessageIndex !== -1 && !isReading && isTtsSupported) {
    const lastAIMessage = messages[lastAIMessageIndex];
    
    // Pequeño delay para que el usuario pueda ver el mensaje primero
    const autoReadTimer = setTimeout(() => {
      console.log('🔊 Lectura automática del mensaje:', lastAIMessageIndex);
      readMessage(lastAIMessage.text, lastAIMessageIndex, true); // <-- Agregar true para indicar que es automática
    }, 1000); // 1 segundo de delay

    return () => clearTimeout(autoReadTimer);
  }
}, [messages, isReading, currentReadingIndex, isTtsSupported, readMessage]);


  // Componente de Feedback
  const renderFeedbackWidget = () => {
    if (!showFeedback) return null;

    return (
      <div className="feedback-widget" ref={feedbackRef}>
        {!feedbackSubmitted ? (
          <>
            {!showFollowup ? (
              <div className="feedback-prompt">
                <p>{t('chat.feedback.initialQuestion')}</p>
                <div className="feedback-buttons">
                  <button
                    className="feedback-btn positive"
                    onClick={() => submitFeedback(true)}
                    type="button"
                  >
                    {t('chat.feedback.positive')}
                  </button>
                  <button
                    className="feedback-btn negative"
                    onClick={() => submitFeedback(false)}
                    type="button"
                  >
                    {t('chat.feedback.negative')}
                  </button>
                </div>
              </div>
            ) : (
              <div className="feedback-followup">
                <h4>{t('chat.feedback.thankYouImprove')}</h4>
                <p>{t('chat.feedback.improvementQuestion')}</p>

                <div className="rating-section">
                  <p>{t('chat.feedback.optional')}</p>
                  <div className="star-rating">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <span
                        key={star}
                        className={`star ${currentRating >= star ? 'filled' : ''}`}
                        onClick={() => setCurrentRating(star)}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                </div>

                <textarea
                  value={userComments}
                  onChange={(e) => setUserComments(e.target.value)}
                  placeholder={t('chat.feedback.commentsPlaceholder')}
                  rows={3}
                ></textarea>

                <div className="feedback-actions">
                  <button
                    onClick={submitDetailedFeedback}
                    className="submit-btn"
                    type="button"
                    disabled={!userComments.trim() && currentRating === 0}
                  >
                    {t('chat.feedback.submitComments')}
                  </button>
                  <button
                    onClick={() => {
                      setShowFeedback(false);
                      resetFeedback();
                    }}
                    className="cancel-btn"
                    type="button"
                  >
                    {t('chat.feedback.cancel')}
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="feedback-thankyou">
            <p>{t('chat.feedback.thankYouFinal')}</p>
          </div>
        )}
      </div>
    );
  };

  // Función para renderizar cada mensaje con botón de lectura
  const renderMessage = (msg: Message, index: number) => {
    const isCurrentMessageReading = isReading && currentReadingIndex === index;

    return (
      <div key={index} className={`message ${msg.isUser ? 'user-message' : 'ai-message'}`}>
        <div className="message-content">
          <div className="message-text">{msg.text}</div>

          {!msg.isUser && isTtsSupported && (
            <button
              className={`tts-button ${isCurrentMessageReading ? 'reading' : ''}`}
              onClick={() => toggleReading(msg, index)}
              type="button"
              title={isCurrentMessageReading ?
                (t('chat.stopReading') || 'Detener lectura') :
                (t('chat.readAloud') || 'Leer en voz alta')}
            >
              {isCurrentMessageReading ? '⏹️' : '🔊'}
            </button>
          )}
        </div>

        {msg.qr_codes && Object.keys(msg.qr_codes).length > 0 && (
          <div className="qr-codes-section">
            <div className="qr-section-title">{t('chat.qrSectionTitle')}</div>
            <div className="qr-codes-container">
              {renderQRCodes(msg.qr_codes)}
            </div>
          </div>
        )}

        <div className="message-time">
          {msg.timestamp.toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-wrapper">
      {/* Botón para volver atrás */}
      <button
        className="back-button"
        onClick={handleGoBack}
        title={t('app.backButton')}
      >
        <span className="back-arrow">←</span>
        {t('app.back')}
      </button>

      {/* Botón del menú flotante */}
      <div className="floating-menu-container" ref={menuRef}>
        <button
          className="floating-menu-button"
          onClick={toggleMenu}
          title={t('chat.menuTitle')}
          type="button"
        >
          <span className="menu-icon">☰</span>
        </button>

        {isMenuOpen && (
          <div className="floating-dropdown-menu">
            <div className="menu-section">
              <div className="menu-section-title">{t('chat.menu.quickQuestions')}</div>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('greeting')}
                type="button"
              >
                <span className="menu-icon">👋</span>
                {t('chat.menu.greetIna')}
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('Laboral')}
                type="button"
              >
                <span className="menu-icon">📋</span>
                {t('chat.menu.internships')}
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('Consultas')}
                type="button"
              >
                <span className="menu-icon">❓</span>
                {t('chat.menu.faq')}
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('TNE')}
                type="button"
              >
                <span className="menu-icon">📋</span>
                {t('chat.menu.tne')}
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('thanks')}
                type="button"
              >
                <span className="menu-icon">🙏</span>
                {t('chat.menu.thankIna')}
              </button>
            </div>

            <div className="menu-divider"></div>

            <div className="menu-section">
              <div className="menu-section-title">{t('chat.menu.tools')}</div>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('clear')}
                disabled={messages.length === 0}
                type="button"
              >
                <span className="menu-icon">🗑️</span>
                {t('chat.menu.clearChat')}
              </button>
            </div>

            <div className="menu-divider"></div>

            <button
              className="menu-item"
              onClick={() => handleMenuAction('settings')}
              type="button"
            >
              <span className="menu-icon">⚙️</span>
              {t('chat.menu.settings')}
            </button>
            <button
              className="menu-item"
              onClick={() => handleMenuAction('help')}
              type="button"
            >
              <span className="menu-icon">❓</span>
              {t('chat.menu.help')}
            </button>
          </div>
        )}
      </div>

      {/* Contenedor del chat */}
      <div className="chat-container" id="Cuerpo">
        <div className="chat-header">
          <h2>{t('chat.title')}</h2>
          <div className="quick-tips">
            {t('chat.quickTips')}
          </div>
          {isListening && (
            <div className="extended-listening-info">
            </div>
          )}
        </div>

        <div className="chat-messages">
          {messages.map((msg, index) => renderMessage(msg, index))}

          {renderFeedbackWidget()}

          {isLoading && (
            <div className="message ai-message">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* FORMULARIO ACTUALIZADO */}
        <form
          className="chat-input"
          onSubmit={handleSendMessage}
        >
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isListening ? t('chat.listeningPlaceholder') : t('chat.inputPlaceholder')}
            disabled={isLoading}
          />
          <button
            className={`mic-button ${isListening ? 'listening' : ''}`}
            onClick={toggleListening}
            type="button"
            disabled={isLoading || !isSpeechSupported}
            title={isListening ? t('chat.stopMicrophone') : t('chat.startMicrophone')}
          >
            <img
              src={microIcon}
              alt={t('chat.microphoneAlt')}
              className="mic-icon"
            />
          </button>
          {isLoading ? (
            <button
              type="button"
              onClick={stopGeneration}
              className="stop-button"
              title={t('chat.stopGeneration') || 'Detener generación'}
            >
              {t('chat.stopGeneration')}
            </button>
          ) : (
            <button
              type="submit"
              disabled={!inputMessage.trim()}
            >
              {t('chat.send')}
            </button>
          )}
        </form>

        {isListening && (
          <div className="voice-status">
            <div className="pulse-ring"></div>
            <div className="listening-text">
              {t('chat.listening')}
            </div>
            <div className="silence-timer">
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;