/* ==========================================================================
   producto-detalle.js
   Lógica de la página de detalle de un producto.
   - Lee el slug del producto de la URL (ej. /producto/playera-uadeo/).
   - Pide los datos del producto al API.
   - Pinta la info en pantalla.
   - El botón "Agregar al carrito" se conecta aquí pero la lógica real
     vivirá en static/js/carrito.js (Fase 5).
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  var slug = obtenerSlugDeURL();
  if (!slug) {
    pintarError('URL inválida.');
    return;
  }
  cargarDetalle(slug);
});

// Lee el slug del producto desde la URL.
// URL ejemplo: /producto/playera-uadeo/  → devuelve "playera-uadeo"
function obtenerSlugDeURL() {
  var partes = window.location.pathname.split('/').filter(function (p) { return p; });
  // partes = ["producto", "playera-uadeo"]
  if (partes.length >= 2 && partes[0] === 'producto') {
    return partes[1];
  }
  return '';
}

function cargarDetalle(slug) {
  apiGet('/api/productos/' + slug + '/')
    .then(function (datos) {
      pintarDetalle(datos.producto);
    })
    .catch(function (err) {
      pintarError(err.message || 'No se pudo cargar el producto.');
    });
}

function pintarDetalle(p) {
  var contenedor = document.getElementById('detalle-producto');
  if (!contenedor) return;

  // Imagen o placeholder.
  var imagenHTML;
  if (p.imagen) {
    imagenHTML = '<img src="' + p.imagen + '" alt="' + escapar(p.nombre) +
                 '" class="detalle__imagen">';
  } else {
    imagenHTML = '<div class="detalle__imagen tarjeta__imagen--vacia" style="height: 320px; font-size: 4rem;">' +
                   escapar(p.nombre.substring(0, 2).toUpperCase()) +
                 '</div>';
  }

  var precioStr = '$' + Number(p.precio).toFixed(2);

  // Botón con dos estados: agregar (si hay stock) o agotado.
  var botonHTML;
  if (p.disponible) {
    botonHTML = '<button type="button" id="btn-agregar" class="btn btn--primario btn--bloque" data-slug="' +
                  escapar(p.slug) + '">' +
                  'Agregar al carrito' +
                '</button>';
  } else {
    botonHTML = '<button type="button" class="btn btn--bloque" disabled>Producto agotado</button>';
  }

  contenedor.innerHTML =
    '<div class="detalle__grid">' +
      '<div class="detalle__media">' + imagenHTML + '</div>' +
      '<div class="detalle__info">' +
        '<span class="tarjeta__categoria">' + escapar(p.categoria) + '</span>' +
        '<h1 class="detalle__nombre">' + escapar(p.nombre) + '</h1>' +
        '<p class="detalle__precio">' + precioStr + '</p>' +
        '<p class="detalle__stock">Stock disponible: ' + p.stock + '</p>' +
        '<p class="detalle__descripcion">' + escapar(p.descripcion || 'Sin descripción.') + '</p>' +
        botonHTML +
      '</div>' +
    '</div>';

  // Botón "Agregar al carrito": guarda el producto en localStorage y muestra feedback.
  var btn = document.getElementById('btn-agregar');
  if (btn) {
    btn.addEventListener('click', function () {
      agregarAlCarrito({
        slug:    p.slug,
        nombre:  p.nombre,
        precio:  p.precio,
        imagen:  p.imagen,
        stock:   p.stock,
      }, 1);
      mostrarToast('Agregado al carrito.', 'exito');
    });
  }
}

function pintarError(mensaje) {
  var contenedor = document.getElementById('detalle-producto');
  if (!contenedor) return;
  contenedor.innerHTML = '<p class="alerta alerta--error">' + escapar(mensaje) + '</p>';
}

// La función escapar() viene de tarjetas.js (se carga antes que este script).
