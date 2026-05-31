"""
Modelos de la app usuarios.

Aquí guardamos información extra del alumno que NO viene en el modelo
User de Django (matrícula, carrera, teléfono).
"""
from django.conf import settings
from django.db import models


class Carrera(models.Model):
    """Carrera universitaria que puede elegir un alumno al registrarse."""

    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PerfilAlumno(models.Model):
    """
    Extiende al usuario de Django con datos propios.

    Aunque el modelo se llama PerfilAlumno, ahora también guarda profesores.
    Se usa el campo `tipo` para distinguirlos. (Se mantiene el nombre por
    compatibilidad con migraciones previas; los profesores no tienen carrera.)
    """

    # Tipos de usuario que pueden registrarse.
    TIPO_ALUMNO = 'ALUMNO'
    TIPO_PROFESOR = 'PROFESOR'
    TIPO_CHOICES = [
        (TIPO_ALUMNO, 'Alumno'),
        (TIPO_PROFESOR, 'Profesor'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_alumno',
    )
    matricula = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default=TIPO_ALUMNO,
    )
    # carrera es OBLIGATORIA para alumnos y OPCIONAL (NULL) para profesores.
    # La validación de "alumno requiere carrera" la hacemos en la vista.
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name='alumnos',
        blank=True,
        null=True,
    )
    telefono = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuarios'
        ordering = ['matricula']

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f'[{self.get_tipo_display()}] {self.matricula} - {nombre}'
