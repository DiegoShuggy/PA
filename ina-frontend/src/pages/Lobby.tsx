import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';
import audio from '../assets/audio/inaaaaaaa.mp3'
function Lobby() {
    console.log('Lobby component is rendering');
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Estado para controlar qué área está activa
    const [areaActiva, setAreaActiva] = useState('general'); // 'general', 'asuntos', 'desarrollo', 'bienestar', 'deportes', 'pastoral'

    // Estados y refs para el lector de texto
    const [isReading, setIsReading] = useState(false);
    const [isTtsSupported, setIsTtsSupported] = useState(false);
    const speechSynthesisRef = useRef<SpeechSynthesis | null>(null);
    const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
    const isManualStopRef = useRef(false);
    const autoReadEnabledRef = useRef(false); // Nuevo ref para controlar lectura automática

    // Nuevo estado para el contador de clics
    const [clickCount, setClickCount] = useState(0);
    const clickTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Ref para el audio
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Efecto para inicializar el audio
    useEffect(() => {
        audioRef.current = new Audio(audio);
        audioRef.current.volume = 0.7; // Ajusta el volumen si es necesario

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
        };
    }, []);

    // Función para manejar el clic en el título
    const handleTitleClick = () => {
        // Limpiar timeout anterior si existe
        if (clickTimeoutRef.current) {
            clearTimeout(clickTimeoutRef.current);
        }

        // Incrementar contador
        const newCount = clickCount + 1;
        setClickCount(newCount);

        // Si llegó a 5 clics, reproducir sonido y resetear contador
        if (newCount >= 5) {
            playSecretSound();
            setClickCount(0);
        } else {
            // Configurar timeout para resetear el contador después de 2 segundos
            clickTimeoutRef.current = setTimeout(() => {
                setClickCount(0);
            }, 2000);
        }
    };

    // Función para reproducir el sonido secreto
    const playSecretSound = () => {
        if (audioRef.current) {
            audioRef.current.currentTime = 0; // Reiniciar al inicio
            audioRef.current.play().catch(error => {
                console.log('❌ Error al reproducir sonido secreto:', error);
            });
            console.log('🎵 Sonido secreto reproducido');
        }
    };

    // Función para cambiar entre áreas
    const cambiarArea = (area: string) => {
        setAreaActiva(area);
        // Activar lectura automática cuando se cambia de área
        autoReadEnabledRef.current = true;
    };
    const isReturningRef = useRef(false);
    // Función para volver al área general
    const volverAGeneral = () => {
        isReturningRef.current = true;
        setAreaActiva('general');
        autoReadEnabledRef.current = true;
    };

    // INICIO - FUNCIONALIDAD DEL LECTOR DE TEXTO ADAPTADA

    // Función para detener la lectura actual
    const stopReading = useCallback((isManual = false) => {
        if (isManual) {
            isManualStopRef.current = true;
            autoReadEnabledRef.current = false; // Desactivar auto-lectura cuando se detiene manualmente
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
                            console.log(`✅ ${voices.length} (t('app.voiceloaded')`);
                        }
                    } catch (error) {
                        console.error(t('app.errorload'), error);
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

    // Mantener getPageText como estaba anteriormente
    const getPageText = useCallback(() => {
        // Si estamos volviendo a general, no leer título y descripción
        const isReturning = isReturningRef.current;
        isReturningRef.current = false; // Resetear después de usar
        // Obtener título y descripción SOLO para área general
        const pageTitle = (areaActiva === 'general' && !isReturning) ? document.querySelector('h2')?.textContent || '' : '';
        const pageDescription = (areaActiva === 'general' && !isReturning) ? document.querySelector('h3')?.textContent || '' : '';


        // Obtener texto introductorio de áreas SOLO cuando no sea un "volver"
        const areaIntroText = (!isReturning) ? document.querySelector('.sr-only')?.textContent || '' : '';

        // Obtener nombres de las áreas disponibles (botones) - SOLO para área general
        let areaButtons = '';
        if (areaActiva === 'general' && !isReturning) {
            const areaNames = Array.from(document.querySelectorAll('.cambio-item span'))
                .map(span => span.textContent)
                .filter(Boolean);

            // Formatear los nombres de áreas con "y" antes del último elemento
            if (areaNames.length > 0) {
                if (areaNames.length === 1) {
                    areaButtons = areaNames[0];
                } else {
                    const lastArea = areaNames.pop();
                    areaButtons = `${areaNames.join(', ')} ${t('Lobby.areaconnect')} ${lastArea}`;
                }
            }
        }

        // Obtener todas las preguntas del área activa
        const questions = Array.from(document.querySelectorAll('.lobby-item span, .Coordinador-item span'))
            .map(span => span.textContent)
            .filter(Boolean)
            .join('. ');

        // Construir texto completo según el área activa
        let fullText = '';

        if (areaActiva === 'general') {
            if (isReturning) {
                // Texto conciso para cuando se vuelve a general - solo las preguntas
                fullText = `${t('Lobby.VolverText')} ${questions}`;
            } else {
                // Texto completo para primera vez en general
                fullText = `${pageTitle}. ${pageDescription}. ${areaIntroText} ${areaButtons}. ${t('Lobby.FAQareas')} ${questions}`;
            }
        } else {
            // Para áreas específicas - NO incluir título y descripción
            const areaName = getCurrentAreaName();
            let areaIntro = '';

            // Personalizar la introducción según el área
            switch (areaActiva) {
                case 'pastoral':
                    areaIntro = `${t('Lobby.areapas')}`;
                    break;
                default:
                    areaIntro = `${t('Lobby.area')} ${areaName}.`;
            }

            fullText = `${areaIntro} ${t('Lobby.FAQTitle')} ${areaName.toLowerCase()}: ${questions}`;
        }

        return fullText.trim();
    }, [areaActiva]);

    // Función auxiliar para obtener el nombre del área actual
    const getCurrentAreaName = () => {
        switch (areaActiva) {
            case 'asuntos': return t('Lobby.Switch.Asuntos');
            case 'desarrollo': return t('Lobby.Switch.Desarrollo');
            case 'bienestar': return t('Lobby.Switch.Bienestar');
            case 'deportes': return t('Lobby.Switch.Deportes');
            case 'pastoral': return t('Lobby.Switch.Pastoral');
            default: return 'General';
        }
    };

    // Función para leer texto en voz alta
    const readText = useCallback((text: string, isAutoRead = false) => {
        // Si es lectura automática y hubo detención manual, no leer
        if (isAutoRead && isManualStopRef.current) {
            console.log(t('app.manualbloq'));
            return;
        }

        if (!speechSynthesisRef.current || !isTtsSupported) {
            alert(t('Lobby.ttsNotSupported'));
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
                // Reemplazar "/" por espacios antes de crear el utterance
                const processedText = text.replace(/\//g, ' ');
                const utterance = new SpeechSynthesisUtterance(processedText);
                utterance.lang = ttsLang;
                utterance.rate = 0.75;
                utterance.pitch = 1;
                utterance.volume = 1;

                // Seleccionar voz adecuada (código existente de selección de voz)
                const voices = speechSynthesisRef.current?.getVoices() || [];
                let preferredVoice = null;

                const femaleVoiceNames = [
                    'google español', 'español', 'spanish', 'mujer', 'female', 'femenina',
                    'mexico', 'colombia', 'argentina', 'latina', 'españa'
                ];

                const maleVoiceNames = [
                    'raul', 'pablo', 'carlos', 'diego', 'male', 'masculino'
                ];

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

    // Efecto para leer automáticamente cuando cambia el área activa
    useEffect(() => {
        // Pequeño delay para asegurar que el DOM se haya actualizado
        const timer = setTimeout(() => {
            if (autoReadEnabledRef.current && !isManualStopRef.current) {
                const fullText = getPageText();
                if (fullText.trim()) {
                    console.log('🔊 Lectura automática iniciada por cambio de área');
                    readText(fullText, true);
                }
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [areaActiva, getPageText, readText]);
    // Función para leer todo el contenido de la página
    // Función para leer todo el contenido de la página
    const readPageContent = useCallback(() => {
        const fullText = getPageText();

        if (!fullText.trim()) {
            console.warn(t('app.readEmpty'));
            return;
        }

        readText(fullText, false);
    }, [getPageText, readText]);

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
        navigate('/InA', {
            state: {
                predefinedQuestion: questionText,
                autoSend: true
            }
        });
    };

    // Renderizar contenido según el área activa
    const renderizarContenido = () => {
        switch (areaActiva) {
            case 'asuntos':
                return renderAsuntosEstudiantiles();
            case 'desarrollo':
                return renderDesarrolloProfesional();
            case 'bienestar':
                return renderBienestarEstudiantil();
            case 'deportes':
                return renderDeportes();
            case 'pastoral':
                return renderPastoral();
            default:
                return renderFAQGeneral();
        }
    };

    // Renderizar FAQ general (contenido original)
    const renderFAQGeneral = () => (
        <div className="lobby-grid">
            <div className="FAQ">
                <Link to="/Punto" className="FAQ-link">
                    <div className="lobby-item siete">
                        <span>{t('Lobby.Preguntas.FAQ1')}</span>
                    </div>
                </Link>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ2'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Lobby.Preguntas.FAQ2')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ3'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Lobby.Preguntas.FAQ3')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Asuntos.FAQ4'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Asuntos.FAQ4')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Asuntos.FAQ5'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Asuntos.FAQ5')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Asuntos.FAQ6'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Asuntos.FAQ6')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Asuntos.FAQ7'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Asuntos.FAQ7')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Asuntos.FAQ8'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Asuntos.FAQ8')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Desarrollo.FAQ9'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Desarrollo.FAQ9')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Desarrollo.FAQ10'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Desarrollo.FAQ3')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Desarrollo.FAQ11'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Desarrollo.FAQ1')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Desarrollo.FAQ12'))}
                >
                    <div className="lobby-item siete">
                        <span>{t('Desarrollo.FAQ2')}</span>
                    </div>
                </div>
            </div>
        </div>
    );

    // Renderizar Asuntos Estudiantiles
    const renderAsuntosEstudiantiles = () => (
        <div className="lobby-grid">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
                <div className="FAQ" key={num}>
                    <div
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t(`Asuntos.FAQ${num}`))}
                    >
                        <div className="Coordinador-item uno">
                            <span>{t(`Asuntos.FAQ${num}`)}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    // Renderizar Desarrollo Profesional
    const renderDesarrolloProfesional = () => (
        <div className="lobby-grid">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
                <div className="FAQ" key={num}>
                    <div
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t(`Desarrollo.FAQ${num}`))}
                    >
                        <div className="Coordinador-item tres">
                            <span>{t(`Desarrollo.FAQ${num}`)}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    // Renderizar Bienestar Estudiantil
    const renderBienestarEstudiantil = () => (
        <div className="lobby-grid">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((num) => (
                <div className="FAQ" key={num}>
                    <div
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t(`Bienestar.FAQ${num}`))}
                    >
                        <div className="Coordinador-item cuatro">
                            <span>{t(`Bienestar.FAQ${num}`)}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    // Renderizar Deportes
    const renderDeportes = () => (
        <div className="lobby-grid">
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
    );

    // Renderizar Pastoral
    const renderPastoral = () => (
        <div className="lobby-grid">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13].map((num) => (
                <div className="FAQ" key={num}>
                    <div
                        className="FAQ-link"
                        onClick={() => handleQuestionClick(t(`Pastoral.FAQ${num}`))}
                    >
                        <div className="Coordinador-item cinco">
                            <span>{t(`Pastoral.FAQ${num}`)}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <div className="lobby-container">
            {/* Título con detector de clics */}
            <h2
                onClick={handleTitleClick}
            >
                {t('Lobby.title')}
            </h2>
            <h3>{t('Lobby.Descripcion')}</h3>

            {/* Botón de accesibilidad */}
            <div className="accessibility-controls">
                <button
                    onClick={toggleReading}
                    aria-label={isReading ? t('Lobby.stopReading') : t('Lobby.readPage')}
                    className={isReading ? 'reading-active' : ''}
                >
                    {isReading ? '⏹️' : '🔊'}
                </button>
            </div>

            {/* Texto introductorio para áreas - SOLO en área general */}
            {areaActiva === 'general' && (
                <div className="sr-only">
                    <p>{t('Lobby.FAQDesc')}</p>
                </div>
            )}

            {/* Botones de cambio de área */}
            <div className="FAQ-horizontal">
                <div className="cambio">
                    <div
                        className={`cambio-link ${areaActiva === 'asuntos' ? 'active' : ''}`}
                        onClick={() => cambiarArea('asuntos')}
                    >
                        <div className="cambio-item cambio-color">
                            <span>{t('Lobby.Switch.Asuntos')}</span>
                        </div>
                    </div>
                </div>
                <div className="cambio">
                    <div
                        className={`cambio-link ${areaActiva === 'desarrollo' ? 'active' : ''}`}
                        onClick={() => cambiarArea('desarrollo')}
                    >
                        <div className="cambio-item cambio-color">
                            <span>{t('Lobby.Switch.Desarrollo')}</span>
                        </div>
                    </div>
                </div>
                <div className="cambio">
                    <div
                        className={`cambio-link ${areaActiva === 'bienestar' ? 'active' : ''}`}
                        onClick={() => cambiarArea('bienestar')}
                    >
                        <div className="cambio-item cambio-color">
                            <span>{t('Lobby.Switch.Bienestar')}</span>
                        </div>
                    </div>
                </div>
                <div className="cambio">
                    <div
                        className={`cambio-link ${areaActiva === 'deportes' ? 'active' : ''}`}
                        onClick={() => cambiarArea('deportes')}
                    >
                        <div className="cambio-item cambio-color">
                            <span>{t('Lobby.Switch.Deportes')}</span>
                        </div>
                    </div>
                </div>
                <div className="cambio">
                    <div
                        className={`cambio-link ${areaActiva === 'pastoral' ? 'active' : ''}`}
                        onClick={() => cambiarArea('pastoral')}
                    >
                        <div className="cambio-item cambio-color">
                            <span>{t('Lobby.Switch.Pastoral')}</span>
                        </div>
                    </div>
                </div>
            </div>
            {/* Botón para volver al área general */}
            {areaActiva !== 'general' && (
                <div className="back-button">
                    <button onClick={volverAGeneral} className="btn-volver">
                        ← {t('Lobby.VolverGeneral')}
                    </button>
                </div>
            )}


            {/* Contenido dinámico según el área activa */}
            {renderizarContenido()}



            <div ref={messagesEndRef} />
        </div>
    );
}

export default Lobby;