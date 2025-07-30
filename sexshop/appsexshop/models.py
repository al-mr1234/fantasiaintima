
from django.db import models
import random
from datetime import datetime, timedelta
import string
from django.utils import timezone

class categoria(models.Model):
    IdCategoria = models.AutoField(primary_key=True)  
    NombreCategoria = models.CharField(max_length=80)

    class Meta:
        db_table = 'categoria'


class subcategoria(models.Model):
    IdSubCategoria = models.AutoField(primary_key=True)  
    NombresubCategoria = models.CharField(max_length=45)
    categoria = models.ForeignKey('categoria', on_delete=models.CASCADE, db_column='IdCategoria')  

    class Meta:
        db_table = 'subcategoria'

class usuario(models.Model):
    IdUsuario  = models.AutoField(primary_key=True)  
    PrimerNombre = models.CharField(max_length=255)
    OtrosNombres = models.CharField(max_length=255)
    PrimerApellido = models.CharField(max_length=255)
    SegundoApellido = models.CharField(max_length=255)
    Correo = models.EmailField(max_length=255, unique=True)
    NombreUsuario  = models.CharField(max_length=45)
    Contrasena   = models.CharField(max_length=128)
    idRol = models.ForeignKey('roles', on_delete=models.CASCADE, db_column='IdRol')
    imagen_perfil = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    class Meta:
        db_table = 'usuario'


class roles(models.Model):
    IdRol = models.AutoField(primary_key=True)  
    TipoRol = models.CharField(max_length=30)
    class Meta:
        db_table = 'roles'

class domiciliario(models.Model):
    IdDomiciliario = models.AutoField(primary_key=True)
    TipoDocumento = models.CharField(max_length=45)
    Documento = models.IntegerField(unique=True)
    NombreDomiciliario = models.CharField(max_length=100)
    PrimerApellido = models.CharField(max_length=45)
    SegundoApellido = models.CharField(max_length=45, blank=True, null=True)
    Celular = models.BigIntegerField()
    Ciudad = models.CharField(max_length=45, blank=True, null=True)
    Correo = models.EmailField(max_length=255, unique=True)
    IdRol = models.ForeignKey('Roles', on_delete=models.CASCADE, db_column='IdRol', null=True, blank=True)

    class Meta:
        db_table = 'domiciliario'

class producto(models.Model):
    IdProducto = models.AutoField(primary_key=True)  
    Img = models.ImageField(upload_to='productos/')
    Nombre = models.CharField(max_length=100)
    Descripcion = models.CharField(max_length=255)
    Cantidad = models.IntegerField()
    Precio = models.FloatField()
    FechaVence = models.DateField()
    IdSubCategoria = models.ForeignKey('subcategoria', on_delete=models.CASCADE, db_column='IdSubCategoria')

    class Meta:
        db_table = 'productos'


class Calificacion(models.Model):
    IdCalificacion = models.AutoField(primary_key=True)
    Calificacion = models.IntegerField()
    IdProducto = models.ForeignKey('Producto', on_delete=models.CASCADE, db_column='IdProducto')

    class Meta:
        db_table = 'calificacion'

    def __str__(self):
        return f"{self.IdProducto.Nombre} - {self.Calificacion} estrellas"

class CodigoVerificacion(models.Model):
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    utilizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Código para {self.usuario.Correo}"
    
    @classmethod
    def generar_codigo(cls, usuario_obj):
        if not isinstance(usuario_obj, usuario):
            raise ValueError("El parámetro 'usuario' debe ser una instancia del modelo usuario.")

        # Invalidar anteriores
        cls.objects.filter(usuario=usuario_obj, utilizado=False).update(utilizado=True)

        codigo = ''.join(random.choices(string.digits, k=6))
        
        # Usar timezone.now() para la expiración
        fecha_expiracion = timezone.now() + timedelta(minutes=15)

        nuevo_codigo = cls.objects.create(
            usuario=usuario_obj,  # 👈 Este es el fix
            codigo=codigo,
            fecha_expiracion=fecha_expiracion
        )

        return nuevo_codigo

    def es_valido(self):
        return not self.utilizado and timezone.now() < self.fecha_expiracion

    
class carritocompras(models.Model):
    codigo_pedido = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=50)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_compra = models.DateTimeField(blank=True, null=True)

    def save(self):
        self.precio_total = self.cantidad * self.precio
        return super().save()


   