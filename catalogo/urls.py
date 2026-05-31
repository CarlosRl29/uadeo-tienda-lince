"""
URLs de la app catalogo.

Páginas:
  /                         → catálogo (lista de productos)
  /producto/<slug>/         → detalle del producto

API (JSON):
  GET /api/categorias/             → lista de categorías
  GET /api/productos/              → lista de productos (acepta ?categoria= y ?q=)
  GET /api/productos/<slug>/       → detalle de un producto
"""
from django.urls import path

from . import views

urlpatterns = [
    # Páginas
    path('', views.pagina_inicio, name='inicio'),
    path('catalogo/', views.pagina_catalogo, name='catalogo'),
    path('producto/<slug:slug>/', views.pagina_producto, name='pagina_producto'),

    # API
    path('api/categorias/', views.api_categorias, name='api_categorias'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/productos/<slug:slug>/', views.api_producto_detalle, name='api_producto_detalle'),
]
