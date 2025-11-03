from django import forms
from .models import Post, Category


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5',
            'multiple': True
        }),
        label='Категории',
        required=False,
        help_text='Удерживайте Ctrl (Cmd на Mac) для выбора нескольких категорий'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Автоматически назначаем автора из текущего пользователя
        # Это будет сделано в представлении
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
