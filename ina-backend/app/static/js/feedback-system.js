// static/js/feedback-system.js
class InaFeedbackSystem {
    constructor() {
        this.currentSessionId = null;
        this.feedbackSubmitted = false;
        this.widgetElement = null;
        this.initialize();
    }
    
    initialize() {
        // Crear elemento del widget si no existe
        this.createFeedbackWidget();
        this.bindGlobalEvents();
    }
    
    createFeedbackWidget() {
        // El widget se crea dinámicamente para no depender del HTML
        if (document.getElementById('ina-feedback-widget')) {
            this.widgetElement = document.getElementById('ina-feedback-widget');
            return;
        }
        
        const widget = document.createElement('div');
        widget.id = 'ina-feedback-widget';
        widget.className = 'feedback-widget';
        widget.style.display = 'none';
        
        widget.innerHTML = `
            <div class="feedback-prompt">
                <p>¿Te resultó útil esta respuesta de Ina?</p>
                <div class="feedback-buttons">
                    <button class="feedback-btn positive" data-action="satisfied">
                        👍 Sí, cumplió con lo que necesitaba
                    </button>
                    <button class="feedback-btn negative" data-action="unsatisfied">
                        👎 No, podría mejorar
                    </button>
                </div>
            </div>
            <div class="feedback-followup" style="display: none;">
                <h4>¡Gracias por ayudarnos a mejorar!</h4>
                <p>¿Podrías contarnos más sobre cómo podemos mejorar?</p>
                
                <div class="rating-section">
                    <p>Califica esta respuesta (opcional):</p>
                    <div class="star-rating">
                        <span class="star" data-rating="1">★</span>
                        <span class="star" data-rating="2">★</span>
                        <span class="star" data-rating="3">★</span>
                        <span class="star" data-rating="4">★</span>
                        <span class="star" data-rating="5">★</span>
                    </div>
                </div>
                
                <textarea placeholder="Ej: La respuesta fue muy técnica, necesitaba más detalles prácticos..." rows="3"></textarea>
                
                <div class="feedback-actions">
                    <button class="submit-btn">Enviar comentarios</button>
                    <button class="cancel-btn">Cancelar</button>
                </div>
            </div>
            <div class="feedback-thankyou" style="display: none;">
                <p>✅ ¡Gracias por tu feedback! Tu opinión ayuda a mejorar a Ina.</p>
            </div>
        `;
        
        document.body.appendChild(widget);
        this.widgetElement = widget;
        this.bindWidgetEvents();
    }
    
