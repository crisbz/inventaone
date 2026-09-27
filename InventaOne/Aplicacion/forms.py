# filepath: d:\django\inventaone\InventaOne\Aplicacion\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from Aplicacion.models import *
#from .models import Usuario , Categoria
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
        
class PerfilForm(forms.ModelForm):
    """Formulario para que el usuario actualice sus propios datos de perfil.
    No incluye 'rol' ni 'username': un usuario no puede cambiar su propio rol."""
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'email',
            'rut',
            'foto',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre'] 
        
    

        
class SubCategoriaForm(forms.ModelForm):
    id_categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(estado=True)
        .order_by('nombre')
    )
    class Meta:
        model= Subcategoria
        fields = ['id_categoria','nombre']
        labels = {'descripcion':"Sub Categoría",
               "estado":"Estado"}
        widget={'nombre': forms.TextInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['id_categoria'].empty_label =  "Seleccione Categoría"
        


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
            
            

class UnidadMedidaForm(forms.ModelForm):
    class Meta:
        model =  UnidadMedida
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
            

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre',
            'apellido_paterno',
            'rut',
            'correo',
            'contacto',
            'telefono',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'apellido_paterno',
            'rut',
            'correo',
            'direccion',
            'telefono',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo',
            'codigo_barra',
            'nombre',
            'precio',
            'stock',
            'id_categoria',
            'id_subcategoria',
            'id_marca',
            'id_unidad',
            'id_proveedor',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'id_categoria': forms.Select(attrs={'class': 'form-control'}),
            'id_subcategoria': forms.Select(attrs={'class': 'form-control'}),
            'id_marca': forms.Select(attrs={'class': 'form-control'}),
            'id_unidad': forms.Select(attrs={'class': 'form-control'}),
            'id_proveedor': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = [
            'fecha',
            'id_proveedor',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'id_proveedor': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].widget.attrs.update({'class': 'form-control'})