from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .models import categoria, subcategoria, roles, usuario, domiciliario, producto, Calificacion
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from .models import usuario, CodigoVerificacion
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def LadingPage(request):
    categorias = categoria.objects.all().prefetch_related('subcategoria_set')
    productos = producto.objects.all().select_related('IdSubCategoria__categoria').order_by('-IdProducto')

    def agrupar_productos(productos, grupo_de):
        return [productos[i:i+grupo_de] for i in range(0, len(productos), grupo_de)]

    productos_agrupados = agrupar_productos(list(productos), 4)

    return render(request, 'LadingPage.html', {
        'categorias': categorias,
        'productos_agrupados': productos_agrupados,
        'productos': productos,  # <-- AGREGA ESTA LÍNEA
        'username': request.session.get('username', ''),
        'first_name': request.session.get('first_name', ''),
    })


#region categorias
def insertarcategorias(request):
    if request.method == "POST":
        if request.POST.get('NombreCategoria'):
            insertar = connection.cursor()
            insertar.execute("CALL insertarcategorias(%s)", [request.POST.get('NombreCategoria')])
            return redirect("listadocategorias")
    return render(request, 'listadocategorias')

def listadocategorias(request):
    listado = connection.cursor()
    listado.execute("CALL listadocategorias()")
    categorias = listado.fetchall()
    return render(request, "crud/categorias.html", {"listado": categorias})

def borrarcategoria(request, id_categoria):
    try:
        borrar = connection.cursor()
        borrar.execute("CALL borrarcategoria(%s)", [id_categoria])
        messages.success(request, "Categoría eliminada correctamente.")
    except IntegrityError:
        messages.error(request, "No se puede eliminar la categoría porque tiene subcategorías asociadas.")
    return redirect('listadocategorias')

def actualizarcategoria(request, id_categoria):
    if request.method == "POST":
        if request.POST.get('NombreCategoria'):
            actualizar = connection.cursor()
            actualizar.execute("CALL actualizarcategoria(%s, %s)", [id_categoria, request.POST.get('NombreCategoria')])
            return redirect("listadocategorias")
    else:
        categoria = connection.cursor()
        categoria.execute("CALL consultarcategoria(%s)", [id_categoria])
        categoria = categoria.fetchone()
        return render(request, 'crud/editar_categoria.html', {'categoria': categoria})
# endregion


# region subcategorias
def listadosubcategorias(request):
    subcategorias = subcategoria.objects.all()
    categorias = categoria.objects.all()
    return render(request, 'crud/subcategorias.html', {'subcategorias': subcategorias, 'categorias': categorias})

def validar_nombre_subcategoria(nombre):
    if not nombre or not nombre.strip():
        return "Nombre requerido"
    if re.search(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]', nombre):
        return "Nombre inválido"
    return None

