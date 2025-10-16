import React, { useEffect } from 'react';
import '../css/Coordinadores.css';
import Profile from '../img/InA4.png';
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from 'react-router-dom';

export function Desarrollo() {
    console.log('Desarrollo component is rendering');
    const { t } = useTranslation();
    const navigate = useNavigate();


    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);


    // Función para volver a la página anterior
    const handleGoBack = () => {
        navigate(-1); // -1 significa ir a la página anterior en el historial
    };

    return (
        <div className="Asuntos-container">
            {/* Botón para volver atrás */}
            <button
                className="back-button"
                onClick={handleGoBack}
                title={t('app.backButton', 'Volver atrás')}
            >
                <span className="back-arrow">←</span>
                {t('Desarrollo.back', 'Volver')}
            </button>
            <div className='Perfil-container'>
                {/* Contenedor para imagen y título */}
                <div className='imagen-titulo-container'>
                    <img src={Profile} alt="Profile" className="Perfil-imagen2" />
                    <h2 className='tiutlo'>{t('Desarrollo.title')}</h2>
                </div>

                {/* Contenedor para la descripción con título extra */}
                <div className='descripcion-container'>
                    {/* Título extra encima de la descripción */}
                    <h3 className='titulo-extra'>{t('Desarrollo.cargo')}</h3>

                    {/* Descripción */}
                    <p className='desc'>
                        {t('Desarrollo.Descripcion')} <br />
                        <br />{t('Desarrollo.Descripcion2')}
                        <br />{t('Desarrollo.Descripcion3')}
                    </p>
                </div>
            </div>
            <div className="Coordinador-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="CFAQ">
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>
                    <Link to="/InA" className="CFAQ-link">
                        <div className="Coordinador-item tres">
                            <span>{t('Lobby.Preguntas.FAQ4', 'FAQ')}</span>
                        </div>
                    </Link>

                </div>
            </div>
        </div>
    )
}
export default Desarrollo;