from django import forms
from django.db.models.query import QuerySet

from myblog.apps.posts.models import Post, Category, Tag, PostLog
from myblog.apps.users.models import User

from django_ckeditor_5.widgets import CKEditor5Widget

from typing import Dict


class FilterForm(forms.Form):
    created_start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    created_end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    status = forms.MultipleChoiceField(choices=Post.STATUS, required=False,
                                       widget=forms.CheckboxSelectMultiple())
    language = forms.MultipleChoiceField(choices=Post.LANGUAGE, required=False,
                                         widget=forms.CheckboxSelectMultiple())
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

    def clean(self) -> Dict:
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        created_start_date = cleaned_data['created_start_date']
        created_end_date = cleaned_data['created_end_date']

        if created_start_date and created_end_date and created_start_date > created_end_date:
            self.add_error("created_start_date", "Start date can't be greater than end date")

        return cleaned_data

    def filter(self) -> QuerySet:
        statuses = self.cleaned_data['status']
        languages = self.cleaned_data['language']
        category = self.cleaned_data['category']
        created_start_date = self.cleaned_data['created_start_date']
        created_end_date = self.cleaned_data['created_end_date']

        posts = Post.objects.filter(status__in=statuses, language__in=languages).order_by('-created')

        if created_start_date and created_end_date:
            posts = posts.filter(created__date__range=[created_start_date, created_end_date])
        elif created_start_date:
            posts = posts.filter(created__gte=created_start_date)
        elif created_end_date:
            posts = posts.filter(created__lte=created_end_date)

        return posts


class PostCreationForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-input',
                                                                          'placeholder': 'Title'}))
    status = forms.ChoiceField(choices=Post.STATUS, initial=Post.STATUS.draft,
                               widget=forms.Select(attrs={'class': 'form-select'}))
    language = forms.ChoiceField(choices=Post.LANGUAGE, widget=forms.Select(attrs={'class': 'form-select'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False,
                                      widget=forms.Select(attrs={'class': 'form-select'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False,
                                          widget=forms.CheckboxSelectMultiple)
    content = forms.CharField(
        widget=CKEditor5Widget(attrs={'class': 'django_ckeditor_5', 'placeholder': 'Content'},
                               config_name='extends'))
    excerpt = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                                           'placeholder': 'Excerpt'}))
    featured_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-file'}))
    allow_comments = forms.BooleanField(required=False, initial=True,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
    meta_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                                                    'placeholder': 'Meta Description'}))
    meta_keywords = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                                                 'placeholder': 'Meta Keywords'}))
    canonical_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-url',
                                                                                'placeholder': 'Canonical URL'}))
    og_title = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-input',
                                                                                             'placeholder': 'OG Title'}))
    og_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                                                  'placeholder': 'OG Description'}))
    og_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-file'}))

    def save(self, created_by: User) -> Post:
        title = self.cleaned_data['title']
        status = self.cleaned_data['status']
        language = self.cleaned_data['language']
        category = self.cleaned_data['category']
        tags = self.cleaned_data['tags']
        content = self.cleaned_data['content']
        excerpt = self.cleaned_data['excerpt']
        featured_image = self.cleaned_data['featured_image']
        allow_comments = self.cleaned_data['allow_comments']
        meta_description = self.cleaned_data['meta_description'] or excerpt
        meta_keywords = self.cleaned_data['meta_keywords']
        canonical_url = self.cleaned_data['canonical_url']
        og_title = self.cleaned_data['og_title'] or title
        og_description = self.cleaned_data['og_description'] or excerpt
        og_image = self.cleaned_data['og_image'] or featured_image

        post = Post.objects.create(title=title, status=status, language=language, category=category,
                                   content=content, excerpt=excerpt, featured_image=featured_image,
                                   allow_comments=allow_comments, meta_description=meta_description,
                                   meta_keywords=meta_keywords, canonical_url=canonical_url,
                                   og_title=og_title, og_description=og_description, og_image=og_image,
                                   author=created_by)
        post.tags.set(tags)
        post.logs.create(action=PostLog.ACTION.created, created_by=created_by)

        if post.status == Post.STATUS.draft:
            post.drafted(created_by)

        if post.status == Post.STATUS.published:
            post.published(created_by)
