from django import forms

from myblog.apps.posts.models import Comment, Post


class AddCommentForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-[#254336] focus:border-[#254336] sm:text-sm',
            'id': 'author_name',
            'placeholder': 'Your Name',
        })
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-[#254336] focus:border-[#254336] sm:text-sm',
            'id': 'content',
            'placeholder': 'Your Comment',
            'rows': 4,
        })
    )

    def save(self, post: Post) -> None:
        username = self.cleaned_data['username']
        text = self.cleaned_data['text']

        post.comments.create(username=username, text=text)

