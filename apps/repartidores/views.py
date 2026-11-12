from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import RepartidorForm
from .models import Repartidor
from . import services


def lista_repartidores(request):
    """Listado de repartidores con filtros (zona, estado, búsqueda)."""
    filtros = {
        'buscar': request.GET.get('buscar', ''),
        'estado': request.GET.get('estado', ''),
        'vehiculo': request.GET.get('vehiculo', ''),
        'zona': request.GET.get('zona', ''),
    }
    repartidores = services.listar_repartidores(filtros)
    contexto = {
        'repartidores': repartidores,
        'filtros': filtros,
        'estados': Repartidor.Estado.choices,
        'vehiculos': Repartidor.Vehiculo.choices,
    }
    return render(request, 'repartidores/lista.html', contexto)


def detalle_repartidor(request, repartidor_id):
    """Ficha detallada de un repartidor."""
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    return render(request, 'repartidores/detalle.html', {'repartidor': repartidor})


def crear_repartidor(request):
    """Registro de un nuevo repartidor."""
    if request.method == 'POST':
        form = RepartidorForm(request.POST)
        if form.is_valid():
            services.registrar_repartidor(form.cleaned_data)
            messages.success(request, 'Repartidor registrado correctamente.')
            return redirect('repartidores:lista')
    else:
        form = RepartidorForm()
    return render(request, 'repartidores/formulario.html', {
        'form': form,
        'titulo': 'Registrar repartidor',
        'accion': 'Registrar',
    })


def editar_repartidor(request, repartidor_id):
    """Edición de un repartidor existente."""
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    if request.method == 'POST':
        form = RepartidorForm(request.POST, instance=repartidor)
        if form.is_valid():
            services.actualizar_repartidor(repartidor, form.cleaned_data)
            messages.success(request, 'Repartidor actualizado correctamente.')
            return redirect('repartidores:detalle', repartidor_id=repartidor.id)
    else:
        form = RepartidorForm(instance=repartidor)
    return render(request, 'repartidores/formulario.html', {
        'form': form,
        'titulo': f'Editar: {repartidor.nombre}',
        'accion': 'Guardar cambios',
    })


def eliminar_repartidor(request, repartidor_id):
    """Eliminación de un repartidor."""
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    if request.method == 'POST':
        services.eliminar_repartidor(repartidor)
        messages.success(request, 'Repartidor eliminado.')
        return redirect('repartidores:lista')
    return render(request, 'repartidores/eliminar.html', {'repartidor': repartidor})


def cambiar_estado(request, repartidor_id):
    """Cambia el estado de un repartidor (disponible / en pedido / descanso / inactivo)."""
    repartidor = get_object_or_404(Repartidor, pk=repartidor_id)
    nuevo_estado = request.POST.get('estado') or request.GET.get('estado')
    if request.method == 'POST' and nuevo_estado:
        try:
            services.cambiar_estado(repartidor, nuevo_estado)
            messages.success(request, f'Estado actualizado a "{repartidor.get_estado_display()}".')
        except ValueError as error:
            messages.error(request, str(error))
    return redirect(request.POST.get('next') or reverse(
        'repartidores:detalle', args=[repartidor.id]
    ))
