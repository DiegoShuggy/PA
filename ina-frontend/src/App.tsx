import React from 'react';
import Chat from './pages/Chat';
import ConsultasR from './pages/ConsultasR';
import Lobby from './pages/Lobby';
import Asuntos  from './pages/Asuntos';
import Deportes from './pages/Deportes';
import Bienestar from './pages/Bienestar';
import Pastoral from './pages/Pastoral';
import Desarrollo from './pages/Desarrollo';
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
            <Route path="/ConsultasR" element={<ConsultasR />} />
            <Route path="/Asuntos" element={<Asuntos />} />
            <Route path="/Deportes" element={<Deportes />} />
            <Route path="/Bienestar" element={<Bienestar />} />
            <Route path="/Desarrollo" element={<Desarrollo />} />
            <Route path="/Pastoral" element={<Pastoral />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;