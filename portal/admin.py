from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Tag, Article, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'article_count')
    search_fields = ('name', 'slug')
    
    def article_count(self, obj):
        return obj.articles.filter(status='published').count()
    article_count.short_description = 'Опубликовано статей'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'article_count')
    search_fields = ('name', 'slug')
    
    def article_count(self, obj):
        return obj.articles.filter(status='published').count()
    article_count.short_description = 'Статей'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'created_at', 'article_link')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'created_at', 'tags')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    readonly_fields = ('views', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'status')
        }),
        ('Контент', {
            'fields': ('excerpt', 'content', 'cover')
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_link(self, obj):
        if obj.pk:
            url = reverse('portal:article_detail', args=[obj.slug])
            return format_html('<a href="{}" target="_blank">Просмотреть</a>', url)
        return '-'
    article_link.short_description = 'Ссылка'
    
    actions = ['make_published', 'make_draft']
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} статей опубликовано.')
    make_published.short_description = 'Опубликовать выбранные статьи'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} статей перемещено в черновики.')
    make_draft.short_description = 'Переместить в черновики'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article_link', 'author_display', 'name', 'is_moderated', 'created_at', 'preview')
    list_filter = ('is_moderated', 'created_at', 'article')
    search_fields = ('name', 'email', 'content', 'article__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('is_moderated',)
    
    fieldsets = (
        ('Комментарий', {
            'fields': ('article', 'author', 'name', 'email', 'content', 'is_moderated')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def article_link(self, obj):
        if obj.article:
            url = reverse('admin:portal_article_change', args=[obj.article.pk])
            return format_html('<a href="{}">{}</a>', url, obj.article.title[:50])
        return '-'
    article_link.short_description = 'Статья'
    
    def author_display(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return obj.name or 'Гость'
    author_display.short_description = 'Автор'
    
    def preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    preview.short_description = 'Предпросмотр'
    
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_moderated=True)
        self.message_user(request, f'{updated} комментариев одобрено.')
    approve_comments.short_description = 'Одобрить комментарии'
    
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_moderated=False)
        self.message_user(request, f'{updated} комментариев отклонено.')
    reject_comments.short_description = 'Отклонить комментарии'
