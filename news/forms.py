from django import forms
from .models import Post, Author, User


class PostForm(forms.ModelForm):
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Автоматически назначаем автора из текущего пользователя
        # Это будет сделано в представлении
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
