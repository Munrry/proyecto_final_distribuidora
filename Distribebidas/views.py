
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.urls import reverse
from .forms import InventarioForm
from .models import Inventario
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from .forms_auth import PerfilForm
from .models import Cliente
from xhtml2pdf import pisa
from .models import Gaseosa, Perfil, Factura, Pedido, Inventario, ItemPedido
from .models import Inventario, ItemPedido
from django.db.models import Sum  
from .models import Gaseosa, ItemPedido, Inventario
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def index(request):
    # Catálogo general de gaseosas
    bebidas = Gaseosa.objects.all() 
    
    recomendaciones = None
    es_nuevo_usuario = False
    
    if request.user.is_authenticated:
        # 1. INTENTAR TRAER EL HISTORIAL PERSONALIZADO (Usuario antiguo)
        bebidas_mas_compradas = ItemPedido.objects.filter(pedido__cliente=request.user.username)\
            .values('inventario')\
            .annotate(total_comprado=Sum('cantidad'))\
            .order_by('-total_comprado')[:3]
        
        inventario_ids = [item['inventario'] for item in bebidas_mas_compradas if item['inventario']]
        
        if inventario_ids:
            # Caso B: El usuario ya tiene historial real
            recomendaciones = Inventario.objects.filter(id__in=inventario_ids)
            es_nuevo_usuario = False
        else:
            # Caso A: El usuario es nuevo, le sugerimos lo más vendido de TODA la plataforma (CRM Global)
            top_global = ItemPedido.objects.values('inventario')\
                .annotate(total_vendido=Sum('cantidad'))\
                .order_by('-total_vendido')[:3]
            
            global_ids = [item['inventario'] for item in top_global if item['inventario']]
            
            if global_ids:
                recomendaciones = Inventario.objects.filter(id__in=global_ids)
            else:
                # Si la tienda es completamente nueva y nadie ha comprado nada, le muestra 3 productos aleatorios
                recomendaciones = Inventario.objects.all()[:3]
                
            es_nuevo_usuario = True

        top_global_data = None
    if request.user.is_authenticated and request.user.is_staff:
        # Traemos el inventario y anotamos la suma de lo vendido para el reporte administrativo
        top_global_data = ItemPedido.objects.values('inventario')\
            .annotate(total_vendido=Sum('cantidad'))\
            .order_by('-total_vendido')[:3]
        
        # Mapeamos los IDs de inventario para que el HTML pueda iterar los objetos reales
        for item in top_global_data:
            if item['inventario']:
                inventario_obj = Inventario.objects.filter(id=item['inventario']).first()
                if inventario_obj:
                    item['objeto'] = inventario_obj

    return render(request, 'Distribebidas/index.html', {
        'bebidas': bebidas,
        'recomendaciones': recomendaciones,
        'es_nuevo_usuario': es_nuevo_usuario,
        'top_global_data': top_global_data,  # 🌟 Enviamos los datos comerciales al admin
    })

        
    
   
