"""
Data migration: carga las carreras iniciales que ofrece la UAdeO
Región El Fuerte en modalidad semiescolarizada.
"""
from django.db import migrations


CARRERAS = [
    'Administración de Empresas',
    'Administración y Desarrollo Rural',
    'Ciencias de la Comunicación',
    'Derecho y Ciencias Sociales',
    'Psicología',
    'Ingeniería de Software',
]


def crear_carreras(apps, schema_editor):
    Carrera = apps.get_model('usuarios', 'Carrera')
    for nombre in CARRERAS:
        Carrera.objects.get_or_create(nombre=nombre, defaults={'activa': True})


def eliminar_carreras(apps, schema_editor):
    Carrera = apps.get_model('usuarios', 'Carrera')
    Carrera.objects.filter(nombre__in=CARRERAS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_carreras, eliminar_carreras),
    ]
