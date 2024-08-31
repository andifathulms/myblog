from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count

from myblog.apps.posts.models import Category
from myblog.core.decorators import  author_required

from .forms import CategoryBaseForm

from typing import Optional


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
def manage(request: HttpRequest, id: Optional[int] = None) -> HttpResponse:
    if id:
        category = get_object_or_404(Category, pk=id)
        initial = {'name': category.name}
    else:
        category = None
        initial = None

    if request.method == 'POST':
        form = CategoryBaseForm(request.POST, instance=category, initial=initial)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False})
