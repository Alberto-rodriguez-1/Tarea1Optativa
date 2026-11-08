#!/usr/bin/env python3
"""
Genera el PDF de la Actividad 1 (formulario para añadir películas).

Uso:
    pip install reportlab pillow
    python generar_pdf.py --nombre "Ana García López" --repo "https://github.com/usuario/cineflask"

Coloca tus capturas en una carpeta llamada  capturas/  (junto a este script)
con estos nombres (.png o .jpg). Las que falten salen como recuadro pendiente:

    01_formulario_vacio
    02_formulario_error   (aviso rojo de Flask, ver nota de novalidate)
    03_formulario_relleno
    04_listado_exito
    05_base_datos
    06_terminal_arranque
    07_terminal_post
"""
import argparse
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Flowable, KeepTogether, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle,
                                PageBreak, Image)

try:
    from PIL import Image as PILImage
except ImportError:  # Pillow solo se usa para medir las capturas
    PILImage = None

AZUL = colors.HexColor("#1F3A5F")
GRIS = colors.HexColor("#6B7280")
FONDO_CODIGO = colors.HexColor("#F3F4F6")
BORDE = colors.HexColor("#D1D5DB")

ANCHO_UTIL = A4[0] - 4 * cm  # márgenes de 2 cm
MAX_LINEA_CODIGO = 100       # caracteres por línea de código (Courier 7,5 pt)

# ---------------------------------------------------------------- estilos
base = getSampleStyleSheet()
S = {
    "titulo": ParagraphStyle("titulo", parent=base["Title"], fontName="Helvetica-Bold",
                             fontSize=21, leading=26, textColor=AZUL, alignment=TA_CENTER,
                             spaceAfter=4),
    "subtitulo": ParagraphStyle("subtitulo", parent=base["Normal"], fontSize=11.5,
                                leading=15, textColor=GRIS, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold",
                         fontSize=15, leading=19, textColor=AZUL, spaceBefore=14,
                         spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
                         fontSize=11.5, leading=15, textColor=AZUL, spaceBefore=10,
                         spaceAfter=3),
    "p": ParagraphStyle("p", parent=base["Normal"], fontName="Helvetica", fontSize=10,
                        leading=14.5, spaceAfter=5),
    "peq": ParagraphStyle("peq", parent=base["Normal"], fontName="Helvetica", fontSize=8.5,
                          leading=11.5, textColor=GRIS),
    "celda": ParagraphStyle("celda", parent=base["Normal"], fontName="Helvetica",
                            fontSize=9, leading=12),
    "celda_b": ParagraphStyle("celda_b", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=9, leading=12, textColor=colors.white),
    "codigo": ParagraphStyle("codigo", parent=base["Code"], fontName="Courier",
                             fontSize=7.5, leading=9.6, backColor=FONDO_CODIGO,
                             borderColor=BORDE, borderWidth=0.6, borderPadding=6,
                             leftIndent=6, rightIndent=6, spaceBefore=6, spaceAfter=10),
    "pie_captura": ParagraphStyle("pie_captura", parent=base["Normal"], fontSize=8.5,
                                  leading=11, textColor=GRIS, alignment=TA_CENTER,
                                  spaceBefore=3, spaceAfter=10),
}


def p(texto, estilo="p"):
    return Paragraph(texto, S[estilo])


def codigo(texto):
    texto = texto.strip("\n")
    for n, linea in enumerate(texto.split("\n"), 1):
        if len(linea) > MAX_LINEA_CODIGO:
            sys.exit(f"Línea de código demasiado larga ({len(linea)} car.): {linea[:60]}...")
    return KeepTogether([Preformatted(texto, S["codigo"])])


