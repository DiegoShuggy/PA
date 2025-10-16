import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import '../css/Chat.css';
import microIcon from '../img/Micro.png';
import { useNavigate } from 'react-router-dom';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  qr_codes?: { [url: string]: string };
  has_qr?: boolean;
  feedback_session_id?: string;
  chatlog_id?: number;
}

const Chat: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);

  // Estados para feedback
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentFeedbackSession, setCurrentFeedbackSession] = useState<string | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [showFollowup, setShowFollowup] = useState(false);
  const [currentRating, setCurrentRating] = useState<number>(0);
  const [userComments, setUserComments] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');
  const menuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const feedbackRef = useRef<HTMLDivElement>(null);

  // Nuevo ref para el controlador de aborto
  const abortControllerRef = useRef<AbortController | null>(null);

  // Función para volver a la página anterior
  const handleGoBack = () => {
    navigate(-1);
  };

  // Función para detener la generación
  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);

    // Opcional: agregar un mensaje indicando que se canceló
    const cancelMessage: Message = {
      text: t('chat.generationCancelled') || 'Generación cancelada',
      isUser: false,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, cancelMessage]);
  };


  // Cerrar feedback al hacer clic fuera - VERSIÓN CORREGIDA
  // Versión con debug completo


  // Inicializar el reconocimiento de voz
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;

      // Configurar idioma según el idioma actual
      const recognitionLang = i18n.language === 'es' ? 'es-ES' :
        i18n.language === 'fr' ? 'fr-FR' : 'en-US';
      recognition.lang = recognitionLang;

      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onresult = (event: any) => {
        let interimTranscript = '';
        let finalTranscript = finalTranscriptRef.current;

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        finalTranscriptRef.current = finalTranscript;
        setInputMessage(finalTranscript + interimTranscript);
      };

      recognition.onerror = (event: any) => {
        console.error('Error en reconocimiento de voz:', event.error);
        if (event.error === 'not-allowed') {
          alert(t('chat.microphonePermission'));
          setIsSpeechSupported(false);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        if (isListening) {
          try {
            recognition.start();
          } catch (e) {
            console.error('Error al reiniciar reconocimiento:', e);
            setIsListening(false);
          }
        }
      };

      recognitionRef.current = recognition;
    } else {
      console.warn('El reconocimiento de voz no es compatible con este navegador');
      setIsSpeechSupported(false);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      // Limpiar abort controller al desmontar
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [isListening, i18n.language, t]);

  // Función para cambiar idioma
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setIsLanguageMenuOpen(false);

    // Reiniciar reconocimiento de voz si está activo
    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
        setTimeout(() => {
          if (recognitionRef.current) {
            recognitionRef.current.start();
          }
        }, 100);
      } catch (e) {
        console.error('Error al reiniciar reconocimiento:', e);
      }
    }
  };

  // Función para resetear el feedback
  const resetFeedback = () => {
    setCurrentFeedbackSession(null);
    setFeedbackSubmitted(false);
    setShowFollowup(false);
    setCurrentRating(0);
    setUserComments('');
  };

  // Función para enviar feedback básico (Sí/No)
  const submitFeedback = async (isSatisfied: boolean) => {
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
        if (isSatisfied) {
          setFeedbackSubmitted(true);
          setTimeout(() => {
            setShowFeedback(false);
            resetFeedback();
          }, 2000);
        } else {
          setShowFollowup(true);
        }
      }
    } catch (error) {
      console.error(t('chat.feedbackServerError'), error);
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

  const toggleListening = () => {
    if (!recognitionRef.current || !isSpeechSupported) {
      alert(t('chat.browserNotSupported'));
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (e) {
        console.error('Error al detener reconocimiento:', e);
        setIsListening(false);
      }
    } else {
      try {
        finalTranscriptRef.current = inputMessage;
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error('Error al iniciar reconocimiento:', e);
        setIsListening(false);
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
    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (e) {
        console.error('Error al detener reconocimiento:', e);
      }
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
      // Solo mostrar error si no fue una cancelación
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
                  <p>Califica esta respuesta (opcional):</p>
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

  return (
    <div className="chat-wrapper">
      {/* Botón para volver atrás */}
      <button
        className="back-button"
        onClick={handleGoBack}
        title={t('app.backButton', 'Volver atrás')}
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
        </div>

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.isUser ? 'user-message' : 'ai-message'}`}>
              <div className="message-text">{msg.text}</div>

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
          ))}

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
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;