def insertarsubcategoria(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria_id')
        error = validar_nombre_subcategoria(nombre)
        if error:
            messages.error(request, error)
            return redirect('crudSubCategorias')
        # Duplicado
        if subcategoria.objects.filter(NombresubCategoria__iexact=nombre, categoria_id=categoria_id).exists():
            messages.error(request, "Subcategoría ya existe")
            return redirect('crudSubCategorias')
        nueva_subcategoria = subcategoria(NombresubCategoria=nombre, categoria_id=categoria_id)
        nueva_subcategoria.save()
        messages.success(request, "Subcategoría registrada exitosamente")
        return redirect('crudSubCategorias')
    return redirect('crudSubCategorias')

def actualizarsubcategoria(request, id_subcategoria):
    subcat = get_object_or_404(subcategoria, IdSubCategoria=id_subcategoria)
    if request.method == "POST":
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria_id')
        error = validar_nombre_subcategoria(nombre)
        if error:
            messages.error(request, error)
            return redirect('crudSubCategorias')
        # Sin cambios
        if nombre == subcat.NombresubCategoria and int(categoria_id) == subcat.categoria_id:
            messages.info(request, "Sin cambios realizados")
            return redirect('crudSubCategorias')
        # Duplicado
        if subcategoria.objects.filter(NombresubCategoria__iexact=nombre, categoria_id=categoria_id).exclude(IdSubCategoria=id_subcategoria).exists():
            messages.error(request, "Subcategoría ya existe")
            return redirect('crudSubCategorias')
        subcat.NombresubCategoria = nombre
        subcat.categoria_id = categoria_id
        subcat.save()
        messages.success(request, "Subcategoría actualizada exitosamente")
        return redirect('crudSubCategorias')
    return redirect('crudSubCategorias')

def borrarsubcategoria(request, id_subcategoria):
    subcat = get_object_or_404(subcategoria, IdSubCategoria=id_subcategoria)
    # Bloquear si tiene productos relacionados
    if producto.objects.filter(IdSubCategoria=subcat).exists():
        messages.error(request, "Subcategoría en uso")
        return redirect('crudSubCategorias')
    subcat.delete()
    messages.success(request, "Subcategoría eliminada")
    return redirect('crudSubCategorias')
#endregion


# region login
def validar_registro_usuario(data):
    # Todos los campos obligatorios
    campos = ['PrimerNombre', 'OtrosNombres', 'PrimerApellido', 'SegundoApellido', 'Correo', 'NombreUsuario', 'Contraseña']
    for campo in campos:
        if not data.get(campo) or not data.get(campo).strip():
            if campo == 'NombreUsuario':
                return "Nombre de usuario es obligatorio"
            if campo == 'Contraseña':
                return "Contraseña es obligatoria"
            return "Todos los campos son obligatorios"

    # Nombre de usuario largo/corto
    nombre_usuario = data.get('NombreUsuario').strip()
    if len(nombre_usuario) < 3:
        return "El nombre de usuario debe tener al menos 3 caracteres"
    if len(nombre_usuario) > 50:
        return "Nombre excede el límite de caracteres"

    # Contraseña débil y con espacios
    contraseña = data.get('Contraseña')
    if len(contraseña) < 8:
        return "La contraseña debe tener al menos 8 caracteres"
    if ' ' in contraseña:
        return "La contraseña no debe contener espacios"

    return None

def registro(request):
    if request.method == "POST":
        error = validar_registro_usuario(request.POST)
        if error:
            messages.error(request, error)
            return render(request, 'login/registro.html')

        # Usuario duplicado (case sensitive permitido)
        nombre_usuario = request.POST.get('NombreUsuario').strip()
        if usuario.objects.filter(NombreUsuario=nombre_usuario).exists():
            messages.error(request, "El usuario ya existe")
            return render(request, 'login/registro.html')

        rol_default = roles.objects.get(IdRol=3)
        nuevo_usuario = usuario(
            PrimerNombre=request.POST.get('PrimerNombre').strip(),
            OtrosNombres=request.POST.get('OtrosNombres').strip(),
            PrimerApellido=request.POST.get('PrimerApellido').strip(),
            SegundoApellido=request.POST.get('SegundoApellido').strip(),
            Correo=request.POST.get('Correo').strip(),
            NombreUsuario=nombre_usuario,
            Contraseña=make_password(request.POST.get('Contraseña')),
            idRol=rol_default
        )
        nuevo_usuario.save()
        messages.success(request, "Usuario registrado exitosamente")
        return redirect('login')
    return render(request, 'login/registro.html') 


def login(request):
    # --- Bloqueo tras múltiples intentos fallidos ---
    max_intentos = 5
    intentos = request.session.get('login_intentos', 0)
    bloqueado = request.session.get('login_bloqueado', False)

    if bloqueado:
        return render(request, 'login/login.html', {'error': 'Cuenta bloqueada temporalmente'})

    if request.method == "POST":
        correo = request.POST.get('correo', '').strip()
        contraseña = request.POST.get('contraseña', '').strip()

        # --- Validación de campos vacíos ---
        if not correo and not contraseña:
            return render(request, 'login/login.html', {'error': 'Campos obligatorios'})
        if not correo:
            return render(request, 'login/login.html', {'error': 'Este campo es obligatorio'})
        if not contraseña:
            return render(request, 'login/login.html', {'error': 'credenciales invaliadas'})

        # --- Validación de formato de correo ---
        try:
            validate_email(correo)
        except ValidationError:
            return render(request, 'login/login.html', {'error': 'credenciales invaliadas'})

        # --- Usuario no registrado ---
        try:
            user = usuario.objects.get(Correo=correo)
        except usuario.DoesNotExist:
            return render(request, 'login/login.html', {'error': 'Usuario no encontrado'})

        # --- Contraseña incorrecta ---
        if not (user.Contraseña == contraseña or check_password(contraseña, user.Contraseña)):
            intentos += 1
            request.session['login_intentos'] = intentos
            if intentos >= max_intentos:
                request.session['login_bloqueado'] = True
                return render(request, 'login/login.html', {'error': 'Cuenta bloqueada temporalmente'})
            return render(request, 'login/login.html', {'error': 'credenciales invaliadas'})

        # --- Login exitoso ---
        request.session['user_id'] = user.IdUsuario
        request.session['username'] = user.NombreUsuario
        request.session['nombre'] = f"{user.PrimerNombre} {user.PrimerApellido}"
        request.session['role'] = user.idRol.IdRol
        request.session['login_intentos'] = 0
        request.session['login_bloqueado'] = False
        return redirect('Ladingpage')

    return render(request, 'login/login.html')



def logout(request):
    request.session.flush()
    return redirect('Ladingpage')  


def solicitar_recuperacion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = usuario.objects.get(Correo=email)
            
            # Generar código
            codigo_obj = CodigoVerificacion.generar_codigo(user)
            
            # Enviar correo con el código (versión visual con HTML)
            asunto = 'Código de recuperación de contraseña'

            mensaje_html = f"""
            <html>
              <head>
                <style>
                  body {{
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                    padding: 20px;
                  }}
                  .container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                  }}
                  .header {{
                    color: #f5365c;
                    text-align: center;
                  }}
                  .codigo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #f5365c;
                    text-align: center;
                    margin: 30px 0;
                  }}
                  .footer {{
                    font-size: 13px;
                    color: #888;
                    text-align: center;
                    margin-top: 40px;
                  }}
                </style>
              </head>
              <body>
                <div class="container">
                  <h2 class="header">Recuperación de Contraseña</h2>
                  <p>Hola,</p>
                  <p>Recibimos una solicitud para recuperar el acceso a tu cuenta en <strong>Fantasía Íntima</strong>.</p>
                  <p>Ingresa el siguiente código en la página para continuar con el proceso:</p>
                  
                  <div class="codigo">{codigo_obj.codigo}</div>
                  
                  <p>Este código estará disponible durante los próximos <strong>15 minutos</strong>.</p>
                  <p>Si no solicitaste este cambio, puedes ignorar este mensaje.</p>

                  <div class="footer">
                    &copy; 2025 Fantasía Íntima. Todos los derechos reservados.
                  </div>
                </div>
              </body>
            </html>
            """

            send_mail(
                asunto,
                '',  # Texto plano vacío (puedes incluir versión simple si quieres)
                'store.fantasia.intima@gmail.com',
                [email],
                fail_silently=False,
                html_message=mensaje_html  # Aquí enviamos el mensaje bonito
            )
            
            request.session['email_recuperacion'] = email
            messages.success(request, 'Se ha enviado un código de verificación a tu correo.')
            return redirect('verificar_codigo')
        
        except usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta asociada a ese correo.')
    
    return render(request, 'login/recuperarcontraseña.html')


def verificar_codigo(request):
    email = request.session.get('email_recuperacion')
    
    if not email:
        messages.error(request, 'Debes solicitar un código primero.')
        return redirect('solicitar_recuperacion')
    
    if request.method == 'POST':
        codigo_ingresado = ''.join([request.POST.get(f'digit{i}', '') for i in range(1, 7)])
        
        try:
            user = usuario.objects.get(Correo=email)
            codigo_obj = CodigoVerificacion.objects.filter(
                usuario=user,
                utilizado=False,
                codigo=codigo_ingresado
            ).latest('fecha_creacion')
            
            if codigo_obj.es_valido():
                codigo_obj.utilizado = True
                codigo_obj.save()
                
                request.session['codigo_verificado'] = True
                return redirect('nueva_contrasena')
            else:
                messages.error(request, 'El código ha expirado.')
        
        except (usuario.DoesNotExist, CodigoVerificacion.DoesNotExist):
            messages.error(request, 'Código inválido.')
    
    return render(request, 'login/codigo.html')

def nueva_contrasena(request):
    email = request.session.get('email_recuperacion')
    codigo_verificado = request.session.get('codigo_verificado', False)
    
    if not email or not codigo_verificado:
        messages.error(request, 'Debes verificar un código primero.')
        return redirect('solicitar_recuperacion')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'nueva_contrasena.html')
        
        try:
            user = usuario.objects.get(Correo=email)
            user.Contraseña = make_password(password)  # Importante: hashear la nueva contraseña
            user.save()
            
            # Limpiar la sesión
            request.session.pop('email_recuperacion', None)
            request.session.pop('codigo_verificado', None)
            
            return redirect('login')
        
        except usuario.DoesNotExist:
            messages.error(request, 'Ocurrió un error al actualizar la contraseña.')
    
    return render(request, 'login/nuevaContraseña.html')


