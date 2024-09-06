from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from myblog.apps.posts.models import Post, Category
from myblog.core.utils import get_table_of_content

from .forms import AddCommentForm


def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all()
    featured_post = Post.objects.filter(status=Post.STATUS.published).last()
    posts = Post.objects.filter(status=Post.STATUS.published).exclude(id=featured_post.id) \
        .select_related('category', 'author').prefetch_related('tags').order_by('-created')

    context_data = {
        'title': 'Home',
        'featured_post': featured_post,
        'posts': posts,
        'categories': categories
    }
    return render(request, "index.html", context_data)


def details(request: HttpRequest, slug) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    related_posts = Post.objects.filter(status=Post.STATUS.published).exclude(id=post.id)
    table_of_content, updated_content = get_table_of_content(post.content)
    post.content = updated_content

    form = AddCommentForm(request.POST or None)
    if form.is_valid():
        form.save(post)
        messages.success(request, "Comment added successfully")
        return redirect(reverse('details', args=[slug]) + "#comments")

    context_data = {
        'post': post,
        'related_posts': post.get_related_posts(),
        'form': form,
        'title': post.title,
        'comments': post.comments.select_related('author').order_by('-created'),
        'table_of_content': table_of_content
    }
    return render(request, "details.html", context_data)


def about_me(request: HttpRequest) -> HttpResponse:
    context_data = {
        'title': 'About Me'
    }
    return render(request, "about_me.html", context_data)
