/* ==========================================================================
   home.js
   Lógica de la página de inicio (/).
   - Carga los productos marcados como "destacados" y los pinta en el carrusel.
   - Conecta los botones de Prev/Next para desplazar el carrusel.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  cargarDestacados();
  conectarBotonesCarrusel();
});

// Pide los productos destacados al API y los pinta dentro del carrusel.
function cargarDestacados() {
  var contenedor = document.getElementById('carrusel-destacados');
  if (!contenedor) return;

  apiGet('/api/productos/?destacados=true')
    .then(function (datos) {
      pintarCarrusel(datos.productos);
    })
    .catch(function (err) {
      contenedor.innerHTML = '<p class="alerta alerta--error">No se pudieron cargar los productos destacados.</p>';
      console.error(err);
    });
}

function pintarCarrusel(productos) {
  var contenedor = document.getElementById('carrusel-destacados');
  if (!contenedor) return;

  if (!productos || productos.length === 0) {
    contenedor.innerHTML = '<p class="texto-centro" style="padding: 1.5rem; color: var(--color-gris-texto);">Pronto agregaremos productos destacados.</p>';
    return;
  }

  // Envolvemos cada tarjeta en un div .carrusel__item para que el flex y el
  // scroll-snap funcionen correctamente.
  var html = '';
  for (var i = 0; i < productos.length; i++) {
    html += '<div class="carrusel__item">' +
              tarjetaProducto(productos[i], { mostrarBotonCarrito: true }) +
            '</div>';
  }
  contenedor.innerHTML = html;
  conectarBotonesCarritoTarjetas(contenedor);
}

// Cada clic en una flecha desliza ~1 tarjeta hacia el lado correspondiente.
function conectarBotonesCarrusel() {
  var contenedor = document.getElementById('carrusel-destacados');
  var btnPrev = document.getElementById('carrusel-prev');
  var btnNext = document.getElementById('carrusel-next');
  if (!contenedor || !btnPrev || !btnNext) return;

  var PASO = 240;  // ancho aproximado de una tarjeta + el gap

  btnPrev.addEventListener('click', function () {
    contenedor.scrollBy({ left: -PASO, behavior: 'smooth' });
  });

  btnNext.addEventListener('click', function () {
    contenedor.scrollBy({ left: PASO, behavior: 'smooth' });
  });
}
