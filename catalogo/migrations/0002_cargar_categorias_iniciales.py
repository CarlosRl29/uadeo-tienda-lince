"""
Data migration: carga las categorías iniciales de la tienda UAdeO Lince.
"""
from django.db import migrations
from django.utils.text import slugify


CATEGORIAS = [
    'Identidad UAdeO',
    'Papelería',
    'Prácticas',
    'Tecnología',
    'Uniformes',
    'Útiles',
]


def crear_categorias(apps, schema_editor):
    Categoria = apps.get_model('catalogo', 'Categoria')
    for nombre in CATEGORIAS:
        Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'slug': slugify(nombre), 'activa': True},
        )


def eliminar_categorias(apps, schema_editor):
    Categoria = apps.get_model('catalogo', 'Categoria')
    Categoria.objects.filter(nombre__in=CATEGORIAS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_categorias, eliminar_categorias),
    ]
