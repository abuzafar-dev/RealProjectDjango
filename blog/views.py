from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post

SORTS = {
    'new': ('-created_at',),
    'popular': ('-views', '-created_at'),
}


def post_queryset():
    return Post.objects.select_related('author', 'category').annotate(comment_count=Count('comments', distinct=True))


def popular_posts(limit=5):
    return Post.objects.filter(views__gt=0).order_by('-views', '-created_at').only('id', 'title', 'views')[:limit]


class PostListView(ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_sort(self):
        sort = self.request.GET.get('sort', 'new')
        return sort if sort in SORTS else 'new'

    def get_queryset(self):
        posts = post_queryset()
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            posts = posts.filter(Q(title__icontains=self.query) | Q(text__icontains=self.query))
        self.category = None
        slug = self.request.GET.get('category')
        if slug:
            self.category = Category.objects.filter(slug=slug).first()
            posts = posts.filter(category__slug=slug)
        return posts.order_by(*SORTS[self.get_sort()])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        sort_params = params.copy()
        sort_params.pop('sort', None)
        context.update({
            'categories': Category.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0),
            'popular': popular_posts(),
            'query': self.query,
            'active_category': self.category,
            'sort': self.get_sort(),
            'page_params': params.urlencode(),
            'sort_params': sort_params.urlencode(),
            'is_filtered': bool(self.query or self.category),
            'stats': {
                'posts': Post.objects.count(),
                'authors': Post.objects.values('author').distinct().count(),
                'comments': Comment.objects.count(),
            },
        })
        return context


def post_detail(request, pk):
    post = get_object_or_404(post_queryset(), pk=pk)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Izoh qo'shildi")
            return redirect(f'{post.get_absolute_url()}#comment-{comment.pk}')
    else:
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
        post.views += 1
    comments = post.comments.select_related('author')
    related = (post_queryset().filter(category=post.category).exclude(pk=post.pk)[:3]
               if post.category else Post.objects.none())
    return render(request, 'blog/post_detail.html', {
        'post': post, 'comments': comments, 'form': form, 'related': related,
    })


@require_POST
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment.objects.select_related('post'), pk=pk)
    if comment.author != request.user and comment.post.author != request.user:
        messages.error(request, "Bu izohni o'chira olmaysiz")
    else:
        comment.delete()
        messages.success(request, "Izoh o'chirildi")
    return redirect(f'{comment.post.get_absolute_url()}#comments')


def author_detail(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    posts = post_queryset().filter(author=author).order_by('-created_at')
    totals = posts.aggregate(views=Sum('views'))
    return render(request, 'blog/author_detail.html', {
        'author': author,
        'posts': posts,
        'total_views': totals['views'] or 0,
        'comment_count': Comment.objects.filter(post__author=author).count(),
    })


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post qo'shildi")
        return super().form_valid(form)


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Post yangilandi')
        return super().form_valid(form)


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('my_posts')

    def form_valid(self, form):
        messages.success(self.request, "Post o'chirildi")
        return super().form_valid(form)


@login_required
def my_posts(request):
    posts = post_queryset().filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/my_posts.html', {'posts': posts})
