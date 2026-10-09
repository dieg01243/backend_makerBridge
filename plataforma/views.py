from django.http import JsonResponse, request
from django.utils import timezone
from .models import Compra, Producto, Usuario, Pedido, Cotizacion, Pago, LoginHistorial
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status



@csrf_exempt
def register_user(request): #request basicamnete obtiene toda la información que el usuario envía al endpoint, ya sea por GET o POST
#     ej:
#     Ahí request puede contener:
# 
# request.method → "GET", "POST", etc.
# request.body → datos enviados por React.
# request.headers → headers de la petición.
# request.user → usuario autenticado, si corresponde.
# request.GET → parámetros enviados en la URL.
# request.POST → datos de formularios tradicionales.
#==============================================================================
    # Lógica para registrar un nuevo usuario
    


    #verificamos que sea POST
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #sacar el JSON que mando react
    datos = json.loads(request.body)

    #extraer los datos del JSON
    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]
    rol = datos["rol"]
    activo = True
    fecha_registro = timezone.now()

    #crear objeto y agregarlo a la base de datos
    #aca hace las 2 operaciones a la vez
    #.objet crea el objeto y .create crea el objeto en la base de datos
    usuario = Usuario.objects.create(
        nombre=nombre,
        email=email,
        password_hash=password,
        rol=rol,
        activo=activo,
        fecha_registro=fecha_registro
    )
    
    # 5. Responderle a React
    return JsonResponse({
        "mensaje": "Usuario registrado",
        "id_usuario": usuario.id_usuario
    }, status=201)


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    datos = json.loads(request.body)

    email = datos["email"]
    password = datos["password"]

    #con ORM verifica si existe ese mail en la talbla de usuarios
    usuario = Usuario.objects.filter(email=email).first()

    #si no encuentra al usuario
    if usuario is None:
        return Response(
        {"error": "Usuario no encontrado"},
        status=status.HTTP_404_NOT_FOUND
        )
    #si encuentra al usuario, verificamos la contraseña
    if usuario.password_hash != password:
        return Response(
        {"error": "Contraseña incorrecta"},
        status=status.HTTP_401_UNAUTHORIZED
        )
    
    #=========COKIES===========
    request.session["id_usuario"] = usuario.id_usuario
    request.session["rol"] = usuario.rol
    #==========================
    
    #se verifico al usuario y ahora se separan los roles
    if usuario.rol == "maker":
        return Response(
            {"mensaje": "Login exitoso", "rol": "maker", "id_usuario": usuario.id_usuario},
            status=status.HTTP_200_OK,
        )

    elif usuario.rol == "cliente":
        return Response(
            {"mensaje": "Login exitoso", "rol": "cliente", "id_usuario": usuario.id_usuario},
            status=status.HTTP_200_OK,
        )

    #========esto no deberia pasar jajaj===========
    return Response(
        {"error": "Rol no permitido"},
        status=status.HTTP_403_FORBIDDEN,
    )
    #==============================================



#===========================================================================
#==========================CLIENTE==========================================
#===========================================================================



