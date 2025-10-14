from django.views.generic import ListView, DetailView
from .models import Post


class NewsListView(ListView):
    model = Post
    template_name = 'news/list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return (
            Post.objects.filter(post_type__in=[Post.ARTICLE, Post.NEWS])
            .order_by('-created_at')
            .only('id', 'title', 'text', 'created_at')
        )


class NewsDetailView(DetailView):
    model = Post
    template_name = 'news/detail.html'
    context_object_name = 'post'

