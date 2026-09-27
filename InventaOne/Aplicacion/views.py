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
from decimal import Decimal
from django.apps import apps
import json
from django.db import transaction
from django.db.models import Q, Sum, F, DecimalField
from django.utils import timezone
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


# ACTUALIZAR PERFIL PROPIO
# Solo los roles Administrador y Supervisor pueden actualizar su perfil.
# Los demas roles reciben un 403 (PermissionDenied) gracias a RoleRequiredMixin.
class PerfilUpdateView(RoleRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Usuario
    form_class = PerfilForm
    template_name = 'usuarios/perfil_form.html'
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:perfil')
    success_message = "Perfil actualizado correctamente"

    def get_object(self, queryset=None):
        # Cada usuario solo puede editar su propio perfil, nunca el de otro.
        return self.request.user


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

    def form_valid(self, form):
        form.instance.stock = 0  # Seguridad backend: stock siempre inicia en 0
        return super().form_valid(form)

class EditProductoView(RoleRequiredMixin,AjaxFormMixin, generic.UpdateView):
    model =  Producto
    template_name = 'productos/producto_form.html'
    form_class =  ProductoForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:productos')


#################### COMPRAS ####################

class CompraListView(RoleRequiredMixin, generic.ListView):
    model = Compra
    template_name = 'compras/list_compras.html'
    context_object_name = 'obj'
    allowed_roles = ['Administrador', 'Supervisor']

    def get_queryset(self):
        return (
            Compra.objects.all()
            .prefetch_related('detallecompra_set__id_producto', 'id_proveedor')
            .order_by('-id_compra')
        )


class CreateCompraView(RoleRequiredMixin, AjaxFormMixin, CreateView):
    template_name = 'compras/compras_form.html'
    form_class = CompraForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:compras')

    def get(self, request, *args, **kwargs):
        # Sobrescribimos para enviar también los productos al modal
        form = self.form_class()
        context = {
            'form': form,
            'productos': Producto.objects.filter(estado=True).order_by('nombre')
        }
        html_form = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'success': False, 'html_form': html_form})

    def post(self, request, *args, **kwargs):
        # Crear cabecera
        form = self.form_class(request.POST)
        if not form.is_valid():
            context = {
                'form': form,
                'productos': Producto.objects.filter(estado=True).order_by('nombre')
            }
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})

        compra = form.save()

        # Crear detalles desde arrays del formulario
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        precios = request.POST.getlist('precio_unitario[]')

        created = 0
        for pid, cant, prec in zip(productos_ids, cantidades, precios):
            if not pid:
                continue
            try:
                prod = Producto.objects.get(pk=int(pid))
                cantidad = int(cant or 0)
                precio = Decimal(prec or '0')
            except Exception:
                continue
            if cantidad <= 0 or precio < 0:
                continue
            DetalleCompra.objects.create(
                id_compra=compra,
                id_producto=prod,
                cantidad=cantidad,
                precio_unitario=precio,
            )
            created += 1

        if created == 0:
            compra.delete()
            form.add_error(None, 'Debe agregar al menos un ítem válido.')
            context = {
                'form': form,
                'productos': Producto.objects.filter(estado=True).order_by('nombre')
            }
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})

        return JsonResponse({'success': True})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['productos'] = Producto.objects.filter(estado=True).order_by('nombre')
        return ctx


@login_required
@require_POST
def recibir_compra(request, pk):
    """Marca una compra como RECIBIDA y suma al stock la cantidad comprada
    de cada producto del detalle.
    Es idempotente: si la compra ya estaba recibida, no vuelve a sumar."""
    if getattr(request.user, 'rol', None) not in ('Administrador', 'Supervisor'):
        return JsonResponse({'success': False, 'error': 'No tienes permisos para esta acción.'})

    try:
        compra = Compra.objects.get(pk=pk)
    except Compra.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Compra no encontrada.'})

    if compra.recibida:
        return JsonResponse({'success': False, 'error': 'Esta compra ya fue recibida.'})

    detalles = list(compra.detallecompra_set.select_related('id_producto').all())
    if not detalles:
        return JsonResponse({'success': False, 'error': 'La compra no tiene productos para recibir.'})

    with transaction.atomic():
        for det in detalles:
            prod = det.id_producto
            if prod and det.cantidad:
                prod.stock = (prod.stock or 0) + int(det.cantidad)
                prod.save(update_fields=['stock'])
        compra.recibida = True
        compra.fecha_recepcion = timezone.localdate()
        compra.save(update_fields=['recibida', 'fecha_recepcion'])

    return JsonResponse({'success': True})


