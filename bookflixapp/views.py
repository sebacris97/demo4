from django.shortcuts import render, redirect, get_object_or_404
from bookflixapp.models import Trailer, Libro, Novedad, Capitulo, Perfil, Usuario, Comentario
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User
from django.contrib.auth import hashers, authenticate
from django.contrib.auth import login as do_login
from .forms import RegistrationForm, CreateProfileForm, ComentarioForm, EditProfileForm, ProfileForm
from .forms import CustomAuthenticationForm as AuthenticationForm
from .filters import LibroFilter

from django.contrib.auth.decorators import login_required
from django.db.models import F


from django.contrib import messages

from django.utils.datastructures import MultiValueDictKeyError

# Create your views here.


def perfil_actual(request):
    usuario=Usuario.objects.filter(user__email=str(request.user))  #me quedo con el usuario logueado
    perfil=Perfil.objects.filter(usuario__user__email=str(usuario[0]), selected=True) #me quedo con el perfil seleccionado
    return perfil[0]


def agregar_favoritos(id_libro,perfil):
    libro = Libro.objects.filter(id=id_libro)
    perfil.favoritos.add(*libro)

def eliminar_favoritos(id_libro,perfil):
    libro = Libro.objects.filter(id=id_libro)
    perfil.favoritos.remove(*libro)

        
@login_required
def ver_libros(request,choice=''):
    perfil = perfil_actual(request)
    favoritos = list(perfil.favoritos.values_list('id', flat=True))
    if request.method == 'POST':
        id_libro = int(  list(request.POST.keys())[1]  )
        #request.POST es un diccionario (dict_object) que en [0] tiene el csrf_token
        #y en 1 el string del ID del libro que clickie (por eso hago el casteo a int)
        if id_libro not in favoritos:
            agregar_favoritos(id_libro,perfil)
        else:
            eliminar_favoritos(id_libro,perfil)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        #para redirigir a la misma url donde estaba
    
    #favoritos, historial y ver libros son lo mismo, solo cambia el
    #queryset que se muestra (por eso directamente resumi todo en un
    #parametro que determina el queryset elegido)

    if choice == 'favoritos':
        qs = perfil.favoritos
    elif choice == 'historial':
        qs = perfil.historial
    else:
        qs = Libro.objects.all()

    filtro = LibroFilter(request.GET, queryset=qs)

    return render(request, "ver_libros.html", {"filter": filtro,
                                               "favoritos": favoritos})


def action(request, pk_libro, pk_capitulo):
    libro = Libro.objects.filter(id=pk_libro)
    libro.update(contador=F('contador') + 1)
    capitulo = Capitulo.objects.get(id=pk_capitulo)
    perfil = perfil_actual(request)
    perfil.historial.add(*libro) #lo agrgo a la lista de libros leidos
    return redirect(capitulo.pdf.url)


def do_comment(request,form, libro):
    if form.is_valid():
        texto = form.cleaned_data["texto"]
        Comentario.objects.create(perfil=perfil_actual(request), texto=texto, libro=libro)
        messages.success(request, 'Comentario enviado')
    
        
def delete_comment(request):
    id_comentario = (int(request.POST.get('eliminar'))) #id del comentario
    comentario = get_object_or_404(Comentario, pk=id_comentario)
    if (perfil_actual(request).id == comentario.perfil.id) or request.user.is_superuser:
        comentario.delete()
        messages.success(request, 'Comentario eliminado')


def edit_comment(request,form):
    id_comentario = (int(request.POST.get('modificar'))) #id del comentario
    comentario = get_object_or_404(Comentario, pk=id_comentario)
    form = ComentarioForm(request.POST,instance=comentario)
    if form.is_valid():
        texto = form.cleaned_data["texto"]
        if (perfil_actual(request).id == comentario.perfil.id) or request.user.is_superuser:
            comentario.texto = texto
            comentario.save(update_fields=['texto'])
            messages.success(request, 'Comentario modificado')
                

