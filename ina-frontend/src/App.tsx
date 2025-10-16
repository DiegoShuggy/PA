import React, { useState, useRef, useEffect } from 'react';
import Chat from './pages/Chat';
import ConsultasR from './pages/ConsultasR';
import Lobby from './pages/Lobby';
import Asuntos from './pages/Asuntos';
import Deportes from './pages/Deportes';
import Bienestar from './pages/Bienestar';
import Pastoral from './pages/Pastoral';
import Desarrollo from './pages/Desarrollo';
import Reporte from './pages/Reporte';
import { Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './App.css'; // Solo estilos globales
import './translation/i18n'; // Importa la configuración de i18n
import NavBar from './components/NavBar';

function App() {
    const { i18n, t } = useTranslation();
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);

    // Cerrar el menú al hacer clic fuera
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (languageMenuRef.current && !languageMenuRef.current.contains(event.target as Node)) {
                setIsLanguageMenuOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
        setIsLanguageMenuOpen(false);
    };

    return (
        <div className="app">
            <div>
                <NavBar />
                {/* Selector de idiomas global */}
                <div className="language-selector-global" ref={languageMenuRef}>
                    <button
                        className="language-selector-button"
                        onClick={() => setIsLanguageMenuOpen(!isLanguageMenuOpen)}
                        title={t('chat.languageSelector', 'Seleccionar idioma')}
                        type="button"
                    >
                        <span className="language-icon">🌐</span>
                        <span className="current-language">
                            {i18n.language === 'es' ? 'ES' : i18n.language === 'fr' ? 'FR' : 'EN'}
                        </span>
                    </button>

                    {isLanguageMenuOpen && (
                        <div className="language-dropdown-menu">
                            <button
                                className={`language-option ${i18n.language === 'es' ? 'active' : ''}`}
                                onClick={() => changeLanguage('es')}
                                type="button"
                            >
                                <span className="flag">🇪🇸</span>
                                Español
                            </button>
                            <button
                                className={`language-option ${i18n.language === 'en' ? 'active' : ''}`}
                                onClick={() => changeLanguage('en')}
                                type="button"
                            >
                                <span className="flag">🇺🇸</span>
                                English
                            </button>
                            <button
                                className={`language-option ${i18n.language === 'fr' ? 'active' : ''}`}
                                onClick={() => changeLanguage('fr')}
                                type="button"
                            >
                                <span className="flag">🇫🇷</span>
                                Français
                            </button>
                        </div>
                    )}
                </div>
                
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
                        <Route path="/Reporte" element={<Reporte />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
}

export default App;