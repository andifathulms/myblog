from redis import Redis

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Count, Sum, Avg, Q

from myblog.apps.posts.models import Post, Category, Tag, PostLog
from myblog.core.utils import get_table_of_content, get_post_view_threshold

from .forms import AddCommentForm


redis_client = Redis()


def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all()
    featured_post = Post.objects.filter(status=Post.STATUS.published).last()
    posts = Post.objects.filter(status=Post.STATUS.published).exclude(id=featured_post.id) \
        .select_related('category', 'author').prefetch_related('tags').order_by('-created')

    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        posts_html = render_to_string('include/post_partial.html', {'posts': posts})
        return JsonResponse({
            'posts_html': posts_html,
            'has_next': posts.has_next()
        })

    context_data = {
        'title': 'Home',
        'featured_post': featured_post,
        'posts': posts,
        'categories': categories
    }
    return render(request, "index.html", context_data)


def details(request: HttpRequest, slug) -> HttpResponse:
    post = get_object_or_404(Post, slug=slug)
    related_posts = Post.objects.filter(status=Post.STATUS.published).exclude(id=post.id)
    table_of_content, updated_content = get_table_of_content(post.content)
    post.content = updated_content

    redis_key = f'post:{post.id}:views'
    session_key = f'viewed_post_{post.id}'
    view_treshold = get_post_view_threshold(post.views)

    if not request.session.get(session_key, False):
        new_count = redis_client.incr(redis_key)
        request.session[session_key] = True

        if new_count >= view_treshold:
            post.views += new_count
            post.save(update_fields=['views'])

            redis_client.delete(redis_key)

    form = AddCommentForm(request.POST or None)
    if form.is_valid():
        form.save(post)
        messages.success(request, "Comment added successfully")
        return redirect(reverse('details', args=[slug]) + "#comments")

    context_data = {
        'post': post,
        'edit_log': post.logs.filter(action=PostLog.ACTION.edited).last(),
        'related_posts': post.get_related_posts(),
        'form': form,
        'title': post.title,
        'comments': post.comments.select_related('author').order_by('-created'),
        'table_of_content': table_of_content
    }
    return render(request, "details.html", context_data)


def about_me(request: HttpRequest) -> HttpResponse:
    context_data = {
        'title': 'About Me'
    }
    return render(request, "about_me.html", context_data)


def categories(request: HttpRequest, id: int) -> HttpResponse:
    category = get_object_or_404(Category, id=id)
    posts = category.posts.filter(status=Post.STATUS.published) \
        .select_related('category', 'author').prefetch_related('tags').order_by('-created')

    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context_data = {
        'title': f'Post with category of {category.name}',
        'posts': posts
    }
    return render(request, "categories.html", context_data)


def tags(request: HttpRequest, id: int) -> HttpResponse:
    tag = get_object_or_404(Tag, id=id)
    posts = Post.objects.filter(tags=tag, status=Post.STATUS.published) \
        .select_related('category', 'author').prefetch_related('tags').order_by('-created')

    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context_data = {
        'title': f'Post with tags of {tag.name}',
        'posts': posts,
        'show_post_category': True,
        'tag_id': id
    }
    return render(request, "categories.html", context_data)


def analytics(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.annotate(
        total_posts=Count('posts', filter=Q(posts__status=Post.STATUS.published)),
        total_views=Sum('posts__views', filter=Q(posts__status=Post.STATUS.published)),
        avg_read_time=Avg('posts__read_time', filter=Q(posts__status=Post.STATUS.published))
    ).filter(total_posts__gt=0).order_by('-total_posts', '-total_views')

    tags = Tag.objects.annotate(
        total_posts=Count('post', filter=Q(post__status=Post.STATUS.published)),
        total_views=Sum('post__views', filter=Q(post__status=Post.STATUS.published)),
        avg_read_time=Avg('post__read_time', filter=Q(post__status=Post.STATUS.published))
    ).filter(total_posts__gt=0).order_by('-total_posts', '-total_views')

    context_data = {
        'title': 'InsightfulBytes Analytics',
        'categories': categories,
        'tags': tags
    }
    return render(request, "analytics.html", context_data)
