"""
Interfaz Web de Monitoreo para Producción
Accesible vía navegador cuando no hay acceso a CMD
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path
from datetime import datetime
import asyncio

# Crear endpoints de monitoreo en el FastAPI principal
def setup_monitoring_routes(app: FastAPI):
    """Añadir rutas de monitoreo al FastAPI principal"""
    
    @app.get("/monitoring", response_class=HTMLResponse)
    async def monitoring_dashboard():
        """Dashboard HTML para monitoreo"""
        html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor Sistema IA Plaza Norte</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .status-card h3 {
            margin-top: 0;
            color: #495057;
            font-size: 1.2em;
        }
        .status-online {
            border-left: 5px solid #28a745;
        }
        .status-warning {
            border-left: 5px solid #ffc107;
        }
        .status-error {
            border-left: 5px solid #dc3545;
        }
        .metrics-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .log-section {
            background: #343a40;
            color: #fff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .log-entry {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .error-log {
            background: rgba(220,53,69,0.2);
            border-left: 3px solid #dc3545;
        }
        .warning-log {
            background: rgba(255,193,7,0.2);
            border-left: 3px solid #ffc107;
        }
        .info-log {
            background: rgba(40,167,69,0.2);
            border-left: 3px solid #28a745;
        }
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            cursor: pointer;
            font-size: 1em;
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        .timestamp {
            font-size: 0.8em;
            color: #6c757d;
            margin-bottom: 15px;
        }
        .health-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .health-online { background: #28a745; }
        .health-warning { background: #ffc107; }
        .health-error { background: #dc3545; }
        .export-btn {
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            margin: 10px 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .export-btn:hover {
            background: #545b62;
        }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="refreshData()">🔄 Actualizar</button>
    
    <div class="container">
        <h1>🖥️ Monitor Sistema IA Plaza Norte</h1>
        <div class="timestamp" id="lastUpdate">Cargando...</div>
        
        <div class="status-grid" id="statusGrid">
            <!-- Se carga dinámicamente -->
        </div>
        
        <div class="metrics-section">
            <h3>📊 Métricas de Rendimiento</h3>
            <div id="metricsContent">Cargando métricas...</div>
        </div>
        
        <div class="log-section">
            <h3>📋 Eventos Recientes</h3>
            <div>
                <a href="/monitoring/export" class="export-btn">📤 Exportar Logs</a>
                <a href="/monitoring/health" class="export-btn">🏥 Health Check</a>
            </div>
            <div id="logsContent">Cargando eventos...</div>
        </div>
    </div>

    <script>
        async function loadMonitoringData() {
            try {
                const response = await fetch('/monitoring/api/dashboard');
                const data = await response.json();
                
                updateTimestamp();
                updateStatusGrid(data);
                updateMetrics(data);
                updateLogs(data);
                
            } catch (error) {
                console.error('Error cargando datos:', error);
                document.getElementById('statusGrid').innerHTML = 
                    '<div class="status-card status-error"><h3>❌ Error de Conexión</h3><p>No se pueden cargar los datos del sistema</p></div>';
            }
        }
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = 
                `Última actualización: ${now.toLocaleString('es-ES')}`;
        }
        
        function updateStatusGrid(data) {
            const grid = document.getElementById('statusGrid');
            const systemInfo = data.system_info || {};
            const healthSummary = data.health_summary || {};
            
            let statusClass = 'status-online';
            if (systemInfo.status === 'warning' || systemInfo.status === 'degraded') {
                statusClass = 'status-warning';
            } else if (systemInfo.status === 'error' || systemInfo.status === 'critical') {
                statusClass = 'status-error';
            }
            
            grid.innerHTML = `
                <div class="status-card ${statusClass}">
                    <h3><span class="health-indicator health-${systemInfo.status === 'healthy' ? 'online' : systemInfo.status === 'degraded' ? 'warning' : 'error'}"></span>Estado General</h3>
                    <p><strong>Estado:</strong> ${systemInfo.status || 'Desconocido'}</p>
                    <p><strong>Tiempo activo:</strong> ${systemInfo.uptime_minutes || 0} minutos</p>
                    <p><strong>Inicio:</strong> ${systemInfo.startup_time ? new Date(systemInfo.startup_time).toLocaleString('es-ES') : 'N/A'}</p>
                </div>
                
                <div class="status-card">
                    <h3>🤖 Sistema IA</h3>
                    <p><strong>Ollama:</strong> ${getHealthStatus(healthSummary, 'ollama')}</p>
                    <p><strong>ChromaDB:</strong> ${getHealthStatus(healthSummary, 'chromadb')}</p>
                    <p><strong>Sistema Híbrido:</strong> ${getHealthStatus(healthSummary, 'hybrid_system')}</p>
                </div>
                
                <div class="status-card">
                    <h3>📚 Recursos</h3>
                    <p><strong>Templates:</strong> ${getTemplateCount(healthSummary)}</p>
                    <p><strong>Espacio en disco:</strong> ${getDiskSpace(healthSummary)}</p>
                    <p><strong>Errores recientes:</strong> ${(data.recent_errors || []).length}</p>
                </div>
                
                <div class="status-card">
                    <h3>⚡ Rendimiento</h3>
                    <div id="performanceMetrics">
                        ${formatPerformanceMetrics(data.performance || {})}
                    </div>
                </div>
            `;
        }
        
        function getHealthStatus(healthSummary, service) {
            const checks = healthSummary.checks || {};
            const serviceData = checks[service];
            
            if (!serviceData) return '❓ Desconocido';
            
            const status = serviceData.status;
            const statusIcons = {
                'online': '✅',
                'offline': '❌',
                'error': '⚠️',
                'warning': '⚠️',
                'ok': '✅'
            };
            
            const icon = statusIcons[status] || '❓';
            return `${icon} ${status}`;
        }
        
        function getTemplateCount(healthSummary) {
            const checks = healthSummary.checks || {};
            const templates = checks.templates;
            return templates ? `${templates.count || 0} disponibles` : 'No verificado';
        }
        
        function getDiskSpace(healthSummary) {
            const checks = healthSummary.checks || {};
            const disk = checks.disk_space;
            return disk ? `${disk.free_gb || 'N/A'} GB libres` : 'No verificado';
        }
        
        function formatPerformanceMetrics(performance) {
            if (!performance || Object.keys(performance).length === 0) {
                return '<p>No hay métricas disponibles</p>';
            }
            
            let html = '';
            for (const [metric, data] of Object.entries(performance)) {
                html += `<p><strong>${metric}:</strong> ${data.current_value} (${data.context})</p>`;
            }
            return html;
        }
        
        function updateMetrics(data) {
            // Esta función se puede expandir para mostrar gráficos
            const metricsDiv = document.getElementById('metricsContent');
            metricsDiv.innerHTML = formatPerformanceMetrics(data.performance || {});
        }
        
        function updateLogs(data) {
            const logsDiv = document.getElementById('logsContent');
            let logsHtml = '';
            
            // Mostrar errores recientes
            const recentErrors = data.recent_errors || [];
            const recentWarnings = data.recent_warnings || [];
            
            [...recentErrors, ...recentWarnings]
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .slice(0, 10)
                .forEach(log => {
                    const logClass = log.error_type ? 'error-log' : 'warning-log';
                    const timestamp = new Date(log.timestamp).toLocaleString('es-ES');
                    
                    logsHtml += `
                        <div class="log-entry ${logClass}">
                            <strong>[${timestamp}]</strong> ${log.message || log.error_type || 'Evento'}<br>
                            <small>${log.context || 'Sin contexto'}</small>
                        </div>
                    `;
                });
            
            if (logsHtml === '') {
                logsHtml = '<div class="log-entry info-log">✅ No hay eventos recientes - Sistema funcionando correctamente</div>';
            }
            
            logsDiv.innerHTML = logsHtml;
        }
        
        function refreshData() {
            loadMonitoringData();
        }
        
        // Auto-refresh cada 30 segundos
        setInterval(loadMonitoringData, 30000);
        
        // Cargar datos inicial
        loadMonitoringData();
    </script>
</body>
</html>"""
        return html_content
    
    @app.get("/monitoring/api/dashboard")
    async def get_monitoring_data():
        """API endpoint para datos de monitoreo"""
        try:
            from app.production_monitor import get_monitoring_dashboard
            dashboard_data = await get_monitoring_dashboard()
            return dashboard_data
        except Exception as e:
            return {
                "error": str(e),
                "system_info": {"status": "error"},
                "recent_errors": [{"message": f"Error cargando dashboard: {e}", "timestamp": datetime.now().isoformat()}],
                "recent_warnings": [],
                "performance": {},
                "health_summary": {"status": "error"}
            }
    
    @app.get("/monitoring/health")
    async def health_check_endpoint():
        """Endpoint de verificación de salud"""
        try:
            from app.production_monitor import system_health_check
            health_data = await system_health_check()
            return health_data
        except Exception as e:
            return {"error": str(e), "status": "error", "timestamp": datetime.now().isoformat()}
    
    @app.get("/monitoring/export")
    async def export_logs():
        """Endpoint para exportar logs"""
        try:
            from app.production_monitor import production_monitor
            export_file = await production_monitor.export_logs_for_analysis(24)
            
            return JSONResponse({
                "status": "success",
                "export_file": export_file,
                "message": "Logs exportados exitosamente",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return JSONResponse({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    @app.get("/monitoring/status")
    async def simple_status():
        """Status simple para checks externos"""
        try:
            # Verificaciones básicas
            status = "healthy"
            checks = {}
            
            # Check Ollama
            try:
                import requests
                response = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
                checks["ollama"] = response.status_code == 200
            except:
                checks["ollama"] = False
                status = "degraded"
            
            # Check templates
            template_path = Path("app/templates")
            checks["templates"] = template_path.exists()
            if not checks["templates"]:
                status = "degraded"
            
            # Check disk space
            import shutil
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            checks["disk_space"] = free_gb > 0.5
            if not checks["disk_space"]:
                status = "warning"
            
            return {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "checks": checks,
                "uptime": "available"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Función para integrar en main.py
def integrate_monitoring_to_main():
    """Código para añadir a main.py"""
    integration_code = '''
# Añadir al final de app/main.py

# Integrar monitoreo de producción
try:
    from app.monitoring_interface import setup_monitoring_routes
    setup_monitoring_routes(app)
    logger.info("✅ Rutas de monitoreo integradas")
except Exception as e:
    logger.error(f"❌ Error integrando monitoreo: {e}")

# Middleware para logging de requests
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log métrica de rendimiento
        try:
            from app.production_monitor import log_performance_metric
            await log_performance_metric(
                "request_time", 
                process_time, 
                f"{request.method} {request.url.path}"
            )
        except:
            pass  # No fallar si no hay monitor
        
        return response
        
    except Exception as e:
        # Log error
        try:
            from app.production_monitor import log_system_error
            await log_system_error(e, f"Request {request.method} {request.url.path}")
        except:
            pass  # No fallar si no hay monitor
        
        raise e
'''
    
    return integration_code