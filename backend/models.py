import sqlite3
from datetime import datetime

def init_db():
    """Inicializa la base de datos con tablas necesarias"""
    conn = sqlite3.connect('proyecto.db')
    cursor = conn.cursor()
    
    # Tabla películas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            director TEXT,
            year INTEGER,
            genre TEXT,
            description TEXT,
            rating REAL DEFAULT 0.0,
            poster_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla contactos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

def add_sample_movies():
    """Añade películas de ejemplo para tener datos de prueba"""
    sample_movies = [
        ("El Padrino", "Francis Ford Coppola", 1972, "Drama", 
         "La historia de una familia mafiosa italiana en Nueva York", 9.2, 
         "https://m.media-amazon.com/images/I/41+H8LjrDeL._AC_.jpg"),
        ("Pulp Fiction", "Quentin Tarantino", 1994, "Crimen", 
         "Historias entrelazadas en Los Angeles", 8.9,
         "https://m.media-amazon.com/images/I/71c05lTE03L._AC_SY679_.jpg"),
        ("El Señor de los Anillos", "Peter Jackson", 2001, "Fantasía", 
         "La aventura épica de Frodo y el anillo único", 8.8,
         "https://m.media-amazon.com/images/I/91jRdlI6rCL._AC_SY679_.jpg")
    ]
    
    conn = sqlite3.connect('proyecto.db')
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO movies (title, director, year, genre, description, rating, poster_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_movies)
    
    conn.commit()
    conn.close()
    print("✅ Películas de ejemplo añadidas")

def get_all_movies():
    """Obtiene todas las películas de la base de datos"""
    conn = sqlite3.connect('proyecto.db')
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM movies ORDER BY created_at DESC')
    movies = cursor.fetchall()
    
    conn.close()
    return movies

def get_movie_by_id(movie_id):
    """Obtiene una película específica por ID"""
    conn = sqlite3.connect('proyecto.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    
    conn.close()
    return movie

def save_contact(name, email, subject, message):
    """Guarda un mensaje de contacto en la base de datos"""
    conn = sqlite3.connect('proyecto.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contacts (name, email, subject, message)
        VALUES (?, ?, ?, ?)
    ''', (name, email, subject, message))
    
    conn.commit()
    conn.close()
    print(f"✅ Contacto guardado: {name}")
