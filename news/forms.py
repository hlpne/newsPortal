from django import forms
from .models import Post, Author, User


class PostForm(forms.ModelForm):
    author_name = forms.CharField(
        max_length=150,
        label='Имя автора',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя автора'
        }),
        help_text='Введите имя автора (например: Иван Петров)'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'categories': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'categories': 'Категории',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующий пост, показываем текущего автора
        if self.instance and self.instance.pk and self.instance.author:
            self.fields['author_name'].initial = self.instance.author.user.get_full_name() or self.instance.author.user.username

    def clean_author_name(self):
        author_name = self.cleaned_data.get('author_name')
        if not author_name:
            raise forms.ValidationError('Имя автора обязательно для заполнения.')
        return author_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Получаем или создаем автора
        author_name = self.cleaned_data['author_name']
        
        # Ищем существующего пользователя по имени или создаем нового
        user, created = User.objects.get_or_create(
            username=author_name.lower().replace(' ', '_'),
            defaults={
                'first_name': author_name.split()[0] if author_name.split() else author_name,
                'last_name': ' '.join(author_name.split()[1:]) if len(author_name.split()) > 1 else '',
                'email': f"{author_name.lower().replace(' ', '_')}@example.com"
            }
        )
        
        # Создаем или получаем автора
        author, created = Author.objects.get_or_create(user=user)
        instance.author = author
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
