/* ==========================================================================
   auth.js
   Maneja el estado de la sesión del usuario.

   Lo que hace:
   1. Al cargar cualquier página llama a /api/me/ para saber si hay sesión.
   2. Si hay sesión: muestra el saludo y el botón "Cerrar sesión" en la navbar
      y oculta los botones de "Iniciar sesión" y "Registrarse".
   3. Conecta el botón "Cerrar sesión" para hacer logout.
   4. Expone una variable global "usuarioActual" para que otros JS puedan usarla.
   ========================================================================== */

var usuarioActual = null;

// Consulta a Django si hay sesión activa y actualiza la navbar en consecuencia.
function verificarSesion() {
  return apiGet('/api/me/')
    .then(function (datos) {
      usuarioActual = datos.usuario;
      mostrarUsuarioEnNavbar(datos.usuario);
    })
    .catch(function (err) {
      // 401 = no hay sesión, no es un error real.
      usuarioActual = null;
      mostrarInvitadoEnNavbar();
    });
}

function mostrarUsuarioEnNavbar(usuario) {
  var invitado = document.getElementById('navbar-invitado');
  var sesion = document.getElementById('navbar-usuario');
  var saludo = document.getElementById('navbar-saludo');

  if (invitado) invitado.classList.add('oculto');
  if (sesion) sesion.classList.remove('oculto');
  if (saludo) saludo.textContent = 'Hola, ' + (usuario.nombre || usuario.matricula);

  actualizarEnlacePedidos(true);

  // Conectamos el botón "Cerrar sesión"
  var btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.onclick = cerrarSesion;
  }
}

function mostrarInvitadoEnNavbar() {
  var invitado = document.getElementById('navbar-invitado');
  var sesion = document.getElementById('navbar-usuario');

  if (invitado) invitado.classList.remove('oculto');
  if (sesion) sesion.classList.add('oculto');

  actualizarEnlacePedidos(false);
}

// Muestra u oculta "Mis pedidos" según haya sesión activa.
function actualizarEnlacePedidos(visible) {
  var link = document.getElementById('nav-pedidos');
  if (!link) return;
  if (visible) {
    link.classList.remove('oculto');
  } else {
    link.classList.add('oculto');
  }
}

// Cierra la sesión llamando al backend y refresca la página de inicio.
function cerrarSesion() {
  apiPost('/api/logout/', {})
    .then(function () {
      usuarioActual = null;
      // Volvemos a la página principal para que el usuario vea el "estado limpio".
      window.location.href = '/';
    })
    .catch(function (err) {
      alert('No se pudo cerrar sesión: ' + err.message);
    });
}
