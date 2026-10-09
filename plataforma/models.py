from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column="id_usuario")
    nombre = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=10,
        choices=[
            ("cliente", "cliente"),
            ("maker", "maker"),
            ("admin", "admin"),
        ],
    )
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "usuarios"
        app_label = "plataforma"


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True, db_column="id_pedido")
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
    )
    descripcion = models.TextField()
    cantidad = models.IntegerField(default=1)
    material = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    archivo_url = models.CharField(max_length=300, null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        default="pendiente",
        choices=[
            ("pendiente", "pendiente"),
            ("cotizado", "cotizado"),
            ("en_proceso", "en_proceso"),
            ("terminado", "terminado"),
            ("entregado", "entregado"),
            ("cancelado", "cancelado"),
        ],
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "pedidos"
        app_label = "plataforma"


class Cotizacion(models.Model):
    id_cotizacion = models.AutoField(primary_key=True, db_column="id_cotizacion")
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="id_pedido",
    )
    id_maker = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_maker",
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_estimado_dias = models.IntegerField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    estado = models.CharField(
        max_length=12,
        default="pendiente",
        choices=[
            ("pendiente", "pendiente"),
            ("aceptada", "aceptada"),
            ("rechazada", "rechazada"),
        ],
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "cotizaciones"
        app_label = "plataforma"
        unique_together = (("id_pedido", "id_maker"),)


class LoginHistorial(models.Model):
    id_historial = models.AutoField(primary_key=True, db_column="id_historial")
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario",
    )
    fecha = models.DateTimeField(default=timezone.now)
    ip = models.CharField(max_length=45, null=True, blank=True)
    exito = models.BooleanField()

    class Meta:
        managed = False
        db_table = "login_historial"
        app_label = "plataforma"


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True, db_column="id_pago")
    id_cotizacion = models.OneToOneField(
        Cotizacion,
        on_delete=models.CASCADE,
        db_column="id_cotizacion",
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        choices=[
            ("tarjeta", "tarjeta"),
            ("transferencia", "transferencia"),
            ("efectivo", "efectivo"),
            ("mercado_pago", "mercado_pago"),
        ],
    )
    estado = models.CharField(
        max_length=12,
        default="pendiente",
        choices=[
            ("pendiente", "pendiente"),
            ("aprobado", "aprobado"),
            ("rechazado", "rechazado"),
            ("reembolsado", "reembolsado"),
        ],
    )
    fecha_pago = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "pagos"
        app_label = "plataforma"


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True, db_column="id_producto")

    id_maker = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_maker",
        related_name="productos",
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    imagen_url = models.CharField(max_length=500, null=True, blank=True)
    archivo_url = models.CharField(max_length=500, null=True, blank=True)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "productos"
        app_label = "plataforma"

    
class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)

    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        db_column="id_usuario",
        related_name="compras"
    )

    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column="id_producto",
        related_name="compras"
    )

    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)

    estado = models.CharField(
        max_length=20,
        default="pendiente",
        choices=[
            ("pendiente", "Pendiente"),
            ("pagada", "Pagada"),
            ("enviada", "Enviada"),
            ("entregada", "Entregada"),
            ("cancelada", "Cancelada"),
        ]
    )

    fecha_compra = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "compras"
        app_label = "plataforma"