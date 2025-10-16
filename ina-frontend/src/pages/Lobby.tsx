import React, { useRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';

function Lobby() {
    console.log('Lobby component is rendering');
    const { t } = useTranslation();
    const [fontSize, setFontSize] = useState<'small' | 'normal' | 'large'>('normal');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Aplicar el tamaño de fuente al body o elemento raíz
    useEffect(() => {
        const root = document.documentElement;
        root.classList.remove('font-small', 'font-normal', 'font-large');
        root.classList.add(`font-${fontSize}`);
    }, [fontSize]);

    

    // Función para cambiar tamaño de fuente automáticamente
    const toggleFontSize = () => {
        const sizes: ('small' | 'normal' | 'large')[] = ['small', 'normal', 'large'];
        const currentIndex = sizes.indexOf(fontSize);
        const nextIndex = (currentIndex + 1) % sizes.length;
        setFontSize(sizes[nextIndex]);
    };

    // Obtener el ícono correspondiente al tamaño actual
    const getFontSizeIcon = () => {
        switch (fontSize) {
            case 'small': return 'A';
            case 'normal': return 'A';
            case 'large': return 'A+';
            default: return 'A';
        }
    };

    // Obtener el texto descriptivo del tamaño actual
    const getFontSizeLabel = () => {
        switch (fontSize) {
            case 'small': return t('fontSize.small', 'Pequeño');
            case 'normal': return t('fontSize.normal', 'Normal');
            case 'large': return t('fontSize.large', 'Grande');
            default: return t('fontSize.normal', 'Normal');
        }
    };

    return (
        <div className="lobby-container">
            {/* Contenedor para controles de accesibilidad */}
            <div className="accessibility-controls">
                {/* Botón de cambio automático de tamaño de fuente */}
                <div className="font-size-toggle-container">
                    <button
                        className="font-size-toggle-button"
                        onClick={toggleFontSize}
                        title={`${t('chat.fontSizeSelector', 'Cambiar tamaño de letra')} - ${getFontSizeLabel()}`}
                        type="button"
                    >
                        <span className="font-size-toggle-icon">{getFontSizeIcon()}</span>
                        <span className="font-size-toggle-label">{getFontSizeLabel()}</span>
                    </button>
                </div>
            </div>

            <h2>{t('Lobby.title')}</h2>
            <h3>{t('Lobby.Descripcion')}</h3>
            <div className="lobby-grid">
                {/* Tus elementos FAQ existentes */}
                <div className="FAQ">
                    <Link to="/ConsultasR" className="FAQ-link">
                        <div className="lobby-item uno">
                            <span>{t('Lobby.Preguntas.FAQ1', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">
                            <span>{t('Lobby.Preguntas.FAQ2', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                {/* ... resto de tus elementos FAQ ... */}
                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">
                            <span>{t('Lobby.Preguntas.FAQ3', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ5', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

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

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item dos">
                            <span>{t('Lobby.Preguntas.FAQ8', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item tres">
                            <span>{t('Lobby.Preguntas.FAQ9', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cuatro">
                            <span>{t('Lobby.Preguntas.FAQ10', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

                <div className="FAQ">
                    <Link to="/InA" className="FAQ-link">
                        <div className="lobby-item cinco">
                            <span>{t('Lobby.Preguntas.FAQ11', 'FAQ')}</span>
                        </div>
                    </Link>
                </div>

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