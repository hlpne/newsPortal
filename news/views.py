from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post
from .forms import PostForm
from .filters import PostFilter


class NewsListView(ListView):
    model = Post
    template_name = 'news/list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.NEWS)
            .select_related('author__user')
            .order_by('-created_at')
        )

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


class NewsSearchView(FilterView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'posts'
    filterset_class = PostFilter
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.NEWS)
            .select_related('author__user')
            .order_by('-created_at')
        )

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


class NewsDetailView(DetailView):
    model = Post
    template_name = 'news/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS).select_related('author__user')


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.post_type = Post.NEWS
        
        # Автоматически назначаем автора из текущего пользователя
        from .models import Author
        author, created = Author.objects.get_or_create(user=self.request.user)
        instance.author = author
        
        instance.save()
        form.save_m2m()  # Сохраняем связи many-to-many (категории)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})


class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.post_type = Post.ARTICLE
        
        # Автоматически назначаем автора из текущего пользователя
        from .models import Author
        author, created = Author.objects.get_or_create(user=self.request.user)
        instance.author = author
        
        instance.save()
        form.save_m2m()  # Сохраняем связи many-to-many (категории)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class ArticleListView(ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(post_type=Post.ARTICLE)
            .select_related('author__user')
            .order_by('-created_at')
        )

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


class ArticleDetailView(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE).select_related('author__user')