def insertarusuario(request):
    if request.method == "POST":
        if (request.POST.get('PrimerNombre') and request.POST.get('OtrosNombres') and
            request.POST.get('PrimerApellido') and request.POST.get('SegundoApellido') and
            request.POST.get('Correo') and request.POST.get('NombreUsuario') and
            request.POST.get('Contraseña')):

            rol_default = roles.objects.get(IdRol=3)  
            nuevo_usuario = usuario(
                PrimerNombre=request.POST.get('PrimerNombre'),
                OtrosNombres=request.POST.get('OtrosNombres'),
                PrimerApellido=request.POST.get('PrimerApellido'),
                SegundoApellido=request.POST.get('SegundoApellido'),
                Correo=request.POST.get('Correo'),
                NombreUsuario=request.POST.get('NombreUsuario'),
                Contraseña=make_password(request.POST.get('Contraseña')),
                idRol=rol_default
            )
            nuevo_usuario.save()
            return redirect('crudUsuarios')  # Redirige a la lista de usuarios
    return redirect('crudUsuarios')


def editarusuario(request, id_usuario):
    usuario_obj = usuario.objects.get(IdUsuario=id_usuario)
    if request.method == "POST":
        usuario_obj.PrimerNombre = request.POST.get('PrimerNombre')
        usuario_obj.OtrosNombres = request.POST.get('OtrosNombres')
        usuario_obj.PrimerApellido = request.POST.get('PrimerApellido')
        usuario_obj.SegundoApellido = request.POST.get('SegundoApellido')
        usuario_obj.Correo = request.POST.get('Correo')
        usuario_obj.NombreUsuario = request.POST.get('NombreUsuario')
        if request.POST.get('Contraseña'):
            usuario_obj.Contraseña = make_password(request.POST.get('Contraseña'))
        usuario_obj.save()
        return redirect('crudUsuarios')
    return render(request, 'crud/editar_usuario.html', {'usuario': usuario_obj})


