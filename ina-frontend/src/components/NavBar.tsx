import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../css/NavBar.css"
import logo from '../img/pto.png';


function NavBar() {
    const [clickCount, setClickCount] = useState(0);
    const [showModal, setShowModal] = useState(false);
    const [password, setPassword] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Contraseña fija
    const fixedPassword = "hola";

    // Función para manejar el clic secreto en el logo
    const handleSecretClick = () => {
        const newCount = clickCount + 1;
        setClickCount(newCount);

        // Si llega a 5 clics, mostrar el modal
        if (newCount >= 5) {
            setShowModal(true);
            setClickCount(0);
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
            setError('Contraseña incorrecta');
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
                    <div className="navbar-brand" onClick={handleSecretClick}>
                        <img src={logo} alt="Logo" className="navbar-logo" />
                    </div>

                    <header className="app-header">
                        <p>Powered by Mistral 7B</p>
                        <h1>InA - Asistente Virtual Duoc UC</h1>
                    </header>

                    <div className="navbar-links">
                        <Link to="/">Lobby</Link>
                        <Link to="/InA">Chat</Link>
                        <Link to="/ConsultasR">Punto Estudiantil</Link>
                        <Link to="/Reporte">Reporte</Link>
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
                                <h2>Acceso Secreto</h2>
                            </div>

                            <form onSubmit={handleSubmit}>
                                <div className="secret">
                                    <label htmlFor="password">
                                        Contraseña Secreta:
                                    </label>
                                    <input
                                        type="password"
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="contra"
                                        placeholder="Ingresa la contraseña secreta"
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
                                        Cancelar
                                    </button>
                                    <button
                                        type="submit"
                                        className="cancelar"
                                    >
                                        Acceder
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