#==============================
@csrf_exempt
def ver_lista_de_productos(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    productos = Producto.objects.all()
    lista_productos = []

    for producto in productos:
        lista_productos.append({
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio": str(producto.precio),  # Convertir Decimal a string
            "imagen_url": producto.imagen_url,
        })

    #se envia una lista de objetos JSON con todos los productos
    return JsonResponse({"productos": lista_productos}, status=200)

#=============================
#cuando tocan un producto de interes y les mostrara el detalle del producto
@csrf_exempt
def ver_producto(request, id_producto):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #buscar el producto por id
    producto = Producto.objects.filter(id_producto=id_producto).first()

    if producto is None:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

    #si lo encuentra, se envia la info del producto
    detalle_producto = {
        "id_producto": producto.id_producto,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": str(producto.precio),  # Convertir Decimal a string
        "imagen_url": producto.imagen_url,
    }

    return JsonResponse({"producto": detalle_producto}, status=200)

#crear pedido POST
@csrf_exempt
def crear_pedido(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #datos del pedido | 
    datos = json.loads(request.body)

    id_usuario = datos["id_usuario"]
    descripcion = datos["descripcion"]
    cantidad = datos["cantidad"]
    material = datos["material"]   
    color = datos["color"]
    archivo_3d_url = datos["archivo_3d_url"]
    fecha_limite = datos["fecha_limite"]
    estado = "pendiente"  # Estado inicial del pedido
    fecha_pedido = timezone.now()

    #creacion del objeto e ingreso de datos a la talba de pedidos
    pedido = Pedido.objects.create(
        id_usuario=id_usuario,
        descripcion=descripcion,
        cantidad=cantidad,
        material=material,
        color=color,
        archivo_3d_url=archivo_3d_url,
        fecha_limite=fecha_limite,
        estado=estado,
        fecha_pedido=fecha_pedido
    )
    return JsonResponse({
        "mensaje": "Pedido creado",
        "id_pedido": pedido.id_pedido
    }, status=201)


#ver lista de pedidos GET //me enviaria los datos del usuario y lo filtro en la tabla pedidos
@csrf_exempt
def ver_lista_de_pedidos(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #obtener el id del usuario desde los parámetros de la URL
    id_usuario = request.GET.get("id_usuario")

    #verificar si se proporcionó el id del usuario
    if not id_usuario:
        return JsonResponse({"error": "Se requiere el id del usuario"}, status=400)

    #filtrar los pedidos por el id del usuario
    pedidos = Pedido.objects.filter(id_usuario=id_usuario)
    lista_pedidos = []

    for pedido in pedidos:
        lista_pedidos.append({
            "id_pedido": pedido.id_pedido,
            "descripcion": pedido.descripcion,
            "cantidad": pedido.cantidad,
            "material": pedido.material,
            "color": pedido.color,
            "archivo_3d_url": pedido.archivo_3d_url,
            "fecha_limite": pedido.fecha_limite,
            "estado": pedido.estado,
            "fecha_pedido": pedido.fecha_pedido,
        })

    

    return JsonResponse({"pedidos": lista_pedidos}, status=200)

#ver lista de pedidos cotizados GET
@csrf_exempt
def ver_lista_de_pedidos_cotizados(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #obtener el id del usuario desde los parámetros de la URL
    id_usuario = request.GET.get("id_usuario")

    #verificar si se proporcionó el id del usuario
    if not id_usuario:
        return JsonResponse({"error": "Se requiere el id del usuario"}, status=400)

    #filtrar los pedidos por el id del usuario y estado "cotizado"
    pedidos_cotizados = Pedido.objects.filter(id_usuario=id_usuario, estado="cotizado")
    lista_pedidos_cotizados = []

    for pedido in pedidos_cotizados:
        lista_pedidos_cotizados.append({
            "id_pedido": pedido.id_pedido,
            "descripcion": pedido.descripcion,
            "cantidad": pedido.cantidad,
            "material": pedido.material,
            "color": pedido.color,
            "archivo_3d_url": pedido.archivo_3d_url,
            "fecha_limite": pedido.fecha_limite,
            "estado": pedido.estado,
            "fecha_pedido": pedido.fecha_pedido,
        })

    return JsonResponse({"pedidos_cotizados": lista_pedidos_cotizados}, status=200)

#comprar producto // nos llega los datos del producto

@csrf_exempt
def comprar_producto(request, id_producto):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Método no permitido"}, status=405
        )

    # 1. Obtener el ID del usuario desde la sesión
    id_usuario = request.session.get("id_usuario")

    if id_usuario is None:
        return JsonResponse(
            {"error": "Debes iniciar sesión"}, status=401
        )

    # 2. Obtener los datos que envía React
    try:
        datos = json.loads(request.body)
        cantidad = int(datos["cantidad"])

        if cantidad <= 0:
            return JsonResponse(
                {"error": "La cantidad debe ser mayor a cero"},
                status=400
            )

    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return JsonResponse(
            {"error": "Datos inválidos"}, status=400
        )

    # 3. Buscar el producto en la base de datos
    producto = Producto.objects.filter(
        id_producto=id_producto,
        activo=True
    ).first()

    if producto is None:
        return JsonResponse(
            {"error": "Producto no encontrado"}, status=404
        )

    # 4. Verificar el stock
    if producto.stock < cantidad:
        return JsonResponse(
            {"error": "Stock insuficiente"}, status=400
        )

    # 5. Calcular el importe desde el precio de la base de datos
    precio_unitario = producto.precio
    monto_total = precio_unitario * cantidad

    # 6. Registrar la compra
    compra = Compra.objects.create(
        id_usuario_id=id_usuario,
        id_producto_id=producto.id_producto,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        monto_total=monto_total,
        estado="pendiente"
    )

    # 7. Responder a React
    return JsonResponse({
        "mensaje": "Compra registrada",
        "id_compra": compra.id_compra,
        "monto_total": str(compra.monto_total),
        "estado": compra.estado
    }, status=201)

#============================
@csrf_exempt
def ver_compras(request):
    if request.method != "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # Obtener el ID del usuario desde la sesión
    id_usuario = request.session.get("id_usuario")

    if id_usuario is None:
        return JsonResponse({"error": "Debes iniciar sesión"}, status=401)

    # Filtrar las compras por el ID del usuario
    compras = Compra.objects.filter(id_usuario=id_usuario)
    lista_compras = []

    for compra in compras:
        lista_compras.append({
            "id_compra": compra.id_compra,
            "id_producto": compra.id_producto.id_producto,
            "nombre_producto": compra.id_producto.nombre,
            "cantidad": compra.cantidad,
            "precio_unitario": str(compra.precio_unitario),
            "monto_total": str(compra.monto_total),
            "estado": compra.estado,
        })

    return JsonResponse({"compras": lista_compras}, status=200)