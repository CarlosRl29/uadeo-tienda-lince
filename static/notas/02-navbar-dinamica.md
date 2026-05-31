# 02 - Navbar dinámica (cómo funciona la inyección con JS)

## El problema que resuelve

Si copiamos el navbar (menú de arriba) en CADA archivo HTML:
- Hay 10 páginas → 10 copias del mismo navbar.
- Si cambiamos un enlace, hay que cambiarlo 10 veces.
- Si nos equivocamos en una página, esa queda diferente y se ve mal.

**Solución:** escribir el navbar UNA sola vez en JavaScript y dejar que el
navegador lo "pegue" automáticamente en cada página.

## Las tres piezas que lo hacen funcionar

### 1) En cada archivo HTML hay un "hueco" vacío

Mira el `index.html`:

```html
<header id="navbar"></header>
```

Ese `<header>` está vacío a propósito. Es solo un punto de anclaje, como
diciendo: "aquí va a entrar la navbar". El `id="navbar"` es la etiqueta que
JavaScript va a buscar.

Lo mismo pasa con el footer:

```html
<footer id="footer"></footer>
```

### 2) En el `<body>` decimos qué página somos

```html
<body data-pagina="catalogo">
```

`data-pagina` es un atributo personalizado de HTML5 (cualquier atributo que
empieza con `data-` es válido). Sirve para que el JS sepa en qué página
estamos y pueda marcar el enlace correspondiente del menú como activo.

Valores que usaremos:
- `catalogo` → para la página de inicio (catálogo)
- `carrito`  → para `/carrito/`
- `pedidos`  → para `/mis-pedidos/`
- `login`    → para `/login/`
- etc.

### 3) Los scripts se cargan al final del `<body>`

```html
<script src="/static/js/navbar.js"></script>
<script src="/static/js/footer.js"></script>
<script src="/static/js/main.js"></script>
```

El orden importa:
1. `navbar.js` define la función `inicializarNavbar()`.
2. `footer.js` define la función `inicializarFooter()`.
3. `main.js` ESPERA a que el HTML esté listo, lee `data-pagina` y llama a
   las dos funciones anteriores para que pinten su contenido.

## Lo que hace `main.js` paso a paso

```javascript
document.addEventListener('DOMContentLoaded', function () {
  var paginaActual = document.body.getAttribute('data-pagina') || '';
  inicializarNavbar(paginaActual);
  inicializarFooter();
});
```

Traducción a español:

1. **"Cuando el HTML termine de cargar..."**
   (`DOMContentLoaded` significa exactamente eso).
2. **"...lee el atributo `data-pagina` del `<body>`."**
   Por ejemplo, devuelve `"catalogo"`.
3. **"Llama a `inicializarNavbar("catalogo")`."**
4. **"Llama a `inicializarFooter()`."**

## Lo que hace `inicializarNavbar(paginaActual)` paso a paso

```javascript
function inicializarNavbar(paginaActual) {
  var contenedor = document.getElementById('navbar');
  contenedor.className = 'navbar';
  contenedor.innerHTML = construirNavbar(paginaActual);
  actualizarBadgeCarrito();
}
```

1. Busca el `<header id="navbar">` (el "hueco" vacío).
2. Le pone la clase CSS `navbar` para que tenga los estilos.
3. Construye el HTML del navbar como un string gigante y lo mete adentro
   con `innerHTML`.
4. Actualiza el numerito del carrito leyendo `localStorage`.

## Lo que hace `construirNavbar(paginaActual)`

Es la "plantilla" del navbar pero en formato JavaScript. Se ven cosas como:

```javascript
var enlaces = [
  { id: 'catalogo',  texto: 'Catálogo',    url: '/' },
  { id: 'carrito',   texto: 'Carrito',     url: '/carrito/' },
  { id: 'pedidos',   texto: 'Mis pedidos', url: '/mis-pedidos/' },
];
```

Y luego un `for` que recorre cada enlace y genera un `<a>`:

```javascript
for (var i = 0; i < enlaces.length; i++) {
  var enlace = enlaces[i];
  var claseActiva = (enlace.id === paginaActual) ? ' navbar__link--activo' : '';
  menuHTML += '<a href="' + enlace.url + '" class="navbar__link' + claseActiva + '">' + enlace.texto + '</a>';
}
```

La línea importante:

```javascript
var claseActiva = (enlace.id === paginaActual) ? ' navbar__link--activo' : '';
```

Eso es un **operador ternario**. Se lee así:

> Si `enlace.id` es igual a `paginaActual`, agrega la clase
> `navbar__link--activo`. Si no, no agregues nada.

Resultado: el enlace de la página donde estamos se ve subrayado en rojo vino.

## ¿Cómo agregar un nuevo enlace al menú?

Súper sencillo, solo tocas el array de `enlaces` en `navbar.js`:

```javascript
var enlaces = [
  { id: 'catalogo',  texto: 'Catálogo',    url: '/' },
  { id: 'carrito',   texto: 'Carrito',     url: '/carrito/' },
  { id: 'pedidos',   texto: 'Mis pedidos', url: '/mis-pedidos/' },
  { id: 'ayuda',     texto: 'Ayuda',       url: '/ayuda/' },  // ← nuevo
];
```

Y se ve actualizado en TODAS las páginas. Ese es el beneficio de la inyección dinámica.

## Diagrama resumen

```
index.html                        navbar.js
┌────────────────────┐            ┌──────────────────────────┐
│ <header id="navbar"│            │ function construirNavbar │
│         ></header> │            │  (devuelve string HTML)  │
│                    │ ────────►  │                          │
│ <script src=       │  llamada   │ function inicializarNavbar│
│  "navbar.js">      │            │  (mete el HTML adentro)  │
│ <script src=       │            │                          │
│  "main.js">        │            │ function actualizarBadge │
└────────────────────┘            └──────────────────────────┘
        │
        │ main.js arranca cuando el DOM está listo
        ▼
   navbar pintada
```
