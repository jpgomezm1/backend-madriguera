from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # Importa pytz para manejar zonas horarias

# Inicialización de SQLAlchemy
db = SQLAlchemy()

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100))
    numero_telefono = db.Column(db.String(20))
    correo_electronico = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    barrio = db.Column(db.String(100))
    productos = db.Column(db.String(500))
    metodo_pago = db.Column(db.String(50))
    comprobante_pago = db.Column(db.String(200))
    fecha_hora = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/Bogota')))
    estado = db.Column(db.String(50), default='Pedido Recibido')

    def __repr__(self):
        return f'<Pedido {self.nombre_completo}>'

    def to_dict(self):
        # Asegúrate de que la conversión a string también considere la zona horaria si es necesario
        local_date = self.fecha_hora.astimezone(pytz.timezone('America/Bogota')) if self.fecha_hora else 'Sin fecha registrada'
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'numero_telefono': self.numero_telefono,
            'correo_electronico': self.correo_electronico,
            'direccion': self.direccion,
            'barrio': self.barrio,
            'productos': self.productos,
            'metodo_pago': self.metodo_pago,
            'comprobante_pago': self.comprobante_pago,
            'fecha_hora': local_date.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_hora else 'Sin fecha registrada',
            'estado': self.estado
        }



