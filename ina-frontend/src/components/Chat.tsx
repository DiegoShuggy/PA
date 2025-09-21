import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          // Solo reiniciar si aún debería estar escuchando
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
      // Detener la escucha
      try {
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (e) {
        console.error('Error al detener reconocimiento:', e);
        setIsListening(false);
      }
    } else {
      // Comenzar a escuchar
      try {
        finalTranscriptRef.current = inputMessage; // Mantener el texto existente
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error('Error al iniciar reconocimiento:', e);
        setIsListening(false);
      }
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Detener la grabación si está activa
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
        timestamp: new Date() 
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

  return (
    <div className="chat-container">
      
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user-message' : 'ai-message'}`}>
            <div className="message-text">{msg.text}</div>
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
          <span className="mic-icon"></span>
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
  );
};

export default Chat;