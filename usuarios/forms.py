# PLUME-PROJECT/usuarios/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class NovoUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Obrigatório. Um email válido.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.', label='Nome')
    last_name = forms.CharField(max_length=150, required=True, help_text='Obrigatório.', label='Sobrenome')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def clean_email(self):
        """
        Verifica se o e-mail fornecido já existe no banco de dados.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este endereço de e-mail já está em uso por outra conta.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email') # Garante que o email seja salvo
        if commit:
            user.save()
        return user

class PerfilForm(forms.ModelForm):
    data_nascimento = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'DD/MM/AAAA'}),
        required=False,
        label='Data de Nascimento'
    )
    cidade = forms.CharField(
        max_length=100,
        required=False,
        label='Cidade',
        widget=forms.TextInput(attrs={'placeholder': 'Sua cidade'})
    )
    biografia = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Conte um pouco sobre você...'}),
        required=False,
        label='Biografia'
    )

    class Meta:
        model = Perfil
        fields = ['biografia', 'cidade', 'data_nascimento']

class AvatarUploadForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=True, 
        label='Nova Foto de Perfil',
    )

    class Meta:
        model = Perfil
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
            if avatar.size > MAX_SIZE_BYTES:
                raise forms.ValidationError(f"A imagem é muito grande. O tamanho máximo permitido é de 2MB.")
        return avatar