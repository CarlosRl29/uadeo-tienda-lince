/* ==========================================================================
   navbar.js
   Genera el HTML de la barra de navegación y lo inyecta dentro de la
   etiqueta <header id="navbar"></header> que existe en cada página.

   Así no tenemos que copiar y pegar el mismo navbar en cada archivo HTML.
   ========================================================================== */

// Función que devuelve el HTML del navbar como un string.
// La página actual se marca con la clase "navbar__link--activo".
function construirNavbar(paginaActual) {
  // Definimos los enlaces del menú como una lista de objetos.
  // Si en el futuro agregamos un enlace nuevo, lo añadimos aquí y listo.
  var enlaces = [
    { id: 'inicio',    texto: 'Inicio',      url: '/' },
    { id: 'catalogo',  texto: 'Catálogo',    url: '/catalogo/' },
    { id: 'carrito',   texto: 'Carrito',     url: '/carrito/' },
    { id: 'pedidos',   texto: 'Mis pedidos', url: '/mis-pedidos/' },
  ];

  // Construimos los <a> del menú concatenando strings.
  var menuHTML = '';
  for (var i = 0; i < enlaces.length; i++) {
    var enlace = enlaces[i];
    var claseActiva = (enlace.id === paginaActual) ? ' navbar__link--activo' : '';
    // "Mis pedidos" empieza oculto; auth.js lo muestra cuando hay sesión.
    if (enlace.id === 'pedidos') {
      menuHTML += '<a href="' + enlace.url + '" id="nav-pedidos" class="navbar__link oculto' + claseActiva + '">' + enlace.texto + '</a>';
    } else {
      menuHTML += '<a href="' + enlace.url + '" class="navbar__link' + claseActiva + '">' + enlace.texto + '</a>';
    }
  }

  // Plantilla completa del navbar.
  var html =
    '<nav class="navbar__contenedor">' +
      '<a href="/" class="navbar__marca">' +
        '<span class="navbar__logo-icono">L</span>' +
        '<span>UAdeO Tienda Lince</span>' +
      '</a>' +
      '<div class="navbar__menu">' + menuHTML + '</div>' +
      '<div class="navbar__acciones">' +
        // Botón del carrito con un badge que muestra cuántos productos hay.
        '<a href="/carrito/" class="navbar__carrito" title="Ver carrito">' +
          'Carrito ' +
          '<span class="navbar__carrito-badge" id="badge-carrito">0</span>' +
        '</a>' +
        // Acciones para usuarios SIN sesión (las activamos por defecto).
        '<span id="navbar-invitado">' +
          '<a href="/login/" class="btn btn--fantasma">Iniciar sesión</a>' +
          '<a href="/registro/" class="btn btn--primario">Registrarse</a>' +
        '</span>' +
        // Acciones para usuarios CON sesión (ocultas por defecto).
        '<span id="navbar-usuario" class="oculto">' +
          '<span id="navbar-saludo" style="margin-right: 0.5rem;"></span>' +
          '<button type="button" class="btn btn--secundario" id="btn-logout">Cerrar sesión</button>' +
        '</span>' +
      '</div>' +
    '</nav>';

  return html;
}

// Función principal: inyecta el navbar dentro del <header id="navbar">.
// Recibe el id de la página actual para marcar el enlace correspondiente.
function inicializarNavbar(paginaActual) {
  var contenedor = document.getElementById('navbar');
  if (!contenedor) {
    console.warn('No se encontró <header id="navbar"></header> en la página.');
    return;
  }
  contenedor.className = 'navbar';
  contenedor.innerHTML = construirNavbar(paginaActual);

  // Actualizamos el badge del carrito leyendo localStorage.
  actualizarBadgeCarrito();
}

// Lee el carrito de localStorage y actualiza el numerito del navbar.
// Lo dejamos preparado para que cuando hagamos la Fase 5 (carrito) ya funcione.
function actualizarBadgeCarrito() {
  var badge = document.getElementById('badge-carrito');
  if (!badge) return;

  var carrito = [];
  try {
    var datos = localStorage.getItem('carrito_uadeo');
    if (datos) {
      carrito = JSON.parse(datos);
    }
  } catch (e) {
    carrito = [];
  }

  // Sumamos las cantidades de todos los productos.
  var total = 0;
  for (var i = 0; i < carrito.length; i++) {
    total += carrito[i].cantidad || 0;
  }
  badge.textContent = total;
}
