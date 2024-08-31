from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count

from myblog.apps.posts.models import Category
from myblog.core.decorators import  author_required

from .forms import CategoryBaseForm


@author_required
def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')

    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)

    context_data = {
        'title': 'Post List',
        'categories': categories,
        'form': CategoryBaseForm()
    }
    return render(request, "backoffice/categories/index.html", context_data)


@author_required
def add(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CategoryBaseForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False})
