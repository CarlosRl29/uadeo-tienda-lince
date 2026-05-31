"""
Configuración del panel admin para la app usuarios.

Mostramos el PerfilAlumno como un "inline" dentro del usuario,
para que al crear un usuario también podamos llenar su matrícula y carrera.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Carrera, PerfilAlumno


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)


class PerfilAlumnoInline(admin.StackedInline):
    """Permite editar el PerfilAlumno desde la página del User."""
    model = PerfilAlumno
    can_delete = False
    verbose_name_plural = 'Perfil de alumno'
    fk_name = 'usuario'


class UsuarioConPerfilAdmin(UserAdmin):
    """Reemplaza el admin estándar de User para mostrar el perfil dentro."""
    inlines = (PerfilAlumnoInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_matricula')

    def get_matricula(self, obj):
        # getattr con fallback evita errores si el usuario aún no tiene perfil.
        perfil = getattr(obj, 'perfil_alumno', None)
        return perfil.matricula if perfil else '-'
    get_matricula.short_description = 'Matrícula'


# Desregistramos el UserAdmin por defecto y registramos el nuestro.
admin.site.unregister(User)
admin.site.register(User, UsuarioConPerfilAdmin)


@admin.register(PerfilAlumno)
class PerfilAlumnoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'tipo', 'usuario', 'carrera', 'telefono')
    list_filter = ('tipo', 'carrera')
    search_fields = ('matricula', 'usuario__username', 'usuario__first_name', 'usuario__last_name')
    autocomplete_fields = ('usuario', 'carrera')
