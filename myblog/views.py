from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from myblog.apps.posts.models import Post, Category


def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all()
    posts = Post.objects.filter(status=Post.STATUS.published) \
        .select_related('category', 'author').prefetch_related('tags').order_by('-created')
    context_data = {
        'title': 'Home',
        'posts': posts,
        'categories': categories
    }
    return render(request, "index.html", context_data)


def details(request: HttpRequest, slug) -> HttpResponse:
    post = Post.objects.get(slug=slug)
    context_data = {
        'post': post,
        'title': post.title
    }
    return render(request, "details.html", context_data)
