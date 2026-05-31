"""Panel admin para Categoria y Producto."""
from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)
    # Autocompleta el slug a partir del nombre mientras el admin escribe.
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'activo', 'destacado', 'fecha_creacion')
    list_filter = ('categoria', 'activo', 'destacado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'activo', 'destacado')
    prepopulated_fields = {'slug': ('nombre',)}
    autocomplete_fields = ('categoria',)
    readonly_fields = ('fecha_creacion',)
