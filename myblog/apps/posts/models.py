from django.db import models
from django.db.models import QuerySet, Count
from django.utils import timezone
from django.utils.text import slugify

from thumbnails.fields import ImageField

from myblog.apps.users.models import User
from myblog.core.utils import FilenameGenerator

from model_utils import Choices
from django_ckeditor_5.fields import CKEditor5Field

from typing import Optional


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    background_color = models.CharField(max_length=7, default='#000')

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    STATUS = Choices(
        (10, 'draft', 'Draft'),
        (15, 'published', 'Published'),
        (20, 'archived', 'Archived')
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=STATUS.draft)

    LANGUAGE = Choices(
        (1, 'id', 'Indonesian'),
        (2, 'en', 'English')
    )
    language = models.PositiveSmallIntegerField(choices=LANGUAGE)

    TYPE = Choices(
        (1, 'regular', 'Regular'),
        (2, 'assignment', 'Assignment')
    )
    type = models.PositiveSmallIntegerField(choices=TYPE, default=TYPE.regular)

    category = models.ForeignKey(Category, related_name='posts', on_delete=models.SET_NULL,
                                 null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    content = CKEditor5Field('Text', config_name='extends')
    has_latex = models.BooleanField(default=False)
    excerpt = models.TextField(blank=True, null=True)
    featured_image = ImageField(upload_to=FilenameGenerator(prefix='feature_images'),
                                blank=True, null=True)

    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    published_date = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    allow_comments = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(blank=True, null=True)  # Estimated in minutes

    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)

    canonical_url = models.URLField(blank=True, null=True)
    og_title = models.CharField(max_length=200, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = ImageField(upload_to=FilenameGenerator(prefix='og_images'), blank=True, null=True)

    def save(self, *args, **kwargs) -> 'Post':
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug

        self.read_time = len(self.content.split()) // 200  # Rough estimate: 200 words/minute

        post = super().save(*args, **kwargs)
        return post

    def __str__(self):
        return self.title

    def drafted(self, created_by: Optional[User], notes: Optional[str] = '') -> None:
        self.status = self.STATUS.draft
        self.save(update_fields=['status'])

        self.logs.create(action=PostLog.ACTION.drafted, created_by=created_by, notes=notes)

    def published(self, created_by: Optional[User], notes: Optional[str] = '') -> None:
        self.status = self.STATUS.published
        self.published_date = timezone.now()
        self.save(update_fields=['status', 'published_date'])

        self.logs.create(action=PostLog.ACTION.published, created_by=created_by, notes=notes)

    def get_related_posts(self) -> QuerySet:
        related_posts = Post.objects.exclude(id=self.id)
        tags = self.tags.all()
        if tags.exists():
            related_posts = related_posts \
                .filter(tags__in=tags, status=self.STATUS.published, type=self.type) \
                .annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')

        category = self.category
        if category:
            related_posts = related_posts | Post.objects.filter(category=category, status=self.STATUS.published, type=self.type) \
                .exclude(id=self.id).order_by('-created')

        if len(related_posts) < 3:
            latest_posts = Post.objects.filter(status=self.STATUS.published, type=self.type).exclude(id=self.id).order_by('-created')
            related_posts = related_posts | latest_posts

        return related_posts.distinct()[:3]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies',
                               null=True, blank=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments',
                               blank=True, null=True)

    def __str__(self):
        author = self.author.name if self.author else self.username
        return f"Comment by {author} on {self.post}"


class PostLog(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='logs')

    ACTION = Choices(
        (5, 'created', 'Created'),
        (10, 'drafted', 'Drafted'),
        (11, 'published', 'Published'),
        (12, 'archived', 'Archived'),
        (20, 'edited', 'Edited')
    )
    action = models.PositiveSmallIntegerField(choices=ACTION)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User', related_name="post_logs", on_delete=models.CASCADE,
                                   blank=True, null=True)
    notes = models.TextField(default="")
