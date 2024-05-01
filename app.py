from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
from models import db, Pedido
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import http.client
import ssl
import json

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pedidos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Vinculación de db (SQLAlchemy) con la aplicación Flask y configuración de Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Función de Envío de Mensajes con UltraMsg
def enviar_mensaje_whatsapp(numero_telefono, mensaje):
    token = os.getenv('ULTRAMSG_TOKEN')
    instance_id = os.getenv('ULTRAMSG_INSTANCE_ID')
    conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
    payload = f"token={token}&to=+57{numero_telefono}&body={mensaje}"
    headers = {'content-type': "application/x-www-form-urlencoded"}

    conn.request("POST", f"/{instance_id}/messages/chat", payload.encode('utf-8'), headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    print(data.decode("utf-8"))


productos_map = {
    1: "Crookie Chocolate Negro",
    2: "Crokie Chocolate Blanco",
    3: "Cajita x 5 Mini Crookies"
}


@app.route('/')
def home():
    return "Bienvenido a la app de domicilios!"

@app.route('/pedido', methods=['POST'])
def recibir_pedido():
    if 'comprobante' in request.files:
        file = request.files['comprobante']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(basedir, 'uploads', filename)
            file.save(file_path)
            comprobante_url = request.host_url + 'uploads/' + filename
        else:
            comprobante_url = None
    else:
        comprobante_url = None

    data = request.form
    nuevo_pedido = Pedido(
        nombre_completo=data['nombre_completo'],
        numero_telefono=data['numero_telefono'],
        correo_electronico=data['correo_electronico'],
        direccion=data['direccion'],
        barrio=data['barrio'],
        productos=data['productos'],
        metodo_pago=data['metodo_pago'],
        comprobante_pago=comprobante_url
    )
    db.session.add(nuevo_pedido)
    db.session.commit()

    # Parsear los productos y crear un mensaje legible
    try:
        productos_json = json.loads(nuevo_pedido.productos)
        descripcion_productos = ", ".join(f"{productos_map[prod['id']]} ( x {prod['quantity']})" for prod in productos_json)
    except:
        descripcion_productos = "Información de productos no disponible"

    # Mensaje más detallado y amigable
    mensaje = (
        f"🐰 Hola {nuevo_pedido.nombre_completo}, ¡tu pedido fue recibido! 🐰\n\n"
        f"📦 Productos: {descripcion_productos}\n"
        f"🏠 Dirección de entrega: {nuevo_pedido.direccion}\n"
        f"💳 Método de pago: {nuevo_pedido.metodo_pago}\n\n"
        f"¡Gracias por elegirnos! 🐰"
    )
    enviar_mensaje_whatsapp(nuevo_pedido.numero_telefono, mensaje)
    
    return jsonify({"mensaje": "Pedido recibido y almacenado", "id": nuevo_pedido.id}), 201

@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    pedidos = Pedido.query.all()
    return jsonify([pedido.to_dict() for pedido in pedidos])


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(basedir, 'uploads'), filename)


@app.route('/pedido/<int:pedido_id>/estado', methods=['PUT'])
def actualizar_estado_pedido(pedido_id):
    data = request.get_json()
    pedido = Pedido.query.get(pedido_id)
    if pedido:
        estado_anterior = pedido.estado
        pedido.estado = data.get('estado', pedido.estado)
        db.session.commit()
        
        # Verifica si el estado cambió a "Pedido Enviado"
        if pedido.estado == "Pedido Enviado" and estado_anterior != "Pedido Enviado":
            # Mensaje de notificación de envío
            mensaje_envio = (
                f"🐰 Hola {pedido.nombre_completo}, ¡tu pedido ha sido enviado y está en camino! 🐰\n\n"
                f"🚚 Tu pedido pronto llegará a tu dirección.\n"
                f"📞 Para cualquier consulta, no dudes en contactarnos. ¡Gracias por escoger madriguera! 🐰"
            )
            enviar_mensaje_whatsapp(pedido.numero_telefono, mensaje_envio)

        return jsonify({"mensaje": "Estado del pedido actualizado", "estado": pedido.estado}), 200
    else:
        return jsonify({"mensaje": "Pedido no encontrado"}), 404
    

@app.cli.command('clear_db')
def clear_database():
    """Elimina todos los registros de la base de datos."""
    try:
        # Eliminar todos los registros de cada tabla
        num_rows_deleted = db.session.query(Pedido).delete()
        # Aquí puedes añadir más líneas si tienes otras tablas
        db.session.commit()
        print(f"Registros eliminados: {num_rows_deleted}")
    except Exception as e:
        print(f"Error al eliminar registros: {e}")
        db.session.rollback()
    

if __name__ == '__main__':
    app.run(debug=True)


    