    bindWidgetEvents() {
        // Botones principales de feedback
        this.widgetElement.querySelector('[data-action="satisfied"]').addEventListener('click', () => {
            this.submitFeedback(true);
        });
        
        this.widgetElement.querySelector('[data-action="unsatisfied"]').addEventListener('click', () => {
            this.submitFeedback(false);
        });
        
        // Rating con estrellas
        const stars = this.widgetElement.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const rating = parseInt(star.getAttribute('data-rating'));
                this.setRating(rating);
            });
            
            star.addEventListener('mouseover', () => {
                const rating = parseInt(star.getAttribute('data-rating'));
                this.highlightStars(rating);
            });
        });
        
        // Restablecer estrellas al quitar el mouse
        this.widgetElement.querySelector('.star-rating').addEventListener('mouseleave', () => {
            this.highlightStars(this.currentRating || 0);
        });
        
        // Botones de acciones detalladas
        this.widgetElement.querySelector('.submit-btn').addEventListener('click', () => {
            this.submitDetailedFeedback();
        });
        
        this.widgetElement.querySelector('.cancel-btn').addEventListener('click', () => {
            this.hideFeedbackWidget();
        });
    }
    
    bindGlobalEvents() {
        // Cerrar feedback al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (this.widgetElement.style.display === 'block' && 
                !this.widgetElement.contains(e.target) &&
                !e.target.closest('.ai-message')) {
                this.hideFeedbackWidget();
            }
        });
        
        // Tecla Escape para cerrar
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.widgetElement.style.display === 'block') {
                this.hideFeedbackWidget();
            }
        });
    }
    
    initializeFeedback(sessionId, positionElement = null) {
        this.currentSessionId = sessionId;
        this.feedbackSubmitted = false;
        this.currentRating = 0;
        
        // Posicionar el widget cerca del último mensaje de Ina
        if (positionElement) {
            this.positionWidgetNearElement(positionElement);
        }
        
        this.showFeedbackWidget();
    }
    
    positionWidgetNearElement(element) {
        const rect = element.getBoundingClientRect();
        this.widgetElement.style.position = 'absolute';
        this.widgetElement.style.top = `${rect.bottom + 10}px`;
        this.widgetElement.style.left = `${rect.left}px`;
        this.widgetElement.style.maxWidth = `${rect.width}px`;
    }
    
    async submitFeedback(isSatisfied) {
        if (!this.currentSessionId) {
            console.error('No hay sesión de feedback activa');
            return;
        }
        
        try {
            const response = await fetch('http://localhost:8000/feedback/response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    is_satisfied: isSatisfied,
                    rating: null,
                    comments: null
                })
            });
            
            if (response.ok) {
                if (isSatisfied) {
                    this.showThankYou();
                } else {
                    this.showDetailedFeedback();
                }
                
                // Analytics personalizado
                this.trackFeedbackEvent(isSatisfied ? 'positive' : 'negative');
            } else {
                console.error('Error en respuesta del servidor:', response.status);
            }
        } catch (error) {
            console.error('Error enviando feedback:', error);
            this.showError('Error al enviar feedback. Intenta nuevamente.');
        }
    }
    
    async submitDetailedFeedback() {
        if (!this.currentSessionId) return;
        
        const comments = this.widgetElement.querySelector('textarea').value;
        
        try {
            const response = await fetch('http://localhost:8000/feedback/response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    is_satisfied: false,
                    rating: this.currentRating || null,
                    comments: comments || null
                })
            });
            
            if (response.ok) {
                this.showThankYou();
                this.trackFeedbackEvent('detailed_negative', {
                    rating: this.currentRating,
                    hasComments: !!comments
                });
            }
        } catch (error) {
            console.error('Error enviando feedback detallado:', error);
            this.showError('Error al enviar comentarios. Intenta nuevamente.');
        }
    }
    
    setRating(rating) {
        this.currentRating = rating;
        this.highlightStars(rating);
    }
    
    highlightStars(rating) {
        const stars = this.widgetElement.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
    }
    
    showFeedbackWidget() {
        this.resetWidget();
        this.widgetElement.style.display = 'block';
        this.widgetElement.querySelector('.feedback-prompt').style.display = 'block';
    }
    
    showDetailedFeedback() {
        this.widgetElement.querySelector('.feedback-prompt').style.display = 'none';
        this.widgetElement.querySelector('.feedback-followup').style.display = 'block';
    }
    
    showThankYou() {
        this.feedbackSubmitted = true;
        this.widgetElement.querySelector('.feedback-prompt').style.display = 'none';
        this.widgetElement.querySelector('.feedback-followup').style.display = 'none';
        this.widgetElement.querySelector('.feedback-thankyou').style.display = 'block';
        
        // Ocultar automáticamente después de 3 segundos
        setTimeout(() => {
            this.hideFeedbackWidget();
        }, 3000);
    }
    
    showError(message) {
        // Implementación básica de mostrar error
        alert(message);
    }
    
    hideFeedbackWidget() {
        this.widgetElement.style.display = 'none';
        this.resetWidget();
    }
    
    resetWidget() {
        this.currentRating = 0;
        this.highlightStars(0);
        this.widgetElement.querySelector('textarea').value = '';
        
        // Mostrar todas las secciones ocultas
        this.widgetElement.querySelector('.feedback-prompt').style.display = 'block';
        this.widgetElement.querySelector('.feedback-followup').style.display = 'none';
        this.widgetElement.querySelector('.feedback-thankyou').style.display = 'none';
    }
    
    trackFeedbackEvent(type, metadata = {}) {
        // Analytics personalizado
        if (typeof gtag !== 'undefined') {
            gtag('event', 'feedback', {
                'event_category': 'user_feedback',
                'event_label': type,
                ...metadata
            });
        }
        
        // Console log para desarrollo
        console.log(`Feedback event: ${type}`, {
            sessionId: this.currentSessionId,
            ...metadata
        });
    }
    
    // Métodos utilitarios para integración con React
    static attachToLastAIMessage(sessionId) {
        const aiMessages = document.querySelectorAll('.ai-message');
        const lastAIMessage = aiMessages[aiMessages.length - 1];
        
        if (lastAIMessage) {
            window.inaFeedback.initializeFeedback(sessionId, lastAIMessage);
        }
    }
}

// Instancia global
window.inaFeedback = new InaFeedbackSystem();

// Auto-inicialización cuando el DOM está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.inaFeedback.initialize();
    });
} else {
    window.inaFeedback.initialize();
}