def borrarusuario(request, id_usuario):
    usuario_obj = usuario.objects.get(IdUsuario=id_usuario)
    usuario_obj.delete()
    return redirect('crudUsuarios')
      
#endregion


#region domiciliario
def insertardomiciliario(request):
    if request.method == "POST":
        try:
            # Asignar automáticamente el rol de domiciliario
            rol_domiciliario = roles.objects.get(IdRol=2)

            # Crear el domiciliario con los datos del formulario
            nuevo_domiciliario = domiciliario(
                TipoDocumento=request.POST.get('TipoDocumento'),
                Documento=request.POST.get('Documento'),
                NombreDomiciliario=request.POST.get('NombreDomiciliario'),
                PrimerApellido=request.POST.get('PrimerApellido'),
                SegundoApellido=request.POST.get('SegundoApellido'),
                Celular=request.POST.get('Celular'),
                Ciudad=request.POST.get('Ciudad'),  # Captura la ciudad
                Correo=request.POST.get('Correo'),
                Contraseña=make_password(request.POST.get('Contraseña')),
                IdRol=rol_domiciliario  # Asignar el rol de domiciliario
            )

            nuevo_domiciliario.save()

            return redirect('crudDomiciliarios')
        except roles.DoesNotExist:
            return render(request, 'crud/insertar_domiciliario.html', {'error': 'El rol especificado no existe en el sistema.'})
    
    return render(request, 'crud/insertar_domiciliario.html')

def editardomiciliario(request, id_domiciliario):
    domiciliario_obj = get_object_or_404(domiciliario, IdDomiciliario=id_domiciliario)
    
    if request.method == "POST":
        domiciliario_obj.TipoDocumento = request.POST.get('TipoDocumento')
        domiciliario_obj.Documento = request.POST.get('Documento')
        domiciliario_obj.NombreDomiciliario = request.POST.get('NombreDomiciliario')
        domiciliario_obj.PrimerApellido = request.POST.get('PrimerApellido')
        domiciliario_obj.SegundoApellido = request.POST.get('SegundoApellido')
        domiciliario_obj.Celular = request.POST.get('Celular')
        domiciliario_obj.Ciudad = request.POST.get('Ciudad')
        domiciliario_obj.Correo = request.POST.get('Correo')
        if request.POST.get('Contraseña'):
            domiciliario_obj.Contraseña = make_password(request.POST.get('Contraseña'))
        domiciliario_obj.save()
        return redirect('crudDomiciliarios')
    
    return render(request, 'crud/editar_domiciliario.html', {'domiciliario': domiciliario_obj})

def borrardomiciliario(request, id_domiciliario):
    domiciliario_obj = domiciliario.objects.get(IdDomiciliario=id_domiciliario)
    domiciliario_obj.delete()
    return redirect('crudDomiciliarios')
#endregion


#region productos
def validar_nombre_producto(nombre):
    if not nombre or not nombre.strip():
        return "El nombre es obligatorio."
    if re.search(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]', nombre):
        return "Nombre inválido: no se permiten caracteres especiales."
    return None

def insertarproducto(request):
    if request.method == "POST":
        nombre = request.POST.get('Nombre', '').strip()
        descripcion = request.POST.get('Descripcion', '').strip()
        precio = request.POST.get('Precio')
        cantidad = request.POST.get('Cantidad')
        fecha_vence = request.POST.get('FechaVence')
        id_subcategoria = request.POST.get('IdSubCategoria')
        img = request.FILES.get('Img')

        # Validaciones
        error = validar_nombre_producto(nombre)
        if error:
            messages.error(request, error)
            return redirect('crudProductos')
        if not id_subcategoria:
            messages.error(request, "La subcategoría es obligatoria.")
            return redirect('crudProductos')
        # Duplicado: mismo nombre y subcategoría
        if producto.objects.filter(Nombre__iexact=nombre, IdSubCategoria_id=id_subcategoria).exists():
            messages.error(request, "Ya existe un producto con ese nombre en la misma subcategoría.")
            return redirect('crudProductos')

        # Crear producto
        nuevo_producto = producto(
            Nombre=nombre,
            Descripcion=descripcion,
            Precio=precio,
            Cantidad=cantidad,
            FechaVence=fecha_vence,
            IdSubCategoria=subcategoria.objects.get(IdSubCategoria=id_subcategoria),
            Img=img
        )
        nuevo_producto.save()
        messages.success(request, "Producto registrado exitosamente")
        return redirect('crudProductos')
    return render(request, 'crud/productos.html')

def editarproducto(request, id_producto):
    producto_obj = get_object_or_404(producto, IdProducto=id_producto)
    if request.method == "POST":
        nombre = request.POST.get('Nombre', '').strip()
        descripcion = request.POST.get('Descripcion', '').strip()
        precio = request.POST.get('Precio')
        cantidad = request.POST.get('Cantidad')
        fecha_vence = request.POST.get('FechaVence')
        id_subcategoria = request.POST.get('IdSubCategoria')
        img = request.FILES.get('Img')

        # Validaciones
        error = validar_nombre_producto(nombre)
        if error:
            messages.error(request, error)
            return redirect('crudProductos')
        if not id_subcategoria:
            messages.error(request, "La subcategoría es obligatoria.")
            return redirect('crudProductos')
        # Duplicado: mismo nombre y subcategoría, excluyendo el actual
        if producto.objects.filter(
            Nombre__iexact=nombre,
            IdSubCategoria_id=id_subcategoria
        ).exclude(IdProducto=id_producto).exists():
            messages.error(request, "Ya existe un producto con ese nombre en la misma subcategoría.")
            return redirect('crudProductos')

        # Actualizar producto
        producto_obj.Nombre = nombre
        producto_obj.Descripcion = descripcion
        producto_obj.Precio = precio
        producto_obj.Cantidad = cantidad
        producto_obj.FechaVence = fecha_vence
        producto_obj.IdSubCategoria = subcategoria.objects.get(IdSubCategoria=id_subcategoria)
        if img:
            producto_obj.Img = img
        producto_obj.save()
        messages.success(request, "Producto modificado exitosamente")
        return redirect('crudProductos')
    return render(request, 'crud/editar_producto.html', {'producto': producto_obj})
def borrarproducto(request, id_producto):
    producto_obj = get_object_or_404(producto, IdProducto=id_producto)
    producto_obj.delete()
    return redirect('crudProductos') # importa producto con minúscula si así está definido


@csrf_exempt
def guardar_calificacion(request):
    try:
        print("POST recibido:", request.POST)

        id_producto = request.POST.get('id_producto')
        calificacion = request.POST.get('calificacion')

        if not id_producto or not calificacion:
            raise ValueError("Faltan datos")
        producto_obj = producto.objects.filter(IdProducto=id_producto).first()
        if not producto_obj:
            raise ValueError("Producto no encontrado")
        # Guardar la calificación
        Calificacion.objects.create(
            IdProducto=producto_obj,
            Calificacion=int(calificacion)
        )
        promedio = Calificacion.objects.filter(
            IdProducto=producto_obj
        ).aggregate(Avg('Calificacion'))['Calificacion__avg']
        total_reviews = Calificacion.objects.filter(
            IdProducto=producto_obj
        ).count()
        return JsonResponse({
            'success': True,
            'mensaje': 'Gracias por tu calificación',
            'nuevo_promedio': round(promedio, 1),
            'total_reviews': total_reviews
        })
    except Exception as e:
            print(f"Error interno: {str(e)}")
            return JsonResponse({'success': False, 'mensaje': str(e)})

    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})

    

# region perfiles
def perfiles(request):
    if not request.session.get('user_id'):
        return redirect('login')
    
    try:
        user = usuario.objects.get(IdUsuario=request.session['user_id'])
        
        if request.method == 'POST':
            # Verificar si es una actualización de datos o solo de imagen
            if 'profile-pic' in request.FILES:
                # Solo actualizar imagen
                user.imagen_perfil = request.FILES['profile-pic']
                user.save()
                return JsonResponse({
                    'status': 'success',
                    'new_image_url': user.imagen_perfil.url if user.imagen_perfil else '/static/img/perfil.png'
                })
            else:
                # Actualizar datos del perfil
                user.PrimerNombre = request.POST.get('primerNombre', user.PrimerNombre)
                user.OtrosNombres = request.POST.get('segundoNombre', user.OtrosNombres)
                user.PrimerApellido = request.POST.get('primerApellido', user.PrimerApellido)
                user.SegundoApellido = request.POST.get('segundoApellido', user.SegundoApellido)
                user.NombreUsuario = request.POST.get('nombreUsuario', user.NombreUsuario)
                
                if request.POST.get('contrasena'):
                    user.Contraseña = make_password(request.POST.get('contrasena'))
                
                user.save()
                request.session['nombre'] = f"{user.PrimerNombre} {user.PrimerApellido}"
                return redirect('perfiles')
        
        return render(request, 'perfiles.html', {
        'usuario': user,
        'imagen_perfil': user.imagen_perfil.url if user.imagen_perfil else '/static/img/perfil.png'
    })
        
    except usuario.DoesNotExist:
        return redirect('login')

def eliminar_foto_perfil(request):
    if request.method == 'POST' and request.session.get('user_id'):
        try:
            user = usuario.objects.get(IdUsuario=request.session['user_id'])
            if user.imagen_perfil:
                user.imagen_perfil.delete()
                user.imagen_perfil = None
                user.save()
            return JsonResponse({
                'status': 'success',
                'new_image_url': '/static/img/perfil.png'
            })
        except usuario.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=400)

def eliminar_cuenta(request):
    if request.method == 'POST' and request.session.get('user_id'):
        try:
            user = usuario.objects.get(IdUsuario=request.session['user_id'])
            user.delete()  # Delete the user account
            request.session.flush()  # Clear the session
            return redirect('Ladingpage')  # Redirect to the landing page
        except usuario.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=400)
# endregion

def crudCategorias(request):
    return render(request, 'crud/categorias.html')

def crudSubCategorias(request):
    subcategorias = subcategoria.objects.all()
    categorias = categoria.objects.all()
    return render(request, 'crud/subcategorias.html', {'subcategorias': subcategorias, 'categorias': categorias})

def crudProductos(request):
    productos = producto.objects.all()  # Obtener todos los productos
    subcategorias = subcategoria.objects.all()  # Obtener todas las subcategorías
    return render(request, 'crud/productos.html', {'productos': productos, 'subcategorias': subcategorias})

def crudDomiciliarios(request):
    domiciliarios = domiciliario.objects.filter(IdRol=2)  
    return render(request, 'crud/domiciliarios.html', {'domiciliarios': domiciliarios})


def crudUsuarios(request):
    usuarios = usuario.objects.filter(idRol=3)  
    return render(request, 'crud/usuarios.html', {'usuarios': usuarios})


def recuperarContraseña(request):
    return render(request, 'login/recuperarcontraseña.html')

def pedido(request):
    return render(request, 'pedido.html')

def codigo(request):
    return render(request, 'login/codigo.html')

def nuevaContraseña(request):
    return render(request, 'login/nuevaContraseña.html')



def carrito(request):
    return render(request, 'carrito/carrito.html')

def lencerias(request):
    # Obtener la categoría de lencería
    categoria_lenceria = categoria.objects.get(NombreCategoria='Lencería')
    
    # Filtrar productos que pertenecen a la categoría de lencería o a sus subcategorías
    productos = producto.objects.filter(IdSubCategoria__categoria=categoria_lenceria)
    
    return render(request, 'carrito/lencerias.html', {'productos': productos})

def vibradores(request):
    # Obtener la categoría de vibradores
    categoria_vibrador = categoria.objects.get(NombreCategoria='vibradores')  # Cambiado a get
    
    # Filtrar productos que pertenecen a la categoría de vibradores o a sus subcategorías
    productos = producto.objects.filter(IdSubCategoria__categoria=categoria_vibrador)
    
    return render(request, 'carrito/vibradores.html', {'productos': productos})

def disfraces(request):
    # Obtener la categoría de disfraces
    categoria_disfraces = categoria.objects.get(NombreCategoria='Lencería')  # Cambiado a 'Lencería'
    
    # Filtrar productos que pertenecen a la categoría de lencería o a sus subcategorías
    productos = producto.objects.filter(IdSubCategoria__categoria=categoria_disfraces)
    
    return render(request, 'carrito/disfraces.html', {'productos': productos})

def dildos(request):
    # Obtener la categoría de dildos
    categoria_dildo = categoria.objects.get(NombreCategoria='Dildos')  # Cambiado a get
    
    # Filtrar productos que pertenecen a la categoría de dildos o a sus subcategorías
    productos = producto.objects.filter(IdSubCategoria__categoria=categoria_dildo)
    
    return render(request, 'carrito/dildos.html', {'productos': productos})

def productosCarrito(request):
    productos = producto.objects.all().order_by('-IdProducto')  # Obtener todos los productos
    return render(request, 'carrito/productos.html', {'productos': productos})