def registrar(request):
    if request.method == "POST":
        # Usamos el formulario estándar de Django para evitar el ImportError
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.create(user=user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("Distribebidas:login")
    else:
        form = UserCreationForm()
    return render(request, "Distribebidas/registro.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            session_carrito = request.session.get('carrito', {})
            request.session['carrito'] = session_carrito
            return redirect('Distribebidas:index')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, 'Distribebidas/login.html')

def logout_view(request):
    logout(request)
    return redirect("Distribebidas:index")

@login_required
def perfil(request):
    usuario = request.user
    perfil, created = Perfil.objects.get_or_create(user=usuario)
    
    facturas_huerfanas = []
    for factura in Factura.objects.all():
        try:
            if not factura.pedido:
                facturas_huerfanas.append(factura.id)
            elif factura.pedido.cliente != usuario.username:
                facturas_huerfanas.append(factura.id)
        except Pedido.DoesNotExist:
            facturas_huerfanas.append(factura.id)
    
    if facturas_huerfanas:
        Factura.objects.filter(id__in=facturas_huerfanas).delete()
    
    pedidos = Pedido.objects.filter(cliente=usuario.username).order_by('-fecha')
    
    return render(request, 'Distribebidas/perfil.html', {
        'perfil': perfil,
        'pedidos': pedidos,
    })


@login_required

def modificar_perfil(request):
    perfil = Perfil.objects.filter(user=request.user).first()
    
    
    if not perfil:
        perfil = Perfil.objects.create(user=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('Distribebidas:perfil')
    else:
        form = PerfilForm(instance=perfil)
    
    
    return render(request, 'Distribebidas/modificar_perfil.html', {
        'form': form,
        'perfil': perfil
    })
@login_required
def cambiar_contrasena(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('Distribebidas:perfil')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'Distribebidas/cambiar_contrasena.html', {'form': form})

def carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    subtotal = 0
    for sku, datos in carrito.items():
        inventario_id = datos.get('inventario_id')
        if not inventario_id:
            continue
        try:
            inventario = Inventario.objects.get(id=inventario_id)
        except Inventario.DoesNotExist:
            continue
        cantidad = datos.get('cantidad', 1)
        item_subtotal = float(inventario.precio * cantidad)
        subtotal += item_subtotal
        productos.append({
            'gaseosa': inventario.gaseosa.nombre,
            'contenido': inventario.contenido,
            'sku': inventario.sku,
            'precio': inventario.precio,
            'cantidad': cantidad,
            'item_subtotal': item_subtotal,
        })
    iva = subtotal * 0.19
    total = subtotal + iva
    return render(request, 'Distribebidas/carrito.html', {
        'productos': productos,
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
    })

def agregar_carrito(request, inventario_id, cantidad=1):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    cantidad = int(cantidad)
    if cantidad > inventario.stock or inventario.stock == 0:
        messages.error(request, "No hay suficiente stock disponible para esta presentación.")
        return redirect('Distribebidas:pedido_cliente', inventario_id=inventario.id)
    
    carrito = request.session.get('carrito', {})
    sku = inventario.sku
    
    if sku in carrito:
        if carrito[sku]['cantidad'] + cantidad > inventario.stock:
            messages.error(request, "No hay suficiente stock disponible para esta presentación.")
            return redirect('Distribebidas:pedido_cliente', inventario_id=inventario.id)
        carrito[sku]['cantidad'] += cantidad
    else:
        carrito[sku] = {
            "inventario_id": inventario.id,
            "gaseosa": inventario.gaseosa.nombre,
            "contenido": inventario.contenido,
            "sku": inventario.sku,
            "precio": float(inventario.precio),
            "cantidad": cantidad
        }
    request.session['carrito'] = carrito
    messages.success(request, f"{inventario.gaseosa.nombre} {inventario.contenido} agregado al carrito.")
    return redirect('Distribebidas:carrito')

def vaciar_carrito(request):
    request.session["carrito"] = {}
    return redirect("Distribebidas:carrito")

def finalizar_compra(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect('Distribebidas:login')
    
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('Distribebidas:carrito')
    
    perfil = Perfil.objects.get(user=request.user)
    campos_requeridos = {
        'nombre': perfil.nombre,
        'correo': perfil.correo,
        'telefono': perfil.telefono,
        'direccion': perfil.direccion,
    }
    
    campos_faltantes = [campo for campo, valor in campos_requeridos.items() if not valor]
    
    if campos_faltantes:
        campos_texto = ', '.join(campos_faltantes)
        messages.error(
            request, 
            f"Debes completar los siguientes datos en tu perfil antes de finalizar: {campos_texto}. "
            f"<a href='{reverse('Distribebidas:modificar_perfil')}'>Ir a modificar perfil</a>"
        )
        return redirect('Distribebidas:carrito')
    
    for sku, item in carrito.items():
        inventario_id = item.get('inventario_id')
        if not inventario_id:
            messages.error(request, "Error: datos incompletos en el carrito.")
            return redirect('Distribebidas:carrito')
        try:
            inventario = Inventario.objects.get(id=inventario_id)
            if item['cantidad'] > inventario.stock:
                messages.error(request, f"No hay suficiente stock para {inventario.gaseosa.nombre} {inventario.contenido}.")
                return redirect('Distribebidas:carrito')
        except Inventario.DoesNotExist:
            messages.error(request, "Producto no encontrado. Recarga tu carrito.")
            return redirect('Distribebidas:carrito')
    
    try:
        with transaction.atomic():
            numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
            pedido = Pedido.objects.create(
                numero_pedido=numero_pedido,
                cliente=request.user.username,
                estado='procesado'
            )
            
            for sku, datos in carrito.items():
                inventario_id = datos.get('inventario_id')
                inventario = Inventario.objects.select_for_update().get(id=inventario_id)
                
                # Al crear el ItemPedido, la señal 'descontar_stock' en signals.py
                # se activa automáticamente y resta el inventario de manera segura.
                ItemPedido.objects.create(
                    pedido=pedido,
                    gaseosa=inventario.gaseosa,
                    inventario=inventario,
                    contenido=inventario.contenido,
                    cantidad=datos['cantidad'],
                    precio=inventario.precio
                )
                
                # ❌ ELIMINADAS LAS LÍNEAS MANUALES DE RESTA DE STOCK QUE DUPLICABAN EL PROCESO.
            
            factura = Factura.generar_desde_pedido(pedido)
            
        request.session['carrito'] = {}
        messages.success(request, "¡Compra completada exitosamente!")
        
        return redirect('Distribebidas:factura_detail', factura_id=factura.id)
    
    except IntegrityError:
        messages.error(request, "Error al crear el pedido. Intenta de nuevo.")
        return redirect('Distribebidas:carrito')
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect('Distribebidas:carrito')
@login_required
def crear_pedido_cliente(request):
    bebidas = Gaseosa.objects.prefetch_related('inventarios').all()
    return render(request, 'Distribebidas/crear_pedido_cliente.html', {'bebidas': bebidas})

def pedido_cliente(request, inventario_id):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    presentaciones = Inventario.objects.filter(gaseosa=inventario.gaseosa, stock__gt=0)
    if request.method == "POST":
        inventario_id = request.POST.get('inventario_id')
        cantidad = int(request.POST.get('cantidad', 1))
        return redirect('Distribebidas:agregar_carrito', inventario_id=inventario_id, cantidad=cantidad)
    return render(request, 'Distribebidas/pedido_cliente.html', {
        'gaseosa': inventario.gaseosa,
        'presentaciones': presentaciones,
        'inventario': inventario,
        'descripcion': inventario.gaseosa.descripcion, 
    })

@login_required
def factura_detail(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'Distribebidas/factura_detail.html', {'factura': factura})

@login_required
def factura_pdf(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    template_path = 'Distribebidas/factura_pdf_plantilla.html'
    context = {'factura': factura}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.id}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response


@login_required
def agregar_inventario(request):
    if not request.user.is_staff:
        return redirect('Distribebidas:index')
        
    if request.method == 'POST':
        form = InventarioForm(request.POST, request.FILES) # Soportamos también si subes imagen
        if form.is_valid():
            form.save()
            messages.success(request, "Presentación agregada al inventario con éxito.")
            return redirect('Distribebidas:dashboard_admin') # Te redirige directo al panel corregido
    else:
        form = InventarioForm()
        
    return render(request, 'Distribebidas/inventario_form.html', {'form': form})

@login_required
def editar_inventario(request, pk):
    # Comprobamos que el usuario sea administrador (staff)
    if not request.user.is_staff:
        return redirect('Distribebidas:index')
        
    inventario = get_object_or_404(Inventario, pk=pk)
    
    if request.method == 'POST':
        # Pasamos instance=inventario para que edite el registro existente en vez de crear uno nuevo
        form = InventarioForm(request.POST, request.FILES, instance=inventario)
        if form.is_valid():
            form.save()
            messages.success(request, f"La presentación de {inventario.gaseosa.nombre} fue actualizada correctamente.")
            return redirect('Distribebidas:dashboard_admin') # Redirige de vuelta al panel
    else:
        form = InventarioForm(instance=inventario)
        
    return render(request, 'Distribebidas/inventario_form.html', {
        'form': form,
        'editando': True,
        'inventario': inventario
    }) 

@login_required
def inventario_list(request):
    if not request.user.is_staff:
        return redirect('Distribebidas:index')
    inventarios = Inventario.objects.select_related('gaseosa').all()
    return render(request, 'Distribebidas/inventario_list.html', {'inventarios': inventarios})

@require_POST
def eliminar_carrito(request, sku):
    carrito = request.session.get('carrito', {})
    if sku in carrito:
        del carrito[sku]
        request.session['carrito'] = carrito
        messages.success(request, "Producto eliminado del carrito.")
    return redirect('Distribebidas:carrito')

@require_POST
def actualizar_cantidad(request, sku):
    accion = request.POST.get('accion')
    carrito = request.session.get('carrito', {})
    for pid, item in carrito.items():
        if item['sku'] == sku:
            if accion == 'mas':
                item['cantidad'] += 1
            elif accion == 'menos' and item['cantidad'] > 1:
                item['cantidad'] -= 1
            break
    request.session['carrito'] = carrito
    return redirect('Distribebidas:carrito')

@login_required
def dashboard_admin(request):
    if not request.user.is_staff:
        return redirect('Distribebidas:index')
        
    inventarios = Inventario.objects.select_related('gaseosa').all()
    total_bebidas = inventarios.count()
    bebidas_agotadas = inventarios.filter(stock=0).count()
    pedidos = Pedido.objects.all().order_by('-fecha')
    
    ventas_totales = sum(pedido.total for pedido in pedidos if pedido.total)

    return render(request, 'Distribebidas/admin_dashboard.html', {
        'inventarios': inventarios,
        'total_bebidas': total_bebidas,
        'bebidas_agotadas': bebidas_agotadas,
        'pedidos': pedidos,
        'ventas_totales': ventas_totales,
    })

@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    detalles = pedido.itempedido_set.all()
    return render(request, 'Distribebidas/pedido_detail.html', {
        'pedido': pedido,
        'detalles': detalles,
 })
@staff_member_required
def cambiar_estado_pedido(request, pedido_id, nuevo_estado):
    """Cambia el estado transaccional del pedido y refresca la pantalla de detalle."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Lista de estados válidos según tu modelo
    estados_validos = ["pendiente", "pagado", "procesado", "cancelado", "entregado"]
    
    if nuevo_estado in estados_validos:
        pedido.estado = nuevo_estado
        pedido.save()
        
    # Redirecciona automáticamente a la misma página donde estabas
    return redirect('Distribebidas:detalle_pedido', pk=pedido.id)
  

    