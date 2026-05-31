/* ==========================================================================
   api.js
   Helpers para que JavaScript hable con Django.

   ¿Por qué necesitamos esto?
   - Django protege los POST con un "token CSRF" (un código secreto que evita
     que páginas externas envíen formularios a nuestro backend).
   - Cuando enviamos datos con fetch(), tenemos que incluir ese token en una
     cabecera especial llamada "X-CSRFToken".
   - Aquí centralizamos esa lógica para no repetirla en cada formulario.
   ========================================================================== */

// Lee una cookie del navegador por su nombre. Devuelve '' si no existe.
function obtenerCookie(nombre) {
  var cookies = document.cookie ? document.cookie.split(';') : [];
  for (var i = 0; i < cookies.length; i++) {
    var c = cookies[i].trim();
    if (c.startsWith(nombre + '=')) {
      return decodeURIComponent(c.substring(nombre.length + 1));
    }
  }
  return '';
}

// Devuelve el token CSRF que Django pone como cookie.
function obtenerCSRF() {
  return obtenerCookie('csrftoken');
}

// Helper genérico para hacer peticiones GET a la API.
// Devuelve una Promesa con los datos parseados como objeto JS.
function apiGet(url) {
  return fetch(url, {
    method: 'GET',
    credentials: 'same-origin', // envía la cookie de sesión
    headers: { 'Accept': 'application/json' },
  }).then(procesarRespuesta);
}

// Helper genérico para hacer peticiones POST con cuerpo JSON.
function apiPost(url, datos) {
  return fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': obtenerCSRF(),
    },
    body: JSON.stringify(datos || {}),
  }).then(procesarRespuesta);
}

// Convierte la respuesta del servidor en un objeto JS y maneja errores.
// Si la respuesta NO es 2xx, lanza un error con el mensaje del servidor.
function procesarRespuesta(respuesta) {
  return respuesta.json().catch(function () {
    // Si la respuesta no era JSON válido devolvemos un objeto vacío.
    return {};
  }).then(function (datos) {
    if (!respuesta.ok) {
      var mensaje = (datos && datos.error) ? datos.error : 'Error de conexión (HTTP ' + respuesta.status + ')';
      var err = new Error(mensaje);
      err.status = respuesta.status;
      err.datos = datos;
      throw err;
    }
    return datos;
  });
}
