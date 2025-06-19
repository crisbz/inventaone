# filepath: d:\django\inventaone\InventaOne\Aplicacion\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.utils.crypto import get_random_string

class UsuarioCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "Las contraseñas no coinciden.",
    }
    class Meta:
        model = Usuario
        fields = [
           # 'username',
            'email',
            'rol',
            'rut',
            'nombre',
            'apellido_paterno',
            'apellido_materno'
        ]
        help_texts = {
            #'username': '',  # Oculta el help_text por defecto
            # Puedes personalizar otros campos aquí
        }

   # def clean_username(self):
    #    username = self.cleaned_data.get('username')
     #   if not username.isalnum():
      #      raise forms.ValidationError("El nombre de usuario solo puede contener letras y números.")
       # return username
    def save(self, commit=True):
        user = super().save(commit=False)
        # Si no hay username, genera uno único
        if not user.username:
            base_username = (self.cleaned_data.get('email') or self.cleaned_data.get('rut') or 'user').split('@')[0]
            user.username = base_username + get_random_string(5)
        if commit:
            user.save()
        return user

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'rol',
            'rut',
            'nombre',
            'apellido_paterno',
            'apellido_materno'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
        }