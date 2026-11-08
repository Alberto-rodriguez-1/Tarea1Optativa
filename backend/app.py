from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import (init_db, add_sample_movies, get_all_movies,
                    get_movie_by_id, save_contact, add_movie)

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'dev-secret'

def initialize_app():
    """Inicializa la base de datos y añade datos de ejemplo solo si está vacía"""
    init_db()
    if len(get_all_movies()) == 0:
        add_sample_movies()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/movies', endpoint='movies')
def movies_list():
    movies = get_all_movies()
    return render_template('movies.html', movies=movies)

@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie = get_movie_by_id(movie_id)
    if not movie:
        abort(404)
    return render_template('movie_detail.html', movie=movie)
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
            flash('Rellena los campos obligatorios (título, director, año, género y sinopsis).', 'error')
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

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        if not name or not email or not message:
            flash('Por favor rellena los campos requeridos.', 'error')
            return redirect(url_for('contact'))
        save_contact(name, email, subject, message)
        flash('Gracias por tu mensaje — te responderemos pronto.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


initialize_app()

if __name__ == '__main__':
    app.run(debug=True)
