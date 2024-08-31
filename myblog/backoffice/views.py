from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse

from myblog.core.decorators import  author_required


@author_required
def index(request: HttpRequest) -> HttpResponse:
    context_data = {
        'title': 'Backoffice'
    }
    return render(request, "backoffice/index.html", context_data)
