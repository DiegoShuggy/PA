import './ConsultasR.css';

function ConsultasR() {
  console.log('ConsultasR component is rendering'); // ← Agrega esto
  
  return (
    <div className="consultas-r" id="Cuerpo">
      <h2>Consultas Recientes</h2>
      <p className='uno'>Asuntos Estudiantil</p>
      <p className='dos'>Desarrollo Profesional y Titulados</p>
      <p className='tres'>Bienestar Estudiantil</p>
      <p className='cuatro'>Deportes</p>
      <p className='cinco'>Pastoral</p>
    </div>
  );
}

export default ConsultasR;