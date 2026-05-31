/* ==========================================================================
   main.js
   Se carga en TODAS las páginas. Su trabajo es:
     1. Pintar el navbar y el footer (las inyecciones)
     2. Marcar el enlace de la página actual como activo
     3. Verificar si hay sesión iniciada y actualizar la navbar en consecuencia

   ¿Cómo sabe cuál es la página actual?
   La página le dice su nombre con:
     <body data-pagina="catalogo">
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Leemos el atributo "data-pagina" del <body> para saber dónde estamos.
  var paginaActual = document.body.getAttribute('data-pagina') || '';

  // 2. Inyectamos navbar y footer en sus huecos.
  inicializarNavbar(paginaActual);
  inicializarFooter();

  // 3. Preguntamos al backend si hay sesión y mostramos lo correspondiente.
  //    Si la función no existe (alguna página no carga auth.js) lo ignoramos.
  if (typeof verificarSesion === 'function') {
    verificarSesion();
  }
});
