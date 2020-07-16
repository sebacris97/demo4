"""bookflix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from bookflixapp import views
from django.conf.urls import url, include
from django.conf import settings

from django.conf.urls.static import static

from django.contrib.auth.views import LogoutView


urlpatterns = [

                path('admin/', admin.site.urls, name='admin'),
                path('', views.index, name='index'),

                url(r'^post-search/$', views.post_search, name='post-search'),

                path('perfil/', views.verperfil, name='verperfil'),
                path('selecPerfil/', views.selecperfil, name='seleccionarPerfil'),
                path('crearPerfil/', views.createprofile, name='crearPerfil'),
                path('eliminarPerfil/', views.borrarperfil, name='eliminarPerfil'),
                path('verLibros/', views.ver_libros, name='verLibros'),
                path('verLibros/<str:choice>', views.ver_libros, name='verLibros'),
                path('verCapitulos/<int:pk>', views.ver_capitulos, name='verCapitulos'),
                path('verDatos/', views.verusuario, name='verDatos'),
                path('modificarDatos/', views.modificardatos, name='modificarDatos'),
                path('eliminarDatos/', views.borrarusuario, name='eliminarDatos'),
                  # <int:pk> significa que ver capitulos recibe de parametro la en pk
                  # la clave primaria del libro desde el template que se lo llama (desde verLibros)

                path('action/<int:pk_libro>/<int:pk_capitulo>', views.action, name='action'), 
                path('register/', views.register, name='register'),
                path('login/', views.login, name='login'),
                
                url(r'^logout/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),


                path('pagarSuscripcion/', views.pagarsuscripcion, name='pagarSuscripcion'),
                path('premium/', views.pasarpremium, name='pasarPremium'),
                path('normal/', views.pasarnormal, name='pasarNormal'),
                path('modificarPerfil/', views.modificarperfil, name='modificarPerfil'),



              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
