from django.urls import path
from .views import (
    NewsListView, NewsDetailView, NewsSearchView,
    NewsCreateView, NewsUpdateView, NewsDeleteView,
    ArticleListView, ArticleDetailView,
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
    CategoryListView, CategoryDetailView, subscribe_category, unsubscribe_category,
    send_test_digest,
)

app_name = 'news'

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
    
    # Категории и подписки
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:pk>/subscribe/', subscribe_category, name='category_subscribe'),
    path('category/<int:pk>/unsubscribe/', unsubscribe_category, name='category_unsubscribe'),
    
    # Тестовая отправка дайджеста (только для администраторов)
    path('send-test-digest/', send_test_digest, name='send_test_digest'),
]


