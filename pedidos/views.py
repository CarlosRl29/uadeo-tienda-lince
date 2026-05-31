"""
Vistas de la app pedidos.

1. PÁGINA: HTML del carrito, historial y confirmación.
2. API: serializers (DRF) para crear y consultar pedidos.
"""
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tienda_uadeo.api_utils import respuesta_error, respuesta_error_serializer

from .models import Pedido
from .serializers import CrearPedidoSerializer, PedidoSerializer


# ---------------------------------------------------------------------------
# Vistas de PÁGINA
# ---------------------------------------------------------------------------

@ensure_csrf_cookie
def pagina_carrito(request):
    return render(request, 'carrito.html')


@ensure_csrf_cookie
def pagina_mis_pedidos(request):
    return render(request, 'mis-pedidos.html')


@ensure_csrf_cookie
def pagina_confirmacion(request, codigo):
    return render(request, 'confirmacion.html', {'codigo': codigo})


# ---------------------------------------------------------------------------
# Vistas de API (con serializers)
# ---------------------------------------------------------------------------

@api_view(['POST'])
def api_crear_pedido(request):
    """Confirma el apartado desde el carrito del navegador."""
    if not request.user.is_authenticated:
        return respuesta_error('Debes iniciar sesión para continuar.', status=401)

    serializer = CrearPedidoSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return respuesta_error_serializer(serializer)

    pedido = serializer.save()
    pedido = Pedido.objects.prefetch_related('detalles__producto').get(pk=pedido.pk)
    return Response({
        'ok': True,
        'pedido': PedidoSerializer(pedido).data,
    }, status=201)


@api_view(['GET'])
def api_mis_pedidos(request):
    """Historial de pedidos del alumno logueado."""
    if not request.user.is_authenticated:
        return respuesta_error('Debes iniciar sesión para continuar.', status=401)

    pedidos = (
        Pedido.objects
        .filter(alumno=request.user)
        .prefetch_related('detalles__producto')
        .order_by('-fecha_creacion')
    )
    serializer = PedidoSerializer(pedidos, many=True)
    return Response({'ok': True, 'pedidos': serializer.data})


@api_view(['GET'])
def api_pedido_detalle(request, codigo):
    """Detalle de un pedido por código (solo si es del usuario logueado)."""
    if not request.user.is_authenticated:
        return respuesta_error('Debes iniciar sesión para continuar.', status=401)

    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('detalles__producto'),
        codigo_pedido=codigo,
        alumno=request.user,
    )
    return Response({'ok': True, 'pedido': PedidoSerializer(pedido).data})
