"""
Data migration: catálogo con productos que usan las fotos PNG en static/img/productos/.

Desactiva los 12 productos de prueba anteriores y carga 20 productos nuevos
con slug que coincide con el nombre del archivo PNG (ej: playera.png -> slug).
"""
from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


# (nombre, categoria, precio, stock, descripcion, slug_imagen_sin_extension, destacado)
PRODUCTOS_PNG = [
    ('Camiseta deportiva UAdeO', 'Identidad UAdeO', '280.00', 25,
     'Camiseta deportiva con detalles blancos y logo institucional.',
     'camiseta-deportiva-uadeo', True),
    ('Sudadera UAdeO con emblema', 'Identidad UAdeO', '520.00', 18,
     'Sudadera con emblema bordado UAdeO. Ideal para el campus.',
     'sudadera-uadeo-emblema', True),
    ('Chaqueta cortavientos UAdeO', 'Uniformes', '650.00', 12,
     'Chaqueta cortavientos color burdeos con logo UAdeO.',
     'chaqueta-cortavientos-uadeo', False),
    ('Chaleco UAdeO bordado', 'Uniformes', '480.00', 15,
     'Chaleco marón con detalles bordados institucionales.',
     'chaleco-uadeo-bordado', False),
    ('Botella deportiva UAdeO', 'Identidad UAdeO', '180.00', 30,
     'Botella deportiva blanca con logo UAdeO.',
     'botella-deportiva-uadeo', True),
    ('Taza de viaje UAdeO', 'Identidad UAdeO', '150.00', 35,
     'Taza térmica de viaje con acabado mármol y logo UAdeO.',
     'taza-viaje-uadeo', True),
    ('Pin escudo UAdeO', 'Identidad UAdeO', '45.00', 80,
     'Pin metálico con escudo de la universidad.',
     'pin-escudo-uadeo', False),
    ('Peluche Lince UAdeO', 'Identidad UAdeO', '320.00', 20,
     'Peluche de la mascota Lince con hoodie UAdeO.',
     'peluche-lince-uadeo', False),
    ('Cuaderno universitario UAdeO', 'Papelería', '95.00', 60,
     'Cuaderno profesional color vino con emblema UAdeO.',
     'cuaderno-universitario-uadeo', True),
    ('Carpeta con sello UAdeO', 'Papelería', '120.00', 40,
     'Carpeta elegante con sello institucional.',
     'carpeta-sello-uadeo', False),
    ('Batería portátil UAdeO', 'Tecnología', '380.00', 22,
     'Batería portátil con logo UAdeO para cargar tus dispositivos.',
     'bateria-portatil-uadeo', False),
    ('Audífonos inalámbricos UAdeO', 'Tecnología', '450.00', 18,
     'Audífonos inalámbricos con estuche y logo institucional.',
     'audifonos-inalambricos-uadeo', False),
    ('Altavoz portátil UAdeO', 'Tecnología', '420.00', 16,
     'Altavoz portátil con diseño elegante y marca UAdeO.',
     'altavoz-portatil-uadeo', False),
    ('Funda laptop UAdeO', 'Tecnología', '290.00', 24,
     'Funda para laptop con logo UAdeO.',
     'funda-laptop-uadeo', False),
    ('Maletín UAdeO cuero', 'Útiles', '580.00', 14,
     'Maletín color burdeos con detalles de cuero.',
     'maletin-uadeo-cuero', False),
    ('Portafolio UAdeO cuero', 'Papelería', '520.00', 12,
     'Portafolio en cuero burdeos con logo UAdeO.',
     'portafolio-uadeo-cuero', False),
    ('Paraguas UAdeO', 'Identidad UAdeO', '220.00', 28,
     'Paraguas institucional para la temporada de lluvias.',
     'paraguas-uadeo', False),
    ('Banda de silicón UAdeO', 'Identidad UAdeO', '35.00', 100,
     'Banda de silicón con detalle UAdeO.',
     'banda-silicon-uadeo', False),
    ('Calendario de mesa UAdeO 2025', 'Papelería', '85.00', 45,
     'Calendario de escritorio UAdeO edición 2025.',
     'calendario-mesa-uadeo-2025', False),
    ('Marco diploma UAdeO', 'Identidad UAdeO', '180.00', 20,
     'Marco para diploma con acabado institucional.',
     'marco-diploma-uadeo', False),
]

NOMBRES_ANTIGUOS = [
    'Playera UAdeO', 'Sudadera UAdeO', 'Gorra Lince', 'Termo UAdeO',
    'Taza UAdeO', 'Llavero Lince', 'Lanyard porta gafete',
    'Cuaderno universitario', 'Pluma institucional', 'Carpeta escolar',
    'Memoria USB 32GB', 'Bata para prácticas',
]


def cargar_productos_png(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    Categoria = apps.get_model('catalogo', 'Categoria')

    # Ocultamos los productos de prueba anteriores (sin borrarlos por si hay pedidos).
    Producto.objects.filter(nombre__in=NOMBRES_ANTIGUOS).update(activo=False, destacado=False)

    categorias = {c.nombre: c for c in Categoria.objects.all()}

    for nombre, cat_nombre, precio, stock, descripcion, slug_img, destacado in PRODUCTOS_PNG:
        categoria = categorias.get(cat_nombre)
        if not categoria:
            continue
        Producto.objects.update_or_create(
            slug=slug_img,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': Decimal(precio),
                'stock': stock,
                'categoria': categoria,
                'activo': True,
                'destacado': destacado,
            },
        )


def revertir(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    slugs = [p[5] for p in PRODUCTOS_PNG]
    Producto.objects.filter(slug__in=slugs).delete()
    Producto.objects.filter(nombre__in=NOMBRES_ANTIGUOS).update(activo=True)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0005_marcar_destacados'),
    ]

    operations = [
        migrations.RunPython(cargar_productos_png, revertir),
    ]
