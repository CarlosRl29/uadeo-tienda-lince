# 05 - Catálogo y fetch: cómo se pinta una lista de productos

Esta nota explica cómo el navegador y Django se ponen de acuerdo para
mostrar la lista de productos, los filtros por categoría y el buscador.

## Visión general

```
┌──────────────────────────────────┐
│  index.html  (HTML vacío)        │
│                                  │
│  <input id="input-busqueda">     │
│  <div id="filtros-categorias">   │
│  <div id="lista-productos">      │
└─────────────┬────────────────────┘
              │  productos.js arranca cuando carga el DOM
              ▼
┌──────────────────────────────────┐
│  fetch /api/categorias/          │ → pinta los botones de filtro
│  fetch /api/productos/           │ → pinta las tarjetas
└──────────────────────────────────┘
              │  el usuario teclea o hace clic en una categoría
              ▼
┌──────────────────────────────────┐
│  fetch /api/productos/?categoria= │
│            &q=...                 │ → vuelve a pintar las tarjetas
└──────────────────────────────────┘
```

## Endpoints nuevos en esta fase

| Método | URL | Qué hace |
|---|---|---|
| `GET` | `/api/categorias/` | Lista de categorías activas (id, nombre, slug). |
| `GET` | `/api/productos/` | Lista de productos. Acepta filtros opcionales en la URL. |
| `GET` | `/api/productos/<slug>/` | Detalle de un producto por su slug. |

### Filtros del listado

La URL del listado acepta dos parámetros opcionales:

| Parámetro | Ejemplo | Efecto |
|---|---|---|
| `categoria` | `/api/productos/?categoria=papeleria` | Solo muestra productos de esa categoría. |
| `q` | `/api/productos/?q=playera` | Busca en nombre y descripción. |

Y se pueden combinar:
```
/api/productos/?categoria=identidad-uadeo&q=termo
```

## Cómo lo arma JavaScript

### Estado del catálogo

```javascript
var estadoCatalogo = {
  categoria: '',  // '' = todas
  texto: '',      // texto del buscador
};
```

Es un objeto simple. Cualquier interacción que cambie esto vuelve a llamar
a `cargarProductos()`. Es el patrón "datos → vista" en su forma más simple.

### Debounce del buscador

Si llamáramos a la API cada vez que el usuario teclea una letra, en buscar
"playera" mandaríamos 7 peticiones. Mal.

Solución: esperar 300 ms desde la última tecla.

```javascript
input.addEventListener('input', function () {
  estadoCatalogo.texto = input.value.trim();
  clearTimeout(timerBusqueda);
  timerBusqueda = setTimeout(cargarProductos, 300);
});
```

`clearTimeout` cancela el timer anterior. Si tecleas rápido, solo se ejecuta
el último. Es una técnica que vas a usar muchísimo en frontend.

### Cómo armamos la URL con filtros

```javascript
var params = [];
if (estadoCatalogo.categoria) params.push('categoria=' + encodeURIComponent(estadoCatalogo.categoria));
if (estadoCatalogo.texto)     params.push('q=' + encodeURIComponent(estadoCatalogo.texto));
var url = '/api/productos/' + (params.length ? '?' + params.join('&') : '');
```

`encodeURIComponent` convierte caracteres especiales (espacios, acentos) en
formato URL para que el servidor los reciba bien.

### Cómo pintamos las tarjetas

Para cada producto generamos un string HTML y lo concatenamos:

```javascript
var html = '';
for (var i = 0; i < productos.length; i++) {
  html += tarjetaProducto(productos[i]);
}
contenedor.innerHTML = html;
```

Una sola asignación a `innerHTML` al final → más rápido que agregar uno por uno.

### Placeholder cuando no hay imagen

Algunos productos pueden no tener imagen aún (porque el admin no la subió).
En vez de mostrar un ícono de imagen rota, generamos un bloque con las
primeras 2 letras del nombre:

```javascript
if (p.imagen) {
  imagenHTML = '<img src="' + p.imagen + '" ...>';
} else {
  imagenHTML = '<div class="tarjeta__imagen tarjeta__imagen--vacia">' +
                 p.nombre.substring(0, 2).toUpperCase() +
               '</div>';
}
```

Y el CSS le pone un degradado bonito:

```css
.tarjeta__imagen--vacia {
  background: linear-gradient(135deg, var(--color-vino) 0%, var(--color-vino-claro) 100%);
  color: var(--color-blanco);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 700;
}
```

## Página de detalle: cómo sabe qué producto mostrar

La URL es `/producto/<slug>/`. JavaScript lee el slug así:

```javascript
function obtenerSlugDeURL() {
  var partes = window.location.pathname.split('/').filter(function (p) { return p; });
  // /producto/playera-uadeo/ → ["producto", "playera-uadeo"]
  if (partes.length >= 2 && partes[0] === 'producto') {
    return partes[1];
  }
  return '';
}
```

Después llama a `/api/productos/<slug>/` y pinta el detalle.

> Nota: la **vista de Django** `pagina_producto` también valida que el slug
> existe antes de servir el HTML. Si no existe, devuelve 404 directamente
> (sin esperar a que JS lo descubra). Es una defensa extra del lado servidor.

## Seguridad pequeña: escapar HTML

Si un producto se llamara `<script>alert("hola")</script>`, al meterlo con
`innerHTML` se ejecutaría. Por eso la función `escapar()`:

```javascript
function escapar(texto) {
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
```

Convierte caracteres especiales en su forma "inocente". Cualquier cosa que
venga del backend y se pinte como HTML pasa por aquí.

## Resumen

| Pregunta | Respuesta |
|---|---|
| ¿Cuándo llamamos al API? | Al cargar la página y cada vez que cambia un filtro. |
| ¿Cómo evitamos saturar el servidor al teclear? | Debounce de 300 ms. |
| ¿Cómo combinamos filtros? | Construyendo la URL `?categoria=...&q=...`. |
| ¿Cómo manejamos productos sin imagen? | Placeholder con las iniciales. |
| ¿Cómo evitamos inyección de HTML? | Pasando todo texto por `escapar()`. |
