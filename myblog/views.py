from django.http import HttpResponse, HttpRequest
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    context_data = {
        'titles': ['Data Science 101', 'Programming 101', 'History of Discuss Throw',
                   'Machine Learning 101', 'Advance Programming', 'Timurid Empire'],
        'categories': ['Programming', 'Data Science', 'Machine Learning', 'Sports']
    }
    return render(request, "index.html", context_data)