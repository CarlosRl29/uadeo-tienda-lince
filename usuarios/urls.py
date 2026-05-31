"""
URLs de la app usuarios.

Hay dos grupos:
- Páginas: las que el navegador abre directamente (/registro/, /login/).
- API: las que llama JavaScript con fetch() (/api/...).
"""
from django.urls import path

from . import views

urlpatterns = [
    # Páginas (HTML)
    path('registro/', views.pagina_registro, name='pagina_registro'),
    path('login/', views.pagina_login, name='pagina_login'),

    # API (JSON)
    path('api/carreras/', views.api_carreras, name='api_carreras'),
    path('api/registro/', views.api_registro, name='api_registro'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/me/', views.api_me, name='api_me'),
]
