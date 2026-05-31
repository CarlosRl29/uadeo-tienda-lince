"""
Modelos de la app catalogo.

Aquí vive todo lo relacionado con productos y categorías de la tienda.
"""
from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    """Agrupa productos por tipo (Papelería, Uniformes, Tecnología, etc.)."""

    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Si no se proporciona slug, lo generamos a partir del nombre.
        # Útil cuando se crean categorías por código en vez del admin.
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Producto(models.Model):
    """Artículo que el alumno puede agregar al carrito."""

    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    # upload_to es relativo a MEDIA_ROOT, así que las imágenes subidas
    # desde el admin se guardarán en media/productos/
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # no permitimos borrar una categoría con productos
        related_name='productos',
    )
    activo = models.BooleanField(default=True)
    # destacado: aparece en el carrusel "Los más vendidos" de la página de inicio.
    destacado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    @property
    def disponible(self):
        """True si el producto está activo y con stock."""
        return self.activo and self.stock > 0