@login_required
def ver_capitulos(request, pk):
    capitulos = Capitulo.objects.filter(libro__id=pk)
    if len(capitulos) > 0:  # parche temporal para los libros que no tienen capitulos
        libro = capitulos[0].libro
        comentarios = Comentario.objects.filter(libro__id=pk)
        comentario_form = ComentarioForm(request.POST or None)
        if request.method == 'POST':
            if request.POST.get('enviar'):
                do_comment(request,comentario_form,libro)
            if request.POST.get('eliminar'):
                delete_comment(request)
            if request.POST.get('modificar'):
                edit_comment(request,comentario_form)
            return HttpResponseRedirect(request.path_info)


        # el parametro lo recibe de urls. lo que hago es filtrar los capitulos
        # que pertenecen al libro que recibo como parametro
        # (si hiciese objects.all() me estoy quedando con todos los capitulos de todos los libros)

        return render(request, "ver_capitulos.html", {"capitulos": capitulos,
                                "libro": libro, "comentarios": comentarios,
                                "comentario_form": comentario_form,
                                "perfil_actual": perfil_actual(request)})
    else:
        return redirect('/')  # si no se le subio capitulo te manda a index


@login_required
def post_search(request):
    return redirect('/verLibros/?titulo__icontains=' + request.POST['search'])


def index(request):
    d = timezone.now() - timedelta(days=7)
    trailers = Trailer.objects.filter(creacion__gte=d)
    novedades = Novedad.objects.filter(creacion__gte=d)
    if request.user.is_authenticated:
        if request.user.is_superuser:
            nombre_perfil = 'admin'
        else:
            perfil = perfil_actual(request)
            nombre_perfil = str(perfil)
        return render(request, "index.html", {"trailers":trailers,"novedades": novedades,"nombre_perfil":nombre_perfil})
    return render(request, "index.html", {"trailers":trailers,"novedades": novedades})

def register(request):
    # Creamos el formulario de autenticación vacío
    form = RegistrationForm(data=request.POST or None)
    if request.method == "POST":

        # Si el formulario es válido...
        if form.is_valid():

            # Creamos la nueva cuenta de usuario
            username = form.cleaned_data["email"]
            realpassword = hashers.make_password(password=form.cleaned_data["password1"])
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            fecha = form.cleaned_data["fecha_de_nacimiento"]
            membresia = request.POST['membresia']
            mem = membresia.split()
            m = mem[0]
            u = User(username=username, first_name=first_name, last_name=last_name, password=realpassword,
                     email=username)
            u.save()
            if m == 'Premium':
                user = Usuario(user=u, fecha_de_nacimiento=fecha)
                user.save()
                p = Perfil(usuario=user, username=u.first_name)
                p.save()
                do_login(request, u)
                return HttpResponseRedirect('/premium')
            else:
                user = Usuario(user=u, fecha_de_nacimiento=fecha)
            # Si el usuario se crea correctamente
            if user is not None:
                # Hacemos el login manualmente
                user.save()
                p = Perfil(usuario=user, username=u.first_name)
                p.save()
                do_login(request, u)
                # Y le redireccionamos a la portada
                return redirect('/')
    # Si llegamos al final renderizamos el formulario
    return render(request, "registration/register.html", {'form': form})

