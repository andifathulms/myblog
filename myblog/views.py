from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    context_data = {}
    return render(request, "index.html", context_data)