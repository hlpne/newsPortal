import django_filters
from django import forms
from .models import Post, Category


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Название",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по названию'})
    )
    author = django_filters.CharFilter(
        field_name="author__user__username",
        lookup_expr="icontains",
        label="Автор",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по автору'})
    )
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        label="Категории",
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    date_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gt",
        label="Позже даты",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = Post
        fields = ["title", "author", "categories", "date_after"]
