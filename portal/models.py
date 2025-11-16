from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.utils.safestring import mark_safe

User = get_user_model()

# Try to import markdown and bleach
try:
    import markdown
    import bleach
    MARKDOWN_AVAILABLE = True
    # Allowed HTML tags for markdown content
    ALLOWED_TAGS = ['p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'code', 'pre', 
                    'blockquote', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'table': ['class'],
        'th': ['scope'],
        'td': ['colspan', 'rowspan'],
    }
except ImportError:
    MARKDOWN_AVAILABLE = False
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS_CHOICES = [('draft', 'Черновик'), ('published', 'Опубликовано')]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    cover = models.ImageField(upload_to='articles/covers/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portal:article_detail', args=[self.slug])

    @property
    def estimated_read_time(self):
        """Return approximate reading time in minutes based on content length."""
        words = len(self.content.split())
        return max(1, round(words / 200))
    
    def get_content_html(self):
        """Convert markdown content to HTML with sanitization."""
        if MARKDOWN_AVAILABLE:
            html = markdown.markdown(self.content, extensions=['fenced_code', 'tables', 'nl2br'])
            cleaned_html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
            return mark_safe(cleaned_html)
        else:
            # Fallback to plain text with line breaks if markdown is not available
            return mark_safe(self.content.replace('\n', '<br>'))
    
    def save(self, *args, **kwargs):
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        super().save(*args, **kwargs)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    content = models.TextField()
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name or (self.author and self.author.username)}'
