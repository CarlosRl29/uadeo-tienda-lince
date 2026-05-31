"""
Serializers de la app pedidos.
"""
from django.db import transaction
from rest_framework import serializers

from catalogo.models import Producto

from .models import DetallePedido, Pedido


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='producto.nombre', read_only=True)
    slug = serializers.CharField(source='producto.slug', read_only=True)
    precio_unitario = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True,
    )

    class Meta:
        model = DetallePedido
        fields = ['producto', 'slug', 'cantidad', 'precio_unitario', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(source='codigo_pedido', read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=True,
    )
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)
    fecha = serializers.SerializerMethodField()
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['codigo', 'total', 'estado', 'estado_texto', 'fecha', 'detalles']

    def get_fecha(self, pedido):
        return pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')


class ItemCarritoSerializer(serializers.Serializer):
    slug = serializers.CharField()
    cantidad = serializers.IntegerField(min_value=1)


class CrearPedidoSerializer(serializers.Serializer):
    """Valida el carrito que llega del frontend y crea el pedido en la BD."""

    items = ItemCarritoSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('No hay productos válidos en el carrito.')
        return items

    def create(self, validated_data):
        user = self.context['request'].user
        items = validated_data['items']

        # Agrupamos por slug por si el frontend manda duplicados.
        cantidades = {}
        for item in items:
            slug = item['slug'].strip()
            cantidades[slug] = cantidades.get(slug, 0) + item['cantidad']

        try:
            with transaction.atomic():
                pedido = Pedido.objects.create(alumno=user)

                for slug, cantidad in cantidades.items():
                    try:
                        producto = (
                            Producto.objects
                            .select_for_update()
                            .get(slug=slug, activo=True)
                        )
                    except Producto.DoesNotExist:
                        raise serializers.ValidationError(
                            f'El producto "{slug}" ya no está disponible.'
                        )

                    if producto.stock < cantidad:
                        raise serializers.ValidationError(
                            f'Stock insuficiente para "{producto.nombre}". '
                            f'Disponible: {producto.stock}, solicitado: {cantidad}.'
                        )

                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                    )

                    producto.stock -= cantidad
                    producto.save(update_fields=['stock'])

                pedido.recalcular_total()

        except serializers.ValidationError:
            raise

        return pedido
