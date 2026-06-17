from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import ItemPedido, Inventario
from decimal import Decimal


@receiver(pre_save, sender=ItemPedido)
def calcular_delta(sender, instance, **kwargs):
    """
    Calcula la diferencia (delta) entre la cantidad nueva y la anterior.
    Valida que haya stock disponible.
    """
    if instance.pk:
        old = ItemPedido.objects.get(pk=instance.pk)
        instance._delta = instance.cantidad - old.cantidad
    else:
        instance._delta = instance.cantidad
    
    # Validar stock si existe inventario
    if instance.inventario:
        if instance._delta > instance.inventario.stock:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {instance.inventario.stock}, Solicitado: {instance._delta}"
            )


@receiver(post_save, sender=ItemPedido)
def descontar_stock(sender, instance, created, **kwargs):
    """
    Descuenta stock después de guardar ItemPedido.
    """
    if instance.inventario and hasattr(instance, '_delta'):
        instance.inventario.stock -= instance._delta
        instance.inventario.save()
        
        # Si después del descuento el stock queda en 10 o menos (pero mayor a 0)
        if 0 < instance.inventario.stock <= 10:
            print(f"\n REABASTECIMIENTO REQUERIDO: "
                  f"La gaseosa '{instance.inventario.gaseosa.nombre}' ({instance.inventario.contenido}) "
                  f"ha entrado en stock crítico. Quedan solo {instance.inventario.stock} unidades.\n")
    
    # Recalcular total del pedido
    if instance.pedido:
        instance.pedido.calcular_total()


@receiver(post_delete, sender=ItemPedido)
def restaurar_stock(sender, instance, **kwargs):
    """
    Restaura stock cuando se elimina un ItemPedido.
    """
    if instance.inventario:
        instance.inventario.stock += instance.cantidad
        instance.inventario.save()
    
    # Recalcular total del pedido
    if instance.pedido:
        instance.pedido.calcular_total()