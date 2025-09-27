from django.db.models import Count, Q

from .models import Article, Category


def portal_defaults(request):
    categories = (
        Category.objects.annotate(
            published_count=Count('articles', filter=Q(articles__status='published'))
        )
        .filter(published_count__gt=0)
        .order_by('name')
    )
    trending = (
        Article.objects.filter(status='published')
        .select_related('category')
        .order_by('-views', '-created_at')[:3]
    )
    return {
        'nav_categories': categories,
        'trending_articles': trending,
    }
