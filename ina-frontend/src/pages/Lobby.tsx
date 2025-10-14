import React, { useRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';


function Lobby() {
    console.log('Lobby component is rendering');
    const { t, i18n } = useTranslation();
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);


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
        <div className="lobby-container">
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

            <h2>{t('Lobby.title')}</h2>
            <h3>{t('Lobby.Descripcion')}</h3>
            <div className="lobby-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="FAQ">
                    <Link to="/ConsultasR" className="FAQ-link">
                        <div className="lobby-item uno">

                            <span>{t('Lobby.Preguntas.FAQ1', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Consultas Frecuentes / Frequent Queries / Questions Fréquentes */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">

                            <span>{t('Lobby.Preguntas.FAQ2', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Desarrollo Profesional y Titulados / Professional Development and Graduates / Développement Professionnel et Diplômés */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">

                            <span>{t('Lobby.Preguntas.FAQ3', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Bienestar Estudiantil / Student Selfcare / Bien-être Estudiantin */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Deportes / Sports / Sports */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ5', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Pastoral / Pastoral / Pastorale */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item seis">
                            <span>{t('Lobby.Preguntas.FAQ6', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>
                <div className="FAQ">
                    <Link to="/Punto" className="FAQ-link">
                        <div className="lobby-item uno">

                            <span>{t('Lobby.Preguntas.FAQ7', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Consultas Frecuentes / Frequent Queries / Questions Fréquentes */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">

                            <span>{t('Lobby.Preguntas.FAQ8', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Desarrollo Profesional y Titulados / Professional Development and Graduates / Développement Professionnel et Diplômés */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">

                            <span>{t('Lobby.Preguntas.FAQ9', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Bienestar Estudiantil / Student Selfcare / Bien-être Estudiantin */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ10', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Deportes / Sports / Sports */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ11', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* Pastoral / Pastoral / Pastorale */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item seis">
                            <span>{t('Lobby.Preguntas.FAQ12', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}

export default Lobby;