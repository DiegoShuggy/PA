import React, { useEffect, useRef, useState, useCallback } from 'react';
import '../css/Coordinadores.css';
import Profile from '../img/Asuntoscoord.jpg';
import { useTranslation } from "react-i18next";
import { useNavigate } from 'react-router-dom';

export function Asuntos() {
    console.log('Asuntos component is rendering');
    const { t } = useTranslation();
    const navigate = useNavigate();

    // Estado y refs para el temporizador de inactividad
    const [inactivityTime, setInactivityTime] = useState(0);
    const inactivityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const inactivityCounterRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    // Configuración del temporizador de inactividad (en milisegundos)
    const INACTIVITY_TIMEOUT = 300000; // 5 minutos

    // Función para manejar el clic en las preguntas y enviar automáticamente
    const handleQuestionClick = (questionText: string) => {
        // Navegar al chat y pasar la pregunta como estado con un flag de autoSend
        navigate('/InA', {
            state: {
                predefinedQuestion: questionText,
                autoSend: true // Flag para indicar envío automático
            }
        });
    };
    // Función para reiniciar el temporizador de inactividad
    const resetInactivityTimer = useCallback(() => {
        setInactivityTime(0);

        // Limpiar temporizadores existentes
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
        }
        if (inactivityCounterRef.current) {
            clearInterval(inactivityCounterRef.current);
        }

        // Crear nuevo temporizador
        inactivityTimerRef.current = setTimeout(() => {
            console.log('Tiempo de inactividad agotado - redirigiendo...');
            navigate('/'); // Redirige a la página principal
        }, INACTIVITY_TIMEOUT);

        // Opcional: Contador para debug (puedes remover esto en producción)
        inactivityCounterRef.current = setInterval(() => {
            setInactivityTime(prev => prev + 1000);
        }, 1000);
    }, [navigate]);

    // Función para manejar eventos de actividad
    const handleActivity = useCallback(() => {
        resetInactivityTimer();
    }, [resetInactivityTimer]);

    // Efecto para inicializar los detectores de actividad
    useEffect(() => {
        // Lista de eventos que indican actividad del usuario
        const events = [
            'mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart',
            'click', 'input', 'focus'
        ];

        // Agregar event listeners
        events.forEach(event => {
            document.addEventListener(event, handleActivity, true);
        });

        // Iniciar el temporizador por primera vez
        resetInactivityTimer();

        // Cleanup: remover event listeners y limpiar temporizadores
        return () => {
            events.forEach(event => {
                document.removeEventListener(event, handleActivity, true);
            });

            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
            }
            if (inactivityCounterRef.current) {
                clearInterval(inactivityCounterRef.current);
            }
        };
    }, [handleActivity, resetInactivityTimer]);

    // Efecto opcional para mostrar el tiempo de inactividad en consola (debug)
    useEffect(() => {
        if (inactivityTime > 0 && inactivityTime % 5000 === 0) {
            console.log(`Tiempo de inactividad: ${inactivityTime / 1000} segundos`);
        }
    }, [inactivityTime]);

    // Función para volver a la página anterior
    const handleGoBack = useCallback(() => {
        navigate(-1); // -1 significa ir a la página anterior en el historial
    }, [navigate]);

    // Scroll to top when component mounts
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    return (
        <div className="Asuntos-container">
            {/* Botón para volver atrás */}
            <button
                className="back-button"
                onClick={handleGoBack}
                title={t('app.backButton')}
            >
                <span className="back-arrow">←</span>
                {t('app.back')}
            </button>
            <div className='Perfil-container'>
                {/* Contenedor para imagen, título y correo */}
                <div className='imagen-titulo-container'>
                    <img src={Profile} alt="Profile" className="Perfil-imagen" />
                    <h2 className='tiutlo'>{t('Asuntos.title')}</h2>
                    {/* Mover el correo aquí */}
                    <p className='correo'>
                        {t('Asuntos.correo')}
                    </p>
                </div>

                {/* Contenedor para la descripción con título extra */}
                <div className='descripcion-container'>
                    {/* Título extra encima de la descripción */}
                    <h3 className='titulo-extra'>{t('Asuntos.cargo')}</h3>

                    {/* Descripción */}
                    <p className='desc'>
                        {t('Asuntos.Descripcion')}
                        {t('Asuntos.Descripcion2')}<br />
                        {t('Asuntos.Descripcion3')}<br />
                    </p>
                </div>
            </div>
            <div className="Coordinador-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="CFAQ">
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ1'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ1')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ2'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ2')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ3'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ3')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ4'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ4')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ5'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ5')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ6'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ6')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ7'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ7')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ8'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ8')}</span>
                            </div>
                        </div>
                    </div>
                    <div className="FAQ">
                        <div
                            className="FAQ-link"
                            onClick={() => handleQuestionClick(t('Asuntos.FAQ9'))}
                        >
                            <div className="Coordinador-item uno">
                                <span>{t('Asuntos.FAQ9')}</span>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}
export default Asuntos;