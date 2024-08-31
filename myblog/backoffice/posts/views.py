from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from myblog.apps.posts.models import Post
from myblog.core.decorators import  author_required


@author_required
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.order_by('-created')

    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context_data = {
        'title': 'Post List',
        'posts': posts
    }
    return render(request, "backoffice/posts/index.html", context_data)
