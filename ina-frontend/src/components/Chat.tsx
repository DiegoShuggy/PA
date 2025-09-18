import React, { useState, useRef, useEffect } from 'react';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // 1. Crear mensaje de usuario
    const userMessage: Message = { 
      text: inputMessage, 
      isUser: true, 
      timestamp: new Date() 
    };

    // 2. Limpiar input y actualizar estado INMEDIATAMENTE
    setInputMessage('');
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 3. Llamar al backend
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

      // 4. Agregar respuesta de IA
      const aiMessage: Message = { 
        text: data.response, 
        isUser: false, 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      // 5. Manejar error
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
            <div className="message-text">InA está pensando...</div>
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
          placeholder="Escribe tu pregunta o consulta..."
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? '...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};

export default Chat;