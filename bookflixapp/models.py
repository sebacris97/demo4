from django.db import models
from django.db.models import Sum
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator, MinLengthValidator
from django.contrib.auth.models import User

# los validator te ahorran tener que hardcodear algunas validaciones que django ya provee


class Autor(models.Model):
    nombre   =  models.CharField(max_length=50)
    apellido =  models.CharField(max_length=50, default='')

    def __str__(self):
        return '%s %s' % (self.nombre, self.apellido)

    class Meta:
        verbose_name_plural  =  "Autores"
        ordering             =  ["apellido", "nombre"]


class Genero(models.Model):
    nombre  =  models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural =  "Generos"
        ordering            =  ["nombre"]


class Editorial(models.Model):
    nombre  =  models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Editoriales"
        ordering = ["nombre"]


class Capitulo(models.Model):
    libro      =  models.ForeignKey('Libro', on_delete=models.CASCADE)  # libro al cual pertenece el capitulo
    numero     =  models.PositiveIntegerField(default=None, validators=[MinValueValidator(1)], verbose_name='Numero del capitulo', null=True, blank=True)
    nropaginas =  models.PositiveIntegerField(default=None, validators=[MinValueValidator(1)], verbose_name="Numero de paginas", null=True, blank=True)
    ultimo     =  models.BooleanField(default=False, blank=True, verbose_name="Ultimo Capitulo")
    
    def __str__(self):
        return str(self.libro) + ' - Capitulo: ' + str(self.numero)

    class Meta:
        verbose_name_plural  =  "Capitulos"
        ordering             =  ["numero"]
        unique_together      =  [['libro','ultimo',],['libro', 'numero',]]
        # no existen 2 capitulos 1 para el mismo libro
        # no existen 2 capitulos ultimo para el mismo libro

    def content_file_name(instance, filename):
        nombre  =  str(instance.numero) + '- ' + filename
        return '/'.join(['libros', instance.libro.titulo, nombre])

    pdf        =  models.FileField(null=True, blank=True, upload_to=content_file_name, validators=[FileExtensionValidator(['pdf'], 'Solo se permiten archivos pdf')])


class Calificacion(models.Model):
    nota    =  models.PositiveIntegerField(default=0, editable=False, validators=[MinValueValidator(0)], verbose_name="Calificacion")
    perfil  =  models.ForeignKey('Perfil', editable=False, on_delete=models.CASCADE)
    libro   =  models.ForeignKey('Libro' , editable=False, on_delete=models.CASCADE)

    def __str__(self):
        return "nota: " + str(self.nota) + '\nperfil: ' + str(self.perfil) + '\nlibro: ' + str(self.libro)

    class Meta:
        verbose_name_plural  =  'Calificaciones'
        unique_together      =  ['libro', 'perfil',]


class Libro(models.Model):
    titulo        =  models.CharField(max_length=200)
    nropaginas    =  models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)], verbose_name="Numero de paginas")
    nrocapitulos  =  models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)], verbose_name="Numero de capitulos")
    isbn          =  models.CharField(max_length=13, unique=True, validators=[RegexValidator('^(\d{10}|\d{13})$', 'El numero debe tener 10 o 13 digitos numericos')], verbose_name="ISBN")
    autor         =  models.ForeignKey(Autor, on_delete=models.CASCADE)
    editorial     =  models.ForeignKey(Editorial, on_delete=models.CASCADE)
    genero        =  models.ManyToManyField(Genero)
    agnoedicion   =  models.DateField(verbose_name="Año de edicion")
    contador      =  models.PositiveIntegerField(default=0, editable=False, verbose_name='Veces leido')
    subido        =  models.DateTimeField(auto_now_add=True, verbose_name="Fecha de carga")
    texto         =  models.TextField(max_length=1000, default='NONE', verbose_name="Texto")

    def content_file_name(instance, filename):
        nombre  =  instance.titulo + '- ' + filename
        return '/'.join(['libros', instance.titulo, nombre])

    imagen        =  models.ImageField(null=True, upload_to=content_file_name, default='default.jpg', verbose_name="Imagen")

    def get_imagen(self):
        return self.imagen.url

    @property
    def get_calificaciones(self):
        return Calificacion.objects.filter(libro__id=self.id)
    
    @property
    def get_votos(self):
        return len(self.get_calificaciones)

    @property
    def get_nota(self):
        return Calificacion.objects.filter(libro__id=self.id).aggregate(Sum('nota'))['nota__sum'] or 0

    @property
    def calcular_calificacion(self):
        try:
            return self.get_nota / self.get_votos
        except:
            return 0

    @property
    def get_calificacion(self):
        return self.calcular_calificacion


    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural  =  "Libros"
        ordering             =  ["-subido", "-contador", "titulo", "-agnoedicion", "isbn"]



