from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from users.models import CustomUser

class CambiarContrasenaForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
