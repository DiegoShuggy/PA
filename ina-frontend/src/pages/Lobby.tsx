import React, { useRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';

function Lobby() {
    console.log('Lobby component is rendering');
    const { t } = useTranslation();
    const [fontSize, setFontSize] = useState<'small' | 'normal' | 'large'>('normal');
    const [lineHeight, setLineHeight] = useState<'normal' | 'large' | 'x-large'>('normal');
    const [highContrast, setHighContrast] = useState(false);
    const [grayscale, setGrayscale] = useState(false);
    const [showAccessibilityMenu, setShowAccessibilityMenu] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Aplicar los estilos de accesibilidad
    useEffect(() => {
        const root = document.documentElement;
        
        // Aplicar tamaño de fuente
        root.classList.remove('font-small', 'font-normal', 'font-large');
        root.classList.add(`font-${fontSize}`);
        
        // Aplicar altura de línea
        root.classList.remove('line-height-normal', 'line-height-large', 'line-height-x-large');
        root.classList.add(`line-height-${lineHeight}`);
        
        // Aplicar alto contraste
        if (highContrast) {
            root.classList.add('high-contrast');
        } else {
            root.classList.remove('high-contrast');
        }
        
        // Aplicar escala de grises
        if (grayscale) {
            root.classList.add('grayscale');
        } else {
            root.classList.remove('grayscale');
        }
    }, [fontSize, lineHeight, highContrast, grayscale]);

    // Resetear todas las opciones de accesibilidad
    const resetAccessibility = () => {
        setFontSize('normal');
        setLineHeight('normal');
        setHighContrast(false);
        setGrayscale(false);
    };

    return (
        <div className="lobby-container">
            {/* Botón flotante de accesibilidad */}
            <div className="accessibility-floating-button">
                <button
                    className="accessibility-toggle"
                    onClick={() => setShowAccessibilityMenu(!showAccessibilityMenu)}
                    title={t('accessibility.menu', 'Menú de accesibilidad')}
                    type="button"
                    aria-expanded={showAccessibilityMenu}
                >
                    <span className="accessibility-icon">♿</span>
                </button>

                {/* Menú desplegable de accesibilidad */}
                {showAccessibilityMenu && (
                    <div className="accessibility-menu">
                        <div className="accessibility-header">
                            <h4>{t('Accesibilidad.titulo')}</h4>
                            <button 
                                className="close-menu"
                                onClick={() => setShowAccessibilityMenu(false)}
                            >
                                ×
                            </button>
                        </div>
                        
                        <div className="accessibility-options">
                            {/* Tamaño de fuente */}
                            <div className="accessibility-option">
                                <label>{t('Accesibilidad.tamaño')}</label>
                                <div className="font-size-buttons">
                                    <button
                                        className={`font-size-btn ${fontSize === 'small' ? 'active' : ''}`}
                                        onClick={() => setFontSize('small')}
                                    >
                                        a
                                    </button>
                                    <button
                                        className={`font-size-btn ${fontSize === 'normal' ? 'active' : ''}`}
                                        onClick={() => setFontSize('normal')}
                                    >
                                        A
                                    </button>
                                    <button
                                        className={`font-size-btn ${fontSize === 'large' ? 'active' : ''}`}
                                        onClick={() => setFontSize('large')}
                                    >
                                        A+
                                    </button>
                                </div>
                            </div>

                            {/* Altura de línea */}
                            <div className="accessibility-option">
                                <label>{t('Accesibilidad.altura')}</label>
                                <div className="line-height-buttons">
                                    <button
                                        className={`line-height-btn ${lineHeight === 'normal' ? 'active' : ''}`}
                                        onClick={() => setLineHeight('normal')}
                                    >
                                        ─
                                    </button>
                                    <button
                                        className={`line-height-btn ${lineHeight === 'large' ? 'active' : ''}`}
                                        onClick={() => setLineHeight('large')}
                                    >
                                        ──
                                    </button>
                                    <button
                                        className={`line-height-btn ${lineHeight === 'x-large' ? 'active' : ''}`}
                                        onClick={() => setLineHeight('x-large')}
                                    >
                                        ───
                                    </button>
                                </div>
                            </div>

                            {/* Alto contraste */}
                            <div className="accessibility-option">
                                <label className="toggle-label">
                                    <input
                                        type="checkbox"
                                        checked={highContrast}
                                        onChange={(e) => setHighContrast(e.target.checked)}
                                    />
                                    <span className="toggle-slider"></span>
                                    {t('Accesibilidad.contraste')}
                                </label>
                            </div>

                            {/* Escala de grises */}
                            <div className="accessibility-option">
                                <label className="toggle-label">
                                    <input
                                        type="checkbox"
                                        checked={grayscale}
                                        onChange={(e) => setGrayscale(e.target.checked)}
                                    />
                                    <span className="toggle-slider"></span>
                                    {t('Accesibilidad.saturacion')}
                                </label>
                            </div>

                            {/* Botón de reset */}
                            <div className="accessibility-option">
                                <button
                                    className="reset-button"
                                    onClick={resetAccessibility}
                                >
                                    {t('Accesibilidad.restablecer')}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <h2>{t('Lobby.title')}</h2>
            <h3>{t('Lobby.Descripcion')}</h3>
            <div className="lobby-grid">
                {/* Tus elementos FAQ existentes */}
                <div className="FAQ">
                    <Link to="/ConsultasR" className="FAQ-link">
                        <div className="lobby-item uno">
                            <span>{t('Lobby.Preguntas.FAQ1')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">
                            <span>{t('Lobby.Preguntas.FAQ2')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">
                            <span>{t('Lobby.Preguntas.FAQ3')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ4')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ5')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item seis">
                            <span>{t('Lobby.Preguntas.FAQ6')}</span>
                        </div>
                    </Link>
                </div>
                
                <div className="FAQ">
                    <Link to="/Punto" className="FAQ-link">
                        <div className="lobby-item uno">
                            <span>{t('Lobby.Preguntas.FAQ7')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">
                            <span>{t('Lobby.Preguntas.FAQ8')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">
                            <span>{t('Lobby.Preguntas.FAQ9')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ10')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ11')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item seis">
                            <span>{t('Lobby.Preguntas.FAQ12')}</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}

export default Lobby;