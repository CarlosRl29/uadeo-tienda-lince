/* ==========================================================================
   login.js
   Lógica del formulario de inicio de sesión.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('form-login');
  if (form) {
    form.addEventListener('submit', enviarLogin);
  }
});

function enviarLogin(evento) {
  evento.preventDefault();

  var caja = document.getElementById('login-mensaje');
  var boton = document.getElementById('btn-iniciar');

  var datos = {
    matricula: document.getElementById('login-matricula').value.trim(),
    password:  document.getElementById('login-password').value,
  };

  if (!datos.matricula || !datos.password) {
    mostrarMensajeLogin(caja, 'Llena los dos campos.', 'error');
    return;
  }

  boton.disabled = true;
  boton.textContent = 'Entrando...';

  apiPost('/api/login/', datos)
    .then(function () {
      // Si el usuario venía del carrito (u otra página), regresamos ahí.
      var destino = sessionStorage.getItem('volver_a') || '/';
      sessionStorage.removeItem('volver_a');
      mostrarMensajeLogin(caja, 'Bienvenido. Te llevamos a la página solicitada.', 'exito');
      setTimeout(function () { window.location.href = destino; }, 500);
    })
    .catch(function (err) {
      mostrarMensajeLogin(caja, err.message || 'No se pudo iniciar sesión.', 'error');
      boton.disabled = false;
      boton.textContent = 'Entrar';
    });
}

function mostrarMensajeLogin(caja, texto, tipo) {
  if (!caja) return;
  caja.textContent = texto;
  caja.classList.remove('oculto', 'alerta--exito', 'alerta--error', 'alerta--info');
  caja.classList.add(tipo === 'exito' ? 'alerta--exito' : 'alerta--error');
}
