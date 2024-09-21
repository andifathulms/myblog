from django.http import HttpRequest
from django.db.models import Count, Q

from .models import Category, Post
from typing import Dict


def post_settings(request: HttpRequest) -> Dict:
    active_categories = Category.objects \
        .annotate(post_count=Count('posts', filter=Q(posts__status=Post.STATUS.published))) \
        .filter(post_count__gt=0)

    return {
        'active_categories': active_categories
    }
