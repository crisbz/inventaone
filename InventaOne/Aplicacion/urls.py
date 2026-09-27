from django.urls import path
from django.views.generic import RedirectView
from .views import Home
from django.contrib.auth import views as auth_views


from .views import *

#app_name = 'Aplicacion' # Asegúrate de que tu app se llama "Aplicacion"

urlpatterns = [
    #path('', RedirectView.as_view(pattern_name='Aplicacion:home', permanent=False)),  # Redirige '/' a '/home/'
    path('',Home.as_view(), name='home'),
    path('login/',auth_views.LoginView.as_view(template_name='login.html'),
        name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='login.html'),name='logout'),
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('usuarios/', UsuariosView.as_view(), name='usuarios'),
    path('usuarios/toggle/<int:pk>/', toggle_usuario_activo, name='toggle_usuario_activo'),
    path('usuarios/create/', CreateUserView.as_view(), name='create_user'),
    path('perfil/', PerfilUpdateView.as_view(), name='perfil'),
    path('chatbot/api/', chatbot_api, name='chatbot_api'),
    path('categoria/', CategoriaListView.as_view(), name='categorias'),
    path('toggle/<str:modelo>/<int:pk>/', toggle_estado, name='toggle_estado'), # esto de manera generica inactivar o activar un objeto de cualquier modelo
    path('categoria/create/', CreateCategoriaView.as_view(), name='create_categoria'),
    path('categoria/edit/<int:pk>/', EditCategoriaView.as_view(), name='edit_categoria'),
    
    path('<str:modelo>/delete/<int:pk>/', delete_objeto, name='delete_objeto'),  # esto de manera generica eliminar un objeto de cualquier modelo
    
    path('subcategoria/', SubcategoriaListView.as_view(), name='subcategorias'),
    path('subcategoria/create/', CreateSubcategoriaView.as_view(), name='create_subcategoria'),
    path('subcategoria/edit/<int:pk>/', EditSubcategoriaView.as_view(), name='edit_subcategoria'),
    path('marca/', MarcaListView.as_view(), name='marcas'),
    path('marca/create/', CreateMarcaView.as_view(), name='create_marca'),
    path('marca/edit/<int:pk>/', EditMarcaView.as_view(), name='edit_marca'),
    path('unidadmedida/', UnidadMedidaListView.as_view(), name='unidadmedida'),
    path('unidadmedida/create/', CreateUnidadMedidaView.as_view(), name='create_unidad_medida'),
    path('unidadmedida/edit/<int:pk>/', EditUnidadMedidaView.as_view(), name='edit_unidad_medida'),
    path('provedores/', ProveedorListView.as_view(), name='proveedores'),
    path('proveedores/create/', CreateProveedorView.as_view(), name='create_proveedor'),
    path('proveedores/edit/<int:pk>/', EditProveedorView.as_view(), name='edit_proveedor'),
    path('clientes/', ClienteListView.as_view(), name='clientes'),
    path('clientes/create/', CreateClienteView.as_view(), name='create_cliente'),
    path('clientes/edit/<int:pk>/', EditClienteView.as_view(), name='edit_cliente'),
    path('productos/', ProductoListView.as_view(), name='productos'),
    path('productos/create/', CreateProductoView.as_view(), name='create_producto'),
    path('productos/edit/<int:pk>/', EditProductoView.as_view(), name='edit_producto'),

    # Compras
    path('compras/', CompraListView.as_view(), name='compras'),
    path('compras/create/', CreateCompraView.as_view(), name='create_compra'),
    path('compras/edit/<int:pk>/', EditCompraView.as_view(), name='edit_compra'),
    path('compras/recibir/<int:pk>/', recibir_compra, name='recibir_compra'),
]