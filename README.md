# InventaOne

Sistema web de gestión de inventario desarrollado en Django. Permite administrar
productos, stock, compras, proveedores, clientes y usuarios con control de
acceso por rol, e incluye un asistente virtual (chatbot) que consulta la base
de datos en tiempo real.

## Características principales

- **Autenticación y roles**: login con correo o usuario, y 4 roles
  (`Administrador`, `Supervisor`, `Operador`, `Vendedor`) que controlan el
  acceso a cada módulo.
- **Gestión de inventario**: categorías, subcategorías, marcas, unidades de
  medida y productos, con activar/desactivar y control de stock.
- **Compras**: registro de compras con múltiples ítems y **recepción de
  mercadería**: al marcar una compra como recibida, el stock de cada producto
  se actualiza automáticamente.
- **Proveedores y clientes**: alta, edición y listado.
- **Usuarios**: creación, activar/desactivar cuentas, y actualización de
  perfil propio (datos personales y foto), restringida a Administrador y
  Supervisor.
- **Asistente virtual (ChatBot IA)**: widget flotante disponible en toda la
  aplicación, con menú de opciones que consulta productos, stock, proveedores,
  compras y ventas directamente desde la base de datos.
- **Interfaz**: formularios en modales vía AJAX, tablas con búsqueda y
  paginación (DataTables), y selects con buscador (Tom Select).

## Tecnologías

| Categoría | Tecnología |
|---|---|
| Backend | Python 3.13, Django 5.2 |
| Base de datos | SQLite (desarrollo) |
| Frontend | Bootstrap 5, jQuery, DataTables, Tom Select, Font Awesome |
| Imágenes | Pillow |

## Estructura del proyecto

```
InventaOne/                # Raíz del proyecto Django (manage.py vive aquí)
├── manage.py
├── requerimientos.txt      # Dependencias (pip freeze)
├── InventaOne/             # Configuración del proyecto (settings, urls, wsgi/asgi)
└── Aplicacion/             # App principal
    ├── models.py           # Usuario, Producto, Compra, Proveedor, Cliente, Venta, ...
    ├── views.py            # Vistas, asistente virtual y lógica de negocio
    ├── forms.py
    ├── urls.py
    ├── static/              # CSS e imágenes propias
    └── templates/           # Plantillas (incluye includes/chatbot.html)
```

## Roles y permisos

| Rol | Acceso |
|---|---|
| Administrador | Acceso total: usuarios, activar/desactivar y eliminar registros, todos los módulos. |
| Supervisor | Igual que Administrador en los módulos de inventario, compras, proveedores y clientes; puede actualizar su perfil. |
| Operador / Vendedor | Acceso restringido; sin permisos de administración de módulos. |

## Instalación y puesta en marcha

1. **Clonar el repositorio**
   ```bash
   git clone git@github.com:crisbz/inventaone.git
   cd inventaone
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv env
   # Windows
   env\Scripts\activate
   # Linux / macOS
   source env/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r InventaOne/requerimientos.txt
   ```

4. **Aplicar migraciones**
   ```bash
   cd InventaOne
   python manage.py migrate
   ```

5. **Crear un superusuario** (rol `Administrador`)
   ```bash
   python manage.py createsuperuser
   ```

6. **Levantar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

7. Abrir [http://127.0.0.1:8000/](http://127.0.0.1:8000/) e iniciar sesión.

## Notas de desarrollo

- Los modelos `Venta` y `DetallePedido`/`Pedido` existen en el esquema para
  soportar reportes (consultados por el asistente virtual), pero aún no
  cuentan con una interfaz CRUD dedicada.
- En desarrollo se usa SQLite y se sirven los archivos multimedia (fotos de
  perfil) desde `MEDIA_ROOT`; para producción se recomienda una base de datos
  dedicada y un servidor de archivos estáticos/media independiente.
