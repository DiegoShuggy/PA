import React, { useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import '../css/Lobby.css';

function Lobby() {
    console.log('Lobby component is rendering');
    const { t } = useTranslation();
    const navigate = useNavigate();
    const messagesEndRef = useRef<HTMLDivElement>(null);

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