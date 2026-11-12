from django.contrib import admin
from django.utils.html import format_html

from .models import Repartidor


@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'dni', 'telefono', 'vehiculo', 'zona',
        'badge_estado', 'calificacion', 'entregas_completadas',
    )
    list_filter = ('estado', 'vehiculo', 'zona')
    search_fields = ('nombre', 'dni', 'telefono', 'email')
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    fieldsets = (
        ('Datos personales', {
            'fields': ('usuario', 'nombre', 'dni', 'telefono', 'email'),
        }),
        ('Trabajo', {
            'fields': ('vehiculo', 'placa', 'zona', 'estado'),
        }),
        ('Desempeño', {
            'fields': ('calificacion', 'entregas_completadas'),
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Estado')
    def badge_estado(self, obj):
        colores = {
            Repartidor.Estado.DISPONIBLE: '#28a745',
            Repartidor.Estado.EN_PEDIDO: '#ffc107',
            Repartidor.Estado.DESCANSO: '#17a2b8',
            Repartidor.Estado.INACTIVO: '#6c757d',
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display(),
        )
