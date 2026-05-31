/* ==========================================================================
   registro.js
   Lógica del formulario de registro.
   - Al cargar la página, pide las carreras a Django y llena el <select>.
   - Muestra/oculta el campo de carrera según el tipo (Alumno o Profesor).
   - Filtra el campo de teléfono para que solo acepte números.
   - Al enviar el formulario, lo valida y manda los datos a /api/registro/.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  cargarCarreras();
  configurarSelectorTipo();
  configurarFiltroTelefono();

  var form = document.getElementById('form-registro');
  if (form) {
    form.addEventListener('submit', enviarRegistro);
  }
});

// Pide las carreras a la API y las pone como <option> en el select.
function cargarCarreras() {
  var select = document.getElementById('reg-carrera');
  if (!select) return;

  apiGet('/api/carreras/')
    .then(function (datos) {
      select.innerHTML = '<option value="">Selecciona una carrera</option>';
      for (var i = 0; i < datos.carreras.length; i++) {
        var c = datos.carreras[i];
        var opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.nombre;
        select.appendChild(opt);
      }
    })
    .catch(function (err) {
      select.innerHTML = '<option value="">No se pudieron cargar las carreras</option>';
      console.error(err);
    });
}

// Escucha cambios en el selector "Soy Alumno/Profesor" y oculta o muestra
// el campo de carrera según corresponda.
function configurarSelectorTipo() {
  var selectorTipo = document.getElementById('reg-tipo');
  if (!selectorTipo) return;

  selectorTipo.addEventListener('change', actualizarVistaSegunTipo);
  // Llamamos una vez al inicio para que la vista refleje el valor por defecto.
  actualizarVistaSegunTipo();
}

function actualizarVistaSegunTipo() {
  var tipo = document.getElementById('reg-tipo').value;
  var campoCarrera = document.getElementById('campo-carrera');
  var selectCarrera = document.getElementById('reg-carrera');
  var etiquetaMatricula = document.getElementById('reg-etiqueta-matricula');

  if (tipo === 'PROFESOR') {
    campoCarrera.classList.add('oculto');
    selectCarrera.value = '';  // limpiamos para no enviarla por error
    etiquetaMatricula.textContent = 'Número de empleado';
  } else {
    campoCarrera.classList.remove('oculto');
    etiquetaMatricula.textContent = 'Matrícula';
  }
}

// Hace que el campo de teléfono solo acepte dígitos.
// Si el usuario pega o escribe letras, se eliminan silenciosamente.
function configurarFiltroTelefono() {
  var input = document.getElementById('reg-telefono');
  if (!input) return;

  input.addEventListener('input', function () {
    var soloNumeros = input.value.replace(/[^0-9]/g, '');
    if (input.value !== soloNumeros) {
      input.value = soloNumeros;
    }
  });
}

// Envía el formulario al backend después de validar.
function enviarRegistro(evento) {
  evento.preventDefault();

  var caja = document.getElementById('registro-mensaje');
  var boton = document.getElementById('btn-registrar');
  var tipo = document.getElementById('reg-tipo').value;

  var datos = {
    tipo:       tipo,
    nombre:     document.getElementById('reg-nombre').value.trim(),
    apellido:   document.getElementById('reg-apellido').value.trim(),
    matricula:  document.getElementById('reg-matricula').value.trim(),
    correo:     document.getElementById('reg-correo').value.trim(),
    telefono:   document.getElementById('reg-telefono').value.trim(),
    password:   document.getElementById('reg-password').value,
  };
  // carrera_id solo se incluye si es alumno.
  if (tipo === 'ALUMNO') {
    datos.carrera_id = document.getElementById('reg-carrera').value;
  }
  var password2 = document.getElementById('reg-password2').value;

  // Validación rápida en el navegador.
  if (!datos.nombre || !datos.apellido || !datos.matricula
      || !datos.correo || !datos.password) {
    mostrarMensaje(caja, 'Llena todos los campos obligatorios.', 'error');
    return;
  }
  if (tipo === 'ALUMNO' && !datos.carrera_id) {
    mostrarMensaje(caja, 'Selecciona una carrera.', 'error');
    return;
  }
  if (datos.password.length < 8) {
    mostrarMensaje(caja, 'La contraseña debe tener al menos 8 caracteres.', 'error');
    return;
  }
  if (datos.password !== password2) {
    mostrarMensaje(caja, 'Las contraseñas no coinciden.', 'error');
    return;
  }

  boton.disabled = true;
  boton.textContent = 'Creando cuenta...';

  apiPost('/api/registro/', datos)
    .then(function () {
      var destino = sessionStorage.getItem('volver_a') || '/';
      sessionStorage.removeItem('volver_a');
      mostrarMensaje(caja, '¡Cuenta creada! Te llevamos a la página solicitada.', 'exito');
      setTimeout(function () { window.location.href = destino; }, 800);
    })
    .catch(function (err) {
      mostrarMensaje(caja, err.message || 'No se pudo crear la cuenta.', 'error');
      boton.disabled = false;
      boton.textContent = 'Crear cuenta';
    });
}

// Pinta un mensaje dentro del cuadro de alertas del formulario.
function mostrarMensaje(caja, texto, tipo) {
  if (!caja) return;
  caja.textContent = texto;
  caja.classList.remove('oculto', 'alerta--exito', 'alerta--error', 'alerta--info');
  caja.classList.add(tipo === 'exito' ? 'alerta--exito' : 'alerta--error');
}
