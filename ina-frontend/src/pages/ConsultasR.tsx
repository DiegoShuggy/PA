import React, { useRef, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/ConsultasR.css';
import ina1 from '../img/asuntos.png';
import ina2 from '../img/faq.png';
import ina3 from '../img/desarrollo.png';
import ina4 from '../img/bienestar.png';
import ina5 from '../img/deportes.png';
import ina6 from '../img/pastoral.png';


function ConsultasR() {
    console.log('ConsultasR component is rendering');
    const { t } = useTranslation();
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    // Función para volver a la página anterior
    const handleGoBack = () => {
        navigate(-1); // -1 significa ir a la página anterior en el historial
    };

    // Scroll to top when component mounts
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);


    return (
        <div className="consultas-container">
            {/* Botón para volver atrás */}
            <button
                className="back-button"
                onClick={handleGoBack}
                title={t('app.backButton', 'Volver atrás')}
            >
                <span className="back-arrow">←</span>
                {t('Asuntos.back', 'Volver')}
            </button>

            <h2>{t('consultas.title', 'Área de Consultas')}</h2>

            <div className="areas-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="area">
                    <Link to="/Asuntos" className="area-link">
                        <div className="consultas-item uno">
                            <img
                                src={ina1}
                                alt={t('consultas.areas.bienestar.alt', 'Asuntos Estudiantiles')}
                                className="imagen1"
                            />
                            <span>{t('consultas.areas.bienestar.title', 'Asuntos Estudiantiles')}</span>
                        </div>
                    </Link>
                </div>

                {/* Consultas Frecuentes / Frequent Queries / Questions Fréquentes */}
                <div className="area">
                    <Link to="/InA" className="area-link">
                        <div className="consultas-item dos">
                            <img
                                src={ina2}
                                alt={t('consultas.areas.ConsultasFrecuentes.alt', 'Consultas Frecuentes')}
                                className="imagen2"
                            />
                            <span>{t('consultas.areas.ConsultasFrecuentes.title', 'Consultas Frecuentes')}</span>
                        </div>
                    </Link>
                </div>

                {/* Desarrollo Profesional y Titulados / Professional Development and Graduates / Développement Professionnel et Diplômés */}
                <div className="area">
                    <Link to="/Desarrollo" className="area-link">
                        <div className="consultas-item tres">
                            <img
                                src={ina3}
                                alt={t('consultas.areas.professionalDevelopment.alt', 'Desarrollo Profesional y Titulados')}
                                className="imagen3"
                            />
                            <span>{t('consultas.areas.professionalDevelopment.title', 'Desarrollo Profesional y Titulados')}</span>
                        </div>
                    </Link>
                </div>

                {/* Bienestar Estudiantil / Student Selfcare / Bien-être Estudiantin */}
                <div className="area">
                    <Link to="/Bienestar" className="area-link">
                        <div className="consultas-item cuatro">
                            <img
                                src={ina4}
                                alt={t('consultas.areas.studentWelfare.alt', 'Bienestar Estudiantil')}
                                className="imagen4"
                            />
                            <span>{t('consultas.areas.studentWelfare.title', 'Bienestar Estudiantil')}</span>
                        </div>
                    </Link>
                </div>

                {/* Deportes / Sports / Sports */}
                <div className="area">
                    <Link to="/Deportes" className="area-link">
                        <div className="consultas-item cinco">
                            <img
                                src={ina5}
                                alt={t('consultas.areas.sports.alt', 'Deportes')}
                                className="imagen5"
                            />
                            <span>{t('consultas.areas.sports.title', 'Deportes')}</span>
                        </div>
                    </Link>
                </div>

                {/* Pastoral / Pastoral / Pastorale */}
                <div className="area">
                    <Link to="/Pastoral" className="area-link">
                        <div className="consultas-item seis">
                            <img
                                src={ina6}
                                alt={t('consultas.areas.pastoral.alt', 'Pastoral')}
                                className="imagen6"
                            />
                            <span>{t('consultas.areas.pastoral.title', 'Pastoral')}</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div ref={messagesEndRef} />
        </div>
    );
}

export default ConsultasR;