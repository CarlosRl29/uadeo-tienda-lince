"""
Panel admin para Pedido y DetallePedido.

El administrador podrá ver todos los pedidos y cambiar su estado
(pendiente -> pagado en escuela -> entregado).
"""
from django.contrib import admin

from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    """Muestra los productos del pedido dentro de la página del pedido."""
    model = DetallePedido
    extra = 0
    autocomplete_fields = ('producto',)
    readonly_fields = ('subtotal_display',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.pk:
            return obj.subtotal
        return '-'
    subtotal_display.short_description = 'Subtotal'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo_pedido', 'alumno', 'total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('codigo_pedido', 'alumno__username', 'alumno__email')
    readonly_fields = ('codigo_pedido', 'fecha_creacion', 'total')
    list_editable = ('estado',)
    autocomplete_fields = ('alumno',)
    inlines = [DetallePedidoInline]
    date_hierarchy = 'fecha_creacion'


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('pedido__codigo_pedido', 'producto__nombre')
    autocomplete_fields = ('pedido', 'producto')