@login_required
def pasarpremium(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    if request.method == "POST":
        tarjeta = request.POST['tarjeta']
        ut = usuario.tarjeta
        if ut == "":
            usuario.tarjeta = tarjeta
            usuario.cantPerfiles = 4
            usuario.is_premium = True
            usuario.save()
            return render(request, 'pasar_premium.html', {'cant': 2})
        else:
            if tarjeta == usuario.tarjeta:
                usuario.cantPerfiles = 4
                usuario.is_premium = True
                usuario.save()
                return render(request, 'pasar_premium.html', {'cant': 2})
            else:
                return render(request, 'pasar_premium.html', {'cant': 0})
    return render(request, "pasar_premium.html", {'cant': 1})


@login_required
def pasarnormal(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    perfiles = Perfil.objects.filter(usuario=usuario)
    if request.method == "POST":
        if perfiles.count() <= 2:
            usuario.cantPerfiles = 2
            usuario.is_premium = False
            usuario.save()
            return render(request, 'pasar_normal.html', {'cant': 1})
        else:
            p_seleccionado_id = int(request.POST['nombre'])
            p_seleccionado = Perfil.objects.get(id=p_seleccionado_id)
            p = Perfil.objects.filter(usuario=usuario)
            sel = p_seleccionado.selected
            for per in p:
                if per != p_seleccionado:
                    if sel:
                        per.selected = True
                        per.save()
                    p_seleccionado.delete()
                    break
            perfiles = Perfil.objects.filter(usuario=usuario)
            if perfiles.count() > 2:
                return render(request, 'borrar_perfil.html', {'perfiles': perfiles, 'cant': 10})
            else:
                return render(request, "pasar_normal.html", {'cant': 1})
    if perfiles.count() > 2:
        return render(request,'borrar_perfil.html', {'perfiles': perfiles, 'cant': 10})
    else:
        usuario.cantPerfiles = 2
        usuario.is_premium = False
        usuario.save()
        return render(request, "pasar_normal.html", {'cant': 1})


@login_required
def pagarsuscripcion(request):
    user = request.user
    if request.method == "POST":
        tarjeta = request.POST["tarjeta"]
        usuario = Usuario.objects.get(user=user)
        ut = usuario.tarjeta
        if ut == "":
            usuario.tarjeta = tarjeta
            if usuario.is_premium:
                usuario.cantPerfiles = 4
            usuario.save()
            return render(request, 'pagar_suscripcion.html', {'cant': 2})
        else:
            if tarjeta == usuario.tarjeta:
                return render(request, 'pagar_suscripcion.html', {'cant': 2})
            else:
                return render(request, 'pagar_suscripcion.html', {'cant': 0})
    return render(request, "pagar_suscripcion.html", {'cant': 1})


def login(request):
    # Creamos el formulario de autenticación
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)
            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)

                # Si el usuario es administrador
                if request.user.is_superuser:
                    # Lo redireccionamos a la pagina del admin
                    return HttpResponseRedirect('/admin')
                else:
                    # Y sino le redireccionamos a la portada
                    return HttpResponseRedirect('/')
      
    # Si llegamos al final renderizamos el formulario
    return render(request, "registration/login.html", {'form': form})



