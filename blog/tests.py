from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Category, Comment, Post


class BlogTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('ali', password='Kuchli_parol_123')
        self.other = User.objects.create_user('vali', password='Kuchli_parol_123')
        self.category = Category.objects.create(name='Python', slug='python')
        self.post = Post.objects.create(author=self.author, category=self.category, title='Django asoslari', text='Matn')

    def test_list_and_search(self):
        Post.objects.create(author=self.author, title='FastAPI', text='Boshqa')
        response = self.client.get(reverse('post_list'), {'q': 'django'})
        self.assertContains(response, 'Django asoslari')
        self.assertNotContains(response, 'FastAPI')

    def test_filter_by_category(self):
        Post.objects.create(author=self.author, title='Kategoriyasiz', text='Matn')
        response = self.client.get(reverse('post_list'), {'category': 'python'})
        self.assertEqual(len(response.context['posts']), 1)

    def test_detail_increases_views(self):
        self.client.get(reverse('post_detail', args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_create_requires_login(self):
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_post(self):
        self.client.force_login(self.other)
        self.client.post(reverse('post_create'), {'title': 'Yangi', 'text': 'Matn', 'category': self.category.pk})
        self.assertEqual(Post.objects.get(title='Yangi').author, self.other)

    def test_only_author_can_edit(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('post_update', args=[self.post.pk]), {'title': 'Buzildi', 'text': 'x'})
        self.assertEqual(response.status_code, 403)

    def test_author_can_delete(self):
        self.client.force_login(self.author)
        self.client.post(reverse('post_delete', args=[self.post.pk]))
        self.assertFalse(Post.objects.exists())

    def test_add_comment(self):
        self.client.force_login(self.other)
        self.client.post(reverse('post_detail', args=[self.post.pk]), {'text': 'Zo\'r post'})
        self.assertEqual(Comment.objects.get().author, self.other)

    def test_anonymous_cannot_comment(self):
        self.client.post(reverse('post_detail', args=[self.post.pk]), {'text': 'Spam'})
        self.assertFalse(Comment.objects.exists())

    def test_my_posts(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('my_posts'))
        self.assertNotContains(response, 'Django asoslari')
