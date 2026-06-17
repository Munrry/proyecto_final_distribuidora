from django.contrib import admin
from .models import Cliente, Gaseosa, Inventario, Pedido, ItemPedido, Factura


class ItemInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'cliente', 'estado', 'total')
    inlines = [ItemInline]
    actions = ["generar_factura"]

    def generar_factura(self, request, queryset):
        for pedido in queryset:
            if not hasattr(pedido, "factura"):
                Factura.generar_desde_pedido(pedido)
        self.message_user(request, "Facturas generadas correctamente.")

    generar_factura.short_description = "Generar factura para pedidos seleccionados"

admin.site.register(Gaseosa)
admin.site.register(Cliente)
admin.site.register(Factura)

class InventarioAdmin(admin.ModelAdmin):
    list_display = ('gaseosa', 'contenido', 'sku', 'precio', 'stock', 'ultima_actualizacion')
    readonly_fields = ('sku',)

admin.site.register(Inventario, InventarioAdmin)
