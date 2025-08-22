from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin  # Import del mixin de mensajes
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .forms import UsuarioCreationForm
from Aplicacion.models import *
from Aplicacion.forms import *
#from .models import Usuario, Cliente, Categoria
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.apps import apps
from .mixins import AjaxFormMixin # Importa tu mixin personalizado si lo tienes
# TODO: Importa o define aquí tu clase personalizada 'SinPrivilegios'
# from .mixins import SinPrivilegios

# TODO: Importa o define aquí tu clase 'VistaBaseEdit' si la usas
# from .mixins import VistaBaseEdit

# Mixin para verificar roles de usuario
class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied  # Muestra error 403 si no tiene el rol adecuado

# Vista de inicio
class Home(generic.TemplateView):
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        # Si el usuario está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        # Si no está autenticado, redirigir al login
        return redirect('/login/')
# Vista del dashboard de administración

class AdminDashboardView(RoleRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir


# VER USUARIOS
class UsuariosView(RoleRequiredMixin, generic.ListView):
    model = Usuario
    template_name = 'usuarios/usuarios.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir

    def get_queryset(self):
        return Usuario.objects.exclude(id_usuario=self.request.user.id_usuario)

# TODO: Define tu mixin SinPrivilegios o quítalo si no lo usas
# class SinPrivilegios(PermissionRequiredMixin):
#     ...

# esto es una vista base para crear objetos
# Puedes usarla para crear cualquier modelo que necesites
class VistaBaseCreate(SuccessMessageMixin, LoginRequiredMixin, generic.CreateView):
    context_object_name = 'obj'
    success_message = "Registro Agregado Satisfactoriamente"
    # permission_required = "Aplicacion.add_usuario"  # Puedes añadirlo aquí si quieres
    login_url = 'Aplicacion:login'

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


# TODO: Importa o define VistaBaseEdit si realmente la usas
# class VistaBaseEdit(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
#     ...

# CREAR UN NUEVO USUARIO
class CreateUserView(RoleRequiredMixin, CreateView):
    template_name = 'usuarios/usuario_form.html'
    form_class = UsuarioCreationForm
    allowed_roles = ['Administrador','Supervisor']  # O los roles que quieras permitir
    success_url = reverse_lazy('Aplicacion:usuarios')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        html_form = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'success': False, 'html_form': html_form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            context = {'form': form}
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})


@login_required
@require_POST
def toggle_usuario_activo(request, pk):
    # Verificar que el usuario sea Administrador
    if not hasattr(request.user, 'rol') or request.user.rol != 'Administrador':
        return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
    
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})

    if usuario == request.user:
        return JsonResponse({'success': False, 'error': 'No puedes desactivar tu propia cuenta.'})

    usuario.is_active = not usuario.is_active
    usuario.save()
    return JsonResponse({'success': True, 'is_active': usuario.is_active})

@login_required
@require_POST
def toggle_estado(request, modelo, pk):
    try:
        Model = apps.get_model('Aplicacion', modelo)
        obj = Model.objects.get(pk=pk)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Objeto no encontrado'})

    obj.estado = not obj.estado
    obj.save()
    return JsonResponse({'success': True, 'estado': obj.estado})

# class UsuarioEdit(VistaBaseEdit):
#     model = Usuario
#     template_name = "usuarios/usuario_form.html"
#     form_class = UsuarioCreationForm
#     success_url = reverse_lazy("Aplicacion:usuarios")
#     permission_required = "Aplicacion.change_usuario"

#     def get(self, request, *args, **kwargs):
#         print("sobre escribir get en editar")
#         print(request)
#         t = request.GET.get("t", None)
#         print(t)
#         self.object = self.get_object()
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         context = self.get_context_data(object=self.object, form=form, t=t)
#         print(form_class, form, context)
#         return self.render_to_response(context)

class CategoriaListView(RoleRequiredMixin, generic.ListView):
    model = Categoria
    template_name = 'inventario/list_categoria.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir


from .forms import CategoriaForm  # Asegúrate de tener este formulario

class CreateCategoriaView(RoleRequiredMixin, AjaxFormMixin, CreateView):
    template_name = 'inventario/categoria_form.html'  # Crea esta plantilla si no existe
    form_class = CategoriaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:categorias')
    
    

# Editar una categoría existente    
class EditCategoriaView(RoleRequiredMixin, AjaxFormMixin, generic.UpdateView):
    model = Categoria
    template_name = 'inventario/categoria_form.html'
    form_class = CategoriaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:categorias')

