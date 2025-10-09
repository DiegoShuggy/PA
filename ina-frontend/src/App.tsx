import React from 'react';
import Chat from './pages/Chat';
import ConsultasR from './pages/ConsultasR';
import Lobby from './pages/Lobby';
import { Routes, Route } from 'react-router-dom';
import './App.css'; // Solo estilos globales
import './translation/i18n'; // Importa la configuración de i18n
import NavBar from './components/NavBar';
function App() {
  return (
    <div className="app">
      <div>
        <NavBar />
        <main className='main-content'>
          <Routes>
            <Route path="/" element={<Lobby />} />
            <Route path="/InA" element={<Chat />} />
            <Route path="/Punto" element={<ConsultasR />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;