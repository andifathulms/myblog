from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count

from myblog.apps.posts.models import Category
from myblog.core.decorators import  author_required


@author_required
def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-name')

    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)

    context_data = {
        'title': 'Post List',
        'categories': categories
    }
    return render(request, "backoffice/categories/index.html", context_data)
