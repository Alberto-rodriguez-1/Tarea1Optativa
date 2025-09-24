from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'dev-secret'

# Datos de ejemplo en memoria
movies = [
    {
        'id': 1,
        'title': 'The Shawshank Redemption',
        'director': 'Frank Darabont',
        'year': 1994,
        'genre': 'Drama',
        'rating': 9.3,
        'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
        'poster_url': None
    },
    {
        'id': 2,
        'title': 'The Godfather',
        'director': 'Francis Ford Coppola',
        'year': 1972,
        'genre': 'Crime',
        'rating': 9.2,
        'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
        'poster_url': None
    }
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/movies', endpoint='movies')
def movies_list():
    return render_template('movies.html', movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        abort(404)
    return render_template('movie_detail.html', movie=movie)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash('Por favor rellena los campos requeridos.', 'error')
            return redirect(url_for('contact'))
        flash('Gracias por tu mensaje — te responderemos pronto.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
