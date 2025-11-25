from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Plato(models.Model):
    CATEGORIAS_PLATO = [
        ('ENTRADA', 'Entrada'),
        ('PLATO_PRINCIPAL', 'Plato Principal'),
        ('POSTRE', 'Postre'),
        ('BEBIDA', 'Bebida'),
        ('ENSALADA', 'Ensalada'),
        ('SOPA', 'Sopa'),
    ]
    
    id_plato = models.AutoField(primary_key=True)
    nombre_plato = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    categoria = models.CharField(max_length=50, choices=CATEGORIAS_PLATO)
    tiempo_preparacion = models.IntegerField(validators=[MinValueValidator(0)])  # en minutos
    ingredientes = models.TextField()
    disponible = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre_plato} - ${self.precio}"
    
    class Meta:
        verbose_name = 'Plato'
        verbose_name_plural = 'Platos'

class Mesa(models.Model):
    ESTADOS_MESA = [
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
    ]
    
    id_mesa = models.AutoField(primary_key=True)
    numero_mesa = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    capacidad = models.IntegerField(validators=[MinValueValidator(1)])
    estado_mesa = models.CharField(max_length=50, choices=ESTADOS_MESA, default='DISPONIBLE')
    ubicacion = models.CharField(max_length=100)  # Ej: "Terraza", "Interior", "Ventana"
    es_reservable = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.ubicacion} (Cap: {self.capacidad})"
    
    class Meta:
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'

class Empleado_Restaurante(models.Model):
    CARGOS_EMPLEADO = [
        ('GERENTE', 'Gerente'),
        ('CHEF', 'Chef'),
        ('MESERO', 'Mesero'),
        ('CAJERO', 'Cajero'),
        ('BARTENDER', 'Bartender'),
        ('LIMPIEZA', 'Limpieza'),
    ]
    
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50, choices=CARGOS_EMPLEADO)
    salario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_contratacion = models.DateField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo}"
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

class Cliente_Restaurante(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    fecha_registro = models.DateField(auto_now_add=True)
    preferencias_alimentarias = models.TextField(blank=True, null=True)
    puntos_fidelidad = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.email}"
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('EN_PREPARACION', 'En Preparación'),
        ('LISTO', 'Listo para Servir'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPOS_PEDIDO = [
        ('RESTAURANTE', 'En Restaurante'),
        ('DOMICILIO', 'Domicilio'),
        ('RECOGER', 'Para Llevar'),
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    id_mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    id_empleado = models.ForeignKey(Empleado_Restaurante, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    estado_pedido = models.CharField(max_length=50, choices=ESTADOS_PEDIDO, default='PENDIENTE')
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tipo_pedido = models.CharField(max_length=50, choices=TIPOS_PEDIDO, default='RESTAURANTE')
    hora_pedido = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.fecha_pedido.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los subtotales de los detalles"""
        detalles = self.detalles.all()
        total = sum(detalle.subtotal for detalle in detalles)
        self.total_pedido = total
        self.save()
        return total
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

class Detalle_Pedido(models.Model):
    id_detalle_pedido = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    id_plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='detalles_pedidos')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notas_plato = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    descuento_item = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el subtotal al guardar"""
        precio_con_descuento = self.precio_unitario * (1 - self.descuento_item / 100)
        self.subtotal = precio_con_descuento * self.cantidad
        super().save(*args, **kwargs)
        # Actualizar el total del pedido
        self.id_pedido.calcular_total()
    
    def __str__(self):
        return f"Detalle #{self.id_detalle_pedido} - Pedido #{self.id_pedido.id_pedido}"
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

class Reserva(models.Model):
    ESTADOS_RESERVA = [
        ('CONFIRMADA', 'Confirmada'),
        ('PENDIENTE', 'Pendiente'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
        ('NO_SHOW', 'No Show'),
    ]
    
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente_Restaurante, on_delete=models.CASCADE, related_name='reservas')
    id_mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    num_personas = models.IntegerField(validators=[MinValueValidator(1)])
    estado_reserva = models.CharField(max_length=50, choices=ESTADOS_RESERVA, default='PENDIENTE')
    comentarios = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Reserva #{self.id_reserva} - {self.id_cliente.nombre} - {self.fecha_reserva}"
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        unique_together = ['id_mesa', 'fecha_reserva', 'hora_reserva']
