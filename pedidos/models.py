"""
Modelos de la app pedidos.

Pedido     -> el "apartado" que el alumno confirma desde el carrito.
DetallePedido -> las líneas del pedido (un producto + cantidad + precio).

Reglas importantes:
- En esta versión NO se paga en línea: el pedido nace como "pendiente de pago".
- El alumno paga físicamente en la escuela y el administrador cambia el estado.
"""
import secrets
from decimal import Decimal

from django.conf import settings
from django.db import models

from catalogo.models import Producto


class Pedido(models.Model):
    """Apartado generado por un alumno desde el carrito."""

    # Estados que puede tener un pedido (etiquetas para el admin/UI).
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_PAGADO = 'PAGADO'
    ESTADO_CANCELADO = 'CANCELADO'
    ESTADO_ENTREGADO = 'ENTREGADO'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente de pago'),
        (ESTADO_PAGADO, 'Pagado en escuela'),
        (ESTADO_CANCELADO, 'Cancelado'),
        (ESTADO_ENTREGADO, 'Entregado'),
    ]

    alumno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # conservamos el pedido aunque se borre el usuario
        related_name='pedidos',
    )
    codigo_pedido = models.CharField(max_length=20, unique=True, editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.codigo_pedido} ({self.get_estado_display()})'

    def save(self, *args, **kwargs):
        # Generamos un código corto y legible la primera vez que se guarda.
        # Ej: PED-9F3A2B7C
        if not self.codigo_pedido:
            self.codigo_pedido = f'PED-{secrets.token_hex(4).upper()}'
        super().save(*args, **kwargs)

    def recalcular_total(self):
        """Suma los subtotales de los detalles y guarda el total del pedido."""
        total = sum((d.subtotal for d in self.detalles.all()), Decimal('0.00'))
        self.total = total
        self.save(update_fields=['total'])
        return total


class DetallePedido(models.Model):
    """Línea de un pedido: producto + cantidad + precio en el momento de la compra."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,  # si se borra el pedido, se borran sus detalles
        related_name='detalles',
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,  # no perdemos el detalle si se borra el producto
        related_name='detalles',
    )
    cantidad = models.PositiveIntegerField(default=1)

    # Guardamos el precio en el momento del apartado para no afectar
    # pedidos históricos si más tarde cambia el precio del producto.
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedidos'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
