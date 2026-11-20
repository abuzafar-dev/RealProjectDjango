import re

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from django.core.management import call_command

from blog.models import Category, Comment, Post
from blog.text import plain_excerpt, reading_minutes, render_body


CARD_TITLE_RE = re.compile(r'class="post-card__title"><a href="[^"]+">([^<]+)</a>')
RANK_TITLE_RE = re.compile(r'<li><div><a href="[^"]+">([^<]+)</a>')


def card_titles(response):
    """Titles of the post cards on a page (Jinja2 responses carry no context)."""
    return CARD_TITLE_RE.findall(response.content.decode())


class BlogTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('ali', password='Kuchli_parol_123')
        self.other = User.objects.create_user('vali', password='Kuchli_parol_123')
        self.category = Category.objects.create(name='Python', slug='python')
        self.post = Post.objects.create(author=self.author, category=self.category, title='Django asoslari', text='Matn')

    def test_list_and_search(self):
        Post.objects.create(author=self.author, title='FastAPI', text='Boshqa')
        response = self.client.get(reverse('post_list'), {'q': 'django'})
        self.assertEqual(card_titles(response), ['Django asoslari'])

    def test_filter_by_category(self):
        Post.objects.create(author=self.author, title='Kategoriyasiz', text='Matn')
        response = self.client.get(reverse('post_list'), {'category': 'python'})
        self.assertEqual(card_titles(response), ['Django asoslari'])
        self.assertContains(response, 'aria-label="Kategoriyani tozalash"')

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

    def test_pages_render_with_jinja(self):
        for i in range(6):
            Post.objects.create(author=self.author, title=f'Post {i}', text='Matn')
        self.assertContains(self.client.get(reverse('login')), 'Parol')
        self.assertContains(self.client.get(reverse('register')), "Ro'yxatdan o'tish")
        self.client.force_login(self.author)
        pages = [
            (reverse('post_list'), 'Keyingi'),
            (reverse('post_detail', args=[self.post.pk]), 'Tahrirlash'),
            (reverse('post_create'), 'Yangi post'),
            (reverse('post_update', args=[self.post.pk]), 'Postni tahrirlash'),
            (reverse('post_delete', args=[self.post.pk]), "o'chirasizmi"),
            (reverse('my_posts'), 'Django asoslari'),
        ]
        for url, text in pages:
            response = self.client.get(url)
            self.assertContains(response, text)
            self.assertContains(response, 'csrfmiddlewaretoken')

    def test_sort_popular(self):
        hot = Post.objects.create(author=self.author, title='Mashhur post', text='Matn', views=50)
        response = self.client.get(reverse('post_list'), {'sort': 'popular'})
        self.assertEqual(card_titles(response)[0], 'Mashhur post')
        self.assertContains(response, 'sort=popular" aria-current="true"')

    def test_unknown_sort_falls_back_to_new(self):
        response = self.client.get(reverse('post_list'), {'sort': 'drop table'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sort=new" aria-current="true"')

    def test_pagination_keeps_filters(self):
        for i in range(7):
            Post.objects.create(author=self.author, category=self.category, title=f'Post {i}', text='Matn')
        response = self.client.get(reverse('post_list'), {'category': 'python', 'sort': 'popular'})
        self.assertContains(response, '?category=python&amp;sort=popular&amp;page=2')

    def test_popular_sidebar_skips_unread_posts(self):
        Post.objects.create(author=self.author, title="O'qilgan", text='Matn', views=3)
        html = self.client.get(reverse('post_list')).content.decode()
        self.assertEqual(RANK_TITLE_RE.findall(html), ['O&#39;qilgan'])

    def test_author_page(self):
        Post.objects.create(author=self.other, title='Valining posti', text='Matn', views=7)
        response = self.client.get(reverse('author_detail', args=['ali']))
        self.assertEqual(card_titles(response), ['Django asoslari'])
        self.assertEqual(self.client.get(reverse('author_detail', args=['yoq'])).status_code, 404)

    def test_comment_author_can_delete_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.other, text='Izoh')
        self.client.force_login(self.other)
        self.client.post(reverse('comment_delete', args=[comment.pk]))
        self.assertFalse(Comment.objects.exists())

    def test_post_author_can_moderate_comments(self):
        comment = Comment.objects.create(post=self.post, author=self.other, text='Spam')
        self.client.force_login(self.author)
        self.client.post(reverse('comment_delete', args=[comment.pk]))
        self.assertFalse(Comment.objects.exists())

    def test_stranger_cannot_delete_comment(self):
        stranger = User.objects.create_user('sardor', password='Kuchli_parol_123')
        comment = Comment.objects.create(post=self.post, author=self.other, text='Izoh')
        self.client.force_login(stranger)
        self.client.post(reverse('comment_delete', args=[comment.pk]))
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())
        self.assertEqual(self.client.get(reverse('comment_delete', args=[comment.pk])).status_code, 405)

    def test_post_body_is_escaped_and_code_rendered(self):
        self.post.text = '<script>alert(1)</script>\n\n## Sarlavha\n\n```python\nprint("<b>")\n```'
        self.post.save()
        response = self.client.get(reverse('post_detail', args=[self.post.pk]))
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')
        self.assertContains(response, '<h2>Sarlavha</h2>')
        self.assertContains(response, '<pre data-lang="python"><code>print(&quot;&lt;b&gt;&quot;)</code></pre>', html=False)

    def test_404_page(self):
        response = self.client.get('/posts/999999/')
        self.assertEqual(response.status_code, 404)

    def test_seed_demo_is_idempotent(self):
        call_command('seed_demo', stdout=open('/dev/null', 'w'))
        counts = (Post.objects.count(), Comment.objects.count(), User.objects.count())
        call_command('seed_demo', stdout=open('/dev/null', 'w'))
        self.assertEqual(counts, (Post.objects.count(), Comment.objects.count(), User.objects.count()))
        self.assertGreater(counts[0], 5)


class TextFormattingTests(TestCase):
    def test_inline_code_and_paragraphs(self):
        html = render_body('Birinchi `kod` qator\n\nIkkinchi')
        self.assertEqual(str(html), '<p>Birinchi <code>kod</code> qator</p><p>Ikkinchi</p>')

    def test_excerpt_drops_code_blocks(self):
        self.assertEqual(plain_excerpt('Kirish\n```\nx = 1\n```\nTamom'), 'Kirish Tamom')

    def test_reading_minutes(self):
        self.assertEqual(reading_minutes('soz ' * 10), 1)
        self.assertEqual(reading_minutes('soz ' * 600), 3)

    def test_excerpt_skips_headings(self):
        self.assertEqual(plain_excerpt('Kirish\n\n## Bo\'lim\n\nDavomi'), 'Kirish Davomi')
