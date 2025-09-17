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

  // ✅ FUNCIÓN DONDE VA EL CÓDIGO QUE ME MOSTRASTE
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Agregar mensaje del usuario al chat
    const userMessage: Message = { 
      text: inputMessage, 
      isUser: true, 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    

    try {
      // ✅ AQUÍ ESTÁ EL CÓDIGO EXACTO PARA LLAMAR AL BACKEND
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

      // Agregar respuesta de la IA al chat
      const aiMessage: Message = { 
        text: data.response, 
        isUser: false, 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, aiMessage]);
      console.log("Respuesta de la IA:", data.response);
      

    } catch (error) {
      // Manejar errores
      const errorMessage: Message = { 
        text: 'Error al conectar con el servidor. Verifica que el backend esté ejecutándose.', 
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
            <div className="loading">InA está pensando...</div>
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