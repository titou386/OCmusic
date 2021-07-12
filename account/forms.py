from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Pseudo', widget=forms
                               .TextInput(attrs={'autofocus': True,
                                                 'class': 'form-control'}))
    password = forms.CharField(label='Mot de passe', widget=forms
                               .PasswordInput(attrs={'autocomplete':
                                                     'current-password',
                                                     'class': 'form-control'}))


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Pseudo', min_length=4, max_length=150,
                               widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Mot de passe',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Vérification du mot de passe',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        r = User.objects.filter(username=username)
        if r.exists():
            raise ValidationError("Pseudo non disponible.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Le mots ne correspondent pas.")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