class EditCompraView(RoleRequiredMixin, AjaxFormMixin, generic.UpdateView):
    model = Compra
    template_name = 'compras/compras_form.html'
    form_class = CompraForm
    allowed_roles = ['Administrador', 'Supervisor']
    success_url = reverse_lazy('Aplicacion:compras')


#################### CHATBOT / ASISTENTE DE INVENTARIO ####################
# Asistente guiado por botones (menú de opciones) que consulta la base de
# datos real. Disponible para todos los usuarios autenticados.
#
# El frontend (includes/chatbot.html) envía POST JSON:
#   { "action": "<clave del nodo>", "query": "<texto opcional de búsqueda>" }
# y recibe:
#   {
#     "text": "...",                       # cuerpo del mensaje del bot
#     "icon": "fa-box",                    # (opcional) icono Font Awesome del encabezado
#     "options": [                         # botones de opción
#       {"label": "...", "action": "...", "icon": "fa-..."}
#     ],
#     "expects_input": bool, "input_action": "...", "input_placeholder": "..."
#   }
#
# Los iconos son clases de Font Awesome 5 (ya cargado en base_file.html); NO se
# usan emojis en el código. El frontend valida cada icono con /^fa-[a-z0-9-]+$/
# y lo pinta con document.createElement('i') (sin innerHTML), así que es seguro.

def _money(value):
    """Formatea un número como monto en pesos (separador de miles con punto)."""
    try:
        n = int(round(float(value or 0)))
    except (TypeError, ValueError):
        n = 0
    return "$" + format(n, ",d").replace(",", ".")


def _lista_stock(titulo, qs, vacio="Sin resultados.", limite=40):
    total = qs.count()
    if total == 0:
        return f"{titulo}\n\n{vacio}"
    filas = []
    for p in qs[:limite]:
        nombre = p.nombre or f"Producto {p.id_producto}"
        filas.append(f"- {nombre}: {p.stock or 0} u.")
    texto = f"{titulo}  ({total})\n\n" + "\n".join(filas)
    if total > limite:
        texto += f"\n... y {total - limite} mas."
    return texto


def _op(label, action, icon):
    """Construye una opción (botón) del chatbot."""
    return {"label": label, "action": action, "icon": icon}


def _volver(target):
    return _op("Volver", target, "fa-arrow-left")


