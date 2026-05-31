/* ==========================================================================
   productos.js
   Lógica del catálogo (página /catalogo/).
   - Carga las categorías y arma los botones de filtro VERTICALES del sidebar.
   - Carga los productos y los pinta como tarjetas.
   - Conecta el buscador y los botones de categoría para refiltrar.

   Las funciones tarjetaProducto() y escapar() vienen de tarjetas.js.
   ========================================================================== */

// Estado actual del catálogo. Lo cambian los filtros y el buscador.
var estadoCatalogo = {
  categoria: '',  // '' = todas
  texto: '',      // texto de búsqueda
};

// Para no llamar a la API en cada tecla, usamos un "debounce" pequeño.
var timerBusqueda = null;

document.addEventListener('DOMContentLoaded', function () {
  cargarFiltrosCategorias();
  cargarProductos();
  conectarBuscador();
});


// ---------------------------------------------------------------------------
// Categorías (filtros verticales del sidebar)
// ---------------------------------------------------------------------------

function cargarFiltrosCategorias() {
  var contenedor = document.getElementById('filtros-categorias');
  if (!contenedor) return;

  apiGet('/api/categorias/')
    .then(function (datos) {
      var html = botonFiltro('', 'Todas las categorías', true);
      for (var i = 0; i < datos.categorias.length; i++) {
        var c = datos.categorias[i];
        html += botonFiltro(c.slug, c.nombre, false);
      }
      contenedor.innerHTML = html;

      var botones = contenedor.querySelectorAll('.filtro-btn');
      for (var j = 0; j < botones.length; j++) {
        botones[j].addEventListener('click', cambiarCategoria);
      }
    })
    .catch(function (err) {
      contenedor.innerHTML = '<p class="alerta alerta--error">No se pudieron cargar las categorías.</p>';
      console.error(err);
    });
}

function botonFiltro(slug, nombre, activo) {
  // Usamos las clases del sidebar (filtro-btn--vertical) en lugar de los
  // botones tipo "chip" horizontal de la versión anterior.
  var clases = 'filtro-btn filtro-btn--vertical' + (activo ? ' filtro-btn--activo' : '');
  return '<button type="button" class="' + clases + '" data-slug="' + slug + '">' +
           nombre +
         '</button>';
}

function cambiarCategoria(evento) {
  var slug = evento.currentTarget.getAttribute('data-slug');
  estadoCatalogo.categoria = slug;

  var botones = document.querySelectorAll('.filtro-btn');
  for (var i = 0; i < botones.length; i++) {
    botones[i].classList.remove('filtro-btn--activo');
  }
  evento.currentTarget.classList.add('filtro-btn--activo');

  cargarProductos();
}


// ---------------------------------------------------------------------------
// Buscador
// ---------------------------------------------------------------------------

function conectarBuscador() {
  var input = document.getElementById('input-busqueda');
  if (!input) return;

  input.addEventListener('input', function () {
    estadoCatalogo.texto = input.value.trim();
    clearTimeout(timerBusqueda);
    timerBusqueda = setTimeout(cargarProductos, 300);
  });
}


// ---------------------------------------------------------------------------
// Productos
// ---------------------------------------------------------------------------

function cargarProductos() {
  var contenedor = document.getElementById('lista-productos');
  var titulo = document.getElementById('titulo-resultados');
  if (!contenedor) return;

  contenedor.innerHTML = '<p class="texto-centro" style="grid-column: 1 / -1; padding: 1rem; color: var(--color-gris-texto);">Cargando...</p>';

  var params = [];
  if (estadoCatalogo.categoria) params.push('categoria=' + encodeURIComponent(estadoCatalogo.categoria));
  if (estadoCatalogo.texto)     params.push('q=' + encodeURIComponent(estadoCatalogo.texto));
  var url = '/api/productos/' + (params.length ? '?' + params.join('&') : '');

  apiGet(url)
    .then(function (datos) {
      pintarProductos(datos.productos);
      if (titulo) {
        var sufijo = datos.total === 1 ? ' (1 resultado)' : ' (' + datos.total + ' resultados)';
        titulo.textContent = 'Catálogo de productos' + sufijo;
      }
    })
    .catch(function (err) {
      contenedor.innerHTML = '<p class="alerta alerta--error" style="grid-column: 1 / -1;">No se pudieron cargar los productos.</p>';
      console.error(err);
    });
}

function pintarProductos(productos) {
  var contenedor = document.getElementById('lista-productos');
  if (!contenedor) return;

  if (!productos || productos.length === 0) {
    contenedor.innerHTML = '<p class="texto-centro" style="grid-column: 1 / -1; padding: 2rem; color: var(--color-gris-texto);">No se encontraron productos con esos filtros.</p>';
    return;
  }

  var html = '';
  for (var i = 0; i < productos.length; i++) {
    html += tarjetaProducto(productos[i], { mostrarBotonCarrito: true });
  }
  contenedor.innerHTML = html;
  conectarBotonesCarritoTarjetas(contenedor);
}
