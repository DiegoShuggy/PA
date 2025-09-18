import React from 'react';
import Chat from './components/Chat';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <p>Powered by Mistral 7B</p>
        <h1>InA - Asistente Virtual Duoc UC</h1>
        
      </header>
      <main>
        <Chat />
      </main>
    </div>
  );
}

export default App;