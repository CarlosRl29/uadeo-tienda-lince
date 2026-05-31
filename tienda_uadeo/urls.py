"""
URLs principales del proyecto UAdeO Tienda Lince.

Aquí solo se conectan:
- El panel de administración
- Las URLs de cada app (usuarios, catalogo, pedidos)
- El servidor de archivos media en modo desarrollo
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # App catalogo: incluye la página de inicio (/).
    path('', include('catalogo.urls')),

    # App usuarios: /registro/, /login/ y endpoints /api/...
    path('', include('usuarios.urls')),

    # App pedidos: /carrito/ (y en la Fase 6 también /mis-pedidos/ y APIs).
    path('', include('pedidos.urls')),
]

# En desarrollo, servimos los archivos subidos (media) desde Django.
# En producción esto lo hace el servidor web (Nginx, Apache, etc.).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'catalogo.views.pagina_no_encontrada'
