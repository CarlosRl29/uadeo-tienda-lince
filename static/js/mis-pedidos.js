/* ==========================================================================
   mis-pedidos.js
   Carga y muestra el historial de pedidos del alumno logueado.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  if (!document.getElementById('pedidos-lista')) return;

  // Esperamos a que auth.js termine de verificar la sesión.
  var promesa = (typeof verificarSesion === 'function')
    ? verificarSesion()
    : Promise.resolve();

  promesa
    .then(function () { cargarMisPedidos(); })
    .catch(function () { cargarMisPedidos(); });
});

function cargarMisPedidos() {
  var cargando = document.getElementById('pedidos-cargando');
  var vacio = document.getElementById('pedidos-vacio');
  var lista = document.getElementById('pedidos-lista');
  var sinSesion = document.getElementById('pedidos-sin-sesion');

  if (!usuarioActual) {
    if (cargando) cargando.classList.add('oculto');
    if (sinSesion) sinSesion.classList.remove('oculto');
    return;
  }

  apiGet('/api/pedidos/')
    .then(function (datos) {
      if (cargando) cargando.classList.add('oculto');

      if (!datos.pedidos || datos.pedidos.length === 0) {
        vacio.classList.remove('oculto');
        return;
      }

      var html = '';
      for (var i = 0; i < datos.pedidos.length; i++) {
        html += tarjetaPedido(datos.pedidos[i]);
      }
      lista.innerHTML = html;
      lista.classList.remove('oculto');
    })
    .catch(function (err) {
      if (cargando) cargando.classList.add('oculto');
      if (err.status === 401 && sinSesion) {
        sinSesion.classList.remove('oculto');
      } else {
        lista.innerHTML = '<div class="alerta alerta--error">' +
          escapar(err.message || 'No se pudieron cargar los pedidos.') +
          '</div>';
        lista.classList.remove('oculto');
      }
    });
}

function tarjetaPedido(p) {
  var claseEstado = claseEstadoPedido(p.estado);
  var detallesHTML = '';

  if (p.detalles && p.detalles.length) {
    detallesHTML = '<ul class="pedido-card__productos">';
    for (var i = 0; i < p.detalles.length; i++) {
      var d = p.detalles[i];
      detallesHTML += '<li>' + escapar(d.cantidad + ' x ' + d.producto) +
                      ' — $' + Number(d.subtotal).toFixed(2) + '</li>';
    }
    detallesHTML += '</ul>';
  }

  return '' +
    '<article class="pedido-card">' +
      '<div class="pedido-card__encabezado">' +
        '<div>' +
          '<span class="pedido-card__codigo">' + escapar(p.codigo) + '</span>' +
          '<span class="pedido-card__fecha">' + escapar(p.fecha) + '</span>' +
        '</div>' +
        '<span class="pedido-estado ' + claseEstado + '">' +
          escapar(p.estado_texto) +
        '</span>' +
      '</div>' +
      detallesHTML +
      '<div class="pedido-card__total">' +
        'Total: <strong>$' + Number(p.total).toFixed(2) + '</strong>' +
      '</div>' +
      '<a href="/pedido/' + escapar(p.codigo) + '/confirmacion/" ' +
         'class="btn btn--fantasma btn--pequeno mt-1">Ver detalle</a>' +
    '</article>';
}

function claseEstadoPedido(estado) {
  var mapa = {
    PENDIENTE: 'pedido-estado--pendiente',
    PAGADO: 'pedido-estado--pagado',
    CANCELADO: 'pedido-estado--cancelado',
    ENTREGADO: 'pedido-estado--entregado',
  };
  return mapa[estado] || 'pedido-estado--pendiente';
}