# esta vista es para eliminar un objeto de cualquier modelo
@login_required
@require_POST
def delete_objeto(request, modelo, pk):
    # Verificar que el usuario sea Administrador
    if not hasattr(request.user, 'rol') or request.user.rol != 'Administrador':
        return JsonResponse({'success': False, 'error': 'No tienes permisos para realizar esta acción'})
    
    try:
        Model = apps.get_model('Aplicacion', modelo)
        obj = Model.objects.get(pk=pk)
        obj.delete()
        return JsonResponse({'success': True})
    except Exception:
        return JsonResponse({'success': False, 'error': 'Objeto no encontrado'})






############################### SUBCATEGORÍAS ####################################

    
# Vista para listar subcategorías
class SubcategoriaListView(RoleRequiredMixin, generic.ListView):
    model = Subcategoria
    template_name = 'inventario/list_subcategoria.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir



# Vista para crear una nueva subcategoría
class CreateSubcategoriaView(RoleRequiredMixin,AjaxFormMixin, CreateView):
    template_name = 'inventario/subcategoria_form.html'  # Crea esta plantilla si no existe
    form_class = SubCategoriaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:categorias')
    
        
# Editar una subcategoría existente
class EditSubcategoriaView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Subcategoria
    template_name = 'inventario/subcategoria_form.html'
    form_class =  SubCategoriaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:subcategorias')

################################ MARCAS####################################


# Vista para listar marcas
class MarcaListView(RoleRequiredMixin, generic.ListView):
    model =  Marca
    template_name = 'inventario/list_marca.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir



# Vista para crear una nueva  marca
class CreateMarcaView(RoleRequiredMixin,AjaxFormMixin,CreateView):
    template_name = 'inventario/marca_form.html'  # Crea esta plantilla si no existe
    form_class = MarcaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:marcas')
    
    
class EditMarcaView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Marca
    template_name = 'inventario/marca_form.html'
    form_class =  MarcaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:marcas')

############################### UNIDADES DE MEDIDA ####################################


# Vista para listar  unidades de medida
class UnidadMedidaListView(RoleRequiredMixin, generic.ListView):
    model =   UnidadMedida
    template_name = 'inventario/list_unidad_medida.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir


class CreateUnidadMedidaView(RoleRequiredMixin,AjaxFormMixin,CreateView):
    template_name = 'inventario/unidad_medida_form.html'  # Crea esta plantilla si no existe
    form_class = UnidadMedidaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:unidadmedida')
    
    

class EditUnidadMedidaView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  UnidadMedida
    template_name = 'inventario/unidad_medida_form.html'
    form_class =  UnidadMedidaForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:unidadmedida')


############################# PROVEEDORES ####################################
# Vista para listar proveedores
class ProveedorListView(RoleRequiredMixin, generic.ListView):
    model =  Proveedor
    template_name = 'proveedor/list_proveedor.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir


class CreateProveedorView(RoleRequiredMixin,AjaxFormMixin,CreateView):
    template_name = 'proveedor/proveedor_form.html'  # Crea esta plantilla si no existe
    form_class = ProveedorForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:proveedores')
    
    
class EditProveedorView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Proveedor
    template_name = 'proveedor/proveedor_form.html'
    form_class =  ProveedorForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:proveedores')

##########################CLIENTES####################################
# vista para listar clientes
class ClienteListView(RoleRequiredMixin, generic.ListView):
    model = Cliente
    template_name = 'cliente/list_cliente.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir
    

# Vista para crear un nuevo cliente    
class CreateClienteView(RoleRequiredMixin,AjaxFormMixin,CreateView):
    template_name = 'cliente/cliente_form.html'  # Crea esta plantilla si no existe
    form_class = ClienteForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:clientes')

class EditClienteView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Cliente
    template_name = 'cliente/cliente_form.html'
    form_class =  ClienteForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:clientes')


#################### PRODUCTOS ####################

class ProductoListView(RoleRequiredMixin, generic.ListView):
    model = Producto
    template_name = 'productos/list_productos.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']  # O los roles que quieras permitir


# Vista para crear un nuevo producto
class CreateProductoView(RoleRequiredMixin,AjaxFormMixin,CreateView):
    template_name = 'productos/producto_form.html'  # Crea esta plantilla si no existe
    form_class = ProductoForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:productos')

class EditProductoView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Producto
    template_name = 'productos/producto_form.html'
    form_class =  ProductoForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:productos')