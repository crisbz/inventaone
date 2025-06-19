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
    path('productos/', VistaSoloAdmin.as_view(), name='productos'),
    path('usuarios/', UsuariosView.as_view(), name='usuarios'),
   path('usuarios/toggle/<int:pk>/', toggle_usuario_activo, name='toggle_usuario_activo'),
    path('usuarios/create/', CreateUserView.as_view(), name='create_user'),
]
