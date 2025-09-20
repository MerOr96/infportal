from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse
from .models import Article, Category, Tag
from .forms import CommentForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

class ArticleListView(ListView):
    model = Article
    template_name = 'portal/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.filter(status='published')

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'portal/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # increment view count
        obj.views = obj.views + 1
        obj.save(update_fields=['views'])
        return obj

def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if request.user.is_authenticated:
                comment.author = request.user
            comment.article = article
            comment.save()
            messages.success(request, 'Комментарий добавлен. Ожидает модерации.')
            return redirect(article.get_absolute_url() if hasattr(article, 'get_absolute_url') else reverse('portal:article_detail', args=[article.slug]))
    else:
        form = CommentForm()
    return render(request, 'portal/comment_form.html', {'form': form, 'article': article})

# Simple search view
def search(request):
    q = request.GET.get('q', '')
    results = Article.objects.filter(status='published').filter(title__icontains=q) if q else Article.objects.none()
    return render(request, 'portal/search.html', {'q': q, 'results': results})
