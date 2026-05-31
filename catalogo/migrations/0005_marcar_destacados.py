"""
Data migration: marca los 6 productos iniciales que aparecerán en el
carrusel "Los más vendidos" de la página de inicio.
"""
from django.db import migrations


DESTACADOS = [
    'Playera UAdeO',
    'Sudadera UAdeO',
    'Termo UAdeO',
    'Taza UAdeO',
    'Memoria USB 32GB',
    'Cuaderno universitario',
]


def marcar(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    Producto.objects.filter(nombre__in=DESTACADOS).update(destacado=True)


def desmarcar(apps, schema_editor):
    Producto = apps.get_model('catalogo', 'Producto')
    Producto.objects.filter(nombre__in=DESTACADOS).update(destacado=False)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0004_producto_destacado'),
    ]

    operations = [
        migrations.RunPython(marcar, desmarcar),
    ]
