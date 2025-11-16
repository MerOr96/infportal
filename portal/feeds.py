from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Article

class LatestArticlesFeed(Feed):
    title = "Информационный портал - Последние статьи"
    link = "/"
    description = "Последние опубликованные статьи на информационном портале"
    
    def items(self):
        return Article.objects.filter(status='published').order_by('-created_at')[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt or item.content[:500] + '...' if len(item.content) > 500 else item.content
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self, item):
        return item.created_at
    
    def item_author_name(self, item):
        if item.author:
            return item.author.get_full_name() or item.author.username
        return 'Редакция портала'
    
    def item_categories(self, item):
        categories = []
        if item.category:
            categories.append(item.category.name)
        return categories + [tag.name for tag in item.tags.all()]

