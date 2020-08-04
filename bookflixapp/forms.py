from django import forms
from django.core.exceptions import ValidationError
from .models import Autor, Editorial, Genero, Usuario, Comentario, Perfil
from datetime import datetime as d
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User


from django.utils.translation import gettext_lazy as _


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Email',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su email',
        'autofocus': True, 'type': 'email', 'class': 'form-control',
        'id': 'id_email'}),
    )
    
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña',
               'class': 'form-control', 'autocomplete': 'current-password'}),
    )


        
class RegistrationForm(UserCreationForm):

    fecha_de_nacimiento = forms.DateField(required=True)
    #tarjeta = forms.CharField(required=True, max_length=16, min_length=16)
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields['password2'].help_text = None

    def clean_email(self):
        data = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise ValidationError("El email ya esta registrado")



class EditProfileForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = (
                 'email',
                 'first_name',
                 'last_name'
                )

    user = None
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('user'):
            self.user = kwargs.pop('user', None)
        super(EditProfileForm, self).__init__(*args,**kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        owns_email = (email != self.user.email)
        if User.objects.filter(email__icontains=email).exists() and owns_email:
            raise forms.ValidationError("El email ya esta registrado")
        return email

        
class ProfileForm(forms.ModelForm):
    tarjeta = forms.CharField(required=False, label="Tarjeta De Credito", max_length=16, min_length=16)

    def clean_tarjeta(self):
        tarjeta = self.cleaned_data.get("tarjeta")
        if tarjeta != "" and not tarjeta.isdigit():
            raise forms.ValidationError("Tarjeta invalida, ingrese solo digitos")
        return tarjeta

    class Meta:
        model = Usuario
        fields = ('fecha_de_nacimiento', 'tarjeta',)


class CreateProfileForm(forms.Form):
    profilename = forms.CharField(required=True, label="Nombre de Perfil")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CreateProfileForm, self).__init__(*args, **kwargs)

    def clean_profilename(self):
        data = self.cleaned_data['profilename']
        aus = self.user
        u = User.objects.get(email=aus)
        usu = Usuario.objects.get(user=u)
        try:
            p = Perfil.objects.get(usuario=usu, username=data)
        except Perfil.DoesNotExist:
            return data
        raise ValidationError("Nombre de perfil ya usado")


class ComentarioForm(forms.ModelForm):

    texto = forms.CharField( required=False,
        label="Escriba un comentario",
        widget=forms.Textarea(attrs={'maxlength':'1000', 'minlength':'20',
                                     'placeholder':'Escribe un comentario',
                                     'name':'texto', 'rows':'4',
                                     'class':'form-control',
                                     'style':'resize:none;'}),
    )
    
    class Meta:
        model = Comentario
        fields = ('texto',)
