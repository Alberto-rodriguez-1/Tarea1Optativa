# Proyecto CineFlask — Reestructuración

Estructura propuesta:

- `frontend/` — HTML, CSS y JS (assets públicos y templates Jinja)
  - `templates/` — archivos `.html` (Jinja2)
  - `static/` — `css/` y `js/`

- `backend/` — servidor Flask
  - `app.py` — aplicación Flask mínima de ejemplo
  - `script_py_orig.py` y `script1_py_orig.py` — copias de los scripts originales

Cómo lanzar el proyecto (macOS / zsh):

1) Crear y activar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Instalar dependencias:

```bash
pip install -r requirements.txt
```

3) Ejecutar la app Flask (desde la carpeta `backend`):

```bash
cd backend
python app.py
```

4) Abrir en el navegador:

- `http://127.0.0.1:5000/` — Inicio
- `http://127.0.0.1:5000/movies` — Catálogo
- `http://127.0.0.1:5000/about` — Sobre
- `http://127.0.0.1:5000/contact` — Contacto

Notas:
- Los templates y los assets están en `frontend/`. `backend/app.py` está configurado para usar `../frontend/templates` y `../frontend/static`.
