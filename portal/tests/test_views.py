from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from portal.models import Article, Category, Comment, Tag


class ArticleViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='author',
            email='author@example.com',
            password='test-password',
            first_name='Автор',
            last_name='Теста',
        )
        cls.category = Category.objects.create(name='Новости', slug='novosti')
        cls.tag = Tag.objects.create(name='Актуально', slug='aktualno')
        cls.article = Article.objects.create(
            title='Свежие новости портала',
            slug='svezhie-novosti-portala',
            excerpt='Коротко рассказываем о ключевых обновлениях.',
            content='Полный текст новости.' * 50,
            author=cls.user,
            category=cls.category,
            status='published',
            created_at=timezone.now() - timezone.timedelta(days=1),
            views=5,
        )
        cls.article.tags.add(cls.tag)

    def test_article_list_renders_with_published_article(self):
        response = self.client.get(reverse('portal:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.category.name)
        self.assertIn('trending_articles', response.context)

    def test_article_detail_increments_views(self):
        detail_url = self.article.get_absolute_url()
        initial_views = Article.objects.get(pk=self.article.pk).views
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.article.refresh_from_db(fields=['views'])
        self.assertEqual(self.article.views, initial_views + 1)

    def test_search_finds_article_by_title(self):
        response = self.client.get(reverse('portal:search'), {'q': 'новости'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_add_comment_creates_record(self):
        payload = {
            'name': 'Гость',
            'email': 'guest@example.com',
            'content': 'Очень полезно!',
        }
        response = self.client.post(
            reverse('portal:add_comment', args=[self.article.slug]),
            data=payload,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(article=self.article)
        self.assertEqual(comment.content, payload['content'])
        self.assertFalse(comment.is_moderated)
        self.assertEqual(comment.name, payload['name'])

