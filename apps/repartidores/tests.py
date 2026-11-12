from django.test import TestCase
from django.urls import reverse

from .models import Repartidor
from . import services


def crear_repartidor_base(**overrides):
    """Helper para crear repartidores de prueba."""
    datos = {
        'nombre': 'Freddy Ramos',
        'dni': '12345678',
        'telefono': '999888777',
        'vehiculo': Repartidor.Vehiculo.MOTO,
        'placa': 'AB-1234',
        'zona': 'Lima Norte',
        'estado': Repartidor.Estado.DISPONIBLE,
    }
    datos.update(overrides)
    return Repartidor.objects.create(**datos)


class RepartidorModelTests(TestCase):
    """Pruebas del modelo Repartidor."""

    def test_creacion_repartidor(self):
        repartidor = crear_repartidor_base()
        self.assertEqual(Repartidor.objects.count(), 1)
        self.assertEqual(str(repartidor), 'Freddy Ramos (Moto)')

    def test_dni_unico(self):
        crear_repartidor_base(dni='87654321')
        with self.assertRaises(Exception):
            crear_repartidor_base(nombre='Otro', dni='87654321')

    def test_estado_por_defecto_disponible(self):
        repartidor = crear_repartidor_base()
        self.assertTrue(repartidor.esta_disponible)

    def test_calificacion_por_defecto(self):
        repartidor = crear_repartidor_base()
        self.assertEqual(repartidor.calificacion, 5.00)


class RepartidorServicesTests(TestCase):
    """Pruebas de la capa de servicios."""

    def setUp(self):
        self.repartidor = crear_repartidor_base()

    def test_listar_con_filtro_zona(self):
        crear_repartidor_base(nombre='Otro repartidor', dni='11112222', zona='Lima Centro')
        resultados = services.listar_repartidores({'zona': 'Lima Norte'})
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first(), self.repartidor)

    def test_listar_busqueda_por_nombre(self):
        resultados = services.listar_repartidores({'buscar': 'freddy'})
        self.assertEqual(resultados.count(), 1)

    def test_listar_disponibles_ordenado_por_calificacion(self):
        crear_repartidor_base(
            nombre='Bajo puntaje', dni='22223333',
            estado=Repartidor.Estado.DISPONIBLE, calificacion=2.50,
        )
        crear_repartidor_base(
            nombre='Ocupado', dni='33334444',
            estado=Repartidor.Estado.EN_PEDIDO, calificacion=4.90,
        )
        disponibles = services.listar_disponibles()
        self.assertEqual(disponibles.count(), 2)
        self.assertEqual(disponibles.first().calificacion, 5.00)

    def test_cambiar_estado_valido(self):
        actualizado = services.cambiar_estado(self.repartidor, Repartidor.Estado.DESCANSO)
        self.assertEqual(actualizado.estado, Repartidor.Estado.DESCANSO)

    def test_cambiar_estado_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            services.cambiar_estado(self.repartidor, 'volando')

    def test_marcar_entrega_completada(self):
        services.cambiar_estado(self.repartidor, Repartidor.Estado.EN_PEDIDO)
        resultado = services.marcar_entrega_completada(self.repartidor)
        self.assertEqual(resultado.entregas_completadas, 1)
        self.assertEqual(resultado.estado, Repartidor.Estado.DISPONIBLE)

    def test_actualizar_calificacion_valida(self):
        resultado = services.actualizar_calificacion(self.repartidor, 4.5)
        self.assertEqual(resultado.calificacion, 4.5)

    def test_actualizar_calificacion_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            services.actualizar_calificacion(self.repartidor, 7)

    def test_obtener_repartidor_inexistente(self):
        self.assertIsNone(services.obtener_repartidor(9999))

    def test_estadisticas(self):
        crear_repartidor_base(nombre='Extra', dni='44445555', estado=Repartidor.Estado.INACTIVO)
        datos = services.estadisticas()
        self.assertEqual(datos['total'], 2)
        self.assertEqual(datos['disponibles'], 1)


class RepartidorViewTests(TestCase):
    """Pruebas de vistas (flujos de pantalla)."""

    def setUp(self):
        self.repartidor = crear_repartidor_base()

    def test_lista_repartidores(self):
        respuesta = self.client.get(reverse('repartidores:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Freddy Ramos')

    def test_detalle_repartidor(self):
        respuesta = self.client.get(
            reverse('repartidores:detalle', args=[self.repartidor.id])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '999888777')

    def test_crear_repartidor_post_valido(self):
        respuesta = self.client.post(reverse('repartidores:crear'), {
            'nombre': 'Nuevo Repartidor',
            'dni': '55556666',
            'telefono': '911222333',
            'email': '',
            'vehiculo': 'bicicleta',
            'placa': '',
            'zona': 'Lima Centro',
            'estado': 'disponible',
        })
        self.assertRedirects(respuesta, reverse('repartidores:lista'))
        self.assertTrue(Repartidor.objects.filter(dni='55556666').exists())

    def test_crear_repartidor_dni_invalido(self):
        respuesta = self.client.post(reverse('repartidores:crear'), {
            'nombre': 'Malo',
            'dni': '123',  # DNI incompleto
            'telefono': '911222333',
            'vehiculo': 'bicicleta',
            'zona': '',
            'estado': 'disponible',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '8 dígitos')
        self.assertFalse(Repartidor.objects.filter(nombre='Malo').exists())

    def test_crear_repartidor_placa_requerida_para_moto(self):
        respuesta = self.client.post(reverse('repartidores:crear'), {
            'nombre': 'Sin placa',
            'dni': '66667777',
            'telefono': '911222444',
            'vehiculo': 'auto',
            'placa': '',
            'zona': '',
            'estado': 'disponible',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'placa')
        self.assertFalse(Repartidor.objects.filter(dni='66667777').exists())

    def test_editar_repartidor(self):
        respuesta = self.client.post(
            reverse('repartidores:editar', args=[self.repartidor.id]),
            {
                'nombre': 'Freddy Ramos Actualizado',
                'dni': '12345678',
                'telefono': '999888777',
                'email': 'freddy@delivery.com',
                'vehiculo': 'auto',
                'placa': 'XY-9999',
                'zona': 'Lima Este',
                'estado': 'disponible',
            }
        )
        self.assertRedirects(
            respuesta, reverse('repartidores:detalle', args=[self.repartidor.id])
        )
        self.repartidor.refresh_from_db()
        self.assertEqual(self.repartidor.nombre, 'Freddy Ramos Actualizado')
        self.assertEqual(self.repartidor.placa, 'XY-9999')

    def test_eliminar_repartidor(self):
        respuesta = self.client.post(
            reverse('repartidores:eliminar', args=[self.repartidor.id])
        )
        self.assertRedirects(respuesta, reverse('repartidores:lista'))
        self.assertEqual(Repartidor.objects.count(), 0)

    def test_cambiar_estado_desde_pantalla(self):
        respuesta = self.client.post(
            reverse('repartidores:cambiar_estado', args=[self.repartidor.id]),
            {'estado': Repartidor.Estado.EN_PEDIDO},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.repartidor.refresh_from_db()
        self.assertEqual(self.repartidor.estado, Repartidor.Estado.EN_PEDIDO)

    def test_cambiar_estado_invalido_muestra_error(self):
        respuesta = self.client.post(
            reverse('repartidores:cambiar_estado', args=[self.repartidor.id]),
            {'estado': 'volando'},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.repartidor.refresh_from_db()
        self.assertEqual(self.repartidor.estado, Repartidor.Estado.DISPONIBLE)
