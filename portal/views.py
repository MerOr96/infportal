from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404, HttpResponseNotFound, HttpResponseServerError

from .models import Article, Comment
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

    def get_queryset(self):
        # Only show published articles to non-staff users
        queryset = Article.objects.filter(status='published').select_related('category', 'author').prefetch_related('tags')
        # Allow staff to see draft articles
        if self.request.user.is_staff:
            queryset = Article.objects.all().select_related('category', 'author').prefetch_related('tags')
        return queryset
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Atomic increment view count using F() to avoid race conditions
        # Only count views for published articles (and not for staff preview)
        if obj.status == 'published' and not self.request.user.is_staff:
            Article.objects.filter(pk=obj.pk).update(views=F('views') + 1)
            obj.refresh_from_db()
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
        
        # Paginated comments
        comments = article.comments.filter(is_moderated=True).select_related('author')
        paginator = Paginator(comments, 10)
        page_number = self.request.GET.get('page')
        context['comments'] = paginator.get_page(page_number)
        
        return context

def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Simple rate limiting: prevent spam by checking recent comments
    if request.method == 'POST':
        # Check for honeypot field (handled in form validation)
        form = CommentForm(request.POST)
        if form.is_valid():
            # Additional rate limiting check for anonymous users
            email = form.cleaned_data.get('email')
            if not request.user.is_authenticated and email:
                recent_comments = Comment.objects.filter(
                    email=email,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
                )
                if recent_comments.exists():
                    messages.warning(request, 'Пожалуйста, подождите немного перед добавлением следующего комментария.')
                    return redirect(article.get_absolute_url())
            
            comment = form.save(commit=False)
            if request.user.is_authenticated:
                comment.author = request.user
                # Auto-moderate comments from authenticated users
                comment.is_moderated = True
            comment.article = article
            comment.save()
            messages.success(request, 'Комментарий добавлен. Ожидает модерации.' if not comment.is_moderated else 'Комментарий добавлен и опубликован.')
            return redirect(article.get_absolute_url())
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

# Improved search view
def search(request):
    q = request.GET.get('q', '').strip()
    if q:
        # Split query into words for better search
        query_words = q.split()
        q_objects = Q()
        for word in query_words:
            q_objects |= (
                Q(title__icontains=word)
                | Q(excerpt__icontains=word)
                | Q(content__icontains=word)
                | Q(tags__name__icontains=word)
            )
        results = (
            Article.objects.filter(status='published')
            .filter(q_objects)
            .select_related('category', 'author')
            .prefetch_related('tags')
            .distinct()
            .order_by('-created_at')
        )
    else:
        results = Article.objects.none()
    
    # Paginate results
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(
        request,
        'portal/search.html',
        {
            'q': q,
            'results': page_obj,
            'current_category': '',
            'page_obj': page_obj,
        },
    )

# Error handlers
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
