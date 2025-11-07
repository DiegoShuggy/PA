import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import VoiceSearch from '../components/VoiceSearch';
import '../css/Lobby.css';

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

    // Efecto para el sonido al cargar/refrescar la página
    useEffect(() => {
        const playRefreshSound = async () => {
            try {
                const refreshSound = new Audio('/sounds/kronii-gwakk.mp3');
                refreshSound.volume = 0.3;
                await refreshSound.play();
                console.log('🔊 Sonido de refresh reproducido');
            } catch (error) {
                console.log('❌ No se pudo reproducir el sonido:', error);
            }
        };
        playRefreshSound();
        return () => {
            const audioElements = document.querySelectorAll('audio');
            audioElements.forEach(audio => {
                audio.pause();
                audio.currentTime = 0;
            });
        };
    }, []);

    // Función para cambiar entre áreas
    const cambiarArea = (area: string) => {
        setAreaActiva(area);
        // Reproducir sonido al cambiar de área
        const playAreaChangeSound = async () => {
            try {
                const changeSound = new Audio('/sounds/kronii-gwakk.mp3');
                changeSound.volume = 0.2;
                await changeSound.play();
                console.log('🔊 Sonido de cambio de área reproducido');
            } catch (error) {
                console.log('❌ No se pudo reproducir el sonido de cambio de área:', error);
            }
        };
        playAreaChangeSound();
    };

    // Función para volver al área general
    const volverAGeneral = () => {
        setAreaActiva('general');
    };

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

    // Función para manejar búsquedas por voz (opcional)
    const handleVoiceSearch = (query: string) => {
        console.log('Búsqueda por voz:', query);
        // Puedes agregar lógica adicional aquí si necesitas
    };

    // Función para leer texto en voz alta
    const readText = useCallback((text: string, isAutoRead = false) => {
        // Si es lectura automática y hubo detención manual, no leer
        if (isAutoRead && isManualStopRef.current) {
            console.log('🚫 Lectura automática bloqueada por detención manual');
            return;
        }

        if (!speechSynthesisRef.current || !isTtsSupported) {
            alert(t('Lobby.ttsNotSupported') || 'El lector de texto no es compatible con este navegador.');
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
        const pageTitle = document.querySelector('h2')?.textContent || '';
        const pageDescription = document.querySelector('h3')?.textContent || '';
        const questions = Array.from(document.querySelectorAll('.lobby-item span'))
            .map(span => span.textContent)
            .filter(Boolean)
            .join('. ');

        const fullText = `${pageTitle}. ${pageDescription}. ${questions}`;

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
                    <div className="lobby-item uno">
                        <span>{t('Lobby.Preguntas.FAQ1')}</span>
                    </div>
                </Link>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ2'))}
                >
                    <div className="lobby-item dos">
                        <span>{t('Lobby.Preguntas.FAQ2')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ3'))}
                >
                    <div className="lobby-item tres">
                        <span>{t('Lobby.Preguntas.FAQ3')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ4'))}
                >
                    <div className="lobby-item cuatro">
                        <span>{t('Lobby.Preguntas.FAQ4')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ5'))}
                >
                    <div className="lobby-item cinco">
                        <span>{t('Lobby.Preguntas.FAQ5')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ6'))}
                >
                    <div className="lobby-item seis">
                        <span>{t('Lobby.Preguntas.FAQ6')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ7'))}
                >
                    <div className="lobby-item uno">
                        <span>{t('Lobby.Preguntas.FAQ7')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ8'))}
                >
                    <div className="lobby-item dos">
                        <span>{t('Lobby.Preguntas.FAQ8')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ9'))}
                >
                    <div className="lobby-item tres">
                        <span>{t('Lobby.Preguntas.FAQ9')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ10'))}
                >
                    <div className="lobby-item cuatro">
                        <span>{t('Lobby.Preguntas.FAQ10')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ11'))}
                >
                    <div className="lobby-item cinco">
                        <span>{t('Lobby.Preguntas.FAQ11')}</span>
                    </div>
                </div>
            </div>

            <div className="FAQ">
                <div
                    className="FAQ-link"
                    onClick={() => handleQuestionClick(t('Lobby.Preguntas.FAQ12'))}
                >
                    <div className="lobby-item seis">
                        <span>{t('Lobby.Preguntas.FAQ12')}</span>
                    </div>
                </div>
            </div>
        </div>
    );

    // Renderizar Asuntos Estudiantiles
    const renderAsuntosEstudiantiles = () => (
        <div className="lobby-grid">
            {/* Renderizar preguntas dinámicamente */}
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
            {/* Renderizar preguntas dinámicamente */}
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
            {/* Renderizar preguntas dinámicamente */}
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
    );

    // Renderizar Pastoral
    const renderPastoral = () => (
        <div className="lobby-grid">
            {/* Renderizar preguntas dinámicamente */}
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
            <h2>{t('Lobby.title')}</h2>
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

            {/* Buscador por voz (solo en área general) */}
            {areaActiva === 'general' && (
                <div className="voice-search-section">
                    <h4>{t('Lobby.voicetitle')}</h4>
                    <VoiceSearch onSearch={handleVoiceSearch} />
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}

export default Lobby;