"""
Vistas de la app catalogo.

Hay dos tipos:
1. Vistas de PÁGINA: solo regresan el HTML (sin meterle datos).
2. Vistas de API: regresan JSON para que el JavaScript pinte el contenido.
"""
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from .models import Categoria, Producto


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
    """Página de detalle de un producto.

    Validamos aquí (no en JS) que el slug exista para que el navegador
    devuelva un 404 real si la URL es inventada.
    """
    get_object_or_404(Producto, slug=slug, activo=True)
    return render(request, 'producto.html')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _url_imagen_producto(producto, request):
    """Devuelve la URL de la imagen del producto.

    Prioridad:
    1. Imagen subida desde el admin (campo imagen → carpeta media/)
    2. Imagen estática de respaldo en static/img/productos/<slug>.svg
    """
    if producto.imagen:
        return request.build_absolute_uri(producto.imagen.url)

    from django.conf import settings
    from django.templatetags.static import static

    ruta_fisica = settings.BASE_DIR / 'static' / 'img' / 'productos' / f'{producto.slug}.svg'
    if ruta_fisica.exists():
        return request.build_absolute_uri(static(f'img/productos/{producto.slug}.svg'))
    return ''


def _producto_a_dict(producto, request):
    """Convierte un Producto en un diccionario listo para JSON."""
    return {
        'id': producto.id,
        'nombre': producto.nombre,
        'slug': producto.slug,
        'descripcion': producto.descripcion,
        'precio': str(producto.precio),
        'stock': producto.stock,
        'imagen': _url_imagen_producto(producto, request),
        'categoria': producto.categoria.nombre,
        'categoria_slug': producto.categoria.slug,
        'destacado': producto.destacado,
        'disponible': producto.activo and producto.stock > 0,
    }


# ---------------------------------------------------------------------------
# Vistas de API
# ---------------------------------------------------------------------------

@require_GET
def api_categorias(request):
    """Lista todas las categorías activas (para los botones de filtro)."""
    categorias = Categoria.objects.filter(activa=True).values('id', 'nombre', 'slug')
    return JsonResponse({'categorias': list(categorias)})


@require_GET
def api_productos(request):
    """
    Lista los productos activos.

    Filtros opcionales en la URL:
      - ?categoria=papeleria     → filtra por slug de categoría
      - ?q=cuaderno              → busca en nombre y descripción
      - ?destacados=true         → solo productos marcados como destacados
    """
    qs = Producto.objects.filter(activo=True).select_related('categoria')

    categoria_slug = request.GET.get('categoria', '').strip()
    if categoria_slug:
        qs = qs.filter(categoria__slug=categoria_slug)

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        from django.db.models import Q
        qs = qs.filter(Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda))

    if request.GET.get('destacados') == 'true':
        qs = qs.filter(destacado=True)

    productos = [_producto_a_dict(p, request) for p in qs]
    return JsonResponse({'productos': productos, 'total': len(productos)})


@require_GET
def api_producto_detalle(request, slug):
    """Detalle de un producto por su slug."""
    try:
        producto = Producto.objects.select_related('categoria').get(
            slug=slug, activo=True,
        )
    except Producto.DoesNotExist:
        return JsonResponse(
            {'ok': False, 'error': 'Producto no encontrado.'},
            status=404,
        )
    return JsonResponse({'ok': True, 'producto': _producto_a_dict(producto, request)})


def pagina_no_encontrada(request, exception):
    """Página 404 personalizada (se usa cuando DEBUG=False o con handler404)."""
    return render(request, '404.html', status=404)
