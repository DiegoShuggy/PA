import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../css/NavBar.css"
import { useTranslation } from "react-i18next";
import logo from '../img/puntoestudiantil.png';
// Agregar import de VoiceSearch
import VoiceSearch from '../components/VoiceSearch';

function NavBar() {
    const { t } = useTranslation();
    const [clickCount, setClickCount] = useState(0);
    const [showModal, setShowModal] = useState(false);
    const [password, setPassword] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Contraseña fija
    const fixedPassword = "hola";

    // Referencia para el temporizador
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Función para salir del modo pantalla completa
    const exitFullscreen = () => {
        try {
            const doc = document as any;
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (doc.mozCancelFullScreen) { // Firefox
                doc.mozCancelFullScreen();
            } else if (doc.webkitExitFullscreen) { // Chrome, Safari
                doc.webkitExitFullscreen();
            } else if (doc.msExitFullscreen) { // IE/Edge
                doc.msExitFullscreen();
            }
            console.log('Saliendo del modo pantalla completa');
        } catch (error) {
            console.warn('Error al salir de pantalla completa:', error);
        }
    };

    // Función que recibe la pregunta desde el componente VoiceSearch
    const handleQuestionFromVoice = (questionText: string) => {
        console.log('Búsqueda por voz desde NavBar:', questionText);
        // Redirigir al chat con la consulta de voz
        navigate('/InA', {
            state: {
                predefinedQuestion: questionText,
                autoSend: true
            }
        });
    };

    // Función para manejar el clic secreto en el logo
    const handleSecretClick = () => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }
        const newCount = clickCount + 1;
        setClickCount(newCount);

        // Si llega a 5 clics, mostrar el modal
        if (newCount >= 5) {
            setShowModal(true);
            setClickCount(0);
        } else {
            // Configurar temporizador para resetear el contador después de 2 segundos
            timerRef.current = setTimeout(() => {
                setClickCount(0);
            }, 2000);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (password === fixedPassword) {
            setIsAuthenticated(true);
            setError('');
            setShowModal(false);
            
            // Salir del modo pantalla completa antes de redirigir
            exitFullscreen();
            
            // Pequeño delay para asegurar que salió de pantalla completa antes de redirigir
            setTimeout(() => {
                navigate("/Reporte");
            }, 300);
        } else {
            setError(t('navbar.error.incorrectPassword'));
            setPassword('');
        }
    };

    const closeModal = () => {
        setShowModal(false);
        setPassword('');
        setError('');
    };

    return (
        <>
            <nav className="navbar">
                <div className="navbar-menu_container">
                    <div className="navbar-brand">
                        <div className="logo-container">
                            <img 
                                src={logo} 
                                alt="Logo" 
                                className="navbar-logo" 
                                onClick={handleSecretClick} 
                            />
                        </div>
                    </div>

                    <header className="app-header">
                        
                        <h1>{t('navbar.InA')}</h1>
                    </header>

                    {/* Agregar la sección de búsqueda por voz aquí */}
                    <div className="navbar-voice-search">
                        <VoiceSearch 
                            onQuestionSelect={handleQuestionFromVoice}
                            onVoiceTranscript={(transcript) => console.log('Transcripción:', transcript)}
                        />
                    </div>

                    <div className="navbar-links">
                        <Link to="/">{t('navbar.Lobby')}</Link>
                        <Link to="/InA">{t('navbar.Chat')}</Link>
                        <Link to="/Punto">{t('navbar.Punto')}</Link>
                        <Link to="/Reporte">{t('navbar.Reporte')}</Link>
                    </div>
                </div>
            </nav>

            {/* Modal de autenticación */}
            {showModal && (
                <div className="modal-overlay">
                    <div className="modal-content">

                        <div className="modal-title">
                            <div className="Acceso">
                                <h2>{t('navbar.secretAccess')}</h2>
                            </div>

                            <form onSubmit={handleSubmit}>
                                <div className="secret">
                                    <label htmlFor="password">
                                        {t('navbar.secretPassword')}:
                                    </label>
                                    <input
                                        type="password"
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="contra"
                                        placeholder={t('navbar.passwordPlaceholder')}
                                        required
                                        autoFocus
                                    />
                                </div>

                                {error && (
                                    <div className="error">
                                        {error}
                                    </div>
                                )}

                                <div className="flex gap-2">
                                    <button
                                        type="button"
                                        onClick={closeModal}
                                        className="cancelar"
                                    >
                                        {t('navbar.cancel')}
                                    </button>
                                    <button
                                        type="submit"
                                        className="cancelar"
                                    >
                                        {t('navbar.access')}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default NavBar;