def _chatbot_response(action, query=""):
    action = (action or "menu").strip()
    query = (query or "").strip()

    # ---------------- MENÚ PRINCIPAL ----------------
    if action in ("menu", "inicio", "start"):
        return {
            "text": "Asistente de Inventario\n\n¿Qué deseas consultar?",
            "icon": "fa-robot",
            "options": [
                _op("Productos", "productos", "fa-box"),
                _op("Proveedores", "proveedores", "fa-truck"),
                _op("Compras", "compras", "fa-shopping-cart"),
                _op("Ventas", "ventas", "fa-dollar-sign"),
            ],
        }

    # ---------------- PRODUCTOS ----------------
    if action == "productos":
        return {
            "text": "Productos\n\n¿Qué deseas saber?",
            "icon": "fa-box",
            "options": [
                _op("Cantidad de productos", "prod_cantidad", "fa-chart-bar"),
                _op("Stock disponible", "prod_stock", "fa-boxes"),
                _op("Productos con poco stock", "prod_poco", "fa-exclamation-triangle"),
                _op("Buscar producto", "prod_buscar", "fa-search"),
                _volver("menu"),
            ],
        }

    if action == "prod_cantidad":
        total = Producto.objects.count()
        activos = Producto.objects.filter(estado=True).count()
        return {
            "text": (f"Hay {total} productos registrados.\n"
                     f"- Activos: {activos}\n- Inactivos: {total - activos}"),
            "icon": "fa-chart-bar",
            "options": [_volver("productos")],
        }

    if action == "prod_stock":
        return {
            "text": "Stock\n\nSelecciona una opción:",
            "icon": "fa-boxes",
            "options": [
                _op("Ver todo el stock", "stock_todo", "fa-list"),
                _op("Productos agotados", "stock_agotado", "fa-ban"),
                _op("Productos con menos de 10 unidades", "stock_bajo", "fa-exclamation-triangle"),
                _volver("productos"),
            ],
        }

    if action == "stock_todo":
        qs = Producto.objects.filter(estado=True).order_by("nombre")
        return {"text": _lista_stock("Stock disponible", qs),
                "icon": "fa-boxes", "options": [_volver("prod_stock")]}

    if action == "stock_agotado":
        qs = Producto.objects.filter(stock__lte=0).order_by("nombre")
        return {"text": _lista_stock("Productos agotados", qs,
                                     vacio="No hay productos agotados."),
                "icon": "fa-ban", "options": [_volver("prod_stock")]}

    if action == "stock_bajo":
        qs = Producto.objects.filter(stock__lt=10).order_by("stock", "nombre")
        return {"text": _lista_stock("Productos con menos de 10 unidades", qs,
                                     vacio="Ningún producto bajo 10 unidades."),
                "icon": "fa-exclamation-triangle", "options": [_volver("prod_stock")]}

    if action == "prod_poco":
        qs = Producto.objects.filter(stock__lt=5).order_by("stock", "nombre")
        return {"text": _lista_stock("Productos con poco stock (menos de 5)", qs,
                                     vacio="Ningún producto con poco stock."),
                "icon": "fa-exclamation-triangle", "options": [_volver("productos")]}

    if action == "prod_buscar":
        return {
            "text": "Escribe el nombre o código del producto que buscas.",
            "icon": "fa-search",
            "options": [_volver("productos")],
            "expects_input": True,
            "input_action": "prod_buscar_run",
            "input_placeholder": "Nombre o código del producto...",
        }

    if action == "prod_buscar_run":
        if not query:
            return {"text": "Escribe un texto para buscar.",
                    "icon": "fa-search",
                    "options": [_volver("productos")],
                    "expects_input": True, "input_action": "prod_buscar_run",
                    "input_placeholder": "Nombre o código del producto..."}
        qs = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(codigo_barra__icontains=query)
        ).order_by("nombre")
        total = qs.count()
        opciones = [_op("Buscar otro", "prod_buscar", "fa-search"), _volver("productos")]
        if total == 0:
            return {"text": f'Sin resultados para "{query}".', "icon": "fa-search", "options": opciones}
        filas = []
        for p in qs[:20]:
            filas.append(f"- {p.nombre or ('Producto ' + str(p.id_producto))} (cod: {p.codigo or '-'})\n"
                         f"   stock: {p.stock or 0} u. | precio: {_money(p.precio)}")
        texto = f'{total} resultado(s) para "{query}":\n\n' + "\n".join(filas)
        if total > 20:
            texto += f"\n... y {total - 20} mas."
        return {"text": texto, "icon": "fa-search", "options": opciones}

    # ---------------- PROVEEDORES ----------------
    if action == "proveedores":
        return {
            "text": "Proveedores\n\n¿Qué deseas saber?",
            "icon": "fa-truck",
            "options": [
                _op("Cantidad de proveedores", "prov_cantidad", "fa-chart-bar"),
                _op("Listar proveedores", "prov_listar", "fa-list"),
                _op("Buscar proveedor", "prov_buscar", "fa-search"),
                _volver("menu"),
            ],
        }

    if action == "prov_cantidad":
        total = Proveedor.objects.count()
        activos = Proveedor.objects.filter(estado=True).count()
        return {"text": (f"Hay {total} proveedores.\n"
                         f"- Activos: {activos}\n- Inactivos: {total - activos}"),
                "icon": "fa-chart-bar", "options": [_volver("proveedores")]}

    if action == "prov_listar":
        qs = Proveedor.objects.filter(estado=True).order_by("nombre")
        total = qs.count()
        if total == 0:
            return {"text": "No hay proveedores registrados.",
                    "icon": "fa-list", "options": [_volver("proveedores")]}
        filas = []
        for p in qs[:30]:
            nom = " ".join(x for x in [p.nombre, p.apellido_paterno] if x) or (p.rut or f"Proveedor {p.id_proveedor}")
            filas.append(f"- {nom} | {p.telefono or 's/tel'} | {p.correo or 's/correo'}")
        texto = f"Proveedores ({total}):\n\n" + "\n".join(filas)
        if total > 30:
            texto += f"\n... y {total - 30} mas."
        return {"text": texto, "icon": "fa-list", "options": [_volver("proveedores")]}

    if action == "prov_buscar":
        return {
            "text": "Escribe el nombre o RUT del proveedor.",
            "icon": "fa-search",
            "options": [_volver("proveedores")],
            "expects_input": True,
            "input_action": "prov_buscar_run",
            "input_placeholder": "Nombre o RUT...",
        }

    if action == "prov_buscar_run":
        opciones = [_op("Buscar otro", "prov_buscar", "fa-search"), _volver("proveedores")]
        if not query:
            return {"text": "Escribe un texto para buscar.", "icon": "fa-search", "options": opciones}
        qs = Proveedor.objects.filter(
            Q(nombre__icontains=query) | Q(apellido_paterno__icontains=query) | Q(rut__icontains=query)
        ).order_by("nombre")
        total = qs.count()
        if total == 0:
            return {"text": f'Sin resultados para "{query}".', "icon": "fa-search", "options": opciones}
        filas = []
        for p in qs[:20]:
            nom = " ".join(x for x in [p.nombre, p.apellido_paterno] if x) or (p.rut or f"Proveedor {p.id_proveedor}")
            filas.append(f"- {nom} | RUT {p.rut or '-'} | {p.telefono or 's/tel'} | {p.correo or 's/correo'}")
        return {"text": f"{total} resultado(s):\n\n" + "\n".join(filas),
                "icon": "fa-search", "options": opciones}

    # ---------------- COMPRAS ----------------
    if action == "compras":
        return {
            "text": "Compras\n\n¿Qué deseas saber?",
            "icon": "fa-shopping-cart",
            "options": [
                _op("Cantidad de compras", "compra_cantidad", "fa-chart-bar"),
                _op("Últimas compras", "compra_ultimas", "fa-receipt"),
                _op("Total comprado", "compra_total", "fa-money-bill-wave"),
                _volver("menu"),
            ],
        }

    if action == "compra_cantidad":
        return {"text": f"Hay {Compra.objects.count()} compras registradas.",
                "icon": "fa-chart-bar", "options": [_volver("compras")]}

    if action == "compra_ultimas":
        qs = (Compra.objects.select_related("id_proveedor")
              .prefetch_related("detallecompra_set").order_by("-id_compra")[:10])
        if not qs:
            return {"text": "No hay compras registradas.",
                    "icon": "fa-receipt", "options": [_volver("compras")]}
        filas = []
        for c in qs:
            prov = c.id_proveedor.nombre if c.id_proveedor else "-"
            filas.append(f"- #{c.id_compra} | {c.fecha or 's/f'} | {prov} | {_money(c.total)}")
        return {"text": "Últimas compras:\n\n" + "\n".join(filas),
                "icon": "fa-receipt", "options": [_volver("compras")]}

    if action == "compra_total":
        agg = DetalleCompra.objects.aggregate(
            t=Sum(F("cantidad") * F("precio_unitario"), output_field=DecimalField()))
        return {"text": f"Total comprado (histórico): {_money(agg['t'])}",
                "icon": "fa-money-bill-wave", "options": [_volver("compras")]}

    # ---------------- VENTAS ----------------
    if action == "ventas":
        return {
            "text": "Ventas\n\n¿Qué deseas saber?",
            "icon": "fa-dollar-sign",
            "options": [
                _op("Cantidad de ventas", "venta_cantidad", "fa-chart-bar"),
                _op("Últimas ventas", "venta_ultimas", "fa-receipt"),
                _op("Total vendido", "venta_total", "fa-money-bill-wave"),
                _volver("menu"),
            ],
        }

    if action == "venta_cantidad":
        return {"text": f"Hay {Venta.objects.count()} ventas registradas.",
                "icon": "fa-chart-bar", "options": [_volver("ventas")]}

    if action == "venta_ultimas":
        qs = Venta.objects.select_related("id_cliente").order_by("-id_venta")[:10]
        if not qs:
            return {"text": "No hay ventas registradas.",
                    "icon": "fa-receipt", "options": [_volver("ventas")]}
        filas = []
        for v in qs:
            cli = "-"
            if v.id_cliente:
                cli = " ".join(x for x in [v.id_cliente.nombre, v.id_cliente.apellido_paterno] if x) \
                    or f"Cliente {v.id_cliente.id_cliente}"
            filas.append(f"- #{v.id_venta} | {v.fecha or 's/f'} | {cli} | {_money(v.total)}")
        return {"text": "Últimas ventas:\n\n" + "\n".join(filas),
                "icon": "fa-receipt", "options": [_volver("ventas")]}

    if action == "venta_total":
        agg = Venta.objects.aggregate(t=Sum("total"))
        return {"text": f"Total vendido (histórico): {_money(agg['t'])}",
                "icon": "fa-money-bill-wave", "options": [_volver("ventas")]}

    # ---------------- TEXTO LIBRE / DESCONOCIDO ----------------
    if action == "freetext" and query:
        # Por defecto intentamos buscar un producto con ese texto
        return _chatbot_response("prod_buscar_run", query)

    return {
        "text": "No entendí esa opción. Usa los botones para navegar.",
        "icon": "fa-robot",
        "options": [_op("Menú principal", "menu", "fa-home")],
    }


@login_required
@require_POST
def chatbot_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        payload = {}

    action = str(payload.get("action") or payload.get("message") or "menu")
    query = str(payload.get("query") or "")

    data = _chatbot_response(action, query)
    data.setdefault("options", [])
    data["timestamp"] = timezone.localtime().strftime("%H:%M")
    return JsonResponse(data)
    
    
    
