import React, { useState, useRef, useEffect } from 'react';
import '../css/Chat.css';
import microIcon from '../css/Micro.png';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  qr_codes?: { [url: string]: string };
  has_qr?: boolean;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');
  const menuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);



  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cerrar menú al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);


  // Inicializar el reconocimiento de voz

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.lang = 'es-ES';
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
          alert('Por favor permite el acceso al micrófono en tu navegador');
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
    };
  }, [isListening]);

  const toggleListening = () => {
    if (!recognitionRef.current || !isSpeechSupported) {
      alert('Tu navegador no soporta reconocimiento de voz. Prueba con Chrome o Edge.');
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

  const handleMenuAction = (action: string) => {
    setIsMenuOpen(false);

    switch (action) {
      case 'clear':
        setMessages([]);
        break;
      case 'help':
        alert('Mostrar ayuda del chat');
        break;
      // Nuevas opciones que insertan texto
      case 'greeting':
        insertText('¡Hola InA! ¿Podrías ayudarme con');
        break;
      case 'thanks':
        insertText('¡Muchas gracias por tu ayuda InA, WAH!');
        break;
      case 'Laboral':
        insertText('¿Podrías explicarme como es el proceso de Practicas Laborales en DuocUC?');
        break;
      case 'Consultas':
        insertText('¿Podrías darme más información sobre DuocUC?');
        break;
      case 'TNE':
        insertText('¿Podrías explicarme como es el proceso de Obtencion/validación de TNE en DuocUC?');
        break;
      default:
        break;
    }
  };

  const insertText = (text: string) => {
    // Si ya hay texto, agregar un espacio antes del nuevo texto
    const newText = inputMessage ? `${inputMessage} ${text}` : text;
    setInputMessage(newText);

    // Enfocar el input para que el usuario pueda escribir inmediatamente
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

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

    setInputMessage('');
    finalTranscriptRef.current = '';
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: inputMessage
        })
      });

      if (!response.ok) {
        throw new Error('Error en la respuesta del servidor');
      }

      const data = await response.json();

      const aiMessage: Message = {
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        qr_codes: data.qr_codes || {},
        has_qr: data.has_qr || false
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      const errorMessage: Message = {
        text: 'Error al conectar con el servidor',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
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
          alt={`QR code para ${url}`}
          className="qr-code-image"
        />
        <div className="qr-instruction">Escanea con tu celular</div>
      </div>
    ));
  };

  return (
    <div className="chat-wrapper" >
      {/* Botón del menú flotante en la esquina derecha */}
      <div className="floating-menu-container" ref={menuRef}>
        <button
          className="floating-menu-button"
          onClick={toggleMenu}
          title="Opciones del chat"
        >
          <span className="menu-icon">☰</span>
        </button>

        {isMenuOpen && (
          <div className="floating-dropdown-menu">
            {/* Sección de preguntas rápidas */}
            <div className="menu-section">
              <div className="menu-section-title">Preguntas rápidas</div>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('greeting')}
              >
                <span className="menu-icon">👋</span>
                Saluda a InA
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('Laboral')}
              >
                <span className="menu-icon">📋</span>
                Practicas laborales
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('Consultas')}
              >
                <span className="menu-icon">❓</span>
                Consultas frecuentes
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('TNE')}
              >
                <span className="menu-icon">📋</span>
                Consultas TNE
              </button>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('thanks')}
              >
                <span className="menu-icon">🙏</span>
                Agradecer a InA
              </button>
            </div>

            <div className="menu-divider"></div>

            {/* Sección de herramientas */}
            <div className="menu-section">
              <div className="menu-section-title">Herramientas</div>
              <button
                className="menu-item"
                onClick={() => handleMenuAction('clear')}
                disabled={messages.length === 0}
              >
                <span className="menu-icon">🗑️</span>
                Limpiar chat
              </button>
            </div>

            <div className="menu-divider"></div>

            {/* Sección de información */}
            <button
              className="menu-item"
              onClick={() => handleMenuAction('settings')}
            >
              <span className="menu-icon">⚙️</span>
              Configuración
            </button>
            <button
              className="menu-item"
              onClick={() => handleMenuAction('help')}
            >
              <span className="menu-icon">❓</span>
              Ayuda
            </button>
          </div>
        )}
      </div>

      {/* Contenedor del chat */}
      <div className="chat-container" id="Cuerpo">
        <div className="chat-header">
          <h2>Chat Asistente</h2>
          <div className="quick-tips">
            Usa el menú ☰ para preguntas rápidas
          </div>
        </div>

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.isUser ? 'user-message' : 'ai-message'}`}>
              <div className="message-text">{msg.text}</div>

              {/* Mostrar códigos QR si existen */}
              {msg.has_qr && msg.qr_codes && (
                <div className="qr-codes-section">
                  <div className="qr-section-title">📱 Escanear con celular:</div>
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

        <div className="chat-input">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={isListening ? "Escuchando... Habla ahora" : "Escribe tu pregunta o consulta..."}
            disabled={isLoading}
          />
          <button
            className={`mic-button ${isListening ? 'listening' : ''}`}
            onClick={toggleListening}
            type="button"
            disabled={isLoading || !isSpeechSupported}
            title={isListening ? "Detener micrófono" : "Activar micrófono"}
          >
            <img
              src={microIcon}
              alt="Micrófono"
              className="mic-icon"
            />
          </button>
          <button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()}>
            {isLoading ? '...' : 'Enviar'}
          </button>
        </div>

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