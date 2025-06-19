from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.management.base import CommandError
# Create your models here.




ROLE_CHOICES = [
    ('Vendedor', 'Vendedor'),
    ('Supervisor', 'Supervisor'),
    ('Operador', 'Operador'),
    ('Administrador', 'Administrador'),
]

class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    rol = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'rol']  # <-- Agrega esto

    def save(self, *args, **kwargs):
        # Si el rol es Administrador, es superuser y staff
        if self.rol == 'Administrador':
            self.is_superuser = True
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Usuario'

class ClaseModelo(models.Model):
    estado = models.BooleanField(default=True)
    fc = models.DateTimeField(auto_now_add=True)
    fm = models.DateTimeField(auto_now=True)
    uc = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    um = models.IntegerField(blank=True,null=True)

    class Meta:
        abstract=True

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'Categoria'

class Subcategoria(models.Model):
    id_subcategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Subcategoria'

class Marca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'Marca'

class UnidadMedida(models.Model):
    id_unidad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'UnidadMedida'

class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    contacto = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'Proveedor'


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'Cliente'

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Pedido'

class DetallePedido(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetallePedido'

class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    id_proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Compra'

class DetalleCompra(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey('Compra', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetalleCompra'

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True, blank=True)
    id_subcategoria = models.ForeignKey('Subcategoria', on_delete=models.CASCADE, null=True, blank=True)
    id_marca = models.ForeignKey('Marca', on_delete=models.CASCADE, null=True, blank=True)
    id_unidad = models.ForeignKey('UnidadMedida', on_delete=models.CASCADE, null=True, blank=True)
    id_proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Producto'

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=True)
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Venta'

class DetalleVenta(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetalleVenta'

def add_arguments(self, parser):
    super().add_arguments(parser)
    parser.add_argument(
        '--rol',
        type=str,
        choices=[choice[0] for choice in ROLE_CHOICES],
        help='Rol del usuario (Vendedor, Supervisor, Operador, Administrador)'
    )

def handle(self, *args, **options):
    rol = options.get('rol')
    if not rol:
        # Si no se pasa por argumento, pedirlo por input
        roles = [choice[0] for choice in ROLE_CHOICES]
        rol = input(f"Rol ({', '.join(roles)}): ")
        if rol not in roles:
            raise CommandError(f"Rol debe ser uno de: {', '.join(roles)}")
    options['rol'] = rol
    super().handle(*args, **options)

