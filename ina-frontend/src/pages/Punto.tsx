import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Punto.css';
import ina1 from '../img/asuntos.png';
import ina2 from '../img/faq.png';
import ina3 from '../img/desarrollo.png';
import ina4 from '../img/bienestar.png';
import ina5 from '../img/deportes.png';
import ina6 from '../img/pastoral.png';

function Punto() {
    console.log('Punto component is rendering');
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null);

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
            alert(t('consultas.ttsNotSupported') || 'El lector de texto no es compatible con este navegador.');
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

    // TEXTO ADICIONAL PARA LA LECTURA - Todo incluido en el JavaScript
    const getPageContentWithDescriptions = () => {
        // Texto descriptivo adicional que no está visible en la pantalla
        const pageIntroduction = "Página de Área de Consultas Universitarias. En esta sección podrá acceder a diferentes departamentos y servicios de la institucion academica.";
        
        const navigationInstructions = "Para navegar a cualquier área, haga clic en la tarjeta correspondiente. Cada tarjeta representa un departamento universitario especializado.";
        
        const areasDescriptions = {
            asuntos: "Asuntos Estudiantiles: Departamento encargado de trámites administrativos, certificados, y gestión documental estudiantil.",
            consultasFrecuentes: "Consultas Frecuentes: Respuestas a las preguntas más comunes sobre procesos universitarios y servicios.",
            desarrollo: "Desarrollo Profesional y Titulados: Servicios de orientación laboral, bolsa de trabajo, y seguimiento a graduados.",
            bienestar: "Bienestar Estudiantil: Área dedicada a la salud mental, apoyo psicológico, y bienestar integral del estudiante.",
            deportes: "Deportes: Información sobre actividades deportivas, equipos universitarios, y instalaciones deportivas.",
            pastoral: "Pastoral: Servicios espirituales, actividades de reflexión, y apoyo en valores humanos y cristianos."
        };

        const closingInstructions = "Si desea volver a la página anterior, utilice el botón de retroceso ubicado en la parte superior izquierda de la pantalla.";

        // Combinar todo el contenido
        const fullContent = `
            ${pageIntroduction}
            ${navigationInstructions}
            
            Áreas disponibles:
            
            1. ${areasDescriptions.asuntos}
            
            2. ${areasDescriptions.consultasFrecuentes}
            
            3. ${areasDescriptions.desarrollo}
            
            4. ${areasDescriptions.bienestar}
            
            5. ${areasDescriptions.deportes}
            
            6. ${areasDescriptions.pastoral}
            
            ${closingInstructions}
        `;

        return fullContent;
    };

    // Función para leer todo el contenido de la página con descripciones extendidas
    const readPageContent = () => {
        const pageTitle = ` ${document.querySelector('h2')?.textContent || 'Área de Consultas'}`;
        
        // Obtener los nombres reales de las áreas desde la página
        const areaElements = Array.from(document.querySelectorAll('.consultas-item span'));
        const areaNames = areaElements.map(span => span.textContent).filter(Boolean);
        
        // Crear texto combinado con nombres reales y descripciones adicionales
        const areasWithDescriptions = areaNames.map((name, index) => {
            
            return `Opción ${index + 1}: ${name}.`;
        }).join(' ');

        const fullText = `
            ${pageTitle}.
            
            Bienvenido al área de consultas de la Institucion academica. Esta plataforma le permite acceder a los diferentes servicios y departamentos universitarios.
            
            ${areasWithDescriptions}
            
            Instrucciones de uso: Para seleccionar cualquier área, simplemente haga clic en la tarjeta correspondiente. Si necesita asistencia adicional, utilice el botón de lectura en voz alta para repetir esta información.
            
        `;

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
        <div className="consultas-container">
            {/* Botón para volver atrás */}
            <button
                className="back-button"
                onClick={handleGoBack}
                title={t('app.backButton', 'Volver atrás')}
            >
                <span className="back-arrow">←</span>
                {t('app.back')}
            </button>

            {/* Botón de accesibilidad para leer la página */}
            <div className="accessibility-controls">
                <button 
                    onClick={toggleReading}
                    aria-label={isReading ? t('consultas.stopReading') : t('consultas.readPage')}
                    className={isReading ? 'reading-active' : ''}
                >
                    {isReading ? '⏹️' : '🔊'}
                </button>
            </div>

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

export default Punto;