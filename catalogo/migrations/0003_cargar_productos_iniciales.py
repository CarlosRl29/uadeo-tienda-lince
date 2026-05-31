"""
Data migration: 12 productos de prueba para la tienda UAdeO Lince.

Las imágenes se dejan vacías a propósito: el administrador las sube
después desde el panel admin (Producto -> Imagen).
"""
from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


# Cada tupla: (nombre, categoria_nombre, precio, stock, descripcion)
PRODUCTOS = [
    ('Playera UAdeO', 'Identidad UAdeO', '220.00', 30,
     'Playera oficial UAdeO con escudo bordado. Disponible en varias tallas.'),
    ('Sudadera UAdeO', 'Identidad UAdeO', '480.00', 15,
     'Sudadera con capucha y estampado UAdeO. Ideal para el frío del semestre.'),
    ('Gorra Lince', 'Identidad UAdeO', '180.00', 25,
     'Gorra ajustable con bordado del lince universitario.'),
    ('Termo UAdeO', 'Identidad UAdeO', '260.00', 20,
     'Termo de acero inoxidable, 500 ml, con logo institucional.'),
    ('Taza UAdeO', 'Identidad UAdeO', '120.00', 40,
     'Taza cerámica con escudo UAdeO. Para tu café del semestre.'),
    ('Llavero Lince', 'Identidad UAdeO', '60.00', 50,
     'Llavero metálico con el lince UAdeO.'),
    ('Lanyard porta gafete', 'Identidad UAdeO', '80.00', 60,
     'Cordón con clip para portar tu credencial UAdeO.'),
    ('Cuaderno universitario', 'Papelería', '75.00', 100,
     'Cuaderno profesional 100 hojas, raya, con portada UAdeO.'),
    ('Pluma institucional', 'Papelería', '25.00', 200,
     'Pluma con logo UAdeO, tinta negra.'),
    ('Carpeta escolar', 'Papelería', '95.00', 50,
     'Carpeta tamaño carta con divisores y logo UAdeO.'),
    ('Memoria USB 32GB', 'Tecnología', '220.00', 25,
     'Memoria USB 3.0 de 32 GB, ideal para llevar tus trabajos.'),
    ('Bata para prácticas', 'Prácticas', '320.00', 18,
     'Bata blanca para laboratorio y prácticas profesionales.'),
]


def crear_productos(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    Categoria = apps.get_model('catalogo', 'Categoria')

    # Pre-cargamos las categorías en un diccionario para evitar consultas repetidas.
    categorias = {c.nombre: c for c in Categoria.objects.all()}

    for nombre, cat_nombre, precio, stock, descripcion in PRODUCTOS:
        categoria = categorias.get(cat_nombre)
        if categoria is None:
            # Si por algún motivo la categoría no existe, la saltamos.
            continue
        Producto.objects.get_or_create(
            nombre=nombre,
            defaults={
                'slug': slugify(nombre),
                'descripcion': descripcion,
                'precio': Decimal(precio),
                'stock': stock,
                'categoria': categoria,
                'activo': True,
            },
        )


def eliminar_productos(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    nombres = [p[0] for p in PRODUCTOS]
    Producto.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_cargar_categorias_iniciales'),
    ]

    operations = [
        migrations.RunPython(crear_productos, eliminar_productos),
    ]
