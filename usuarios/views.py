"""
Vistas de la app usuarios.

Hay dos tipos:
1. Vistas de PÁGINA: solo entregan el HTML (registro.html, login.html).
2. Vistas de API: reciben/envían JSON para que el JavaScript hable con Django.
   Estas son las que crean usuarios, validan login y devuelven info de la sesión.

Importante: en este proyecto la MATRÍCULA es el "username" de Django.
Así el alumno solo necesita recordar su matrícula y su contraseña.
"""
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Carrera, PerfilAlumno


# ---------------------------------------------------------------------------
# Vistas de PÁGINA (solo entregan HTML, sin datos)
#
# @ensure_csrf_cookie obliga a Django a mandar la cookie csrftoken al
# navegador. La necesitamos porque nuestro JS (api.js) la lee para
# protegerse de CSRF al hacer POST.
# ---------------------------------------------------------------------------

@ensure_csrf_cookie
def pagina_registro(request):
    return render(request, 'registro.html')


@ensure_csrf_cookie
def pagina_login(request):
    return render(request, 'login.html')


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _leer_json(request):
    """Lee el cuerpo JSON de una petición y devuelve un dict.

    Si el JSON viene mal formado, devolvemos un dict vacío para que la
    validación posterior reporte los campos faltantes con un mensaje claro.
    """
    try:
        return json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return {}


def _datos_usuario(user):
    """Empaqueta los datos del usuario en un diccionario seguro para enviar al frontend.

    Nunca devolvemos el password ni datos sensibles.
    """
    perfil = getattr(user, 'perfil_alumno', None)
    return {
        'id': user.id,
        'username': user.username,
        'nombre': user.first_name,
        'apellido': user.last_name,
        'correo': user.email,
        'es_staff': user.is_staff,
        'tipo': perfil.tipo if perfil else '',
        'matricula': perfil.matricula if perfil else '',
        'carrera': perfil.carrera.nombre if perfil and perfil.carrera else '',
        'carrera_id': perfil.carrera_id if perfil else None,
        'telefono': perfil.telefono if perfil else '',
    }


# ---------------------------------------------------------------------------
# Vistas de API
# ---------------------------------------------------------------------------

@require_GET
def api_carreras(request):
    """Devuelve la lista de carreras activas para llenar el <select> del registro."""
    carreras = Carrera.objects.filter(activa=True).values('id', 'nombre')
    return JsonResponse({'carreras': list(carreras)})


@require_POST
def api_registro(request):
    """Crea un usuario nuevo (User + PerfilAlumno) en una sola transacción.

    Cuerpo esperado (JSON):
    {
      "tipo": "ALUMNO" | "PROFESOR",
      "nombre": "Juan",
      "apellido": "Pérez",
      "matricula": "20230501",
      "correo": "juan@uadeo.mx",
      "password": "abc12345",
      "carrera_id": 6,            // solo si tipo == "ALUMNO"
      "telefono": "6671234567"    // opcional, solo números
    }
    """
    datos = _leer_json(request)

    # Tipo de usuario: por defecto ALUMNO si no llega nada.
    tipo = str(datos.get('tipo') or PerfilAlumno.TIPO_ALUMNO).upper()
    if tipo not in (PerfilAlumno.TIPO_ALUMNO, PerfilAlumno.TIPO_PROFESOR):
        return JsonResponse(
            {'ok': False, 'error': 'Tipo de usuario no válido.'},
            status=400,
        )

    # Los campos básicos son obligatorios para ambos tipos.
    requeridos = ['nombre', 'apellido', 'matricula', 'correo', 'password']
    if tipo == PerfilAlumno.TIPO_ALUMNO:
        requeridos.append('carrera_id')

    faltantes = [c for c in requeridos if not datos.get(c)]
    if faltantes:
        return JsonResponse(
            {'ok': False, 'error': f'Faltan campos: {", ".join(faltantes)}'},
            status=400,
        )

    matricula = str(datos['matricula']).strip()
    correo = str(datos['correo']).strip().lower()
    password = datos['password']

    # Limpiamos el teléfono: solo dígitos.
    telefono_raw = str(datos.get('telefono') or '').strip()
    telefono = ''.join(ch for ch in telefono_raw if ch.isdigit())

    if len(password) < 8:
        return JsonResponse(
            {'ok': False, 'error': 'La contraseña debe tener al menos 8 caracteres.'},
            status=400,
        )

    if User.objects.filter(username=matricula).exists():
        return JsonResponse(
            {'ok': False, 'error': 'Ya existe una cuenta con esa matrícula.'},
            status=400,
        )

    if User.objects.filter(email__iexact=correo).exists():
        return JsonResponse(
            {'ok': False, 'error': 'Ya existe una cuenta con ese correo.'},
            status=400,
        )

    # Solo los alumnos llevan carrera. Para profesores la dejamos en None.
    carrera = None
    if tipo == PerfilAlumno.TIPO_ALUMNO:
        try:
            carrera = Carrera.objects.get(id=datos['carrera_id'], activa=True)
        except Carrera.DoesNotExist:
            return JsonResponse(
                {'ok': False, 'error': 'Carrera no válida.'},
                status=400,
            )

    # Creamos User + PerfilAlumno juntos. Si algo falla, no queda nada a medias.
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=matricula,
                email=correo,
                password=password,
                first_name=str(datos['nombre']).strip(),
                last_name=str(datos['apellido']).strip(),
            )
            PerfilAlumno.objects.create(
                usuario=user,
                matricula=matricula,
                tipo=tipo,
                carrera=carrera,
                telefono=telefono,
            )
    except IntegrityError:
        return JsonResponse(
            {'ok': False, 'error': 'No se pudo crear la cuenta. Intenta de nuevo.'},
            status=400,
        )

    # Iniciamos sesión automáticamente para no obligar al usuario a teclear de nuevo.
    login(request, user)

    return JsonResponse({'ok': True, 'usuario': _datos_usuario(user)}, status=201)


@require_POST
def api_login(request):
    """Inicia sesión con matrícula + contraseña.

    Cuerpo esperado (JSON):
    {
      "matricula": "20230501",
      "password": "abc12345"
    }
    """
    datos = _leer_json(request)
    matricula = str(datos.get('matricula') or '').strip()
    password = datos.get('password') or ''

    if not matricula or not password:
        return JsonResponse(
            {'ok': False, 'error': 'Matrícula y contraseña son obligatorias.'},
            status=400,
        )

    user = authenticate(request, username=matricula, password=password)
    if user is None:
        return JsonResponse(
            {'ok': False, 'error': 'Matrícula o contraseña incorrectos.'},
            status=401,
        )

    login(request, user)
    return JsonResponse({'ok': True, 'usuario': _datos_usuario(user)})


@require_POST
def api_logout(request):
    """Cierra la sesión actual."""
    logout(request)
    return JsonResponse({'ok': True})


@require_GET
def api_me(request):
    """Devuelve los datos del usuario logueado, o 401 si no hay sesión.

    El frontend usa este endpoint para saber si pintar "Iniciar sesión" o
    "Cerrar sesión" en la navbar al cargar cualquier página.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'autenticado': False}, status=401)

    return JsonResponse({'ok': True, 'autenticado': True, 'usuario': _datos_usuario(request.user)})
