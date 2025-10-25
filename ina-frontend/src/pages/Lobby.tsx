import React, { useRef, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';

function Lobby() {
    console.log('Lobby component is rendering');
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [speech, setSpeech] = useState<SpeechSynthesisUtterance | null>(null);
    const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);

    // Obtener las voces disponibles y configurar según el idioma
    useEffect(() => {
        const loadVoices = () => {
            const voices = window.speechSynthesis.getVoices();
            setAvailableVoices(voices);
            configureSpeechForLanguage(voices, i18n.language);
        };

        // Cargar voces cuando estén disponibles
        if ('speechSynthesis' in window) {
            // Las voces se cargan asíncronamente, así que necesitamos esperar
            if (speechSynthesis.getVoices().length > 0) {
                loadVoices();
            } else {
                speechSynthesis.addEventListener('voiceschanged', loadVoices);
            }

            const utterance = new SpeechSynthesisUtterance();
            setSpeech(utterance);

            return () => {
                speechSynthesis.removeEventListener('voiceschanged', loadVoices);
                speechSynthesis.cancel();
            };
        } else {
            console.warn('Tu navegador no soporta la Web Speech API');
        }
    }, [i18n.language]);

    // Configurar la voz según el idioma actual
    const configureSpeechForLanguage = (voices: SpeechSynthesisVoice[], language: string) => {
        if (!speech) return;

        // Mapeo de idiomas a códigos de voz
        const languageMap: { [key: string]: string } = {
            'es': 'es-ES',
            'en': 'en-US',
            'fr': 'fr-FR'
        };

        const targetLang = languageMap[language] || language;
        
        // Buscar una voz que coincida con el idioma
        const preferredVoice = voices.find(voice => 
            voice.lang.includes(targetLang)
        );

        // Si no encuentra una voz exacta, buscar una voz similar
        const fallbackVoice = voices.find(voice => 
            voice.lang.startsWith(language)
        );

        const selectedVoice = preferredVoice || fallbackVoice;

        if (selectedVoice) {
            speech.voice = selectedVoice;
            speech.lang = selectedVoice.lang;
            console.log(`Voz seleccionada: ${selectedVoice.name} para idioma: ${language}`);
        } else {
            console.warn(`No se encontró voz para el idioma: ${language}`);
            // Usar la voz por defecto del navegador
            speech.lang = targetLang;
        }

        // Configurar propiedades del speech
        speech.rate = 0.9;
        speech.pitch = 1;
        speech.volume = 1;
    };

    // Actualizar la configuración cuando cambia el idioma
    useEffect(() => {
        if (speech && availableVoices.length > 0) {
            configureSpeechForLanguage(availableVoices, i18n.language);
        }
    }, [i18n.language, speech, availableVoices]);

    // Función para leer todo el contenido de la página
    const readPageContent = () => {
        if (!speech) {
            console.error('Speech no está inicializado');
            return;
        }

        // Cancelar cualquier speech en curso
        speechSynthesis.cancel();

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

        // Configurar y ejecutar el speech
        speech.text = fullText;
        
        speech.onstart = () => {
            setIsSpeaking(true);
            console.log('Iniciando lectura con idioma:', speech.lang);
        };
        
        speech.onend = () => {
            setIsSpeaking(false);
            console.log('Lectura finalizada');
        };
        
        speech.onerror = (event) => {
            setIsSpeaking(false);
            console.error('Error en speech synthesis:', event);
        };

        try {
            speechSynthesis.speak(speech);
        } catch (error) {
            console.error('Error al iniciar speech synthesis:', error);
            setIsSpeaking(false);
        }
    };

    // Función para detener la lectura
    const stopReading = () => {
        speechSynthesis.cancel();
        setIsSpeaking(false);
    };


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

    return (
        <div className="lobby-container">
            {/* Botón de accesibilidad para leer la página */}
            <div className="accessibility-controls" style={{
                position: 'fixed',
                top: '20px',
                right: '20px',
                zIndex: 1000
            }}>
                <button 
                    onClick={isSpeaking ? stopReading : readPageContent}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: isSpeaking ? '#ff4444' : '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        fontSize: '16px'
                    }}
                    aria-label={isSpeaking ? t('Lobby.stopReading') : t('Lobby.readPage')}
                >
                    {isSpeaking ? '⏹️' : '🔊'}
                </button>
            </div>
            <h2>{t('Lobby.title')}</h2>
            <h3>{t('Lobby.Descripcion')}</h3>
            <div className="lobby-grid">
                {/* Tus elementos FAQ existentes - Modificados para usar onClick */}
                <div className="FAQ">
                    <Link to="/ConsultasR" className="FAQ-link">
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
            <div ref={messagesEndRef} />
        </div>
    );
}

export default Lobby;