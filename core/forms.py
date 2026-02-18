from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 or password2:
            if not password1 or not password2:
                raise forms.ValidationError("Completa ambos campos de contraseña.")
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user
