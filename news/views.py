from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Count
from .models import Post, Category, Author
from .forms import PostForm
from .filters import PostFilter


class PaginationWindowMixin:
    """Mixin для добавления окна страниц в контекст пагинации."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_obj = context['page_obj']
        
        # Создаем окно страниц для навигации
        current_page = page_obj.number
        total_pages = paginator.num_pages
        
        # Определяем окно страниц (текущая ± 2)
        window_size = 2
        start_page = max(1, current_page - window_size)
        end_page = min(total_pages, current_page + window_size)
        
        # Создаем список номеров страниц в окне
        page_numbers_window = list(range(start_page, end_page + 1))
        
        # Определяем, нужно ли показывать многоточие
        show_start_ellipsis = start_page > 2
        show_end_ellipsis = end_page < total_pages - 1
        
        context.update({
            'page_numbers_window': page_numbers_window,
            'show_start_ellipsis': show_start_ellipsis,
            'show_end_ellipsis': show_end_ellipsis,
        })
        
        return context


class PostCreateMixin:
    """Mixin для создания постов с проверкой лимита публикаций."""
    def form_valid(self, form):
        # Проверяем лимит публикаций (не более 3 в сутки)
        today = timezone.now().date()
        posts_today = Post.objects.filter(
            author__user=self.request.user,
            created_at__date=today
        ).count()
        if posts_today >= 3:
            form.add_error(None, ValidationError('Лимит публикаций: не более 3 в сутки.'))
            return self.form_invalid(form)
        
        # Если instance уже создан в дочернем классе, используем его
        if hasattr(self, '_instance'):
            instance = self._instance
        else:
            instance = form.save(commit=False)
        
        # Автоматически назначаем автора из текущего пользователя
        if not hasattr(instance, 'author') or instance.author is None:
            author, created = Author.objects.get_or_create(user=self.request.user)
            instance.author = author
        
        instance.save()
        form.save_m2m()  # Сохраняем связи many-to-many (категории)
        return super().form_valid(form)


class NewsListView(PaginationWindowMixin, ListView):
    model = Post
    template_name = 'news/list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.NEWS)
            .select_related('author__user')
            .prefetch_related('categories')
            .order_by('-created_at')
        )

class NewsSearchView(PaginationWindowMixin, FilterView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'posts'
    filterset_class = PostFilter
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.NEWS)
            .select_related('author__user')
            .prefetch_related('categories')
            .order_by('-created_at')
        )

class NewsDetailView(DetailView):
    model = Post
    template_name = 'news/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS).select_related('author__user').prefetch_related('categories')


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, PostCreateMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.post_type = Post.NEWS
        self._instance = instance  # Сохраняем для использования в миксине
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})


class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})


class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news:news_list')
    permission_required = ('news.delete_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, PostCreateMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.post_type = Post.ARTICLE
        self._instance = instance  # Сохраняем для использования в миксине
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:article_detail', kwargs={'pk': self.object.pk})


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)

    def get_success_url(self):
        return reverse_lazy('news:article_detail', kwargs={'pk': self.object.pk})


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('news:article_list')
    permission_required = ('news.delete_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class ArticleListView(PaginationWindowMixin, ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.ARTICLE)
            .select_related('author__user')
            .prefetch_related('categories')
            .order_by('-created_at')
        )


class ArticleDetailView(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE).select_related('author__user').prefetch_related('categories')


class CategoryListView(ListView):
    model = Category
    template_name = 'news/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(
            posts_count=Count('posts')
        ).order_by('name')


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['is_subscribed'] = user.is_authenticated and self.object.subscribers.filter(pk=user.pk).exists()
        ctx['posts'] = Post.objects.filter(categories=self.object).select_related('author__user').order_by('-created_at')
        return ctx


@login_required
def subscribe_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    messages.success(request, f'Вы подписались на категорию: {category.name}')
    return redirect(category.get_absolute_url())


@login_required
def unsubscribe_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.remove(request.user)
    messages.info(request, f'Вы отписались от категории: {category.name}')
    return redirect(category.get_absolute_url())


@login_required
def send_test_digest(request):
    """Тестовая функция для отправки еженедельного дайджеста (только для тестирования)"""
    from scheduler.jobs import weekly_digest_job
    
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Доступ запрещен. Только для администраторов.')
        return redirect('news:news_list')
    
    try:
        weekly_digest_job()
        messages.success(request, 'Еженедельный дайджест успешно отправлен всем подписчикам!')
    except Exception as e:
        messages.error(request, f'Ошибка при отправке дайджеста: {str(e)}')
    
    return redirect('news:news_list')

