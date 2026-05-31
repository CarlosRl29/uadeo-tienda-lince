"""
Vistas de la app catalogo.

Hay dos tipos:
1. Vistas de PÁGINA: solo regresan el HTML (sin meterle datos).
2. Vistas de API: usan serializers (DRF) para devolver JSON al JavaScript.
"""
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


# ---------------------------------------------------------------------------
# Vistas de PÁGINA
# ---------------------------------------------------------------------------

@ensure_csrf_cookie
def pagina_inicio(request):
    """Página principal: hero, anuncios, carrusel de destacados y enlaces."""
    return render(request, 'home.html')


@ensure_csrf_cookie
def pagina_catalogo(request):
    """Catálogo completo con sidebar de filtros + grid de productos."""
    return render(request, 'catalogo.html')


@ensure_csrf_cookie
def pagina_producto(request, slug):
    """Página de detalle de un producto."""
    get_object_or_404(Producto, slug=slug, activo=True)
    return render(request, 'producto.html')


def pagina_no_encontrada(request, exception):
    """Página 404 personalizada."""
    return render(request, '404.html', status=404)


# ---------------------------------------------------------------------------
# Vistas de API (con serializers)
# ---------------------------------------------------------------------------

@api_view(['GET'])
def api_categorias(request):
    """Lista todas las categorías activas (para los botones de filtro)."""
    categorias = Categoria.objects.filter(activa=True)
    serializer = CategoriaSerializer(categorias, many=True)
    return Response({'categorias': serializer.data})


@api_view(['GET'])
def api_productos(request):
    """
    Lista los productos activos.

    Filtros opcionales:
      ?categoria=papeleria
      ?q=cuaderno
      ?destacados=true
    """
    qs = Producto.objects.filter(activo=True).select_related('categoria')

    categoria_slug = request.GET.get('categoria', '').strip()
    if categoria_slug:
        qs = qs.filter(categoria__slug=categoria_slug)

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        qs = qs.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda))

    if request.GET.get('destacados') == 'true':
        qs = qs.filter(destacado=True)

    serializer = ProductoSerializer(qs, many=True, context={'request': request})
    return Response({'productos': serializer.data, 'total': len(serializer.data)})


@api_view(['GET'])
def api_producto_detalle(request, slug):
    """Detalle de un producto por su slug."""
    try:
        producto = Producto.objects.select_related('categoria').get(
            slug=slug, activo=True,
        )
    except Producto.DoesNotExist:
        return Response({'ok': False, 'error': 'Producto no encontrado.'}, status=404)

    serializer = ProductoSerializer(producto, context={'request': request})
    return Response({'ok': True, 'producto': serializer.data})
