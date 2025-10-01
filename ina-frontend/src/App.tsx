import React from 'react';
import Chat from './components/Chat';
import ConsultasR from './pages/ConsultasR';
import { Routes, Route } from 'react-router-dom';
import './App.css'; // Solo estilos globales

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <p>Powered by Mistral 7B</p>
        <h1>InA - Asistente Virtual Duoc UC</h1>
      </header>
      <main className='main-content'>
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/Consultas" element={<ConsultasR />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;