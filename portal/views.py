from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.urls import reverse

from .models import Article
from .forms import CommentForm
from django.contrib import messages

class ArticleListView(ListView):
    model = Article
    template_name = 'portal/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        queryset = (
            Article.objects.filter(status='published')
            .select_related('category', 'author')
            .prefetch_related('tags')
        )
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.request.GET.get('category', '')
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context['article']
        context['current_category'] = article.category.slug if article.category else ''
        context['related_articles'] = (
            Article.objects.filter(status='published', category=article.category)
            .exclude(pk=article.pk)
            .select_related('category', 'author')
            .prefetch_related('tags')[:3]
        )
        return context

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
    return render(
        request,
        'portal/comment_form.html',
        {
            'form': form,
            'article': article,
            'current_category': article.category.slug if article.category else '',
        },
    )

# Simple search view
def search(request):
    q = request.GET.get('q', '')
    if q:
        results = (
            Article.objects.filter(status='published')
            .filter(
                Q(title__icontains=q)
                | Q(excerpt__icontains=q)
                | Q(content__icontains=q)
            )
            .select_related('category', 'author')
            .prefetch_related('tags')
        )
    else:
        results = Article.objects.none()
    return render(
        request,
        'portal/search.html',
        {
            'q': q,
            'results': results,
            'current_category': '',
        },
    )
