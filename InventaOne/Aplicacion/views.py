from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin  # Import del mixin de mensajes
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .forms import UsuarioCreationForm
from .models import Usuario, Cliente
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
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
class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'
    login_url = 'Aplicacion:login'

# Vista para el dashboard del Producto
class VistaSoloAdmin(RoleRequiredMixin, generic.TemplateView):
    template_name = 'producto/productos.html'
    allowed_roles = ['Administrador']

# Vista del dashboard de administración

class AdminDashboardView(RoleRequiredMixin, generic.TemplateView):
    template_name = 'dashboard.html'
    allowed_roles = ['Administrador']


# VER USUARIOS
class UsuariosView(RoleRequiredMixin, generic.ListView):
    model = Usuario
    template_name = 'usuarios/usuarios.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador']

    def get_queryset(self):
        return Usuario.objects.exclude(id_usuario=self.request.user.id_usuario)

# TODO: Define tu mixin SinPrivilegios o quítalo si no lo usas
# class SinPrivilegios(PermissionRequiredMixin):
#     ...

# 
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
    allowed_roles = ['Administrador']
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
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})

    if usuario == request.user:
        return JsonResponse({'success': False, 'error': 'No puedes desactivar tu propia cuenta.'})

    usuario.is_active = not usuario.is_active
    usuario.save()
    return JsonResponse({'success': True, 'is_active': usuario.is_active})

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