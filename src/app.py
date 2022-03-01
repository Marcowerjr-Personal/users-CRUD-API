from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost/usuarios'
mongo = PyMongo(app)
# Primera coleccion


@app.route('/user/create', methods=['POST'])
def create_user():
    # recibir datos
    username = request.json['username']
    nombre = request.json['nombre']
    apellido1 = request.json['apellido1']
    apellido2 = request.json['apellido2']
    password = request.json['password']
    telefono = request.json['telefono']
    direccion = request.json['direccion']
    email = request.json['email']

    if username and nombre and apellido1 and apellido2 and password and telefono and direccion and email:
        newusuarios = mongo.db.users.find_one({'username': username})
        print(newusuarios)
        if newusuarios != None:
            print('usuario repetido')
            return usuario_repetido()
        else:
            valid_password = password_check(password)
            print('paspsapsapsda', valid_password)
            if valid_password == 'OK':
                password = generate_password_hash(password)
                mongo.db.users.insert_one({
                    'username': username,
                    'nombre': nombre,
                    'apellido1': apellido1,
                    'apellido2': apellido2,
                    'password': password,
                    'telefono': telefono,
                    'direccion': direccion,
                    'email': email
                })
                response = jsonify({
                    'message': 'Usuario creado con exito',
                    'status': 200
                })
                
                return response
            else:
                return invalid_password(valid_password)
    else:
        return Falta_campos()

@app.route('/user/login',methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']
    
    user = mongo.db.users.find_one({'username': username})
    
    if user == None:
        response = jsonify({
            'message': "El usuario: " + username + ", no existe",   
            'status': 404    
        })
        return response
    else:
        hashed_password = user['password']
        check_password = check_password_hash(hashed_password, password)
        if check_password:
            response = jsonify({
                'message': 'Usuario logueado con exito',
                'status': 200
            })
            return response
        else:
            response = jsonify({
                'message': 'La contraseña es incorrecta',
                'status': 401
            })
            return response
    


@app.route('/users/all', methods=['GET'])
def get_user():
    users = mongo.db.users.find()
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')


@app.route('/user/<id>', methods=['GET'])
def get_userid(id):
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')


@app.route('/delete/user/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'User' + id + 'was Deleted successfully'})
    return response


@app.route('/update/user/<id>', methods=['PUT'])
def update_user(id):
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if username and password and email:
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one({'_id': ObjectId(id)}, {'$set': {
            'username': username,
            'password': hashed_password,
            'email': email
        }})
        response = jsonify(
            {'message': 'User' + id + 'was update successfully'})
        return response

# Para recivir error y enviar avisos


@app.errorhandler(400)
def not_found(error=None):
    response = jsonify({
        'message': 'Resoure Not Found' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response


def Falta_campos(error=None):
    response = jsonify({
        'message': 'Le falta campos para la creación del usuario'
    })
    return response


def usuario_repetido(error=None):
    response = jsonify({
        'message': 'El usuario ya existe'
    })
    return response


def invalid_password(msg):
    response = jsonify({
        'message': msg
    })
    return response

def password_check(password):
    SpecialSym =['$', '@', '#', '%', '.']
    msg = 'OK'
    if len(password) < 8:
        msg = 'La contraseña le faltan caracteres, minimo 8 caracteres'
    if not any(char.isdigit() for char in password):
        msg = 'La contraseña debe contener al menos un numero'
    if not any(char.isupper() for char in password):
        msg = 'La contraseña debe contener al menos una mayúscula'
    if not any(char.islower() for char in password):
        msg = 'La contraseña debe contener al menos una minúscula'
    if not any(char in SpecialSym for char in password):
        msg = 'La contraseña debe contener al menos un caracter especial'
    
    return msg

if __name__ == "__main__":
    app.run(debug=True)
