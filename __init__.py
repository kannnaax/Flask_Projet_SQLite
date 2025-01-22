from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html') #Deploy#Deploy2

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

    # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password':  # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement

# Ajouter un livre
@app.route('/add_book', methods=['POST'])
def add_book():
    if not est_authentifie() or not session.get('admin'):
        return redirect(url_for('authentification'))
    
    title = request.form['title']
    author = request.form['author']
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, available) VALUES (?, ?, ?)", (title, author, 1))
    conn.commit()
    conn.close()
    return redirect('/consultation_books')  # Rediriger vers la page des livres après l'ajout

# Lister tous les livres disponibles
@app.route('/consultation_books', methods=['GET'])
def consultation_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE available = 1")
    books = cursor.fetchall()
    conn.close()
    return render_template('consult_books.html', books=books)

# Emprunter un livre
@app.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    if book and book[0] == 1:  # Livre disponible
        cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        return redirect('/consultation_books')
    else:
        conn.close()
        return "<h3>Ce livre est déjà emprunté.</h3>"

# Rechercher un livre par titre
@app.route('/search_book', methods=['GET'])
def search_book():
    title = request.args.get('title')
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + title + '%',))
    books = cursor.fetchall()
    conn.close()
    return render_template('consult_books.html', books=books)

# Ajouter un utilisateur (admin)
@app.route('/add_user', methods=['POST'])
def add_user():
    if not est_authentifie() or not session.get('admin'):
        return redirect(url_for('authentification'))
    
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return redirect('/consultation_users')

# Lister tous les utilisateurs (admin)
@app.route('/consultation_users', methods=['GET'])
def consultation_users():
    if not est_authentifie() or not session.get('admin'):
        return redirect(url_for('authentification'))
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('consult_users.html', users=users)

if __name__ == "__main__":
    app.run(debug=True)
