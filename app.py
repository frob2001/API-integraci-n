from flask import Flask, render_template, request, jsonify
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuración de la base de datos
DB_HOST = "35.193.168.157"
DB_NAME = "integracion_api"
DB_USER = "postgres"
DB_PASS = "admin"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

# Rutas CRUD para Estudiantes

@app.route('/estudiantes', methods=['GET'])
def get_estudiantes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM estudiantes;')
    estudiantes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(estudiantes)

@app.route('/estudiantes/<int:id>', methods=['GET'])
def get_estudiante(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM estudiantes WHERE id = %s;', (id,))
    estudiante = cursor.fetchone()
    cursor.close()
    conn.close()
    if estudiante:
        return jsonify(estudiante)
    else:
        return jsonify({'error': 'Estudiante no encontrado'}), 404

@app.route('/estudiantes', methods=['POST'])
def create_estudiante():
    nuevo_estudiante = request.get_json()
    nombre = nuevo_estudiante['nombre']
    apellido = nuevo_estudiante['apellido']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO estudiantes (nombre, apellido) VALUES (%s, %s) RETURNING *;',
                   (nombre, apellido))
    estudiante = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(estudiante), 201

@app.route('/estudiantes/<int:id>', methods=['PUT'])
def update_estudiante(id):
    actualizacion = request.get_json()
    nombre = actualizacion['nombre']
    apellido = actualizacion['apellido']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE estudiantes SET nombre = %s, apellido = %s WHERE id = %s RETURNING *;',
                   (nombre, apellido, id))
    estudiante = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if estudiante:
        return jsonify(estudiante)
    else:
        return jsonify({'error': 'Estudiante no encontrado'}), 404

@app.route('/estudiantes/<int:id>', methods=['DELETE'])
def delete_estudiante(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM estudiantes WHERE id = %s RETURNING *;', (id,))
    estudiante = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if estudiante:
        return jsonify({'message': 'Estudiante eliminado'})
    else:
        return jsonify({'error': 'Estudiante no encontrado'}), 404

# Rutas CRUD para Notas

@app.route('/estudiantes/<int:id>/notas', methods=['GET'])
def get_notas(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM notas WHERE estudiante_id = %s;', (id,))
    notas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notas)

@app.route('/notas', methods=['POST'])
def create_nota():
    nueva_nota = request.get_json()
    estudiante_id = nueva_nota['estudiante_id']
    curso = nueva_nota['curso']
    nota = nueva_nota['nota']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notas (estudiante_id, curso, nota) VALUES (%s, %s, %s) RETURNING *;',
                   (estudiante_id, curso, nota))
    nota = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(nota), 201

@app.route('/notas/<int:id>', methods=['PUT'])
def update_nota(id):
    actualizacion = request.get_json()
    curso = actualizacion['curso']
    nota = actualizacion['nota']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE notas SET curso = %s, nota = %s WHERE id = %s RETURNING *;',
                   (curso, nota, id))
    nota = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if nota:
        return jsonify(nota)
    else:
        return jsonify({'error': 'Nota no encontrada'}), 404

@app.route('/notas/<int:id>', methods=['DELETE'])
def delete_nota(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notas WHERE id = %s RETURNING *;', (id,))
    nota = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if nota:
        return jsonify({'message': 'Nota eliminada'})
    else:
        return jsonify({'error': 'Nota no encontrada'}), 404

# Ruta para la API de Pokémon

@app.route('/', methods=['GET', 'POST'])
def home():
    pokemon_info = None
    error_message = None

    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name').lower()
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}')
        
        if response.status_code == 200:
            data = response.json()
            pokemon_info = {
                'name': data['name'],
                'height': data['height'],
                'weight': data['weight'],
                'base_experience': data['base_experience'],
                'image_url': data['sprites']['front_default']
            }
        else:
            error_message = 'Pokemon not found. Please try again.'

    return render_template('index.html', pokemon=pokemon_info, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
