# 01 - Arquitectura general

## La idea en una frase

> El HTML está "vacío" y el JavaScript le pide datos a Django para llenarlo.

## Las dos partes del proyecto

```
┌─────────────────────────┐         ┌─────────────────────────┐
│      FRONTEND           │         │       BACKEND           │
│  (lo que ve el usuario) │         │   (Django + SQLite)     │
│                         │         │                         │
│  - HTML puro            │  fetch  │  - Vistas en Python     │
│  - CSS                  │ ──────► │  - Modelos              │
│  - JavaScript           │ ◄────── │  - Base de datos        │
│                         │  JSON   │  - Admin                │
└─────────────────────────┘         └─────────────────────────┘
```

### Frontend
- Está en `templates/*.html`, `static/css/` y `static/js/`.
- Es **HTML normal**: nada de `{% %}` ni `{{ }}`.
- JavaScript se encarga de:
  - Pintar el navbar y el footer.
  - Pedir datos a Django (en la Fase 4 en adelante).
  - Manejar el carrito en `localStorage`.

### Backend
- Está en las apps `usuarios/`, `catalogo/`, `pedidos/`.
- Tiene **dos tipos de vistas**:
  1. **Vistas de página**: solo regresan el HTML sin meterle datos.
     Ejemplo: `def pagina_inicio(request): return render(request, 'index.html')`
  2. **Vistas de API** (las haremos en Fase 4): regresan JSON.
     Ejemplo: `def api_productos(request): return JsonResponse(...)`

## ¿Por qué hacerlo así?

| Razón | Beneficio |
|---|---|
| El HTML no tiene sintaxis rara | Lo entendemos completo, igual que en proyectos web normales. |
| El JavaScript sí maneja datos | Aprendemos `fetch()` y APIs reales (es lo que se usa en la industria). |
| Django solo entrega datos | Su código de Python queda más limpio y reusable. |
| Frontend y backend separados | Si mañana hacemos una app móvil, reusamos la misma API. |

## Flujo cuando un alumno entra al catálogo (lo veremos en Fase 4)

1. El navegador pide `http://127.0.0.1:8000/`.
2. Django ejecuta la vista `pagina_inicio()`.
3. Django responde con el archivo `templates/index.html` tal cual (sin datos).
4. El navegador descarga también el CSS y los `.js`.
5. `main.js` arranca y llama a `inicializarNavbar()` e `inicializarFooter()`.
6. Más tarde, otro JS hace `fetch('/api/productos/')` para pedir productos.
7. Django responde con un JSON tipo `[{nombre: "Playera", precio: 250}, ...]`.
8. El JS recorre el JSON y crea las tarjetas dentro de `<div id="lista-productos">`.

## ¿Y el panel admin?

Eso es la única parte donde Django sí genera HTML por su cuenta (no la tocamos
nosotros, ya viene hecha). Por eso `http://127.0.0.1:8000/admin/` se ve distinto
al resto del sitio. Es 100% Django, sin nuestro CSS.
