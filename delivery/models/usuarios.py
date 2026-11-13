class Usuarios:
    def __init__(self, nombre, tipo_comida):
        self.nombre = nombre
        self.tipo_comida = tipo_comida
        self.menu = {}  # { "Plato": precio }
        self.mesas = {}  # { numero_mesa: "Libre" o "Reservada" }
        self.pedidos = []  # Lista de órdenes realizadas
