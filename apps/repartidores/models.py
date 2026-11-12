from django.db import models
from django.contrib.auth.models import User


class Repartidor(models.Model):
    """Modelo para los repartidores del sistema de delivery."""

    class Vehiculo(models.TextChoices):
        MOTO = 'moto', 'Moto'
        BICICLETA = 'bicicleta', 'Bicicleta'
        AUTO = 'auto', 'Auto'
        A_PIE = 'a_pie', 'A pie'

    class Estado(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        EN_PEDIDO = 'en_pedido', 'En pedido'
        DESCANSO = 'descanso', 'Descanso'
        INACTIVO = 'inactivo', 'Inactivo'

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repartidor',
        verbose_name='Usuario asociado',
    )
    nombre = models.CharField('Nombre completo', max_length=120)
    dni = models.CharField('DNI', max_length=8, unique=True)
    telefono = models.CharField('Teléfono', max_length=15)
    email = models.EmailField('Correo electrónico', blank=True)
    vehiculo = models.CharField(
        'Vehículo', max_length=10, choices=Vehiculo.choices, default=Vehiculo.MOTO
    )
    placa = models.CharField('Placa', max_length=10, blank=True)
    zona = models.CharField('Zona de trabajo', max_length=60, blank=True)
    estado = models.CharField(
        'Estado', max_length=10, choices=Estado.choices, default=Estado.DISPONIBLE
    )
    calificacion = models.DecimalField(
        'Calificación', max_digits=3, decimal_places=2, default=5.00,
        help_text='Promedio de 0.00 a 5.00'
    )
    entregas_completadas = models.PositiveIntegerField(
        'Entregas completadas', default=0
    )
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última actualización', auto_now=True)

    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.nombre} ({self.get_vehiculo_display()})'

    @property
    def esta_disponible(self):
        return self.estado == self.Estado.DISPONIBLE
