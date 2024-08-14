from django.db import models
from django.utils.text import slugify

from thumbnails.fields import ImageField

from myblog.core.utils import FilenameGenerator

from model_utils import Choices


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

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

    category = models.ForeignKey(Category, related_name='posts', on_delete=models.SET_NULL,
                                 null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    content = models.TextField()
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.read_time:
            self.read_time = len(self.content.split()) // 200  # Rough estimate: 200 words/minute
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies',
                               null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.author.name} on {self.post}"


class PostLog(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='logs')

    ACTION = Choices(
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
