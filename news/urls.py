from django.urls import path
from .views import (
    NewsListView, NewsDetailView, NewsSearchView,
    NewsCreateView, NewsUpdateView, NewsDeleteView,
    ArticleListView, ArticleDetailView,
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
)

urlpatterns = [
    # Новости
    path('', NewsListView.as_view(), name='news_list'),
    path('search/', NewsSearchView.as_view(), name='news_search'),
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    
    # Статьи
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
]


