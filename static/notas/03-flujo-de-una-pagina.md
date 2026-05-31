# 03 - Flujo completo cuando alguien entra a la página

Vamos a seguir paso a paso lo que pasa cuando un alumno escribe
`http://127.0.0.1:8000/` en su navegador.

## Paso 1: el navegador pide la página a Django

```
NAVEGADOR ──► GET /  ──► Django
```

Django revisa `tienda_uadeo/urls.py` y encuentra:

```python
path('', include('catalogo.urls')),
```

Eso le dice: "esta URL la maneja la app catalogo". Luego Django revisa
`catalogo/urls.py` y encuentra:

```python
path('', views.pagina_inicio, name='inicio'),
```

Eso le dice: "ejecuta la función `pagina_inicio`".

## Paso 2: Django ejecuta la vista

```python
def pagina_inicio(request):
    return render(request, 'index.html')
```

`render(request, 'index.html')` busca `index.html` en la carpeta `templates/`
y lo manda al navegador **tal cual**. No le inyecta ningún dato.

## Paso 3: el navegador recibe el HTML

```
Django ──► HTML ──► NAVEGADOR
```

El navegador empieza a leer el HTML de arriba a abajo:

```html
<head>
  <link rel="stylesheet" href="/static/css/styles.css">
</head>
```

→ Ve el `<link>` al CSS y hace otra petición para descargar `styles.css`.

```html
<body data-pagina="catalogo">
  <header id="navbar"></header>  ← vacío
  <main> ... </main>
  <footer id="footer"></footer>  ← vacío

  <script src="/static/js/navbar.js"></script>
  <script src="/static/js/footer.js"></script>
  <script src="/static/js/main.js"></script>
</body>
```

→ Ve los `<script>` y descarga los 3 archivos `.js`.

## Paso 4: los scripts se ejecutan

El orden importa porque `main.js` USA funciones que están definidas en
`navbar.js` y `footer.js`.

1. **`navbar.js`** se ejecuta:
   - Define las funciones `construirNavbar()`, `inicializarNavbar()`,
     `actualizarBadgeCarrito()`.
   - Pero no las llama todavía, solo las deja listas.

2. **`footer.js`** se ejecuta:
   - Define `construirFooter()` e `inicializarFooter()`.
   - Tampoco las llama.

3. **`main.js`** se ejecuta:

```javascript
document.addEventListener('DOMContentLoaded', function () {
  var paginaActual = document.body.getAttribute('data-pagina') || '';
  inicializarNavbar(paginaActual);
  inicializarFooter();
});
```

   - Espera a que el DOM (toda la estructura HTML) esté lista.
   - Lee `data-pagina` del `<body>` → `"catalogo"`.
   - Llama a `inicializarNavbar("catalogo")` → el `<header>` ahora tiene
     toda la barra de navegación.
   - Llama a `inicializarFooter()` → el `<footer>` ahora tiene el pie.

## Paso 5: el usuario ve la página completa

El usuario ve:
- Una barra arriba (navbar) con el logo, los enlaces y los botones.
- El hero con el mensaje de bienvenida.
- Un mensaje provisional donde irán los productos.
- El pie de página abajo.

Todo eso aunque el HTML original estaba "vacío" (los huecos del navbar y footer
los llenó JavaScript).

## En la Fase 4 agregaremos un paso más

```javascript
fetch('/api/productos/')
  .then(respuesta => respuesta.json())
  .then(productos => {
    // ...pintamos las tarjetas dentro de <div id="lista-productos">
  });
```

Eso será un viaje extra al backend, pero solo para los DATOS, no para el HTML.

## Resumen visual

```
1. NAVEGADOR   pide   →  DJANGO  responde con HTML vacío
2. NAVEGADOR   pide   →  CSS    para los estilos
3. NAVEGADOR   pide   →  JS     (navbar.js, footer.js, main.js)
4. main.js   ejecuta  →  llena el navbar y el footer
5. (Fase 4) JS pide  →  API     /api/productos/ → JSON → pinta tarjetas
```
