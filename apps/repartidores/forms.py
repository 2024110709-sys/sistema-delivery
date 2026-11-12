from django import forms

from .models import Repartidor


class RepartidorForm(forms.ModelForm):
    """Formulario para crear/editar repartidores."""

    class Meta:
        model = Repartidor
        fields = [
            'nombre', 'dni', 'telefono', 'email', 'vehiculo',
            'placa', 'zona', 'estado',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '8'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'zona': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '')
        if not dni.isdigit() or len(dni) != 8:
            raise forms.ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        limpio = telefono.replace(' ', '').replace('-', '')
        if not limpio.isdigit() or not (9 <= len(limpio) <= 15):
            raise forms.ValidationError('Ingrese un teléfono válido (solo dígitos).')
        return telefono

    def clean(self):
        cleaned = super().clean()
        vehiculo = cleaned.get('vehiculo')
        placa = cleaned.get('placa')
        if vehiculo in (Repartidor.Vehiculo.MOTO, Repartidor.Vehiculo.AUTO) and not placa:
            self.add_error('placa', 'La placa es obligatoria para moto o auto.')
        return cleaned
