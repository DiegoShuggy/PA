import React, { useState, useRef } from 'react';
import '../css/Reporte.css';
import { useTranslation } from "react-i18next";
import { useNavigate } from 'react-router-dom';
import ina from '../img/InA6.png';
// Importa tu archivo MP4 - ajusta la ruta según donde lo coloques
import videoEffect from '../assets/videos/wah.mp4'; // Ajusta esta ruta

const Reporte = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    
    // Estados para el sistema de reportes
    const [selectedPeriod, setSelectedPeriod] = useState<number>(1);
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [isSendingEmail, setIsSendingEmail] = useState<boolean>(false);
    const [reportData, setReportData] = useState<any>(null);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [showEmailForm, setShowEmailForm] = useState<boolean>(false);
    
    // Estados para el contador de clics y el video
    const [clickCount, setClickCount] = useState<number>(0);
    const [showVideo, setShowVideo] = useState<boolean>(false);
    const videoRef = useRef<HTMLVideoElement | null>(null);

    // Opciones de período
    const periodOptions = [
        { value: 1, label: '1 Día' },
        { value: 7, label: '1 Semana' },
        { value: 14, label: '2 Semanas' },
        { value: 21, label: '3 Semanas' },
        { value: 30, label: '1 Mes' }
    ];

    // Función para manejar el clic en la imagen
    const handleImageClick = () => {
        const newCount = clickCount + 1;
        setClickCount(newCount);
        
        console.log(`Clic número: ${newCount}`); // Para debugging
        
        // Si llega a 5 clics, mostrar video y resetear contador
        if (newCount === 5) {
            playVideo();
            setClickCount(0);
            
            // Opcional: Mostrar mensaje de éxito
            setSuccess('🎉 ¡Easter egg activado! Video reproducido.');
            
            // Limpiar mensaje después de 3 segundos
            setTimeout(() => {
                setSuccess('');
            }, 3000);
        }
        
        // Resetear contador después de 2 segundos si no se completan los 5 clics
        if (newCount === 1) {
            setTimeout(() => {
                if (clickCount + 1 === newCount) { // Verificar que no haya más clics
                    setClickCount(0);
                    console.log('Contador reseteado por tiempo'); // Para debugging
                }
            }, 2000);
        }
    };

    // Función para reproducir el video
    const playVideo = () => {
        setShowVideo(true);
        
        // Reproducir el video después de un pequeño delay para asegurar que se montó
        setTimeout(() => {
            if (videoRef.current) {
                videoRef.current.currentTime = 0; // Reiniciar el video
                videoRef.current.play().catch(error => {
                    console.error('Error reproduciendo video:', error);
                });
            }
        }, 100);
    };

    // Función para cerrar el video
    const closeVideo = () => {
        if (videoRef.current) {
            videoRef.current.pause();
            videoRef.current.currentTime = 0;
        }
        setShowVideo(false);
    };

    // Función cuando el video termina
    const handleVideoEnd = () => {
        setShowVideo(false);
    };

    // Función para generar reporte
    const generateReport = async () => {
        setIsGenerating(true);
        setError('');
        setSuccess('');
        
        try {
            const response = await fetch('http://localhost:8000/reports/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    period_days: selectedPeriod,
                    include_pdf: true
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                setReportData(data.data);
                setSuccess(`✅ Reporte generado exitosamente para ${selectedPeriod} días`);
                
                // Mostrar información del PDF generado
                if (data.pdf) {
                    setSuccess(prev => prev + `\n📄 PDF: ${data.pdf.filename}`);
                }
                
            } else {
                setError('❌ Error generando el reporte');
            }
        } catch (err) {
            setError('❌ Error de conexión con el servidor');
            console.error('Error:', err);
        } finally {
            setIsGenerating(false);
        }
    };

    // Función para enviar reporte por email
    const sendReportByEmail = async () => {
        if (!email) {
            setError('❌ Por favor ingresa un correo electrónico');
            return;
        }

        // Validación básica de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('❌ Por favor ingresa un correo electrónico válido');
            return;
        }

        setIsSendingEmail(true);
        setError('');
        
        try {
            const response = await fetch('http://localhost:8000/reports/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    period_days: selectedPeriod,
                    report_type: "basic"
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                setSuccess(`✅ Reporte enviado exitosamente a: ${email}`);
                setShowEmailForm(false);
                setEmail('');
            } else {
                // Mostrar mensaje de error más específico
                const errorMessage = data.message || 'Error desconocido';
                if (errorMessage.includes('SMTP') || errorMessage.includes('configuración')) {
                    setError('❌ Error de configuración del servidor de correo. Contacta al administrador.');
                } else {
                    setError(`❌ Error enviando email: ${errorMessage}`);
                }
            }
        } catch (err) {
            setError('❌ Error de conexión con el servidor');
            console.error('Error:', err);
        } finally {
            setIsSendingEmail(false);
        }
    };

    // Función para volver
    const handleGoBack = () => {
        navigate(-1);
    };

    return (
        <div className="reporte-container">
            {/* Modal de video */}
            {showVideo && (
                <div className="video-modal-overlay" onClick={closeVideo}>
                    <div className="video-modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="video-close-button" onClick={closeVideo}>
                            ×
                        </button>
                        <video
                            ref={videoRef}
                            controls
                            autoPlay
                            onEnded={handleVideoEnd}
                            className="easter-egg-video"
                        >
                            <source src={videoEffect} type="video/mp4" />
                            Tu navegador no soporta el elemento de video.
                        </video>
                        <p className="video-caption">🎉 ¡Easter egg desbloqueado!</p>
                    </div>
                </div>
            )}

            {/* Header con botones de navegación */}
            <div className="reporte-header">
                <button className="back-button" onClick={handleGoBack}>
                    <span className="back-arrow">←</span>
                    {t('app.back')}
                </button>
                
                <div className="navbar-brand">
                    <img 
                        src={ina} 
                        alt="Logo InA" 
                        className="navbar-logo"
                        onClick={handleImageClick}
                        style={{ cursor: 'pointer' }}
                        title="Haz clic 5 veces para un easter egg"
                    />
                </div>
            </div>

            {/* Contenido principal */}
            <div className="reporte-content">
                <h1 className="reporte-title">📊 Generar Reporte de Consultas</h1>
                <p className="reporte-subtitle">
                    Selecciona el período para generar un reporte detallado de las consultas realizadas
                </p>

                {/* Selector de período */}
                <div className="period-selector">
                    <label htmlFor="period-select" className="period-label">
                        Período del Reporte:
                    </label>
                    <select
                        id="period-select"
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(Number(e.target.value))}
                        className="period-select"
                    >
                        {periodOptions.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Botones de acción */}
                <div className="action-buttons">
                    <button
                        onClick={generateReport}
                        disabled={isGenerating}
                        className={`generate-button ${isGenerating ? 'generating' : ''}`}
                    >
                        {isGenerating ? '🔄 Generando...' : '📄 Generar Reporte PDF'}
                    </button>

                    <button
                        onClick={() => setShowEmailForm(!showEmailForm)}
                        className="email-toggle-button"
                    >
                        📧 {showEmailForm ? 'Cancelar Envío' : 'Enviar por Email'}
                    </button>
                </div>

                {/* Formulario de email */}
                {showEmailForm && (
                    <div className="email-form">
                        <h3>📨 Enviar Reporte por Correo</h3>
                        <div className="email-input-group">
                            <input
                                type="email"
                                placeholder="Ingresa tu correo electrónico"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="email-input"
                                disabled={isSendingEmail}
                            />
                            <button
                                onClick={sendReportByEmail}
                                disabled={isSendingEmail || !email}
                                className="send-email-button"
                            >
                                {isSendingEmail ? '📤 Enviando...' : '📤 Enviar Reporte'}
                            </button>
                        </div>
                        <p className="email-note">
                            El reporte se enviará como PDF adjunto al correo especificado.
                        </p>
                    </div>
                )}

                {/* Mensajes de estado */}
                {error && (
                    <div className="message error-message">
                        {error}
                    </div>
                )}
                
                {success && (
                    <div className="message success-message">
                        {success.split('\n').map((line, index) => (
                            <div key={index}>{line}</div>
                        ))}
                    </div>
                )}

                {/* Vista previa del reporte */}
                {reportData && (
                    <div className="report-preview">
                        <h3>📋 Vista Previa del Reporte</h3>
                        
                        <div className="preview-grid">
                            <div className="preview-card">
                                <h4>📈 Métricas Principales</h4>
                                <p><strong>Total Consultas:</strong> {reportData.summary_metrics?.total_consultas || 0}</p>
                                <p><strong>Consultas sin Respuesta:</strong> {reportData.summary_metrics?.consultas_sin_respuesta || 0}</p>
                                <p><strong>Tasa de Respuesta:</strong> {reportData.summary_metrics?.tasa_respuesta?.toFixed(1) || 0}%</p>
                                <p><strong>Tasa de Satisfacción:</strong> {reportData.summary_metrics?.tasa_satisfaccion?.toFixed(1) || 0}%</p>
                            </div>
                            
                            <div className="preview-card">
                                <h4>🎯 Feedback</h4>
                                <p><strong>Respuestas Evaluadas:</strong> {reportData.feedback_detallado?.respuestas_evaluadas || 0}</p>
                                <p><strong>Feedback Positivo:</strong> {reportData.feedback_detallado?.feedback_positivo || 0}</p>
                                <p><strong>Feedback Negativo:</strong> {reportData.feedback_detallado?.feedback_negativo || 0}</p>
                                <p><strong>Rating Promedio:</strong> {reportData.feedback_detallado?.rating_promedio?.toFixed(1) || 0}/5</p>
                            </div>
                        </div>

                        {/* Categorías populares */}
                        {reportData.categorias_populares && Object.keys(reportData.categorias_populares).length > 0 && (
                            <div className="preview-card full-width">
                                <h4>📊 Categorías Más Consultadas</h4>
                                <div className="categories-list">
                                    {Object.entries(reportData.categorias_populares)
                                        .slice(0, 5)
                                        .map(([category, count]) => (
                                            <div key={category} className="category-item">
                                                <span className="category-name">{category}</span>
                                                <span className="category-count">{count as number} consultas</span>
                                            </div>
                                        ))
                                    }
                                </div>
                            </div>
                        )}

                        {/* Información del período */}
                        <div className="preview-card full-width">
                            <h4>📅 Información del Período</h4>
                            <p><strong>Período analizado:</strong> {selectedPeriod} día{selectedPeriod !== 1 ? 's' : ''}</p>
                            <p><strong>Fecha de inicio:</strong> {new Date(reportData.report_metadata?.period_range?.start).toLocaleDateString()}</p>
                            <p><strong>Fecha de fin:</strong> {new Date(reportData.report_metadata?.period_range?.end).toLocaleDateString()}</p>
                            <p><strong>Generado el:</strong> {new Date(reportData.report_metadata?.generated_at).toLocaleString()}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reporte;