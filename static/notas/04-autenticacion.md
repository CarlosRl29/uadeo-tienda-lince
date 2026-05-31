# 04 - Autenticación (registro, login, logout)

Esta nota explica **cómo se conecta el formulario HTML con Django** para
crear cuentas, iniciar sesión y cerrar sesión.

## La regla general

```
[ FORMULARIO HTML ]
        │
        │  JavaScript toma los valores
        ▼
[ apiPost('/api/login/', datos) ]
        │
        │  fetch() viaja por HTTP con CSRF token
        ▼
[ DJANGO recibe JSON ]
        │
        │  valida, crea el User o autentica, responde JSON
        ▼
[ JavaScript decide qué hacer ]
        - Si OK: redirige al inicio
        - Si error: muestra mensaje rojo al usuario
```

## Endpoints que creamos

| Método | URL | Qué hace |
|---|---|---|
| `GET`  | `/api/carreras/`   | Devuelve las 6 carreras para llenar el `<select>` del registro. |
| `POST` | `/api/registro/`   | Crea un User + PerfilAlumno y deja al alumno logueado. |
| `POST` | `/api/login/`      | Inicia sesión con matrícula + contraseña. |
| `POST` | `/api/logout/`     | Cierra la sesión actual. |
| `GET`  | `/api/me/`         | Dice si hay sesión y devuelve los datos del usuario. |

Estos son los "JSON endpoints". No tienen HTML, solo datos.

## Decisión importante: la matrícula es el username

En Django, cada usuario tiene un campo `username` único. Nosotros guardamos
ahí la **matrícula del alumno**. Así:

- El alumno solo recuerda su matrícula y su contraseña.
- El admin sigue funcionando porque Django solo necesita un username.

## ¿Qué es el CSRF y por qué lo necesitamos?

CSRF = Cross-Site Request Forgery (falsificación de petición entre sitios).

**El problema:** sin protección, una página maliciosa podría hacer que tu
navegador envíe un POST a Django mientras estás logueado, y Django pensaría
que tú lo enviaste.

**La defensa de Django:**
1. Django pone una cookie llamada `csrftoken` cuando visitas el sitio.
2. Cada POST debe incluir ese token en una cabecera `X-CSRFToken`.
3. Si el token no coincide, Django rechaza la petición con 403.

**Nuestra solución en `api.js`:**

```javascript
function apiPost(url, datos) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': obtenerCSRF(),  // ← aquí inyectamos el token
      'Content-Type': 'application/json',
    },
    credentials: 'same-origin',
    body: JSON.stringify(datos),
  }).then(procesarRespuesta);
}
```

Y la función `obtenerCSRF()` simplemente lee la cookie `csrftoken`:

```javascript
function obtenerCSRF() {
  return obtenerCookie('csrftoken');
}
```

## ¿Cómo Django sabe que estamos logueados?

Es lo mismo que en cualquier página normal:

1. Cuando llamamos `login(request, user)` en el backend, Django crea una
   "sesión" en la base de datos y manda una **cookie `sessionid`** al navegador.
2. Cada petición posterior que hace el navegador envía esa cookie automáticamente
   (porque pusimos `credentials: 'same-origin'` en fetch).
3. Django lee la cookie y reconoce al usuario.

Por eso `request.user.is_authenticated` funciona en cualquier vista de Django
sin que tengamos que pasarle nada explícitamente.

## Flujo completo paso a paso: REGISTRO

```
1. Alumno entra a /registro/
   → Django ejecuta pagina_registro() → manda registro.html

2. El HTML se carga junto con sus scripts:
   - api.js, auth.js, registro.js

3. registro.js arranca y llama a cargarCarreras():
   - fetch GET /api/carreras/
   - Django devuelve { carreras: [{id:1, nombre:"..."} ...] }
   - JS llena el <select> con esas opciones

4. Alumno llena el formulario y clic en "Crear cuenta"

5. enviarRegistro() recoge los valores, los valida en el navegador
   (campos obligatorios, contraseñas coinciden, etc.)

6. apiPost('/api/registro/', {nombre, apellido, matricula, ...})
   - fetch envía JSON + cookie csrftoken
   - Django valida, crea User + PerfilAlumno en una transacción
   - Django llama a login(request, user) → crea sesión
   - Django responde { ok: true, usuario: {...} }

7. registro.js muestra "¡Cuenta creada!" y redirige a /

8. En la página de inicio, main.js llama a verificarSesion()
   - fetch GET /api/me/
   - Django responde con los datos del usuario
   - auth.js muestra "Hola, Juan" y el botón "Cerrar sesión"
```

## Flujo completo paso a paso: LOGIN

```
1. Alumno entra a /login/
2. Llena matrícula y contraseña
3. login.js → apiPost('/api/login/', {matricula, password})
4. Django llama a authenticate(username=matricula, password=password)
   - Si OK → login(request, user) → crea sesión → responde 200
   - Si MAL → responde 401 con { error: "Matrícula o contraseña incorrectos." }
5. JS:
   - Si 200 → redirige a /
   - Si 401 → muestra mensaje rojo
```

## Flujo completo paso a paso: LOGOUT

```
1. Alumno clic en "Cerrar sesión" del navbar
2. auth.js → cerrarSesion() → apiPost('/api/logout/', {})
3. Django llama a logout(request) → borra la sesión
4. JS redirige a / para limpiar el estado visual
```

## Seguridad básica que ya tenemos

- **Contraseñas hasheadas:** Django guarda las contraseñas con PBKDF2 (algoritmo
  fuerte), nunca en texto plano.
- **CSRF activado:** todas las peticiones POST requieren el token.
- **Sesiones en BD:** la cookie del navegador solo lleva un ID; el resto vive
  en la base de datos.
- **Validación doble:** validamos en el navegador (rápido) Y en el servidor
  (obligatorio, porque el navegador se puede saltar).
- **PROTECT en relaciones:** una carrera con alumnos no se puede borrar por accidente.

## Cosas que NO debes hacer

| Mal | Por qué |
|---|---|
| Guardar contraseñas en localStorage | Cualquier extensión maliciosa las puede leer. |
| Confiar solo en validación del frontend | El usuario puede modificar el JS. |
| Mandar `password` en una URL | Quedan en logs y en el historial del navegador. |
| Reusar el mismo CSRF token de hace meses | Django ya los rota; no inventes el tuyo. |
