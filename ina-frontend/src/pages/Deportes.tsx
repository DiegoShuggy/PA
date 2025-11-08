import React, { useEffect, useRef, useState, useCallback } from 'react';
import '../css/Coordinadores.css';
import Profile from '../img/DeportesJefe.jpg';
import Profile2 from '../img/DeportesCAF.jpg';
import { useTranslation } from "react-i18next";
import { useNavigate } from 'react-router-dom';

export function Deportes() {
    console.log('Deportes component is rendering');
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();

    // Estados y refs para el lector de texto
    const [isReading, setIsReading] = useState(false);
    const [isTtsSupported, setIsTtsSupported] = useState(false);
    const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);
    const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
    const isManualStopRef = useRef(false);

    // Estado y refs para el temporizador de inactividad
    const [inactivityTime, setInactivityTime] = useState(0);
    const inactivityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const inactivityCounterRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const INACTIVITY_TIMEOUT = 300000; // 5 minutos

    // INICIO - FUNCIONALIDAD DEL LECTOR DE TEXTO ADAPTADA

    // Función para detener la lectura actual
    const stopReading = useCallback((isManual = false) => {
        if (isManual) {
            isManualStopRef.current = true;
        }

        if (speechSynthesisRef.current) {
            speechSynthesisRef.current.cancel();
            currentUtteranceRef.current = null;
            setIsReading(false);
        }
    }, []);

    // Verificar soporte del lector de texto
    useEffect(() => {
        if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
            speechSynthesisRef.current = window.speechSynthesis;
            setIsTtsSupported(true);

            // Función para cargar voces
            const loadVoices = () => {
                if (speechSynthesisRef.current) {
                    try {
                        const voices = speechSynthesisRef.current.getVoices();
                        if (voices.length > 0) {
                            console.log(`✅ ${voices.length} voces cargadas`);
                        }
                    } catch (error) {
                        console.error('Error cargando voces:', error);
                    }
                }
            };

            speechSynthesisRef.current.onvoiceschanged = loadVoices;
            loadVoices();

        } else {
            setIsTtsSupported(false);
            console.warn(t('app.noncompatible'));
        }

        // Cleanup al desmontar el componente
        return () => {
            stopReading();
        };
    }, [stopReading]);

    // Función para leer texto en voz alta
    const readText = useCallback((text: string, isAutoRead = false) => {
        // Si es lectura automática y hubo detención manual, no leer
        if (isAutoRead && isManualStopRef.current) {
            console.log(t('app.ttsNotSupported'));
            return;
        }

        if (!speechSynthesisRef.current || !isTtsSupported) {
            alert(t('app.ttsNotSupported') || 'El lector de texto no es compatible con este navegador.');
            return;
        }

        // Resetear el flag de detención manual si es lectura manual
        if (!isAutoRead) {
            isManualStopRef.current = false;
        }

        // Detener cualquier lectura en curso
        stopReading();

        // Pequeña pausa antes de empezar nueva lectura
        setTimeout(() => {
            try {
                // Configurar idioma
                const ttsLang = i18n.language === 'es' ? 'es-ES' :
                    i18n.language === 'fr' ? 'fr-FR' : 'en-US';
                const processedText = text.replace(/\//g, ' ');
                const utterance = new SpeechSynthesisUtterance(processedText);
                utterance.lang = ttsLang;
                utterance.rate = 0.75;
                utterance.pitch = 1.2;
                utterance.volume = 1;

                // Seleccionar voz adecuada
                const voices = speechSynthesisRef.current?.getVoices() || [];
                let preferredVoice = null;

                // Buscar voces femeninas
                const femaleVoiceNames = [
                    'google español', 'español', 'spanish', 'mujer', 'female', 'femenina',
                    'mexico', 'colombia', 'argentina', 'latina', 'españa'
                ];

                const maleVoiceNames = [
                    'raul', 'pablo', 'carlos', 'diego', 'male', 'masculino'
                ];

                // Buscar voz femenina del idioma correcto
                for (let voice of voices) {
                    const voiceName = voice.name.toLowerCase();
                    const voiceLang = voice.lang.toLowerCase();

                    if (!voiceLang.startsWith(ttsLang.substring(0, 2))) continue;

                    const isFemale = femaleVoiceNames.some(femaleName =>
                        voiceName.includes(femaleName.toLowerCase())
                    );

                    const isMale = maleVoiceNames.some(maleName =>
                        voiceName.includes(maleName.toLowerCase())
                    );

                    if (isFemale && !isMale) {
                        preferredVoice = voice;
                        break;
                    }
                }

                // Si no encuentra voz femenina, usar cualquier voz no masculina
                if (!preferredVoice) {
                    for (let voice of voices) {
                        const voiceName = voice.name.toLowerCase();
                        const voiceLang = voice.lang.toLowerCase();

                        if (!voiceLang.startsWith(ttsLang.substring(0, 2))) continue;

                        const isMale = maleVoiceNames.some(maleName =>
                            voiceName.includes(maleName.toLowerCase())
                        );

                        if (!isMale) {
                            preferredVoice = voice;
                            break;
                        }
                    }
                }

                // Si todavía no hay voz, usar la primera disponible del idioma
                if (!preferredVoice) {
                    preferredVoice = voices.find(voice =>
                        voice.lang.startsWith(ttsLang.substring(0, 2))
                    );
                }

                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }

                utterance.onstart = () => {
                    setIsReading(true);
                    console.log(t('app.readStart'), utterance.voice?.name);
                    // Reiniciar temporizador de inactividad cuando empieza la lectura
                    resetInactivityTimer();
                };

                utterance.onend = () => {
                    console.log(t('app.readFinished'));
                    setIsReading(false);
                    currentUtteranceRef.current = null;

                    // Resetear flag de detención manual cuando termina naturalmente
                    if (!isAutoRead) {
                        isManualStopRef.current = false;
                    }
                };

                utterance.onerror = (event) => {
                    console.error(t('app.readError'), event.error);
                    setIsReading(false);
                    currentUtteranceRef.current = null;

                    // Resetear flag de detención manual en caso de error
                    if (!isAutoRead) {
                        isManualStopRef.current = false;
                    }
                };

                currentUtteranceRef.current = utterance;

                // Pequeño delay antes de empezar
                setTimeout(() => {
                    if (speechSynthesisRef.current && currentUtteranceRef.current === utterance) {
                        speechSynthesisRef.current.speak(utterance);
                    }
                }, 100);

            } catch (error) {
                console.error(t('app.readEmpty'), error);
                setIsReading(false);
            }
        }, 50);
    }, [i18n.language, t, isTtsSupported, stopReading]);

    // Función para leer todo el contenido de la página
    const readPageContent = () => {
        // Obtener todo el texto relevante de la página
        const pageTitle = `${t('Asuntos.coordinad@')} ${document.querySelector('.titulo')?.textContent || ''}`;
        const pageTitle2 = `${t('Asuntos.coordinad@')}  ${document.querySelector('.titulo2')?.textContent || ''}`;
        const AreaTitle = `${t('Asuntos.area')}  ${document.querySelector('.titulo-extra')?.textContent || ''}`;

        // Usar los elementos ocultos para pronunciación
        const correoPronunciacion = `${t('Asuntos.correoE')} ${document.querySelector('.sr-only:nth-of-type(1)')?.textContent || ''}`;
        const correo2Pronunciacion = `${t('Asuntos.correoE')} ${document.querySelector('.sr-only:nth-of-type(2)')?.textContent || ''}`;

        const descripcion = document.querySelector('.desc')?.textContent || '';
        const questions = Array.from(document.querySelectorAll('.Coordinador-item span'))
            .map(span => span.textContent)
            .filter(Boolean)
            .join('. ');

        const fullText = `${AreaTitle}. ${pageTitle}. ${correoPronunciacion}.  ${pageTitle2}.  ${correo2Pronunciacion}. ${descripcion}. ${questions}`;

        if (!fullText.trim()) {
            console.warn(t('app.readEmpty'));
            return;
        }

        readText(fullText, false);
    };

    // Función para alternar lectura
    const toggleReading = () => {
        if (isReading) {
            stopReading(true);
        } else {
            readPageContent();
        }
    };

    // FIN - FUNCIONALIDAD DEL LECTOR DE TEXTO

    // Función para manejar el clic en las preguntas
    const handleQuestionClick = (questionText: string) => {
        // Detener lectura si está activa
        if (isReading) {
            stopReading(true);
        }

        // Navegar al chat
        navigate('/InA', {
            state: {
                predefinedQuestion: questionText,
                autoSend: true
            }
        });
    };

    // FUNCIONALIDAD DEL TEMPORIZADOR DE INACTIVIDAD

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
            // Detener lectura antes de redirigir
            stopReading(true);
            navigate('/'); // Redirige a la página principal
        }, INACTIVITY_TIMEOUT);

        // Opcional: Contador para debug (puedes remover esto en producción)
        inactivityCounterRef.current = setInterval(() => {
            setInactivityTime(prev => prev + 1000);
        }, 1000);
    }, [navigate, stopReading]);

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

            // Detener lectura al desmontar
            stopReading();
        };
    }, [handleActivity, resetInactivityTimer, stopReading]);

    // Efecto opcional para mostrar el tiempo de inactividad en consola (debug)
    useEffect(() => {
        if (inactivityTime > 0 && inactivityTime % 5000 === 0) {
            console.log(`Tiempo de inactividad: ${inactivityTime / 1000} segundos`);
        }
    }, [inactivityTime]);

    // Función para volver a la página anterior
    const handleGoBack = useCallback(() => {
        // Detener lectura antes de navegar
        stopReading(true);
        navigate(-1);
    }, [navigate, stopReading]);

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
                title={t('app.backButton', 'Volver atrás')}
            >
                <span className="back-arrow">←</span>
                {t('Deportes.back', 'Volver')}
            </button>
            {/* Botón de accesibilidad para leer la página */}
            <div className="accessibility-controls">
                <button
                    onClick={toggleReading}
                    aria-label={isReading ? t('Asuntos.stopReading') : t('Asuntos.readPage')}
                    className={isReading ? 'reading-active' : ''}
                >
                    {isReading ? '⏹️' : '🔊'}
                </button>
            </div>
            <div className='Perfil-container'>
                {/* Contenedor para imagen, título y correo */}
                <div className='imagen-titulo-container'>
                    {/* Primer perfil */}
                    <img src={Profile} alt="Profile" className="Perfil-imagen4" />
                    <h2 className='titulo'>{t('Deportes.title')}</h2>
                    <p className='correo'>
                        {t('Deportes.correo')}
                    </p>
                    {/* Elemento oculto para pronunciación */}
                    <span className="sr-only">{t('Deportes.correo_pronunciacion')}</span>

                    {/* Segundo perfil */}
                    <img src={Profile2} alt="Profile" className="Perfil-imagen4" />
                    <h2 className='titulo2'>{t('Deportes.title2')}</h2>
                    <p className='correo2'>
                        {t('Deportes.correo2')}
                    </p>
                    {/* Elemento oculto para pronunciación */}
                    <span className="sr-only">{t('Deportes.correo2_pronunciacion')}</span>
                </div>

                {/* Contenedor para la descripción con título extra */}
                <div className='descripcion-container'>
                    {/* Título extra encima de la descripción */}
                    <h3 className='titulo-extra'>{t('Deportes.cargo')}</h3>

                    {/* Descripción */}
                    <p className='desc'>
                        {t('Deportes.Descripcion')} <br />
                        <h2 className='titulo'>{t('Deportes.Desctitle')}</h2>
                        <br />{t('Deportes.principales')}
                        <br />{t('Deportes.Descripcion2')}
                        <br />{t('Deportes.Descripcion3')}
                        <br />{t('Deportes.Descripcion4')}
                        <br />{t('Deportes.Descripcion5')}
                        <br />{t('Deportes.Competencias')}
                        <br />{t('Deportes.Descripcion6')}
                        <br />{t('Deportes.Descripcion7')}
                        <br />{t('Deportes.Descripcion8')}
                    </p>
                </div>
            </div>
            <h2 className='titulo'>{t('Deportes.FAQTiltle')}</h2>
            <div className="Coordinador-grid">
                <div className="CFAQ">
                    {/* Renderizar preguntas dinámicamente */}
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13].map((num) => (
                        <div className="FAQ" key={num}>
                            <div
                                className="FAQ-link"
                                onClick={() => handleQuestionClick(t(`Deportes.FAQ${num}`))}
                            >
                                <div className="Coordinador-item cinco">
                                    <span>{t(`Deportes.FAQ${num}`)}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
export default Deportes;