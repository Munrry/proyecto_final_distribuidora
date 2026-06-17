# Distribebidas/context_processors.py
from .models import Gaseosa

def crm_stock_context(request):
    """
    Inyecta de forma global el listado de bebidas para que el CRM Operativo 
    pueda evaluar las alertas de stock en cualquier vista del sistema.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return {'bebidas': Gaseosa.objects.all()}
    return {'bebidas': []}