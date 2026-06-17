from django import forms
from django.contrib.auth.models import User
from .models import Perfil
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class RegistroForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico',
            'autocomplete': 'off'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'off'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'off'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(password1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        return cleaned_data


PAISES_CHOICES = [
    ('', 'Seleccionar país'),
    ('CO', 'Colombia'),
    ('AR', 'Argentina'),
    ('MX', 'México'),
    ('ES', 'España'),
    ('US', 'Estados Unidos'),
    ('BR', 'Brasil'),
    ('CL', 'Chile'),
    ('PE', 'Perú'),
    ('VE', 'Venezuela'),
    ('EC', 'Ecuador'),
    # Agregar más según necesites
]

IDENTIFICADOR_TELEFONO_CHOICES = [
    ('+57', '+57 (Colombia)'),
    ('+54', '+54 (Argentina)'),
    ('+52', '+52 (México)'),
    ('+34', '+34 (España)'),
    ('+1', '+1 (USA/Canadá)'),
    ('+55', '+55 (Brasil)'),
    ('+56', '+56 (Chile)'),
    ('+51', '+51 (Perú)'),
    ('+58', '+58 (Venezuela)'),
    ('+593', '+593 (Ecuador)'),
]

SEXO_CHOICES = [
    ('', 'Seleccionar'),
    ('Masculino', 'Masculino'),
    ('Femenino', 'Femenino'),
    ('Otro', 'Otro'),
    ('Prefiero no decir', 'Prefiero no decir'),
]

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'correo', 'telefono', 'identificador_telefono', 
                  'direccion', 'edad', 'sexo', 'nacionalidad']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo',
                'pattern': '^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$',
                'title': 'Solo letras y espacios'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567',
                'pattern': '[0-9]{10}',
                'title': '10 dígitos numéricos',
                'maxlength': '10'
            }),
            'identificador_telefono': forms.Select(choices=IDENTIFICADOR_TELEFONO_CHOICES, attrs={
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 123 #45-67',
                'minlength': '10'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '18',
                'min': 18,
                'max': 120
            }),
            'sexo': forms.Select(choices=SEXO_CHOICES, attrs={
                'class': 'form-control'
            }),
            'nacionalidad': CountrySelectWidget(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_edad(self):
        edad = self.cleaned_data.get('edad')
        if edad and edad < 18:
            raise forms.ValidationError('Debes ser mayor de 18 años.')
        return edad
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError('El teléfono debe contener solo números.')
        if telefono and len(telefono) != 10:
            raise forms.ValidationError('El teléfono debe tener 10 dígitos.')
        return telefono