from django.urls import path
from . import views

app_name = 'Distribebidas'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registrar, name='registro'),
    
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/modificar/', views.modificar_perfil, name='modificar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    
    path('pedido/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/cliente/', views.crear_pedido_cliente, name='crear_pedido_cliente'),
    path('pedido/cliente/<int:inventario_id>/', views.pedido_cliente, name='pedido_cliente'),

    
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:inventario_id>/<int:cantidad>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('carrito/eliminar/<str:sku>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('carrito/actualizar/<str:sku>/', views.actualizar_cantidad, name='actualizar_cantidad'),

    path('factura/<int:factura_id>/', views.factura_detail, name='factura_detail'),
    path('factura/<int:factura_id>/pdf/', views.factura_pdf, name='factura_pdf'),
    
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('inventario/agregar/', views.agregar_inventario, name='agregar_inventario'),
    path('inventario/editar/<int:pk>/', views.editar_inventario, name='editar_inventario'),
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('pedido/<int:pedido_id>/cambiar-estado/<str:nuevo_estado>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]
