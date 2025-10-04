import { Link } from 'react-router-dom';
import '../css/ConsultasR.css';
import ina1 from '../css/InA1.png';
import ina2 from '../css/InA2.png';
import ina3 from '../css/InA3.png';
import ina4 from '../css/InA4.png';
import ina5 from '../css/InA5.png';
import ina6 from '../css/InA6.png';
import React, { useRef, useEffect } from 'react';
function ConsultasR() {
    console.log('ConsultasR component is rendering');

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    };

    useEffect(() => {
        scrollToBottom();
    }, []);

    return (
        <div className="consultas-container">
            <h2>Consultas</h2>
            <div className="areas-grid">
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item uno">
                            <img
                                src={ina1}
                                alt="Asuntos Estudiantiles"
                                className="imagen1"
                            />
                            <span>Asuntos Estudiantiles</span>
                        </div>
                    </Link>
                </div>
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item seis">
                            <img
                                src={ina6}
                                alt="Proyectos rigidos"
                                className="imagen6"
                            />
                            <span>Proyectos rigidos</span>
                        </div>
                    </Link>
                </div>
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item dos">
                            <img
                                src={ina2}
                                alt="Desarrollo Profesional y Htulados"
                                className="imagen2"
                            />
                            <span>Desarrollo Profesional y Htulados</span>
                        </div>
                    </Link>
                </div>
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item tres">
                            <img
                                src={ina3}
                                alt="Eisenstar Estudiantli"
                                className="imagen3"
                            />
                            <span>Eisenstar Estudiantli</span>
                        </div>
                    </Link>
                </div>
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item cuatro">
                            <img
                                src={ina4}
                                alt="Properter"
                                className="imagen4"
                            />
                            <span>Reporters</span>
                        </div>
                    </Link>
                </div>
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item cinco">
                            <img
                                src={ina5}
                                alt="Eisenstar"
                                className="imagen5"
                            />
                            <span>Pastoral</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}

export default ConsultasR;