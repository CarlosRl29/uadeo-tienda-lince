"""
Vistas de la app pedidos.

Tipos de vista:
1. PÁGINA: entregan HTML (carrito, mis pedidos, confirmación).
2. API: reciben/envían JSON para confirmar apartados y consultar historial.
"""
import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from catalogo.models import Producto

from .models import DetallePedido, Pedido


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _leer_json(request):
    try:
        return json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return {}


def _requiere_login(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'ok': False, 'error': 'Debes iniciar sesión para continuar.'},
            status=401,
        )
    return None


def _pedido_a_dict(pedido, incluir_detalles=False):
    """Convierte un Pedido a dict seguro para el frontend."""
    data = {
        'codigo': pedido.codigo_pedido,
        'total': str(pedido.total),
        'estado': pedido.estado,
        'estado_texto': pedido.get_estado_display(),
        'fecha': pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
    }
    if incluir_detalles:
        detalles = []
        for d in pedido.detalles.select_related('producto'):
            detalles.append({
                'producto': d.producto.nombre,
                'slug': d.producto.slug,
                'cantidad': d.cantidad,
                'precio_unitario': str(d.precio_unitario),
                'subtotal': str(d.subtotal),
            })
        data['detalles'] = detalles
    return data


# ---------------------------------------------------------------------------
# Vistas de PÁGINA
# ---------------------------------------------------------------------------

@ensure_csrf_cookie
def pagina_carrito(request):
    """Página del carrito. El contenido se llena con JavaScript leyendo localStorage."""
    return render(request, 'carrito.html')


@ensure_csrf_cookie
def pagina_mis_pedidos(request):
    """Historial de pedidos del alumno logueado."""
    return render(request, 'mis-pedidos.html')


@ensure_csrf_cookie
def pagina_confirmacion(request, codigo):
    """Página de confirmación después de apartar. El JS lee el código de la URL."""
    return render(request, 'confirmacion.html', {'codigo': codigo})


# ---------------------------------------------------------------------------
# Vistas de API
# ---------------------------------------------------------------------------

@require_POST
def api_crear_pedido(request):
    """Confirma el apartado: crea Pedido + DetallePedido y descuenta stock.

    Cuerpo esperado (JSON):
    {
      "items": [
        { "slug": "playera-uadeo", "cantidad": 2 },
        ...
      ]
    }

    Usamos transaction.atomic() y select_for_update() para que dos alumnos
    no aparten el mismo stock al mismo tiempo.
    """
    no_auth = _requiere_login(request)
    if no_auth:
        return no_auth

    datos = _leer_json(request)
    items_raw = datos.get('items')

    if not items_raw or not isinstance(items_raw, list):
        return JsonResponse(
            {'ok': False, 'error': 'El carrito está vacío o llegó mal formado.'},
            status=400,
        )

    # Agrupamos por slug por si el frontend manda duplicados.
    cantidades = {}
    for item in items_raw:
        slug = str(item.get('slug') or '').strip()
        cantidad = int(item.get('cantidad') or 0)
        if not slug or cantidad <= 0:
            continue
        cantidades[slug] = cantidades.get(slug, 0) + cantidad

    if not cantidades:
        return JsonResponse(
            {'ok': False, 'error': 'No hay productos válidos en el carrito.'},
            status=400,
        )

    try:
        with transaction.atomic():
            pedido = Pedido.objects.create(alumno=request.user)

            for slug, cantidad in cantidades.items():
                try:
                    producto = (
                        Producto.objects
                        .select_for_update()
                        .get(slug=slug, activo=True)
                    )
                except Producto.DoesNotExist:
                    raise ValueError(f'El producto "{slug}" ya no está disponible.')

                if producto.stock < cantidad:
                    raise ValueError(
                        f'Stock insuficiente para "{producto.nombre}". '
                        f'Disponible: {producto.stock}, solicitado: {cantidad}.'
                    )

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )

                producto.stock -= cantidad
                producto.save(update_fields=['stock'])

            pedido.recalcular_total()

    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    return JsonResponse({
        'ok': True,
        'pedido': _pedido_a_dict(pedido, incluir_detalles=True),
    }, status=201)


@require_GET
def api_mis_pedidos(request):
    """Lista los pedidos del usuario logueado (más recientes primero)."""
    no_auth = _requiere_login(request)
    if no_auth:
        return no_auth

    pedidos = (
        Pedido.objects
        .filter(alumno=request.user)
        .prefetch_related('detalles__producto')
        .order_by('-fecha_creacion')
    )

    lista = [_pedido_a_dict(p, incluir_detalles=True) for p in pedidos]
    return JsonResponse({'ok': True, 'pedidos': lista})


@require_GET
def api_pedido_detalle(request, codigo):
    """Devuelve un pedido por código. Solo si pertenece al usuario logueado."""
    no_auth = _requiere_login(request)
    if no_auth:
        return no_auth

    try:
        pedido = (
            Pedido.objects
            .prefetch_related('detalles__producto')
            .get(codigo_pedido=codigo, alumno=request.user)
        )
    except Pedido.DoesNotExist:
        return JsonResponse(
            {'ok': False, 'error': 'Pedido no encontrado.'},
            status=404,
        )

    return JsonResponse({'ok': True, 'pedido': _pedido_a_dict(pedido, incluir_detalles=True)})
