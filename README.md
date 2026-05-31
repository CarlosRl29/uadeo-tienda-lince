# UAdeO Tienda Lince

Tienda virtual universitaria para alumnos de la **UAdeO Región El Fuerte** (modalidad semiescolarizada).

Los alumnos pueden registrarse, explorar productos, armar un carrito, confirmar un apartado y pagar físicamente en la escuela. El administrador gestiona productos y pedidos desde Django Admin.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Django 5.1 + Python |
| API JSON | Django REST Framework (serializers) |
| Frontend | HTML, CSS, JavaScript (vanilla) |
| Base de datos | SQLite |
| Imágenes | Pillow (subida desde admin) |

## Requisitos

- Windows 10/11
- Python 3.11 o superior
- VS Code o Cursor

## Instalación (primera vez)

Abre una terminal en la carpeta del proyecto y ejecuta estos pasos **en orden**:

### 1. Crear entorno virtual

```powershell
python -m venv venv
```

### 2. Activar el entorno virtual

```powershell
venv\Scripts\activate
```

Verás `(venv)` al inicio de la línea de la terminal.

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Aplicar migraciones (crear la base de datos)

```powershell
python manage.py migrate
```

Esto crea `db.sqlite3` con carreras, categorías y 12 productos de prueba.

### 5. Crear usuario administrador

```powershell
python manage.py createsuperuser
```

Elige un nombre de usuario, correo y contraseña. Este usuario accede a `/admin/`.

### 6. Levantar el servidor

```powershell
python manage.py runserver
```

Abre el navegador en: **http://127.0.0.1:8000/**

## Uso diario (cuando ya instalaste todo)

```powershell
cd "ruta\a\STORE UADEO"
venv\Scripts\activate
python manage.py runserver
```

## Estructura del proyecto

```
STORE UADEO/
├── manage.py
├── requirements.txt
├── tienda_uadeo/          # Configuración global (settings, urls)
├── usuarios/              # Registro, login, perfiles, carreras
├── catalogo/              # Productos, categorías, página de inicio
├── pedidos/               # Carrito (página), apartados, historial
├── templates/             # Páginas HTML (sin sintaxis Django compleja)
├── static/
│   ├── css/styles.css
│   ├── js/                # JavaScript del frontend
│   ├── img/productos/     # Imágenes SVG de respaldo por producto
│   └── notas/             # Material de estudio para el equipo
└── media/                 # Imágenes subidas desde el admin (se crea sola)
```

## URLs principales

| URL | Descripción |
|---|---|
| `/` | Página de inicio (hero, anuncios, carrusel) |
| `/catalogo/` | Catálogo con filtros y buscador |
| `/producto/<slug>/` | Detalle de un producto |
| `/registro/` | Crear cuenta (Alumno o Profesor) |
| `/login/` | Iniciar sesión |
| `/carrito/` | Ver y editar el carrito |
| `/mis-pedidos/` | Historial de apartados (requiere sesión) |
| `/admin/` | Panel de administración Django |

## Roles del sistema

### Alumno / Profesor
- Se registran con matrícula, correo y contraseña
- Los alumnos eligen carrera; los profesores no
- Pueden comprar (apartar) productos y ver su historial

### Administrador
- Accede a `/admin/` con el superusuario
- Gestiona productos, categorías, stock e imágenes
- Ve todos los pedidos y cambia su estado (Pendiente → Pagado → Entregado)

## Imágenes de productos

Cada producto tiene una imagen SVG de respaldo en `static/img/productos/<slug>.svg`.

Para usar fotos reales:
1. Entra a `/admin/catalogo/producto/`
2. Edita el producto
3. Sube la imagen en el campo **Imagen**

La imagen subida desde el admin tiene prioridad sobre la SVG estática.

## Material de estudio

En `static/notas/` hay explicaciones paso a paso del proyecto. Léelas en orden (00 → 08).

## Solución de problemas

**`python` no se reconoce**
→ Instala Python desde python.org y marca "Add to PATH".

**Error al activar venv**
→ Ejecuta: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Página en blanco o sin estilos**
→ Verifica que el servidor esté corriendo y que accedas a `http://127.0.0.1:8000/`.

**No aparecen productos**
→ Ejecuta `python manage.py migrate` de nuevo.

**Olvidé la contraseña del admin**
→ Crea otro superusuario con `python manage.py createsuperuser`.

## Equipo

Proyecto escolar — Cuarto semestre  
Universidad Autónoma de Occidente — Región El Fuerte
