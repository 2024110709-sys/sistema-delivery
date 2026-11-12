class Restaurant:
    def __init__(self, nombre, tipo_comida):
        self.nombre = nombre
        self.tipo_comida = tipo_comida
        self.menu = {}  # { "Plato": precio }
        self.mesas = {}  # { numero_mesa: "Libre" o "Reservada" }
        self.pedidos = []  # Lista de órdenes realizadas

    def agregar_al_menu(self, plato, precio):
        self.menu[plato] = precio
        print(f"Plato '{plato}' agregado al menú por ${precio}.")

    def imprimir_menu(self):
        print(f"\n--- Menú de {self.nombre} ---")
        if not self.menu:
            print("El menú está vacío.")
        for plato, precio in self.menu.items():
            print(f"- {plato}: ${precio}")

    def reservar_mesa(self, numero_mesa):
        if numero_mesa in self.mesas:
            if self.mesas[numero_mesa] == "Libre":
                self.mesas[numero_mesa] = "Reservada"
                print(f"Mesa {numero_mesa} reservada con éxito.")
            else:
                print(f"La mesa {numero_mesa} ya está ocupada/reservada.")
        else:
            self.mesas[numero_mesa] = "Reservada"
            print(f"Mesa {numero_mesa} registrada y reservada.")

    def tomar_pedido(self, numero_mesa, platos_solicitados):
        pedido = {
            "mesa": numero_mesa,
            "platos": platos_solicitados,
            "total": sum(self.menu.get(p, 0) for p in platos_solicitados)
        }
        self.pedidos.append(pedido)
        print(f"Pedido registrado para la mesa {numero_mesa}. Total: ${pedido['total']}")

    def imprimir_pedidos(self):
        print(f"\n--- Pedidos en {self.nombre} ---")
        if not self.pedidos:
            print("No hay pedidos registrados.")
        for i, pedido in enumerate(self.pedidos, 1):
            print(f"Pedido #{i} | Mesa: {pedido['mesa']} | Platos: {', '.join(pedido['platos'])} | Total: ${pedido['total']}")


# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Crear una instancia del restaurante
    mi_restaurante = Restaurant("Sabor Peruano", "Criolla")

    # Agregar elementos al menú
    mi_restaurante.agregar_al_menu("Ceviche", 35.0)
    mi_restaurante.agregar_al_menu("Lomo Saltado", 40.0)
    mi_restaurante.agregar_al_menu("Chicha Morada", 8.0)

    # Imprimir menú
    mi_restaurante.imprimir_menu()

    # Reservar mesas
    mi_restaurante.reservar_mesa(1)
    mi_restaurante.reservar_mesa(2)

    # Tomar pedidos
    mi_restaurante.tomar_pedido(1, ["Ceviche", "Chicha Morada"])
    mi_restaurante.tomar_pedido(2, ["Lomo Saltado", "Chicha Morada"])

    # Ver listado de pedidos
    mi_restaurante.imprimir_pedidos()
