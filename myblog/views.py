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
    related_posts = Post.objects.filter(status=Post.STATUS.published).exclude(id=post.id)

    context_data = {
        'post': post,
        'related_posts': post.get_related_posts(),
        'title': post.title,
        'comments': post.comments.select_related('author').order_by('-created')
    }
    return render(request, "details.html", context_data)


def about_me(request: HttpRequest) -> HttpResponse:
    context_data = {
        'title': 'About Me'
    }
    return render(request, "about_me.html", context_data)
