"""
Endpoints mejorados para el sistema de QR
=========================================
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime

# Importar el sistema mejorado
try:
    from enhanced_qr_system import enhanced_qr_generator, qr_health_checker
except ImportError:
    # Fallback al sistema original si no está disponible
    from app.qr_generator import qr_generator
    enhanced_qr_generator = None
    qr_health_checker = None

logger = logging.getLogger(__name__)

# Router para endpoints de QR
qr_router = APIRouter(prefix="/qr", tags=["QR"])

# Modelos Pydantic
class QRGenerationRequest(BaseModel):
    url: HttpUrl
    size: Optional[int] = 200
    validate_url: Optional[bool] = True
    with_logo: Optional[bool] = False

class BatchQRRequest(BaseModel):
    urls: List[HttpUrl]
    size: Optional[int] = 200
    validate_urls: Optional[bool] = True

class QRResponse(BaseModel):
    success: bool
    qr_data: Optional[str] = None
    url: str
    validated: Optional[bool] = None
    validation_message: Optional[str] = None
    from_cache: Optional[bool] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None

class BatchQRResponse(BaseModel):
    success: bool
    total_generated: int
    total_requested: int
    total_time: float
    results: Dict[str, Union[QRResponse, Dict]]

class HealthCheckResponse(BaseModel):
    overall_status: str
    timestamp: str
    checks: Dict

class MetricsResponse(BaseModel):
    qr_generated: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate_percentage: float
    validation_requests: int
    failed_validations: int
    cache_entries: int

@qr_router.post("/generate", response_model=QRResponse)
async def generate_qr_enhanced(request: QRGenerationRequest):
    """
    Generar QR con el sistema mejorado
    
    - **url**: URL para generar QR
    - **size**: Tamaño del QR en píxeles (default: 200)
    - **validate_url**: Validar si la URL es accesible (default: true)
    - **with_logo**: Agregar logo al QR (funcionalidad futura)
    """
    try:
        logger.info(f"📱 Solicitud de QR mejorado para: {request.url}")
        
        if enhanced_qr_generator:
            # Usar sistema mejorado
            result = enhanced_qr_generator.generate_enhanced_qr(
                str(request.url),
                size=request.size,
                with_logo=request.with_logo,
                validate_url=request.validate_url
            )
            
            if result:
                return QRResponse(
                    success=True,
                    qr_data=result['qr_data'],
                    url=result['url'],
                    validated=result.get('validated'),
                    validation_message=result.get('validation_message'),
                    from_cache=result.get('from_cache'),
                    generation_time=result.get('generation_time')
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to generate QR code")
        
        else:
            # Fallback al sistema original
            qr_code = qr_generator.generate_qr_code(str(request.url), request.size)
            if qr_code:
                return QRResponse(
                    success=True,
                    qr_data=qr_code,
                    url=str(request.url),
                    validated=None,
                    validation_message="Original system - no validation"
                )
            else:
                raise HTTPException(status_code=400, detail="Failed to generate QR code")
        
    except Exception as e:
        logger.error(f"❌ Error generando QR: {e}")
        return QRResponse(
            success=False,
            url=str(request.url),
            error=str(e)
        )

@qr_router.post("/generate/batch", response_model=BatchQRResponse)
async def generate_batch_qr(request: BatchQRRequest):
    """
    Generar múltiples QRs en lote
    
    - **urls**: Lista de URLs para generar QRs
    - **size**: Tamaño de los QRs (default: 200)
    - **validate_urls**: Validar URLs antes de generar (default: true)
    """
    try:
        logger.info(f"📦 Solicitud de lote de {len(request.urls)} QRs")
        
        if not enhanced_qr_generator:
            raise HTTPException(status_code=501, detail="Batch generation not available in basic mode")
        
        # Convertir URLs a strings
        urls_str = [str(url) for url in request.urls]
        
        # Generar en lote
        batch_result = enhanced_qr_generator.batch_generate_qrs(
            urls_str,
            size=request.size,
            validate=request.validate_urls
        )
        
        # Convertir resultados al formato esperado
        formatted_results = {}
        for url, result in batch_result['results'].items():
            if 'error' in result:
                formatted_results[url] = QRResponse(
                    success=False,
                    url=url,
                    error=result['error']
                )
            else:
                formatted_results[url] = QRResponse(
                    success=True,
                    qr_data=result['qr_data'],
                    url=result['url'],
                    validated=result.get('validated'),
                    validation_message=result.get('validation_message'),
                    from_cache=result.get('from_cache'),
                    generation_time=result.get('generation_time')
                )
        
        return BatchQRResponse(
            success=True,
            total_generated=batch_result['total_generated'],
            total_requested=len(request.urls),
            total_time=batch_result['total_time'],
            results=formatted_results
        )
        
    except Exception as e:
        logger.error(f"❌ Error en generación de lote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@qr_router.get("/health", response_model=HealthCheckResponse)
async def check_qr_system_health():
    """
    Verificar el estado de salud del sistema de QR
    
    Retorna información sobre:
    - Estado de generación de QR
    - Conectividad de URLs principales
    - Estado del cache
    - Métricas generales
    """
    try:
        if not qr_health_checker:
            return HealthCheckResponse(
                overall_status="unknown",
                timestamp=datetime.now().isoformat(),
                checks={"message": "Health checking not available in basic mode"}
            )
        
        health_report = qr_health_checker.check_system_health()
        
        return HealthCheckResponse(
            overall_status=health_report['overall_status'],
            timestamp=health_report['timestamp'],
            checks=health_report['checks']
        )
        
    except Exception as e:
        logger.error(f"❌ Error verificando salud del sistema: {e}")
        return HealthCheckResponse(
            overall_status="error",
            timestamp=datetime.now().isoformat(),
            checks={"error": str(e)}
        )

@qr_router.get("/metrics", response_model=MetricsResponse)
async def get_qr_metrics():
    """
    Obtener métricas del sistema de QR
    
    Incluye:
    - Estadísticas de generación
    - Información de cache
    - Tasas de éxito/fallo
    """
    try:
        if not enhanced_qr_generator:
            raise HTTPException(status_code=501, detail="Metrics not available in basic mode")
        
        metrics = enhanced_qr_generator.get_metrics()
        
        return MetricsResponse(
            qr_generated=metrics['qr_generated'],
            cache_hits=metrics['cache_hits'],
            cache_misses=metrics['cache_misses'],
            cache_hit_rate_percentage=metrics['cache_hit_rate_percentage'],
            validation_requests=metrics['validation_requests'],
            failed_validations=metrics['failed_validations'],
            cache_entries=metrics['cache_entries']
        )
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@qr_router.post("/cache/clear")
async def clear_qr_cache(background_tasks: BackgroundTasks):
    """
    Limpiar el cache del sistema de QR
    
    Útil para:
    - Liberar memoria
    - Forzar regeneración de QRs
    - Mantenimiento del sistema
    """
    try:
        if not enhanced_qr_generator:
            raise HTTPException(status_code=501, detail="Cache management not available in basic mode")
        
        # Limpiar cache en background para no bloquear la respuesta
        background_tasks.add_task(enhanced_qr_generator.clear_cache)
        
        return {
            "success": True,
            "message": "Cache clearing initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error limpiando cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@qr_router.get("/urls/validate/{url:path}")
async def validate_single_url(url: str):
    """
    Validar una URL específica sin generar QR
    
    - **url**: URL a validar
    """
    try:
        if not enhanced_qr_generator:
            raise HTTPException(status_code=501, detail="URL validation not available in basic mode")
        
        is_valid, message, fallback_url = enhanced_qr_generator.validate_url(url)
        
        return {
            "url": url,
            "valid": is_valid,
            "message": message,
            "fallback_url": fallback_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error validando URL {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@qr_router.get("/system/info")
async def get_system_info():
    """
    Obtener información sobre el sistema de QR disponible
    """
    return {
        "enhanced_system_available": enhanced_qr_generator is not None,
        "health_checking_available": qr_health_checker is not None,
        "features": {
            "url_validation": enhanced_qr_generator is not None,
            "caching": enhanced_qr_generator is not None,
            "batch_generation": enhanced_qr_generator is not None,
            "metrics": enhanced_qr_generator is not None,
            "health_checks": qr_health_checker is not None,
            "fallback_urls": enhanced_qr_generator is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# Endpoints compatibles con el sistema anterior
@qr_router.get("/duoc-urls")
async def get_all_duoc_qrs_enhanced():
    """
    Obtener todos los QR de URLs de Duoc (versión mejorada)
    """
    try:
        from app.qr_generator import duoc_url_manager
        
        all_urls = duoc_url_manager.get_all_urls()
        qr_data = {}
        
        for key, url in all_urls.items():
            if enhanced_qr_generator:
                result = enhanced_qr_generator.generate_enhanced_qr(url, validate_url=True)
                if result:
                    qr_data[key] = {
                        "url": result['url'],
                        "qr_code": result['qr_data'],
                        "name": key.replace('_', ' ').title(),
                        "validated": result.get('validated', False),
                        "from_cache": result.get('from_cache', False)
                    }
            else:
                # Fallback al sistema original
                from app.qr_generator import qr_generator
                qr_code = qr_generator.generate_duoc_qr(key)
                if qr_code:
                    qr_data[key] = {
                        "url": url,
                        "qr_code": qr_code,
                        "name": key.replace('_', ' ').title(),
                        "validated": None
                    }
        
        return {
            "status": "success",
            "total_qrs": len(qr_data),
            "qr_codes": qr_data,
            "enhanced_system": enhanced_qr_generator is not None
        }
        
    except Exception as e:
        logger.error(f"❌ Error generando QRs Duoc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@qr_router.get("/generate-simple")
async def generate_simple_qr(url: str):
    """
    Generar QR simple (compatibilidad con sistema anterior)
    """
    try:
        request = QRGenerationRequest(url=url)
        return await generate_qr_enhanced(request)
    except Exception as e:
        logger.error(f"❌ Error en generación simple: {e}")
        raise HTTPException(status_code=500, detail=str(e))