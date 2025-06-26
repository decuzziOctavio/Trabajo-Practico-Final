import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

def crearTabla():
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nombre TEXT UNIQUE,
        email TEXT,
        objetivo TEXT,
        restricciones TEXT,
        peso REAL,
        altura REAL,
        planpremium BOOLEAN
    )''')
    conexion.commit()
    conexion.close()

crearTabla()


@app.route('/usuarios', methods=['POST'])
def registro_usuario():
    data = request.get_json()
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('''INSERT INTO usuarios 
        (id, nombre, email, objetivo, restricciones, peso, altura, planpremium) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (data['id'], data['nombre'], data['email'], data['objetivo'], data['restricciones'],
         data['peso'], data['altura'], data['planpremium']))
    conexion.commit()
    conexion.close()
    return jsonify({'mensaje': 'Usuario creado'}), 201

# Actualizar peso de un usuario
@app.route('/usuarios/<int:id>/peso', methods=['PUT'])
def modificar_peso(id):
    nuevo_peso = request.json.get('peso')
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('UPDATE usuarios SET peso = ? WHERE id = ?', (nuevo_peso, id))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'mensaje': 'Peso actualizado'}), 200

# Eliminar usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'mensaje': 'Usuario eliminado'}), 200

# Listar todos los usuarios
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios')
    filas = cursor.fetchall()
    columnas = []
    for descripcion in cursor.description:
        nombre_columna = descripcion[0]
        columnas.append(nombre_columna)
    usuarios = []
    for fila in filas:
        usuario = {}
        for i in range(len(columnas)):
            usuario[columnas[i]] = fila[i]
        usuarios.append(usuario)
    conexion.close()
    return jsonify(usuarios)

#Buscar usuario por id
@app.route('/usuarios/<int:id>', methods=['GET'])
def buscar_usuario(id):
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?',(id,))
    fila = cursor.fetchone()
    columnas = cursor.description
    conexion.close()
    if fila is None:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    usuario = {}
    for i in range(len(columnas)):
        nombre_columna = columnas[i][0]
        valor = fila[i]
        usuario[nombre_columna] = valor
    return jsonify(usuario), 200

#Actualizar objetivo
@app.route('/usuarios/<int:id>/objetivo',methods=['PUT'])
def cambio_objetivo(id):
    nuevo_obj = request.json.get('objetivo')
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('UPDATE usuarios SET objetivo = ? WHERE id = ?',(nuevo_obj,id))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'mensaje': 'Objetivo Actualizado actualizado'}), 200

#Actualizar Plan
@app.route('/usuarios/<int:id>/planpremium', methods=['PUT'])
def cambiar_planpremium(id):
    nuevo_plan = request.json.get('planpremium')
    conexion = sqlite3.connect('eatwise.db')
    cursor = conexion.cursor()
    cursor.execute('UPDATE usuarios SET planpremium = ? WHERE id = ?', (nuevo_plan, id))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'mensaje': 'Plan actualizado'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)

print("terminado!")