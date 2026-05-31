"""
Vistas de la app usuarios.

1. Vistas de PÁGINA: entregan HTML (registro, login).
2. Vistas de API: usan serializers (DRF) para validar y devolver JSON.

La matrícula es el username de Django.
"""
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tienda_uadeo.api_utils import respuesta_error, respuesta_error_serializer

from .models import Carrera
from .serializers import (
    CarreraSerializer,
    LoginSerializer,
    RegistroSerializer,
    UsuarioSerializer,
)


# ---------------------------------------------------------------------------
# Vistas de PÁGINA
# ---------------------------------------------------------------------------

@ensure_csrf_cookie
def pagina_registro(request):
    return render(request, 'registro.html')


@ensure_csrf_cookie
def pagina_login(request):
    return render(request, 'login.html')


# ---------------------------------------------------------------------------
# Vistas de API (con serializers)
# ---------------------------------------------------------------------------

@api_view(['GET'])
def api_carreras(request):
    """Lista de carreras activas para el <select> del registro."""
    carreras = Carrera.objects.filter(activa=True)
    serializer = CarreraSerializer(carreras, many=True)
    return Response({'carreras': serializer.data})


@api_view(['POST'])
def api_registro(request):
    """Crea User + PerfilAlumno usando RegistroSerializer."""
    serializer = RegistroSerializer(data=request.data)
    if not serializer.is_valid():
        return respuesta_error_serializer(serializer)

    user = serializer.save()
    login(request, user)

    usuario_data = UsuarioSerializer(user).data
    return Response({'ok': True, 'usuario': usuario_data}, status=201)


@api_view(['POST'])
def api_login(request):
    """Inicia sesión con matrícula + contraseña."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        errors = serializer.errors
        if 'non_field_errors' in errors:
            return respuesta_error(str(errors['non_field_errors'][0]), status=401)
        return respuesta_error('Matrícula y contraseña son obligatorias.', status=400)

    user = serializer.validated_data['user']
    login(request, user)
    return Response({'ok': True, 'usuario': UsuarioSerializer(user).data})


@api_view(['POST'])
def api_logout(request):
    logout(request)
    return Response({'ok': True})


@api_view(['GET'])
def api_me(request):
    """Datos del usuario logueado, o 401 si no hay sesión."""
    if not request.user.is_authenticated:
        return Response({'ok': False, 'autenticado': False}, status=401)

    return Response({
        'ok': True,
        'autenticado': True,
        'usuario': UsuarioSerializer(request.user).data,
    })
