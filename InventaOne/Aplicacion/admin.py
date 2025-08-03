from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'id_usuario', 'nombre', 'apellido_paterno', 'rol', 'email'
    ]
    fields = [
        'username','rut', 'nombre', 'apellido_paterno', 'apellido_materno', 'rol', 'email', 'is_active', 'is_staff', 'date_joined','is_superuser'
    ]
    # Puedes agregar otros campos que sí quieras mostrar

admin.site.register(Usuario, UsuarioAdmin)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = [
        'id_categoria', 'nombre', 'estado',
        'get_uc_nombre', 'get_um_nombre', 'fc', 'fm'
    ]
    readonly_fields = ['mostrar_uc', 'mostrar_um', 'fc', 'fm']

    def get_uc_nombre(self, obj):
        if obj.uc:
            return f"{obj.uc.nombre} {obj.uc.apellido_paterno}"
        return "-"
    get_uc_nombre.short_description = "Creado por"

    def get_um_nombre(self, obj):
        if obj.um:
            return f"{obj.um.nombre} {obj.um.apellido_paterno}"
        return "-"
    get_um_nombre.short_description = "Modificado por"

    def mostrar_uc(self, obj):
        return self.get_uc_nombre(obj)
    mostrar_uc.short_description = "Creado por"

    def mostrar_um(self, obj):
        return self.get_um_nombre(obj)
    mostrar_um.short_description = "Modificado por"

admin.site.register(Categoria, CategoriaAdmin)