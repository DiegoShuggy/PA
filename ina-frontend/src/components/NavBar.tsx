import { Link } from "react-router-dom";
import "../css/NavBar.css"
import logo from '../css/pto.png';
function NavBar() {
    return <nav className="navbar">
        <div className="navbar-menu_container">
            {/* Añade esta línea para la imagen */}
            <Link to="/" className="FAQ-link">
            <div className="navbar-brand">
                <img src={logo} alt="Logo" className="navbar-logo" />
            </div>
            </Link>

            <header className="app-header">
                <p>Powered by Mistral 7B</p>
                <h1>InA - Asistente Virtual Duoc UC</h1>
            </header>

            <div className="navbar-links">
                <Link to="/">Lobby</Link>
                <Link to="/InA">Chat</Link>
                <Link to="/Punto">ConsultasR</Link>
                <Link to="/Asuntos"> Asuntos </Link>
            </div>
        </div>
    </nav>
}

export default NavBar