# 09 - Serializers con Django REST Framework (DRF)

A partir de esta fase, las **APIs JSON** del proyecto usan **serializers**
de Django REST Framework en lugar de convertir modelos a dict a mano.

## ¿Qué es DRF?

**Django REST Framework** es una librería que se instala encima de Django
para construir APIs. Lo más importante para nosotros: los **serializers**.

```
pip install djangorestframework
```

En `settings.py` agregamos `'rest_framework'` a `INSTALLED_APPS`.

## ¿Qué hace un serializer?

| Dirección | Qué hace |
|---|---|
| **Salida** (Model → JSON) | Lee un `Producto` y devuelve `{ "nombre": "...", "precio": "220.00" }` |
| **Entrada** (JSON → validado) | Recibe datos del frontend, valida y crea/actualiza en la BD |

Antes lo hacíamos manual:

```python
def _producto_a_dict(producto, request):
    return {'nombre': producto.nombre, ...}
```

Ahora:

```python
serializer = ProductoSerializer(producto, context={'request': request})
return Response({'producto': serializer.data})
```

## Archivos nuevos por app

| App | Archivo | Serializers |
|---|---|---|
| `catalogo` | `serializers.py` | `CategoriaSerializer`, `ProductoSerializer` |
| `usuarios` | `serializers.py` | `CarreraSerializer`, `UsuarioSerializer`, `RegistroSerializer`, `LoginSerializer` |
| `pedidos` | `serializers.py` | `DetallePedidoSerializer`, `PedidoSerializer`, `CrearPedidoSerializer` |

## Ejemplo: ProductoSerializer

```python
class ProductoSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen = serializers.SerializerMethodField()
    disponible = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'slug', 'precio', ...]

    def get_imagen(self, producto):
        request = self.context.get('request')
        return url_imagen_producto(producto, request)
```

- `ModelSerializer`: genera campos automáticos desde el modelo.
- `source='categoria.nombre'`: lee un campo relacionado.
- `SerializerMethodField`: campo calculado (imagen URL, disponible).

## Ejemplo: RegistroSerializer (entrada + create)

```python
class RegistroSerializer(serializers.Serializer):
    matricula = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    ...

    def validate_matricula(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Ya existe esa matrícula.')
        return value

    def create(self, validated_data):
        # Crea User + PerfilAlumno
        return user
```

En la view:

```python
serializer = RegistroSerializer(data=request.data)
if serializer.is_valid():
    user = serializer.save()
```

## Vistas con @api_view

Seguimos usando **funciones** (no ViewSets) para que sea más fácil de leer:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_productos(request):
    ...
    return Response({'productos': serializer.data})
```

`@api_view` reemplaza `@require_GET` / `@require_POST` de Django.

## ¿Cambió el frontend?

**No.** El JavaScript sigue igual. Los endpoints devuelven el mismo JSON:

- `{ "productos": [...], "total": 12 }`
- `{ "ok": true, "usuario": {...} }`
- `{ "ok": false, "error": "mensaje" }`

Solo cambió **cómo** Django arma ese JSON por dentro.

## Autenticación y CSRF

En `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

Usamos la **misma sesión** que el login normal. El JS sigue mandando
`X-CSRFToken` en los POST con `api.js`.

## Flujo completo (registro)

```
1. JS: POST /api/registro/ con JSON
2. View: RegistroSerializer(data=request.data)
3. Serializer valida campos (validate_*, validate)
4. serializer.save() → create() → User + PerfilAlumno
5. UsuarioSerializer(user).data → JSON de respuesta
6. JS recibe { ok: true, usuario: {...} }
```

## Helpers compartidos

`tienda_uadeo/api_utils.py` tiene funciones para errores uniformes:

- `respuesta_error(mensaje, status)` → `{ ok: false, error: "..." }`
- `respuesta_error_serializer(serializer)` → primer error del serializer

## Qué NO usamos (a propósito)

Para mantener el proyecto entendible en 4° semestre **no** usamos aún:

- ViewSets / Routers automáticos
- TokenAuthentication / JWT
- Browsable API en producción

Eso se ve en cursos más avanzados. Aquí solo serializers + `@api_view`.
