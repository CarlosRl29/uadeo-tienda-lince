"""
URLs de la app pedidos.

Páginas:
  /carrito/
  /mis-pedidos/
  /pedido/<codigo>/confirmacion/

API:
  GET  /api/pedidos/              -> listar mis pedidos
  POST /api/pedidos/crear/        -> confirmar apartado
  GET  /api/pedidos/<codigo>/     -> detalle de un pedido
"""
from django.urls import path

from . import views

urlpatterns = [
    path('carrito/', views.pagina_carrito, name='pagina_carrito'),
    path('mis-pedidos/', views.pagina_mis_pedidos, name='pagina_mis_pedidos'),
    path(
        'pedido/<str:codigo>/confirmacion/',
        views.pagina_confirmacion,
        name='pagina_confirmacion',
    ),

    # "crear" va ANTES de <codigo> para que Django no lo confunda con un código.
    path('api/pedidos/crear/', views.api_crear_pedido, name='api_crear_pedido'),
    path('api/pedidos/<str:codigo>/', views.api_pedido_detalle, name='api_pedido_detalle'),
    path('api/pedidos/', views.api_mis_pedidos, name='api_mis_pedidos'),
]
