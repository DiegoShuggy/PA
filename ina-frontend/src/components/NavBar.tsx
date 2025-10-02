import { Link } from "react-router-dom";
import "./NavBar.css"
function NavBar() {
    return <nav className="navbar">
        <div className="navbar-menu_container">
            <div className="navbar-links">
                <Link to="/">ConsultasR</Link>
                <Link to="/InA">Chat</Link>
            </div>
        </div>
    </nav>
}
export default NavBar