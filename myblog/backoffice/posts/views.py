from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from myblog.apps.posts.models import Post, PostLog
from myblog.core.decorators import  author_required

from .forms import FilterForm, PostCreationForm


@author_required
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.order_by('-created')

    initial = {
        'status': [Post.STATUS.published],
        'language': [Post.LANGUAGE.id, Post.LANGUAGE.en]
    }
    form = FilterForm(request.GET or initial)
    if form.is_valid():
        posts = form.filter()

    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context_data = {
        'title': 'Post List',
        'posts': posts,
        'form': form
    }
    return render(request, "backoffice/posts/index.html", context_data)


@author_required
def add(request: HttpRequest) -> HttpResponse:
    user = request.user

    form = PostCreationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        print('valid')
        form.save(created_by=user)
        messages.success(request, 'Post succesfully created')
        return redirect(reverse("backoffice:posts:index"))
    else:
        print('errors')
        print(form.errors)

    context_data = {
        'title': 'Add Post',
        'form': form
    }
    return render(request, "backoffice/posts/add.html", context_data)


@author_required
def draft(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    post.status = Post.STATUS.draft
    post.save(update_fields=['status'])
    post.logs.create(action=PostLog.ACTION.drafted, created_by=request.user)

    return redirect(reverse("backoffice:posts:index"))


@author_required
def publish(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    post.status = Post.STATUS.published
    update_fields = ['status']

    if not post.published_date:
        post.published_date = timezone.now()
        update_fields.append('published_date')

    post.save(update_fields=update_fields)
    post.logs.create(action=PostLog.ACTION.published, created_by=request.user)

    return redirect(reverse("backoffice:posts:index"))
