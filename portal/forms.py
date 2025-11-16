from django import forms
from .models import Comment, Article

class CommentForm(forms.ModelForm):
    # Honeypot field for spam protection
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'style': 'display:none', 'tabindex': '-1', 'autocomplete': 'off'}),
        label=''
    )
    
    class Meta:
        model = Comment
        fields = ('name', 'email', 'content', 'website')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Электронная почта'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Поделитесь своим мнением'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError('Имя должно содержать минимум 2 символа.')
        return name.strip()
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError('Комментарий должен содержать минимум 10 символов.')
        if len(content) > 2000:
            raise forms.ValidationError('Комментарий не должен превышать 2000 символов.')
        return content.strip()
    
    def clean_website(self):
        # Honeypot: if filled, it's spam
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError('Спам-фильтр активирован.')
        return website

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title','slug','excerpt','content','category','tags','cover','status')
