import './ConsultasR.css';

function ConsultasR() {
  console.log('ConsultasR component is rendering'); // ← Agrega esto
  
  return (
    <div className="consultas-r" >
      <h2>Áreas de consultas</h2>
      <p className='uno'>Asuntos Estudiantil</p>
      <p className='dos'>Desarrollo Profesional y Titulados</p>
      <p className='tres'>Bienestar Estudiantil</p>
      <p className='cuatro'>Deportes</p>
      <p className='cinco'>Pastoral</p>
    </div>
  );
}

export default ConsultasR;