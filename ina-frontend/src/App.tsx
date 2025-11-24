import React, { useState, useRef, useEffect } from 'react';
import Chat from './pages/Chat';
import Punto from './pages/Punto';
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
import ojoAbierto from './img/ojo-abierto.png';
import ojoCerrado from './img/ojo-cerrado.png';

function App() {
    const { i18n, t } = useTranslation();
    const [isHovering, setIsHovering] = useState(false);
    const [fontSize, setFontSize] = useState<'small' | 'normal' | 'large'>('normal');
    const [lineHeight, setLineHeight] = useState<'normal' | 'large' | 'x-large'>('normal');
    const [textSpacing, setTextSpacing] = useState<'normal' | 'large' | 'x-large'>('normal');
    const [highContrast, setHighContrast] = useState(false);
    const [grayscale, setGrayscale] = useState(false);
    const [dyslexicFont, setDyslexicFont] = useState(false);
    const [showAccessibilityMenu, setShowAccessibilityMenu] = useState(false);
    const [readingGuide, setReadingGuide] = useState(false);
    const [readingPosition, setReadingPosition] = useState(0);
    const [isDragging, setIsDragging] = useState(false);
    const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
    const [isCursorInViewport, setIsCursorInViewport] = useState(true);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const guideLineRef = useRef<HTMLDivElement>(null);
    const menuRef = useRef<HTMLDivElement>(null);
    const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
    const languageMenuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const enterFullscreen = async () => {
            try {
                const docElement = document.documentElement as any;
            
            if (document.fullscreenElement) return;

            if (docElement.requestFullscreen) {
                await docElement.requestFullscreen();
            } else if (docElement.mozRequestFullScreen) {
                await docElement.mozRequestFullScreen();
            } else if (docElement.webkitRequestFullscreen) {
                await docElement.webkitRequestFullscreen();
            } else if (docElement.msRequestFullscreen) {
                await docElement.msRequestFullscreen();
            }
                console.log('Pantalla completa activada automáticamente');
            } catch (error) {
                console.warn('No se pudo activar la pantalla completa automáticamente:', error);
            }
        };

        const timer = setTimeout(() => {
            enterFullscreen();
        }, 500);

        enterFullscreen();


        // O agregar un botón para activar pantalla completa
        const handleFullscreen = () => {
            enterFullscreen();
        };

        // Ejemplo: agregar evento a un botón específico
        const fullscreenButton = document.getElementById('fullscreen-btn');
        if (fullscreenButton) {
            fullscreenButton.addEventListener('click', handleFullscreen);
        }

        // Activar después de que la página se haya cargado completamente
        const handleLoad = () => {
            setTimeout(enterFullscreen, 500); // 1 segundo después de la carga
        };
        if (document.readyState === 'complete') {
            setTimeout(enterFullscreen, 500);
        } else {
            window.addEventListener('load', handleLoad);
        }
        return () => {
            window.removeEventListener('load', handleLoad);
            clearTimeout(timer);
            if (fullscreenButton) {
                fullscreenButton.removeEventListener('click', handleFullscreen);
            }
        };

    }, []);
    // Handle click outside accessibility menu
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (showAccessibilityMenu &&
                menuRef.current &&
                !menuRef.current.contains(event.target as Node) &&
                !(event.target as Element).closest('.accessibility-toggle')) {
                setShowAccessibilityMenu(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showAccessibilityMenu]);

    // Aplicar los estilos de accesibilidad (actualizado para incluir temas)
    useEffect(() => {
        const root = document.documentElement;

        // Aplicar tamaño de fuente
        root.classList.remove('font-small', 'font-normal', 'font-large');
        root.classList.add(`font-${fontSize}`);

        // Aplicar altura de línea
        root.classList.remove('line-height-normal', 'line-height-large', 'line-height-x-large');
        root.classList.add(`line-height-${lineHeight}`);

        // Aplicar espaciado de texto
        root.classList.remove('text-spacing-normal', 'text-spacing-large', 'text-spacing-x-large');
        root.classList.add(`text-spacing-${textSpacing}`);

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

        // Aplicar fuente para disléxicos
        if (dyslexicFont) {
            root.classList.add('dyslexic-font');
        } else {
            root.classList.remove('dyslexic-font');
        }

        // Aplicar seguidor de cursor
        if (readingGuide) {
            root.classList.add('reading-guide-active');
        } else {
            root.classList.remove('reading-guide-active');
        }

    }, [fontSize, lineHeight, highContrast, grayscale, dyslexicFont, textSpacing, readingGuide]);

    // Efecto para el seguidor de cursor
    useEffect(() => {
        if (!readingGuide) return;

        const handleMouseMove = (e: MouseEvent) => {
            setCursorPosition({ x: e.clientX, y: e.clientY });
            setIsCursorInViewport(true);

            if (!isDragging) {
                setReadingPosition(e.clientY);
            }
        };

        const handleMouseLeave = () => {
            setIsCursorInViewport(false);
        };

        const handleMouseEnter = () => {
            setIsCursorInViewport(true);
        };

        const handleMouseDown = (e: MouseEvent) => {
            if (guideLineRef.current?.contains(e.target as Node)) {
                setIsDragging(true);
            }
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        const handleDrag = (e: MouseEvent) => {
            if (isDragging) {
                setReadingPosition(e.clientY);
                setCursorPosition({ x: e.clientX, y: e.clientY });
            }
        };

        const handleTouchMove = (e: TouchEvent) => {
            if (e.touches.length > 0) {
                const touch = e.touches[0];
                setCursorPosition({ x: touch.clientX, y: touch.clientY });
                if (!isDragging) {
                    setReadingPosition(touch.clientY);
                }
            }
        };

        const handleTouchStart = (e: TouchEvent) => {
            if (guideLineRef.current?.contains(e.target as Node)) {
                setIsDragging(true);
                if (e.touches.length > 0) {
                    const touch = e.touches[0];
                    setCursorPosition({ x: touch.clientX, y: touch.clientY });
                }
            }
        };

        const handleTouchEnd = () => {
            setIsDragging(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseleave', handleMouseLeave);
        document.addEventListener('mouseenter', handleMouseEnter);
        document.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mousemove', handleDrag);
        document.addEventListener('touchmove', handleTouchMove);
        document.addEventListener('touchstart', handleTouchStart);
        document.addEventListener('touchend', handleTouchEnd);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseleave', handleMouseLeave);
            document.removeEventListener('mouseenter', handleMouseEnter);
            document.removeEventListener('mousedown', handleMouseDown);
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('touchmove', handleTouchMove);
            document.removeEventListener('touchstart', handleTouchStart);
            document.removeEventListener('touchend', handleTouchEnd);
        };
    }, [readingGuide, isDragging]);

    // Resetear todas las opciones de accesibilidad (actualizado)
    const resetAccessibility = () => {
        setFontSize('normal');
        setLineHeight('normal');
        setTextSpacing('normal');
        setHighContrast(false);
        setGrayscale(false);
        setDyslexicFont(false);
        setReadingGuide(false);
    };

    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
        setIsLanguageMenuOpen(false);
    };

    return (
        <div className="app">
            <div>
                <NavBar />

                {/* Botón flotante de accesibilidad */}
                <div className="accessibility-floating-button">
                    <button
                        className="accessibility-toggle"
                        onClick={() => setShowAccessibilityMenu(!showAccessibilityMenu)}
                        onMouseEnter={() => setIsHovering(true)}
                        onMouseLeave={() => setIsHovering(false)}
                        title={t('accessibility.menu', 'Menú de accesibilidad')}
                        type="button"
                        aria-expanded={showAccessibilityMenu}
                    >
                        <img
                            src={isHovering || showAccessibilityMenu ? ojoCerrado : ojoAbierto}
                            alt="Menú de accesibilidad"
                            className="accessibility-icon-img"
                        />
                    </button>

                    {/* Menú desplegable de accesibilidad - ACTUALIZADO CON TEMAS */}
                    {showAccessibilityMenu && (
                        <div className="accessibility-menu" ref={menuRef}>
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

                                {/* Espaciado de texto */}
                                <div className="accessibility-option">
                                    <label>{t('Accesibilidad.espaciado')}</label>
                                    <div className="text-spacing-buttons">
                                        <button
                                            className={`text-spacing-btn ${textSpacing === 'normal' ? 'active' : ''}`}
                                            onClick={() => setTextSpacing('normal')}
                                        >
                                            Aa
                                        </button>
                                        <button
                                            className={`text-spacing-btn ${textSpacing === 'large' ? 'active' : ''}`}
                                            onClick={() => setTextSpacing('large')}
                                            title="Espaciado amplio"
                                        >
                                            A a
                                        </button>
                                        <button
                                            className={`text-spacing-btn ${textSpacing === 'x-large' ? 'active' : ''}`}
                                            onClick={() => setTextSpacing('x-large')}
                                        >
                                            A  a
                                        </button>
                                    </div>
                                </div>

                                {/* Seguidor de curso */}
                                <div className="accessibility-option">
                                    <label className="toggle-label">
                                        <input
                                            type="checkbox"
                                            checked={readingGuide}
                                            onChange={(e) => setReadingGuide(e.target.checked)}
                                        />
                                        <span className="toggle-slider"></span>
                                        {t('Accesibilidad.tracker')}
                                    </label>
                                </div>

                                {/* Fuente para Dyslexia */}
                                <div className="accessibility-option">
                                    <label className="toggle-label">
                                        <input
                                            type="checkbox"
                                            checked={dyslexicFont}
                                            onChange={(e) => setDyslexicFont(e.target.checked)}
                                        />
                                        <span className="toggle-slider"></span>
                                        {t('Accesibilidad.dyslexia')}
                                    </label>
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
                <button
                    id="fullscreen-btn"
                    className="fullscreen-button"
                    onClick={() => {
                        const docElement = document.documentElement;
                        if (docElement.requestFullscreen) {
                            docElement.requestFullscreen();
                        }
                    }}
                >
                    ⛶
                </button>
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

                {/* Seguidor de cursor */}
                {readingGuide && (
                    <div
                        className="reading-guide-line"
                        ref={guideLineRef}
                        style={{ top: `${readingPosition}px` }}
                    >
                        <div
                            className="guide-handle"
                            style={{
                                left: `${cursorPosition.x}px`,
                                opacity: isCursorInViewport ? 1 : 0
                            }}
                        >
                        </div>
                    </div>
                )}

                <main className='main-content'>
                    <Routes>
                        <Route path="/" element={<Lobby />} />
                        <Route path="/InA" element={<Chat />} />
                        <Route path="/Punto" element={<Punto />} />
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