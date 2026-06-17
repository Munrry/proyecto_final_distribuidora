from django import forms
from .models import Cliente
from django.forms import inlineformset_factory
from .models import Pedido, ItemPedido, Gaseosa, Inventario

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['numero_pedido', 'cliente', 'estado']

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['gaseosa', 'cantidad', 'precio']
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01'})
        }

ItemPedidoFormSet = inlineformset_factory(Pedido, ItemPedido, form=ItemPedidoForm, extra=1, can_delete=True)

class GaseosaForm(forms.ModelForm):
    class Meta:
        model = Gaseosa
        fields = ['marca', 'nombre', 'sku_base', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['gaseosa', 'contenido', 'precio', 'stock']
        widgets = {
            'contenido': forms.Select(choices=Inventario.CONTENIDO_OPCIONES),
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }
