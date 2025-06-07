"""
URL configuration for sexshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include 
from appsexshop.views import (
    LadingPage, listadocategorias, insertarcategorias, borrarcategoria, actualizarcategoria, 
    perfiles, crudCategorias, crudSubCategorias, crudProductos, crudDomiciliarios, crudUsuarios, 
    login, registro, solicitar_recuperacion, pedido, verificar_codigo, 	nueva_contrasena,
    insertarsubcategoria, listadosubcategorias, borrarsubcategoria, actualizarsubcategoria,editarusuario,
    borrarusuario, insertarusuario, carrito, lencerias, productosCarrito, insertardomiciliario, editardomiciliario, borrardomiciliario,
    insertarproducto, editarproducto, borrarproducto, vibradores, disfraces, dildos, logout, eliminar_foto_perfil, eliminar_cuenta, guardar_calificacion, devoluciones
)

urlpatterns = [
    path('', LadingPage, name='Ladingpage'),
    path('perfiles/', perfiles, name='perfiles'),
    path('eliminar-foto-perfil/', eliminar_foto_perfil, name='eliminar_foto_perfil'),
    path('listadocategorias/', listadocategorias, name='listadocategorias'),
    path('insertarcategorias/', insertarcategorias, name='insertarcategorias'),
    path('categorias/borrar/<int:id_categoria>/', borrarcategoria, name='borrarcategoria'),
    path('categorias/actualizar/<int:id_categoria>/', actualizarcategoria, name='actualizarcategoria'),
    path('crud/categorias', crudCategorias,  name='crudCategorias'),
    path('crud/subcategorias', crudSubCategorias, name='crudSubCategorias'),
    path('subcategorias/insertar/', insertarsubcategoria, name='insertarsubcategoria'),
    path('subcategorias/listado/', listadosubcategorias, name='listadosubcategorias'),
    path('subcategorias/borrar/<int:id_subcategoria>/', borrarsubcategoria, name='borrarsubcategoria'),
    path('subcategorias/actualizar/<int:id_subcategoria>/', actualizarsubcategoria, name='actualizarsubcategoria'),
    path('crud/productos', crudProductos, name='crudProductos'),
    path('crud/productos/insertar/', insertarproducto, name='insertarproducto'),
    path('crud/productos/editar/<int:id_producto>/', editarproducto, name='editarproducto'),
    path('crud/productos/eliminar/<int:id_producto>/', borrarproducto, name='borrarproducto'),
    path('crud/domiciliarios', crudDomiciliarios, name='crudDomiciliarios'),
    path('crud/domiciliarios/insertar/', insertardomiciliario, name='insertardomiciliario'),
    path('crud/domiciliarios/editar/<int:id_domiciliario>/', editardomiciliario, name='editardomiciliario'),
    path('crud/domiciliarios/eliminar/<int:id_domiciliario>/', borrardomiciliario, name='borrardomiciliario'),
    path('crud/usuarios', crudUsuarios, name='crudUsuarios'),
    path('crud/usuarios/insertar/', insertarusuario, name='insertarusuario'),
    path('crud/usuarios/editar/<int:id_usuario>/', editarusuario, name='actualizarusuario'),
    path('crud/usuarios/eliminar/<int:id_usuario>/', borrarusuario, name='borrarusuario'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('registro/', registro, name='registro'),
    path('recuperarContraseña', solicitar_recuperacion, name='solicitar_recuperacion'),
    path('codigo', verificar_codigo, name='verificar_codigo'),
    path('nuevaContraseña',nueva_contrasena, name='nueva_contrasena'),
    path('pedido', pedido, name='pedido'),
    path('devoluciones', devoluciones, name='devoluciones'),
    path('carrito', carrito, name='carrito'),
    path('lencerias', lencerias, name='lencerias'),
    path('vibradores', vibradores, name='vibradores'),
    path('disfraces', disfraces, name='disfraces'),
    path('dildos', dildos, name='dildos'),
    path('productos', productosCarrito, name='productosCarrito'),
    path('eliminar-cuenta/', eliminar_cuenta, name='eliminar_cuenta'),
    path('guardar-calificacion/', guardar_calificacion, name='guardar_calificacion'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
