import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../css/NavBar.css"
import { useTranslation } from "react-i18next";
import logo from '../img/pto.png';

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
            // Redirigir a la página Reporte
            navigate("/Reporte");
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
                    {/* Logo con funcionalidad secreta */}
                    <div className="navbar-brand">
                        <img src={logo} alt="Logo" className="navbar-logo" onClick={handleSecretClick} />
                    </div>

                    <header className="app-header">
                        <p>{t('navbar.poweredBy')}</p>
                        <h1>{t('navbar.InA')}</h1>
                    </header>

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
                        {/* Grid de imágenes de fondo */}
                        <div className="modal-background-grid">
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                            <div className="grid-image"></div>
                        </div>

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