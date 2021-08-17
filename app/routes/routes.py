from itertools import permutations
from os import access
from flask import Blueprint, json,request,jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models.models import Usuario,Pelicula
from database import db
from schema.schema import pelicula_schema,peliculas_schema
import bcrypt
blue_print = Blueprint('app',__name__)

#Inicio
@blue_print.route('/',methods=['GET'])
def inicio():
    return jsonify(respuesta='Rest API con PYthon, flask y MySQL')

@blue_print.route('/auth/registrar',methods=['POST'])
def rergistrar_usuario():
    try:
        #obtener valores
        usuario = request.json.get('usuario')
        clave = request.json.get('clave')

        if not usuario or not clave:
            return jsonify(respuesta='Campos invalidos'),400

        existe_usuario = Usuario.query.filter_by(usuario=usuario).first()
        if existe_usuario:
            return jsonify(respuesta='Ya existe usuario'),400
        #encriptamos
        clave_encriptada = bcrypt.hashpw(clave.encode('utf-8'),bcrypt.gensalt())
        #creamos modelo a guardar
        nuevo_usuario = Usuario(usuario,clave_encriptada)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify(respuesta='creado con exito'),201

    except Exception:
            return jsonify(respuesta='Error en peticion'),500

#ruta de inicio
@blue_print.route('/auth/login',methods=['POST'])
def iniciar_sesion():
    try:
         #obtener valores
        usuario = request.json.get('usuario')
        clave = request.json.get('clave')

        if not usuario or not clave:
            return jsonify(respuesta='Campos invalidos'),400
        existe_usuario = Usuario.query.filter_by(usuario=usuario).first()
        if not existe_usuario:
            return jsonify(respuesta='Usuario no encontrado'),404
        es_clave_valida = bcrypt.checkpw(clave.encode('utf-8'),existe_usuario.clave.encode('utf-8'))
        
        #validamos claves
        if es_clave_valida:
            access_token = create_access_token(identity=usuario)
            return jsonify(access_token=access_token),200
        return jsonify(respuesta='usuario o clave incorrecto'),404
        
    except Exception:
            return jsonify(respuesta='Error en peticion'),500
"""Rutas Protegidas"""
#Crea pelicula
@blue_print.route('/api/peliculas',methods=['POST'])
@jwt_required()
def crear_pelicula():
    try:
        nombre = request.json['nombre']
        estreno = request.json['estreno']
        director = request.json['director']
        reparto = request.json['reparto']
        genero = request.json['genero']
        sinopsis = request.json['sinopsis']

        nueva_pelicula = Pelicula(nombre,estreno,director,reparto,genero,sinopsis)
        db.session.add(nueva_pelicula)
        db.session.commit()
        return jsonify(respuesta='pelicula cargada con exito'),201
    except Exception:
            return jsonify(respuesta='Error en peticion'),500

#Obtener pelicula
@blue_print.route('/api/peliculas',methods=['GET'])
@jwt_required()
def obteher_peliculas():
    try:
        peliculas = Pelicula.query.all()
        respuesta = peliculas_schema.dump(peliculas)
        return peliculas_schema.jsonify(respuesta),200
    except Exception:
            return jsonify(respuesta='Error en peticion'),500
    
#Obtener pelicula id
@blue_print.route('/api/peliculas/<int:id>',methods=['GET'])
@jwt_required()
def obteher_pelicula_id(id):
    try:
        pelicula = Pelicula.query.get(id)
        respuesta = pelicula_schema.dump(pelicula)
        return pelicula_schema.jsonify(respuesta),200
    except Exception:
            return jsonify(respuesta='Error en peticion'),500

#update pelicula
@blue_print.route('/api/peliculas/<int:id>',methods=['PUT'])
@jwt_required()
def actualizar_pelicula(id):
    try:
        pelicula = Pelicula.query.get(id)
        if not pelicula:
            return jsonify(respuesta='no se encontro pelicula'),404
        
        pelicula.nombre = pelicula.json['nombre']
        pelicula.estreno = request.json['estreno']
        pelicula.director = request.json['director']
        pelicula.reparto = request.json['reparto']
        pelicula.genero = request.json['genero']
        pelicula.sinopsis = request.json['sinopsis']

      
        db.session.commit()
        return jsonify(respuesta='pelicula update con exito'),200
    except Exception:
            return jsonify(respuesta='Error en peticion'),500

#borrar pelicula id
@blue_print.route('/api/peliculas/<int:id>',methods=['DELETE'])
@jwt_required()
def eliminar_pelicula_id(id):
    try:
        pelicula = Pelicula.query.get(id)
        if not pelicula:
             return jsonify(respuesta='Peli no encontrada'),404

        db.session.delete(pelicula)
        db.session.commit()
        return jsonify(respuesta='Se borro peli con exito'),200
    except Exception:
            return jsonify(respuesta='Error en peticion'),500
