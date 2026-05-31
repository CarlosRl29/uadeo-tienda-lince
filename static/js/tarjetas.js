/* ==========================================================================
   tarjetas.js
   Funciones compartidas para mostrar productos.
   Se usa en home.js (carrusel), productos.js (catálogo) y donde haga falta.

   Expone dos funciones globales:
     - tarjetaProducto(p)  → devuelve string HTML de UNA tarjeta de producto
     - escapar(texto)      → previene inyección de HTML
   ========================================================================== */

// Devuelve el HTML de UNA tarjeta de producto.
// opciones.mostrarBotonCarrito = true agrega el botón "Agregar al carrito".
function tarjetaProducto(p, opciones) {
  opciones = opciones || {};
  var imagenHTML;
  if (p.imagen) {
    imagenHTML = '<img src="' + p.imagen + '" alt="' + escapar(p.nombre) +
                 '" class="tarjeta__imagen">';
  } else {
    imagenHTML = '<div class="tarjeta__imagen tarjeta__imagen--vacia">' +
                   escapar(p.nombre.substring(0, 2).toUpperCase()) +
                 '</div>';
  }

  var precioStr = '$' + Number(p.precio).toFixed(2);
  var disponibilidad = p.disponible
    ? '<small style="color: var(--color-gris-texto);">' + p.stock + ' en stock</small>'
    : '<small style="color: var(--color-error);">Agotado</small>';

  var botonHTML = '';
  if (opciones.mostrarBotonCarrito && p.disponible) {
    botonHTML =
      '<div class="tarjeta__pie">' +
        '<button type="button" class="btn btn--secundario btn--bloque btn--pequeno tarjeta__btn-carrito" ' +
          'data-slug="' + escapar(p.slug) + '" ' +
          'data-nombre="' + escapar(p.nombre) + '" ' +
          'data-precio="' + escapar(p.precio) + '" ' +
          'data-imagen="' + escapar(p.imagen || '') + '" ' +
          'data-stock="' + p.stock + '">' +
          'Agregar al carrito' +
        '</button>' +
      '</div>';
  }

  return '' +
    '<article class="tarjeta">' +
      '<a href="/producto/' + p.slug + '/" class="tarjeta__enlace">' +
        imagenHTML +
        '<div class="tarjeta__cuerpo">' +
          '<span class="tarjeta__categoria">' + escapar(p.categoria) + '</span>' +
          '<span class="tarjeta__nombre">' + escapar(p.nombre) + '</span>' +
          disponibilidad +
          '<span class="tarjeta__precio">' + precioStr + '</span>' +
        '</div>' +
      '</a>' +
      botonHTML +
    '</article>';
}

// Conecta los botones "Agregar al carrito" dentro de un contenedor.
// Usamos delegación de eventos: funciona aunque las tarjetas se repinten.
function conectarBotonesCarritoTarjetas(contenedor) {
  if (!contenedor || typeof agregarAlCarrito !== 'function') return;
  if (contenedor.dataset.carritoConectado) return;
  contenedor.dataset.carritoConectado = '1';

  contenedor.addEventListener('click', function (evento) {
    var btn = evento.target.closest('.tarjeta__btn-carrito');
    if (!btn) return;

    evento.preventDefault();
    evento.stopPropagation();

    agregarAlCarrito({
      slug: btn.getAttribute('data-slug'),
      nombre: btn.getAttribute('data-nombre'),
      precio: btn.getAttribute('data-precio'),
      imagen: btn.getAttribute('data-imagen'),
      stock: parseInt(btn.getAttribute('data-stock'), 10) || 1,
    }, 1);

    if (typeof mostrarToast === 'function') {
      mostrarToast('Agregado al carrito.', 'exito');
    }
  });
}

// Escapa caracteres HTML para evitar que un nombre raro rompa el layout
// o introduzca código malicioso.
function escapar(texto) {
  if (texto == null) return '';
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
