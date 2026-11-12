from django.db.models import Q
from django.utils import timezone

from .models import Repartidor


def listar_repartidores(filtros=None):
    """Retorna todos los repartidores, con filtros opcionales.

    filtros: dict con claves opcionales 'zona', 'estado', 'vehiculo', 'buscar'.
    """
    filtros = filtros or {}
    queryset = Repartidor.objects.all()

    if filtros.get('zona'):
        queryset = queryset.filter(zona__icontains=filtros['zona'])
    if filtros.get('estado'):
        queryset = queryset.filter(estado=filtros['estado'])
    if filtros.get('vehiculo'):
        queryset = queryset.filter(vehiculo=filtros['vehiculo'])
    if filtros.get('buscar'):
        termino = filtros['buscar']
        queryset = queryset.filter(
            Q(nombre__icontains=termino)
            | Q(dni__icontains=termino)
            | Q(telefono__icontains=termino)
        )
    return queryset


def listar_disponibles(zona=None):
    """Repartidores disponibles para asignar un pedido, opcionalmente por zona."""
    queryset = Repartidor.objects.filter(estado=Repartidor.Estado.DISPONIBLE)
    if zona:
        queryset = queryset.filter(zona__icontains=zona)
    return queryset.order_by('-calificacion')


def obtener_repartidor(repartidor_id):
    """Retorna un repartidor por id o None si no existe."""
    try:
        return Repartidor.objects.get(pk=repartidor_id)
    except Repartidor.DoesNotExist:
        return None


def registrar_repartidor(datos):
    """Crea un repartidor a partir de un dict de datos validados."""
    return Repartidor.objects.create(**datos)


def actualizar_repartidor(repartidor, datos):
    """Actualiza los campos de un repartidor existente."""
    for campo, valor in datos.items():
        setattr(repartidor, campo, valor)
    repartidor.save()
    return repartidor


def eliminar_repartidor(repartidor):
    """Elimina un repartidor del sistema."""
    repartidor.delete()


def cambiar_estado(repartidor, nuevo_estado):
    """Cambia el estado del repartidor validando que sea un estado válido."""
    if nuevo_estado not in Repartidor.Estado.values:
        raise ValueError(f'Estado inválido: {nuevo_estado}')
    repartidor.estado = nuevo_estado
    repartidor.save()
    return repartidor


def marcar_entrega_completada(repartidor):
    """Suma una entrega completada y vuelve a dejarlo disponible."""
    repartidor.entregas_completadas += 1
    repartidor.estado = Repartidor.Estado.DISPONIBLE
    repartidor.save()
    return repartidor


def actualizar_calificacion(repartidor, nueva_nota):
    """Actualiza la calificación validando el rango 0-5."""
    if not 0 <= float(nueva_nota) <= 5:
        raise ValueError('La calificación debe estar entre 0 y 5.')
    repartidor.calificacion = nueva_nota
    repartidor.save()
    return repartidor


def estadisticas():
    """Resumen general para el dashboard del módulo."""
    hoy = timezone.now().date()
    total = Repartidor.objects.count()
    por_estado = {
        estado: Repartidor.objects.filter(estado=estado).count()
        for estado in Repartidor.Estado.values
    }
    por_vehiculo = {
        vehiculo: Repartidor.objects.filter(vehiculo=vehiculo).count()
        for vehiculo in Repartidor.Vehiculo.values
    }
    return {
        'total': total,
        'disponibles': por_estado.get(Repartidor.Estado.DISPONIBLE, 0),
        'por_estado': por_estado,
        'por_vehiculo': por_vehiculo,
        'generado': hoy,
    }
