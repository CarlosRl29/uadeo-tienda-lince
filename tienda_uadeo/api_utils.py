"""
Helpers compartidos para respuestas de la API.
El frontend espera siempre: { ok: false, error: "mensaje" } en errores.
"""
from rest_framework.response import Response


def primer_error(serializer):
    """Extrae el primer mensaje de error de un serializer de DRF."""
    errors = serializer.errors
    if isinstance(errors, dict):
        for valor in errors.values():
            if isinstance(valor, list) and valor:
                return str(valor[0])
            return str(valor)
    return 'Datos no válidos.'


def respuesta_error(mensaje, status=400):
    return Response({'ok': False, 'error': mensaje}, status=status)


def respuesta_error_serializer(serializer, status=400):
    return respuesta_error(primer_error(serializer), status=status)
