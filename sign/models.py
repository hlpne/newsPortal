from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class CommonSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style all form fields with consistent Bootstrap styling
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
        
        # Add the username field to the form fields
        self.fields['username'] = forms.CharField(
            label="Имя пользователя",
            max_length=150,
            required=True,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            })
        )
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username
    
    def save(self, request):
        user = super().save(request)
        # Set the username from the form
        user.username = self.cleaned_data['username']
        user.save()
        common_group, _ = Group.objects.get_or_create(name='common')
        common_group.user_set.add(user)
        return user