@login_required
def createprofile(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    pp = Perfil.objects.filter(usuario=usuario)
    c = pp.count()
    if request.method == "POST":
        form = CreateProfileForm(user=user, data=request.POST)
        if form.is_valid():
            profilename = form.cleaned_data["profilename"]
            p = Perfil.objects.filter(usuario=usuario, selected=True)
            per = p[0]
            per.selected = False
            per.save()
            profile = Perfil(usuario=usuario, username=profilename)
            profile.save()
            if profile is not None:
                return HttpResponseRedirect("/")
        else:
            return render(request, "crear_perfil.html", {'form': None})
    else:
        form = CreateProfileForm(user)
        return render(request, "crear_perfil.html", {'form': form, 'cant1': usuario.cantPerfiles, 'cant2': c})


@login_required
def verperfil(request):
    perfil = perfil_actual(request)
    return render(request, 'perfil.html', {"perfil": perfil})


@login_required
def selecperfil(request):
    
    #me quedo con el usuario logueado
    usuario = Usuario.objects.get(user=request.user)
    #me quedo con los perfiles del usuario logueado
    perfiles = Perfil.objects.filter(usuario=usuario)
    
    #me quedo con el perfil actual
    p_actual = perfil_actual(request)

    #si se prsiona seleccionar
    if request.method == "POST":

        #me quedo con el id del usuario que seleccione
        p_seleccionado_id = int(request.POST['nombre'])
        #me quedo con el objeto del usuario que seleccione
        p_seleccionado = Perfil.objects.get(id=p_seleccionado_id)

        #si el perfil que seleccione no es el que actualmente esta seleccinado
        if p_seleccionado.selected == False:

            #"deselecciono" el perfil actual
            p_actual.selected = False
            #y actualizo la base de datos
            p_actual.save(update_fields=['selected'])
            #ahora marco el que seleccione como seleccionado
            p_seleccionado.selected = True
            #y acutalizo la base de datos
            p_seleccionado.save(update_fields=['selected'])

        #redireccionamos a verperfil
        return HttpResponseRedirect('/perfil')

    #renderizo el template con los perfiles del usuario logueado
    return render(request, 'selec_perfil.html', {"perfiles": perfiles,"p_actual":p_actual})


@login_required
def verusuario(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
    else:
        user = request.user
        usuario = Usuario.objects.get(user=user)
        return render(request, 'ver_usuario.html', {'user': user, 'usuario': usuario})






@login_required
def modificarperfil(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    perfil = perfil_actual(request)
    cant = 1
    if request.method == 'POST':
        nuevo_per = request.POST['nuevo']
        per = Perfil.objects.filter(usuario=usuario)
        for p in per:
            if p.username == nuevo_per:
                cant = -1
                return render(request, 'modificar_perfil.html', {'perfil': perfil, 'cant': cant })
        perfil.username = nuevo_per
        perfil.save()
        return HttpResponseRedirect('/perfil')
    return render(request, 'modificar_perfil.html', {'perfil': perfil, 'cant': cant })


def borrarperfil(request):
    usuario = Usuario.objects.get(user=request.user)
    perfiles = Perfil.objects.filter(usuario=usuario)
    cant = perfiles.count()
    if request.method == "POST":
        p_seleccionado_id =  int(request.POST['nombre'])
        p_seleccionado = Perfil.objects.get(id=p_seleccionado_id)
        p = Perfil.objects.filter(usuario=usuario)
        sel = p_seleccionado.selected
        for per in p:
            if per != p_seleccionado:
                if sel:
                    per.selected = True
                    per.save()
                p_seleccionado.delete()
                break
        return render(request, 'borrar_perfil.html', {"cant": 0})
    return render(request, 'borrar_perfil.html', {"perfiles": perfiles, "cant": cant})

"""
@login_required
def borrarperfil(request):
    
    usuario = Usuario.objects.get(user=request.user)
    perfiles = Perfil.objects.filter(usuario=usuario)
    cant = perfiles.count()
    
    if request.method == "POST":
        p_seleccionado_id = int(request.POST['nombre'])
        p_seleccionado = Perfil.objects.get(id=p_seleccionado_id)
        
        if p_seleccionado_id != perfil_actual(request).id:
            p_seleccionado.delete()
            return HttpResponseRedirect('/')

        else:
            messages.error(request, 'No se puede eliminar el perfil que esta seleccionado')
            return HttpResponseRedirect('/eliminarPerfil')
        
    return render(request, 'borrar_perfil.html', {"perfiles": perfiles, "cant": cant})
"""



@login_required
def modificardatos(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)

    if request.method == 'POST':
        print("hola")
        form = EditProfileForm(request.POST, instance=user, user=user)
        profile_form = ProfileForm(request.POST, instance=usuario)

        if form.is_valid() and profile_form.is_valid():
            email         = form.cleaned_data['email']
            first_name    = form.cleaned_data['first_name']
            last_name     = form.cleaned_data['last_name']
            f_nacimiento  = profile_form.cleaned_data['fecha_de_nacimiento']
            tarjeta       = profile_form.cleaned_data['tarjeta']

            usuario.fecha_de_nacimiento = f_nacimiento
            usuario.tarjeta             = tarjeta
            user.first_name             = first_name
            user.last_name              = last_name
            user.email                  = email
            user.username               = email
            user.save()
            usuario.save()
            #user_form = form.save()
            #custom_form = profile_form.save(False)
            #custom_form.user = user_form
            #custom_form.save()
            
            return redirect('/verDatos')
    else:
        form = EditProfileForm(instance=request.user, user=user)
        profile_form = ProfileForm(instance=usuario)

    return render(request, 'modf_usuario.html', {'form': form, 'p_form': profile_form, 'user': user, 'usuario': usuario})

@login_required
def borrarusuario(request):
    user = request.user
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username == request.user.email:
                usr = authenticate(username=username, password=password)
                if usr is not None:
                    usuario = Usuario.objects.get(user=usr)
                    Perfil.objects.filter(usuario=usuario).delete()
                    usuario.delete()
                    usr.delete()
                    return HttpResponseRedirect("/")
            else:
                messages.error(request, "Por favor, introduzca un nombre de usuario y clave correctos."
                                        " Observe que ambos campos pueden ser sensibles a mayúsculas.")
            
    return render(request, 'borrar_usuario.html', {'form': form, 'user': user})