# ---------------------------------------------------------------- capturas
class Pendiente(Flowable):
    """Recuadro discontinuo para las capturas que aún no se han añadido."""

    def __init__(self, texto, alto=6.2 * cm):
        super().__init__()
        self.texto, self.alto = texto, alto

    def wrap(self, aw, ah):
        self.ancho = aw
        return aw, self.alto

    def draw(self):
        c = self.canv
        c.setStrokeColor(GRIS)
        c.setDash(4, 3)
        c.setLineWidth(1)
        c.roundRect(0, 0, self.ancho, self.alto, 6)
        c.setDash()
        c.setFillColor(GRIS)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.ancho / 2, self.alto / 2 + 6, "CAPTURA PENDIENTE")
        c.setFont("Helvetica", 8.5)
        c.drawCentredString(self.ancho / 2, self.alto / 2 - 8, self.texto)


def buscar_imagen(carpeta, nombre):
    for ext in (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"):
        ruta = os.path.join(carpeta, nombre + ext)
        if os.path.isfile(ruta):
            return ruta
    return None


def captura(carpeta, nombre, titulo, instruccion):
    """Devuelve (flowables, encontrada)."""
    ruta = buscar_imagen(carpeta, nombre)
    if ruta and PILImage:
        w, h = PILImage.open(ruta).size
        max_w, max_h = ANCHO_UTIL, 11.5 * cm
        escala = min(max_w / w, max_h / h)
        img = Image(ruta, width=w * escala, height=h * escala)
        img.hAlign = "CENTER"
        caja = img
    elif ruta:
        img = Image(ruta, width=ANCHO_UTIL, height=9 * cm, kind="proportional")
        img.hAlign = "CENTER"
        caja = img
    else:
        caja = Pendiente(instruccion)
    return KeepTogether([caja, Paragraph(titulo, S["pie_captura"])]), bool(ruta)


# ---------------------------------------------------------------- documento
def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, 1.2 * cm, "Actividad 1 - Frameworks aplicados a la web - CineFlask")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def tabla(filas, anchos):
    datos = [[Paragraph(c, S["celda_b"]) for c in filas[0]]]
    datos += [[Paragraph(c, S["celda"]) for c in fila] for fila in filas[1:]]
    t = Table(datos, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_CODIGO]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def construir(nombre, repo, carpeta_capturas, salida):
    doc = SimpleDocTemplate(salida, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Actividad 1 - Formulario para añadir películas",
                            author=nombre)
    f = []

    # ------------------------------------------------------------ cabecera
    f += [p("Actividad 1: formulario para añadir películas", "titulo"),
          p("Frameworks aplicados a la web &nbsp;|&nbsp; UT 1 &nbsp;|&nbsp; Proyecto CineFlask",
            "subtitulo"),
          Spacer(1, 8),
          tabla([["Alumno/a", "Repositorio de GitHub"],
                 [nombre, repo]], [ANCHO_UTIL * 0.4, ANCHO_UTIL * 0.6])]

    # ------------------------------------------------------------ 1. intro
    f += [p("1. Objetivo y punto de partida", "h1"),
          p("CineFlask es una aplicación web hecha con <b>Flask</b> y una base de datos "
            "<b>SQLite</b>. Sigue el patrón MVC: <font name='Courier'>models.py</font> es el "
            "modelo (acceso a la BD), las plantillas Jinja2 de "
            "<font name='Courier'>frontend/templates</font> son la vista y "
            "<font name='Courier'>app.py</font> es el controlador (rutas)."),
          p("El objetivo es añadir una página con un <b>formulario HTML</b> (hecho con Jinja2 "
            "y extendiendo <font name='Courier'>base.html</font>) que permita insertar "
            "películas en la base de datos mediante el método <b>POST</b>."),
          p("El <font name='Courier'>app.py</font> de partida todavía usaba una lista de "
            "películas en memoria, por lo que antes del formulario hubo que conectar la "
            "aplicación a SQLite (paso 2). Estructura final del proyecto:"),
          codigo("""
proyecto-flask/
+-- frontend/
|   +-- static/            (css y js)
|   +-- templates/
|       +-- base.html        <- modificado (enlace en el navbar)
|       +-- add_movie.html   <- NUEVO (formulario)
|       +-- index.html, movies.html, movie_detail.html, about.html, contact.html
+-- backend/
|   +-- app.py             <- modificado (rutas + ruta nueva)
|   +-- models.py          <- modificado (función add_movie)
|   +-- proyecto.db        <- se crea automáticamente
+-- requirements.txt
+-- .gitignore             <- modificado (*.db)
""")]

    # ------------------------------------------------------------ 2. pasos
    f += [p("2. Descripción de los pasos seguidos", "h1")]

    f += [p("Paso 1: función para insertar una película (models.py)", "h2"),
          p("En el modelo se añadió <font name='Courier'>add_movie()</font>, que abre la "
            "conexión, ejecuta un <font name='Courier'>INSERT</font> y confirma con "
            "<font name='Courier'>commit()</font>. Se usan parámetros <b>?</b> en lugar de "
            "concatenar texto, para evitar ataques de SQL Injection."),
          codigo("""
def add_movie(title, director, year, genre, description, rating, poster_url):
    \"\"\"Inserta una película nueva en la base de datos\"\"\"
    conn = sqlite3.connect('proyecto.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO movies (title, director, year, genre, description, rating, poster_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, director, year, genre, description, rating, poster_url))

    conn.commit()
    conn.close()
""")]

    f += [p("Paso 2: conectar app.py a la base de datos", "h2"),
          p("Se importaron las funciones del modelo, se eliminó la lista de películas "
            "hardcodeada y se añadió <font name='Courier'>initialize_app()</font>, que crea "
            "las tablas y carga películas de ejemplo solo si la BD está vacía. Después, las "
            "rutas <font name='Courier'>/movies</font> y <font name='Courier'>/movies/&lt;id&gt;"
            "</font> pasaron a leer con <font name='Courier'>get_all_movies()</font> y "
            "<font name='Courier'>get_movie_by_id()</font>, y el formulario de contacto guarda "
            "los mensajes con <font name='Courier'>save_contact()</font>."),
          codigo("""
from models import (init_db, add_sample_movies, get_all_movies,
                    get_movie_by_id, save_contact, add_movie)

def initialize_app():
    init_db()
    if len(get_all_movies()) == 0:
        add_sample_movies()

@app.route('/movies', endpoint='movies')
def movies_list():
    movies = get_all_movies()
    return render_template('movies.html', movies=movies)
""")]

    f += [p("Paso 3: ruta del formulario (app.py)", "h2"),
          p("Se creó la ruta <font name='Courier'>/movies/add</font> con "
            "<font name='Courier'>methods=['GET', 'POST']</font>. Si la petición es GET se "
            "muestra el formulario vacío. Si es POST se recogen los datos con "
            "<font name='Courier'>request.form</font>, se validan (campos obligatorios, año "
            "numérico entre 1888 y 2100, puntuación entre 0 y 10), se guardan con "
            "<font name='Courier'>add_movie()</font> y se redirige al listado con un mensaje "
            "flash (patrón Post-Redirect-Get, que evita reenviar el formulario al recargar). "
            "Si hay un error, se vuelve a pintar el formulario conservando lo escrito. La "
            "función se llama <font name='Courier'>new_movie</font> para no chocar con la "
            "<font name='Courier'>add_movie</font> importada del modelo."),
          codigo("""
@app.route('/movies/add', methods=['GET', 'POST'])
def new_movie():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        director = request.form.get('director', '').strip()
        year = request.form.get('year', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        rating = request.form.get('rating', '').strip()
        poster_url = request.form.get('poster_url', '').strip()

        if not title or not director or not year or not genre or not description:
            flash('Rellena los campos obligatorios (título, director, año, género y '
                  'sinopsis).', 'error')
            return render_template('add_movie.html', form=request.form)

        try:
            year = int(year)
            rating = float(rating) if rating else 0.0
        except ValueError:
            flash('El año y la puntuación deben ser números.', 'error')
            return render_template('add_movie.html', form=request.form)

        if not 1888 <= year <= 2100:
            flash('El año no es válido.', 'error')
            return render_template('add_movie.html', form=request.form)

        if not 0 <= rating <= 10:
            flash('La puntuación debe estar entre 0 y 10.', 'error')
            return render_template('add_movie.html', form=request.form)

        add_movie(title, director, year, genre, description, rating, poster_url)

        flash(f'Película "{title}" añadida correctamente.', 'success')
        return redirect(url_for('movies'))

    return render_template('add_movie.html', form={})
""")]

    f += [p("Paso 4: plantilla add_movie.html (Jinja2)", "h2"),
          p("La plantilla nueva <b>extiende base.html</b> con "
            "<font name='Courier'>{% extends %}</font> y rellena los bloques "
            "<font name='Courier'>title</font> y <font name='Courier'>content</font>, "
            "reutilizando el navbar, el footer y los mensajes flash. El formulario usa "
            "<font name='Courier'>method=\"POST\"</font>, y los atributos "
            "<font name='Courier'>name</font> de cada campo coinciden con los "
            "<font name='Courier'>request.form.get()</font> de la ruta. Los "
            "<font name='Courier'>value=\"{{ form.get(...) }}\"</font> devuelven al usuario "
            "lo que escribió cuando hay un error. Campos: título, director, año, género, "
            "puntuación, sinopsis y URL del póster. Los atributos HTML "
            "<font name='Courier'>required</font>, <font name='Courier'>min</font> y "
            "<font name='Courier'>max</font> añaden una primera validación en el navegador; "
            "la validación de la ruta del paso 3 es la que protege realmente al servidor."),
          codigo("""
{% extends "base.html" %}
{% block title %}Añadir película - CineFlask{% endblock %}

{% block content %}
<form method="POST" action="{{ url_for('new_movie') }}">
    <input type="text" class="form-control" id="title" name="title"
           value="{{ form.get('title', '') }}" required>
    ... (resto de campos) ...
    <button type="submit" class="btn btn-primary">Guardar película</button>
</form>
{% endblock %}
""")]

    f += [p("Paso 5: enlace en el navbar (base.html)", "h2"),
          p("Se añadió un <font name='Courier'>&lt;li&gt;</font> nuevo en la barra de "
            "navegación de Bootstrap, justo después del enlace a «Películas». Usa "
            "<font name='Courier'>url_for('new_movie')</font>, por lo que este paso debe "
            "hacerse después de crear la ruta del paso 3."),
          codigo("""
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('new_movie') }}">
        <i class="fas fa-plus-circle me-1"></i>Añadir película
    </a>
</li>
""")]

    f += [p("Paso 6: .gitignore", "h2"),
          p("Para no subir la base de datos al repositorio se añadieron estas líneas:"),
          codigo("""
*.db
*.sqlite
""")]

    f += [p("Paso 7: ejecución de la aplicación", "h2"),
          p("Desde la carpeta <font name='Courier'>backend</font> (porque "
            "<font name='Courier'>proyecto.db</font> usa una ruta relativa):"),
          codigo("""
cd backend
python -m flask --app app run --debug
"""),
          p("Salida obtenida al arrancar:"),
          codigo("""
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 561-767-400
""")]

    f += [p("Paso 8: pruebas realizadas", "h2"),
          tabla([["Prueba", "Acción", "Resultado esperado"],
                 ["Acceso", "Pulsar «Añadir película» en el navbar",
                  "Se abre /movies/add con el formulario vacío."],
                 ["Validación (navegador)", "Dejar un campo obligatorio vacío o poner año 1500",
                  "El navegador bloquea el envío y muestra su propio aviso."],
                 ["Validación (servidor)",
                  "Añadir novalidate al formulario de forma temporal y enviar año 1500",
                  "Aviso rojo de Flask «El año no es válido.», el formulario conserva lo "
                  "escrito y no se inserta nada."],
                 ["Alta correcta", "Rellenar todos los campos obligatorios y enviar",
                  "Redirección (302) a /movies, aviso verde y la película en el listado."],
                 ["Detalle", "Pulsar «Ver detalles» de la película nueva",
                  "Se muestran todos sus datos."],
                 ["Persistencia", "Reiniciar el servidor y volver a /movies",
                  "La película sigue ahí (está guardada en proyecto.db)."]],
                [ANCHO_UTIL * 0.17, ANCHO_UTIL * 0.38, ANCHO_UTIL * 0.45])]

    # ------------------------------------------------------------ problemas
    f += [KeepTogether([p("3. Problemas encontrados y soluciones", "h1"),
          tabla([["Error", "Causa", "Solución"],
                 ["IndentationError: unindent does not match any outer indentation level "
                  "(app.py, función contact)",
                  "Al pegar el código, una línea quedó con distinta sangría que la anterior.",
                  "Reescribir el bloque con 4 espacios por nivel y convertir la indentación "
                  "del archivo a espacios."],
                 ["Error: Could not import 'backend.app'",
                  "Flask intentaba cargar un módulo con ese nombre al lanzarse desde la "
                  "carpeta backend.",
                  "Indicar la aplicación explícitamente: "
                  "<font name='Courier'>python -m flask --app app run --debug</font>."],
                 ["La BD no se inicializaba con flask run",
                  "El código dentro de <font name='Courier'>if __name__ == '__main__'</font> "
                  "no se ejecuta con <font name='Courier'>flask run</font>.",
                  "Llamar a <font name='Courier'>initialize_app()</font> fuera de ese "
                  "bloque, a nivel de módulo."],
                 ["No aparecía el aviso rojo de Flask con año 1500",
                  "El navegador valida antes (required, min, max) y el formulario no llega "
                  "a enviarse.",
                  "Añadir <font name='Courier'>novalidate</font> a la etiqueta "
                  "<font name='Courier'>&lt;form&gt;</font> solo para la prueba y quitarlo "
                  "después."]],
                [ANCHO_UTIL * 0.30, ANCHO_UTIL * 0.33, ANCHO_UTIL * 0.37])])]

    # ------------------------------------------------------------ capturas
    f += [p("4. Capturas de pantalla", "h1")]
    lista = [
        ("01_formulario_vacio", "Captura 1: formulario «Añadir película» vacío",
         "Abre /movies/add (se ve el navbar con el enlace nuevo)"),
        ("02_formulario_error", "Captura 2: error de validación del servidor (aviso rojo de Flask)",
         "Con novalidate temporal: año 1500, enviar y capturar el aviso"),
        ("03_formulario_relleno", "Captura 3: formulario relleno antes de enviar",
         "Rellena todos los campos de una película nueva"),
        ("04_listado_exito", "Captura 4: listado de películas con el aviso de éxito",
         "Tras enviar: /movies con el aviso verde y la película nueva"),
        ("05_base_datos", "Captura 5: base de datos con las películas añadidas",
         "DB Browser for SQLite: tabla movies de proyecto.db"),
        ("06_terminal_arranque", "Captura 6: terminal al arrancar el servidor",
         "Salida de python -m flask --app app run --debug"),
        ("07_terminal_post", "Captura 7: terminal con las peticiones al enviar el formulario",
         "Líneas GET /movies/add y POST /movies/add 302"),
    ]
    faltan = []
    for nombre_img, titulo, instruccion in lista:
        bloque, ok = captura(carpeta_capturas, nombre_img, titulo, instruccion)
        f.append(bloque)
        if not ok:
            faltan.append(nombre_img)

    # ------------------------------------------------------------ repo
    f += [p("5. Repositorio", "h1"),
          p(f"Código fuente de la aplicación con el formulario funcional: <b>{repo}</b>")]

    doc.build(f, onFirstPage=pie, onLaterPages=pie)
    return faltan


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", default="Nombre Apellidos",
                    help="Tu nombre y apellidos, por ejemplo \"Ana García López\"")
    ap.add_argument("--repo", default="https://github.com/USUARIO/REPOSITORIO",
                    help="URL de tu repositorio de GitHub")
    ap.add_argument("--capturas", default="capturas", help="Carpeta con las capturas")
    ap.add_argument("--salida", default=None, help="Nombre del PDF de salida")
    a = ap.parse_args()

    salida = a.salida or "Actividad_1_" + "_".join(a.nombre.split()) + ".pdf"
    faltan = construir(a.nombre, a.repo, a.capturas, salida)
    print(f"PDF generado: {salida}")
    if faltan:
        print("Capturas que faltan (salen como recuadro pendiente):")
        for n in faltan:
            print("  -", n)


if __name__ == "__main__":
    main()
