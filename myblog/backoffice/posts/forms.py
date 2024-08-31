from django import forms
from django.db.models.query import QuerySet

from myblog.apps.posts.models import Post, Category

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
