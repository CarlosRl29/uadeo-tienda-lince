# 07 - Pedidos y confirmación de apartado

Esta nota explica qué pasa cuando el alumno confirma su carrito y cómo
el backend guarda el pedido en la base de datos.

## Flujo completo (de carrito a pedido)

```
1. El alumno tiene productos en localStorage (carrito_uadeo)
2. Hace clic en "Confirmar apartado" en /carrito/
3. carrito.js verifica sesión:
     - Sin sesión → login → vuelve al carrito
     - Con sesión → continúa
4. carrito.js envía POST /api/pedidos/crear/ con:
     { "items": [ { "slug": "playera-uadeo", "cantidad": 2 }, ... ] }
5. Django (api_crear_pedido):
     a. Verifica que el usuario esté logueado
     b. Abre una transacción atómica (transaction.atomic)
     c. Crea el Pedido (estado: PENDIENTE)
     d. Por cada item:
          - Bloquea el producto (select_for_update)
          - Valida stock suficiente
          - Crea DetallePedido con el precio ACTUAL
          - Descuenta stock
     e. Recalcula el total del pedido
     f. Responde JSON con codigo, total, detalles...
6. carrito.js vacía localStorage y redirige a:
     /pedido/PED-XXXXXXXX/confirmacion/
7. confirmacion.js lee el código de la URL y pide
     GET /api/pedidos/PED-XXXXXXXX/ para pintar los datos
```

## ¿Por qué transaction.atomic()?

Imagina que dos alumnos apartan la última playera al mismo tiempo:

- Sin transacción: los dos podrían pasar la validación de stock y el
  stock quedaría en negativo.
- Con `transaction.atomic()` + `select_for_update()`: el segundo alumno
  espera a que termine el primero. Si ya no hay stock, recibe un error claro.

## Endpoints de pedidos

| Método | URL | Quién | Qué hace |
|---|---|---|---|
| POST | `/api/pedidos/crear/` | Alumno logueado | Crea pedido desde el carrito |
| GET | `/api/pedidos/` | Alumno logueado | Lista sus pedidos |
| GET | `/api/pedidos/<codigo>/` | Alumno logueado | Detalle de UN pedido suyo |

Todos devuelven JSON. Las páginas HTML (`/mis-pedidos/`, confirmación)
solo son contenedores; el JS hace las peticiones.

## Modelos involucrados

**Pedido**
- `alumno` → User de Django
- `codigo_pedido` → generado automáticamente (PED-9F3A2B7C)
- `total` → suma de subtotales
- `estado` → PENDIENTE / PAGADO / CANCELADO / ENTREGADO
- `fecha_creacion`

**DetallePedido**
- `pedido` → FK al Pedido
- `producto` → FK al Producto
- `cantidad`
- `precio_unitario` → precio **en el momento del apartado**

Guardamos el precio en el detalle para que si mañana sube el precio de
la playera, los pedidos viejos sigan mostrando lo que el alumno acordó.

## Estados del pedido

| Código | Etiqueta | Significado |
|---|---|---|
| PENDIENTE | Pendiente de pago | Recién creado, falta pagar en escuela |
| PAGADO | Pagado en escuela | El admin confirmó el pago en caja |
| CANCELADO | Cancelado | Se canceló (sin entrega) |
| ENTREGADO | Entregado | Ya se entregó al alumno |

El alumno **no** cambia estados desde la tienda. Eso lo hace el
administrador desde Django Admin.

## Seguridad

- Solo usuarios logueados pueden crear o ver pedidos.
- `api_pedido_detalle` filtra por `alumno=request.user`: un alumno no
  puede ver el pedido de otro aunque adivine el código.
- El frontend manda solo `slug` y `cantidad`. El backend recalcula
  precios y valida stock; no confiamos en lo que diga localStorage.

## Páginas nuevas

| URL | Archivo HTML | JS |
|---|---|---|
| `/mis-pedidos/` | mis-pedidos.html | mis-pedidos.js |
| `/pedido/<codigo>/confirmacion/` | confirmacion.html | confirmacion.js |

## Navbar: "Mis pedidos"

El enlace `#nav-pedidos` empieza oculto (`oculto`). Cuando `auth.js`
detecta sesión activa, lo muestra. Si no hay sesión, no aparece.

## Qué probar manualmente

1. Inicia sesión con una cuenta de alumno.
2. Agrega 2-3 productos al carrito.
3. Ve a `/carrito/` → **Confirmar apartado**.
4. Deberías llegar a la página de confirmación con tu código `PED-...`.
5. El badge del carrito debe volver a **0** (localStorage vacío).
6. Ve a **Mis pedidos** → aparece el pedido con estado "Pendiente de pago".
7. En Django Admin (`/admin/pedidos/pedido/`) el admin puede cambiar
   el estado a "Pagado en escuela" o "Entregado".
8. Intenta apartar más unidades de las que hay en stock → debe mostrar
   error en un toast rojo.
