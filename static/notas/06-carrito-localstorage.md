# 06 - Carrito con localStorage

Esta nota explica por qué el carrito vive **en el navegador** y no en la
base de datos, y cómo lo manejamos.

## ¿Qué es localStorage?

Es un "almacén" que cada navegador (Chrome, Firefox, Edge) le da a cada
sitio web. Sirve para guardar texto que **sobrevive entre recargas y
sesiones**.

```javascript
localStorage.setItem('clave', 'valor');           // guardar
var valor = localStorage.getItem('clave');         // leer
localStorage.removeItem('clave');                  // borrar uno
localStorage.clear();                              // borrar todo
```

Limitaciones:
- Solo guarda **strings**. Para guardar objetos usamos `JSON.stringify` y
  `JSON.parse`.
- Capacidad: típicamente 5-10 MB (más que suficiente para un carrito).
- Es **por dominio**. El localStorage de `tienda-uadeo.com` no se ve desde
  `otra-pagina.com`.
- Es **por navegador**. El carrito que guardas en Chrome no aparece en
  Firefox. Tampoco si abres ventana incógnita.

## ¿Por qué no guardarlo en la base de datos?

Podríamos, pero tendría desventajas para este caso:

| En la BD | En localStorage |
|---|---|
| Necesita estar logueado para tener carrito | El alumno puede ir agregando antes de logearse |
| Cada cambio (+/-) es una llamada al servidor | Todo es instantáneo |
| Más código en el backend | El backend solo recibe el pedido al confirmar |
| Más responsabilidad para el servidor | Más ligero |

La regla: usa localStorage para datos **temporales y locales** (carrito,
preferencias visuales, borrador de formulario). Usa la BD para datos
**permanentes y compartidos** (pedidos confirmados, productos, usuarios).

## Cómo guardamos el carrito

Bajo la clave `"carrito_uadeo"` guardamos un **array de items** convertido
a JSON:

```json
[
  {
    "slug": "playera-uadeo",
    "nombre": "Playera UAdeO",
    "precio": "220.00",
    "imagen": "http://127.0.0.1:8000/media/productos/playera.png",
    "stock": 30,
    "cantidad": 2
  },
  {
    "slug": "termo-uadeo",
    "nombre": "Termo UAdeO",
    "precio": "260.00",
    "imagen": "",
    "stock": 20,
    "cantidad": 1
  }
]
```

¿Por qué guardamos también `nombre`, `precio` e `imagen` (y no solo el slug)?
Para que la página del carrito se pinte **sin necesidad de pedir nada al
servidor**. Más rápido, funciona aunque la conexión esté lenta.

¿Y si el precio cambia mientras está en el carrito? El alumno verá el precio
viejo en su carrito, pero al confirmar el apartado (Fase 6) el backend
recalcula con el precio actual.

## Funciones que expone `carrito.js`

```javascript
obtenerCarrito()                                 // → array
guardarCarrito(carrito)                          // guarda y actualiza badge
agregarAlCarrito({slug, nombre, precio, imagen, stock}, cantidad)
quitarDelCarrito(slug)
cambiarCantidad(slug, nuevaCantidad)
vaciarCarrito()

totalProductos(carrito)                          // → número de items
totalDinero(carrito)                             // → número decimal

mostrarToast(mensaje, tipo)                      // tipo: 'exito', 'error', 'info'
```

## El badge del navbar

El número que aparece a un lado del icono del carrito en el navbar:

1. El navbar (`navbar.js`) tiene la función `actualizarBadgeCarrito()` que
   lee `localStorage` y suma todas las cantidades.
2. Cada vez que `carrito.js` modifica el carrito (`guardarCarrito`), llama a
   esa función. El número se actualiza al instante.

## Flujo: el alumno agrega un producto al carrito

```
1. Está en /producto/playera-uadeo/
2. Hace clic en "Agregar al carrito"
3. producto-detalle.js llama a:
     agregarAlCarrito({slug: "playera-uadeo", nombre: "...", precio: "220.00", ...}, 1)
4. carrito.js revisa si la playera ya está en el carrito:
     - Si NO: la agrega como item nuevo
     - Si SÍ: suma 1 a su cantidad (sin pasar del stock)
5. Guarda el carrito en localStorage
6. Llama a actualizarBadgeCarrito() → el badge del navbar pasa de "0" a "1"
7. Muestra un toast verde: "Agregado al carrito."
```

## Flujo: el alumno va a /carrito/

```
1. carrito.html se carga. Su <body data-pagina="carrito">.
2. carrito.js arranca cuando DOMContentLoaded.
3. Detecta el id "carrito-items" → sabe que está en la página del carrito.
4. Llama a renderizarCarrito():
     - Lee localStorage
     - Si vacío: muestra el div #carrito-vacio
     - Si tiene items: muestra el layout con la lista + el resumen
5. Para cada item pinta:
     - Imagen (o placeholder con iniciales)
     - Nombre y precio unitario
     - Selector de cantidad (- número +)
     - Subtotal
     - Botón × para quitar
6. Para los botones de cada item conecta listeners (+, -, input, quitar).
7. Actualiza "Productos: N" y "Total: $X" en el resumen.
```

## Flujo: confirmar el apartado (preview de Fase 6)

```
1. Alumno hace clic en "Confirmar apartado"
2. carrito.js revisa si hay sesión (usuarioActual):
     - NO hay sesión:
         * Guarda "/carrito/" en sessionStorage['volver_a']
         * Muestra toast: "Inicia sesión para confirmar..."
         * Redirige a /login/
         * Cuando el alumno inicia sesión, login.js lee 'volver_a' y
           lo manda de vuelta al carrito.
     - SÍ hay sesión:
         * (Fase 6) envía POST /api/pedidos/ con el contenido del carrito
         * Recibe el código del pedido (PED-9F3A2B7C)
         * Vacía el carrito local
         * Redirige a la página de confirmación
```

## sessionStorage vs localStorage

| | localStorage | sessionStorage |
|---|---|---|
| Sobrevive cerrar el navegador | Sí | No |
| Para qué lo usamos | Carrito | "Volver a esta página después de login" |

`sessionStorage` se borra solo cuando el alumno cierra la pestaña, así que
es perfecto para datos transitorios como "vuelve aquí después de logearte".

## ¿Cómo veo el carrito desde DevTools?

1. F12 → pestaña **Application** (Chrome) o **Almacenamiento** (Firefox).
2. En la izquierda: **Local Storage → http://127.0.0.1:8000**.
3. Ahí verás la clave `carrito_uadeo` con el JSON adentro.
4. Puedes editarlo manualmente para hacer pruebas (cambiar cantidades,
   borrar el carrito completo, etc.).
