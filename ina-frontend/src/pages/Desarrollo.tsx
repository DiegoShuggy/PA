import React, { useCallback, useEffect,useRef ,useState} from 'react';
import '../css/Coordinadores.css';
import Profile from '../img/desarrollo2.jpg';
import { useTranslation } from "react-i18next";
import { useNavigate } from 'react-router-dom';

export function Desarrollo() {
    console.log('Desarrollo component is rendering');
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
            console.warn('El lector de texto no es compatible con este navegador');
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
            console.log('🚫 Lectura automática bloqueada por detención manual');
            return;
        }

        if (!speechSynthesisRef.current || !isTtsSupported) {
            alert(t('Asuntos.ttsNotSupported') || 'El lector de texto no es compatible con este navegador.');
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

                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = ttsLang;
                utterance.rate = 0.8;
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
                    console.log(`🔊 Lectura iniciada con voz:`, utterance.voice?.name);
                    // Reiniciar temporizador de inactividad cuando empieza la lectura
                    resetInactivityTimer();
                };

                utterance.onend = () => {
                    console.log('✅ Lectura finalizada');
                    setIsReading(false);
                    currentUtteranceRef.current = null;

                    // Resetear flag de detención manual cuando termina naturalmente
                    if (!isAutoRead) {
                        isManualStopRef.current = false;
                    }
                };

                utterance.onerror = (event) => {
                    console.error('❌ Error en la lectura:', event.error);
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
                console.error('💥 Error al configurar la lectura:', error);
                setIsReading(false);
            }
        }, 50);
    }, [i18n.language, t, isTtsSupported, stopReading]);

    // Función para leer todo el contenido de la página
    const readPageContent = () => {
        // Obtener todo el texto relevante de la página
        const pageTitle = document.querySelector('.tiutlo')?.textContent || '';
        const cargoTitle = document.querySelector('.titulo-extra')?.textContent || '';
        const correo = `Correo electrónico: ${document.querySelector('.correo')?.textContent || ''}`;
        const descripcion = document.querySelector('.desc')?.textContent || '';
        const questions = Array.from(document.querySelectorAll('.Coordinador-item span'))
            .map(span => span.textContent)
            .filter(Boolean)
            .join('. ');

        const fullText = `${pageTitle}. ${cargoTitle}. ${correo}. ${descripcion}. ${questions}`;

        if (!fullText.trim()) {
            console.warn('No hay texto para leer');
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
                title={t('app.backButton')}
            >
                <span className="back-arrow">←</span>
                {t('app.back')}
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
                {/* Contenedor para imagen y título */}
                <div className='imagen-titulo-container'>
                    <img src={Profile} alt="Profile" className="Perfil-imagen2" />
                    <h2 className='tiutlo'>{t('Desarrollo.title')}</h2>
                    {/* Mover el correo aquí */}
                    <p className='correo'>
                        {t('Desarrollo.correo')}
                    </p>
                </div>

                {/* Contenedor para la descripción con título extra */}
                <div className='descripcion-container'>
                    {/* Título extra encima de la descripción */}
                    <h3 className='titulo-extra'>{t('Desarrollo.cargo')}</h3>

                    {/* Descripción */}
                    <p className='desc'>
                        {t('Desarrollo.Descripcion')} <br />
                        <h2 className='tiutlo'>{t('Desarrollo.Desctitle')}</h2>
                        <br />{t('Desarrollo.Descripcion2')}
                        <br />{t('Desarrollo.Descripcion3')}
                        <br />{t('Desarrollo.Descripcion4')}
                        <br />{t('Desarrollo.Descripcion5')}
                        <br />{t('Desarrollo.Descripcion6')}
                    </p>
                </div>
            </div>
            <h2 className='tiutlo'>{t('Bienestar.FAQTiltle')}</h2>
            <div className="Coordinador-grid">
                {/* Asuntos Estudiantiles / Student Affairs / Affaires Estudiantines */}
                <div className="CFAQ">
                    <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ1'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ1')}</span>
                        </div>
                    </div>
                </div>
                    <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ2'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ2')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ3'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ3')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ4'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ4')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ5'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ5')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ6'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ6')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ7'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ7')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ8'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ8')}</span>
                        </div>
                    </div>
                </div>
                <div className="FAQ">
                    <div 
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t('Desarrollo.FAQ9'))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t('Desarrollo.FAQ9')}</span>
                        </div>
                    </div>
                </div>

                </div>
            </div>
        </div>
    )
}
export default Desarrollo;