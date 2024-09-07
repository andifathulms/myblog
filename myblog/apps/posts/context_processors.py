from django.http import HttpRequest
from django.db.models import Count

from .models import Category
from typing import Dict


def post_settings(request: HttpRequest) -> Dict:
    active_categories = Category.objects.annotate(post_count=Count('posts')) \
        .filter(post_count__gt=0)

    return {
        'active_categories': active_categories
    }
