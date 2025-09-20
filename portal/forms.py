from django import forms
from .models import Comment, Article

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'content')

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title','slug','excerpt','content','category','tags','cover','status')