class Novedad(models.Model):
    titulo    =  models.CharField(max_length=100)
    texto     =  models.TextField()
    creacion  =  models.DateTimeField(auto_now_add=True, verbose_name="Creacion")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural  =  "Novedades"
        ordering             =  ["-creacion"]


class Usuario(models.Model):
    user                =  models.OneToOneField(User, on_delete=models.CASCADE, default='')
    tarjeta             =  models.CharField(max_length=16, validators=[RegexValidator('^(\d{16})$', 'Debe introducir un numero de 16 digitos')], verbose_name="Tarjeta de credito")
    fecha_de_nacimiento =  models.DateField(verbose_name='Fecha de nacimiento')
    cantPerfiles        =  models.IntegerField(default=2)
    is_premium          =  models.BooleanField(default=False)
    
    class Meta:
        ordering            =  ["user__email", "fecha_de_nacimiento"]
        verbose_name_plural =  "Usuarios"

    def __str__(self):
        return self.user.email

class Trailer(models.Model):

    def content_file_name(instance, filename):
        nombre  =  filename
        return '/'.join(['trailers', instance.titulo, nombre])

    titulo    =  models.CharField(max_length=200, default='NONE', verbose_name="Titulo")
    imagen    =  models.ImageField(null=True, blank=True, upload_to=content_file_name, default='default.jpg', verbose_name="Imagen")
    texto     =  models.TextField(max_length=1000, default='NONE', verbose_name="Texto")
    creacion  =  models.DateTimeField(auto_now_add=True, verbose_name="Creacion")
    libro     =  models.ForeignKey(Libro, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo + ' trailer'

    class Meta:
        verbose_name_plural = "Trailers"
        ordering = ["-creacion"]

    def get_imagen(self):
        return self.imagen.url


class Perfil(models.Model):
    usuario      =  models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    username     =  models.CharField(max_length=20, verbose_name='Nombre de usuario')
    historial    =  models.ManyToManyField('Libro', verbose_name='Historial'  , related_name="historial"  )
    favoritos    =  models.ManyToManyField('Libro', verbose_name='Favoritos'  , related_name="favoritos"  )
    leidos       =  models.ManyToManyField('Libro', verbose_name='Leidos'     , related_name="leidos"     )
    selected     =  models.BooleanField(default=True, verbose_name='Perfil seleccionado')

    @property
    def get_calificados(self):
        return Calificacion.objects.filter(perfil__id=self.id)
    
    def __str__(self):
        return self.username

    class Meta:
        ordering             =  ['-selected']
        verbose_name_plural  =  "Perfiles"


class Comentario(models.Model):
    perfil =  models.ForeignKey('Perfil', on_delete=models.SET_NULL, null=True,verbose_name='Perfil del comentario')
    libro  =  models.ForeignKey('Libro', on_delete=models.SET_NULL, null=True,verbose_name='Libro del comentario')
    texto  =  models.TextField(max_length=1000, validators=[MinLengthValidator(20)],verbose_name='Texto del comentario')
    fecha  =  models.DateTimeField(auto_now_add=True,verbose_name='Fecha del comentario')

    class Meta:
        ordering  =  ['-fecha']

    def __str__(self):
        """
        los datetimefield son datetime.datetime objects de python
        en la base de datos es almacena la fecha en utc y cuando uno cambia en settings
        la time_zone solo cambia a fines de traduccion de django pero no el como se almacena en la db
        por eso es necesaria transformarla cuando se muestra como string el objeto directo desde la db
        y para eso usamos el metodo astimezone de datime que devuelve el objeto datetime de la timezone local
        """
        perfil  =  str(self.perfil)
        fecha   =  str(self.fecha.astimezone().strftime("%d-%m-%Y"))
        hora    =  str(self.fecha.astimezone().strftime("%H:%M"))
        return 'Comentado por ' + perfil + ' el ' + fecha + ' a las ' + hora

