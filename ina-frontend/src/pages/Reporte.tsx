import React, { useState, useRef, useEffect } from 'react';
import '../css/Reporte.css';
import { useTranslation } from "react-i18next";
import { useNavigate } from 'react-router-dom';
import ina from '../img/InA6.png'

const Reporte = () => {
        console.log('Reporte component is rendering');
    const [password, setPassword] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [error, setError] = useState('');
    const [clickCount, setClickCount] = useState(0);
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    // Contraseña fija
    const fixedPassword = "hola";

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (password === fixedPassword) {
            setIsAuthenticated(true);
            setError('');
        } else {
            setError('Contraseña incorrecta');
            setPassword('');
        }
    };

    // Función para manejar el clic secreto
    const handleSecretClick = () => {
        // Limpiar temporizador anterior si existe

        const newCount = clickCount + 1;
        setClickCount(newCount);

        // Si llega a 10 clics, mostrar alerta y resetear
        if (newCount >= 10) {
            alert('¡Has descubierto la funcionalidad secreta!');
            setClickCount(0);
        }
    };

    // Cleanup del temporizador al desmontar el componente

    if (isAuthenticated) {
        return (
            <div>
                <h1>Contenido Protegido</h1>
                <p>¡Bienvenido! Has accedido correctamente.</p>
            </div>
        );
    }
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

        <div className="min-h-screen flex items-center justify-center bg-gray-100">
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
<div className="navbar-menu_container">
                    {/* Logo con funcionalidad secreta */}
                    <div className="navbar-brand" onClick={handleSecretClick}>
                        <img src={ina} alt="Logo" className="navbar-WAH" />
                    </div>
                    </div>
                    </div>
    );
};

export default Reporte;