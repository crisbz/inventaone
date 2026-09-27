from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.db import models
from django.core.management.base import CommandError
from django.conf import settings
from django.templatetags.static import static
from django.utils import timezone
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
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)

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

    @property
    def foto_url(self):
        """URL de la foto de perfil; si no tiene, devuelve la imagen por defecto."""
        if self.foto and hasattr(self.foto, 'url'):
            return self.foto.url
        return static('img/perfil_default.svg')

    @property
    def nombre_completo(self):
        partes = [self.nombre, self.apellido_paterno, self.apellido_materno]
        completo = " ".join(p for p in partes if p).strip()
        return completo or self.username

    class Meta:
        db_table = 'Usuario'

class ClaseModelo(models.Model):
    estado = models.BooleanField(default=True)
    fc = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática  default=timezone.now
    fm = models.DateTimeField(auto_now=True)      # Fecha de modificación automática  default=timezone.now
    uc = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.CASCADE)  
    um = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='modificados_%(class)s'
    )

    class Meta:
        abstract = True

class Categoria(ClaseModelo):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    
    
    # Recordatorio: __str__ define el texto legible que verás en selects, admin y plantillas.
    # Usamos 'nombre' y dejamos un fallback por si está vacío o nulo.
    def __str__(self):
        return self.nombre or f"Categoría {self.id_categoria}"

    class Meta:
        db_table = 'Categoria'
  
class Subcategoria(ClaseModelo):
    id_subcategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True, blank=True)

    # Recordatorio: mostrar el 'nombre' en desplegables/listas; fallback si no hay nombre.
    def __str__(self):
        return self.nombre or f"Subcategoría {self.id_subcategoria}"

    class Meta:
        db_table = 'Subcategoria'

class Marca(ClaseModelo):
    id_marca = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)

    # Recordatorio: 'nombre' es el identificador visible; usa fallback para evitar cadenas vacías.
    def __str__(self):
        return self.nombre or f"Marca {self.id_marca}"

    class Meta:
        db_table = 'Marca'

class UnidadMedida(ClaseModelo):
    id_unidad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    
    # Recordatorio: usar 'nombre' para la representación y fallback si está vacío.
    def __str__(self):
        return self.nombre or f"Unidad {self.id_unidad}"

    class Meta:
        db_table = 'UnidadMedida'

class Proveedor(ClaseModelo):
    id_proveedor = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido_paterno = models.CharField(max_length=100, null=True, blank=True)
    apellido_materno = models.CharField(max_length=100, null=True, blank=True)
    contacto = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)

    # Recordatorio: componer nombre legible; si no hay datos, usar RUT o un fallback con el ID.
    def __str__(self):
        nombre_completo = " ".join([p for p in [self.nombre, self.apellido_paterno, self.apellido_materno] if p]).strip()
        return nombre_completo or self.rut or f"Proveedor {self.id_proveedor}"

    class Meta:
        db_table = 'Proveedor'

class Cliente(ClaseModelo):
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

class Pedido(ClaseModelo):
    id_pedido = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'Pedido'

class DetallePedido(ClaseModelo):
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetallePedido'



class Compra(ClaseModelo):
    id_compra = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    id_proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)
    recibida = models.BooleanField(default=False)          # True cuando la mercadería ya ingresó a stock
    fecha_recepcion = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'Compra'

    # Propiedades calculadas para soportar la plantilla sin migraciones
    @property
    def fecha_factura(self):
        return None

    @property
    def descuento(self):
        return Decimal('0')

    @property
    def subtotal(self):
        total = Decimal('0')
        for det in self.detallecompra_set.all():
            total += det.subtotal
        return total

    @property
    def total(self):
        return self.subtotal - self.descuento


class DetalleCompra(ClaseModelo):
    id_detalle = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey('Compra', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetalleCompra'

    @property
    def subtotal(self):
        if self.cantidad and self.precio_unitario is not None:
            return Decimal(self.cantidad) * Decimal(self.precio_unitario)
        return Decimal('0')

class Producto(ClaseModelo):
    id_producto = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,      # ← temporal
        blank=True      # ← temporal
    )
    codigo_barra = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0, null=True, blank=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True, blank=True)
    id_subcategoria = models.ForeignKey('Subcategoria', on_delete=models.CASCADE, null=True, blank=True)
    id_marca = models.ForeignKey('Marca', on_delete=models.CASCADE, null=True, blank=True)
    id_unidad = models.ForeignKey('UnidadMedida', on_delete=models.CASCADE, null=True, blank=True)
    id_proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)

    # Recordatorio: mostrar 'nombre' del producto; si falta, usar 'codigo' y como último recurso el ID.
    def __str__(self):
        return self.nombre or self.codigo or f"Producto {self.id_producto}"

    class Meta:
        db_table = 'Producto'

class Venta(ClaseModelo):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, blank=True)
    #id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True, blank=True, related_name='ventas_realizadas')

    class Meta:
        db_table = 'Venta'

class DetalleVenta(ClaseModelo):
    id_detalle = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE, null=True, blank=True)
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'DetalleVenta'
