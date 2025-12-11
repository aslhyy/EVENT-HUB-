"""
Manejador global de excepciones para EventHub.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones.
    """
    # Llamar al manejador por defecto primero
    response = exception_handler(exc, context)
    
    # Si DRF no manejó la excepción, la manejamos nosotros
    if response is None:
        if isinstance(exc, ObjectDoesNotExist):
            return Response(
                {
                    'error': 'Recurso no encontrado',
                    'detail': str(exc),
                    'status_code': 404
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if isinstance(exc, Http404):
            return Response(
                {
                    'error': 'Recurso no encontrado',
                    'detail': 'El recurso solicitado no existe',
                    'status_code': 404
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Error no manejado - loguear y retornar 500
        logger.error(f'Unhandled exception: {exc}', exc_info=True)
        return Response(
            {
                'error': 'Error interno del servidor',
                'detail': 'Ha ocurrido un error inesperado',
                'status_code': 500
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Personalizar respuestas de DRF
    if isinstance(exc, ValidationError):
        response.data = {
            'error': 'Error de validación',
            'detail': response.data,
            'status_code': response.status_code
        }
    
    elif isinstance(exc, NotFound):
        response.data = {
            'error': 'No encontrado',
            'detail': str(exc),
            'status_code': 404
        }
    
    elif isinstance(exc, PermissionDenied):
        response.data = {
            'error': 'Permiso denegado',
            'detail': str(exc),
            'status_code': 403
        }
    
    else:
        # Estructura estándar para otras excepciones
        if not isinstance(response.data, dict):
            response.data = {'detail': response.data}
        
        response.data['status_code'] = response.status_code
    
    return response