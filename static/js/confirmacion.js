/* ==========================================================================
   confirmacion.js
   Muestra los datos del pedido recién confirmado leyendo el código de la URL.
   URL esperada: /pedido/PED-XXXXXXXX/confirmacion/
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  if (!document.getElementById('confirmacion-ok')) return;

  var codigo = obtenerCodigoDeURL();
  if (!codigo) {
    mostrarErrorConfirmacion();
    return;
  }

  var promesa = (typeof verificarSesion === 'function')
    ? verificarSesion()
    : Promise.resolve();

  promesa
    .then(function () { return apiGet('/api/pedidos/' + encodeURIComponent(codigo) + '/'); })
    .then(function (datos) { pintarConfirmacion(datos.pedido); })
    .catch(function () { mostrarErrorConfirmacion(); });
});

function obtenerCodigoDeURL() {
  // /pedido/PED-9F3A2B7C/confirmacion/
  var partes = window.location.pathname.split('/').filter(function (p) { return p; });
  var idx = partes.indexOf('pedido');
  if (idx !== -1 && partes[idx + 1]) {
    return partes[idx + 1];
  }
  return '';
}

function pintarConfirmacion(p) {
  document.getElementById('confirmacion-cargando').classList.add('oculto');
  document.getElementById('confirmacion-ok').classList.remove('oculto');

  document.getElementById('confirmacion-codigo').textContent = p.codigo;
  document.getElementById('confirmacion-total').textContent = '$' + Number(p.total).toFixed(2);
  document.getElementById('confirmacion-fecha').textContent = p.fecha;

  var estadoEl = document.getElementById('confirmacion-estado');
  estadoEl.textContent = p.estado_texto;
  estadoEl.className = 'pedido-estado ' + claseEstadoPedido(p.estado);

  var html = '';
  if (p.detalles) {
    for (var i = 0; i < p.detalles.length; i++) {
      var d = p.detalles[i];
      html += '' +
        '<div class="confirmacion__detalle-fila">' +
          '<span>' + escapar(d.cantidad + ' x ' + d.producto) + '</span>' +
          '<span>$' + Number(d.subtotal).toFixed(2) + '</span>' +
        '</div>';
    }
  }
  document.getElementById('confirmacion-detalles').innerHTML = html;
}

function mostrarErrorConfirmacion() {
  document.getElementById('confirmacion-cargando').classList.add('oculto');
  document.getElementById('confirmacion-error').classList.remove('oculto');
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
