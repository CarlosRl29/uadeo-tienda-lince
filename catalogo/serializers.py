"""
Serializers de la app catalogo.

Un serializer convierte objetos de Python (modelos) ↔ JSON.
Reemplaza las funciones manuales como _producto_a_dict().
"""
from django.conf import settings
from django.templatetags.static import static
from rest_framework import serializers

from .models import Categoria, Producto


def url_imagen_producto(producto, request):
    """URL de la imagen: admin (media/) o SVG estática de respaldo."""
    if producto.imagen:
        return request.build_absolute_uri(producto.imagen.url)

    ruta_fisica = settings.BASE_DIR / 'static' / 'img' / 'productos' / f'{producto.slug}.svg'
    if ruta_fisica.exists():
        return request.build_absolute_uri(static(f'img/productos/{producto.slug}.svg'))
    return ''


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug']


class ProductoSerializer(serializers.ModelSerializer):
    """Convierte un Producto al JSON que espera el frontend."""

    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_slug = serializers.CharField(source='categoria.slug', read_only=True)
    precio = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=True,
    )
    imagen = serializers.SerializerMethodField()
    disponible = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'slug', 'descripcion', 'precio', 'stock',
            'imagen', 'categoria', 'categoria_slug', 'destacado', 'disponible',
        ]

    def get_imagen(self, producto):
        request = self.context.get('request')
        if not request:
            return ''
        return url_imagen_producto(producto, request)

    def get_disponible(self, producto):
        return producto.activo and producto.stock > 0
