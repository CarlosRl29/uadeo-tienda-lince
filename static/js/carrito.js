/* ==========================================================================
   carrito.js
   El carrito vive 100% en el NAVEGADOR (localStorage), no en el backend.
   El backend solo se entera cuando el alumno confirma el apartado (Fase 6).

   Estructura del carrito en localStorage (clave "carrito_uadeo"):
     [
       { slug: "playera-uadeo", nombre: "Playera UAdeO",
         precio: "220.00", imagen: "...", stock: 30, cantidad: 2 },
       ...
     ]

   Funciones globales que expone este archivo:
     - obtenerCarrito()
     - guardarCarrito(carrito)
     - agregarAlCarrito(producto, cantidad)
     - quitarDelCarrito(slug)
     - cambiarCantidad(slug, cantidad)
     - vaciarCarrito()
     - totalProductos(carrito)
     - totalDinero(carrito)
     - mostrarToast(mensaje, tipo)
   ========================================================================== */

var CLAVE_CARRITO = 'carrito_uadeo';


// ---------------------------------------------------------------------------
// localStorage helpers
// ---------------------------------------------------------------------------

function obtenerCarrito() {
  try {
    var datos = localStorage.getItem(CLAVE_CARRITO);
    return datos ? JSON.parse(datos) : [];
  } catch (e) {
    return [];
  }
}

function guardarCarrito(carrito) {
  localStorage.setItem(CLAVE_CARRITO, JSON.stringify(carrito));
  // El navbar lee el badge directamente de localStorage; lo refrescamos.
  if (typeof actualizarBadgeCarrito === 'function') {
    actualizarBadgeCarrito();
  }
}


// ---------------------------------------------------------------------------
// Operaciones del carrito
// ---------------------------------------------------------------------------

// Agrega un producto al carrito. Si ya está, le suma la cantidad.
// Nunca permite superar el stock disponible del producto.
function agregarAlCarrito(producto, cantidad) {
  cantidad = cantidad || 1;
  var carrito = obtenerCarrito();
  var existente = buscarItem(carrito, producto.slug);

  if (existente) {
    existente.cantidad = Math.min(existente.cantidad + cantidad, producto.stock);
    // Actualizamos la info por si cambió en el catálogo.
    existente.precio = producto.precio;
    existente.imagen = producto.imagen;
    existente.stock = producto.stock;
  } else {
    carrito.push({
      slug: producto.slug,
      nombre: producto.nombre,
      precio: producto.precio,
      imagen: producto.imagen || '',
      stock: producto.stock,
      cantidad: Math.min(cantidad, producto.stock),
    });
  }
  guardarCarrito(carrito);
}

function quitarDelCarrito(slug) {
  var carrito = obtenerCarrito().filter(function (it) { return it.slug !== slug; });
  guardarCarrito(carrito);
}

// Cambia la cantidad de un producto. Si llega a 0, se elimina.
function cambiarCantidad(slug, cantidad) {
  var carrito = obtenerCarrito();
  var item = buscarItem(carrito, slug);
  if (!item) return;

  cantidad = parseInt(cantidad, 10) || 0;
  if (cantidad <= 0) {
    quitarDelCarrito(slug);
    return;
  }
  item.cantidad = Math.min(cantidad, item.stock);
  guardarCarrito(carrito);
}

function vaciarCarrito() {
  localStorage.removeItem(CLAVE_CARRITO);
  if (typeof actualizarBadgeCarrito === 'function') {
    actualizarBadgeCarrito();
  }
}

function buscarItem(carrito, slug) {
  for (var i = 0; i < carrito.length; i++) {
    if (carrito[i].slug === slug) return carrito[i];
  }
  return null;
}


// ---------------------------------------------------------------------------
// Totales
// ---------------------------------------------------------------------------

function totalProductos(carrito) {
  var total = 0;
  for (var i = 0; i < carrito.length; i++) {
    total += carrito[i].cantidad || 0;
  }
  return total;
}

function totalDinero(carrito) {
  var total = 0;
  for (var i = 0; i < carrito.length; i++) {
    total += Number(carrito[i].precio) * carrito[i].cantidad;
  }
  return total;
}


// ---------------------------------------------------------------------------
// Toast: mensajes flotantes de feedback (Agregado al carrito, etc.)
// ---------------------------------------------------------------------------

function mostrarToast(mensaje, tipo) {
  var toast = document.createElement('div');
  toast.className = 'toast toast--' + (tipo || 'info');
  toast.textContent = mensaje;
  document.body.appendChild(toast);

  // Forzamos un reflow y luego añadimos la clase de visibilidad
  // para que la transición CSS se dispare.
  setTimeout(function () { toast.classList.add('toast--visible'); }, 30);
  setTimeout(function () {
    toast.classList.remove('toast--visible');
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 2500);
}


// ---------------------------------------------------------------------------
// Render de la página /carrito/
// (esta parte solo se activa si los elementos del HTML existen)
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {
  // Solo inicializamos la página del carrito si estamos en ella.
  if (document.getElementById('carrito-items')) {
    renderizarCarrito();
    conectarBotonesGenerales();
  }
});

