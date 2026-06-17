from django.db import models
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
import datetime
from django.contrib.auth import authenticate, login
import uuid
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    identificador_telefono = models.CharField(max_length=10, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=20, blank=True)
    nacionalidad =  CountryField(blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=300, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    historial = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.nit})"


class Gaseosa(models.Model):
    marca = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    sku_base = models.CharField(max_length=10, unique=True, help_text="Ejemplo: CO para Coca Cola, FAN para Fanta")
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.marca} {self.nombre}"


from django.db import models

class Inventario(models.Model):
    CONTENIDO_OPCIONES = [
        ('100ml', '100ml'),
        ('150ml', '150ml'),
        ('200ml', '200ml'),
        ('500ml', '500ml'),
        ('750ml', '750ml'),
        ('1L', '1L'),
        ('1.5L', '1.5L'),
        ('2L', '2L'),
        ('2.5L', '2.5L'),
        ('3L', '3L'),
    ]
    gaseosa = models.ForeignKey(Gaseosa, on_delete=models.CASCADE, related_name='inventarios')
    contenido = models.CharField(max_length=10, choices=CONTENIDO_OPCIONES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=20, unique=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    # 👇 ESTE ES EL NUEVO BLOQUE QUE PROTEGE TU BASE DE DATOS:
    class Meta:
        # Impide que una misma gaseosa tenga dos registros con el mismo tamaño
        unique_together = ('gaseosa', 'contenido')

    def save(self, *args, **kwargs):
        # Genera el SKU automáticamente si está vacío
        if not self.sku:
            # Se corrigen los índices duplicados y se añaden los tamaños faltantes
            contenido_indices = {
                '100ml': 0, '150ml': 1, '200ml': 2,
                '500ml': 3, '750ml': 4, '1L': 5, 
                '1.5L': 6, '2L': 7, '2.5L': 8, '3L': 9,
            }
            idx = contenido_indices.get(self.contenido, 0)
            base_sku = f"{self.gaseosa.sku_base}{idx}"
            
            # Verificamos si ya existe ese SKU en la base de datos
            if Inventario.objects.filter(sku=base_sku).exists():
                # Si existe, le añadimos un sufijo incremental o único
                contador = 1
                nuevo_sku = f"{base_sku}-{contador}"
                while Inventario.objects.filter(sku=nuevo_sku).exists():
                    contador += 1
                    nuevo_sku = f"{base_sku}-{contador}"
                self.sku = nuevo_sku
            else:
                self.sku = base_sku

        super().save(*args, **kwargs)


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("procesado", "Procesado"),
        ("cancelado", "Cancelado"),
        ("entregado", "Entregado"),
    ]

    numero_pedido = models.CharField(max_length=20, unique=True)
    cliente = models.CharField(max_length=120)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def calcular_total(self, guardar=True):
        total = 0
        for item in self.itempedido_set.all():
            total += item.precio * item.cantidad
        self.total = total
        if guardar:
            self.save()

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    gaseosa = models.ForeignKey(Gaseosa, on_delete=models.CASCADE)
    inventario = models.ForeignKey(Inventario, on_delete=models.SET_NULL, null=True, blank=True)
    contenido = models.CharField(max_length=10)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return (Decimal(self.cantidad) * Decimal(self.precio)).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.cantidad}x {self.gaseosa.nombre}"


class Factura(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="factura")
    numero_factura = models.CharField(max_length=100, unique=True)
    fecha_factura = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def calcular_desde_pedido(self):
        subtotal = Decimal("0.00")
        for item in self.pedido.itempedido_set.all():
            subtotal += item.subtotal()
        self.subtotal = subtotal
        iva = (subtotal * Decimal("0.19")).quantize(Decimal("0.01"))
        self.total = subtotal + iva
        return self.total

    def calcular_iva(self):
        return (self.subtotal * Decimal("0.19")).quantize(Decimal("0.01"))


    def save(self, *args, **kwargs):
        if not self.subtotal or not self.total:
            self.calcular_desde_pedido()
        super().save(*args, **kwargs)

    @classmethod
    def generar_desde_pedido(cls, pedido):
        numero = f"FAC-{uuid.uuid4().hex[:8].upper()}"
        factura = cls(pedido=pedido, numero_factura=numero, subtotal=0, total=0)
        factura.calcular_desde_pedido()
        factura.save()
        return factura

    def __str__(self):
        return f"Factura {self.numero_factura}"


class CarritoTemporal(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    data = models.JSONField(default=dict)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


      