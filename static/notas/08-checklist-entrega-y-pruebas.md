# 08 - Checklist de entrega y pruebas finales

Usa esta lista antes de presentar o entregar el proyecto. Marca cada ítem
cuando lo hayas probado tú mismo en el navegador.

## Instalación en otra computadora

- [ ] Clonar o copiar la carpeta del proyecto (sin `venv/` ni `db.sqlite3`)
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar: `venv\Scripts\activate`
- [ ] Instalar: `pip install -r requirements.txt`
- [ ] Migrar: `python manage.py migrate`
- [ ] Crear admin: `python manage.py createsuperuser`
- [ ] Correr: `python manage.py runserver`
- [ ] Abrir http://127.0.0.1:8000/ sin errores

## Registro e inicio de sesión

- [ ] Registro como **Alumno** pide carrera y acepta matrícula
- [ ] Registro como **Profesor** oculta la carrera
- [ ] Teléfono solo acepta números
- [ ] Login con matrícula + contraseña funciona
- [ ] Logout regresa al inicio
- [ ] Navbar muestra saludo al estar logueado

## Catálogo e imágenes

- [ ] Página de inicio carga el carrusel de destacados
- [ ] Los productos muestran imagen (SVG o foto del admin)
- [ ] Catálogo lista todos los productos
- [ ] Filtro por categoría funciona
- [ ] Buscador por nombre funciona
- [ ] Detalle de producto muestra precio, stock y descripción
- [ ] Botón "Agregar al carrito" en catálogo e inicio funciona

## Carrito

- [ ] Badge del navbar se actualiza al agregar productos
- [ ] Página `/carrito/` muestra los productos guardados
- [ ] Botones + / - cambian cantidades
- [ ] Quitar producto funciona
- [ ] Vaciar carrito pide confirmación
- [ ] El carrito persiste al recargar la página (localStorage)

## Apartado y pedidos

- [ ] Sin sesión, "Confirmar apartado" manda al login
- [ ] Con sesión, confirmar crea pedido y muestra código PED-...
- [ ] El carrito se vacía después de confirmar
- [ ] `/mis-pedidos/` muestra el historial
- [ ] Solo el dueño puede ver su pedido (no el de otro alumno)
- [ ] Stock insuficiente muestra error claro

## Panel de administración

- [ ] Acceso a `/admin/` con superusuario
- [ ] Crear/editar producto (precio, stock, imagen)
- [ ] Marcar producto como destacado (aparece en inicio)
- [ ] Desactivar producto lo oculta del catálogo
- [ ] Ver pedidos y cambiar estado (Pendiente → Pagado → Entregado)

## Responsivo básico

- [ ] Se ve bien en computadora (pantalla ancha)
- [ ] Se ve usable en celular (navbar, catálogo, carrito)

## Archivos que NO se suben a Git

Verifica que `.gitignore` excluya:
- `venv/`
- `db.sqlite3`
- `media/`
- `__pycache__/`
- `.env` (si lo usan)

## Entregables sugeridos para el reporte

1. Capturas de pantalla: inicio, catálogo, carrito, confirmación, mis pedidos, admin
2. Diagrama o explicación de la arquitectura (ver nota 01)
3. Manual de instalación (README.md)
4. Video corto demostrando el flujo completo (opcional)
5. Lista de integrantes del equipo

## Flujo demo recomendado (5 minutos)

1. Mostrar página de inicio y catálogo
2. Registrar un alumno nuevo
3. Agregar 2 productos al carrito desde el catálogo
4. Confirmar apartado → mostrar código
5. Entrar al admin → cambiar estado del pedido a "Pagado en escuela"
6. Volver a "Mis pedidos" y mostrar el estado actualizado
