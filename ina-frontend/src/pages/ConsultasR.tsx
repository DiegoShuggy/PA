import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/ConsultasR.css';
import ina1 from '../css/asuntos.png';
import ina2 from '../css/faq.png';
import ina3 from '../css/desarrollo.png';
import ina4 from '../css/bienestar.png';
import ina5 from '../css/deportes.png';
import ina6 from '../css/pastoral.png';
import React, { useRef, useEffect, useState } from 'react';

function ConsultasR() {
    console.log('ConsultasR component is rendering');
    const { t, i18n } = useTranslation();
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    };

    useEffect(() => {
        scrollToBottom();
    }, []);

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
        <div className="consultas-container">
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

            <h2>{t('consultas.title', 'Área de Consultas')}</h2>
            
            <div className="areas-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item uno">
                            <img
                                src={ina1}
                                alt={t('consultas.areas.studentAffairs.alt', 'Asuntos Estudiantiles')}
                                className="imagen1"
                            />
                            <span>{t('consultas.areas.studentAffairs.title', 'Asuntos Estudiantiles')}</span>
                        </div>
                    </Link>
                </div>

                {/* Consultas Frecuentes / Frequent Queries / Questions Fréquentes */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item dos">
                            <img
                                src={ina2}
                                alt={t('consultas.areas.frequentQueries.alt', 'Consultas Frecuentes')}
                                className="imagen2"
                            />
                            <span>{t('consultas.areas.frequentQueries.title', 'Consultas Frecuentes')}</span>
                        </div>
                    </Link>
                </div>

                {/* Desarrollo Profesional y Titulados / Professional Development and Graduates / Développement Professionnel et Diplômés */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item tres">
                            <img
                                src={ina3}
                                alt={t('consultas.areas.professionalDevelopment.alt', 'Desarrollo Profesional y Titulados')}
                                className="imagen3"
                            />
                            <span>{t('consultas.areas.professionalDevelopment.title', 'Desarrollo Profesional y Titulados')}</span>
                        </div>
                    </Link>
                </div>

                {/* Bienestar Estudiantil / Student Selfcare / Bien-être Estudiantin */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item cuatro">
                            <img
                                src={ina4}
                                alt={t('consultas.areas.studentWelfare.alt', 'Bienestar Estudiantil')}
                                className="imagen4"
                            />
                            <span>{t('consultas.areas.studentWelfare.title', 'Bienestar Estudiantil')}</span>
                        </div>
                    </Link>
                </div>

                {/* Deportes / Sports / Sports */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item cinco">
                            <img
                                src={ina5}
                                alt={t('consultas.areas.sports.alt', 'Deportes')}
                                className="imagen5"
                            />
                            <span>{t('consultas.areas.sports.title', 'Deportes')}</span>
                        </div>
                    </Link>
                </div>

                {/* Pastoral / Pastoral / Pastorale */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item seis">
                            <img
                                src={ina6}
                                alt={t('consultas.areas.pastoral.alt', 'Pastoral')}
                                className="imagen6"
                            />
                            <span>{t('consultas.areas.pastoral.title', 'Pastoral')}</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}

export default ConsultasR;