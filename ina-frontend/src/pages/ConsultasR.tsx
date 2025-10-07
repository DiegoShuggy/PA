import { Link } from 'react-router-dom';
import '../css/ConsultasR.css';

function ConsultasR() {
  console.log('ConsultasR component is rendering'); // ← Agrega esto

  return (
    <div className="consultas-r" >
      <h2>Áreas de consultas</h2>
      <div className="area">
        <Link to="/InA">
          <p className='uno'>Asuntos Estudiantiles</p>
          </Link>
      </div>
      <div className="area">
        <Link to="/InA">
          <p className='dos'>Desarrollo Profesional y Titulados</p>
        </Link>
      </div>
      <div className="area">
        <Link to="/InA">
          <p className='tres'>Bienestar Estudiantil</p>
        </Link>
      </div>
      <div className="area">
        <Link to="/InA">
          <p className='cuatro'>Deportes</p>
        </Link>
      </div>
      <div className="area">
        <Link to="/InA">
          <p className='cinco'>Pastoral</p>
        </Link>
      </div>
    </div>
  );
}


export default ConsultasR;