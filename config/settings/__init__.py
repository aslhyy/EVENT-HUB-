"""
Configuración de settings basada en el entorno.
"""
from decouple import config

# Determinar qué configuración usar
ENVIRONMENT = config('ENVIRONMENT', default='dev')

if ENVIRONMENT == 'prod':
    from .prod import *
else:
    from .dev import *