function renderizarCarrito() {
  var carrito = obtenerCarrito();
  var contenedorVacio = document.getElementById('carrito-vacio');
  var contenedorContenido = document.getElementById('carrito-contenido');
  var contenedorItems = document.getElementById('carrito-items');

  if (carrito.length === 0) {
    contenedorVacio.classList.remove('oculto');
    contenedorContenido.classList.add('oculto');
    return;
  }

  contenedorVacio.classList.add('oculto');
  contenedorContenido.classList.remove('oculto');

  // Pintamos los items.
  var html = '';
  for (var i = 0; i < carrito.length; i++) {
    html += renderItemCarrito(carrito[i]);
  }
  contenedorItems.innerHTML = html;

  // Conectamos los botones de cada item.
  conectarBotonesItems();

  // Actualizamos el resumen.
  document.getElementById('resumen-cantidad').textContent = totalProductos(carrito);
  document.getElementById('resumen-total').textContent = '$' + totalDinero(carrito).toFixed(2);
}

function renderItemCarrito(item) {
  var subtotal = Number(item.precio) * item.cantidad;
  var iniciales = item.nombre.substring(0, 2).toUpperCase();

  var imagenHTML;
  if (item.imagen) {
    imagenHTML = '<img src="' + item.imagen + '" alt="' + escapar(item.nombre) +
                 '" class="carrito-item__imagen">';
  } else {
    imagenHTML = '<div class="carrito-item__imagen tarjeta__imagen--vacia">' +
                   escapar(iniciales) +
                 '</div>';
  }

  return '' +
    '<div class="carrito-item" data-slug="' + escapar(item.slug) + '">' +
      imagenHTML +
      '<div class="carrito-item__info">' +
        '<a href="/producto/' + escapar(item.slug) + '/" class="carrito-item__nombre">' +
          escapar(item.nombre) +
        '</a>' +
        '<span class="carrito-item__precio">$' + Number(item.precio).toFixed(2) + ' c/u</span>' +
      '</div>' +
      '<div class="carrito-item__cantidad">' +
        '<button type="button" class="carrito-item__cant-btn" data-accion="menos">-</button>' +
        '<input type="number" class="carrito-item__cant-input" value="' + item.cantidad +
               '" min="1" max="' + item.stock + '">' +
        '<button type="button" class="carrito-item__cant-btn" data-accion="mas">+</button>' +
      '</div>' +
      '<div class="carrito-item__subtotal">$' + subtotal.toFixed(2) + '</div>' +
      '<button type="button" class="carrito-item__quitar" data-accion="quitar" title="Quitar">&times;</button>' +
    '</div>';
}

function conectarBotonesItems() {
  var items = document.querySelectorAll('.carrito-item');
  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    var slug = item.getAttribute('data-slug');

    var btnMenos  = item.querySelector('[data-accion="menos"]');
    var btnMas    = item.querySelector('[data-accion="mas"]');
    var btnQuitar = item.querySelector('[data-accion="quitar"]');
    var input     = item.querySelector('.carrito-item__cant-input');

    btnMenos.addEventListener('click', (function (s, inp) {
      return function () {
        cambiarCantidad(s, parseInt(inp.value, 10) - 1);
        renderizarCarrito();
      };
    })(slug, input));

    btnMas.addEventListener('click', (function (s, inp) {
      return function () {
        cambiarCantidad(s, parseInt(inp.value, 10) + 1);
        renderizarCarrito();
      };
    })(slug, input));

    input.addEventListener('change', (function (s, inp) {
      return function () {
        cambiarCantidad(s, parseInt(inp.value, 10));
        renderizarCarrito();
      };
    })(slug, input));

    btnQuitar.addEventListener('click', (function (s) {
      return function () {
        quitarDelCarrito(s);
        renderizarCarrito();
        mostrarToast('Producto eliminado del carrito.');
      };
    })(slug));
  }
}

function conectarBotonesGenerales() {
  var btnVaciar = document.getElementById('btn-vaciar');
  if (btnVaciar) {
    btnVaciar.addEventListener('click', function () {
      if (!confirm('¿Vaciar todo el carrito?')) return;
      vaciarCarrito();
      renderizarCarrito();
      mostrarToast('Carrito vaciado.');
    });
  }

  var btnConfirmar = document.getElementById('btn-confirmar');
  if (btnConfirmar) {
    btnConfirmar.addEventListener('click', function () {
      if (!usuarioActual) {
        sessionStorage.setItem('volver_a', '/carrito/');
        mostrarToast('Inicia sesión para confirmar tu apartado.', 'error');
        setTimeout(function () { window.location.href = '/login/'; }, 800);
        return;
      }

      var carrito = obtenerCarrito();
      if (carrito.length === 0) {
        mostrarToast('Tu carrito está vacío.', 'error');
        return;
      }

      btnConfirmar.disabled = true;
      btnConfirmar.textContent = 'Confirmando...';

      var items = [];
      for (var i = 0; i < carrito.length; i++) {
        items.push({
          slug: carrito[i].slug,
          cantidad: carrito[i].cantidad,
        });
      }

      apiPost('/api/pedidos/crear/', { items: items })
        .then(function (datos) {
          vaciarCarrito();
          window.location.href = '/pedido/' + datos.pedido.codigo + '/confirmacion/';
        })
        .catch(function (err) {
          btnConfirmar.disabled = false;
          btnConfirmar.textContent = 'Confirmar apartado';
          mostrarToast(err.message || 'No se pudo confirmar el apartado.', 'error');
        });
    });
  }
}
