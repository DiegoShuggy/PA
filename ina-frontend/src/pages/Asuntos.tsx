import React, { useState, useRef, useEffect } from 'react';
import '../css/Asuntos.css';
import Profile from '../css/InA3.png';
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from 'react-router-dom';

export function Asuntos() {
    console.log('Asuntos component is rendering');
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Función para volver a la página anterior
    const handleGoBack = () => {
        navigate(-1); // -1 significa ir a la página anterior en el historial
    };

    // Cerrar menú de idiomas al hacer clic fuera
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

    // Función para cambiar idioma
    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
        setIsLanguageMenuOpen(false);
    };

    return (
        <div className="Asuntos-container">
            {/* Botón para volver atrás */}
            <button 
                className="back-button"
                onClick={handleGoBack}
                title={t('app.backButton', 'Volver atrás')}
            >
                <span className="back-arrow">←</span>
                {t('Asuntos.back', 'Volver')}
            </button>

            {/* Selector de idiomas */}
            <div className="language-selector-container" ref={languageMenuRef}>
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
            <div className='Perfil-container'>
                {/* Contenedor para imagen y título */}
                <div className='imagen-titulo-container'>
                    <img src={Profile} alt="Profile" className="Perfil-imagen" />
                    <h2 className='tiutlo'>{t('Asuntos.title')}</h2>
                </div>
                
                {/* Contenedor para la descripción con título extra */}
                <div className='descripcion-container'>
                    {/* Título extra encima de la descripción */}
                    <h3 className='titulo-extra'>{t('Asuntos.cargo')}</h3>
                    
                    {/* Descripción */}
                    <p className='desc'>
                        {t('Asuntos.Descripcion')} <br />
                        <br />{t('Asuntos.Descripcion2')}
                        <br />{t('Asuntos.Descripcion3')}
                    </p>
                </div>
            </div>
            <div className="lobby-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item uno">
                            <span>{t('Lobby.Preguntas.FAQ1', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>
            </div>
        </div>
    )
}
export default Asuntos;